import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView

from .models import Author, Post, TextPost, ImagePost
from .admin import AuthorCreationForm

from .utils import AuthorToJSON, PostToJSON

from django.views import generic
from django.urls import reverse_lazy

class UserRegisterView(generic.CreateView):
    form_class = AuthorCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

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
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        json = AuthorToJSON(author)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)

    def post(self, request, *args, **kwargs):
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        jsonData = request.data
        author.host = jsonData.get("host")
        author.displayName = jsonData.get("displayName")
        author.url = jsonData.get("url")
        author.github = jsonData.get("github")
        author.save()

        return HttpResponse(status=200)


class PostEndpoint(APIView):
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

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=404)

        post = None
        is_image = False
        try:
            post = TextPost.objects.get(pk=post_id)
        except:
            try:
                post = ImagePost.objects.get(pk=post_id)
                is_image = True
            except:
                return HttpResponse(status=400)
        if not post:
            return HttpResponse(status=404)

        json = PostToJSON(post, is_image)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)

    # TODO: Make this authenticated
    def post(self, request, *args, **kwargs):
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=404)

        post = None
        try:
            post = TextPost.objects.get(pk=post_id)
        except:
            try:
                post = ImagePost.objects.get(pk=post_id)
            except:
                return HttpResponse(status=400)
        if not post:
            return HttpResponse(status=404)

        # TODO: Handle categories, choose proper visibility
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
        post.visibility = Post.Visibility.PUBLIC
        post.unlisted = bool(jsonData.get("unlisted"))
        post.save()

        return HttpResponse(status=200)

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

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=404)

        post = None
        try:
            post = TextPost.objects.get(pk=post_id)
        except:
            try:
                post = ImagePost.objects.get(pk=post_id)
            except:
                return HttpResponse(status=400)
        if not post:
            return HttpResponse(status=404)

        post.delete()

        return HttpResponse(status=200)

    # TODO: manage post creation based on content type
    def put(self, request, *args, **kwargs):
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=404)

        try:
            jsonData = request.data
            text_post = TextPost(id=post_id, title=jsonData.get("title"), url=jsonData.get("id"), source=jsonData.get("source"),
                                 origin=jsonData.get("origin"), description=jsonData.get("description"), content_type=jsonData.get("contentType"),
                                 author=author, published=datetime(jsonData.get("published")), visibility=Post.Visibility.PUBLIC, unlisted=bool(jsonData.get("unlisted")))
            text_post.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


class PostCreationEndpoint(APIView):
    # TODO: Handle image posts, limit results
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

        text_post_json_list = []
        text_posts = TextPost.objects.filter(author=author)
        for text_post in text_posts:
            json = PostToJSON(text_post)
            if json:
                text_post_json_list.append(json)
        return JsonResponse({"posts":text_post_json_list})

    # TODO: manage post creation based on content type
    def post(self, request, *args, **kwargs):
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        try:
            jsonData = request.data
            text_post = TextPost(title=jsonData.get("title"), url=jsonData.get("id"), source=jsonData.get("source"),
                                 origin=jsonData.get("origin"), description=jsonData.get("description"), content_type=jsonData.get("contentType"),
                                 author=author, published=datetime(jsonData.get("published")), visibility=Post.Visibility.PUBLIC, unlisted=bool(jsonData.get("unlisted")))
            text_post.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)