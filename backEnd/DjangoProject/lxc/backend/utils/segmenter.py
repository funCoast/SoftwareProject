import re
from textwrap import wrap
from typing import List, Tuple

__all__ = [
    "auto_clean_and_split",
    "custom_split",
    "split_by_headings",
]

def auto_clean_and_split(text: str, blank_lines: int = 1) -> List[str]:
    """按连续空行 / 换行符自动分段，过滤空白行"""
    paragraphs, buf = [], []
    for line in text.splitlines():
        if line.strip():
            buf.append(line.strip())
        else:
            if buf:
                paragraphs.append(" ".join(buf).strip())
                buf.clear()
    if buf:
        paragraphs.append(" ".join(buf).strip())
    return paragraphs


def custom_split(text: str, chunk_size: int = 200) -> List[str]:
    """
    优先按自然段落切分（空行分段），再在段内做 wrap 切片。
    中文、英文都统一按字符宽度估算。
    """
    segments = []
    # 先按自然段落粗切
    paragraphs = auto_clean_and_split(text, blank_lines=1)

    for para in paragraphs:
        # 段内再按 chunk_size wrap 切片
        wrapped_chunks = wrap(para, width=chunk_size, replace_whitespace=False, drop_whitespace=False)
        segments.extend([chunk.strip() for chunk in wrapped_chunks if chunk.strip()])

    return segments


_HD = re.compile(r"^\s*(#+)\s+(.*)$")

def split_by_headings(text: str) -> List[Tuple[int, str]]:
    """
    读取 Markdown，返回 (level, text) 列表，按原顺序。
    level = 1 对应 '# '，level = 2 对应 '## '……
    普通正文行以上一个标题为父节点，level = parent_level + 1
    """
    chunks: list[tuple[int, str]] = []
    current_level = 0
    buf = []

    def flush_buf():
        nonlocal buf, current_level
        if buf:
            chunks.append((current_level + 1, " ".join(buf).strip()))
            buf.clear()

    for line in text.splitlines():
        m = _HD.match(line)
        if m:
            flush_buf()
            current_level = len(m.group(1))          # '#' 的个数
            chunks.append((current_level, m.group(2).strip()))
        else:
            if line.strip():
                buf.append(line.strip())
    flush_buf()
    return chunks
