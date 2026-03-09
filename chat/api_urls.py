from django.urls import path
from . import api_views

urlpatterns = [
    path("rooms/", api_views.lobby_rooms_api),
    path("rooms/<int:room_id>/messages/", api_views.room_messages_api),
    path("rooms/<int:room_id>/messages/send/", api_views.room_send_message_api),
    path("rooms/<int:room_id>/stats/", api_views.room_stats_api),
]
