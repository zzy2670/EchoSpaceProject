from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .models import ChatRoom
from .forms import CreateRoomForm
from . import services


@login_required
@require_http_methods(["GET"])
def lobby_view(request):
    rooms_data = services.get_lobby_room_data()
    form = CreateRoomForm() if not request.user.is_guest else None
    return render(
        request,
        "chat/lobby.html",
        {"rooms": rooms_data, "form": form, "is_guest": getattr(request.user, "is_guest", False)},
    )


@login_required
@require_http_methods(["GET", "POST"])
def create_room_view(request):
    if getattr(request.user, "is_guest", False):
        messages.error(request, "Guests cannot create rooms.")
        return redirect("chat:lobby")
    if request.method == "POST":
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            try:
                room = services.create_room(request.user, form.cleaned_data)
                messages.success(request, f"Room '{room.name}' created.")
                return redirect("chat:room", room_id=room.id)
            except Exception as e:
                messages.error(request, str(e))
        else:
            for err in form.non_field_errors():
                messages.error(request, err)
            for field in form:
                for err in field.errors:
                    messages.error(request, err)
    return redirect("chat:lobby")


@login_required
@require_http_methods(["POST"])
def join_room_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    try:
        services.join_room(request.user, room)
        messages.success(request, f"You joined '{room.name}'.")
        return redirect("chat:room", room_id=room.id)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("chat:lobby")


@login_required
@require_http_methods(["GET"])
def room_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    from .models import RoomMembership
    is_member = RoomMembership.objects.filter(room=room, user=request.user).exists()
    if not is_member:
        messages.error(request, "You must join this room first.")
        return redirect("chat:lobby")
        
    messages_list = services.get_room_messages(room)
    last_msg_id = messages_list[-1].id if messages_list else 0
    
    rooms_data = services.get_lobby_room_data()
    
    return render(
        request,
        "chat/room.html",
        {
            "room": room,
            "messages_list": messages_list,
            "current_count": room.current_member_count(),
            "last_message_id": last_msg_id,
            "rooms": rooms_data, 
        },
    )


@login_required
@require_http_methods(["POST"])
def leave_room_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    services.leave_room(request.user, room)
    messages.info(request, f"You left '{room.name}'.")
    return redirect("chat:lobby")