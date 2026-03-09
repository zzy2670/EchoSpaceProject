from django.urls import path
from . import api_views

urlpatterns = [
    path("send/", api_views.ai_send_api),
]
