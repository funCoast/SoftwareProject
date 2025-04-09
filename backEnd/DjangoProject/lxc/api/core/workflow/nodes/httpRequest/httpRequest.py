# http_request_node.py
import time
import requests

def send_http_request(method, url, body=None, headers=None, retries=3, retry_interval=2):
    """
    发送HTTP请求，并在请求失败时根据参数设置重试。
    :param method: 请求方法，例如 "GET", "POST" 等
    :param url: 请求的URL
    :param body: 请求体数据（字典、JSON 字符串或者其他格式，根据实际需要处理）
    :param headers: 请求头字典
    :param retries: 失败时的重试次数
    :param retry_interval: 重试间隔（秒）
    :return: 包含响应状态码，响应数据以及是否成功的字典
    """
    attempt = 0
    while attempt <= retries:
        try:
            response = requests.request(method, url, json=body, headers=headers)
            # 可以根据响应状态码判断是否成功，例如 200-299 是成功的
            if response.ok:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text
                }
            else:
                # 非正常响应时也可能重试
                raise Exception(f"HTTP错误: {response.status_code}")
        except Exception as e:
            attempt += 1
            if attempt > retries:
                return {"success": False, "error": str(e)}
            time.sleep(retry_interval)

# 示例调用
if __name__ == '__main__':
    body = {"username":"testHttpNode","email":"1231414@test.com","password":"000000"}
    result = send_http_request("POST", "http://127.0.0.1:8000/backend/register", body=body, retries=2, retry_interval=1)
    print(result)
