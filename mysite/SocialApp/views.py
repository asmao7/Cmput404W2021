from django.http import HttpResponse
from django.shortcuts import render
from .models import Followers, Author
# from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.views import APIView
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from rest_framework import status


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


class EditFollowersEndpoint(APIView):
    # TODO: Make this authenticated if private/friends
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
# def getAuthorToFollow(request,author_id, foreign_author_id):
    #TODO handle when the given id does not bring up an author
    # if request.method == 'GET':
        foreign_author_id = kwargs.get("foreign_author_id", -1)
        if foreign_author_id == -1:
            return HttpResponse(status=404)
        try:
            get_author = Author.objects.get(pk=foreign_author_id)
        except Author.DoesNotExist:
            get_author = None
        if not get_author:
            author_name = None
        else:
            author_name = get_author.display_name

        """ get the author's followers if the foreign id author is in there then disable follow button """
        current_author = Author.objects.get(pk=author_id)
        followers_list = current_author.followed_by.all()
        followers_ids = []
        for from_author in followers_list:
            followers_ids.append(from_author.id)

        if foreign_author_id in followers_ids:
            is_follower = True
        else:
            is_follower = False

        """ if author ID same as foreign_author_id reroute to author home page"""
        if author_id == foreign_author_id:
            return render(request, 'author.html', {})

        else:
            return render(request, 'find_friends.html', {"author":author_name, 'is_follower': is_follower})

    # elif request.method == 'PUT':
    def put(self, request, *args, **kwargs):  
        #TODO need to authenticate
        #TODO modularize getting followers
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        print("in put")

        foreign_author_id = kwargs.get("foreign_author_id", -1)
        if foreign_author_id == -1:
            return HttpResponse(status=404)

        followersUser(author_id, foreign_author_id)
        current_author = Author.objects.get(pk=author_id)
        followers_list = current_author.followed_by.all()
        followers_ids = []
        for from_author in followers_list:
            followers_ids.append(from_author.id)

        if foreign_author_id in followers_ids:
            is_follower = True
        else:
            is_follower = False

        return render(request, 'find_friends.html', {"author":current_author, 'is_follower': is_follower})
    
    # elif request.method == 'DELETE':
    def delete(self, request, *args, **kwargs):
        print("in delete")

        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=404)

        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        foreign_author_id = kwargs.get("foreign_author_id", -1)
        if foreign_author_id == -1:
            return HttpResponse(status=404)

        foreign_author_id.delete()
        return HttpResponse(status=200)
        # return JsonResponse({'You have successfully deleted'+ followerID + 'as a follower!'})

    def followUser(author_to_follow, from_author):   #will be post for friend request
            new_follower = Followers(author=author_to_follow.id, ollower=from_author.id)
            new_follower.save()



# @api_view(['GET'])
class GetFollowersEndpoint(APIView):
    """ Get all the followers of a specific user"""
# def followers(request, author_id):
    #TODO handle that you can't follow an author twice DONE TEST IT 
    #TODO handle that you can't follow yourself DONE TEST IT
    # if request.method == 'GET':
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

        followers = []
        current_author = Author.objects.get(pk=author_id)
        followers_list = current_author.followed_by.all()

        for follower in followers_list:
            followers.append(follower)

        return render(request, 'followers.html', {"followers":followers}, status=status.HTTP_200_OK)