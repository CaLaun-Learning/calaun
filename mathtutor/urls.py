from django.contrib import admin
from django.urls import path, include
from app.views import LLMChatBotApiView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('api/chatbot/', LLMChatBotApiView.as_view(), name='chatbot'),
]
