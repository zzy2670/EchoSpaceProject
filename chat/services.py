from django.core.exceptions import ValidationError
from django.conf import settings

from .models import ChatRoom, RoomMembership, Message

User = settings.AUTH_USER_MODEL


def create_room(user, cleaned_data):
    if getattr(user, "is_guest", False):
        raise ValidationError("Guests cannot create rooms.")
    name = (cleaned_data.get("name") or "").strip()
    if not name:
        raise ValidationError("Room name is required.")
    if ChatRoom.objects.filter(name=name).exists():
        raise ValidationError("A room with this name already exists.")
    description = (cleaned_data.get("description") or "").strip()[:255]
    max_capacity = cleaned_data.get("max_capacity", 20)
    if max_capacity < 2 or max_capacity > 100:
        raise ValidationError("Max capacity must be between 2 and 100.")
    room = ChatRoom.objects.create(
        name=name,
        description=description,
        max_capacity=max_capacity,
        created_by=user,
    )
    RoomMembership.objects.create(room=room, user=user)
    return room


def join_room(user, room):
    if room.is_full():
        raise ValidationError("This room is full.")
    if RoomMembership.objects.filter(room=room, user=user).exists():
        return
    RoomMembership.objects.create(room=room, user=user)


def leave_room(user, room):
    RoomMembership.objects.filter(room=room, user=user).delete()


def send_room_message(user, room, content):
    content = (content or "").strip()
    if not content:
        raise ValidationError("Message content cannot be empty.")
    if len(content) > 1000:
        raise ValidationError("Message is too long.")
    if not RoomMembership.objects.filter(room=room, user=user).exists():
        raise ValidationError("You must be a member of this room to send messages.")
    return Message.objects.create(room=room, sender=user, content=content)


def get_room_messages(room, after_id=None):
    qs = room.messages.all()
    if after_id is not None:
        qs = qs.filter(id__gt=after_id)
    return list(qs)


def get_lobby_room_data():
    rooms = ChatRoom.objects.select_related("created_by").all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "max_capacity": r.max_capacity,
            "current_count": r.current_member_count(),
            "created_at": r.created_at.isoformat(),
            "created_at_display": r.created_at.strftime("%b %d, %Y"),
            "created_by_name": r.created_by.public_name,
        }
        for r in rooms
    ]
