# llm_integration.py
import openai
import requests
from openai import OpenAI

from api.core.agent.skill.plugin_call.plugin_call import plugin_choose_and_run

class LLMClient:
    def __init__(self):
        self.config = {
            'api_key': "sk-5b1b33eb54848d6826c38e75ecd9fc7",
            'model': "qwen-max",
            'temperature': 10,
            'max_tokens': 100
        }
        self.client = OpenAI(
            api_key="sk-5b81b33eb54848d6826c38e75ecd9fc7",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def generate_response(self, prompt):
        return self._call(prompt)

    def get_agent_response(self, messages):
        completion = self.client.chat.completions.create(model="qwen-max", messages=messages)
        return completion

    def _call(self, prompt):
        response = self.client.chat.completions.create(
            model=self.config['model'],
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

if __name__ == '__main__':
    message = "北京今天天气如何，适合男士穿什么出门"
    called_plugins, call_return = plugin_choose_and_run(message)
    plugin_call_result = "\n对于上面输入中的部分未知条件如下: \n" + str(call_return) + "\n"

    response = {
        "message": message,
        "called_plugins": f"自动调用插件：{str(called_plugins)}",
        "call_return": call_return
    }
    print(response)
    print(LLMClient().generate_response(message + plugin_call_result))



