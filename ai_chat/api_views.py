# POST prompt (optional conversation_id) -> conversation_id, user_message, assistant_message. Same shape for legacy form/JS.
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from . import services


def _json_ok(data):
    out = {"ok": True}
    out.update(data)
    return JsonResponse(out)


def _json_error(msg, status=400):
    return JsonResponse({"ok": False, "error": msg}, status=status)


@require_POST
@login_required
def ai_send_api(request):
    # json or form body; handle_ai_chat does the rest
    try:
        if request.content_type and "application/json" in request.content_type:
            body = json.loads(request.body.decode("utf-8"))
            prompt = body.get("prompt", "").strip()
            conversation_id = body.get("conversation_id")
        else:
            prompt = (request.POST.get("prompt") or "").strip()
            cid = request.POST.get("conversation_id")
            conversation_id = int(cid) if cid else None
    except (ValueError, TypeError, KeyError):
        return _json_error("Invalid request body")

    if not prompt:
        return _json_error("Prompt is required")

    try:
        conversation, reply = services.handle_ai_chat(
            request.user,
            prompt,
            conversation_id=conversation_id,
        )
        return _json_ok({
            "conversation_id": conversation.id,
            "assistant_message": reply,
            "user_message": prompt,
        })
    except ValueError as e:
        return _json_error(str(e))
    except Exception as e:
        return _json_error("Something went wrong. Please try again.", status=500)
