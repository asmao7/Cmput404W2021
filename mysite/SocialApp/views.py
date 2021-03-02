from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from .models import Author

def home(request):
    return render(request, 'home.html', {})

def Login(request):
    return render(request, 'Login.html', {})

def signup(request):
    return render(request, 'signup.html', {})

def author(request):
    return render(request, 'author.html', {})


def editProfile(request):
    return render(request, 'editProfile.html', {})

def newPost(request):
    return render(request, 'newPost.html', {})

def newMessage(request):
    return render(request, 'newMessage.html', {})


class Author(APIView):
    def get(self, request, *args, **kwargs):
        author_id = kwargs.get('author_id', -1)
        if author_id == -1:
            return HttpResponse(status=404)

        author = Author.objects.get(pk=author_id)
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