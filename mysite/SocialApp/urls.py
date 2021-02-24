from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('index.html', views.home, name='home'),
  path('', views.Login, name='Login'),  
  path('Login.html', views.Login, name='Login'),
   path('signup.html', views.signup, name='signup')   
]