from django.urls import path

from backend.community import views

urlpatterns = [
    path('getComments', views.agent_get_comments, name='agent_get_comments'),
]