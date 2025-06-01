# backend/services/copy_kb.py
from backend.models import KnowledgeBase, KnowledgeFile, KnowledgeChunk
from django.core.files.base import File
from django.db import transaction
from django.utils import timezone
import uuid, os

@transaction.atomic
def clone_knowledge_base(user, kb_id: int, new_kb_name: str | None = None) -> int:
    """
    将指定知识库完整克隆给“负责人”user。
    - 物理文件复制并移动到 knowledge/user_<user_id>/ 目录
    - 知识库名称自动去重
    """
    # ---------- 1. 获取旧知识库 ----------
    try:
        old_kb = KnowledgeBase.objects.get(kb_id=kb_id)
    except KnowledgeBase.DoesNotExist:
        raise ValueError("待复制的知识库不存在")

    # ---------- 2. 生成唯一的新知识库名称 ----------
    base_name = new_kb_name or old_kb.kb_name
    while KnowledgeBase.objects.filter(kb_name=base_name, user=user).exists():
        base_name = f"{old_kb.kb_name}_副本_{uuid.uuid4().hex[:4]}"

    # ---------- 3. 创建新 KnowledgeBase ----------
    new_kb = KnowledgeBase.objects.create(
        uuid=uuid.uuid4(),
        kb_name=base_name,
        kb_type=old_kb.kb_type,
        kb_description=old_kb.kb_description,
        user=user,
        icon=old_kb.icon,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )


    # ---------- 4. 复制 KnowledgeFile ----------
    old_file_map: dict[int, KnowledgeFile] = {}
    for old_file in old_kb.files.all():
        # 4.1 读取旧文件内容
        with open(old_file.file.path, "rb") as f:
            ext = os.path.splitext(old_file.file.name)[-1]
            dj_file = File(f, name=f"{uuid.uuid4().hex[:8]}{ext}")

            # 4.2 先创建对象但不传 file，让 upload_to 回调根据新 user 构造路径
            new_file = KnowledgeFile(kb=new_kb,
                                     name=old_file.name,
                                     segment_mode=old_file.segment_mode,
                                     uploaded_at=timezone.now())

            # 4.3 保存文件（触发 user_upload_path → knowledge/user_<new_uid>/…）
            new_file.file.save(dj_file.name, dj_file, save=True)

        old_file_map[old_file.id] = new_file

    # ---------- 5. 复制 KnowledgeChunk ----------
    old_chunks = KnowledgeChunk.objects.filter(kb=old_kb).order_by('chunk_id')
    old_chunk_map: dict[int, KnowledgeChunk] = {}

    for old_chunk in old_chunks:
        new_chunk = KnowledgeChunk.objects.create(
            kb=new_kb,
            file=old_file_map[old_chunk.file.id],
            content=old_chunk.content,
            order=old_chunk.order,
            level=old_chunk.level,
            embedding=old_chunk.embedding,
            created_at=timezone.now()
        )
        old_chunk_map[old_chunk.chunk_id] = new_chunk

    # ---------- 6. 二次更新 parent 关系 ----------
    for old_chunk in old_chunks:
        if old_chunk.parent_id:
            child = old_chunk_map[old_chunk.chunk_id]
            parent = old_chunk_map.get(old_chunk.parent_id)
            if parent:
                child.parent = parent
                child.save(update_fields=["parent"])

    # ---------- 7. 返回结果 ----------
    print(f"[INFO] 知识库 {kb_id} 已成功复制为 {new_kb.kb_id}（所有文件已归档至 user_{user.user_id}）")
    return new_kb.kb_id
