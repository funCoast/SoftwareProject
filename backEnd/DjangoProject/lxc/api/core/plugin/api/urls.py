# plugin_api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('plugins/', views.list_plugins, name='list_plugins'),
    path('plugins/<str:plugin_name>/execute/', views.execute_plugin, name='execute_plugin'),
]