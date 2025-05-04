from django.utils import timezone
import uuid

from backend.models import Agent, Session, Message


def generate_session_id(user_id):
    return f"user_{user_id}_{uuid.uuid4().hex[:8]}"

def get_or_create_session(user, agent_id):
    try:
        agent = Agent.objects.get(agent_id=agent_id)
    except Agent.DoesNotExist:
        return None, "Agent not found"
    session, created = Session.objects.get_or_create(
        user=user,
        agent=agent,
        defaults={'created_at': timezone.now()}
    )
    return session, None

def save_message(session, content, is_user):
    Message.objects.create(
        conversation=session,
        content=content,
        is_user=is_user
    )

def get_limited_session_history(session, max_messages=10):
    messages = Message.objects.filter(conversation=session).order_by('-timestamp')[:max_messages]
    return list(reversed(messages))  # 按时间顺序返回

def generate_prompt_with_context(
        message,
        plugin_response,
        kb_response,
        workflow_response
):
    def count_tokens(text):
        return len(text.split())

    prompt = "根据下面的信息，整合出适合回答输入部分的结果：\n"
    input_str = f"\t- 输入: {message}\n"
    plugin_str = f"\t- 调用插件得到结果: {str(plugin_response)}\n"
    kb_str = f"\t- 调用已有知识库中的内容，得到：{kb_response}\n"
    workflow_str = f"\t- 调用工作流得到结果：{workflow_response}\n"

    return prompt + input_str + plugin_str + kb_str + workflow_str