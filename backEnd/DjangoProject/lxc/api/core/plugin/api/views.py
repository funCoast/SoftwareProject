# plugin_api/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from api.core.plugin.api import register_plugins
from api.core.plugin.managers.plugin_manager import PluginManager

plugin_manager = PluginManager()
register_plugins(plugin_manager)

@csrf_exempt
@require_http_methods(["GET"])
def list_plugins(request):
    plugins = [{"name": name, "description": plugin.description} for name, plugin in plugin_manager.plugins.items()]
    return JsonResponse(plugins, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def execute_plugin(request, plugin_name):
    try:
        data = json.loads(request.body)
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        result = plugin_manager.execute_plugin(plugin_name, *args, **kwargs)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)