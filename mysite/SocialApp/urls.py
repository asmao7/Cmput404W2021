from django.urls import path
from . import views

from .views import UserRegisterView
from .views import HomeView, PostDetailView, AddPostView, UpdatePostView, DeletePostView, AddCommentView

urlpatterns = [
  path('', views.home, name='home'),
  path('index.html', views.home, name='home'),
  #path('', views.Login, name='Login'),  
  #path('Login.html', views.Login, name='Login'),
  path('signup.html', UserRegisterView.as_view(), name="signup"),
  path('author.html', HomeView.as_view(), name="author"),
  path('Details/<str:pk>', PostDetailView.as_view(), name="post-details"),
  path('AddPost.html', AddPostView.as_view(), name="add_post"),
  path('details/edit/<str:pk>', UpdatePostView.as_view(), name="update_post"),
  path('details/<str:pk>/delete', DeletePostView.as_view(), name="delete_post"),
  path('editProfile.html', views.editProfile, name='editProfile'),
  path('post/str:pk/comment', AddCommentView.as_view(), name="add_comment"),
  path('newMessage.html', views.newMessage, name='newMessage'),
  path('author/<str:author_id>/', views.AuthorEndpoint.as_view(), name='Author'),
  path('author/<str:author_id>/posts/<str:post_id>/', views.PostEndpoint.as_view(), name='Post'),
  path('author.html/<str:pk>/like/', views.like, name='like'),
  path('followers', views.followerView, name="followers"),
  path('findFollowers', views.findFollower, name='findFollowers'),
  path('addfollower/<str:foreign_author_id>', views.addFollower, name='addfollower'),
  path('unfollow/<str:foreign_author_id>', views.unFollow, name='unfollow'),
  path('friends', views.friendsView, name="friends"),
  path('remotePosts', views.remotePosts, name="remotePosts"),
  path('author/<str:author_id>/posts/', views.AuthorPostsEndpoint.as_view(), name='AuthorPosts'),
  path('author/<str:author_id>/followers', views.GetFollowersEndpoint.as_view(), name='getFollowers'),
  path('author/<str:author_id>/inbox/', views.InboxEndpoint.as_view(), name="inbox"),
  path('author/<str:author_id>/followers/<str:foreign_author_id>/', views.EditFollowersEndpoint.as_view(), name='editFollowers'),
  path('author/<str:author_id>/posts/<str:post_id>/comments/', views.PostCommentsEndpoint.as_view(), name="PostComments"),
]
