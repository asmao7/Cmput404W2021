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
    # Ended up being too slow because of how long heroku servers take to spool up
    # after they go to sleep. Just serve stale data instead.
    """
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
    
    if (not display_name):
    """

    display_name = None
    try:
        display_name = json.loads(comment.author_json)["displayName"]
    except:
        pass

    if (display_name):
        return display_name
    else:
        return "Anonymous"

@register.filter(name="sanitize_image")
def sanitize_image(base64_content, content_type):
    base64_prefix = "data:{},".format(content_type)
    if content_type == "application/base64":
        base64_prefix = "data:image/png;base64,"
    if (base64_prefix in base64_content):
        return base64_content
    else:
        return "{}{}".format(base64_prefix, base64_content)
