from django.urls import path

from api.core.plugin.api.views import list_plugins, execute_plugin

urlpatterns = [
    path('plugins/', list_plugins, name='list_plugins'),
    path('plugins/<str:plugin_name>/execute/', execute_plugin, name='execute_plugin'),
]