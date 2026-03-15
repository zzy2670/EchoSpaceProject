import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import AIConversation

User = get_user_model()

class AIChatTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        
    def test_ai_chat_page_renders_native_ui(self):
        """Test that the AI chat page loads correctly with the new native UI (no AppFlow)."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('ai_chat:ai_chat'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ai_chat/ai_chat.html')
        # Ensure it passes the conversations history to the context
        self.assertIn('conversations', response.context)

    def test_api_ask_ai_requires_login(self):
        """Ensure the new Gemini API endpoint is protected."""
        response = self.client.post(
            reverse('ai_chat:api_ask_ai'), 
            json.dumps({'message': 'hello'}), 
            content_type='application/json'
        )
        # Should redirect to login page (302)
        self.assertEqual(response.status_code, 302)

    def test_api_ask_ai_returns_valid_json(self):
        """Test that the API correctly handles a request and returns a JSON response."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            reverse('ai_chat:api_ask_ai'), 
            json.dumps({'message': 'I am feeling stressed.'}), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # Should contain a 'reply' or 'error' key
        self.assertTrue('reply' in response_data or 'error' in response_data)

    def test_conversation_deletion(self):
        """Test the AJAX history deletion endpoint functions correctly."""
        self.client.login(username='testuser', password='testpassword')
        # Create a dummy conversation
        conv = AIConversation.objects.create(user=self.user, title="Test Chat")
        
        response = self.client.post(reverse('ai_chat:delete_conversation', args=[conv.id]))
        self.assertEqual(response.status_code, 200)
        # Verify it was deleted from DB
        self.assertFalse(AIConversation.objects.filter(id=conv.id).exists())