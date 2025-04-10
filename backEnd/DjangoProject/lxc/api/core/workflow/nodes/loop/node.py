from typing import Any, Dict, Callable, Literal
from datetime import datetime

def run_loop_node(
    loop_count: int,
    loop_variables: Dict[str, Any],
    condition_checker: Callable[[Dict[str, Any]], bool],
    loop_body_executor: Callable[[Dict[str, Any], int], Dict[str, Any]],
    break_conditions: list[dict] = [],
    logical_operator: Literal["and", "or"] = "and"
) -> Dict[str, Any]:
    """
    通用简化版循环节点逻辑。

    参数:
    - loop_count: 循环次数
    - loop_variables: 初始循环变量
    - condition_checker: 检查是否满足 break 条件的函数
    - loop_body_executor: 每轮循环的执行体，返回变量字典
    - break_conditions: 用于外部 break 判断（可选）
    - logical_operator: 多条件连接逻辑（默认 and）

    返回:
    - 输出结果，包括每轮输出和总循环时长等
    """
    start_time = datetime.now()
    loop_outputs = {}
    all_round_outputs = {}

    for index in range(loop_count):
        loop_variables['index'] = index
        output = loop_body_executor(loop_variables.copy(), index)
        all_round_outputs[index] = output
        loop_variables.update(output)

        if condition_checker(output):
            break

    end_time = datetime.now()

    loop_outputs["outputs"] = loop_variables
    loop_outputs["loop_round_outputs"] = all_round_outputs
    loop_outputs["duration"] = (end_time - start_time).total_seconds()
    return loop_outputs