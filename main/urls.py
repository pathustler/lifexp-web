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
]


