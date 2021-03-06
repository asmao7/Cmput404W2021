"""
Contains useful helper functions
"""
import requests, json
from requests.auth import HTTPBasicAuth
from .models import Author, Post, Comment, PostCategory, InboxItem, Followers, ForeignServer

def AuthorToJSON(author):
    """
    Converts an Author object into a JSON-compatible dictionary.
    Returns None on failure.
    """
    if not author:
        return None
    try:
        json_dict = {
            "type":"author",
            "id":author.url,
            "host":author.host,
            "displayName":author.username,
            "url":author.url,
            "github":author.github
        }
        return json_dict
    except:
        return None


def AuthorListToJSON(authors):
    """
    Converts a list of Author objects into a JSON-compatible list
    of Authors. Returns an empty list on failure.
    """
    if not authors:
        return []
    try:
        author_list = []
        for author in authors:
            test_json = AuthorToJSON(author)
            if test_json:
                author_list.append(test_json)
        return author_list
    except:
        return []


# TODO: Fill out size and paginate
def PostToJSON(post):
    """
    Converts a Post object into a JSON-compatible dictionary.
    Return None on failure.
    """
    if not post:
        return None

    try:
        json_dict = {
            "type":"post",
            "title":post.title,
            "id":post.url,
            "source":post.url,
            "origin":post.url,
            "description":post.description,
            "contentType":post.content_type,
            "content":post.content,
            "author":AuthorToJSON(post.author),
            "categories":PostCategoryListToStringList(post.categories),
            "count":Comment.objects.filter(post=post).count(),
            "size":0,
            "comments":CommentListToJSON(Comment.objects.filter(post=post)),
            "published":str(post.published),
            "visibility":post.visibility,
            "unlisted":post.unlisted
        }
        return json_dict
    except:
        return None

def FollowerFinalJSON(follower_list):
    """
    Converts Followe object into a JSON-compatible dictionary.
    Returns an empty list on failure.
    """
    if not follower_list:
        json_dict = {
            "type":"followers",
            "items": []
        }
        return json
    try:
        json_dict = {
            "type":"followers",
            "items": follower_list
        }
        return json_dict
    except:
        json_dict = {
            "type":"followers",
            "items": []
        }
        return json_dict


def PostListToJSON(posts):
    """
    Converts a list of Post objects into a JSON-compatible list
    of Posts. Returns an empty list on failure.
    """
    if not posts:
        return []
    try:
        post_list = []
        for post in posts:
            test_json = PostToJSON(post)
            if test_json:
                post_list.append(test_json)
        return post_list
    except:
        return []


def CommentToJSON(comment):
    """
    Converts a Comment object into a JSON-compatible dictionary.
    Return None on failure.
    """
    if not comment:
        return None

    if not comment.author_json:
        return None

    # Used to fetch updated author representation to attach to a comment
    # Was too slow in practice (heroku servers take a long time to wake up if they haven't had a request in a while), so our data can get stale now
    try:
        #basic_auth = GetURLBasicAuth(comment.author_url)
        #response = None
        #if (basic_auth):
            #response = requests.get(comment.author_url, auth=basic_auth)
        #else:
            #response = requests.get(comment.author_url)

        #author = None

        #if response.ok:
            #try:
                #author = response.json()
            #except:
                #pass

        author = json.loads(comment.author_json)

        if (author):
            json_dict = {
                "type":"comment",
                "author":author,
                "comment":comment.comment,
                "contentType":comment.content_type,
                "published":str(comment.published),
                "id":comment.url
            }
            return json_dict
        else:
            return None
    except:
        return None


def CommentListToJSON(comments):
    """
    Converts a list of Comment objects into a JSON-compatible list
    of Comments. Returns an empty list on failure.
    """
    if not comments:
        return []
    try:
        comment_list = []
        for comment in comments:
            test_json = CommentToJSON(comment)
            if test_json:
                comment_list.append(test_json)
        return comment_list
    except:
        return []


def ObjectLikeToJSON(like):
    """
    Converts a like on an object to JSON
    """
    if not like:
        return None
    
    if not like.author_json:
        return None

    # Used to fetch updated author representation for likes
    # this is slow, so we stopped doing it and rely on stale data for likes
    try:
        # basic_auth = GetURLBasicAuth(like.author_url)
        # response = None
        # if (basic_auth):
            # response = requests.get(like.author_url, auth=basic_auth)
        #else:
            #response = requests.get(like.author_url)

        #if response.ok:
            #author = response.json()

        author = json.loads(like.author_json)
        
        if (author):
            json_dict = {
                "summary": "{} Likes your content".format(author["displayName"]),
                "type": "Like",
                "author": author,
                "object": like.object_url
            }
            return json_dict
        else:
            return None
    except:
        return None


