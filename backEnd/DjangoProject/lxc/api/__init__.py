from api.core.plugin.api import register_plugins
from api.core.plugin.managers.plugin_manager import PluginManager

plugin_manager = PluginManager()
register_plugins(plugin_manager)