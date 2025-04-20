import json

from api.core.agent.skill.plugin_call.plugin_tools import tools
from api.core.agent.skill.plugin_call.process import intent_recognition, translate_to_english, \
    extract_parameters_by_model
from api.core.plugin.api.views import plugin_manager
from api.core.plugin.plugins.base_plugin import BasePlugin


def execute(plugin: BasePlugin):
    return plugin.execute()


class SkillPluginCall:

    def __init__(self):
        self.plugins = []

    def add_plugin(self, plugin: BasePlugin):
        self.plugins.append(plugin)

    def choose_and_run(self, input_text: str):
        text = translate_to_english(input_text)
        print("英文文本：", text)

        # 意图识别
        intent = intent_recognition(text, list(plugin_manager.intent_dict.keys()))
        print("意图识别结果：", intent.split(" "))
        intents = intent.split(" ")

        for intent in intents:
            kwargs = json.loads(extract_parameters_by_model(text, tools[intent]))
            print(kwargs)
            print(plugin_manager.intent_dict[intent]().execute(**kwargs))

if __name__ == '__main__':
    SkillPluginCall().choose_and_run("北京现在几点")





