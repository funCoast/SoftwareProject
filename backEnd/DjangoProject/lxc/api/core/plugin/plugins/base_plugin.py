class BasePlugin:
    def __init__(self, name, version, description, intent, param_description):
        self.name = name
        self.version = version
        self.description = description
        self.intent = intent
        self.param_description = param_description

    def execute(self, *args, **kwargs):
        raise NotImplementedError("Each plugin must implement the execute method.")