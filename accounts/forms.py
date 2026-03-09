from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    display_name = forms.CharField(max_length=50, required=False, label="Display name / Nickname")

    class Meta:
        model = User
        fields = ("username", "email", "display_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class GuestModeForm(forms.Form):
    nickname = forms.CharField(
        max_length=30,
        required=True,
        label="Your nickname",
        widget=forms.TextInput(attrs={"placeholder": "Enter a nickname to use in chat"}),
    )

    def clean_nickname(self):
        nickname = (self.cleaned_data.get("nickname") or "").strip()
        if not nickname:
            raise forms.ValidationError("Nickname cannot be empty.")
        if len(nickname) > 30:
            raise forms.ValidationError("Nickname must be at most 30 characters.")
        return nickname
