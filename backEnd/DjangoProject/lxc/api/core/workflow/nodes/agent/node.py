from openai import OpenAI
from api.core.agent.chat_bot.gen_response import call_agent
from ...registry import register_node

@register_node("agent")
def run_llm_node(node, inputs):
    """
    工作流中 llm 类型节点的执行函数
    :param node: 节点配置（含 outputs）
    :return: {'response': json_string}
    """
    text = inputs[0].get("value", "")
    agent_id = node.get("data", {}).get("agent_id", "")
    result = call_agent(agent_id,text)

    # 自动生成 outputs（按输出定义）
    outputs = {}
    for output in node.get("outputs", []):
        id = output["id"]
        outputs[id] = result  # 所有输出都给一样的结果（你也可以按 name 分别生成）
    return outputs
