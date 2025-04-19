from ...registry import register_node
@register_node("start")
def run_start_node(node,input):
    outputs = {}
    i = 0
    for output in node.get("outputs", []):
        id = output["id"]
        outputs[id] = input[i]["value"]
        i = i + 1
    return outputs