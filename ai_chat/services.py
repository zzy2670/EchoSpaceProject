# Reply generation , conversation create/save. session_id stored on AIConversation for dashscope multi-turn.
from django.conf import settings
from .models import AIConversation, AIMessage

MOCK_RESPONSES = [
    "Thank you for sharing that. It sounds like you're carrying a lot right now. Remember, it's okay to take things one step at a time.",
    "I hear you. What you're feeling is valid. Sometimes just naming our feelings can help us feel a little lighter.",
    "It takes courage to open up. Whatever you're going through, you don't have to face it alone.",
    "That sounds really tough. Be gentle with yourself today.",
    "Thanks for trusting me with this. Would it help to talk more about what's on your mind?",
]


def _mock_reply(prompt):
    # hash so tests get stable reply; leave as-is
    import hashlib
    idx = int(hashlib.md5((prompt or "").encode()).hexdigest(), 16) % len(MOCK_RESPONSES)
    return MOCK_RESPONSES[idx]


def _openai_reply(prompt):
    # None => caller falls back to mock
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


def _dashscope_reply(prompt, session_id=None):
    # returns (text, new_sid) or (None, None)
    api_key = getattr(settings, "DASHSCOPE_API_KEY", "") or None
    app_id = getattr(settings, "DASHSCOPE_APP_ID", "") or None
    if not api_key or not app_id:
        return None, None
    try:
        from http import HTTPStatus
        from dashscope import Application

        kwargs = {
            "api_key": api_key,
            "app_id": app_id,
            "prompt": prompt[:2000],
        }
        if session_id:
            kwargs["session_id"] = session_id

        response = Application.call(**kwargs)
        if response.status_code != HTTPStatus.OK:
            return None, None
        text = getattr(response.output, "text", None)
        new_sid = getattr(response.output, "session_id", None) or None
        if not text:
            return None, new_sid
        return str(text).strip(), new_sid
    except Exception:
        return None, None


def generate_ai_reply(prompt, conversation=None):
    # provider from settings; conversation only used to pass dashscope session_id
    prompt = (prompt or "").strip()
    if not prompt:
        return "Please share what's on your mind.", None
    provider = getattr(settings, "AI_PROVIDER", "mock").lower()
    if provider == "openai":
        reply = _openai_reply(prompt)
        if reply:
            return reply, None
    elif provider in ("dashscope", "bailian", "aliyun"):
        sid = None
        if conversation:
            sid = (getattr(conversation, "dashscope_session_id", None) or "").strip() or None
        reply, new_sid = _dashscope_reply(prompt, session_id=sid)
        if reply:
            return reply, new_sid
    return _mock_reply(prompt), None


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
    # one turn: conv, user msg, reply (and sid when dashscope), assistant msg. Return (conv, reply)
    prompt = (prompt or "").strip()
    if not prompt:
        raise ValueError("Prompt cannot be empty.")
    if len(prompt) > 2000:
        raise ValueError("Message is too long.")
    conversation = create_or_get_conversation(user, conversation_id=conversation_id, first_prompt=prompt)
    save_user_message(conversation, prompt)
    try:
        reply, session_id_to_save = generate_ai_reply(prompt, conversation=conversation)
    except Exception:
        reply = "I'm sorry, I couldn't process that right now. Please try again in a moment."
        session_id_to_save = None
    save_assistant_message(conversation, reply)
    update_fields = ["updated_at"]
    if session_id_to_save:
        conversation.dashscope_session_id = session_id_to_save
        update_fields.append("dashscope_session_id")
    conversation.save(update_fields=update_fields)
    # print('sid saved', conversation.dashscope_session_id[:16] if conversation.dashscope_session_id else None)
    return conversation, reply
