"""
URL configuration for EchoSpace project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("accounts/", include("accounts.urls")),
    path("chat/", include("chat.urls")),
    path("chat/api/", include("chat.api_urls")),
    path("ai/", include("ai_chat.urls")),
    path("ai/api/", include("ai_chat.api_urls")),
    path("dashboard/", include("dashboard.urls")),
]
