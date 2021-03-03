from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView

from .models import Author
from .admin import AuthorCreationForm

from django.views import generic
from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView, CreateView
from .models import TextPost

class UserRegisterView(generic.CreateView):
    form_class = AuthorCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

class HomeView(ListView):
    model = TextPost
    template_name = 'author.html'

class PostDetailView(DetailView):
    model = TextPost
    template_name = 'PostDetails.html'

class AddPostView(CreateView):
    model = TextPost
    template_name = 'AddPost.html'
    fields = '__all__'
    #fields = ('title', 'content', 'visibility')


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

        json = {
            "type":"author",
            "id":author.url,
            "host":author.host,
            "displayName":author.display_name,
            "url":author.url,
            "github":author.github
        }
        return JsonResponse(json)

    def post(self, request, *args, **kwargs):
        author_id = kwargs.get('author_id', -1)
        if author_id == -1:
            return HttpResponse(status=404)

        author = Author.objects.get(pk=author_id)
        if not author:
            return HttpResponse(status=404)

        jsonData = request.data
        author.host = jsonData.get("host")
        author.displayName = jsonData.get("displayName")
        author.url = jsonData.get("url")
        author.github = jsonData.get("github")
        author.save()

        return HttpResponse(status=200)