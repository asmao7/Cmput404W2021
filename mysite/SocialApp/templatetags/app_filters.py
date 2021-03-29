from django import template
from SocialApp.models import LikedPost

register = template.Library()

@register.filter(name='liked_or_not')
#@stringfilter
def liked_or_not(value, arg):
	liked = len(LikedPost.objects.filter(post_id=value, user_id=arg))
	if liked == 0:
		return '♡'
	else:
		return '🖤'
