# plugin_api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list_plugins/', views.list_plugins, name='list_plugins'),
    path('<str:plugin_name>/execute/', views.execute_plugin, name='execute_plugin'),
]