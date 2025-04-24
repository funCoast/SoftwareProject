from api.core.agent.chat_bot.views import send_message
from django.urls import path

urlpatterns = [
    path('temp/conversation', send_message, name='conversation'),
]