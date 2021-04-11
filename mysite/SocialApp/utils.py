"""
Contains useful helper functions
"""
import requests
from .models import Author, Post, Comment, PostCategory, InboxItem, Followers

def AuthorToJSON(author):
    """
    Converts an Author object into a JSON-compatible dictionary.
    Returns None on failure.
    """
    if not author:
        return None
    try:
        json = {
            "type":"author",
            "id":author.url,
            "host":author.host,
            "displayName":author.username,
            "url":author.url,
            "github":author.github
        }
        return json
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
        json = {
            "type":"post",
            "title":post.title,
            "id":post.url,
            "source":post.source,
            "origin":post.origin,
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
        return json
    except:
        return None

def FollowerFinalJSON(follower_list):
    """
    Converts Followe object into a JSON-compatible dictionary.
    Returns an empty list on failure.
    """
    if not follower_list:
        json = {
            "type":"followers",
            "items": []
        }
        return json
    try:
        json = {
            "type":"followers",
            "items": follower_list
        }
        return json
    except:
        json = {
            "type":"followers",
            "items": []
        }
        return json


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
    try:
        json = {
            "type":"comment",
            "author":AuthorToJSON(comment.author),
            "comment":comment.comment,
            "contentType":comment.content_type,
            "published":str(comment.published),
            "id":comment.url
        }
        return json
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


def PostLikeToJSON(like):
    """
    Converts a like on a post to JSON
    """
    if not like:
        return None
    try:
        json = {
            "type": "Like",
            "author": AuthorToJSON(like.user_id),
            "object": like.post_id.url
        }
        return json
    except:
        return None


def PostLikeListToJSON(likes):
    """
    Converts a list of LikePost objects to a JSON-compatible list
    of likes. Returns an empty list on failure.
    """
    if not likes:
        return []
    try:
        likes_list = []
        for like in likes:
            test_json = PostLikeToJSON(like)
            if test_json:
                likes_list.append(test_json)
        return likes_list
    except:
        return []


def CommentLikeToJSON(like):
    """
    Converts a like on a comment to JSON
    """
    if not like:
        return None
    try:
        json = {
            "type": "Like",
            "author": AuthorToJSON(like.user_id),
            "object": like.comment_id.url
        }
        return json
    except:
        return None


def CommentLikeListToJSON(likes):
    """
    Converts a list of CommentPost objects to a JSON-compatible list
    of likes. Returns an empty list on failure.
    """
    if not likes:
        return []
    try:
        likes_list = []
        for like in likes:
            test_json = CommentLikeToJSON(like)
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
    Request the InboxItem's link and rely on APIs to return the right JSONs.
    eg. see SocialApp.views.PostEndpoint.get()
    Returns None on failure.
    item - an InboxItem object
    """
    if not item:
        return None
    try:
        # NOTE: may need to convert given template urls to API urls
        # NOTE: Follows added to the inbox need to be "approved" later
        r = requests.get(item.link)
        json = r.json() # returns JSON, not Dict
        return json
    except Exception as e:
        # Can't get the object from `link` eg. doesn't exist
        placeholder = {
            "type":"post",
            "title":"Something went wrong.",
            "id":item.link,
            "source":"",
            "origin":"",
            "description":"There was a shared item here, but we couldn't retrieve it.",
            "contentType":"text/plain",
            "content":str(e),
            "author":{},
            "categories":"",
            "count":0,
            "size":0,
            "comments":"",
            "published":"",
            "visibility":"PUBLIC",
            "unlisted":True
        }
        print(e)
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
        json = {
            "type":"follow",
            "author_id":requesting_author
           
            
        }
         # "summary": requesting_author['displayName'] + " wants to follow " + requested_author['displayName'],

         # "author_id":requesting_author,
            # "object":requested_author,
        return json
    except:
        return None

def AuthorJSON(author):
    """
    Converts an Author object into a JSON-compatible dictionary.
    Returns None on failure.
    """
    if not author:
        return None
    try:
        json = {
            "type":"author",
            "id":str(author.id),
            "host":author.host,
            "displayName":author.username,
            "url":author.url,
            "github":author.github
        }
        return json
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
       
    return True
