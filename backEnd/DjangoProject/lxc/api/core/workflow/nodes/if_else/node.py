from typing import Any, Literal
from ...registry import register_node

def compare(compare_type:int,input_val,compare_val):
    match = False
    if compare_type == 1:  # 包含
        match = compare_val in input_val
    elif compare_type == 2:  # 不包含
        match = compare_val not in input_val
    elif compare_type == 3:  # 开始是
        match = input_val.startswith(compare_val)
    elif compare_type == 4:  # 结束是
        match = input_val.endswith(compare_val)
    elif compare_type == 5:  # 是（全等）
        match = input_val == compare_val
    elif compare_type == 6:  # 不是（不等）
        match = input_val != compare_val
    elif compare_type == 7:  # 为空
        match = input_val == ""
    elif compare_type == 8:  # 不为空
        match = input_val != ""
    return match

def judge_case(case: dict, inputs: list) -> bool:
    # 把 inputs 列表转成 dict: {name: value}
    input_dict = {item["name"]: item["value"] for item in inputs}

    # else 分支直接返回 True
    if "condition" not in case:
        return True

    conditions = case["condition"]
    and_or = case.get("and_or", 1)
    results = []

    for cond in conditions:
        variable = cond.get("variable")
        compare_value = cond.get("compare_value")
        compare_type = cond.get("compare_type")

        input_val = input_dict.get(variable, "")
        result = compare(compare_type, input_val, compare_value)
        results.append(result)

    # 返回条件组合的最终判断结果
    if and_or == 1:
        return all(results)
    else:
        return any(results)


@register_node("if_else")
def run_if_else_node(node, inputs):
    case_list = node.get("data", {}).get("case", [])

    # 预处理 inputs: list -> dict
    input_dict = {item["id"]: item["value"] for item in inputs}

    for case in case_list:
        conditions = case["condition"]
        if not conditions:
            return case.get("next_node")
        and_or = case.get("and_or", 1)
        results = []

        for cond in conditions:
            variable = cond.get("variable")
            compare_value = cond.get("compare_value")
            compare_type = cond.get("compare_type")
            input_val = input_dict.get(variable, "")
            result = compare(compare_type, input_val, compare_value)
            results.append(result)

        if (and_or == 1 and all(results)) or (and_or == 0 and any(results)):
            return {"next_node":case.get("next_node")}

    return None  # 所有条件都不满足
