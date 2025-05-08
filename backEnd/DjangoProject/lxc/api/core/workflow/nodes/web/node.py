import requests

from api.core.workflow.registry import register_node

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from itertools import groupby

def extract_dynamic_text(url: str) -> str:
    chrome_options = Options()
    chrome_options.add_argument("--headless")        # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--lang=zh-CN")      # 中文网页
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(3)  # 等待 JS 渲染

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # 提取所有可见文本
        texts = soup.find_all(string=True)
        visible_texts = [
            t.strip() for t in texts
            if t.strip() and t.parent.name not in ['script', 'style', 'meta', 'noscript']
        ]

        # 去掉重复和杂乱内容
        cleaned = []
        for key, group in groupby(visible_texts):
            if len(key) > 1:
                cleaned.append(key)

        # 返回格式化后的字符串
        return "\n\n".join(cleaned)

    except Exception as e:
        return f"Error: {e}"

    finally:
        driver.quit()

@register_node("web")
def run_web_node(node, inputs):
    """
    工作流中 llm 类型节点的执行函数
    :param node: 节点配置（含 outputs）
    :return: {'response': json_string}
    """
    url = inputs[0].get("value","")
    result = extract_dynamic_text(url)

    # 自动生成 outputs（按输出定义）
    outputs = {}
    for output in node.get("outputs", []):
        id = output["id"]
        outputs[id] = result  # 所有输出都给一样的结果（你也可以按 name 分别生成）
    return outputs

if __name__ == '__main__':
    print(extract_dynamic_text("https://www.bilibili.com/"))