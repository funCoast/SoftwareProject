from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('register', views.register, name='register'),
    path('user/sendCode', views.send_code, name='send_code'),
    path('user/login', views.user_login_by_code, name='user_login'),

]