import datetime
import requests
import uuid
import json

from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .forms import SignUpForm, LoginForm

import datetime, uuid, requests
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import escape
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView, status

from .models import Author, Post, Comment, LikedPost, InboxItem, Followers
from .admin import AuthorCreationForm

from .utils import AuthorToJSON, PostToJSON, CommentToJSON, StringListToPostCategoryList, AuthorListToJSON, PostListToJSON, InboxItemToJSON , FollowerFinalJSON, ValidateForeignPostJSON

from django.views import generic
from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import PostForm, CommentForm

class UserRegisterView(generic.CreateView):
    form_class = AuthorCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

class HomeView(ListView):
    model = Post
    template_name = 'author.html'
    likeModel = LikedPost
    ordering = ['-published']

class PostDetailView(DetailView):
    model = Post
    template_name = 'PostDetails.html'

class AddPostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'AddPost.html'
    success_url = reverse_lazy('author')

class AddCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'AddComment.html'
    #fields = '__all__'
    success_url = reverse_lazy('author')

class UpdatePostView(UpdateView):
    model = Post
    template_name = 'EditPost.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('author')

class DeletePostView(DeleteView):
    model = Post
    template_name = 'DeletePost.html'
    success_url = reverse_lazy('author')

def like(request, pk):
	# add a line to database that has user id and post id
	current_user = request.user
	post = get_object_or_404(Post, id=pk)
	
	liked = len(LikedPost.objects.filter(post_id=post, user_id=current_user))	
	if liked == 0:
		liked_post = LikedPost(post_id=post, user_id=current_user)
		liked_post.save()
	
	return HttpResponseRedirect(reverse('author'))

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

def inbox(request):
    """
    Request all of the inbox items using our API endpoint and render out.
    """
    # Martijn Pieters https://stackoverflow.com/a/13569789
    logurl = request.scheme+"://"+request.get_host()+"/SocialApp/login/"
    client = requests.session()
    client.get(logurl) # Sets cookie
    if 'csrftoken' in client.cookies:
        csrftoken = client.cookies['csrftoken']
    else: print("No CSRF cookie found")
    sessionid = request.COOKIES.get('sessionid') # FBI OPEN UP
    if not sessionid:
        print("No sessionid cookie found")
    cookies = dict(csrftoken=csrftoken, sessionid=sessionid)
    # Now GET the inbox endpoint and pass in our cookies
    url = request.scheme+"://"+request.get_host()+"/author/"+str(request.user.id)+"/inbox/"
    resp = client.get(url, cookies=cookies, headers=dict(Referer=logurl))
    # Pass the resulting inbox items to the template if successful
    if resp.status_code == 200:
        inbox_json = dict(resp.json())
        inbox_items = inbox_json["items"]
        return render(request, 'inbox.html', { 'inbox_items': inbox_items })
    else:
        return HttpResponse(str(resp.text), status=resp.status_code)
    

class AllAuthorsEndpoint(APIView):
    """
    The authors/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve all authors on the system
        """
        # Check that a user is an authenticated server since this gives access to sensitive data
        if not request.user.is_authenticated or not request.user.is_server:
            return HttpResponse(status=401)

        try:
            json = AuthorListToJSON(Author.objects.all())
            return JsonResponse({"authors":json})
        except:
            return HttpResponse(status=500)


class AuthorEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests
        """

        # Check for bad URI
        author_id = kwargs.get('author_id', -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Check that associated author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Return public info about the author
        json = AuthorToJSON(author)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests
        """

        # Check for bad URI
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Check that associated author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author and not request.user.is_server:
            return HttpResponse(status=401)

        # Update author info
        jsonData = request.data
        author.username = jsonData.get("displayName")
        author.github = jsonData.get("github")
        author.save()

        return HttpResponse(status=200)


class AllPostsEndpoint(APIView):
    """
    The posts/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve all posts on the system
        """
        # Check that a user is an authenticated server since this gives access to sensitive data
        if not request.user.is_authenticated or not request.user.is_server:
            return HttpResponse(status=401)

        try:
            json = PostListToJSON(Post.objects.all())
            return JsonResponse({"posts":json})
        except:
            return HttpResponse(status=500)


class PostEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/{POST_ID}/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve a JSON representation of the post specified in the URL
        """
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

        if post.author != author:
            return HttpResponse(status=404)

        # Public posts can be viewed by anyone
        if post.visibility != "PUBLIC":
            # Check that a user is authenticated
            if not request.user.is_authenticated:
                return HttpResponse(status=401)

            # TODO: Must be author's friend to have access

        json = PostToJSON(post)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to update the post specified in the URL
        """
        
        # Check for bad URI (author portion)
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check for bad URI (post portion)
        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        # Make sure post exists
        try:
            post = Post.objects.get(pk=post_id, author=author)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Make sure the author is actually the post's author
        if post.author != author:
            return HttpResponse(status=404)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author and not request.user.is_server:
            return HttpResponse(status=401)

        jsonData = request.data
        post.title = jsonData.get("title")
        post.description = jsonData.get("description")
        post.content_type = jsonData.get("contentType")
        post.content = jsonData.get("content")
        post.visibility = jsonData.get("visibility")
        post.unlisted = bool(jsonData.get("unlisted"))
        post.categories.set(StringListToPostCategoryList(jsonData.get("categories")))
        post.save()

        return HttpResponse(status=200)

    def delete(self, request, *args, **kwargs):
        """
        Handles DELETE requests to delete the post specified in the URL
        """

        # Check for bad URI (author portion)
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check for bad URI (post portion)
        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        # Make sure post exists
        try:
            post = Post.objects.get(pk=post_id, author=author)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Make sure the author is actually the post's author
        if post.author != author:
            return HttpResponse(status=404)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author and not request.user.is_server:
            return HttpResponse(status=401)

        post.delete()

        return HttpResponse(status=200)

    def put(self, request, *args, **kwargs):
        """
        Handles PUT requests to create a new post with the ID and author specified by the URL
        """
        
        # Check for bad URI (author portion)
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check for bad URI (post portion)
        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        # Check for malformed URI (post portion)
        try:
            test = uuid.UUID(post_id)
        except:
            return HttpResponse(status=400)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author and not request.user.is_server:
            return HttpResponse(status=401)

        try:
            jsonData = request.data
            post = Post(id=post_id, title=jsonData.get("title"), source=jsonData.get("source"), origin=jsonData.get("origin"),
                        description=jsonData.get("description"), content_type=jsonData.get("contentType"), content=jsonData.get("content"),
                        author=author, visibility=jsonData.get("visibility"), unlisted=bool(jsonData.get("unlisted")))
            post.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


class AuthorPostsEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to return the author's last N posts
        """
        # TODO: Paginate results and sort by date
        # TODO: Authenticate? Or only allow this endpoint to return PUBLIC posts?
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        posts = Post.objects.filter(author=author)

        try:
            json = PostListToJSON(posts)
            return JsonResponse({"posts":json})
        except:
            return HttpResponse(status=500)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new post for the author specified by the URL
        """
        
        # Check for bad URI
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check that a user is authenticated
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        # Check that the right user is authenticated
        if request.user != author and not request.user.is_server:
            return HttpResponse(status=401)

        try:
            jsonData = request.data
            post = Post(title=jsonData.get("title"), source=jsonData.get("source"), origin=jsonData.get("origin"),
                        description=jsonData.get("description"), content_type=jsonData.get("contentType"), content=jsonData.get("content"),
                        author=author, visibility=jsonData.get("visibility"), unlisted=bool(jsonData.get("unlisted")))
            post.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


class PostCommentsEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/{POST_ID}/comments/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to return the last N comments on a specific post
        """
        # TODO: Paginate results and sort by date
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

        if post.author != author:
            return HttpResponse(status=404)

        comment_json_list = []
        comments = Comment.objects.filter(post=post)
        for comment in comments:
            json = CommentToJSON(comment)
            if json:
                comment_json_list.append(json)
        return JsonResponse({"comments":comment_json_list})

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to add a new comment to a post
        """

        # Check for bad URI (author portion)
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)

        # Make sure author exists
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Check for bad URI (post portion)
        post_id = kwargs.get("post_id", -1)
        if post_id == -1:
            return HttpResponse(status=400)

        # Make sure post exists
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        # Make sure the author in the URI matches the post's author
        if post.author != author:
            return HttpResponse(status=404)

        # Check that a user is authenticated so it can be the author of the post
        if not request.user.is_authenticated:
            return HttpResponse(status=401)

        try:
            jsonData = request.data
            comment = Comment(author=request.user, post=post, comment=jsonData.get("comment"),
                              content_type=jsonData.get("contentType"))
            comment.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=500)


