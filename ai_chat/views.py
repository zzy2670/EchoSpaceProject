# AI Tree Hole page; same template for new chat or opening by conversation_id (history). Context keys used by template: don't rename.
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, get_object_or_404

from .models import AIConversation


@login_required
def ai_chat_view(request, conversation_id=None):
    # appflow_enabled / appflow_url come from settings, template picks iframe vs fallback
    conversation = None
    if conversation_id:
        conversation = get_object_or_404(
            AIConversation,
            id=conversation_id,
            user=request.user,
        )
    conversations = AIConversation.objects.filter(user=request.user).order_by("-updated_at")[:20]
    return render(
        request,
        "ai_chat/ai_chat.html",
        {
            "conversation": conversation,
            "conversations": conversations,
            "appflow_enabled": getattr(settings, "APPFLOW_AI_CHAT_ENABLED", False),
            "appflow_url": getattr(settings, "APPFLOW_AI_CHAT_URL", ""),
        },
    )
