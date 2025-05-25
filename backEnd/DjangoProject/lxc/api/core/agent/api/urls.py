from api.core.agent.api.views import temp_send_message, send_agent_message, AgentInfoView, AgentCreateView, \
    AgentUpdateView, AgentFetchAgentMessageView
from django.urls import path

urlpatterns = [
    path('sendMessage', temp_send_message, name='temp_conversation'),
    path('sendAgentMessage', send_agent_message, name='send_agent_message'),
    path('getInfo', AgentInfoView.as_view(), name='get_info'),
    path('updateInfo', AgentUpdateView.as_view(), name='update_info'),
    path('create', AgentCreateView.as_view(), name='create'),
    path('fetchAgentMessage', AgentFetchAgentMessageView.as_view(), name='fetch_agent_message'),
    path('clearHistoryMessage', AgentCreateView.as_view(), name='clear_history_message'),
]