from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, Message
from ai_chat.models import AIConversation

User = get_user_model()


@staff_member_required
def dashboard_home(request):
    total_users = User.objects.count()
    guest_count = User.objects.filter(is_guest=True).count()
    room_count = ChatRoom.objects.count()
    message_count = Message.objects.count()
    ai_conv_count = AIConversation.objects.count()
    recent_rooms = ChatRoom.objects.select_related("created_by").order_by("-created_at")[:10]
    recent_messages = Message.objects.select_related("room", "sender").order_by("-created_at")[:15]
    recent_conversations = AIConversation.objects.select_related("user").order_by("-updated_at")[:10]
    return render(
        request,
        "dashboard/dashboard_home.html",
        {
            "total_users": total_users,
            "guest_count": guest_count,
            "room_count": room_count,
            "message_count": message_count,
            "ai_conv_count": ai_conv_count,
            "recent_rooms": recent_rooms,
            "recent_messages": recent_messages,
            "recent_conversations": recent_conversations,
        },
    )
