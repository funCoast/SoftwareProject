# http_request_node.py
import time
import requests
from api.core.workflow.registry import register_node
import requests
import time
import os
import uuid
from django.conf import settings

def store_workflow_file(content: bytes, filename: str) -> str:
    """
    保存返回的文件内容到后端指定目录，并返回可访问的 URL
    """
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_dir = os.path.join(settings.MEDIA_ROOT, "workflow_files")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(content)

    # 你需要在 settings 中配置 MEDIA_URL = "/media/"
    return f"{settings.MEDIA_URL}workflow_files/{unique_name}"

def send_http_request(method, url, body=None, headers=None, retries=3, retry_interval=2):
    """
    支持文件保存与 URL 返回的 HTTP 请求函数
    """
    attempt = 0
    while attempt <= retries:
        try:
            response = requests.request(method, url, json=body, headers=headers)

            content_type = response.headers.get("Content-Type", "")
            is_json = "application/json" in content_type

            # 文件检测与存储
            file_urls = []
            if "Content-Disposition" in response.headers and "attachment" in response.headers["Content-Disposition"]:
                # 提取文件名
                disposition = response.headers["Content-Disposition"]
                filename = "unknown.bin"
                if "filename=" in disposition:
                    filename = disposition.split("filename=")[-1].strip('"')

                # 存储文件并获取 URL
                file_url = store_workflow_file(response.content, filename)
                file_urls.append(file_url)

            if response.ok:
                return {
                    "success": True,
                    "body": response.json() if is_json else response.text,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "files": file_urls
                }
            else:
                raise Exception(f"HTTP错误: {response.status_code}")

        except Exception as e:
            attempt += 1
            if attempt > retries:
                return {
                    "success": False,
                    "error": str(e),
                    "body": None,
                    "status_code": None,
                    "headers": {},
                    "files": []
                }
            time.sleep(retry_interval)
@register_node("httpRequest")
def run_httpRequest_node(node,inputs):
    method = inputs[1]
    url = inputs[0]
    result = send_http_request(method, url)
    outputs = {}
    i = 0
    for output in node.get("outputs", []):
        id = output["id"]
        if i == 0:
            outputs[id] = result["body"]
        elif i == 1:
            outputs[id] = result["status_code"]
        elif i == 2:
            outputs[id] = result["headers"]
        elif i == 3:
            outputs[id] = result["files"]
        i = i + 1
    return outputs

# 示例调用
if __name__ == '__main__':
    body = {"username":"testHttpNode","email":"1231414@test.com","password":"000000"}
    result = send_http_request("POST", "http://127.0.0.1:8000/backend/register", body=body, retries=2, retry_interval=1)
    print(result)
