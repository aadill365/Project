from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from .models import CustomUser ,Post, Follow, Saved, Notifications
from .forms import PostForm, LoginForm, UserRegisterForm, ProfileUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import threading
import uuid

# Create your views here.

def home(request):
	if not request.user.is_authenticated:
		return redirect('about')
	if not request.user.is_verified:
		messages.warning(request, "Your account is not verified")
		return redirect('logout')
	ids = request.user.followed_users()
	ids.append(request.user.id)
	posts = Post.objects.filter(author_id__in = ids).order_by('-date_posted')
	pages = Paginator(posts, 5)
	page_num = request.GET.get('page',1)
	try:
		page = pages.page(page_num)
	except EmptyPage:
		page = pages.page(1)
	saved = Saved.objects.filter(user = request.user)
	saved_posts = []
	for save in saved:
		saved_posts.append(save.saved_posts.id)
	notifications = Notifications.objects.filter(receiver=request.user, read=False)
	notifications = notifications.exclude(sender=request.user)
	
	return render(request, 'newuser/home.html',{'posts':page,'saved_posts':saved_posts,'notifications':notifications})

def about(request):
	return render(request, 'newuser/about.html')

def verify(request,token):
	if request.user.is_authenticated:
		raise Http404
	user = get_object_or_404(CustomUser,token=token)
	if user.is_verified:
		messages.info(request, 'Your account is already verified')
	else:
		user.is_verified = True
		user.save()
		messages.warning(request,'your account has been verified you can now login')
	return redirect('login')

def send_email(user,email,token):
	email_subject = 'Activate Your Account'
	email_body = f"""
	Hello {user},

	Visit this link to activate your account on Koseeke : http://localhost:8000/verify/{token}
	"""
	html_template = render_to_string('newuser/email_template.html',{'user':user,'token':token})
	email = EmailMessage(email_subject, html_template,settings.EMAIL_HOST_USER,[email])
	email.send(fail_silently=False)

def register(request):
	if request.user.is_authenticated:
		return redirect('home')
	if request.method == 'POST':
		form =UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			token = uuid.uuid4()
			
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			user = CustomUser.objects.filter(email=email).first()
			user.token = token
			user.save()
			send_email(username,email,token)
			messages.success(request, f'Your account has been created check your email to activate your account!')
			return redirect('login')
	else:
		form =UserRegisterForm()
	return render(request, "newuser/register.html",{'form':form})

def Login(request):
	if request.user.is_authenticated:
		return redirect('home')
	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			email=form.cleaned_data.get('email')
			password=form.cleaned_data.get('password')
			user=CustomUser.objects.filter(email=email).first()
			if not user.is_verified:
				messages.warning(request, "Your account is not verified")
				return redirect('login')
			else:

				user = authenticate(email=user.email,password=password)
				login(request, user)
			if request.GET.get('next', None):
				return redirect(request.GET['next'])
			messages.success(request, "Login successful")
			return redirect('home')
		else:
			for field in form.errors:
				form[field].field.widget.attrs['class'] = 'is-invalid form-control'

	else:
		form = LoginForm()
	return render(request, 'newuser/login.html',{'form':form})

def Logout(request):
	logout(request)
	return redirect('home')

