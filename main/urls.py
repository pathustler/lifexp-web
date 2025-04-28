from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/<str:username>/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
    path('posts/new', views.new_post, name='new_post'),
    path('leaderboard/<str:type>', views.leaderboard, name='leaderboard'),
    path('settings/', views.settings, name='settings'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>', views.post_detail, name='post_detail'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('add_reply/<int:comment_id>/', views.add_reply, name='add_reply'),
    path('toggle-follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('fetch_posts/', views.fetch_posts, name='fetch_posts'),
    path('get_comments/', views.get_comments, name='get_comments'),
    path('api/comments/', views.post_comment, name='post_comment'),
    path("notifications/mark-read/", views.mark_notifications_read, name="mark_notifications_read"),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('delete-search-history/<int:id>/', views.delete_search_history, name='delete_search_history'),
    path('history/', views.history, name='history'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/report/', views.report_post, name='report_post'),
    path('notifications/', views.notification_page, name='notification_page'),
    path('create_custom_activity', views.create_custom_activity, name='create_custom_activity'),
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='users/change_password.html',
        success_url='/settings/'
    ), name='change_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('validate_post/', views.validate_post, name='validate_post'),
    path('fetch_activity_info/', views.fetch_activity_info, name='fetch_activity_info'),


]


