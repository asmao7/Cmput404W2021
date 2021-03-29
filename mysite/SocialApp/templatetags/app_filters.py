from django import template

register = template.Library()

@register.filter(name='liked_or_not')
def liked_or_not(value):
	current_user = request.user
	liked = len(LikedPost.objects.filter(post_id=value, user_id=current_user))
	if liked == 0:
		return '♡'
	else:
		return '🖤'
