from django.http import JsonResponse
from django.shortcuts import render


def home_view(request):
    return render(request, "main/home.html")


def health_view(request):
    return JsonResponse({"status": "ok", "service": "EchoSpace"})
