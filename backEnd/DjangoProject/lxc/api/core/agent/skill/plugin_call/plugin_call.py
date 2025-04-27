import json

from api.core.agent.skill.plugin_call.plugin_tools import tools
from api.core.agent.skill.plugin_call.process import intent_recognition, translate_to_english, \
    extract_parameters_by_model
from api.core.plugin.api.views import plugin_manager
from api.core.plugin.plugins.base_plugin import BasePlugin


def execute(plugin: BasePlugin):
    return plugin.execute()


def plugin_choose_and_run(input_text: str):
    text = translate_to_english(input_text)

    # 意图识别
    intent = intent_recognition(text, list(plugin_manager.intent_dict.keys()))
    intents = intent.split(" ")

    called_plugins = []
    call_results = []

    for intent in intents:
        if intent in tools.keys():
            kwargs = json.loads(extract_parameters_by_model(text, tools[intent]))
            llm_response = plugin_manager.intent_dict[intent]().execute(**kwargs)
            called_plugins.append(plugin_manager.intent_dict[intent]().name)
            if llm_response and llm_response["status"] == 'success':
                call_results.append({intent: llm_response["result"]})

    return called_plugins, call_results

def plugin_call(message: str):
    called_plugins, call_return = plugin_choose_and_run(message)

    response = {
        "message": message,
        "called_plugins": f"自动调用插件：{str(called_plugins)}",
        "call_return": call_return
    }

    return response

if __name__ == '__main__':
    print(plugin_choose_and_run("北京现在天气如何"))





