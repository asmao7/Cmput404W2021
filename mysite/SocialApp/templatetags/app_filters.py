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

@register.filter(name='comment_author_name')
def comment_author_name(author_url):
	try:
		author = requests.get(author_url).json()
		return author["displayName"]
	except:
		return "Anonymous"