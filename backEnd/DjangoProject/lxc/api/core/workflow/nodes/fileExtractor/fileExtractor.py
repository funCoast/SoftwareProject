# file_extractor_node.py
import os

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text_from_docx(file_path):
    from docx import Document
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def extract_text_from_pdf(file_path):
    # 使用 pdfminer.six 进行解析
    from io import StringIO
    from pdfminer.high_level import extract_text
    return extract_text(file_path)

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        return extract_text_from_txt(file_path)
    elif ext in [".doc", ".docx"]:
        return extract_text_from_docx(file_path)
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError("不支持的文件格式")

# 示例调用
if __name__ == '__main__':
    # 假设文件路径已知，此处演示 txt 文件
    file_path = "example.docx"
    try:
        text = extract_text(file_path)
        print("提取文本：")
        print(text)
    except Exception as e:
        print(f"文件提取失败：{e}")
