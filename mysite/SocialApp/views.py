import datetime, uuid, requests, json

from requests.auth import HTTPBasicAuth

from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView, status
from .forms import SignUpForm, LoginForm
from requests.auth import HTTPBasicAuth

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.html import escape
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Author, Post, Comment,ObjectLike, InboxItem, Followers, ForeignServer, RemoteFollow, RemoteFollowers
from .admin import AuthorCreationForm
from .forms import SignUpForm, LoginForm, PostForm, CommentForm

from .utils import AuthorToJSON, PostToJSON, CommentToJSON, CommentListToJSON, StringListToPostCategoryList, AuthorListToJSON, PostListToJSON, InboxItemToJSON , FollowerFinalJSON, ValidateForeignPostJSON, ObjectLikeToJSON, ObjectLikeListToJSON, FriendRequestToJson, GetURLBasicAuth

from django.views import generic
from django.views import View
from django.urls import reverse_lazy
import uuid

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


from .forms import PostForm, CommentForm, SharedPostForm

class UserRegisterView(generic.CreateView):
    form_class = AuthorCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')


class UpdateProfile(UpdateView):
    model = Author
    template_name = "editProfile.html"
    fields = ['username', 'github']
    success_url = reverse_lazy('author')


class HomeView(ListView):
    model = Post
    template_name = 'author.html'
    ordering = ['-published']
"""
class GithubView(View):
	model = Author
	template_name = 'githubDetails.html'
"""

class PostDetailView(DetailView):
    model = Post
    template_name = 'PostDetails.html'


class AddPostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'AddPost.html'
    success_url = reverse_lazy('author')

    """
    # this is to redicrect to the appropriate pages
    def get(self, request):
        form = PostForm()
        if form.is_valid():
            vis = form.cleaned_data['visibility']
    """


class AddCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'AddComment.html'
    #fields = '__all__'
    success_url = reverse_lazy('author')

    def form_valid(self, form):
        form.instance.post = Post.objects.get(pk=self.kwargs["pk"])
        author_json = AuthorToJSON(self.request.user)
        if (author_json):
            form.instance.author_json = author_json
        return super().form_valid(form)


class UpdatePostView(UpdateView):
    model = Post
    template_name = 'EditPost.html'
    fields = ['title', 'description', 'content']
    success_url = reverse_lazy('author')


class DeletePostView(DeleteView):
    model = Post
    template_name = 'DeletePost.html'
    success_url = reverse_lazy('author')


def like(request):
    try:
        # add a line to database that has user url and object url
        like = ObjectLike.objects.filter(author_url=request.POST["author_url"], object_url=request.POST["object_url"])
        liked = len(like)
        if liked == 0:
            liked_object = ObjectLike(author_url=request.POST["author_url"], author_json=json.dumps(AuthorToJSON(request.user)), object_url=request.POST["object_url"])
            liked_object.save()
            # Notify the author of the liked post by POSTing this to their inbox.
            # Remember, we might be posting to a foreign node here.
            # Also, `object` might be foreign too. We need its author, though.
            like_json = ObjectLikeToJSON(liked_object)

            basic_auth = GetURLBasicAuth(request.POST["object_url"])
            response = None
            if (basic_auth):
                response = requests.get(request.POST["object_url"], auth=basic_auth)
            else:
                response = requests.get(request.POST["object_url"])

            if response.ok:
                author_url = response.json()["author"]["url"]
                if author_url[-1] == "/":
                    author_url += "inbox/"
                else:
                    author_url += "/inbox/"
                
                basic_auth2 = GetURLBasicAuth(author_url)
                response2 = None
                if (basic_auth2):
                    response2 = requests.post(author_url, json=like_json, auth=basic_auth2)
                else:
                    response2 = requests.post(author_url, json=like_json)
            else:
                # `object` is probably behind authentication or something
                print("Couldn't get object. "+str(res.text))
        else:
            like.delete()
    except:
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remoteComment(request):
    """
    Handles posting a comment to a foreign source
    """
    try:
        comment_json = {
            "type": "comment",
            "author": AuthorToJSON(request.user),
            "comment": request.POST["comment"],
            "contentType": request.POST["content_type"]
        }
        post_url = request.POST["post_url"]
        if post_url[-1] == "/":
            post_url += "comments/"
        else:
            post_url += "/comments/"

        basic_auth = GetURLBasicAuth(post_url)
        if (basic_auth):
            requests.post(post_url, json=comment_json, auth=basic_auth)
        else:
            requests.post(post_url, json=comment_json)
    except:
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def home(request):
    return render(request, 'home.html', {})

