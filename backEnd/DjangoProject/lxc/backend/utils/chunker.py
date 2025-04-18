def split_text(text, max_len=500, overlap=50):
    """
    把长文本切成多个小块，用于向量化
    max_len: 每块最大长度
    overlap: 相邻块之间的重叠部分，避免上下文割裂
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_len
        chunk = text[start:end]
        chunks.append(chunk)
        start += max_len - overlap
    return chunks
