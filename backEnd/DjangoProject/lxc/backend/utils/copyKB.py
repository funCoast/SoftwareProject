from backend.models import KnowledgeBase, KnowledgeFile, KnowledgeChunk
from django.utils import timezone
import uuid

def clone_knowledge_base(kb_id: int, new_kb_name: str = None) -> int:
    """
    克隆指定的知识库，包括文件和片段。
    :param kb_id: 要复制的知识库ID
    :param new_kb_name: 新知识库名称（不传则自动和之前一致）
    :return: 新知识库的ID
    """
    try:
        old_kb = KnowledgeBase.objects.get(kb_id=kb_id)
    except KnowledgeBase.DoesNotExist:
        raise ValueError("待复制的知识库不存在")

    # 1. 克隆 KnowledgeBase
    new_kb = KnowledgeBase.objects.create(
        uuid=uuid.uuid4(),
        kb_name=new_kb_name or f"{old_kb.kb_name}",
        kb_type=old_kb.kb_type,
        kb_description=old_kb.kb_description,
        user=old_kb.user,
        icon=old_kb.icon,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    # 2. 克隆 KnowledgeFile
    old_files = old_kb.files.all()
    old_file_map = {}  # old_file.id -> new_file
    for old_file in old_files:
        new_file = KnowledgeFile.objects.create(
            kb=new_kb,
            file=old_file.file,
            name=old_file.name,
            segment_mode=old_file.segment_mode,
            uploaded_at=timezone.now()
        )
        old_file_map[old_file.id] = new_file

    # 3. 克隆 KnowledgeChunk
    old_chunks = KnowledgeChunk.objects.filter(kb=old_kb).order_by('chunk_id')
    old_chunk_map = {}  # old_chunk.id -> new_chunk

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

    # 4. 处理 parent 关联（二次更新）
    for old_chunk in old_chunks:
        if old_chunk.parent_id:
            new_chunk = old_chunk_map[old_chunk.chunk_id]
            new_parent = old_chunk_map.get(old_chunk.parent_id)
            if new_parent:
                new_chunk.parent = new_parent
                new_chunk.save(update_fields=['parent'])

    print(f"[INFO] 知识库 {kb_id} 已成功复制为 {new_kb.kb_id}")

    return new_kb.kb_id
