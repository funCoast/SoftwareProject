import numpy as np
import json

from api.core.workflow.registry import register_node
from backend.models import User, KnowledgeBase, KnowledgeChunk
from django.conf import settings
import dashscope
from http import HTTPStatus

def get_tongyi_embedding(text):
    # 从 settings 获取 API key
    dashscope.api_key = getattr(settings, "DASHSCOPE_API_KEY", None)
    if not dashscope.api_key:
        print("[通义嵌入失败] 未配置 DASHSCOPE_API_KEY")
        return None

    try:
        resp = dashscope.TextEmbedding.call(
            model=dashscope.TextEmbedding.Models.text_embedding_v3,
            input=text,
            dimension=1024,
            output_type="dense&sparse"
        )
        if resp.status_code == HTTPStatus.OK:
            return resp.output["embeddings"][0]["embedding"]
        else:
            print(f"[通义嵌入异常返回] {resp}")
            return None
    except Exception as e:
        print(f"[通义嵌入失败] {str(e)}")
        return None


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

@register_node("kbRetrieval")
def run_kbRetrieval_node(node,inputs):
    query_text = inputs[0].get("value","")
    if not query_text:
        raise ValueError("query_text 不能为空")

    # 提取 node.data 中的 uid 和第一个 kb id
    data = node.get("data", {})
    uid = data.get("uid")
    kbs = data.get("kbs", [])
    if not uid or not kbs or not isinstance(kbs, list) or not kbs[0].get("id"):
        raise ValueError("缺少 uid 或知识库 ID")

    all_results = []

    # 遍历每个知识库，分别查询
    for kb in kbs:
        kb_id = kb.get("id")
        if kb_id is None:
            continue
        try:
            results = query_kb(uid=uid, kb_id=kb_id, query_text=query_text)
            all_results.extend(results)
        except Exception as e:
            print(f"[知识库 {kb_id} 查询失败]: {e}")

    # 按相似度排序（跨库合并后）
    all_results.sort(key=lambda x: x["similarity"], reverse=True)

    # 拼接所有 chunk 内容
    content = "\n".join([item["content"] for item in all_results])

    outputs = {}
    for output in node.get("outputs", []):
        id = output["id"]
        outputs[id] = content  # 所有输出都给一样的结果（你也可以按 name 分别生成）
    return outputs