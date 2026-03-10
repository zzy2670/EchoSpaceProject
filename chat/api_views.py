import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .models import ChatRoom
from . import services


def _json_ok(data):
    # lobby/room APIs wrap in "data" key
    return JsonResponse({"ok": True, "data": data})


def _json_error(msg):
    return JsonResponse({"ok": False, "error": msg}, status=400)


@require_GET
def lobby_rooms_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "Authentication required"}, status=401)
    data = services.get_lobby_room_data()
    return _json_ok(data)


@require_GET
@login_required
def room_messages_api(request, room_id):
    room = ChatRoom.objects.filter(id=room_id).first()
    if not room:
        return _json_error("Room not found")
    from .models import RoomMembership
    if not RoomMembership.objects.filter(room=room, user=request.user).exists():
        return JsonResponse({"ok": False, "error": "Not a member of this room"}, status=403)
    after_id = request.GET.get("after_id")
    if after_id is not None:
        try:
            after_id = int(after_id)
        except ValueError:
            after_id = None
    messages_list = services.get_room_messages(room, after_id=after_id)
    payload = [
        {
            "id": m.id,
            "sender_name": m.sender.public_name,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages_list
    ]
    return _json_ok(payload)


@require_POST
@login_required
def room_send_message_api(request, room_id):
    room = ChatRoom.objects.filter(id=room_id).first()
    if not room:
        return _json_error("Room not found")
    from .models import RoomMembership
    if not RoomMembership.objects.filter(room=room, user=request.user).exists():
        return JsonResponse({"ok": False, "error": "Not a member of this room"}, status=403)
    content = request.POST.get("content")
    if not content and request.body:
        try:
            body = json.loads(request.body.decode("utf-8"))
            content = body.get("content", "")
        except (ValueError, KeyError):
            content = ""
    content = (content or "").strip()
    if not content:
        return _json_error("Message content is required")
    try:
        msg = services.send_room_message(request.user, room, content)
        return _json_ok({
            "id": msg.id,
            "sender_name": msg.sender.public_name,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
        })
    except Exception as e:
        return _json_error(str(e))


@require_GET
@login_required
def room_stats_api(request, room_id):
    room = ChatRoom.objects.filter(id=room_id).first()
    if not room:
        return _json_error("Room not found")
    return _json_ok({
        "current_count": room.current_member_count(),
        "max_capacity": room.max_capacity,
    })
