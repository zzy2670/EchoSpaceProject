"""
AI chat business logic. Supports mock (default) and OpenAI.
"""
from django.conf import settings
from .models import AIConversation, AIMessage

# Mock responses for emotional support when no API key
MOCK_RESPONSES = [
    "Thank you for sharing that. It sounds like you're carrying a lot right now. Remember, it's okay to take things one step at a time.",
    "I hear you. What you're feeling is valid. Sometimes just naming our feelings can help us feel a little lighter.",
    "It takes courage to open up. Whatever you're going through, you don't have to face it alone.",
    "That sounds really tough. Be gentle with yourself today.",
    "Thanks for trusting me with this. Would it help to talk more about what's on your mind?",
]


def _mock_reply(prompt):
    """Return a stable mock reply based on prompt (for tests) or random."""
    import hashlib
    idx = int(hashlib.md5((prompt or "").encode()).hexdigest(), 16) % len(MOCK_RESPONSES)
    return MOCK_RESPONSES[idx]


def _openai_reply(prompt):
    """Call OpenAI API if key is set. On any failure, return None to fall back to mock."""
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        return None
    try:
        import openai
        openai.api_key = api_key
        model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
        client = getattr(openai, "OpenAI", None)
        if client:
            c = client(api_key=api_key)
            r = c.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt[:2000]}],
                max_tokens=300,
            )
            if r.choices:
                return (r.choices[0].message.content or "").strip()
        return None
    except Exception:
        return None


def generate_ai_reply(prompt):
    """Generate AI reply. Uses OpenAI if configured, else mock."""
    prompt = (prompt or "").strip()
    if not prompt:
        return "Please share what's on your mind."
    provider = getattr(settings, "AI_PROVIDER", "mock").lower()
    if provider == "openai":
        reply = _openai_reply(prompt)
        if reply:
            return reply
    return _mock_reply(prompt)


def create_or_get_conversation(user, conversation_id=None, first_prompt=None):
    if conversation_id:
        conv = AIConversation.objects.filter(user=user, id=conversation_id).first()
        if conv:
            return conv
    conv = AIConversation.objects.create(user=user)
    if first_prompt:
        title = (first_prompt[:60] + "..." if len(first_prompt) > 60 else first_prompt).strip()
        conv.title = title
        conv.save(update_fields=["title"])
    return conv


def save_user_message(conversation, content):
    return AIMessage.objects.create(conversation=conversation, role="user", content=content[:2000])


def save_assistant_message(conversation, content):
    return AIMessage.objects.create(conversation=conversation, role="assistant", content=content[:2000])


def handle_ai_chat(user, prompt, conversation_id=None):
    """
    Process one user message: create/get conversation, save user message,
    generate reply, save assistant message. Returns (conversation, user_msg, assistant_content).
    On error raises or returns (None, None, error_message).
    """
    prompt = (prompt or "").strip()
    if not prompt:
        raise ValueError("Prompt cannot be empty.")
    if len(prompt) > 2000:
        raise ValueError("Message is too long.")
    conversation = create_or_get_conversation(user, conversation_id=conversation_id, first_prompt=prompt)
    save_user_message(conversation, prompt)
    try:
        reply = generate_ai_reply(prompt)
    except Exception as e:
        reply = "I'm sorry, I couldn't process that right now. Please try again in a moment."
    save_assistant_message(conversation, reply)
    conversation.save(update_fields=["updated_at"])
    return conversation, reply
