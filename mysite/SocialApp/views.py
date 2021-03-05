from django.http import HttpResponse
from django.shortcuts import render
from .forms import SignUpForm, LoginForm, EditProfileForm

def home(request):
    return render(request, 'home.html', {})

def Login(request):
    form = LoginForm(request.POST)
    return render(request, 'Login.html', {'form': form})

def signup(request):
    form = SignUpForm(request.POST)
    return render(request, 'signup.html', {'form': form})

def author(request):
    return render(request, 'author.html', {})


def editProfile(request):
    form = EditProfileForm(request.POST)
    return render(request, 'editProfile.html', {'form': form})

def newPost(request):
    return render(request, 'newPost.html', {})

def newMessage(request):
    return render(request, 'newMessage.html', {})