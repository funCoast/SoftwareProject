import json
import os
import openai
import re
import nltk
from openai import OpenAI

from api.core.plugin.plugins.time.current_time_plugin import CurrentTimePlugin
from api.core.plugin.plugins.time.timestamp_pulgin import TimestampPlugin
from api.core.plugin.plugins.time.timestamp_transform_plugin import TimestampTransformPlugin
from api.core.plugin.plugins.time.timezoen_switch_plugin import TimezoneSwitchPlugin
from api.core.plugin.plugins.time.weekday_calculator_plugin import WeekdayCalculatorPlugin
from api.core.plugin.plugins.weather.weather_scraper_plugin import WeatherScraperPlugin

client = OpenAI(
    api_key="sk-5b81b33eb54848d6826c38e75ecd9fc7",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


plugins = {
    "current_time": {
        "plugin": CurrentTimePlugin(),
        "params": ["timezone", "time_format"]
    },
    "timestamp": {
        "plugin": TimestampPlugin(),
        "params": ["timezone", "readable_time"]
    },
    "timestamp_to_time": {
        "plugin": TimestampTransformPlugin(),
        "params": ["timezone", "timestamp"]
    },
    "time_zone_switch": {
        "plugin": TimezoneSwitchPlugin(),
        "params": ["time", "current_timezone", "target_timezone"]
    },
    "weekday_calculator": {
        "plugin": WeekdayCalculatorPlugin(),
        "params": ["date"]
    },
    "weather_query": {
        "plugin": WeatherScraperPlugin(),
        "params": ["city_code"]
    }
}


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


def intent_and_parameter_recognition(text):
    # 提示模型识别意图并提取参数
    prompt = f"""
    Identify the intent of the following text and extract the required parameters in JSON format.
    Possible intents are: {list(plugins.keys())}.
    Parameters depend on the intent and should follow the structure:
    - For 'current_time': timezone, time_format
    - For 'timestamp': timezone, readable_time
    - For 'timestamp_to_time': timezone, timestamp
    - For 'time_zone_switch': time, current_timezone, target_timezone
    - For 'weekday_calculator': date
    - For 'weather_query': city_code
    If no parameters can be found for an intent, return an empty JSON object.
    Text: '{text}'
    """
    completion = client.chat.completions.create(
        model="qwen-turbo-2024-11-01",
        messages=[{"role": "user", "content": prompt}]
    )
    print("---=--", completion.choices[0].message.content.strip())
    response = completion.choices[0].message.content.strip()
    try:
        result = json.loads(response)
        return result.get("intent"), result.get("parameters", {})
    except json.JSONDecodeError:
        return None, {}


def main():
    input_text = "2025年6月7日是星期几"

    # 翻译为英文
    english_text = translate_to_english(input_text)
    print("英文文本：", english_text)

    # 去噪
    cleaned_text = remove_noise(english_text)
    print("去噪后的文本：", cleaned_text)

    # 意图和参数识别
    intent, parameters = intent_and_parameter_recognition(cleaned_text)
    print("意图：", intent)
    print("参数：", parameters)

    # 根据意图调用插件
    if intent in plugins:
        plugin_info = plugins[intent]
        plugin = plugin_info["plugin"]
        # 提取插件需要的参数
        params = {param: parameters.get(param) for param in plugin_info["params"]}
        result = plugin.execute(**params)
        print("插件执行结果：", result)
    else:
        print("No suitable plugin found for the identified intent.")


if __name__ == "__main__":
    main()