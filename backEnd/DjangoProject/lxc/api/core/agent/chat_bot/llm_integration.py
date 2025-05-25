# llm_integration.py
import openai
import requests
from dashscope import Generation
from openai import OpenAI, completions

from api.core.agent.skill.plugin_call.plugin_call import plugin_choose_and_run
from lxc import settings


class LLMClient:
    def __init__(self):
        self.config = {
            'api_key': "sk-5b1b33eb54848d6826c38e75ecd9fc7",
            'model': "qwen-plus",
            'temperature': 10,
            'max_tokens': 100
        }

        self.qwen_client = OpenAI(
            api_key="sk-5b81b33eb54848d6826c38e75ecd9fc7",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        self.deepseek_client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def call_deepseek_message(self, prompt):
        completion = self.deepseek_client.chat.completions.create(
            model="deepseek-r1",
            messages=[
                {'role': 'user', 'content': prompt},
            ]
        )

        return {
            'thinking_chain': completion.choices[0].message.reasoning_content,
            'response': completion.choices[0].message.content
        }

    def call_deepseek_messages(self, messages):
        completion = self.deepseek_client.chat.completions.create(
            model="deepseek-r1",
            messages=messages,
            stream=True,
        )
        reasoning_content = ""
        answer_content = ""
        is_answering = False

        for chunk in completion:
            if not chunk.choices:
                pass
            else:
                delta = chunk.choices[0].delta
                # 打印思考过程
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                    reasoning_content += delta.reasoning_content
                else:
                    if delta.content != "" and is_answering == False:
                        is_answering = True
                    answer_content += delta.content

        return {
            'thinking_chain': reasoning_content,
            'response': answer_content
        }

    def call_qwen_message(self, prompt, search=False):
        completion = self.qwen_client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'user', 'content': prompt},
            ],
            extra_body = {
                "enable_search": search
            }
        )

        return {
            'thinking_chain': '',
            'response': completion.choices[0].message.content
        }

    def call_qwen_messages(self, messages, search=False):
        completion = self.qwen_client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            extra_body={
                "enable_search": search
            }
        )

        return {
            'thinking_chain': '',
            'response': completion.choices[0].message.content
        }

    def call_glm_messages(self, messages, search=False):
        # response = {
        #     'thinking_chain': '',
        #     'response': Generation().call(
        #         api_key=settings.DASHSCOPE_API_KEY,
        #         model='chatglm-6b-v2',
        #         messages=messages,
        #         result_format='message',
        #     )
        # }
        # return response
        completion = self.qwen_client.chat.completions.create(
            model="chatglm-6b-v2",
            messages=messages,
            extra_body={
                "enable_search": search
            }
        )

        return {
            'thinking_chain': '',
            'response': completion.choices[0].message.content
        }
