import re

# 自动清洗并分段
def auto_clean_and_split(text, max_len=500, overlap=50):
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return _split_text(cleaned, max_len, overlap)

# 自定义切分
def custom_split(text, max_len=300, overlap=30, clean=True):
    if clean:
        text = re.sub(r'\s+', ' ', text.strip())
    return _split_text(text, max_len, overlap)

def split_by_headings(text):
    pattern = re.compile(r'(?P<heading>#+\s+[^\n]+)')
    parts = pattern.split(text)

    chunks = []
    parent_stack = []  # 用于构建层级结构

    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ''
        level = heading.count('#')
        title = heading.replace('#', '').strip()

        # 建立当前 chunk
        chunk = {
            'title': title,
            'level': level,
            'content': content,
            'parent': None,
        }

        # 更新 parent_stack，根据层级找到上级父亲
        while parent_stack and parent_stack[-1]['level'] >= level:
            parent_stack.pop()

        if parent_stack:
            chunk['parent'] = parent_stack[-1]  # 记录父亲

        parent_stack.append(chunk)
        chunks.append(chunk)

    return chunks


# 公共切片函数
def _split_text(text, max_len=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        chunks.append(text[start:end])
        start += max_len - overlap
    return chunks
