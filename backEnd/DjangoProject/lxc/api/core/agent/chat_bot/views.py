# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.models import Agent, Conversation, Message
from .serializers import AgentSerializer, ConversationSerializer, MessageSerializer
from .llm_integration import LLMClient
from ..skill.plugin_call.plugin_call import plugin_choose_and_run


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def create(self, request):
        agent = Agent.objects.get(pk=request.data['agent_id'])
        conversation = Conversation.objects.create(
            user=request.user,
            agent=agent
        )
        return Response(ConversationSerializer(conversation).data)



@action(detail=False, methods=['post'], url_path='send/(?P<conversation_id>\d+)')
def send_message(self, request, conversation_id=None):
    conversation = Conversation.objects.get(pk=conversation_id)
    message = Message.objects.create(
        conversation=conversation,
        content=request.data['content'],
        is_user=True
    )

    # 异步调用大模型
    self.process_ai_response(conversation, message)

    return Response({'status': 'processing'})

def process_ai_response(self, conversation, user_message):
    # 调用大模型接口
    llm_client = LLMClient()
    response = llm_client.generate_response(user_message.content)

    Message.objects.create(
        conversation=conversation,
        content=response,
        is_user=False
    )



