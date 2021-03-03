from django.urls import path
from . import views

from .views import UserRegisterView

urlpatterns = [
  path('', views.home, name='home'),
  path('index.html', views.home, name='home'),
  #path('', views.Login, name='Login'),  
  #path('Login.html', views.Login, name='Login'),
  path('signup.html', UserRegisterView.as_view(), name="signup"),
  path('author.html', views.author, name='author') ,
  path('editProfile.html', views.editProfile, name='editProfile'),
  path('newPost.html', views.newPost, name='newPost'),
  path('newMessage.html', views.newMessage, name='newMessage'),
  path('author/<str:author_id>/', views.AuthorEndpoint.as_view(), name='Author'),
  path('author/<str:author_id>/posts/<str:post_id>/', views.PostEndpoint.as_view(), name='Post')
]