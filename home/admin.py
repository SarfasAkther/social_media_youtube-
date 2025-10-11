from django.contrib import admin
from .models import WatchLater, Like, Dislike, UserUploads,Comments, UserVideosHistory,Channel, Subscription
admin.site.register(WatchLater)
admin.site.register(Like)
admin.site.register(Dislike)
admin.site.register(UserUploads)
admin.site.register(Comments)
admin.site.register(UserVideosHistory)
admin.site.register(Channel)
admin.site.register(Subscription)

