import os
import uuid

from django.core.files.storage import default_storage

from api.core.agent.chat_bot.llm_integration import LLMClient
from api.core.agent.skill.file_analyse.file_analyse import FileAnalyse
from api.core.agent.skill.plugin_call.plugin_call import plugin_call
from api.core.agent.skill.workflow_call import workflows_call
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

        # 无论成功与否，最终删除文件
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception as e:
                print(f"文件删除失败：{str(e)}")

        return result

    except KeyError:
        return False

    except Exception as e:
        return False

def gen_response(user_id, agent_id, message, files, can_search, session_history):
    try:
        user = User.objects.get(user_id=user_id)
        agent = Agent.objects.get(agent_id=agent_id)

        # 文件读取
        file_str = ""
        if len(files) != 0:
            session_id = "temp" + str(uuid.uuid4())
            file_str = f"\t- 上传的文件识别结果：{upload_and_process_file(files[0], session_id, message)}"
        # 插件调用
        plugin_str = f"\t- 插件调用结果：{call_plugin(message)}"
        # 知识库查询
        kb_str = f"\t- 知识库查询结果：{call_kb(agent, message)}"
        # 工作流运行
        workflow_str = f"\t- 工作流运行结果：{call_workflow(agent, file_str + plugin_str + kb_str + message)}"

        # 总结输入
        total_prompt = (f"{message}\n" + """
以上是用户输入，请按以下流程处理用户请求：
1. **多源信息整合**：
   - 优先使用用户知识库的权威信息
   - 补充插件提供的实时数据
   - 适配用户工作流的具体场景
   
2. **自然语言生成**：
   - 将技术术语转换为日常表达（如："数据库查询结果" → "根据现有记录"）
   - 使用连接词平滑衔接不同来源信息
   - 避免出现"系统检测""调用接口"等技术表述

3. **结果呈现**：
   - 采用「结论先行」结构
   - 复杂信息使用分项说明（•）
   - 数据展示需附带简要解释
   - 保持口语化表达（Flesch可读性分数>60）
   
最终输出应让用户感知为连贯的自然答复，不暴露后台处理过程。
        """ +
                        file_str + plugin_str + kb_str + workflow_str)

        messages = [
            {
                "role": "system",
                "content": agent.persona
            },
        ]

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
        else:
            response = LLMClient().call_qwen_message(messages)

        return response

    except Exception as e:
        return {
            'response': str(e),
        }

def gen_response_temp(user_id, agent_id, message, files, can_search):
    try:
        user = User.objects.get(user_id=user_id)
        agent = Agent.objects.get(agent_id=agent_id)

        # 文件读取
        file_str = ""
        if len(files) != 0:
            session_id = "temp" + str(uuid.uuid4())
            file_str = f"\t- 上传的文件识别结果：{upload_and_process_file(files[0], session_id, message)}"
        # 插件调用
        plugin_str = f"\t- 插件调用结果：{call_plugin(message)}"
        # 知识库查询
        kb_str = f"\t- 知识库查询结果：{call_kb(agent, message)}"
        # 工作流运行
        workflow_str = f"\t- 工作流运行结果：{call_workflow(agent, file_str + plugin_str + kb_str + message)}"

        # 总结输入
        total_prompt = (f"{message}\n" + """
以上是用户输入，请按以下流程处理用户请求：
1. **多源信息整合**：
   - 优先使用用户知识库的权威信息
   - 补充插件提供的实时数据
   - 适配用户工作流的具体场景
   
2. **自然语言生成**：
   - 将技术术语转换为日常表达（如："数据库查询结果" → "根据现有记录"）
   - 使用连接词平滑衔接不同来源信息
   - 避免出现"系统检测""调用接口"等技术表述

3. **结果呈现**：
   - 采用「结论先行」结构
   - 复杂信息使用分项说明（•）
   - 数据展示需附带简要解释
   - 保持口语化表达（Flesch可读性分数>60）
   
最终输出应让用户感知为连贯的自然答复，不暴露后台处理过程。
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
        else:
            response = LLMClient().call_qwen_message(messages)

        print(response)
        return response

    except Exception as e:
        return {
            'response': str(e),
        }



