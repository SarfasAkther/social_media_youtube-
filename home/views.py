from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from home.decorators import channel_required
from .forms import UserFilesForm, ChannelForm
from .models import Channel, Comments, UserUploads, Like, Dislike, WatchLater, Subscription,UserVideosHistory
from django.db.models import Q

@login_required(login_url='login')
@channel_required
def index(request):
    videos = UserUploads.objects.all().order_by('-video_timestamp')

    # Get the logged-in user's channel
    subscribed_channels = []
    my_channel = Channel.objects.filter(user=request.user).first()

    if my_channel:
        subscriptions = Subscription.objects.filter(subscriber=my_channel)
        subscribed_channels = [sub.channel for sub in subscriptions]

    context = {
        'videos': videos,
        'subscribed_channels': subscribed_channels,
    }
    return render(request, 'index.html', context)




@login_required(login_url='login')
def play(request, video_id):
    video = get_object_or_404(UserUploads, video_id=video_id)
    
    # ✅ Increment view count + update watch history
    video.increment_views(request)

    # ✅ Comments with user/channel info
    comments = Comments.objects.filter(video=video).order_by('-timestamp')
    comment_data = []
    for c in comments:
        channel = getattr(c.user, 'channel', None)
        comment_data.append({
            "content": c.content,
            "timestamp": c.timestamp,
            "name": channel.channel_name if channel else c.user.username,
            "picture": channel.channel_picture.url if channel and channel.channel_picture else '/static/images/default-channel.png'
        })

    # ✅ Subscription check
    is_subscribed = False
    if hasattr(request.user, 'channel'):
        publisher_channel = getattr(video.user, 'channel', None)
        if publisher_channel:
            is_subscribed = Subscription.objects.filter(
                subscriber=request.user.channel,
                channel=publisher_channel
            ).exists()

    context = {
        'video': video,
        'publisher_info': getattr(video.user, 'channel', None),
        'comments': comment_data,
        'user_uploads': UserUploads.objects.exclude(video_id=video_id)[:10],
        'user_has_liked': Like.objects.filter(user=request.user, video=video).exists(),
        'user_has_disliked': Dislike.objects.filter(user=request.user, video=video).exists(),
        'is_subscribed': is_subscribed,
    }
    return render(request, 'play-video.html', context)





def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists! Please try another one.')
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('signup')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, f"Welcome {username}, your account has been created.")
            return redirect('create_channel')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back {username}!")
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

@login_required(login_url='login')
@channel_required
def user_upload(request):
    # Check if user has a channel
    if not hasattr(request.user, 'channel'):
        messages.error(request, "You need to create a channel first.")
        return redirect('create_channel')
    elif request.method == "POST":
        form = UserFilesForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            upload.save()
            messages.success(request, "Video uploaded successfully!")
            return redirect('home')
        else:
            messages.error(request, "Something went wrong. Please try again.")
    else:
        form = UserFilesForm()
    return render(request, 'user_upload.html', {'form': form})


@login_required(login_url='login')
def create_channel(request):
    # Check if user already has a channel
    if Channel.objects.filter(user=request.user).exists():
        messages.warning(request, "You already have a channel.")
        return redirect('home')

    if request.method == "POST":
        form = ChannelForm(request.POST, request.FILES)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.user = request.user
            channel.save()
            messages.success(request, "Channel created successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please fill all required fields and upload a picture.")
    else:
        form = ChannelForm()

    return render(request, 'create_channel.html', {'form': form})


@login_required(login_url='login')
def like_video(request, video_id):
    video = get_object_or_404(UserUploads, video_id=video_id)
    like_obj = Like.objects.filter(user=request.user, video=video)

    if like_obj.exists():
        like_obj.delete()
    else:
        Dislike.objects.filter(user=request.user, video=video).delete()
        Like.objects.create(user=request.user, video=video)

    return redirect('play', video_id=video.video_id)


@login_required(login_url='login')
def dislike_video(request, video_id):
    video = get_object_or_404(UserUploads, video_id=video_id)
    dislike_obj = Dislike.objects.filter(user=request.user, video=video)

    if dislike_obj.exists():
        dislike_obj.delete()
    else:
        Like.objects.filter(user=request.user, video=video).delete()
        Dislike.objects.create(user=request.user, video=video)

    return redirect('play', video_id=video.video_id)

@login_required
def save_watchlater(request, video_id):
    video = get_object_or_404(UserUploads, video_id=video_id)
    obj, created = WatchLater.objects.get_or_create(user=request.user, videos=video)
    if not created:
        obj.delete()
    return redirect('play', video_id=video.video_id)


@login_required
def add_comment(request, video_id):
    if request.method == 'POST':
        content = request.POST.get('comment')
        video = get_object_or_404(UserUploads, video_id=video_id)
        Comments.objects.create(user=request.user, video=video, content=content)
    return redirect('play', video_id=video_id)

