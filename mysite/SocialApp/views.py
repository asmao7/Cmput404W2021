import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView

from .models import Author, Post, Comment
from .admin import AuthorCreationForm

from .utils import AuthorToJSON, PostToJSON, CommentToJSON

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

class PostDetailView(DetailView):
    model = Post
    template_name = 'PostDetails.html'

class AddPostView(CreateView):
    model = Post
    template_name = 'AddPost.html'
    fields = '__all__'
    #fields = ('title', 'content', 'visibility')
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
    def get(self, request, *args, **kwargs):
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
    # TODO: Make this authenticated if private/friends
    def get(self, request, *args, **kwargs):
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

        json = PostToJSON(post)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)

    # TODO: Make this authenticated
    def post(self, request, *args, **kwargs):
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

        # TODO: Handle categories
        jsonData = request.data
        post.title = jsonData.get("title")
        post.id = jsonData.get("id")
        post.source = jsonData.get("source")
        post.origin = jsonData.get("origin")
        post.description = jsonData.get("description")
        post.content_type = jsonData.get("contentType")
        post.content = jsonData.get("content")
        post.categories = None
        post.published = datetime(jsonData.get("published"))
        post.visibility = jsonData.get("visibility")
        post.unlisted = bool(jsonData.get("unlisted"))
        post.save()

        return HttpResponse(status=200)

    # TODO: Make this authenticated
    def delete(self, request, *args, **kwargs):
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

        post.delete()

        return HttpResponse(status=200)

    # TODO: manage post creation based on content type
    def put(self, request, *args, **kwargs):
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
            jsonData = request.data
            post = Post(id=post_id, title=jsonData.get("title"), url=jsonData.get("id"), source=jsonData.get("source"),
                                 origin=jsonData.get("origin"), description=jsonData.get("description"), content_type=jsonData.get("contentType"),
                                 author=author, published=datetime(jsonData.get("published")), visibility=jsonData.get("visibility"), unlisted=bool(jsonData.get("unlisted")))
            post.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


class PostCreationEndpoint(APIView):
    # TODO: Handle image posts, limit results, sort by date
    def get(self, request, *args, **kwargs):
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
            post = Post(title=jsonData.get("title"), url=jsonData.get("id"), source=jsonData.get("source"),
                        origin=jsonData.get("origin"), description=jsonData.get("description"), content_type=jsonData.get("contentType"),
                        author=author, published=datetime(jsonData.get("published")), visibility=Post.Visibility.PUBLIC, unlisted=bool(jsonData.get("unlisted")))
            post.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


class CommentEndpoint(APIView):
    def get(self, request, *args, **kwargs):
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

        comment_json_list = []
        comments = Comment.objects.filter(author=author, post=post)
        for comment in comments:
            json = CommentToJSON(comment)
            if json:
                comment_json_list.append(json)
        return JsonResponse({"comments":comment_json_list})

    def post(self, request, *args, **kwargs):
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

        try:
            jsonData = request.data
            comment = Comment(author=author, post=post, comment=jsonData.get("comment"), content_type=jsonData.get("contentType"),
                              published=datetime(jsonData.get("published")), url=jsonData.get("id"))
            comment.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)