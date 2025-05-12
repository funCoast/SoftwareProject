import requests

from api.core.workflow.registry import register_node

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from itertools import groupby

def extract_dynamic_text(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="load")

        html = page.content()
        browser.close()

        soup = BeautifulSoup(html, "html.parser")
        texts = soup.find_all(string=True)
        visible_texts = [
            t.strip() for t in texts
            if t.strip() and t.parent.name not in ['script', 'style', 'meta', 'noscript']
        ]

        cleaned = []
        for key, group in groupby(visible_texts):
            if len(key) > 1:
                cleaned.append(key)

        return "\n\n".join(cleaned)

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