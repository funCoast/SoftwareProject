from typing import Any, Literal


def resolve_variable(variable_selector: list[str], variable_pool: dict[str, dict[str, Any]]) -> Any:
    """
    从变量池中解析变量值。
    :param variable_selector: 变量选择器，例如 ["node_id", "input"]
    :param variable_pool: 当前执行上下文的变量池
    :return: 解析得到的变量值
    """
    node_id, key = variable_selector
    return variable_pool.get(node_id, {}).get(key)


def process_condition(
    condition: dict,
    variable_pool: dict[str, dict[str, Any]]
) -> bool:
    """
    处理单个条件判断。
    :param condition: 条件定义 dict
    :param variable_pool: 当前变量池
    :return: bool 判断结果
    """
    left_value = resolve_variable(condition["variable_selector"], variable_pool)
    right_value = condition["value"]
    operator = condition["comparison_operator"]

    if operator == "is":
        return left_value == right_value
    elif operator == "is_not":
        return left_value != right_value
    elif operator == "contains":
        return isinstance(left_value, str) and right_value in left_value
    elif operator == "not_contains":
        return isinstance(left_value, str) and right_value not in left_value
    else:
        raise ValueError(f"Unsupported comparison_operator: {operator}")


def process_conditions_group(
    conditions: list[dict],
    operator: Literal["and", "or"],
    variable_pool: dict[str, dict[str, Any]]
) -> bool:
    """
    处理一组条件与逻辑组合。
    """
    results = [process_condition(cond, variable_pool) for cond in conditions]
    return all(results) if operator == "and" else any(results)


def evaluate_if_else_node(
    node_data: dict,
    variable_pool: dict[str, dict[str, Any]]
) -> dict:
    """
    处理 if-else 节点判断逻辑。
    :param node_data: 节点配置数据（来自前端 JSON）
    :param variable_pool: 当前变量池
    :return: 判断结果，包括是否命中和选择的 case_id
    """
    for case in node_data.get("cases", []):
        conditions = case.get("conditions", [])
        operator = case.get("logical_operator", "and")
        passed = process_conditions_group(conditions, operator, variable_pool)

        if passed:
            return {
                "result": True,
                "selected_case_id": case["case_id"],
                "edge_source_handle": case["case_id"]
            }

    return {
        "result": False,
        "selected_case_id": "false",
        "edge_source_handle": "false"
    }