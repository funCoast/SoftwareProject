import asyncio
import builtins
import textwrap
import types
import math
import datetime
import json

class Args:
    def __init__(self, params: dict):
        self.params = params

class CodeRunPlugin:
    def __init__(self):
        self.name = "CodeRunPlugin"
        self.version = "1.0"
        self.description = "执行代码并返回输出"

    def execute(self, *args, **kwargs):
        code = kwargs['code']
        variables = kwargs['variables']
        return asyncio.run(self._run_code(code, variables))


    async def _run_code(self, code: str, variables: list):
        # 构造参数
        args_dict = {}
        for var in variables:
            name, value, vtype = var["name"], var["value"], var["type"]
            if vtype == "int":
                args_dict[name] = int(value)
            elif vtype == "float":
                args_dict[name] = float(value)
            elif vtype == "bool":
                args_dict[name] = bool(value)
            elif vtype == "list":
                args_dict[name] = list(value)
            elif vtype == "dict":
                args_dict[name] = dict(value)
            else:  # 默认为字符串
                args_dict[name] = str(value)

        args_obj = Args(args_dict)

        # 安全的 builtins 白名单
        safe_builtins = {
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "enumerate": enumerate,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "pow": pow,
            "range": range,
            "reversed": reversed,
            "round": round,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
        }

        # 限制性模块（白名单）
        safe_modules = {
            "math": math,
            "datetime": datetime,
            "json": json,
        }

        # 构建执行环境
        global_env = {
            "__builtins__": safe_builtins,
            "Args": Args,
            "Output": dict,
            **safe_modules
        }
        local_env = {}

        try:
            clean_code = textwrap.dedent(code)
            exec(clean_code, global_env, local_env)

            main_func = local_env.get("main") or global_env.get("main")
            if not main_func or not asyncio.iscoroutinefunction(main_func):
                return {"status":"error", "message": "main 函数未定义或不是 async 函数"}

            # ⏱ 设置最大运行时间为 100 秒
            result = await asyncio.wait_for(main_func(args_obj), timeout=100)

            if not isinstance(result, dict):
                return {"status":"error", "message": "返回结果必须是字典类型"}

            return {"status":"success", "ret": result}

        except asyncio.TimeoutError:
            return {"status":"error", "message": "代码执行超时：运行超过 100 秒"}
        except Exception as e:
            return {"status":"error", "message": f"代码执行出错: {str(e)}"}


if __name__ == "__main__":
    code = """
async def main(args: Args) -> Output:
    params = args.params
    # 构建输出对象
    ret: Output = {
        "key0": params['input'] + params['input'], # 拼接两次入参 input 的值
        "key1": ["hello", "world"],  # 输出一个数组
        "key2": { # 输出一个Object 
            "key21": "hi"
        },
    }
    return ret
    return ret
    """
    variables = [
        {"name": "input", "value": "你好", "type": "str"},
    ]
    print(CodeRunPlugin().execute(code=code, variables=variables))