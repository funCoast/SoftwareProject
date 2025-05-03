import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from api.core.agent.chat_bot.llm_integration import LLMClient
from api.core.agent.chat_bot.session import get_or_create_session, save_message, get_limited_session_history, \
    generate_prompt_with_context
from api.core.agent.skill.plugin_call.plugin_call import plugin_call
from backend.models import User, Agent, AgentKnowledgeEntry, AgentWorkflowRelation, KnowledgeBase, Workflow


@csrf_exempt
@require_http_methods(["POST"])
def temp_send_message(request):
    try:
        llm_client = LLMClient()
        data = json.loads(request.body)
        message = data.get('message')

        # 插件调用
        plugin_response = plugin_call(message)

        # 知识库调用
        # 工作流调用

        prompt = "根据下面的信息，整合出适合回答输入部分的结果：\n"
        input_str = f"\t- 输入: {message}\n"
        plugin_str = f"\t- 调用插件得到结果: {str(plugin_response)}\n"
        kb_str = f"\t- 调用已有知识库中的内容，得到：[]\n"
        workflow_str = f"\t- 调用工作流得到结果：[]\n"

        total_message = prompt + input_str + plugin_str + kb_str + workflow_str
        response = llm_client.generate_response(total_message)

        return JsonResponse({"response": response})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def send_agent_message(request):
    try:
        data = json.loads(request.body)
        user = data.get('user_id')
        agent_id = data.get('agent_id')
        message = data.get('message')
        # 获取或创建会话
        session, error = get_or_create_session(User.objects.get(user_id=user), agent_id)
        if not session:
            return JsonResponse({"status": "error", "message": error}, status=500)

        # 保存用户消息
        save_message(session, message, True)

        # 获取会话历史（最近10条消息）
        session_history = get_limited_session_history(session, max_messages=10)

        # 插件调用
        plugin_response = plugin_call(message)

        # 知识库调用
        kb_response = ""

        # 工作流调用
        workflow_response = ""

        # 生成提示词
        prompt = generate_prompt_with_context(
            message=message,
            session_history=session_history,
            plugin_response=plugin_response,
            kb_response=kb_response,
            workflow_response=workflow_response
        )

        # 调用大模型 API
        llm_client = LLMClient()
        response = llm_client.generate_response(prompt)

        # 保存智能体响应
        save_message(session, response, False)

        return JsonResponse({"response": response})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

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
        # 如果有插件关联表，放在这里类似查询
        plugin_ids = []

        # 组装 config
        config = {
            "system_prompt": agent.persona or "",
            "selectedKbs": kb_ids,
            "selectedPlugins": plugin_ids,
            "selectedWorkflows": workflow_ids,
        }

        # 组装最终返回结构
        data = {
            "code": 0,
            "message": "获取成功",
            "config": config,
            "name": agent.agent_name,
            # TODO icon
            "icon": "",
            "description": agent.description or "",
            # TODO 审核
            "status": 2 if agent.is_published else 0,
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
        selected_plugins = data.get('selectedPlugins', [])
        selected_workflows = data.get('selectedWorkflows', [])

        # 参数校验
        if not agent_id:
            return JsonResponse({"code": -1, "message": "缺少 agent_id 参数"}, status=400)

        try:
            agent = Agent.objects.get(agent_id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({"code": -1, "message": "未找到对应的智能体"}, status=404)

        # 更新 system_prompt
        agent.persona = system_prompt
        agent.save()

        # 更新知识库关联：清除旧记录再添加新记录
        AgentKnowledgeEntry.objects.filter(agent=agent).delete()
        for kb_id in selected_kbs:
            try:
                kb = KnowledgeBase.objects.get(pk=kb_id)
                AgentKnowledgeEntry.objects.create(agent=agent, kb=kb, is_used=True)
            except KnowledgeBase.DoesNotExist:
                continue  # 跳过非法 kb_id

        # 更新工作流关联
        AgentWorkflowRelation.objects.filter(agent=agent).delete()
        for wf_id in selected_workflows:
            try:
                wf = Workflow.objects.get(pk=wf_id)
                AgentWorkflowRelation.objects.create(agent=agent, workflow=wf)
            except Workflow.DoesNotExist:
                continue

        # 插件更新逻辑（如有插件模型）
        # AgentPluginRelation.objects.filter(agent=agent).delete()
        # for plugin_id in selected_plugins:
        #     try:
        #         plugin = Plugin.objects.get(pk=plugin_id)
        #         AgentPluginRelation.objects.create(agent=agent, plugin=plugin)
        #     except Plugin.DoesNotExist:
        #         continue

        return JsonResponse({"code": 0, "message": "修改成功"})