from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    display_name = models.CharField(max_length=50, blank=True)
    is_guest = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.public_name

    @property
    def public_name(self):
        if self.display_name and self.display_name.strip():
            return self.display_name.strip()
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
