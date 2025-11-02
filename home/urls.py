from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('play/<int:video_id>/', views.play, name='play'),
    path('register/', views.signup_view, name='signup'),
    path('api/register/', views.api_signup, name='api_signup'),
    path('login-page/', views.login_view, name='login'),
    path('api/login/', views.api_login, name='api_login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('upload/', views.user_upload, name="upload"),
    path('create-channel/', views.create_channel, name="create_channel"),
    path('like/<int:video_id>/', views.like_video, name='like_video'),
    path('api/like/', views.LikeListCreateView.as_view(), name='like-list-create'),
    path('dislike/<int:video_id>/', views.dislike_video, name='dislike_video'),
    path('api/dislike/', views.DislikeListCreateView.as_view(), name='dislike-list-create'),
    path('save/<int:video_id>/', views.save_watchlater, name='save_watchlater'),
    path('comment/<int:video_id>/', views.add_comment, name='add_comment'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('saved/', views.saved_videos, name='saved'),
    path('channel/<int:channel_id>/', views.channel_view, name='channel_detail'),
    path('my-channel/', views.my_channel, name='my_channel'),
    path('history/', views.watched_history, name='watched_history'),
    path('edit-channel/', views.edit_channel, name='edit_channel'),
    path('remove-video/<int:video_id>/', views.remove_video, name='remove_video'),
    path('search/', views.search_results, name='search_results'),


]