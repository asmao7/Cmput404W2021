from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .forms import SignUpForm, LoginForm
import requests

import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView, status

from .models import Author, Post, Comment, LikedPost, Followers
from .admin import AuthorCreationForm

from .utils import AuthorToJSON, PostToJSON, CommentToJSON, FollowerFinalJSON

from django.views import generic
from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

class UserRegisterView(generic.CreateView):
    form_class = AuthorCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

class HomeView(ListView):
    model = Post
    template_name = 'author.html'
    likeModel = LikedPost

class PostDetailView(DetailView):
    model = Post
    template_name = 'PostDetails.html'

class AddPostView(CreateView):
    model = Post
    template_name = 'AddPost.html'
    fields = '__all__'
    #fields = ('title', 'content', 'visibility')
    success_url = reverse_lazy('author')

class AddCommentView(CreateView):
    model = Comment
    template_name = 'AddComment.html'
    fields = '__all__'
    success_url = reverse_lazy('author')

class UpdatePostView(UpdateView):
    model = Post
    template_name = 'EditPost.html'
    fields = ['title', 'text_content']
    success_url = reverse_lazy('author')

class DeletePostView(DeleteView):
    model = Post
    template_name = 'DeletePost.html'
    success_url = reverse_lazy('author')
    

def like(request, pk):
	# add a line to database that has user id and post id
	current_user = request.user
	post = get_object_or_404(Post, id=pk)
	
	liked = len(LikedPost.objects.filter(post_id=post, user_id=current_user))	
	if liked == 0:
		liked_post = LikedPost(post_id=post, user_id=current_user)
		liked_post.save()
	
	return HttpResponseRedirect(reverse('author'))

def home(request):
    return render(request, 'home.html', {})

def author(request):
    return render(request, 'author.html', {})

def editProfile(request):
    return render(request, 'editProfile.html', {})

def newPost(request):
    return render(request, 'newPost.html', {})

def newMessage(request):
    return render(request, 'newMessage.html', {})

class AuthorEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests
        """
        author_id = kwargs.get('author_id', -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        json = AuthorToJSON(author)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests
        """
        # TODO: Make this authenticated
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        jsonData = request.data
        author.displayName = jsonData.get("displayName")
        author.github = jsonData.get("github")
        author.save()

        return HttpResponse(status=200)


class PostEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/{POST_ID}/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve a JSON representation of the post specified in the URL
        """
        # TODO: Make this authenticated if not PUBLIC
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        if post.author != author:
            return HttpResponse(status=404)

        json = PostToJSON(post)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to update the post specified in the URL
        """
        # TODO: Make this authenticated
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        try:
            post = Post.objects.get(pk=post_id, author=author)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        if post.author != author:
            return HttpResponse(status=404)

        # TODO: Handle categories
        jsonData = request.data
        post.title = jsonData.get("title")
        post.description = jsonData.get("description")
        post.content_type = jsonData.get("contentType")
        post.text_content = jsonData.get("content")
        post.visibility = jsonData.get("visibility")
        post.unlisted = bool(jsonData.get("unlisted"))
        post.save()

        return HttpResponse(status=200)

    def delete(self, request, *args, **kwargs):
        """
        Handles DELETE requests to delete the post specified in the URL
        """
        # TODO: Make this authenticated
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        if post.author != author:
            return HttpResponse(status=404)

        post.delete()

        return HttpResponse(status=200)

    # TODO: manage post creation based on content type
    # TODO: Should put prevent overwriting an existing post???
    def put(self, request, *args, **kwargs):
        """
        Handles PUT requests to create a new post with the ID and author specified by the URL
        """
        # TODO: Make this authenticated
        # TODO: Manage how the post is created based on the content type
        # TODO: Should this protect us from overwriting an existing post?
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        try:
            test = uuid.UUID(post_id)
        except:
            return HttpResponse(status=400)

        try:
            jsonData = request.data
            post = Post(id=post_id, title=jsonData.get("title"), source=jsonData.get("source"), origin=jsonData.get("origin"),
                        description=jsonData.get("description"), content_type=jsonData.get("contentType"), text_content=jsonData.get("content"),
                        author=author, visibility=jsonData.get("visibility"), unlisted=bool(jsonData.get("unlisted")))
            post.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


class AuthorPostsEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/ endpoint
    """
    # TODO: Handle image posts
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to return the author's last N posts
        """
        # TODO: Paginate results and sort by date
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        post_json_list = []
        posts = Post.objects.filter(author=author)
        for post in posts:
            json = PostToJSON(post)
            if json:
                post_json_list.append(json)
        return JsonResponse({"posts":post_json_list})

    # TODO: manage post creation based on content type
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new post for the author specified by the URL
        """
        # TODO: Make this authenticated
        # TODO: Manage how the post is created based on the content type
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        try:
            jsonData = request.data
            post = Post(title=jsonData.get("title"), source=jsonData.get("source"), origin=jsonData.get("origin"),
                        description=jsonData.get("description"), content_type=jsonData.get("contentType"), text_content=jsonData.get("content"),
                        author=author, visibility=jsonData.get("visibility"), unlisted=bool(jsonData.get("unlisted")))
            post.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


class PostCommentsEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/{POST_ID}/comments/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to return the last N comments on a specific post
        """
        # TODO: Paginate results and sort by date
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        if post.author != author:
            return HttpResponse(status=404)

        comment_json_list = []
        comments = Comment.objects.filter(post=post)
        for comment in comments:
            json = CommentToJSON(comment)
            if json:
                comment_json_list.append(json)
        return JsonResponse({"comments":comment_json_list})

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to add a new comment to a post
        """
        # TODO: Make this authenticated
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        if post.author != author:
            return HttpResponse(status=404)

        try:
            jsonData = request.data
            comment = Comment(author=author, post=post, comment=jsonData.get("comment"),
                              content_type=jsonData.get("contentType"))
            comment.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


def followerView(request):
    
    # current_author_id = request.user.id
    current_author_id = 1
    current_author = Author.objects.get(pk=current_author_id)
    followers = []
    followers_list = current_author.followed_by.all()

    for follower in followers_list:
        followers.append(follower.display_name)

    if not followers:
       is_empty = True
    else:
        is_empty = False

    return render(request, 'followers.html', {"followers":followers, 'is_empty': is_empty} )

def getFollowerDetails(request):
    """ get the author's followers if the foreign id author is in there then disable follow button """
