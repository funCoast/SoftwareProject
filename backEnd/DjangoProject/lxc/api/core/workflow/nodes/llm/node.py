from openai import OpenAI
import json
client = OpenAI(
    #该API-KEY为组内成员(hty)个人所有。
    api_key="sk-5b81b33eb54848d6826c38e75ecd9fc7",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def call_llm(prompt: str):
    """
    使用通义Qwen模型处理用户输入，并返回完整 JSON 字符串结果
    """
    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个有帮助的助手。"},
                {"role": "user", "content": prompt},
            ]
        )
        return response.model_dump_json(indent=2)  # ✅ 输出完整 JSON
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
