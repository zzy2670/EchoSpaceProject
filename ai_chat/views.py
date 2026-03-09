from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import AIConversation


@login_required
def ai_chat_view(request, conversation_id=None):
    """Single template for new chat and viewing a past conversation."""
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
        },
    )
