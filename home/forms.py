# forms.py
from django import forms
from .models import UserUploads, Channel

class UserFilesForm(forms.ModelForm):
    class Meta:
        model = UserUploads
        fields = ['video_title','video_description', 'video_thumbnail','video_videofile']

class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['channel_name', 'channel_description', 'channel_picture']
