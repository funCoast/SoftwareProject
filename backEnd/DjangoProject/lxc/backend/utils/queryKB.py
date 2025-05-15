import numpy as np
import json
from backend.models import User, KnowledgeBase, KnowledgeChunk
from backend.views import get_tongyi_embedding

def query_kb(uid, kb_id, query_text, top_k=5, threshold=0.6):
    """
    基于余弦相似度的知识库检索
    :param uid: 用户ID
    :param kb_id: 知识库ID
    :param query_text: 查询文本
    :param top_k: 返回前k个最相关chunk
    :param threshold: 相似度阈值（0~1之间）
    """
    try:
        user = User.objects.get(user_id=uid)
    except User.DoesNotExist:
        raise ValueError("用户不存在")

    try:
        kb = KnowledgeBase.objects.get(kb_id=kb_id, user=user)
    except KnowledgeBase.DoesNotExist:
        raise ValueError("知识库不存在或无权限")

    query_embedding = get_tongyi_embedding(query_text)
    if not query_embedding:
        raise ValueError("查询文本嵌入生成失败")

    query_vector = np.array(query_embedding)

    chunks = KnowledgeChunk.objects.filter(kb=kb)

    chunk_vectors = []
    chunk_infos = []

    for chunk in chunks:
        if chunk.embedding:
            try:
                vec = json.loads(chunk.embedding)
                chunk_vectors.append(vec)
                chunk_infos.append(chunk)
            except Exception as e:
                print(f"[解析chunk向量失败]: {e}")

    if not chunk_vectors:
        print("[WARN] 无可用的 chunk 向量")
        return []

    chunk_matrix = np.array(chunk_vectors)
    query_norm = np.linalg.norm(query_vector)
    chunk_norms = np.linalg.norm(chunk_matrix, axis=1)
    chunk_norms[chunk_norms == 0] = 1e-10

    similarities = np.dot(chunk_matrix, query_vector) / (chunk_norms * query_norm)

    # 先根据 threshold 过滤，再按相似度排序
    filtered = [(idx, sim) for idx, sim in enumerate(similarities) if sim >= threshold]

    if not filtered:
        print(f"[INFO] 没有相似度 >= {threshold} 的匹配项")
        return []

    # 排序后取 top_k
    filtered.sort(key=lambda x: x[1], reverse=True)
    top_filtered = filtered[:top_k]

    results = []
    for idx, score in top_filtered:
        chunk = chunk_infos[idx]
        results.append({
            "id": chunk.chunk_id,
            "content": chunk.content,
            "similarity": float(score)
        })

    return results