@login_required(login_url='login')
def subscribe(request):
    if request.method == 'POST':
        # ✅ Get target channel (the one being subscribed to)
        channel_id = request.POST.get('channel_id')
        if not channel_id:
            messages.error(request, "Channel not found.")
            return redirect('home')

        channel_to_subscribe = get_object_or_404(Channel, id=channel_id)

        try:
            # ✅ Get the subscriber's own channel
            subscriber_channel = request.user.channel
        except Channel.DoesNotExist:
            messages.error(request, "You must have a channel to subscribe to others.")
            return redirect('create_channel')

        # ✅ Prevent subscribing to your own channel
        if subscriber_channel == channel_to_subscribe:
            messages.error(request, "You cannot subscribe to your own channel.")
            return redirect('play', video_id=request.POST.get('video_id'))

        # ✅ --- TOGGLE LOGIC STARTS HERE ---
        existing_sub = Subscription.objects.filter(
            subscriber=subscriber_channel,
            channel=channel_to_subscribe
        )

        if existing_sub.exists():
            # 🔹 Already subscribed → unsubscribe (delete)
            existing_sub.delete()
            messages.info(request, f"You unsubscribed from {channel_to_subscribe.channel_name}.")
        else:
            # 🔹 Not subscribed yet → subscribe (create)
            Subscription.objects.create(
                subscriber=subscriber_channel,
                channel=channel_to_subscribe
            )
            messages.success(request, f"You subscribed to {channel_to_subscribe.channel_name}!")
        # ✅ --- TOGGLE LOGIC ENDS HERE ---

        # ✅ Redirect back to the same video page
        video_id = request.POST.get('video_id')
        return redirect('play', video_id=video_id)

    # Fallback
    return redirect('home')

@login_required(login_url='login')
def saved_videos(request):
    saved_videos = WatchLater.objects.filter(user=request.user).select_related('videos').order_by('-id')
    context = {'saved_videos': [entry.videos for entry in saved_videos]}
    return render(request, 'saved_videos.html', context)

@login_required(login_url='login')
def channel_view(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    
    # All videos uploaded by this channel’s user
    videos = UserUploads.objects.filter(user=channel.user).order_by('-video_timestamp')
    
    # Subscriber count
    subscriber_count = Subscription.objects.filter(channel=channel).count()
    
    # Check if the logged-in user is subscribed
    is_subscribed = False
    if request.user.is_authenticated:
        try:
            user_channel = Channel.objects.get(user=request.user)
            is_subscribed = Subscription.objects.filter(subscriber=user_channel, channel=channel).exists()
        except Channel.DoesNotExist:
            pass

    context = {
        'channel': channel,
        'videos': videos,
        'subscriber_count': subscriber_count,
        'is_subscribed': is_subscribed,
    }
    return render(request, 'channel.html', context)

@login_required(login_url='login')
def my_channel(request):
    """Redirect the logged-in user to their own channel page."""
    try:
        channel = Channel.objects.get(user=request.user)
        return redirect('channel_detail', channel_id=channel.id)
    except Channel.DoesNotExist:
        messages.warning(request, "You don’t have a channel yet. Create one to continue.")
        return redirect('create_channel')
    
@login_required(login_url='login')
def watched_history(request):
    """Show recently watched videos (most recent first)"""
    history_entries = (
        UserVideosHistory.objects
        .filter(user=request.user)
        .select_related('video')
        .order_by('-timestamp')
    )
    videos = [entry.video for entry in history_entries]
    return render(request, 'watched_history.html', {'history_videos': videos})



@login_required(login_url='login')
def edit_channel(request):
    channel = get_object_or_404(Channel, user=request.user)

    if request.method == 'POST':
        form = ChannelForm(request.POST, request.FILES, instance=channel)
        if form.is_valid():
            # if user removes channel picture (optional)
            if 'remove_picture' in request.POST:
                channel.channel_picture.delete(save=False)
                channel.channel_picture = None
            form.save()
            return redirect('my_channel')  # redirect to your channel page
    else:
        form = ChannelForm(instance=channel)

    return render(request, 'edit_channel.html', {'form': form})


@login_required
def remove_video(request, video_id):
    video = get_object_or_404(UserUploads, video_id=video_id)

    # Only allow the owner of the video to delete it
    if video.user != request.user:
        messages.error(request, "You cannot delete someone else's video.")
        return redirect('channel_detail', channel_id=request.user.channel.id)

    # Delete related objects
    Like.objects.filter(video=video).delete()
    Dislike.objects.filter(video=video).delete()
    WatchLater.objects.filter(videos=video).delete()
    UserVideosHistory.objects.filter(video=video).delete()

    # Delete the video
    video.delete()
    messages.success(request, "Video removed successfully!")
    return redirect('channel_detail', channel_id=request.user.channel.id)


@login_required(login_url='login')
def search_results(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # ✅ Search by video title OR by channel name
        results = UserUploads.objects.filter(
            Q(video_title__icontains=query) | Q(user__channel__channel_name__icontains=query)
        ).order_by('-video_timestamp')

    return render(request, 'search_results.html', {
        'query': query,
        'results': results
    })





