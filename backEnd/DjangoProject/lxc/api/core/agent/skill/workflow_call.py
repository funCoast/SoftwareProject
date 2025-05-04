import ast

from openai import OpenAI

from api.core.workflow.workflow_tool import get_workflow_tool, run_workflow_tool

client = OpenAI(
    #该API-KEY为组内成员(hty)个人所有。
    api_key="sk-5b81b33eb54848d6826c38e75ecd9fc7",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def workflow_intent_recognition(text, description):

    prompt = f"""
            请根据用户输入和提供的功能描述，严格判断是否需要且能够调用该工作流。必须同时满足以下两个条件：  
            1. 用户需求与工作流描述直接相关  
            2. 工作流具备实现该需求的能力  
            若符合则返回1，否则返回0。仅返回单个数字，禁止任何解释或格式。  
            
            示例逻辑：  
            用户问"生成财报图表"，工作流描述是"自动处理Excel数据并生成可视化图表" → 1  
            用户问"预定会议室"，工作流描述是"处理文本翻译任务" → 0  
            
            当前判断：  
            用户输入："{text}"  
            工作流描述："{description}"
            """
    completion = client.chat.completions.create(
        model="qwen-max",
        messages=[{"role": "user", "content": prompt}]
    )

    intent_labels = completion.choices[0].message.content.strip()
    return False if int(intent_labels[0]) == 0 else True

def workflow_extract_parameters_by_model(text, description, parameters):
    prompt = f"""
        根据用户输入、工作流描述及参数类型要求，严格按以下规则生成参数列表：  
        1. 按参数定义顺序解析，强制保持列表长度与参数数量一致  
        2. 类型处理规则：  
           - str类型：无法解析时返回空字符串""  
           - int类型：无法解析时返回0  
           - bool类型：无法解析时返回False  
        3. 必须输出标准Python列表格式，确保能被ast.literal_eval()正确解析  
        
        示例：  
        参数格式：[str, int]  
        输入："明天下雨吗"  
        工作流："天气查询(city:str, days:int)"  
        → ["明天", 0]  
        
        参数格式：[int, str]  
        输入："生成上海报告"  
        工作流："报告生成(page_num:int, style:str)"  
        → [0, "上海"]  
        
        当前任务：  
        工作流描述："{description}"  
        参数定义：{parameters}  
        用户输入："{text}"  
        
        输出要求：  
        仅返回Python列表，禁止任何解释或附加字符。确保元素顺序、数量、类型与参数定义完全匹配。  
            """

    completion = client.chat.completions.create(
        model="qwen-max",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content

def workflows_call(message, workflow_ids):
    result = []
    for workflow_id in workflow_ids:
        workflow_tool = get_workflow_tool(workflow_id)
        description = workflow_tool["function"]["description"]
        parameters = workflow_tool["function"]["parameters"]
        if description and parameters and workflow_intent_recognition(message, description):
            params_str = workflow_extract_parameters_by_model(message, description, parameters)
            params = ast.literal_eval(params_str)
            sub_result = run_workflow_tool(workflow_id, params)
            result.append(sub_result)
    return result
