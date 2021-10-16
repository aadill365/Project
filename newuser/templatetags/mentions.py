from django import template
from newuser.models import CustomUser


register = template.Library()

@register.filter()
def mention(content):
	for username in content.split():
		if username.startswith('@'):
			user = CustomUser.objects.filter(username=username[1:])
			if user:
				content = content.replace(username, f'<a href="/profile/{username[1:]}">{username}</a>')
	return content