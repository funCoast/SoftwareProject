import os
import docx
from PyPDF2 import PdfReader

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt' or ext == '.md':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    elif ext == '.pdf':
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += (page.extract_text() or '') + '\n'
        return text

    elif ext == '.docx':
        doc = docx.Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs])

    else:
        raise ValueError(f"不支持的文件类型: {ext}")
