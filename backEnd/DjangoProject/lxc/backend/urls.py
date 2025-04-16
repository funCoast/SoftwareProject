from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('register', views.register, name='register'),
    # User
    path('user/sendCode', views.send_code, name='send_code'),
    path('user/loginByCode', views.user_login_by_code, name='user_login_by_code'),
    path('user/loginByPassword', views.user_login_by_password, name='user_login_by_password'),
    path('user/updateProfile', views.user_update_profile, name='user_update_profile'),
    path('user/fetchProfile', views.user_fetch_profile, name='user_fetch_profile'),
    path('user/updateAvatar', views.user_update_avatar, name='user_update_avatar'),
    path('user/getAvatar', views.user_get_avatar, name='user_get_avatar'),
    path('user/getContacts',views.user_get_contacts, name='user_get_contacts'),
    path('user/getMessages',views.user_get_messages, name='user_get_messages'),
    path('user/sendMessage',views.user_send_message, name='user_send_message'),
    # Announcement
    path('anno/add', views.announcement_add, name='announcement_add'),
    path('anno/update', views.announcement_update, name='announcement_update'),
    path('anno/delete', views.announcement_delete, name='announcement_delete'),
    path('anno/get', views.announcement_list, name='announcement_list'),

    # 更新密码
    path('user/updatePassword', views.user_update_password, name='user_update_password'),
]