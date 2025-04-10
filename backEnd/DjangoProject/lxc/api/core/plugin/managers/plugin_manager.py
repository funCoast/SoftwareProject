class PluginManager:
    def __init__(self):
        self.plugins = {}

    def register_plugin(self, plugin):
        self.plugins[plugin.name] = plugin

    def get_plugin(self, name):
        if name not in self.plugins:
            raise ValueError(f"Plugin '{name}' not found.")
        return self.plugins[name]

    def execute_plugin(self, name, *args, **kwargs):
        plugin = self.get_plugin(name)
        return plugin.execute(*args, **kwargs)