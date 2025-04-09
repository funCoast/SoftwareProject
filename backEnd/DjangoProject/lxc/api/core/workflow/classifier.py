# classifier_node.py
import openai
import os

# 初始化 openai 客户端，可根据需要传入 API Key
openai.api_key = os.getenv("DASHSCOPE_API_KEY")


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
    prompt = f"请根据下面的问题内容选择最合适的分类，并给出简要解释。\n\n问题：{question}\n\n"
    for cat, desc in categories.items():
        prompt += f"分类：{cat}，说明：{desc}\n"
    prompt += "\n请输出最合适的分类以及简要解释。"

    response = openai.ChatCompletion.create(
        model="qwen-max-latest",  # 或使用其他支持的模型
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    # 从返回结果中提取文本，可根据返回格式进一步解析
    result_text = response.choices[0].message.content
    return {"raw_result": result_text}


# 示例调用
if __name__ == '__main__':
    question = "我在使用新软件时遇到了一些技术问题..."
    categories = {
        "技术咨询": "关于技术、软件、编程的问题",
        "产品反馈": "对产品体验的意见反馈",
        "常见问题": "系统常见问题或 FAQ"
    }
    result = classify_question(question, categories)
    print(result)