def author(request):
    return render(request, 'author.html', {})

def newPost(request):
    return render(request, 'newPost.html', {})

def inbox(request):
    """
    Request all of the inbox items using our API endpoint and render out.
    """
    # Martijn Pieters https://stackoverflow.com/a/13569789
    logurl = request.scheme+"://"+request.get_host()+"/SocialApp/login/"
    session = requests.Session()
    session.get(logurl) # Sets cookie
    if 'csrftoken' in session.cookies:
        csrftoken = session.cookies['csrftoken']
    else: print("No CSRF cookie found")
    sessionid = request.COOKIES.get('sessionid') # FBI OPEN UP
    if not sessionid:
        print("No sessionid cookie found")
    cookies = dict(csrftoken=csrftoken, sessionid=sessionid)
    # Now GET the inbox endpoint and pass in our cookies
    url = request.scheme+"://"+request.get_host()+"/author/"+str(request.user.id)+"/inbox/"
    resp = session.get(url, cookies=cookies, headers=dict(Referer=logurl))
    # Pass the resulting inbox items to the template if successful
    if resp.status_code == 200:
        inbox_json = dict(resp.json())
        inbox_items = inbox_json["items"]
        return render(request, 'inbox.html', {"inbox_items":inbox_items, "userid":str(request.user.id)})
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
            author_json = AuthorListToJSON(Author.objects.exclude(is_staff=True).exclude(is_server=True))
            return JsonResponse({"authors":author_json})
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
        author_json = AuthorToJSON(author)
        if author_json:
            return JsonResponse(author_json)
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
        if request.user != author:
            return HttpResponse(status=401)

        # Update author info
        jsonData = request.data

        username = jsonData.get("displayName", "")
        github = jsonData.get("github", "")

        if (username != "" and github != ""):
            try:
                author.username = username
                author.github = github
                author.save()
                return HttpResponse(status=200)
            except:
                return HttpResponseRedirect(status=500)
        else:
            return HttpResponse(status=400)
        

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
            post_list_json = PostListToJSON(Post.objects.all())
            return JsonResponse({"posts":post_list_json})
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

        post_json = PostToJSON(post)
        if post_json:
            return JsonResponse(post_json)
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
        if request.user != author:
            return HttpResponse(status=401)

        jsonData = request.data

        title = jsonData.get("title", "")
        description = jsonData.get("description", "")
        content_type = jsonData.get("contentType", "")
        content = jsonData.get("content", "")
        visibility = jsonData.get("visibility", "PUBLIC")
        unlisted = bool(jsonData.get("unlisted", "false"))
        categories = jsonData.get("categories", "")

        if (content_type != ""):
            try:
                post.title = title
                post.description = description
                post.content_type = content_type
                post.content = content
                post.visibility = visibility
                post.unlisted = unlisted
                post.categories.set(StringListToPostCategoryList(categories))
                post.save()
                return HttpResponse(status=200)
            except:
                return HttpResponse(status=500)
        else:
            return HttpResponse(status=400)


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
        if request.user != author:
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
        if request.user != author:
            return HttpResponse(status=401)

        jsonData = request.data

        title = jsonData.get("title", "")
        description = jsonData.get("description", "")
        content_type = jsonData.get("contentType", "")
        content = jsonData.get("content", "")
        visibility = jsonData.get("visibility", "PUBLIC")
        unlisted=bool(jsonData.get("unlisted", "false"))

        if content_type != "":
            try:
                post = Post(id=post_id, title=title, description=description, content_type=content_type, content=content,
                            author=author, visibility=visibility, unlisted=unlisted)
                post.save()
                return HttpResponse(status=200)
            except:
                return HttpResponse(status=500)
        else:
            return HttpResponse(status=400)


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
            post_list_json = PostListToJSON(posts)
            return JsonResponse({"posts":post_list_json})
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
        if request.user != author:
            return HttpResponse(status=401)

        jsonData = request.data

        title = jsonData.get("title", "")
        description = jsonData.get("description", "")
        content_type = jsonData.get("contentType", "")
        content = jsonData.get("content", "")
        visibility = jsonData.get("visibility", "PUBLIC")
        unlisted=bool(jsonData.get("unlisted", "false"))

        if content_type != "":
            try:
                post = Post(title=title, description=description, content_type=content_type, content=content,
                            author=author, visibility=visibility, unlisted=unlisted)
                post.save()
                return HttpResponse(status=200)
            except:
                return HttpResponse(status=500)
        else:
            return HttpResponse(status=400)


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

        comment_json_list = CommentListToJSON(Comment.objects.filter(post=post))

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

        jsonData = request.data
        
        author = jsonData.get("author", "")
        author_url = ""
        if (author != ""):
            author_url = author.get("url", "")
        comment = jsonData.get("comment")
        content_type = jsonData.get("contentType")

        valid_content_type = False
        if (content_type == "text/plain" or content_type == "text/markdown"):
            valid_content_type = True

        if (author_url != "" and comment != "" and valid_content_type):
            try:
                comment = Comment(author_url=author_url, author_json=json.dumps(author), post=post, comment=comment, content_type=content_type)
                comment.save()
                return HttpResponse(status=200)
            except:
                return HttpResponse(status=500)
        else:
            return HttpResponse(status=400)


class CommentEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET request for a specific comment
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

        comment_id = kwargs.get("comment_id", -1)
        if comment_id == -1:
            return HttpResponse(status=400)

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        comment_json = CommentToJSON(comment)
        if comment_json:
            return JsonResponse(comment_json)
        else:
            return HttpResponse(status=500)


class PostLikesEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/{POST_ID}/likes/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET request for the likes on a post
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

        likes_json_list = ObjectLikeListToJSON(ObjectLike.objects.filter(object_url=post.url))

        return JsonResponse({"likes":likes_json_list})


class CommentLikesEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}/likes/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET request for the likes on a comment
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

        comment_id = kwargs.get("comment_id", -1)
        if comment_id == -1:
            return HttpResponse(status=400)

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponse(status=400)

        likes_json_list = ObjectLikeListToJSON(ObjectLike.objects.filter(object_url=comment.url))

        return JsonResponse({"likes":likes_json_list})


class AuthorLikedEndpoint(APIView):
    """
    The author/{AUTHOR_ID}/liked/ endpoint
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to return the author's likes
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

        try:
            likes = ObjectLikeListToJSON(ObjectLike.objects.filter(author_url=author.url))
            return JsonResponse({"likes":likes})
        except:
            return HttpResponse(status=500)


def followerView(request): #TODO get remote followers too
    """
    View shows a list of all the follow/friend requests to the signed in author
    """    
    current_author_id = request.user.id
    current_author = Author.objects.get(pk=current_author_id)
    followers = []
    followers_list = current_author.followee.all() #all the people currently following this user

    #all the people that the user currently follows 
    following = current_author.following.all()
    following_list = []

    for author in following:
        following_list.append(author.author_to)

    for follower in followers_list:
        if follower.author_from in following_list:
            pass
        else:
            followers.append(follower)

    #get remote authors too 
    remote_followers = current_author.remote_followers.all()
    author_remote_following = current_author.remote_following.all()

    remote_following_url = []
    for remote_following in author_remote_following:
                remote_following_url.append(remote_following.remote_author_to)

    remote_list = []
    if remote_followers:
        #get all authors in remote
        for server in ForeignServer.objects.filter(is_active=True):
            authors = None
            try:
                    authors = requests.get(server.authors_url).json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                # Do nothing on connection failure
                pass
            except requests.exceptions.HTTPError:
                # Do nothing on HTTP error
                pass
        if authors:
            for remote_url in remote_followers:
                #check if not friends
                if remote_url.remote_author_from not in remote_following_url:
                    for author in authors:
                        if author["url"] == remote_url.remote_author_from:
                            remote_list.append(author)

    if not followers:
       is_empty = True
    else:
        is_empty = False

    return render(request, 'followers.html', {"followers":followers, 'is_empty': is_empty, "remoteFollowers":remote_list})


def githubView(request, username=None):
    """
    View modifies github username and passes link for github activity image
    """   
    try:
    	username = request.POST["username"]
    except:
    	pass

            
    if username:
        url = f"https://api.github.com/users/{username}"
        r = requests.get(url.format(username)).json()
        if "message" in r:
            if r["message"] == "Not Found":
                return render(request, 'githubDetails.html', {'is_empty': True, 'is_correct': False})
                
        imgString = f"https://grass-graph.moshimo.works/images/{username}.png"
        return render(request, 'githubDetails.html', {"username":username, "url":imgString, 'is_empty': False})
    
    else:
        return render(request, 'githubDetails.html', {'is_empty': True, 'is_correct':True})


def findFollower(request):
    """
    View shows a list of all the authors and allows following (sending a friend request to) any author
    """ 
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
    """
    allows following of an author in the system 
    """ 
    #add new follower and return followers list with new follower included
    #TODO authenticate follower addition
    #TODO check correct save
    foreign_author =  Author.objects.get(pk=foreign_author_id)
    current_author_id = request.user.id
    current_author =  Author.objects.get(pk=current_author_id)

    if current_author_id == foreign_author_id:
            following = False
            return render(request, 'addFollower.html', {"foreign_author":foreign_author, 'new_follower':following} )

    new_follower = Followers.objects.create(author_from=current_author, author_to=foreign_author)
    following = True
    #send friend request through inbox

    return render(request, 'addFollower.html', {"foreign_author":foreign_author, 'new_follower':following} )


def friendsView(request):
    """
    Shows a list of all the people that are friends with the current author
    """ 
    current_author_id = request.user.id
    current_author = Author.objects.get(pk=current_author_id)
    friends = []
    current_followers_list = current_author.followee.all() #all the people currently following this user

    #all the people that the user currently follows
    current_following = current_author.following.all()
    current_following_list = []

    for author in current_following:
        current_following_list.append(author.author_to)

    for follower in current_followers_list:
        if follower.author_from in current_following_list:
            friends.append(follower)

    #add remote friends 
    remote_friends_list = []
    remote_friends = []
    remote_following_query = current_author.remote_following.all()  

    remote_following =[]
    for following in remote_following_query:
        remote_following.append(following.remote_author_to) 

    #all the remote followers
    remote_follower_query = current_author.remote_followers.all()
    for remote_follower in remote_follower_query:
        if remote_follower.remote_author_from in remote_following:
            remote_friends.append(remote_follower.remote_author_from)

    for server in ForeignServer.objects.filter(is_active=True):
        authors = None
        try:
                authors = requests.get(server.authors_url).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Do nothing on connection failure
            pass
        except requests.exceptions.HTTPError:
            # Do nothing on HTTP error
            pass

        if authors:
            for friend in remote_friends:
                for remote_author in authors:
                        if remote_author["url"] == friend:
                            remote_friends_list.append(remote_author)


    if not friends and not remote_friends_list:
       is_empty = True
    else:
        is_empty = False

    return render(request, 'friends.html', {"friends":friends, 'is_empty': is_empty, "remoteFriends":remote_friends_list} )


def unFollow(request, foreign_author_id): 
    """ 
    un follow an author 
    """
    foreign_author =  Author.objects.get(pk=foreign_author_id)
    current_author_id = request.user.id
    current_author =  Author.objects.get(pk=current_author_id)
    current_follower = current_author.following.filter(author_to=foreign_author)

    # can only delete someone that you were following
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

    return friendsView(request)


def remotePosts(request):
    """
    Display public posts on all added servers
    """
    public_posts = []
    for server in ForeignServer.objects.filter(is_active=True):
        posts = None
        try:
            if server.username and server.password:
                posts = requests.get(server.posts_url, auth=HTTPBasicAuth(server.username, server.password)).json()
            else:
                posts = requests.get(server.posts_url).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Do nothing on connection failure
            pass
        except requests.exceptions.HTTPError:
            # Do nothing on HTTP error
            pass
        
        # Append PUBLIC posts to our collection
        if posts:
            clean_posts = []
            if server.posts_json_key:
                for post in posts[server.posts_json_key]:
                    if ValidateForeignPostJSON(post):
                        if post["visibility"] == "PUBLIC":
                            clean_posts.append(post)
            else:
                for post in posts:
                    if ValidateForeignPostJSON(post):
                        if post["visibility"] == "PUBLIC":
                            clean_posts.append(post)

            if clean_posts:
                public_posts.append({"name": server.host_name, "posts":clean_posts})

    return render(request, 'remote_posts.html', {"all_posts":public_posts, "has_content":len(public_posts) > 0})


def findRemoteFollowers(request):
    """
    list all the remote Followers for the author
    """
    final_authorlist = []
    is_empty = True
    for server in ForeignServer.objects.filter(is_active=True):
        authors = None
        try:
            authors = requests.get(server.authors_url).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Do nothing on connection failure
            pass
        except requests.exceptions.HTTPError:
            # Do nothing on HTTP error
            pass

        if authors:
            try:
                is_empty = False
                #check if current author already follows some of them
                current_author_id = request.user.id
                current_author =  Author.objects.get(pk=current_author_id)

                #all the people the current user is following on remote
                following = []
                following_query = current_author.remote_following.all()  

                for follower in following_query:
                    following.append(follower.remote_author_to) 

                #all the remote followers
                follower_query = current_author.remote_followers.all()
                for remote_follower in follower_query:
                    following.append(remote_follower.remote_author_from)
            
                for author in authors:
                    if author["url"] in following:
                        pass
                    else:
                        final_authorlist.append(author) 
            except:
                pass

    return render(request, 'findRemoteFollower.html', {"remote_authors":final_authorlist,'is_empty':is_empty })


def addRemoteFollower(request, remote_author_id):
    """
    Follow a remote follower and send friend request to their inbox endpoint
    """
    #TODO handle when unique fails cleanly

    for server in ForeignServer.objects.filter(is_active=True):
        authors = None
        try:
            authors = requests.get(server.authors_url).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Do nothing on connection failure
            pass
        except requests.exceptions.HTTPError:
            # Do nothing on HTTP error
            pass

        if authors:
            try:
                for author in authors:
                    if author["id"] == remote_author_id:
                        remote_author = author
                
                if not remote_author:
                    is_new_follower = False
                    return render(request, 'addRemoteFollower.html', {"remote_author":None, 'new_follower':is_new_follower} )

                local_author_id = request.user.id
                local_author =  Author.objects.get(pk=local_author_id)

                if local_author_id == remote_author_id:
                    is_new_follower = False
                    return render(request, 'addRemoteFollower.html', {"remote_author":remote_author, 'new_follower':is_new_follower} )

                #Create Json friend request to send to inbox endpoint 
                requesting_author = AuthorToJSON(local_author)
                requested_author = remote_author #AuthorToJSON(remote_author)

                friend_json = FriendRequestToJson(requesting_author, requested_author)
                
                if friend_json:  
                    # print(friend_json)
                    inbox_endpoint = server.authors_url + remote_author_id + "/inbox/"
                    send_request_json = requests.post(inbox_endpoint, auth=HTTPBasicAuth(server.username, server.password), json=friend_json)
                    if send_request_json.status_code == 200:
                        #create record of follow 
                        remote_author_url = remote_author['url']
                        remote_follow = RemoteFollow.objects.create(local_author_from=local_author, remote_author_to=remote_author_url)
                        is_new_follower = True
        
                        return render(request, 'addRemoteFollower.html', {"remote_author":remote_author, 'new_follower':is_new_follower})
                    else:
                        return HttpResponse(status=500)
                else:
                    return HttpResponse(status=500)
            except:
                pass


def unFollowRemote(request, remote_author_id):
    """ 
    un follow a remote author 
    """
    # foreign_author =  Author.objects.get(pk=foreign_author_id)
    current_author_id = request.user.id
    current_author =  Author.objects.get(pk=current_author_id)

    for server in ForeignServer.objects.filter(is_active=True):
        authors = None
        try:
                authors = requests.get(server.authors_url).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Do nothing on connection failure
            pass
        except requests.exceptions.HTTPError:
            # Do nothing on HTTP error
            pass

        if authors:
            for author in authors:
                if author["id"] == remote_author_id:
                    remote_author_url = author["url"]

    if remote_author_url:
        friend_endpoint = server.authors_url + remote_author_id + "/followers/" + str(current_author.id)
        delete_request = requests.delete(friend_endpoint, auth=HTTPBasicAuth(server.username, server.password))
        if delete_request.status_code == 200:
            current_follower = current_author.remote_following.filter(remote_author_to=remote_author_url)

            # can only delete someone you were following 
            if current_follower.exists():
                current_follower.delete()

            return friendsView(request)

        else:
            return HttpResponse(status=500)


class EditFollowersEndpoint(APIView): 

    """
    The author/<str:author_id>/followers/<str:foreign_author_id>/ endpoint
    """

    def get(self, request, *args, **kwargs):
        """
        Check if a remote author is a follower of a local author
        """
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

        #get the foreign author object 
        for server in ForeignServer.objects.filter(is_active=True):
            authors = None
            try:
                authors = requests.get(server.authors_url).json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                # Do nothing on connection failure
                pass
            except requests.exceptions.HTTPError:
                # Do nothing on HTTP error
                pass

            if authors:
                for remote_author in authors:
                    author_url = remote_author["url"].split("/")
                    if author_url[-1] == foreign_author_id:
                        foreign_author = remote_author

        try:
            remote_follower = author.remote_followers.filter(remote_author_from=foreign_author["url"])
        except:
            return HttpResponse(status=400)
        if not author:
            return HttpResponse(status=404)


        if author_id == foreign_author_id:
            return HttpResponse(status=400)

        if remote_follower:
            return JsonResponse(foreign_author)
        else:
            return HttpResponse(status=500)



    def put(self, request, *args, **kwargs):  
        """
        Follower a specific Author (Friend Request) from remote to local
        """
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


        #get the foreign author object 
        for server in ForeignServer.objects.filter(is_active=True):
            authors = None
            try:
                authors = requests.get(server.authors_url).json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                # Do nothing on connection failure
                pass
            except requests.exceptions.HTTPError:
                # Do nothing on HTTP error
                pass

            if authors:
                for remote_author in authors:
                    author_url = remote_author["url"].split("/")
                    if author_url[-1] == foreign_author_id:
                        foreign_author = remote_author  #MAKE SURE THEY EXIST 

        #if author ID same as foreign_author_id bad request since you cannot follow yourself
        if author_id == foreign_author_id:
            return HttpResponse(status=400)
        
        #check if already a follower first 
        is_current_follower = author.remote_followers.filter(remote_author_from=foreign_author["url"])
        if is_current_follower.exists():
            return HttpResponse(status=400)

        else:
            try:
                new_follow = RemoteFollowers.objects.create(local_author_to=author, remote_author_from=foreign_author["url"])
                return HttpResponse(status=200)
            except:
                return HttpResponse(status=500)

    def delete(self, request, *args, **kwargs):
        """
        Stop following an Author
        """
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


        current_follower = current_author.remote_followers.filter(remote_author_from=remote_author_url)

        # can only delete someone that was following you  
        if current_follower.exists():
            current_follower.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
            

class GetFollowersEndpoint(APIView):
    """ 
    Get all the Authors following a specific user
    """
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

        follower_json_list = []

        followers_list = author.followed_by.all()

        for follower in followers_list:
            follower_json = AuthorToJSON(follower)
            follower_json_list.append(follower_json)

        
        #get remote authors too 
        remote_followers = author.remote_followers.all()
        author_remote_following = author.remote_following.all()

        remote_following_url = []
        for remote_following in author_remote_following:
                    remote_following_url.append(remote_following.remote_author_to)

        remote_list = []
        if remote_followers:
            #get all authors in remote
            for server in ForeignServer.objects.filter(is_active=True):
                authors = None
                try:
                        authors = requests.get(server.authors_url).json()
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    # Do nothing on connection failure
                    pass
                except requests.exceptions.HTTPError:
                    # Do nothing on HTTP error
                    pass
            if authors:
                for remote_url in remote_followers:
                    #check if not friends
                    if remote_url.remote_author_from not in remote_following_url:
                        for author in authors:
                            if author["url"] == remote_url.remote_author_from:
                                remote_list.append(author)


        for remote_follower in remote_list:
            follower_json_list.append(remote_follower)

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
        if request.user.is_authenticated and (str(request.user.id) == author_id or request.user.is_server):
            # Get inbox items and format into JSON to return
            inbox_items = InboxItem.objects.filter(author=author)
            item_json_list = []
            for item in inbox_items:
                inbox_json = InboxItemToJSON(item)
                if inbox_json:
                    item_json_list.append(inbox_json)
            response_json = {
                "type":"inbox",
                "author": author.url,
                "items": item_json_list
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
        #if request.user.is_authenticated: # only logged in users can POST to inboxes
        link_field = request.data.get("link", "")
        if link_field != "":
            # Handle as a link to the item
            try:
                new_item = InboxItem(author=author, link=request.data.get("link"))
                new_item.save()
                return HttpResponse(status=201)
            except Exception as e:
                print(e)
                return HttpResponse("Internal Server Error:"+str(e), status=500)
        else:
            # Handle POSTed object as JSON string
            try:
                json_data = request.data
                received_json_str = json.dumps(json_data)          
                # Save Likes we don't have yet (from foreign nodes)
                if json_data["type"] == "Like" or json_data["type"] == "like":
                    like = ObjectLike.objects.filter(author_url=json_data["author"]["url"], object_url=json_data["object"])
                    if len(like) == 0:
                        new_like = ObjectLike(author_url=json_data["author"]["url"], author_json=json.dumps(json_data["author"]), object_url=json_data["object"])
                        new_like.save()
                
                #Save a Remote Follow 
                if json_data["type"] == "Follow" or json_data["type"] == "follow":
                    remote_follower = RemoteFollowers.objects.filter(remote_author_from=json_data["actor"]["url"], local_author_to=json_data["object"])
                    if RemoteFollowers.DoesNotExist:
                        new_remote_follower = RemoteFollowers.objects.create(remote_author_from=json_data["actor"]["url"],  local_author_to=json_data["object"])

                new_item = InboxItem(author=author, json_str=received_json_str)
                new_item.save()
                return HttpResponse(status=201)
            except Exception as e:
                print(str(e))
                return HttpResponse("Internal Server Error:"+str(e), status=500)
        #else:
        #    return HttpResponse("You need to log in first to POST to inboxes.", status=401)

    def delete(self, request, *args, **kwargs):
        """
        Clear the inbox; delete all InboxItems from the authenticated author.
        """
        author_id = kwargs.get("author_id", -1)
        if author_id == -1:
            return HttpResponse(status=400)
        if request.user.is_authenticated and str(request.user.id) == author_id:
            inbox_items = InboxItem.objects.filter(author=request.user.id)
            # Doesn't care if the inbox is already empty
            inbox_items.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse("You need to log in first to delete your inbox.", status=401)


# passing posts and friends to the friend post template (newMessage)
# everything except the last line is basically a copy of the friends
# template, will find a way to get rid of duplicate codes!
def posts_view(request):
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

    return render(request, "newMessage.html", {'posts': (Post.objects.all()).filter(visibility='FRIENDS').order_by('-published'),
                                                "friends":friends, 'is_empty': is_empty })

# pre-populate the form
# I made a different customized from because I wanted to hide the fields
# from the user, so they can't edit the content, but they have the choice of 
# changing the visibility
def shared_post(request, pk):
    try:
        sharing_author = request.user
        post = get_object_or_404(Post, id=pk)
        friends = []
        # all the people currently following this user
        current_followers_list = sharing_author.followee.all()
        #all the people that the user currently follows
        current_following = sharing_author.following.all()
        current_following_list = []

        for author in current_following:
            current_following_list.append(author.author_to)

        for follower in current_followers_list:
            if follower.author_from in current_following_list:
                friends.append(follower)

        if friends:
            for friend in friends:
                inbox_url = friend.author_from.url
                if inbox_url[-1] == "/":
                    inbox_url += "inbox/"
                else:
                    inbox_url += "/inbox/"

                basic_auth = GetURLBasicAuth(inbox_url)
                if (basic_auth):
                    requests.post(inbox_url, json=PostToJSON(post), auth=basic_auth)
                else:
                    requests.post(inbox_url, json=PostToJSON(post))
    except:
        pass

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
