from api.core.agent.chat_bot.views import temp_send_message, send_agent_message
from django.urls import path

urlpatterns = [
    path('temp_conversation', temp_send_message, name='temp_conversation'),
    path('send_agent_message', send_agent_message, name='send_agent_message'),
]