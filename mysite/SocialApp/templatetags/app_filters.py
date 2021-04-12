import requests, json
from django import template
from SocialApp.models import ObjectLike
from SocialApp.utils import GetURLBasicAuth

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

@register.filter(name='comment_author_name')
def comment_author_name(comment):
    # Try to get the latest display name for the author
    basic_auth = GetURLBasicAuth(comment.author_url)
    request = None
    display_name = None
    if (basic_auth):
        request = requests.get(comment.author_url, auth=basic_auth)
    else:
        request = requests.get(comment.author_url)

    if (request.ok):
        try:
            display_name = request.json()["displayName"]
        except:
            try:
                display_name = json.loads(comment.author_json)["displayName"]
            except:
                pass

    if (display_name):
        return display_name
    else:
        return "Anonymous"