import json
import os
import google.generativeai as genai
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, get_object_or_404

from .models import AIConversation, AIMessage

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@login_required
def ai_chat_view(request, conversation_id=None):
    conversation = None
    if conversation_id:
        conversation = get_object_or_404(
            AIConversation,
            id=conversation_id,
            user=request.user,
        )
    conversations = AIConversation.objects.filter(user=request.user).order_by("-updated_at")[:20]
    
    return render(
        request,
        "ai_chat/ai_chat.html",
        {
            "conversation": conversation,
            "conversations": conversations,
        },
    )

@login_required
def api_ask_ai(request):
    if request.method == "POST":
        try:
            if not GEMINI_API_KEY:
                return JsonResponse({"reply": "System Error: Gemini API Key is missing in .env!"})

            data = json.loads(request.body)
            user_message = data.get("message", "")
            conv_id = data.get("conversation_id")
            
            if not user_message:
                return JsonResponse({"reply": "I didn't hear anything. Could you say that again?"})


            if conv_id:
                conv = AIConversation.objects.filter(id=conv_id, user=request.user).first()
                if conv:
                    conv.save() 
            else:
                title = user_message[:20] + "..." if len(user_message) > 20 else user_message
                conv = AIConversation.objects.create(user=request.user, title=title)

            if not conv:
                return JsonResponse({"error": "Conversation not found"}, status=404)


            AIMessage.objects.create(conversation=conv, role="user", content=user_message)


            model = genai.GenerativeModel('gemini-2.5-flash')
            system_prompt = f"""
            You are an empathetic, gentle, and non-judgmental emotional supporter in an anonymous chat app called EchoSpace.
            Your goal is to provide a safe space for users to vent their stress.
            Rules:
            1. Keep your responses conversational, warm, and concise.
            2. Always validate the user's feelings first.
            
            The user says: "{user_message}"
            
            EchoBot's response:
            """
            response = model.generate_content(system_prompt)
            reply_text = response.text


            AIMessage.objects.create(conversation=conv, role="assistant", content=reply_text)
            
            return JsonResponse({
                "reply": reply_text,
                "conversation_id": conv.id
            })
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return JsonResponse({"reply": "Network Error, please try again"})
            
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def delete_conversation(request, conversation_id):
    if request.method == "POST":
        conv = get_object_or_404(AIConversation, id=conversation_id, user=request.user)
        conv.delete()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Invalid request"}, status=400)