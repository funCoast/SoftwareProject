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
        session_history,
        plugin_response,
        kb_response,
        workflow_response,
        max_tokens=1024
):
    def count_tokens(text):
        return len(text.split())

    prompt = "根据下面的信息，整合出适合回答输入部分的结果：\n"
    input_str = f"\t- 输入: {message}\n"
    plugin_str = f"\t- 调用插件得到结果: {str(plugin_response)}\n"
    context_str = "\t- 历史对话:\n"
    kb_str = f"\t- 调用已有知识库中的内容，得到：{kb_response}\n"
    workflow_str = f"\t- 调用工作流得到结果：{workflow_response}\n"

    total_tokens = count_tokens(prompt + input_str + plugin_str)

    for msg in reversed(session_history):
        msg_str = f"\t\t- {'User' if msg.is_user else 'Agent'}: {msg.content}\n"
        if total_tokens + count_tokens(msg_str) > max_tokens * 0.8:
            break
        context_str += msg_str
        total_tokens += count_tokens(msg_str)

    return prompt + input_str + plugin_str + kb_str + workflow_str + context_str