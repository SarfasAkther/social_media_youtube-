# forms.py
from django import forms
from .models import UserUploads, Channel

class UserFilesForm(forms.ModelForm):
    class Meta:
        model = UserUploads
        fields = [
            'video_title',
            'video_description',
            'video_thumbnail',
            'video_videofile'
        ]

class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['channel_name', 'channel_description', 'channel_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['channel_name'].required = True
        self.fields['channel_description'].required = True
        self.fields['channel_picture'].required = True  # ✅ must upload
