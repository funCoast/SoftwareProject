from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('register', views.register, name='register'),
    path('user/sendCode', views.send_code, name='send_code'),
    path('user/login', views.user_login_by_code, name='user_login'),
    path('user/loginByPassword', views.user_login_by_password, name='user_login_by_password'),
    path('user/updateProfile', views.user_update_profile, name='user_update_profile'),
    path('user/fetchProfile', views.user_fetch_profile, name='user_fetch_profile')
]