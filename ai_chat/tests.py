import json
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import AIConversation, AIMessage
from . import services

User = get_user_model()


class AIChatTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass123",
        )

    def test_ai_page_requires_login(self):
        response = self.client.get(reverse("ai_chat:ai_chat"))
        self.assertEqual(response.status_code, 302)

    def test_ai_page_opens_when_logged_in(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("ai_chat:ai_chat"))
        self.assertEqual(response.status_code, 200)

    @override_settings(APPFLOW_AI_CHAT_ENABLED=True, APPFLOW_AI_CHAT_URL="https://example.com/appflow")
    def test_ai_page_renders_iframe_when_appflow_enabled(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("ai_chat:ai_chat"))
      # The view should expose the AppFlow config to the template
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["appflow_enabled"])
        self.assertEqual(response.context["appflow_url"], "https://example.com/appflow")

    @override_settings(APPFLOW_AI_CHAT_ENABLED=False, APPFLOW_AI_CHAT_URL="")
    def test_ai_page_no_appflow_config_ok(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("ai_chat:ai_chat"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["appflow_enabled"])
        self.assertEqual(response.context["appflow_url"], "")

    def test_send_prompt_creates_conv_and_messages(self):
        self.client.login(username="testuser", password="pass123")
        with patch.object(services, "generate_ai_reply", return_value=("Mock reply here", None)):
            response = self.client.post(
                "/ai/api/send/",
                json.dumps({"prompt": "Hello"}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("ok"))
        self.assertIn("assistant_message", data)
        self.assertEqual(AIConversation.objects.filter(user=self.user).count(), 1)
        self.assertEqual(AIMessage.objects.filter(conversation__user=self.user).count(), 2)

    def test_api_returns_assistant_message(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.post(
            "/ai/api/send/",
            {"prompt": "I feel sad", "csrfmiddlewaretoken": "x"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("ok"))
        self.assertIn("assistant_message", data)
        self.assertTrue(len(data["assistant_message"]) > 0)

    def test_mock_provider_works_without_key(self):
        reply, _ = services.generate_ai_reply("Hello")
        self.assertTrue(isinstance(reply, str))
        self.assertTrue(len(reply) > 0)

    def test_service_exception_returns_error_json(self):
        self.client.login(username="testuser", password="pass123")

        def raise_err(*args, **kwargs):
            raise RuntimeError("Simulated failure")

        with patch.object(services, "handle_ai_chat", side_effect=raise_err):
            response = self.client.post(
                "/ai/api/send/",
                json.dumps({"prompt": "Hi"}),
                content_type="application/json",
            )
        self.assertIn(response.status_code, [400, 500])
        data = response.json()
        self.assertFalse(data.get("ok"))
        self.assertIn("error", data)
        # print(data)  # debug 500 vs 400
