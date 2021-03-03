from django.urls import path
from . import views

from .views import UserRegisterView
from .views import HomeView, PostDetailView, AddPostView

urlpatterns = [
  path('', views.home, name='home'),
  path('index.html', views.home, name='home'),
  #path('', views.Login, name='Login'),  
  #path('Login.html', views.Login, name='Login'),
  path('signup.html', UserRegisterView.as_view(), name="signup"),
  path('author.html', HomeView.as_view(), name="author"),
  path('Details/<int:pk>', PostDetailView.as_view(), name="post-details"),
  path('AddPost.html', AddPostView.as_view(), name="add_post"),
  path('editProfile.html', views.editProfile, name='editProfile'),
  #path('newPost.html', views.newPost, name='newPost'),
  path('newMessage.html', views.newMessage, name='newMessage'),
  path('author/<str:author_id>/', views.AuthorEndpoint.as_view(), name='Author')
]