from django.urls import path
from .views import chat_sync, chat_stream_view

app_name = 'chatbot'

urlpatterns = [
    path('chat/', chat_sync, name='chat'),
    path('chat/stream/', chat_stream_view, name='chat_stream'),
]
