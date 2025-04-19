from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role
from django.conf import settings

def ask_llm(query: str, related_chunks: list) -> str:
    # 拼接上下文
    context_text = "\n".join([chunk['content'] for chunk in related_chunks])

    messages = [
        {"role": Role.SYSTEM, "content": "你是一个知识问答助手，根据提供的文档内容回答用户的问题。"},
        {"role": Role.USER, "content": f"文档内容如下：\n{context_text}"},
        {"role": Role.USER, "content": f"问题是：{query}"},
    ]

    response = Generation.call(
        model='qwen-max',
        messages=messages,
        api_key=settings.DASHSCOPE_API_KEY
    )

    if response.status_code == 200:
        return response.output.choices[0]['message']['content']
    else:
        raise Exception(f"通义千问调用失败: {response.message}")
