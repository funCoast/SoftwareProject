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
        1. 逐一检查每个参数要求，从用户输入中提取对应信息  
        2. 若无法提取则根据参数类型和描述设置合理默认值  
        3. 确保最终输出为Python合法列表，可被ast.literal_eval解析  
        
        输出格式要求：  
        [{"name": 参数名, "value": 解析值或默认值}, ...]  
        
        注意：  
        - 值必须符合参数类型（字符串加引号，数字不加）  
        - 必须包含所有参数  
        - 禁止任何解释，仅返回列表  
        
        示例：  
        参数要求：[{"name": "city", "type": "string", "description": "城市名称（英文）"}]  
        用户输入："今天天气怎么样"  
        输出：[{"name": "city", "value": "Beijing"}]  
        
        参数要求：[{"name": "start_date", "type": "string"}, {"name": "end_date", "type": "string"}]  
        用户输入："生成图表"  
        输出：[{"name": "start_date", "value": "2023-01-01"}, {"name": "end_date", "value": "2023-12-31"}]  
        
        当前任务：  
        用户输入："{text}"  
        工作流描述："{description}"  
        参数列表：{parameters}  
        
        请输出解析结果：  
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
        start_description = workflow_tool["function"]["start_description"]
        parameters = workflow_tool["function"]["parameters"]
        if description and start_description and parameters and workflow_intent_recognition(message, description):
            params_str = workflow_extract_parameters_by_model(message, description + start_description, parameters)
            params = ast.literal_eval(params_str)
            sub_result = run_workflow_tool(workflow_id, params)
            result.append(sub_result)
    return result
