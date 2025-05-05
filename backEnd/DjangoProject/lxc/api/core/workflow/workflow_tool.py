from django.core.exceptions import ObjectDoesNotExist

from backend.models import Workflow
import json
from api.core.workflow.executor import Executor
def get_workflow_tool(workflow_id):
    workflow = Workflow.objects.get(workflow_id=workflow_id)
    nodes = workflow.nodes
    description = workflow.description
    start = nodes[0]
    parameters = []
    for output in start["outputs"]:
        parameters.append({
            "name": output["name"],
            "type": output["type"],
            "description": output["description"],
        })

    return {
            "type":"workflow",
            "function":{
                "name": workflow.name,
                "workflow_description": description,
                "start_description": start["description"],
                "parameters":parameters
            }
            }

def run_workflow_tool(workflow_id, inputs):
    # 获取 Workflow 对象
    workflow = Workflow.objects.get(workflow_id=workflow_id)

    nodes = json.loads(workflow.nodes)
    edges = json.loads(workflow.edges)

    # 找到 start 节点
    for node in nodes:
        if node.get("type") == "start":
            for i, input_item in enumerate(node.get("inputs", [])): #替换输入
                if i < len(inputs):
                    input_item["value"]["text"] = inputs[i]
            break  # 只有一个 start 节点

    # 执行工作流
    executor = Executor(0, workflow_id, nodes, edges)
    result = executor.execute()
    end_outputs = {}
    end_node_ids = {node["id"] for node in nodes if node.get("type") == "end"}

    for node_id in result:
        if node_id in end_node_ids:
            end_outputs[node_id] = result[node_id]
    return end_outputs