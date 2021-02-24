from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'home.html', {})

def Login(request):
    return render(request, 'Login.html', {})

def signup(request):
    return render(request, 'signup.html', {})