from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Followers, Author
from django.shortcuts import render
from rest_framework.views import APIView
from django.urls import reverse_lazy, reverse
from django.views.generic.list import ListView
from rest_framework import status
from .forms import SignUpForm, LoginForm
from .utils import FollowerFinalJSON, AuthorToJSON
import requests


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
    return render(request, 'editProfile.html', {})

def newPost(request):
    return render(request, 'newPost.html', {})

def newMessage(request):
    return render(request, 'newMessage.html', {})

def followerView(request):
    # url = reverse_lazy('getFollowers')
    url = reverse_lazy("getFollowers", kwargs={"author_id":request.user.id})
    response = requests.get(url)
    follower_list = response['items']
    
    follower_names = []
    for item in follower_list:
        current_name = item['displayName']
        Follower_names.append(current_name)
    
    if not follower_names:
        is_empty = True
    else:
        is_empty = False

    return render(request, 'followers.html', {"followers":follower_names, 'is_empty': is_empty} )

def getFollowerView(request):
    """ get the author's followers if the foreign id author is in there then disable follow button """
    url = reverse_lazy("editFollowers", kwargs={"author_id":request.user.id, "post_id":cls.post_id})
    response = requests.get(url)
    follower_list = response['items']
        # current_author = Author.objects.get(pk=author_id)
        # followers_list = current_author.followed_by.all()
        # followers_ids = []
        # for from_author in followers_list:
        #     followers_ids.append(from_author.id)

        # if foreign_author_id in followers_ids:
        #     is_follower = True
        # else:
        #     is_follower = False
            
    return render(request, 'find_friends.html', {} )
    # return render(request, 'find_friends.html', {"author":author_name, 'is_follower': is_follower})

class EditFollowersEndpoint(APIView):
    # TODO: Make this authenticated if private/friends

    # def dispatch(self, request, *args, **kwargs):
    #     method = self.request.POST.get('_method', '').lower()
    #     if method == 'put':
    #         return self.put(request, *args, **kwargs)
    #     if method == 'delete':
    #         return self.delete(request, *args, **kwargs)

    #     method = self.request.GET.get('_method', '').lower()
    #     if method == 'get':
    #         return self.delete(request, *args, **kwargs)
    #     return super(EditFollowersEndpoint, self).dispatch(request,*args, **kwargs)

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

        foreign_author_id = kwargs.get("foreign_author_id", -1)
        if foreign_author_id == -1:
            return HttpResponse(status=404)

        try:
            get_foreign_author = Author.objects.get(pk=foreign_author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=400)

        if not get_foreign_author:
            # author_name = None
            return HttpResponse(status=404)
        # else:

        if author_id == foreign_author_id:
            return HttpResponse(status=400)

        follower_json = AuthorToJSON(get_foreign_author)

        if follower_json:
            return JsonResponse(follower_json)
        else:
            return HttpResponse(status=500)

            # author_name = get_author.display_name


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

        """Create Follow Relationship """
        follower_object = Author.objects.get(pk=foreign_author_id)
        current_author = Author.objects.get(pk=author_id)

        """ if author ID same as foreign_author_id bad request since you cannot follow yourself"""
        if author_id == foreign_author_id:
            return HttpResponse(status=400)
            # return render(request, 'author.html', {})
        
        is_current_follower = current_author.followed_by.filter(id=foreign_author_id)
        if is_current_follower.exists():
            return HttpResponse(status=400)
            #     is_follower = True
            # else:
            #     is_follower = False

        else:
            new_follower = Followers(author=current_author, follower=follower_object)
            new_follower.save()
            return HttpResponse(status=200)

        # return render(request, 'find_friends.html', {"author":current_author, 'is_follower': is_follower})
    

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

        current_author = Author.objects.get(pk=author_id)
        current_follower = current_author.followed_by.filter(id=foreign_author_id)

        if current_follower.exists():
            can_be_deleted = True
        else:
            can_be_deleted = False

        """ can only delete someone that was following you """
        if can_be_deleted:
            current_author.followed_by.remove(foreign_author_id)
            return HttpResponse(status=200)
            # """ get follower again with new condition"""
            # is_current_follower = current_author.followed_by.filter(id=foreign_author_id)
            # if is_current_follower.exists():
            #     is_follower = True
            # else:
            #     is_follower = False

            # return HttpResponse(status=200)
            # return render(request, 'find_friends.html', {"author":current_author, 'is_follower': is_follower})
        else:
            return HttpResponse(status=400)
            # return render(request, 'find_friends.html', {"author":current_author, 'can_be_deleted': can_be_deleted})
            

class GetFollowersEndpoint(APIView):
    """ Get all the followers of a specific user"""
# def followers(request, author_id):
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

        follower_json_list = []

        followers_list = author.followed_by.all()

        for follower in followers_list:
            followers.append(follower)
            follower_json = AuthorToJSON(follower)
            follower_json_list.append(follower_json)

        json = FollowerFinalJSON(follower_json_list)
        if json:
            # return HttpResponse(status=200)
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)
        # return HttpResponse(status=200)
        # success_url = reverse_lazy('editFollowers')
        # return render(request, 'followers.html', {"followers":followers, 'is_empty': is_empty, 'author_id':author_id}, status=status.HTTP_200_OK)