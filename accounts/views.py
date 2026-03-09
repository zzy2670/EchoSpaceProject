import uuid
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm, LoginForm, GuestModeForm

User = get_user_model()


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("chat:lobby")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to EchoSpace!")
            return redirect("chat:lobby")
        messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("chat:lobby")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Welcome back!")
                return redirect("chat:lobby")
            form.add_error(None, "Invalid username or password.")
        messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("main:home")


@require_http_methods(["GET", "POST"])
def guest_mode_view(request):
    if request.user.is_authenticated and not request.user.is_guest:
        return redirect("chat:lobby")
    if request.method == "POST":
        form = GuestModeForm(request.POST)
        if form.is_valid():
            nickname = form.cleaned_data["nickname"].strip()
            username = f"guest_{uuid.uuid4().hex[:12]}"
            email = f"{username}@guest.echospace.local"
            user = User.objects.create_user(
                username=username,
                email=email,
                display_name=nickname,
                is_guest=True,
                password=None,
            )
            user.set_unusable_password()
            user.save()
            login(request, user)
            messages.success(request, "Welcome as a guest. You can join rooms and use AI chat.")
            return redirect("chat:lobby")
        messages.error(request, "Please enter a valid nickname.")
    else:
        form = GuestModeForm()
    return render(request, "accounts/guest_mode.html", {"form": form})
