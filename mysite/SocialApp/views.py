import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView

from .models import Author, Post, Comment, LikedPost, InboxItem
from .admin import AuthorCreationForm

from .utils import AuthorToJSON, PostToJSON, CommentToJSON, InboxItemToJSON

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
    print(request.user.id)
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


class InboxEndpoint(APIView):
    """
    ://service/author/{AUTHOR_ID}/inbox
    """
    def get(self, request, *args, **kwargs):
        """
        If authenticated get a list of posts sent to {AUTHOR_ID}.
        Requests the links inside all InboxItem objects and composes 
        their responses in a JSON that represents the inbox.
        """
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)
        # Assuming that nobody else can GET your inbox
        if request.user.is_authenticated and str(request.user.id) == author_id:
            # Get inbox items and format into JSON to return
            inbox_items = InboxItem.objects.filter(author=request.user.id)
            item_json_list = []
            for item in inbox_items:
                json = InboxItemToJSON(item) # will request whatever's at link
                if json:
                    item_json_list.append(json)
            response_json = {
                "type":"inbox",
                "author":request.scheme+"://"+request.get_host()+"/author/"+str(author_id),
                "items":item_json_list
            }
            return JsonResponse(response_json)
        else:
            return HttpResponse("You need to log in first to see your inbox.", status=401)
            
    def post(self, request, *args, **kwargs):
        """
        POST to an author's inbox to send them a link (to either a post, follow, or like).
        """
        author_id = kwargs.get("author_id", -1) # the uuid of the author you want to send to
        if author_id == -1:
            return HttpResponse(status=400)
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception as e:
            print(e)
            return HttpResponse(status=400)
        # NOTE: I am assuming that only logged in users can POST to inboxes.
        if request.user.is_authenticated:
            try:
                new_item = InboxItem(author=author, link=request.data.get("link"))
                new_item.save()
                return HttpResponse(status=201)
            except Exception as e:
                print(e)
                return HttpResponse("Internal Server Error:"+e, status=500)
        else:
            return HttpResponse("You need to log in first to POST to inboxes.", status=401)

    def delete(self, request, *args, **kwargs):
        """
        Clear the inbox; delete all InboxItems from the authenticated author.
        """
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)
        if request.user.is_authenticated and str(request.user.id) == author_id:
            inbox_items = InboxItem.objects.filter(author=request.user.id)
            # NOTE: does not check to see if Inbox is already empty
            inbox_items.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse("You need to log in first to delete your inbox.", status=401)


