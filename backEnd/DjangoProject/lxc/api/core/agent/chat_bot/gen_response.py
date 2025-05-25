import os
import uuid
from idlelib.rpc import response_queue

from django.core.files.storage import default_storage

from api.core.agent.chat_bot.llm_integration import LLMClient
from api.core.agent.skill.file_analyse.file_analyse import FileAnalyse
from api.core.agent.skill.plugin_call.plugin_call import plugin_call
from backend.models import User, Agent, AgentKnowledgeEntry, AgentWorkflowRelation
from backend.utils.queryKB import query_kb
from lxc import settings


def call_kb(agent: Agent, message):
    entries = AgentKnowledgeEntry.objects.filter(agent=agent)
    kbs = [entry.kb for entry in entries]
    kb_response = []
    for kb in kbs:
        kb_response.append(query_kb(agent.user_id, kb.kb_id, message))
    return f'\t- 调用已有知识库中的内容，得到：{kb_response}\n'

def call_plugin(message):
    plugin_response = plugin_call(message)
    return f"\t- 调用插件得到结果: {str(plugin_response)}\n"

def call_workflow(agent: Agent, message):
    entries = AgentWorkflowRelation.objects.filter(agent=agent)
    workflow_ids = [entry.workflow_id for entry in entries]
    from api.core.agent.skill.workflow_call import workflows_call
    workflow_response = workflows_call(message, workflow_ids)
    return f"\t- 调用工作流得到结果：{workflow_response}\n"


