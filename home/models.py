from django.db import models
from django.contrib.auth.models import User
from django.db.models import F


class UserUploads(models.Model):
    video_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    video_title = models.CharField(max_length=150)
    video_description = models.TextField(default="")
    video_thumbnail = models.ImageField(upload_to='upload_thumbnail/')
    video_videofile = models.FileField(upload_to='upload/')
    video_timestamp = models.DateTimeField(auto_now_add=True)
    video_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.video_title

    def increment_views(self, request):
        """Increment view count once per user/session and manage watch history"""
        from django.db.models import F
        from .models import UserVideosHistory

        if request.user.is_authenticated:
            entry, created = UserVideosHistory.objects.get_or_create(
                user=request.user,
                video=self
            )
            if created:  # Only count if first time user watches this video
                self.video_views = F('video_views') + 1
                self.save(update_fields=['video_views'])
                self.refresh_from_db(fields=['video_views'])
            else:
                entry.save()  # Update timestamp
        else:
            session_key = f'viewed_video_{self.video_id}'
            if not request.session.get(session_key):
                self.video_views = F('video_views') + 1
                self.save(update_fields=['video_views'])
                self.refresh_from_db(fields=['video_views'])
                request.session[session_key] = True



class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(UserUploads, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} liked {self.video.video_title}"


class Dislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(UserUploads, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} disliked {self.video.video_title}"


class UserVideosHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(UserUploads, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)  # updates automatically on save()

    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-timestamp']  # newest first

    def __str__(self):
        return f"{self.user.username} watched {self.video.video_title}"


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(UserUploads, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"


class WatchLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    videos = models.ForeignKey(UserUploads, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'videos')

    def __str__(self):
        return f"{self.user.username} will watch {self.videos.video_title} later"


class Channel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=100)
    channel_description = models.TextField(default="No channel description yet.")
    channel_created_at = models.DateTimeField(auto_now_add=True)
    channel_picture = models.ImageField(upload_to='channel_pictures/')

    def __str__(self):
        return self.channel_name


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        'Channel',
        related_name='subscriptions',
        on_delete=models.CASCADE
    )
    channel = models.ForeignKey(
        'Channel',
        related_name='subscribers',
        on_delete=models.CASCADE
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'channel')

    def __str__(self):
        return f"{self.subscriber.channel_name} subscribed to {self.channel.channel_name}"