@login_required
def create_post(request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.save()
			

			
			
			messages.success(request, 'post created successfully')
			return redirect('home')
	form = PostForm()
	context = {'form': form}
	return render(request, 'newuser/post.html', context)



def post_detail(request, pk):
	post = get_object_or_404(Post,pk=pk)
	if post.likes.filter(id = request.user.id):
		liked = True
	else:
		liked=False
	saved = Saved.objects.filter(saved_posts__id = pk,user = request.user).first()
	if saved:
		saved = True
	else:
		saved=False
	return render(request, 'newuser/post_detail.html',{'post':post, 'liked':liked,'saved':saved})

def post_update(request,pk):
	post = get_object_or_404(Post,id=pk)
	if post.author != request.user:
		raise Http404

	if request.method == 'POST':
		form = PostForm(request.POST, instance=post)
		if form.is_valid():
			form.save()
			messages.success(request, 'Post updated successfully')
			return redirect('post-detail',pk=pk)


	
	form = PostForm(instance=post)
	return render(request, 'newuser/post_update.html',{'form':form})



@login_required
def post_delete(request , pk):
	post = get_object_or_404(Post, pk=pk)
	if request.user.username != post.author.username:
		raise Http404

	post.delete()
	messages.success(request, 'post deleted successfully')
	return redirect('home')


def like(request,pk):
	if request.method == 'POST':
		post = get_object_or_404(Post, pk=pk)
		if post.likes.filter(id = request.user.id):
			post.likes.remove(request.user)
			liked = False
			count = post.likes.count()
			noti = Notifications.objects.filter(sender = request.user,receiver=post.author,action='like',post=post).first()
			if noti:
				noti.delete()

		else:
			post.likes.add(request.user)
			liked = True
			noti = Notifications.objects.filter(sender = request.user,receiver=post.author,action='liked your post',post=post).first()
			if noti:
				noti.delete()
			noti = Notifications(sender = request.user,receiver=post.author,action='liked your post',post=post)
			noti.save()
			count = post.likes.count()
		return JsonResponse({'liked':liked,'count':count})

def follow(request,user):
	if request.method=='POST':
		user = CustomUser.objects.get(id=user)

		follow = Follow.objects.filter(user=request.user,followed=user).first()
		if follow:
			follow.delete()
			follow = False
			count = user.followed.count()
			noti = Notifications.objects.filter(sender=request.user, receiver=user,action='follow').first()
			if noti:
				noti.delete()

		else:
			follow = Follow(user=request.user,followed=user)
			follow.save()
			follow=True
			count = user.followed.count()
			noti = Notifications.objects.filter(sender=request.user, receiver=user,action='started following you').first()
			if noti:
				noti.delete()
			noti = Notifications(sender = request.user,receiver=user,action='started following you')
			noti.save()
		return JsonResponse({'follow':follow,'count':count})

@login_required
def notification(request):
	notifications = Notifications.objects.filter(receiver=request.user,read=False)
	notifications = notifications.exclude(sender=request.user)
	older_noti = Notifications.objects.filter(receiver=request.user, read=True).order_by('-timestamp')
	older_noti = older_noti.exclude(sender=request.user)
	return render(request, 'newuser/notifications.html',{'notifications':notifications,'older_noti':older_noti})

def update_notification(request):
	if request.method == 'POST':
		notifications = Notifications.objects.filter(receiver=request.user, read=False)
		for noti in notifications:
			noti.read = True
			noti.save()
		return JsonResponse({'read':True})
	else:
		raise Http404


@login_required
def user_profile(request,username):
	user = get_object_or_404(CustomUser, username=username)
	posts = Post.objects.filter(author=user).order_by('-date_posted')

	follow = Follow.objects.filter(user_id=request.user,followed=user).first()
	saved = Saved.objects.filter(user = request.user)
	saved_posts = []
	for save in saved:
		saved_posts.append(save.saved_posts.id)
	if follow:
		follow = False
	else:
		follow = True

	return render(request, 'newuser/user_profile.html',{'user':user,'posts':posts,'follow':follow,'saved_posts':saved_posts})

def raise_404(request, exception):
	return render(request, 'newuser/404.html')

@login_required
def search(request):
	import json
	from django.core import serializers
	values = CustomUser.objects.all().order_by("username")
	# values = values.exclude(username=request.user.username)
	# data = json.dumps(list(values),indent=4,sort_keys=True,default=str)
	# data = serializers.serialize('json', CustomUser.objects.all().order_by("username"), fields=('username','profile_picture'),default=str)
	data = []
	for value in values:
		data.append({'fields':{'username':f'{value.username}','profile_picture':f'{value.profile_picture.url}'}})
	data = json.dumps(data, indent=4,default=str)

	return render(request, 'newuser/search.html',{'json':data})
	# return JsonResponse(data,safe=False)

def edit_profile(request):
	user = get_object_or_404(CustomUser,username=request.user.username)
	# user = CustomUser.objects.filter(username=username)
	if request.method=='POST':
		form = ProfileUpdateForm(request.POST,
									request.FILES,
									instance=request.user,request=request)
		if form.is_valid():
			form.save()
			messages.success(request, 'profile updated')
			return redirect('profile',username = request.user.username)
		else:
			for field in form.errors:
				form[field].field.widget.attrs['class'] = 'is-invalid form-control'
	else:
		form = ProfileUpdateForm(instance=request.user,request = request)
	return render(request, 'newuser/edit_profile.html',{'form':form})

def Save(request,post_id):
	if request.method=='POST':
		post = get_object_or_404(Post,pk=post_id)
		
		saved = Saved.objects.filter(saved_posts__id = post_id, user = request.user).first()
		if saved:
			saved.delete()
			save = False
			saved = False


		else:
			save = Saved(user = request.user,saved_posts=post)
			save.save()
			save = True
			saved = Saved.objects.filter(saved_posts__id = post_id, user = request.user).first()
			# saved = f'{saved.user.username} | {saved.saved_posts} | {saved.saved_posts.author}'
			saved = {'saved_user':f'{saved.user.username}',
			 'saved_post':f'{saved.saved_posts.title}',
			 'post_author':f'{saved.saved_posts.author}'
			 }

		return JsonResponse({'save':save,'saved':saved})

@login_required
def saved(request):
	posts = Saved.objects.filter(user = request.user).order_by('-date_posted')
	return render(request, 'newuser/saved_posts.html',{'posts':posts})


