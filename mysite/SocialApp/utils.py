"""
Contains useful helper functions
"""
import requests, json
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
        author = requests.get(like.author_url).json()
        json = {
            "type":"comment",
            "author":author,
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


def ObjectLikeToJSON(like):
    """
    Converts a like on an object to JSON
    """
    if not like:
        return None
    try:
        author = requests.get(like.author_url).json()
        json = {
            "summary": "{} Likes your post".format(author["displayName"]),
            "type": "Like",
            "author": author,
            "object": like.object_url
        }
        return json
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
        return [];
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