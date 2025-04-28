import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from api.core.agent.chat_bot.llm_integration import LLMClient
from api.core.agent.chat_bot.session import get_or_create_session, save_message, get_limited_session_history, \
    generate_prompt_with_context
from api.core.agent.skill.plugin_call.plugin_call import plugin_call
from backend.models import User


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