def followerView(request):
    
    current_author_id = request.user.id
    current_author = Author.objects.get(pk=current_author_id)
    followers = []
    followers_list = current_author.followee.all() #all the people currently following this user

    #all the people that the user currently follows 
    #TODO move these to the friends tab
    following = current_author.following.all()
    following_list = []

    for author in following:
        following_list.append(author.author_to)

    for follower in followers_list:
        if follower.author_from in following_list:
            pass
        else:
            followers.append(follower)


    if not followers:
       is_empty = True
    else:
        is_empty = False

    return render(request, 'followers.html', {"followers":followers, 'is_empty': is_empty} )


def findFollower(request):
    author_id = request.user.id
    author_object = Author.objects.get(pk=author_id)
    following_list = []
    following = author_object.following.all()  #all the people the current user follows
    
    for follower in following:
        following_list.append(follower.author_to) #append the author being followed

    #get all the current author's followers so they only show up in the followers tab
    followers = author_object.followee.all() 

    for follower_author in followers:
        following_list.append(follower_author.author_from) #append the author being followed


    all_authors = Author.objects.exclude(pk=author_id).exclude(is_staff=True).exclude(is_server=True)
    authors = []   #list of all authors not followed by the author

    for current in all_authors:
        if current in following_list:
            pass
        else:
            authors.append(current)
    
    if not authors:
        is_empty = True
    else:
        is_empty  = False

    return render(request, 'find_friends.html', {"author_list":authors, 'is_empty': is_empty})


def addFollower(request, foreign_author_id):
    #add new follower and return followers list with new follower included
    #TODO authenticate follower addition
    #TODO check correct save
    #TODO order of add for unique constraint for friends
    foreign_author =  Author.objects.get(pk=foreign_author_id)
    current_author_id = request.user.id
    current_author =  Author.objects.get(pk=current_author_id)

    if current_author_id == foreign_author_id:
            is_new_follower = False
            return render(request, 'addFollower.html', {"foreign_author":foreign_author, 'new_follower':is_new_follower} )
    new_follower = Followers.objects.create(author_from=current_author, author_to=foreign_author)
    is_new_follower = True
    return render(request, 'addFollower.html', {"foreign_author":foreign_author, 'new_follower':is_new_follower} )

def friendsView(request):

    current_author_id = request.user.id
    current_author = Author.objects.get(pk=current_author_id)
    friends = []
    current_followers_list = current_author.followee.all() #all the people currently following this user

    #all the people that the user currently follows
    #TODO move these to the friends tab
    current_following = current_author.following.all()
    current_following_list = []

    for author in current_following:
        current_following_list.append(author.author_to)

    for follower in current_followers_list:
        if follower.author_from in current_following_list:
            friends.append(follower)


    if not friends:
       is_empty = True
    else:
        is_empty = False

    return render(request, 'friends.html', {"friends":friends, 'is_empty': is_empty} )


def unFollow(request, foreign_author_id): 
    """ un follow an author """

    foreign_author =  Author.objects.get(pk=foreign_author_id)
    current_author_id = request.user.id
    current_author =  Author.objects.get(pk=current_author_id)
    current_follower = current_author.following.filter(author_to=foreign_author)

    # can only delete someone that was following you
    if current_follower.exists():
        current_follower.delete()

    following = []
    following_list = current_author.following.all()
    for following_author in following_list:
        following.append(following_author)

    followers = []
    follower_list = current_author.followee.all()
    for follower in follower_list:
        followers.append(follower)

    if not following:
       is_empty = True
    else:
        is_empty = False


   # chnage to render friends template
    return friendsView(request)


def remotePosts(request):
    """
    Display public posts on Team 17's server
    """
    team_17 = "https://cmput-404-group17.herokuapp.com/"
    author_endpoint = "author/"
    authors = requests.get("{}{}".format(team_17, author_endpoint)).json()
    public_posts = []
    for author in authors:
        posts = requests.get("{}/posts/".format(author["url"])).json()
        for post in posts["items"]:
            if ValidateForeignPostJSON(post):
                if post["visibility"] == "PUBLIC":
                    public_posts.append(post)

    return render(request, 'remote_posts.html', {"posts":public_posts, "has_content":len(public_posts) > 0})


