import os
import docx
import markdown
from PyPDF2 import PdfReader

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    elif ext == '.pdf':
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text

    elif ext == '.docx':
        doc = docx.Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs])

    elif ext == '.md':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return markdown.markdown(f.read())  # 返回的是 HTML 字符串
        # 如果你希望保留 Markdown 原文：
        # return f.read()

    else:
        raise ValueError("不支持的文件类型")
