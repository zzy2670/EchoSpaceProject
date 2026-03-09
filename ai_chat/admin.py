from django.contrib import admin
from .models import AIConversation, AIMessage


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("title", "user__username")
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "content_preview", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content",)
    ordering = ("-created_at",)

    def content_preview(self, obj):
        return (obj.content or "")[:60] + ("..." if len(obj.content or "") > 60 else "")

    content_preview.short_description = "Content"
