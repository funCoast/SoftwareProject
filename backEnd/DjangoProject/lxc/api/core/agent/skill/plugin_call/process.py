import json
import os
import openai
import re
from openai import OpenAI

from api.core.agent.skill.plugin_call.plugin_tools import tools
from api.core.plugin.api.views import plugin_manager

client = OpenAI(
    #该API-KEY为组内成员(hty)个人所有。
    api_key="sk-5b81b33eb54848d6826c38e75ecd9fc7",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def remove_first_last_line(s):
    if not s or s.count('\n') < 1:
        return ""
    lines = s.split('\n')
    processed_lines = lines[1:-1]
    return '\n'.join(processed_lines)

def translate_to_english(text):
    """将输入文本翻译为英文"""
    completion = client.chat.completions.create(
        model="qwen-mt-turbo",
        messages=[
            {"role": "user", "content": text}
        ],
        extra_body={
            "translation_options": {
                "source_lang": "auto",
                "target_lang": "English"
            }
        }
    )
    translated_text = completion.choices[0].message.content
    return translated_text


def remove_noise(text):
    # 保留问号、感叹号等关键标点
    text = re.sub(r'[^\w\s?！]', '', text)
    # 处理缩写（如What's -> What is）
    text = re.sub(r"'s\b", " is", text)
    return re.sub(r'\s+', ' ', text).strip()


def intent_recognition(text, labels):
    # 添加提示信息，明确要求模型返回多个意图标签，用空格隔开
    label_str = "; ".join(labels)
    prompt = f"""
        Extract multiple intents from the following text and return them as space-separated labels. 
        The intents must be exactly one of the predefined categories: {label_str}. 
        If no intents are recognized, return only 'unknown'.
        Text: '{text}'
        Intents:
        """
    completion = client.chat.completions.create(
        model="qwen-max",
        messages=[{"role": "user", "content": prompt}]
    )
    # 假设模型的输出直接是意图标签，用空格隔开
    intent_labels = completion.choices[0].message.content.strip()
    return intent_labels


def extract_parameters_by_model(text, tool):
    prompt = f"""
    # 角色
    你作为智能API参数解析器，需严格按以下流程处理请求：
    
    # 强制规则
    1. 输出必须为**合法JSON对象**，且符合工具schema层级
    2. 禁止包含：注释、说明、额外符号、Markdown代码块标记
    3. 当参数无有效输入时：
       - 有默认值：填充默认值
       - 无默认值且required：返回400错误空对象

    # 处理流程
    1. **格式解析阶段**
       ▼ 分析提供的工具schema，提取：
       └─ 参数名称与层级结构
       └─ 参数类型与格式要求
       └─ 默认值设置规则
       └─ 必填参数标记

    2. **语义识别阶段**
       ▼ 解析用户输入"{{用户输入}}"时：
       ● 实体识别：定位与参数相关的命名实体
       ● 隐式推理：通过上下文推导缺失参数
       ● 格式转换：将识别结果转换为schema要求的格式

    3. **参数装配阶段**
       ▼ 按优先级填充：
       (1) 显式声明值 > (2) 隐式推导值 > (3) 默认值
       ▼ 当required参数无法获取时抛出400错误

    # 当前工作
    工具：
    {tool}
    用户请求：
    {text}
        """

    completion = client.chat.completions.create(
        model="qwen-max",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content



