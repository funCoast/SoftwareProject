from api.core.agent.chat_bot.views import temp_send_message
from django.urls import path

urlpatterns = [
    path('temp_conversation', temp_send_message, name='temp_conversation'),
]