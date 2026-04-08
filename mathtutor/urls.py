from django.contrib import admin
from django.urls import path, include
from app.views import ChatBotAppView, ChatBotApiView, LLMChatBotApiView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('', ChatBotAppView.as_view(), name='main'),
    path('api/chatbot/', ChatBotApiView.as_view(), name='chatbot'),
    path('api/llm-chatbot/', LLMChatBotApiView.as_view(), name='llm_chatbot'),
]
