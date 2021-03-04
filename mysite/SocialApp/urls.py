from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('index.html', views.home, name='home'),
  path('Login.html', views.Login, name='Login'),
  path('signup.html', views.signup, name='signup'),
  path('author.html', views.author, name='author') ,
  path('editProfile.html', views.editProfile, name='editProfile'),
  path('newPost.html', views.newPost, name='newPost'),
  path('newMessage.html', views.newMessage, name='newMessage'),
  path('author/<int:author_id>/followers/<int:foreign_author_id>', views.EditFollowersEndpoint.as_view(), name='editFollowers'),
  path('author/<int:author_id>/followers', views.GetFollowersEndpoint.as_view(), name='getFollowers')     
]