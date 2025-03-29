from django.urls import path
from . import views

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
]


