import numpy as np
import json

def query_kb(uid, kb_id, query_text, top_k=5):
    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        raise ValueError("用户不存在")

    try:
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except KnowledgeBase.DoesNotExist:
        raise ValueError("知识库不存在或无权限")

    # 生成查询文本的嵌入
    query_embedding = get_tongyi_embedding(query_text)
    if not query_embedding:
        raise ValueError("查询文本嵌入生成失败")

    query_vector = np.array(query_embedding)

    # 查询所有知识片段
    chunks = KnowledgeChunk.objects.filter(kb=kb)

    similarities = []
    for chunk in chunks:
        if chunk.embedding:
            try:
                chunk_vector = np.array(json.loads(chunk.embedding))
                similarity = np.dot(query_vector, chunk_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(chunk_vector))
                similarities.append((chunk, similarity))
            except Exception as e:
                print(f"[解析chunk向量失败]: {e}")

    # 按相似度排序
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_chunks = similarities[:top_k]

    # 返回简洁结果
    results = []
    for chunk, score in top_chunks:
        results.append({
            "id": chunk.chunk_id,
            "content": chunk.content,
            "similarity": float(score)
        })

    return results
