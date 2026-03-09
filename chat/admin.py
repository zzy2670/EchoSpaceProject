from django.contrib import admin
from .models import ChatRoom, RoomMembership, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "max_capacity", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


@admin.register(RoomMembership)
class RoomMembershipAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "joined_at")
    list_filter = ("room",)
    search_fields = ("user__username", "room__name")
    ordering = ("-joined_at",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("room", "sender", "content_preview", "created_at")
    list_filter = ("room", "created_at")
    search_fields = ("content", "sender__username")
    ordering = ("-created_at",)

    def content_preview(self, obj):
        return (obj.content or "")[:50] + ("..." if len(obj.content or "") > 50 else "")

    content_preview.short_description = "Content"
