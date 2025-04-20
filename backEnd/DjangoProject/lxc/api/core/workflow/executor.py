# workflow/django_executor.py

import time
import uuid
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional

from api.core.workflow.registry import NODE_REGISTRY
from api.core.workflow.nodes import loader

class NodeExecutionError(Exception):
    pass


class Executor:
    def __init__(
        self,
        user_id: str,
        workflow_id: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, int]],
    ) -> None:
        self.user_id = user_id
        self.workflow_id = workflow_id
        self.nodes = {node["id"]: node for node in nodes}
        self.edges = edges
        self.graph = defaultdict(list)
        self.indegree = defaultdict(int)
        self.outputs: Dict[int, Dict[str, Any]] = {}

    def build_graph(self):
        for edge in self.edges:
            source = edge["sourceId"]
            target = edge["targetId"]
            self.graph[source].append(target)
            self.indegree[target] += 1
            if source not in self.indegree:
                self.indegree[source] = 0

    def topological_sort(self) -> List[int]:
        queue = deque([nid for nid in self.nodes if self.indegree[nid] == 0])
        order = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self.graph.get(current, []):
                self.indegree[neighbor] -= 1
                if self.indegree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise Exception("Workflow contains a cycle.")
        return order

    def resolve_inputs(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        inputs = []
        for input_item in node.get("inputs", []):
            val = input_item["value"]
            input_type = val["type"]
            input_name = input_item["name"]

            if val["type"] == 0:
                resolved_value = val["text"]
            elif val["type"] == 1:
                from_node = val["nodeId"]
                output_id = val["outputId"]
                resolved_value = self.outputs[from_node][output_id]
            else:
                resolved_value = None

            inputs.append({
                "name": input_name,
                "type": input_type,
                "value": resolved_value
            })
        return inputs

    """
    inputs类似于
    [
      {"name": "prompt", "type": "string", "value": "你好"},
      {"name": "context", "type": "string", "value": "背景信息"}
    ]
    """

    def run_node(self, node: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        node_type = node["type"]
        func = NODE_REGISTRY.get(node_type)
        if not func:
            raise NodeExecutionError(f"No registered function for node type '{node_type}'")
        return func(node, inputs)

    def execute(self) -> Dict[int, Dict[str, Any]]:
        self.build_graph()
        execution_order = self.topological_sort()

        for node_id in execution_order:
            node = self.nodes[node_id]
            inputs = self.resolve_inputs(node)
            outputs = self.run_node(node, inputs)
            self.outputs[node_id] = outputs
            print(f"[Executed] Node {node['name']} (ID: {node_id}) -> {outputs}")

        return self.outputs

