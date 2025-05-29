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
        # 🔄 创建 indegree 的副本
        indegree_copy = dict(self.indegree)
        queue = deque([nid for nid in self.nodes if indegree_copy[nid] == 0])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self.graph.get(current, []):
                indegree_copy[neighbor] -= 1
                if indegree_copy[neighbor] == 0:
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
            input_id = input_item["id"]

            if val["type"] == 0:
                resolved_value = val["text"]
            elif val["type"] == 1:
                from_node = val["nodeId"]
                output_id = val["outputId"]
                resolved_value = self.outputs[from_node][output_id]
            else:
                resolved_value = None

            inputs.append({
                "id": input_id,
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

    def execute_from_node(self, start_node_id: int, visited: set):
        if start_node_id in visited:
            return
        visited.add(start_node_id)

        node = self.nodes[start_node_id]
        inputs = self.resolve_inputs(node)
        outputs = self.run_node(node, inputs)
        self.outputs[start_node_id] = outputs

        print(f"[Executed] Node {node['name']} (ID: {start_node_id}) -> {outputs}")

        # ✅ 特殊处理 if_else
        if node["type"] == "if_else":
            next_node_id = outputs.get(0)
            if next_node_id is not None and next_node_id in self.nodes:
                self.execute_from_node(next_node_id, visited)
            return  # ❗终止后续 neighbors 遍历

        # ✅ 特殊处理 classifier
        if node["type"] == "classifier":
            next_node_id = outputs.get(0)
            if next_node_id is not None and next_node_id in self.nodes:
                self.execute_from_node(next_node_id, visited)
            return

        # 🔁 默认递归所有下游
        for neighbor in self.graph.get(start_node_id, []):
            self.execute_from_node(neighbor, visited)

    def execute(self) -> Dict[int, Dict[str, Any]]:
        self.build_graph()
        self.topological_sort()  # 仍然可用于环检测
        start_nodes = [nid for nid in self.nodes if self.indegree[nid] == 0]
        print("start_nodes: ", start_nodes)
        visited = set()

        for node_id in start_nodes:
            self.execute_from_node(node_id, visited)

        return self.outputs

