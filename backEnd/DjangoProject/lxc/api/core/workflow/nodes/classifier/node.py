# classifier_node.py
import json
from openai import OpenAI
import openai
import os
from api.core.workflow.registry import register_node
client = OpenAI(
    #该API-KEY为组内成员(hty)个人所有。
    api_key="sk-5b81b33eb54848d6826c38e75ecd9fc7",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def classify_question(question, categories):
    """
    :param question: 用户输入的文本问题
    :param categories: 字典或列表，包含分类名称以及描述。示例：
           categories = {
               "技术咨询": "关于技术、软件、编程的问题",
               "产品反馈": "对产品体验的意见反馈",
               "常见问题": "系统常见问题或 FAQ"
           }
    :return: 返回最佳匹配的分类以及细节信息，例如 {"category": "技术咨询", "explain": "因..."}
    """

    # 构造提示，例如将问题和分类描述一起传入 LLM，让其给出分类判断
    prompt = f"请根据下面的问题内容选择最合适的分类，并给出简要解释。\n\n问题：{question}\n\n分类：\n"
    for cat in categories:
        prompt += f"{cat}\n"
    prompt += "\n请输出最合适的分类不需要解释。"
    response = client.chat.completions.create(
        model="qwen-max-latest",  # 或使用其他支持的模型
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    # 从返回结果中提取文本，可根据返回格式进一步解析
    result_text = response.choices[0].message.content
    # result_text = "学习方法问题（这是test，防止token浪费）"
    return result_text

@register_node("classifier")
def run_classifier_node(node,inputs):
    question = inputs[0].get("value", "")
    # 获取分类列表
    classes = node["data"]["classes"]  # 每项包含 description 和 next_node

    # 构造分类标签列表
    categories = [cls["description"] for cls in classes]

    # 调用分类函数
    result = classify_question(question, categories)  # 返回预测分类名称

    # 找到对应的 next_node
    matched_class = next((cls for cls in classes if cls["description"] == result), None)
    next_node = matched_class["next_node"] if matched_class else -1
    outputs = {}
    for output in node.get("outputs", []):
        id = output["id"]
        outputs[id] = result  # 所有输出都给一样的结果（你也可以按 name 分别生成）
    outputs["next_node"] = next_node
    return outputs
# 示例调用
if __name__ == '__main__':
    question = "在操作飞行管理系统时不知道如何使用飞行计划界面，我也不明白导航数据链的分类协议是什么意思。"
    categories = [
        "飞行操作咨询",
        "机载系统故障",
        "适航规章咨询",
    ]
    result = classify_question(question, categories)
    print(result)
