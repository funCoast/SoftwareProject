import subprocess
import json
import tempfile
from api.core.workflow.registry import register_node
# 修改为（兼容 Python 3.8）：
from typing import Dict, List  # 在文件顶部添加

def safe_exec_javascript(code: str, inputs: Dict, output_vars: List[str]) -> Dict:
    try:
        # 自动生成解构语句
        destructure = f"const {{{', '.join(inputs.keys())}}} = input;"

        # 拼接完整 JS 代码
        temp_code = f"""
const input = {json.dumps(inputs)};
{destructure}

let output = {{}};

try {{
    {code}
    const result = {{ {", ".join([f'"{v}": typeof {v} !== "undefined" ? {v} : null' for v in output_vars])} }};
    console.log(JSON.stringify({{ result }}));
}} catch (err) {{
    console.log(JSON.stringify({{ error: err.message }}));
}}
"""
        with tempfile.NamedTemporaryFile("w+", suffix=".js", delete=False) as f:
            f.write(temp_code)
            f.flush()

            process = subprocess.run(["node", f.name], capture_output=True, text=True, timeout=5)
            output = process.stdout.strip()
            parsed = json.loads(output)
            if "result" in parsed:
                return parsed["result"]
            else:
                return {"error": parsed.get("error", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

def safe_exec_python(code: str, inputs: dict, output_vars: List[str]) -> Dict:
    """
    执行用户提供的 Python 代码，用户可自定义变量名和输出变量。
    :param code: 用户代码（任意 Python）
    :param inputs: 输入变量字典
    :param output_vars: 要返回的变量名列表
    :return: 包含用户指定的输出变量的字典
    """
    local_env = dict(inputs)
    try:
        exec(code, {}, local_env)

        outputs = {}
        for var in output_vars:
            if var in local_env:
                outputs[var] = local_env[var]
            else:
                outputs[var] = None  # 或 raise Exception(f"{var} 未定义")

        return outputs

    except Exception as e:
        return {"error":str(e)}
def safe_exec(code: str, inputs: dict, output_vars: List[str], language: str = "python") -> Dict:
    """
    支持多语言的动态代码执行器。
    :param code: 用户提供的代码
    :param inputs: 输入变量
    :param output_vars: 需要返回的变量名
    :param language: 语言类型，支持 'python', 'javascript'
    :return: 执行结果或错误信息
    """
    if language.lower() == "python":
        return safe_exec_python(code, inputs, output_vars)
    elif language.lower() == "javascript":
        return safe_exec_javascript(code, inputs, output_vars)
    else:
        return {"error": f"不支持的语言类型：{language}"}
@register_node("code")
def run_code_node(node,input):
    input_map = {
        inp["name"]: (
            float(inp["value"]) if inp.get("type") == "number" else inp["value"]
        )
        for inp in input
    }
    # 获取用户代码和语言类型
    code = node.get("data", {}).get("code", "")
    language = node.get("data", {}).get("language", "python")
    output_vars = [out["name"] for out in node.get("outputs", [])]
    result = safe_exec(code,input_map,output_vars,language)
    result_value = [value for value in result.values()]
    outputs = {}
    i = 0
    for output in node.get("outputs", []):
        id = output["id"]
        outputs[id] = result_value[i]  # 所有输出都给一样的结果（你也可以按 name 分别生成）
        i = i + 1
    return outputs


code = """
a = a * 10
b = b + 10
"""
inputs = {"a": 3, "b": 4}
output_vars = ["a", "b"]
print(safe_exec(code, inputs, output_vars))
print(safe_exec(
    code="let z = x + y + 1 + b + c + d;",
    inputs={"x": 10, "y": 5, "b": 2, "c": 3, "d":10},
    output_vars=["z"],
    language="javascript"
))