from django.shortcuts import redirect
from django.contrib import messages
from .models import Channel

def channel_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not Channel.objects.filter(user=request.user).exists():
            messages.warning(request, "You must create a channel to continue.")
            return redirect('create_channel')
        return view_func(request, *args, **kwargs)
    return wrapper
