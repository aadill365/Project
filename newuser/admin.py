from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Notifications)
admin.site.register(Saved)

# UserAdmin.fieldsets += ("Addiional Info",{'fields':('phonenumber','profile_picture')}),
