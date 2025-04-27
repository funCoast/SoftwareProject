from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from api.core.agent.chat_bot.llm_integration import LLMClient
from api.core.agent.skill.plugin_call.plugin_call import plugin_call


@csrf_exempt
@require_http_methods(["POST"])
def temp_send_message(request):
    try:
        llm_client = LLMClient()
        message = "北京今天几点, 是什么节日"

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

        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



