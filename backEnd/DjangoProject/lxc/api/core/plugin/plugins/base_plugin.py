class BasePlugin:
    def __init__(self, name, version, description, intent):
        self.name = name
        self.version = version
        self.description = description
        self.intent = intent

    def execute(self, *args, **kwargs):
        raise NotImplementedError("Each plugin must implement the execute method.")