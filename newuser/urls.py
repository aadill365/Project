from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('create-post/', views.create_post, name='create'),
    path('post/<int:pk>', views.post_detail, name='post-detail'),
    path('post/delete/<int:pk>', views.post_delete, name='post-delete'),
    path('post/update/<int:pk>', views.post_update, name='post-update'),
    path('profile/<str:username>', views.user_profile, name='profile'),
    path('post/like/<int:pk>', views.like, name='like'),
    path('register/', views.register, name='register'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('follow/<int:user>/', views.follow, name='follow'),
    path('search/', views.search, name = 'search'),
    path('edit/', views.edit_profile, name = 'edit'),
    path('about/', views.about, name = 'about'),
    path('save/<int:post_id>/', views.Save, name='save'),
    path('saved/', views.saved, name='saved'),
    path('notifications/', views.notification, name='noti'),
    path('update_notifications/', views.update_notification, name='update_noti'),
    path('verify/<str:token>', views.verify, name='verify'),

]