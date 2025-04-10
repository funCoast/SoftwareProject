"""
知识库检索模块（基于 Chroma + sentence-transformers）

功能说明：
    本模块用于从本地持久化的向量数据库（Chroma）中检索与用户查询最相似的知识内容。

参数说明：
    :param query: 用户查询问题（字符串）
    :param db_name: 知识库名称（对应 ./chroma_stores 下的子目录）
    :param top_k: 返回的相似内容条数，默认 5

返回格式：
    :return: 一个字典，字段 result 为按相关性排序的条目集合：
        [
            {
                "id": "文档ID",
                "content": "知识内容文本",
                "score": 相似度分数（越小越相似，默认欧氏距离）,
                "metadata": {其他元信息，如来源、页码等}
            },
            ...
        ]
"""

import chromadb
from sentence_transformers import SentenceTransformer

# 初始化 sentence-transformer 模型（支持中文，可替换为 bge 等模型）
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def search_chroma(query: str, db_name: str, top_k: int = 5):
    """
    在指定 Chroma 知识库中检索与 query 最相似的 top_k 条内容。

    :param query: 用户问题查询关键词
    :param db_name: 知识库名称（Chroma 存储路径为 ./chroma_stores/{db_name}）
    :param top_k: 返回结果数量，默认为 5
    :return: 检索结果，格式见上文
    """

    # 加载对应知识库路径
    client = chromadb.PersistentClient(path=f"./chroma_stores/{db_name}")
    collection = client.get_or_create_collection(name="documents")

    # 将 query 编码为向量（embedding）
    query_vec = embedding_model.encode(query).tolist()

    # 执行向量相似度搜索
    results = collection.query(
        query_embeddings=[query_vec],
        n_results=top_k
    )

    # 格式化并返回结果
    return {
        "result": [
            {
                "id": doc_id,
                "content": doc,
                "score": float(dist),
                "metadata": metadata or {}
            }
            for doc_id, doc, dist, metadata in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0]
            )
        ]
    }

# 示例调用：
if __name__ == '__main__':
    sample_kb = [
        {"id": "1", "content": "如何解决软件安装过程中的错误...", "metadata": {"source": "安装手册"}},
        {"id": "2", "content": "常见的产品使用反馈包括运行缓慢...", "metadata": {"source": "用户反馈"}}
    ]

    # 创建临时 Chroma 向量数据库
    from chromadb import Client
    from chromadb.config import Settings
    import os

    # 使用内存客户端用于模拟
    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=None))
    collection = client.get_or_create_collection(name="documents")

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")

    docs = [d["content"] for d in sample_kb]
    ids = [d["id"] for d in sample_kb]
    metadatas = [d["metadata"] for d in sample_kb]

    embeddings = model.encode(docs).tolist()
    collection.add(documents=docs, metadatas=metadatas, ids=ids, embeddings=embeddings)

    # 查询
    result = collection.query(
        query_embeddings=[model.encode("安装").tolist()],
        n_results=2
    )

    for doc, score in zip(result["documents"][0], result["distances"][0]):
        print(f"内容: {doc}  相似度: {score:.4f}")