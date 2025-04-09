# kb_retrieval_node.py
def search_knowledge_base(query, knowledge_base):
    """
    模拟知识库检索，knowledge_base 为一个列表，每个元素为字典形式的知识条目。
    :param query: 用户问题查询关键词
    :param knowledge_base: 示例知识库，格式如下：
           [
             {"id": 1, "content": "这是有关技术的说明...", "source": "doc1"},
             {"id": 2, "content": "产品反馈相关说明...", "source": "doc2"},
             ...
           ]
    :return: 按相关性简单排序后的条目集合
    """
    # 这里简单采用关键字匹配；也可以使用更复杂的文本相似度算法。
    result = []
    for entry in knowledge_base:
        if query in entry["content"]:
            result.append(entry)
    # 此处简单排序，可以扩展为按匹配度排序
    return {"result": result}

# 示例调用
if __name__ == '__main__':
    sample_kb = [
        {"id": 1, "content": "如何解决软件安装过程中遇到的错误...", "source": "安装指南"},
        {"id": 2, "content": "产品体验反馈的常见问题...", "source": "用户反馈"},
    ]
    query = "安装"
    result = search_knowledge_base(query, sample_kb)
    print(result)
