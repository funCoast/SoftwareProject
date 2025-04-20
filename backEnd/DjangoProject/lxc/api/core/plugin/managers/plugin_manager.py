from api.core.plugin.plugins.base_plugin import BasePlugin


class PluginManager:
    def __init__(self):
        self.params_dict = {}
        self.plugins = {}
        self.intent_dict = {}

    def register_plugin(self, plugin):
        self.plugins[plugin().name] = plugin
        self.intent_dict[plugin().intent] = plugin
        self.params_dict[plugin().name] = plugin().param_description

    def get_plugin(self, name):
        if name not in self.plugins:
            raise ValueError(f"Plugin '{name}' not found.")
        return self.plugins[name]

    def execute_plugin(self, name, *args, **kwargs):
        plugin = self.plugins[name]()
        return plugin.execute(*args, **kwargs)