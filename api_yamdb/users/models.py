from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLES = (
    (USER, 'User'),
    (MODERATOR, 'Moderator'),
    (ADMIN, 'Admin'),
)


def generate_confirmation_code():
    """Генерация случайного 6-значного кода."""
    return ''.join(random.choices(string.digits, k=6))


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=ROLES, default=USER)
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER
