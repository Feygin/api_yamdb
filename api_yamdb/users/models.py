from django.contrib.auth.models import AbstractUser
from django.db import models

from .utils import generate_confirmation_code

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLES = (
    (USER, 'User'),
    (MODERATOR, 'Moderator'),
    (ADMIN, 'Admin'),
)


class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями.
    Роли: user, moderator, admin.
    Имеет поле для confirmation_code.
    """
    email = models.EmailField(unique=True, blank=False, null=False)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=ROLES, default=USER)
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)

    @property
    def is_admin(self):
        """Возвращает True, если пользователь — админ или суперпользователь."""
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Возвращает True, если пользователь — модератор."""
        return self.role == MODERATOR

    @property
    def is_user(self):
        """Возвращает True, если пользователь — обычный пользователь (user)."""
        return self.role == USER

    def set_new_confirmation_code(self):
        """Устанавливает новый код подтверждения и сохраняет пользователя."""
        self.confirmation_code = generate_confirmation_code()
        self.save(update_fields=['confirmation_code'])
