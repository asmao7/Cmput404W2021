"""
Contains useful helper functions
"""
import requests
from .models import Author, Post, Comment, InboxItem

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
            "displayName":author.display_name,
            "url":author.url,
            "github":author.github
        }
        return json
    except:
        return None


# TODO: Fill out categories, count, size, comments
def PostToJSON(post):
    """
    Converts a Post object into a JSON-compatible dictionary.
    Return None on failure.
    """
    if not post:
        return None
    try:
        # Maybe don't do this? Not sure yet.
        if post.image_content:
            content = post.image_content.url
        else:
            content = post.text_content
        json = {
            "type":"post",
            "title":post.title,
            "id":post.url,
            "source":post.source,
            "origin":post.origin,
            "description":post.description,
            "contentType":post.content_type,
            "content":content,
            "author":AuthorToJSON(post.author),
            "categories":"",
            "count":0,
            "size":0,
            "comments":"",
            "published":str(post.published),
            "visibility":post.visibility,
            "unlisted":post.unlisted
        }
        return json
    except:
        return None


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
            "published":comment.published,
            "id":comment.url
        }
        return json
    except:
        return None


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