from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import ChatRoom, RoomMembership, Message

User = get_user_model()


class ChatTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="user1",
            email="u1@example.com",
            password="pass123",
            display_name="User One",
        )
        self.guest = User.objects.create_user(
            username="guest_abc",
            email="g@guest.echospace.local",
            display_name="Guest",
            is_guest=True,
        )
        self.guest.set_unusable_password()
        self.guest.save()
        self.room = ChatRoom.objects.create(
            name="Test Room",
            description="A test room",
            max_capacity=5,
            created_by=self.user,
        )
        RoomMembership.objects.create(room=self.room, user=self.user)

    def test_registered_user_can_create_room(self):
        self.client.login(username="user1", password="pass123")
        response = self.client.post(
            reverse("chat:create_room"),
            {"name": "New Room", "description": "Desc", "max_capacity": 10},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ChatRoom.objects.filter(name="New Room").exists())

    def test_guest_cannot_create_room(self):
        self.client.force_login(self.guest)
        response = self.client.post(
            reverse("chat:create_room"),
            {"name": "Guest Room", "description": "", "max_capacity": 5},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ChatRoom.objects.filter(name="Guest Room").exists())

    def test_user_can_join_room(self):
        room2 = ChatRoom.objects.create(
            name="Room 2",
            max_capacity=10,
            created_by=self.user,
        )
        self.client.login(username="user1", password="pass123")
        response = self.client.post(reverse("chat:join_room", args=[room2.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RoomMembership.objects.filter(room=room2, user=self.user).exists())

    def test_room_full_cannot_join(self):
        small_room = ChatRoom.objects.create(
            name="Small",
            max_capacity=1,
            created_by=self.user,
        )
        RoomMembership.objects.create(room=small_room, user=self.user)
        other = User.objects.create_user(username="other", email="o@x.com", password="p")
        self.client.login(username="other", password="p")
        response = self.client.post(reverse("chat:join_room", args=[small_room.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RoomMembership.objects.filter(room=small_room, user=other).exists())

    def test_member_can_send_message(self):
        self.client.login(username="user1", password="pass123")
        url = "/chat/api/rooms/{}/messages/send/".format(self.room.id)
        response = self.client.post(url, {"content": "Hello"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(Message.objects.filter(room=self.room).count(), 1)

    def test_non_member_cannot_send_message(self):
        other = User.objects.create_user(username="other", email="o@x.com", password="p")
        self.client.login(username="other", password="p")
        url = "/chat/api/rooms/{}/messages/send/".format(self.room.id)
        response = self.client.post(url, {"content": "Hello"})
        self.assertIn(response.status_code, [403, 400])
        self.assertEqual(Message.objects.filter(room=self.room).count(), 0)

    def test_send_message_api_returns_json(self):
        self.client.login(username="user1", password="pass123")
        response = self.client.post(
            "/chat/api/rooms/{}/messages/send/".format(self.room.id),
            {"content": "Test msg", "csrfmiddlewaretoken": "x"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("ok"))
        self.assertIn("data", data)
        self.assertIn("sender_name", data["data"])

    def test_unauthenticated_chat_api_fails(self):
        response = self.client.get("/chat/api/rooms/")
        self.assertEqual(response.status_code, 401)

    def test_room_count_stat_correct(self):
        self.client.login(username="user1", password="pass123")
        response = self.client.get("/chat/api/rooms/{}/stats/".format(self.room.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data["data"]["current_count"], 1)
        self.assertEqual(data["data"]["max_capacity"], 5)
