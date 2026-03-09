from django import forms
from .models import ChatRoom


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ("name", "description", "max_capacity")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Room name", "maxlength": 100}),
            "description": forms.Textarea(attrs={"placeholder": "Short description (optional)", "rows": 2, "maxlength": 255}),
            "max_capacity": forms.NumberInput(attrs={"min": 2, "max": 100}),
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Room name is required.")
        if ChatRoom.objects.filter(name=name).exists():
            raise forms.ValidationError("A room with this name already exists.")
        return name

    def clean_max_capacity(self):
        val = self.cleaned_data.get("max_capacity")
        if val is not None and (val < 2 or val > 100):
            raise forms.ValidationError("Capacity must be between 2 and 100.")
        return val or 20
