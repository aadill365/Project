text = '''Congue salutandi ex eam! Mei an prima consulatu, erat detracto eu quo? Vim ea esse utinam efficiantur, at noster dicunt.

@koseeke'''

def mention(content):
	for username in content.split():
		if username.startswith('@'):
			return content.replace(username, f'''<a href="profile/{username[1:]}">{username}</a>''')

print(mention(text))