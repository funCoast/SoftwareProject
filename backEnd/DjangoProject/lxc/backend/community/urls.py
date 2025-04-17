from django.urls import path

from backend.community import views

urlpatterns = [
    path('getComments', views.agent_get_comments, name='agent_get_comments'),
    path('sendComment', views.agent_send_comment, name='agent_send_comment'),
]