class EditFollowersEndpoint(APIView): 

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
            return HttpResponse(status=404)

        if author_id == foreign_author_id:
            return HttpResponse(status=400)

        follower_json = AuthorToJSON(get_foreign_author)

        if follower_json:
            return JsonResponse(follower_json)
        else:
            return HttpResponse(status=500)



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


        foreign_author_id = kwargs.get("foreign_author_id", -1)
        if foreign_author_id == -1:
            return HttpResponse(status=404)

        try:
            foreign_author = Author.objects.get(pk=foreign_author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        #if author ID same as foreign_author_id bad request since you cannot follow yourself
        if author_id == foreign_author_id:
            return HttpResponse(status=400)
        
        #check if already following first 
        is_current_follower = current_author.following.filter(author_to=foreign_author_id)
        if is_current_follower.exists():
            return HttpResponse(status=400)

        else:
            new_follower = Followers.objects.create(author_from=author, author_to=foreign_author)
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

        foreign_author_id = kwargs.get("foreign_author_id", -1)
        if foreign_author_id == -1:
            return HttpResponse(status=404)

        try:
            foreign_author = Author.objects.get(pk=foreign_author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)

        # current_author = Author.objects.get(pk=author_id)
        current_follower = current_author.following.filter(author_to=foreign_author)

        # can only delete someone that was following you
        if current_follower.exists():
            current_follower.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
            

class GetFollowersEndpoint(APIView):
    """ Get all the followers of a specific user"""
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
        # followers_list = author.followee.all()

        for follower in followers_list:
            followers.append(follower)
            follower_json = AuthorToJSON(follower)
            follower_json_list.append(follower_json)

        json = FollowerFinalJSON(follower_json_list)
        if json:
            return JsonResponse(json)
        else:
            return HttpResponse(status=500)


class InboxEndpoint(APIView):
    """
    ://service/author/{AUTHOR_ID}/inbox
    """
    def get(self, request, *args, **kwargs):
        """
        If authenticated get a list of posts sent to {AUTHOR_ID}.
        Requests the links inside all InboxItem objects and composes 
        their responses in a JSON that represents the inbox.
        """
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)
        try:
            author = Author.objects.get(pk=author_id)
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)
        # Assuming that nobody else can GET your inbox
        if request.user.is_authenticated and (str(request.user.id) == author_id or request.user.is_server):
            # Get inbox items and format into JSON to return
            inbox_items = InboxItem.objects.filter(author=author)
            item_json_list = []
            for item in inbox_items:
                json = InboxItemToJSON(item) # will request whatever's at link
                if json:
                    item_json_list.append(json)
            response_json = {
                "type":"inbox",
                "author":request.scheme+"://"+request.get_host()+"/author/"+str(author_id),
                "items":item_json_list
            }
            return JsonResponse(response_json)
        else:
            return HttpResponse("You need to log in first to see your inbox.", status=401)
            
    def post(self, request, *args, **kwargs):
        """
        POST to an author's inbox to send them a link (to either a post, follow, or like).
        """
        author_id = kwargs.get("author_id", -1) # the uuid of the author you want to send to
        if author_id == -1:
            return HttpResponse(status=400)
        try:
            author = Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            return HttpResponse(status=404)
        except Exception as e:
            print(e)
            return HttpResponse(status=400)
        # NOTE: I am assuming that only logged in users can POST to inboxes.
        if request.user.is_authenticated:
            try:
                new_item = InboxItem(author=author, link=request.data.get("link"))
                new_item.save()
                return HttpResponse(status=201)
            except Exception as e:
                print(e)
                return HttpResponse("Internal Server Error:"+e, status=500)
        else:
            return HttpResponse("You need to log in first to POST to inboxes.", status=401)

    def delete(self, request, *args, **kwargs):
        """
        Clear the inbox; delete all InboxItems from the authenticated author.
        """
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)
        if request.user.is_authenticated and str(request.user.id) == author_id:
            inbox_items = InboxItem.objects.filter(author=request.user.id)
            # NOTE: does not check to see if Inbox is already empty
            inbox_items.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse("You need to log in first to delete your inbox.", status=401)


