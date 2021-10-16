from django import forms
from .models import Post,CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):

	email = forms.EmailField(label='',widget=forms.EmailInput(attrs={'class':'','placeholder':'Email'}))
	username = forms.CharField(label='',widget=forms.TextInput(attrs={'class':'mt-4','placeholder':'Username'}))
	# phonenumber = forms.CharField(label='',widget=forms.TextInput(attrs={'class':'mb-4','placeholder':'Phone Number'}))
	password1 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'class':'mt-4','placeholder':'Password'}))
	password2 = forms.CharField(label='',widget=forms.PasswordInput(attrs={'class':'mt-4','placeholder':'Confirm Password'}))
	def clean(self):
		email = self.cleaned_data.get('email')

		user = CustomUser.objects.filter(email=email).first()
		# print(user)
		if user:
			raise forms.ValidationError('This email is already taken!! try with another one')
		


	class Meta:
		model = CustomUser
		

		fields = ['email','username','password1','password2']

		help_texts = {
		'username':None,
		'email':None,
		'password1':None,
		}


class LoginForm(forms.Form):
	email = forms.EmailField(
		label='',
		max_length=100,
		widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'}))
	password = forms.CharField(label='',
		min_length=8,
		widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))

	def clean(self):
		cleaned_data= super().clean()
		email = self.cleaned_data.get('email')
		password = self.cleaned_data.get('password')

		user = CustomUser.objects.filter(email = email).first()

		if user:
			if not user.check_password(password):
				raise forms.ValidationError({'password':'Invalid password'})
			if not user.is_active:
				raise forms.ValidationError({'email':'Your account has been deactivated.'})
		else:
			raise forms.ValidationError({'email':'There is no user with this email'})

class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		exclude = ['author']
		fields = ['title','content']

class ProfileUpdateForm(forms.ModelForm):
	username = forms.CharField(label='Username',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
	first_name = forms.CharField(label='First Name',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
	last_name = forms.CharField(label='Last Name',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
	phonenumber = forms.CharField(label='Phone No.',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Phone No'}))
	bio = forms.CharField(label="bio",required=False,widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Bio'}))
	def __init__(self, *args, **kwargs):
		self.request =kwargs.pop('request')
		super(ProfileUpdateForm, self).__init__(*args, **kwargs)

	def clean(self):
		cleaned_data = super().clean()
		username = self.cleaned_data.get('username')
		phonenumber = self.cleaned_data.get('phonenumber')
		if username != self.request.user.username:
			user = CustomUser.objects.filter(username=username)
			if user:
				raise forms.ValidationError({'username':'This username is already taken.'})
		if len(phonenumber) < 10:
			raise forms.ValidationError({'phonenumber':'Ensure this value has at most 10 characters.'})
		try:
			int(phonenumber)
		except Exception as e:
			raise forms.ValidationError({'phonenumber':'Ensure this value must be a number.'})

	class Meta:
		model = CustomUser
		fields = ['username','profile_picture','first_name','last_name','phonenumber','bio']