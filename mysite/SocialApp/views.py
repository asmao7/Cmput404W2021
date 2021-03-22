import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView

from .models import Author, Post, Comment, LikedPost
from .admin import AuthorCreationForm

from .utils import AuthorToJSON, PostToJSON, CommentToJSON, StringListToPostCategoryList, PostListToJSON

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
    fields = ['title', 'content']
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

        # Check for bad URI
        author_id = kwargs.get('author_id', -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Check that associated author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Return public info about the author
        json = AuthorToJSON(author)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests
        """

        # Check for bad URI
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Check that associated author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author:
            return HttpResponse(status=401)

        # Update author info
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

        # Public posts can be viewed by anyone
        if post.visibility != "PUBLIC":
            # Check that a user is authenticated
            if not request.user.is_authenticated:
                return HttpResponse(status=401)

            # TODO: Must be author's friend to have access

        json = PostToJSON(post)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to update the post specified in the URL
        """
        
        # Check for bad URI (author portion)
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check for bad URI (post portion)
        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        # Make sure post exists
        try:
            post = Post.objects.get(pk=post_id, author=author)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Make sure the author is actually the post's author
        if post.author != author:
            return HttpResponse(status=404)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author:
            return HttpResponse(status=401)

        jsonData = request.data
        post.title = jsonData.get("title")
        post.description = jsonData.get("description")
        post.content_type = jsonData.get("contentType")
        post.content = jsonData.get("content")
        post.visibility = jsonData.get("visibility")
        post.unlisted = bool(jsonData.get("unlisted"))
        post.categories.set(StringListToPostCategoryList(jsonData.get("categories")))
        post.save()

        return HttpResponse(status=200)

    def delete(self, request, *args, **kwargs):
        """
        Handles DELETE requests to delete the post specified in the URL
        """

        # Check for bad URI (author portion)
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check for bad URI (post portion)
        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        # Make sure post exists
        try:
            post = Post.objects.get(pk=post_id, author=author)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Make sure the author is actually the post's author
        if post.author != author:
            return HttpResponse(status=404)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author:
            return HttpResponse(status=401)

        post.delete()

        return HttpResponse(status=200)

    def put(self, request, *args, **kwargs):
        """
        Handles PUT requests to create a new post with the ID and author specified by the URL
        """
        
        # Check for bad URI (author portion)
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check for bad URI (post portion)
        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        # Check for malformed URI (post portion)
        try:
            test = uuid.UUID(post_id)
        except:
            return HttpResponse(status=400)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author:
            return HttpResponse(status=401)

        try:
            jsonData = request.data
            post = Post(id=post_id, title=jsonData.get("title"), source=jsonData.get("source"), origin=jsonData.get("origin"),
                        description=jsonData.get("description"), content_type=jsonData.get("contentType"), content=jsonData.get("content"),
                        author=author, visibility=jsonData.get("visibility"), unlisted=bool(jsonData.get("unlisted")))
            post.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


class AuthorPostsEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to return the author's last N posts
        """
        # TODO: Paginate results and sort by date
        # TODO: Authenticate? Or only allow this endpoint to return PUBLIC posts?
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        posts = Post.objects.filter(author=author)
        json = PostListToJSON(posts)
        return JsonResponse({"posts":json})

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new post for the author specified by the URL
        """
        
        # Check for bad URI
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author:
            return HttpResponse(status=401)

        try:
            jsonData = request.data
            post = Post(title=jsonData.get("title"), source=jsonData.get("source"), origin=jsonData.get("origin"),
                        description=jsonData.get("description"), content_type=jsonData.get("contentType"), content=jsonData.get("content"),
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

        # Check for bad URI (author portion)
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check for bad URI (post portion)
        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        # Make sure post exists
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Make sure the author in the URI matches the post's author
        if post.author != author:
            return HttpResponse(status=404)

        # Check that a user is authenticated so it can be the author of the post
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        try:
            jsonData = request.data
            comment = Comment(author=request.user, post=post, comment=jsonData.get("comment"),
                              content_type=jsonData.get("contentType"))
            comment.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)
