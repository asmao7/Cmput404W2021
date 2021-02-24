from django.http import HttpResponse
from django.shortcuts import render

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