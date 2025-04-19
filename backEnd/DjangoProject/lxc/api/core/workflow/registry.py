# workflow/registry.py

from typing import Callable, Dict

# 注册表：type -> 执行函数
NODE_REGISTRY: Dict[str, Callable] = {}

def register_node(node_type: str):
    def decorator(func: Callable):
        NODE_REGISTRY[node_type] = func
        return func
    return decorator