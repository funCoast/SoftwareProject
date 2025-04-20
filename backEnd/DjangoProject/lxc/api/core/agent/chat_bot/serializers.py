# serializers.py
from rest_framework import serializers

from backend.models import Agent, Conversation, Message


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['agent_id', 'agent_name']

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'agent', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'is_user', 'timestamp']