def ObjectLikeListToJSON(likes):
    """
    Converts a list of ObjectLike objects into a JSON-compatible list
    of likes. Returns an empty list on failure.
    """
    if not likes:
        return []
    try:
        likes_list = []
        for like in likes:
            test_json = ObjectLikeToJSON(like)
            if test_json:
                likes_list.append(test_json)
        return likes_list
    except:
        return []


def PostCategoryListToStringList(categories):
    """
    Converts a collection of Category objects into a JSON-compatible
    list of strings. Return empty list on failure.
    """
    if not categories:
        return []
    try:
        category_list = []
        for category in categories:
            category_list.append(category.name)
        return category_list
    except:
        return []


def StringListToPostCategoryList(category_list):
    """
    Converts a list of strings into ORM categories. Will add
    new categories to the database if they do not exist.
    Return empty list on failure.
    """
    if not category_list:
        return []
    try:
        categories = []
        for category in category_list:
            try:
                test_cat = PostCategory.objects.get(name=category)
                categories.append(test_cat)
            except:
                test_cat = PostCategory.objects.create(name=category)
                categories.append(test_cat)
        return categories
    except:
        return []

      
def InboxItemToJSON(item):
    """
    Converts an InboxItem object into a JSON-compatible dictionary.
    Prefers to just use a json string. If `item` has something in its `link` 
    field, request the InboxItem's link and rely on APIs to return the 
    right JSONs. Recommended to just use `json_str`.
    Returns a placeholder dictionary on failure.
    item - an InboxItem object
    """
    if not item:
        return None
    placeholder = {
        "type":"",
        "title":"Something went wrong.",
        "id":"",
        "source":"",
        "origin":"",
        "description":"There was a shared item here, but we couldn't retrieve it.",
        "contentType":"text/plain",
        "content":"",
        "author":{},
        "categories":"",
        "count":0,
        "size":0,
        "comments":"",
        "published":"",
        "visibility":"PUBLIC",
        "unlisted":True
    }
    if item.link != "" and item.json_str == "":
        try:
            r = requests.get(item.link)
            d = r.json() # returns JSON, not Dict
            return d
        except Exception as e:
            # Can't get the object from `link` eg. doesn't exist
            print(e)
            placeholder["id"] = item.link
            placeholder["content"] = str(e)
            return placeholder
    else:
        # Use json_str instead
        try:
            d = json.loads(item.json_str)
            return d
        except Exception as e:
            print(e)
            placeholder["content"] = str(e)
            return placeholder


def FriendRequestToJson(requesting_author, requested_author):
    """
    Converts a Friend Request object into a JSON-compatible dictionary.
    Return None on failure.
    """
    if not requesting_author:
        return None

    if not requested_author:
        return None

    try:
        json_dict = {
            "type":"Follow",
            "summary": requesting_author['displayName'] + " wants to follow " + requested_author['displayName'],
            "actor":requesting_author,
            "object":requested_author,
            
        }
        return json_dict
    except:
        return None


def ValidateForeignPostJSON(post):
    """
    Returns True if JSON conforms to the correct specs. Returns false otherwise.
    """
    if "title" not in post:
        return False

    if "visibility" not in post:
        return False

    if "contentType" not in post:
        return False

    if "content" not in post:
        return False

    if "author" not in post:
        return False

    contentType = post["contentType"]
    if(contentType != "text/plain" and contentType != "text/markdown" and
       contentType != "application/base64" and contentType != "image/png;base64" and
       contentType != "image/jpeg;base64"):
       return False

    for comment in post["comments"]:
        commentContentType = comment["contentType"]
        if (commentContentType != "text/plain" and commentContentType != "text/markdown"):
            return False
       
    return True


def GetURLBasicAuth(url):
    """
    Gets basic auth credentials for this URL
    """
    for server in ForeignServer.objects.all():
        if server.host_name:
            if server.host_name in url and server.username and server.password:
                return HTTPBasicAuth(server.username, server.password)