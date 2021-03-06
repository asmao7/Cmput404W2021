from django.urls import path
from . import views

from .views import UserRegisterView
from .views import HomeView, PostDetailView, AddPostView, UpdatePostView, DeletePostView, AddCommentView

urlpatterns = [
  path('', views.home, name='home'),
  path('index.html', views.home, name='home'),
  path('github.html/', views.githubView, name='github'),
  path('github.html/<slug:username>/', views.githubView, name='github'),
  
  path('inbox/', views.inbox, name="inbox"),
  path('signup.html', UserRegisterView.as_view(), name="signup"),
  path('author.html', HomeView.as_view(), name="author"),
  path('Details/<str:pk>', PostDetailView.as_view(), name="post-details"),
  path('AddPost.html', AddPostView.as_view(), name="add_post"), 
  path('details/<str:pk>/share', views.shared_post, name="share_post"),
  path('details/edit/<str:pk>', UpdatePostView.as_view(), name="update_post"),
  path('details/<str:pk>/delete', DeletePostView.as_view(), name="delete_post"),
  path('profile/edit/<str:pk>/', views.UpdateProfile.as_view(), name='editProfile'),
  path('post/<str:pk>/comment', AddCommentView.as_view(), name="add_comment"),
  path('author/<str:author_id>/', views.AuthorEndpoint.as_view(), name='Author'),
  path('author/<str:author_id>/posts/<str:post_id>/', views.PostEndpoint.as_view(), name='Post'),
  path('author.html/like/', views.like, name='like'),
  path('remote_posts.html/remote_comment/', views.remoteComment, name="remote_comment"),
  path('followers', views.followerView, name="followers"),
  path('findFollowers', views.findFollower, name='findFollowers'),
  path('addfollower/<str:foreign_author_id>', views.addFollower, name='addfollower'),
  path('unfollow/<str:foreign_author_id>', views.unFollow, name='unfollow'),
  path('friends', views.friendsView, name="friends"),
  path('remotePosts', views.remotePosts, name="remotePosts"),
  path('findRemoteFollowers', views.findRemoteFollowers, name="findRemoteFollowers"),
  path('addRemoteFollower/<str:remote_author_id>', views.addRemoteFollower, name="addRemoteFollower"),
  path('removeRemoteFollower/<str:remote_author_id>', views.unFollowRemote, name="removeRemoteFollower"),
  path('newMessage.html', views. posts_view, name="new_message"),
  path('posts/', views.AllPostsEndpoint.as_view(), name="AllPosts"),
  path('authors/', views.AllAuthorsEndpoint.as_view(), name="AllAuthors"),
  path('author/<str:author_id>/posts/', views.AuthorPostsEndpoint.as_view(), name='AuthorPosts'),
  path('author/<str:author_id>/followers', views.GetFollowersEndpoint.as_view(), name='getFollowers'),
  path('author/<str:author_id>/inbox/', views.InboxEndpoint.as_view(), name="Inbox"),
  path('author/<str:author_id>/liked/', views.AuthorLikedEndpoint.as_view(), name="AuthorLiked"),
  path('author/<str:author_id>/followers/<str:foreign_author_id>/', views.EditFollowersEndpoint.as_view(), name='editFollowers'),
  path('author/<str:author_id>/posts/<str:post_id>/likes/', views.PostLikesEndpoint.as_view(), name="PostLikes"),
  path('author/<str:author_id>/posts/<str:post_id>/comments/', views.PostCommentsEndpoint.as_view(), name="PostComments"),
  path('author/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/', views.CommentEndpoint.as_view(), name="Comment"),
  path('author/<str:author_id>/posts/<str:post_id>/comments/likes/', views.CommentLikesEndpoint.as_view(), name="CommentLikes"),
]
