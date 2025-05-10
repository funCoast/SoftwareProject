from pathlib import Path

from openai import OpenAI


class FileAnalyse:
    def __init__(self):
        self.client = OpenAI(
            api_key="sk-5b81b33eb54848d6826c38e75ecd9fc7",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    def analyze(self, file_path, input_message):
        file_object = self.client.files.create(file=Path(file_path), purpose="file-extract")

        completion = self.client.chat.completions.create(
            model="qwen-long",
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                # 请将 'file-fe-xxx'替换为您实际对话场景所使用的 file-id。
                {'role': 'system', 'content': f'fileid://{file_object.id}'},
                {'role': 'user', 'content': f"这是用户的输入{input_message},请你根据用户输入，从文件中提取需要的内容"}
            ],
            stream=True,
            stream_options={"include_usage": True}
        )

        full_content = ""
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                # 拼接输出内容
                full_content += chunk.choices[0].delta.content

        return {full_content}