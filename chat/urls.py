from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("", views.lobby_view, name="lobby"),
    path("rooms/create/", views.create_room_view, name="create_room"),
    path("rooms/<int:room_id>/join/", views.join_room_view, name="join_room"),
    path("rooms/<int:room_id>/", views.room_view, name="room"),
    path("rooms/<int:room_id>/leave/", views.leave_room_view, name="leave_room"),
]
