from openai import OpenAI

from ...registry import register_node

import json
client = OpenAI(
    #该API-KEY为组内成员(hty)个人所有。
    api_key="sk-5b81b33eb54848d6826c38e75ecd9fc7",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def call_llm(user_prompt: str,system_prompt,model: str)->str:
    """
    使用通义Qwen模型处理用户输入，并返回完整 JSON 字符串结果
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": user_prompt},
                {"role": "system", "content": system_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[错误] {str(e)}"
    # return "用户提示词为：" + user_prompt + "\n" + "系统提示词为：" + system_prompt

@register_node("paraExtractor")
def run_paraExtractor_node(node, inputs):
    """
    工作流中 llm 类型节点的执行函数
    :param node: 节点配置（含 outputs）
    :return: {'response': json_string}
    """
    text = inputs[0].get("value","")
    model = node.get("data", {}).get("model", "")
    instruction = node.get("data", {}).get("instruction", "")
    result = call_llm(text,instruction,model)

    # 自动生成 outputs（按输出定义）
    outputs = {}
    for output in node.get("outputs", []):
        id = output["id"]
        outputs[id] = result  # 所有输出都给一样的结果（你也可以按 name 分别生成）
    return outputs
