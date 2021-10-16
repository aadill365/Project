from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class CustomUser(AbstractUser):
	email = models.EmailField(unique=True,max_length=120)
	phonenumber = models.CharField(max_length=10)
	profile_picture = models.ImageField(upload_to='profile',default='default.jpeg')
	bio = models.TextField(null=True, blank=True)
	token = models.CharField(max_length=200)
	is_verified = models.BooleanField(default=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username','phonenumber']

	def __str__(self):
		return self.username


	def followed_users(self):
		ids=[]
		follow = Follow.objects.filter(user_id=self.id)
		for f in follow:
			ids.append(f.followed.id)
		return ids

class Post(models.Model):
	title = models.CharField(max_length=50) 
	content = models.TextField()
	author = models.ForeignKey(CustomUser ,on_delete = models.CASCADE)
	likes = models.ManyToManyField(CustomUser, related_name='likes' ,blank=True)
	date_posted = models.DateTimeField(default=timezone.now)
	tags = models.ManyToManyField(CustomUser,related_name='tags', blank=True)

	def total_likes(self):
		return self.likes.count()

	def __str__(self):
		return self.title
	def all_tags(self):
		users=[]
		for username in self.content.split():
			if username.startswith('@'):
				user = CustomUser.objects.filter(username=username[1:]).first()
				if user:
					users.append(user)
		return users
					
	

class Follow(models.Model):
	user = models.ForeignKey(CustomUser,related_name='follower', on_delete=models.CASCADE)
	followed = models.ForeignKey(CustomUser, related_name='followed',	on_delete=models.CASCADE)
	followed_on = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.followed}"

class Saved(models.Model):
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	saved_posts = models.ForeignKey(Post, related_name='saved',on_delete=models.CASCADE)
	date_posted = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.saved_posts.title

class Notifications(models.Model):
	sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='sender')
	receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='receiver')
	post = models.ForeignKey(Post, on_delete=models.CASCADE,null=True)
	action = models.CharField(max_length=50)
	read = models.BooleanField(default=False)
	timestamp = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.sender} {self.action} {self.receiver}"
#signals

@receiver(post_save, sender = Post)
def notify_tags(sender, instance,*args,**kwargs):
	post = Post.objects.get(pk=instance.pk)
	sender = CustomUser.objects.get(pk=instance.author.pk)
	if post.all_tags():
		post.tags.set(post.all_tags())
		for tag in post.all_tags():
			noti = Notifications.objects.filter(sender = post.author,receiver=tag,action='tagged you in a post',post=post).first()
			if noti:
				noti.delete()
			noti = Notifications(sender = post.author,receiver=tag,action='tagged you in a post',post=post)
			noti.save()