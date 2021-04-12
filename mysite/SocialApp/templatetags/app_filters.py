import requests
from django import template
from SocialApp.models import ObjectLike

register = template.Library()

@register.filter(name='liked_or_not')
def liked_or_not(object_url, author_url):
    liked = len(ObjectLike.objects.filter(author_url=author_url, object_url=object_url))
    if liked == 0:
        return '♡'
    else:
        return '🖤'

@register.filter(name='liked_count')
def liked_count(object_url):
    return len(ObjectLike.objects.filter(object_url=object_url))

@register.filter(name="remote_liked_count")
def remote_liked_count(object_url):
    try:
        # Try to get the latest likes from the remote
        likes_url = object_url
        if likes_url[-1] == "/":
            likes_url += "likes/"
        else:
            likes_url += "/likes/"
        likes = requests.get(likes_url).json()["items"]
        return len(likes)
    except:
        # If we can't fetch likes data, display what we've saved locally
        return len(ObjectLike.objects.filter(object_url=object_url))

@register.filter(name='comment_author_name')
def comment_author_name(author_url):
    try:
    # Try to get the latest display name for the author
        author = requests.get(author_url).json()
        return author["displayName"]
    except:
        # If we can't fetch author data, display the username as Anonymous
        return "Anonymous"