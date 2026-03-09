from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "display_name", "is_guest", "is_staff", "is_active", "created_at")
    list_filter = ("is_guest", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "display_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("display_name", "is_guest", "created_at", "updated_at")}),
    )
