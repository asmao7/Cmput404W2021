from django import template
from SocialApp.models import ObjectLike

register = template.Library()

@register.filter(name='liked_or_not')
def liked_or_not(value, arg):
	liked = len(ObjectLike.objects.filter(author_url=arg.url, object_id=value.url))
	if liked == 0:
		return '♡'
	else:
		return '🖤'
