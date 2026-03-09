from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            display_name="Test User",
        )

    def test_register_success(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "display_name": "New User",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username_fails(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "testuser",
                "email": "other@example.com",
                "display_name": "Other",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("already exists", response.content.decode().lower() or "username")

    def test_register_duplicate_email_fails(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "otheruser",
                "email": "test@example.com",
                "display_name": "Other",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.content.decode().lower())

    def test_login_success(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_guest_mode_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:guest"),
            {"nickname": "GuestNick"},
        )
        self.assertEqual(response.status_code, 302)
        guest = User.objects.get(is_guest=True, display_name="GuestNick")
        self.assertTrue(guest.username.startswith("guest_"))

    def test_unauthenticated_redirect_to_login_for_protected(self):
        response = self.client.get(reverse("chat:lobby"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
