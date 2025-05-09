import json
import os
import time
import uuid

from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from api.core.agent.chat_bot.llm_integration import LLMClient
from api.core.agent.chat_bot.session import get_or_create_session, save_message, get_limited_session_history, \
    generate_prompt_with_context
from api.core.agent.skill.plugin_call.plugin_call import plugin_call
from api.core.agent.skill.workflow_call import workflows_call
from backend.models import User, Agent, AgentKnowledgeEntry, AgentWorkflowRelation, KnowledgeBase, Workflow, Message
from backend.utils.queryKB import query_kb
from lxc import settings


@csrf_exempt
@require_http_methods(["POST"])
def temp_send_message(request):
    try:
        llm_client = LLMClient()
        data = json.loads(request.body)
        user_id = data.get('uid')
        message = data.get('content')
        agent_id = data.get('agent_id')

        input_str = f"这是用户输入: {message}\n"
        # 插件调用
        plugin_response = plugin_call(message)
        plugin_str = f"\t- 调用插件得到结果: {str(plugin_response)}\n"

        # 知识库调用
        agent = Agent.objects.get(agent_id=agent_id)
        entries = AgentKnowledgeEntry.objects.filter(agent=agent)
        kbs = [entry.kb for entry in entries]
        kb_response = []
        for kb in kbs:
            kb_response.append(query_kb(agent.user_id, kb.kb_id, message))
        kb_str = f"\t- 调用已有知识库中的内容，得到：{kb_response}\n"

        # 工作流调用
        entries = AgentWorkflowRelation.objects.filter(agent=agent)
        workflow_ids = [entry.workflow_id for entry in entries]
        workflow_response = workflows_call(input_str + plugin_str + kb_str, workflow_ids)
        workflow_str = f"\t- 调用工作流得到结果：{workflow_response}\n"

        persona_str = agent.persona
        prompt = "以上是用户的输入，下面是调用插件、调用用户知识库以及调用用户的工作流获得的信息，整合出适合回答用户输入部分的结果：\n"

        total_message = input_str + prompt + plugin_str + kb_str + workflow_str
        messages = [
            {
                "role": "system",
                "content": persona_str
            },
            {
                "role": "user",
                "content": total_message
            }
        ]
        response = llm_client.get_agent_response(messages).choices[0].message.content

        return JsonResponse({
            "code": 0,
            "message": "发送成功",
            "content": response,
            "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        })
    except Exception as e:
        return JsonResponse({
            "code": -1,
            "message": "发送失败",
            "content": str(e),
            "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_agent_message(request):
    try:
        # 解析数据
        data = json.loads(request.body)
        user = data.get('uid')
        agent_id = data.get('agent_id')
        message = data.get('content')

        # 获取或创建会话
        session, error = get_or_create_session(User.objects.get(user_id=user), agent_id)
        if not session:
            return JsonResponse({"status": "error", "message": error}, status=500)
        # 获取会话历史（最近10条消息）
        session_history = get_limited_session_history(session, max_messages=10)

        # 保存用户消息
        save_message(session, message, True)
        input_str = f"用户输入: {message}\n"
        # aaa 插件调用
        plugin_response = plugin_call(message)
        plugin_str = f"\t- 调用插件得到结果: {str(plugin_response)}\n"
        # bbb 知识库调用
        agent = Agent.objects.get(agent_id=agent_id)
        entries = AgentKnowledgeEntry.objects.filter(agent=agent)
        kbs = [entry.kb for entry in entries]
        kb_response = []
        for kb in kbs:
            kb_response.append(query_kb(agent.user_id, kb.kb_id, message))
        kb_str = f"\t- 调用已有知识库中的内容，得到：{kb_response}\n"
        # ccc 工作流调用
        entries = AgentWorkflowRelation.objects.filter(agent=agent)
        workflow_ids = [entry.workflow_id for entry in entries]
        workflow_response = workflows_call(input_str + plugin_str + kb_str, workflow_ids)

        # 生成提示词
        prompt = generate_prompt_with_context(
            message=message,
            plugin_response=str(plugin_response),
            kb_response=str(kb_response),
            workflow_response=str(workflow_response)
        )

        messages = [
            {
                "role": "system",
                "content": agent.persona
            }
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
            "content": prompt
        })

        # 调用大模型 API
        llm_client = LLMClient()
        response = llm_client.get_agent_response(messages).choices[0].message.content
        # 保存智能体响应
        save_message(session, response, False)

        return JsonResponse({
            "code": 0,
            "message": "发送成功",
            "content": response,
            "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        })

    except Exception as e:
        return JsonResponse({
            "code": -1,
            "message": "发送失败",
            "content": str(e),
            "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        }, status=500)

class AgentFetchAgentMessageView(View):

    def get(self, request):
        try:
            agent_id = request.GET.get('agent_id')
            uid = request.GET.get('uid')
            if not agent_id:
                return JsonResponse(
                    {"code": -1, "message": "缺少参数 agent_id"},
                    status=400,
                    json_dumps_params={'ensure_ascii': False}
                )

            if not uid:
                return JsonResponse(
                    {"code": -1, "message": "缺少参数 uid"},
                    status=400,
                    json_dumps_params={'ensure_ascii': False}
                )

            # 获取 Agent
            try:
                agent = Agent.objects.get(agent_id=agent_id)
            except Agent.DoesNotExist:
                return JsonResponse(
                    {"code": -1, "message": "未找到对应的智能体"},
                    status=404,
                    json_dumps_params={'ensure_ascii': False}
                )

            session, error = get_or_create_session(User.objects.get(user_id=uid), agent_id)
            if not session:
                return JsonResponse({"status": "error", "message": error}, status=500)

            chat_history = []
            messages = Message.objects.filter(conversation=session).order_by('timestamp')
            for msg in messages:
                chat_history.append({
                    "sender": "user" if msg.is_user else "assistant",
                    "content": msg.content,
                    "time": msg.timestamp,
                })

            return JsonResponse({
                "code": 0,
                "message": "获取成功",
                "chatHistory": chat_history,
            })
        except Exception as e:
            return JsonResponse({
                "code": -1,
                "message": str(e),
                "chatHistory": [],
            })

class AgentInfoView(View):
    """
    GET /agent/getInfo?agent_id=xxx
    不使用 DRF serializer，手动组装 JSON。
    """
    def get(self, request):
        agent_id = request.GET.get('agent_id')
        if not agent_id:
            return JsonResponse(
                {"code": -1, "message": "缺少参数 agent_id"},
                status=400,
                json_dumps_params={'ensure_ascii': False}
            )

        # 获取 Agent 或返回 404
        try:
            agent = Agent.objects.get(agent_id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse(
                {"code": -1, "message": "未找到对应的智能体"},
                status=404,
                json_dumps_params={'ensure_ascii': False}
            )

        # 手动查询关联的 KB、Plugin、Workflow
        kb_ids = list(
            AgentKnowledgeEntry.objects
            .filter(agent=agent)
            .values_list('kb_id', flat=True)
        )
        workflow_ids = list(
            AgentWorkflowRelation.objects
            .filter(agent=agent)
            .values_list('workflow_id', flat=True)
        )

        # 组装 config
        config = {
            "system_prompt": agent.persona or "",
            "selectedKbs": kb_ids,
            "selectedWorkflows": workflow_ids,
            "selectedModel": agent.llm,
        }

        if agent.status=='published':
            status = 2
        elif agent.status=='check':
            status = 1
        else:
            status = 0

        # 找 icon
        icon_url = agent.icon_url

        # 组装最终返回结构
        data = {
            "code": 0,
            "message": "获取成功",
            "config": config,
            "name": agent.agent_name,
            "icon": icon_url,
            "description": agent.description or "",
            "status": status,
        }
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

class AgentUpdateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"code": -1, "message": "JSON 格式错误"}, status=400)

        agent_id = data.get('agent_id')
        system_prompt = data.get('system_prompt')
        selected_kbs = data.get('selectedKbs', [])
        selected_workflows = data.get('selectedWorkflows', [])
        selected_model = data.get('selectedModel', [])

        if not agent_id:
            return JsonResponse({"code": -1, "message": "缺少 agent_id 参数"}, status=400)

        try:
            agent = Agent.objects.get(agent_id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({"code": -1, "message": "未找到对应的智能体"}, status=404)

        agent.persona = system_prompt
        agent.llm = selected_model
        agent.save()

        AgentKnowledgeEntry.objects.filter(agent=agent).delete()
        for kb_id in selected_kbs:
            try:
                kb = KnowledgeBase.objects.get(pk=kb_id)
                AgentKnowledgeEntry.objects.create(agent=agent, kb=kb, is_used=True)
            except KnowledgeBase.DoesNotExist:
                continue

        AgentWorkflowRelation.objects.filter(agent=agent).delete()
        for wf_id in selected_workflows:
            try:
                wf = Workflow.objects.get(pk=wf_id)
                AgentWorkflowRelation.objects.create(agent=agent, workflow=wf)
            except Workflow.DoesNotExist:
                continue

        return JsonResponse({"code": 0, "message": "修改成功"})

class AgentCreateView(View):
    """
    POST /agent/create
    接收 multipart/form-data 或 application/json:
      - uid: 创建者用户 ID（required）
      - name: 智能体名称（required）
      - description: 描述（optional）
      - icon: 图标文件（optional）
    返回 JSON:
      {
        "code": 0/-1,
        "message": "...",
        "agent_id": <新建智能体ID>  # 仅成功时返回
      }
    """
    def post(self, request):
        # 1. 解析 body（支持 JSON 或 form-data）
        if request.content_type.startswith("application/json"):
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse(
                    {"code": -1, "message": "JSON 格式错误"},
                    status=400, json_dumps_params={'ensure_ascii': False}
                )
            uid = data.get("uid")
            name = data.get("name")
            description = data.get("description", "")
            icon = None
        else:
            uid = request.POST.get("uid")
            name = request.POST.get("name")
            description = request.POST.get("description", "")
            icon = request.FILES.get("icon")

        if not uid:
            return JsonResponse(
                {"code": -1, "message": "缺少 uid 参数"},
                status=400, json_dumps_params={'ensure_ascii': False}
            )
        if not name:
            return JsonResponse(
                {"code": -1, "message": "缺少 name 参数"},
                status=400, json_dumps_params={'ensure_ascii': False}
            )

        # 验证用户
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return JsonResponse(
                {"code": -1, "message": "uid 对应的用户不存在"},
                status=404, json_dumps_params={'ensure_ascii': False}
            )

        # icon 上传
        icon_url = f"{settings.MEDIA_URL}agent_icons/defaultAgent.svg"
        if icon:
            icon_dir = os.path.join(settings.MEDIA_ROOT, 'agent_icons')
            os.makedirs(icon_dir, exist_ok=True)

            _, ext = os.path.splitext(icon.name)
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(icon_dir, filename)

            with open(filepath, 'wb+') as dst:
                for chunk in icon.chunks():
                    dst.write(chunk)

            icon_url = f"{settings.MEDIA_URL}agent_icons/{filename}"

        # 创建 Agent 实例
        try:
            agent = Agent.objects.create(
                agent_name=name,
                description=description,
                opening_line="",
                prompt="",
                persona="",
                category="uncategorized",
                icon_url=icon_url,
                user=user,
                status='private',
                is_modifiable=True,
            )
        except Exception as e:
            return JsonResponse(
                {"code": -1, "message": f"创建失败：{str(e)}"},
                status=500, json_dumps_params={'ensure_ascii': False}
            )

        return JsonResponse(
            {"code": 0, "message": "创建成功", "agent_id": agent.agent_id},
            json_dumps_params={'ensure_ascii': False}
        )