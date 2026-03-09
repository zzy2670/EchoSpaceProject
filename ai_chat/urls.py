from django.urls import path
from . import views

app_name = "ai_chat"
urlpatterns = [
    path("", views.ai_chat_view, name="ai_chat"),
    path("conversation/<int:conversation_id>/", views.ai_chat_view, name="conversation"),
]
