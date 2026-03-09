from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="pass",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="pass",
        )

    def test_staff_can_access_dashboard(self):
        self.client.login(username="staff", password="pass")
        response = self.client.get(reverse("dashboard:dashboard_home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_users", response.context)
        self.assertIn("room_count", response.context)

    def test_ordinary_user_cannot_access_dashboard(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("dashboard:dashboard_home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
