from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='dwitter/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('delete/<int:tweet_id>/', views.delete_tweet, name='delete_tweet'),
    path('like/<int:tweet_id>/', views.like_tweet, name='like_tweet'),
]
