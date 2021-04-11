import requests
from django import template
from SocialApp.models import ObjectLike

register = template.Library()

@register.filter(name='liked_or_not')
def liked_or_not(object, author):
	liked = len(ObjectLike.objects.filter(author_url=author.url, object_url=object.url))
	if liked == 0:
		return '♡'
	else:
		return '🖤'

@register.filter(name='liked_count')
def liked_count(object):
	return len(ObjectLike.objects.filter(object_url=object.url))

@register.filter(name='comment_author_name')
def comment_author_name(comment):
	author = requests.get(comment.author_url).json()
	return author["displayName"]