def upload_and_process_file(uploaded_file, session_id, message):
    try:
        # 安全校验
        ALLOWED_TYPES = [
            # 文本类
            'text/plain',
            # PDF
            'application/pdf',
            # Word
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            # Excel
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ]  # 允许的文件类型
        MAX_SIZE = 1 * 1024 * 1024  # 文件限制 1MB

        if uploaded_file.content_type not in ALLOWED_TYPES:
            return False
        if uploaded_file.size > MAX_SIZE:
            return False

        # 动态生成保存路径
        session_file_dir = os.path.join(settings.MEDIA_ROOT, "session_files")
        save_dir = os.path.join(session_file_dir, session_id)
        os.makedirs(save_dir, exist_ok=True)

        # 动态生成唯一文件名（新增代码）
        original_name = os.path.basename(uploaded_file.name)  # 去除路径保留纯文件名
        safe_name = default_storage.get_available_name(original_name)  # 生成唯一文件名
        save_path = os.path.join(save_dir, safe_name)

        # 保存文件到指定位置
        with open(save_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # 处理
        result = FileAnalyse().analyze(save_path, message)


        return result

    except KeyError:
        return False

    except Exception as e:
        return False

def call_agent(agent_id, message):
    return gen_response_temp(agent_id, message, [], False)

def gen_response(user_id, agent_id, message, files, can_search, session_history):
    try:
        user = User.objects.get(user_id=user_id)
        agent = Agent.objects.get(agent_id=agent_id)

        # 文件读取
        file_str = ""
        for file in files:
            session_id = "temp" + str(uuid.uuid4())
            file_str += f"\t- 上传的文件识别结果：{upload_and_process_file(file, session_id, message)}"
        # 插件调用
        plugin_str = f"\t- 插件调用结果：{call_plugin(message)}"
        # 知识库查询
        kb_str = f"\t- 知识库查询结果：{call_kb(agent, message)}"
        # 工作流运行
        workflow_str = f"\t- 工作流运行结果：{call_workflow(agent, file_str + plugin_str + kb_str + message)}"

        # 总结输入
        total_prompt = (f"{message}\n" + """
以上是用户输入，请按以下规则处理用户请求：
【输入分析阶段】
1. 请求类型检测：
   - 问候类：直接匹配预设社交话术库
   - 模糊查询：启动澄清引导协议
   - 明确需求：激活多源信息整合

【多阶段处理流程】
1. 基础响应层（优先级）：
   - 匹配用户意图置信度>80%的直接响应
   - 社交礼仪场景使用自然对话模板：
     ✓ 问候语："你好！有什么可以帮您？"
     ✓ 道谢："不客气，随时为您效劳"
   
2. 增强响应层（需触发）：
   - 当检测到实体名词≥2 或 包含明确操作动词时：
    ① 知识库检索（最新版本优先）
    ② 插件调用（需满足时效性<2分钟）
    ③ 工作流适配（符合用户历史操作模式）
   
3. 模糊处理协议：
   - 信息不足时使用渐进式引导：
     "关于XX事项，您需要了解哪些具体细节？"
     "是否需要比较XX功能的A方案和B方案？"

【输出规范】
1. 会话连续性：
   - 保留上下文记忆窗口（最近3轮对话）
   - 自动补全省略的主语/宾语
   
2. 异常处理：
   - 无有效信息时转向能力边界说明：
     "目前关于XX的详细指南正在整理中，是否需要我帮您记录具体需求？"
   
3. 人格化约束：
   - 禁止出现调用过程描述
   - 错误使用幽默/表情符号
   - 信息存疑时标注置信度提示词：
     "通常来说..." "建议您可以..." 
        """ +
                        file_str + plugin_str + kb_str + workflow_str)

        messages = [
            {
                "role": "system",
                "content": agent.persona
            },
        ]

        if agent.opening_line != "":
            messages.append({
                "role": "assistant",
                "content": agent.opening_line
            })

        for msg in session_history:
            cur_message = {}
            if msg.is_user:
                cur_message["role"] = "user"
            else:
                cur_message["role"] = "assistant"
            cur_message["content"] = msg.content
            messages.append(cur_message)

        messages.append({
            "role": "user",
            "content": total_prompt
        })

        if can_search:
            response = LLMClient().call_qwen_messages(messages, True)
        elif agent.llm == 'deepseek-r1':
            response = LLMClient().call_deepseek_messages(messages)
        elif agent.llm == 'qwen-plus':
            response = LLMClient().call_qwen_messages(messages)
        elif agent.llm == 'chatglm-6b-v2':
            response = LLMClient.call_glm_messages(messages)
        else:
            response = LLMClient().call_qwen_messages(messages)

        return response

    except Exception as e:
        return {
            'response': str(e),
        }

def gen_response_temp(agent_id, message, files, can_search):
    try:
        agent = Agent.objects.get(agent_id=agent_id)

        # 文件读取
        file_str = ""
        for file in files:
            session_id = "temp" + str(uuid.uuid4())
            file_str += f"\t- 上传的文件识别结果：{upload_and_process_file(file, session_id, message)}"
        # 插件调用
        plugin_str = f"\t- 插件调用结果：{call_plugin(message)}"
        # 知识库查询
        kb_str = f"\t- 知识库查询结果：{call_kb(agent, message)}"
        # 工作流运行
        workflow_str = f"\t- 工作流运行结果：{call_workflow(agent, file_str + plugin_str + kb_str + message)}"

        # 总结输入
        total_prompt = (f"{message}\n" + """
以上是用户输入，请按以下规则处理用户请求：
【输入分析阶段】
1. 请求类型检测：
   - 问候类：直接匹配预设社交话术库
   - 模糊查询：启动澄清引导协议
   - 明确需求：激活多源信息整合

【多阶段处理流程】
1. 基础响应层（优先级）：
   - 匹配用户意图置信度>80%的直接响应
   - 社交礼仪场景使用自然对话模板：
     ✓ 问候语："你好！有什么可以帮您？"
     ✓ 道谢："不客气，随时为您效劳"
   
2. 增强响应层（需触发）：
   - 当检测到实体名词≥2 或 包含明确操作动词时：
    ① 知识库检索（最新版本优先）
    ② 插件调用（需满足时效性<2分钟）
    ③ 工作流适配（符合用户历史操作模式）
   
3. 模糊处理协议：
   - 信息不足时使用渐进式引导：
     "关于XX事项，您需要了解哪些具体细节？"
     "是否需要比较XX功能的A方案和B方案？"

【输出规范】
1. 会话连续性：
   - 保留上下文记忆窗口（最近3轮对话）
   - 自动补全省略的主语/宾语
   
2. 异常处理：
   - 无有效信息时转向能力边界说明：
     "目前关于XX的详细指南正在整理中，是否需要我帮您记录具体需求？"
   
3. 人格化约束：
   - 禁止出现调用过程描述
   - 错误使用幽默/表情符号
   - 信息存疑时标注置信度提示词：
     "通常来说..." "建议您可以..." 
        """ +
                        file_str + plugin_str + kb_str + workflow_str)

        messages = [
            {
                "role": "system",
                "content": agent.persona
            },
            {
                "role": "user",
                "content": total_prompt
            }
        ]

        if can_search:
            response = LLMClient().call_qwen_messages(messages, True)
        elif agent.llm == 'deepseek-r1':
            response = LLMClient().call_deepseek_messages(messages)
        elif agent.llm == 'qwen-plus':
            response = LLMClient().call_qwen_messages(messages)
        elif agent.llm == 'chatglm-6b-v2':
            response = LLMClient.call_glm_messages(messages)
        else:
            response = LLMClient().call_qwen_message(messages)

        print(response)
        return response

    except Exception as e:
        return {
            'response': str(e),
        }