#     url = reverse_lazy("editFollowers", kwargs={"author_id":request.user.id, "post_id":cls.post_id})
#     response = requests.get(url)
#     follower_list = response['items']
    # author_id = request.user.id
    author_id = 1
    foreign_author_id = 3
    foreign_author = Author.objects.get(pk=foreign_author_id)
    foreign_author_name = foreign_author.display_name
    current_author = Author.objects.get(pk=author_id)
    method = request.POST.get('_method', '').lower()

    # print(method)

    if method == 'put':
        # print('in post')
        create_new_follower = Followers(author=current_author, follower=foreign_author)
        create_new_follower.save()
    elif method == 'delete':
        # print('in del')
        current_author.followed_by.remove(foreign_author_id)
    
    
    current_followers_list = current_author.followed_by.all()
    followers_ids = []
    for from_author in current_followers_list:
        followers_ids.append(from_author.id)

    if foreign_author_id in followers_ids:
        is_follower = True
    else:
        is_follower = False
            
#     return render(request, 'find_friends.html', {} )
    return render(request, 'find_friends.html', {"author":foreign_author_name, 'is_follower': is_follower})

class EditFollowersEndpoint(APIView): 
    # def dispatch(self, request, *args, **kwargs):
    #     method = self.request.POST.get('_method', '').lower()
    #     if method == 'put':
    #         return self.put(request, *args, **kwargs)
    #     if method == 'delete':
    #         return self.delete(request, *args, **kwargs)

    #     method = self.request.GET.get('_method', '').lower()
    #     if method == 'get':
    #         return self.delete(request, *args, **kwargs)
    #     return super(EditFollowersEndpoint, self).dispatch(request,*args, **kwargs)

    def get(self, request, *args, **kwargs):
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)

        if not author:
            return HttpResponse(status=404)

        foreign_author_id = kwargs.get("foreign_author_id", -1)
        if foreign_author_id == -1:
            return HttpResponse(status=404)

        try:
            get_foreign_author = Author.objects.get(pk=foreign_author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=400)

        if not get_foreign_author:
            # author_name = None
            return HttpResponse(status=404)
        # else:

        if author_id == foreign_author_id:
            return HttpResponse(status=400)

        follower_json = AuthorToJSON(get_foreign_author)

        if follower_json:
            return JsonResponse(follower_json)
        else:
            return HttpResponse(status=500)

            # author_name = get_author.display_name


    def put(self, request, *args, **kwargs):  
        #TODO need to authenticate
        #TODO modularize getting followers
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)


        foreign_author_id = kwargs.get("foreign_author_id", -1)
        if foreign_author_id == -1:
            return HttpResponse(status=404)

        """Create Follow Relationship """
        follower_object = Author.objects.get(pk=foreign_author_id)
        current_author = Author.objects.get(pk=author_id)

        """ if author ID same as foreign_author_id bad request since you cannot follow yourself"""
        if author_id == foreign_author_id:
            return HttpResponse(status=400)
            # return render(request, 'author.html', {})
        
        is_current_follower = current_author.followed_by.filter(id=foreign_author_id)
        if is_current_follower.exists():
            return HttpResponse(status=400)
            #     is_follower = True
            # else:
            #     is_follower = False

        else:
            new_follower = Followers(author=current_author, follower=follower_object)
            new_follower.save()
            return HttpResponse(status=200)

        # return render(request, 'find_friends.html', {"author":current_author, 'is_follower': is_follower})
    

    def delete(self, request, *args, **kwargs):
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        foreign_author_id = kwargs.get("foreign_author_id", -1)
        if foreign_author_id == -1:
            return HttpResponse(status=404)

        current_author = Author.objects.get(pk=author_id)
        current_follower = current_author.followed_by.filter(id=foreign_author_id)

        if current_follower.exists():
            can_be_deleted = True
        else:
            can_be_deleted = False

        """ can only delete someone that was following you """
        if can_be_deleted:
            current_author.followed_by.remove(foreign_author_id)
            return HttpResponse(status=200)
            # """ get follower again with new condition"""
            # is_current_follower = current_author.followed_by.filter(id=foreign_author_id)
            # if is_current_follower.exists():
            #     is_follower = True
            # else:
            #     is_follower = False

            # return HttpResponse(status=200)
            # return render(request, 'find_friends.html', {"author":current_author, 'is_follower': is_follower})
        else:
            return HttpResponse(status=400)
            # return render(request, 'find_friends.html', {"author":current_author, 'can_be_deleted': can_be_deleted})
            

class GetFollowersEndpoint(APIView):
    """ Get all the followers of a specific user"""
    def get(self, request, *args, **kwargs):
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        followers = []

        follower_json_list = []

        followers_list = author.followed_by.all()

        for follower in followers_list:
            followers.append(follower)
            follower_json = AuthorToJSON(follower)
            follower_json_list.append(follower_json)

        json = FollowerFinalJSON(follower_json_list)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)