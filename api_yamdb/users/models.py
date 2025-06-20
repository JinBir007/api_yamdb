from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_name
from .constants import MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH


class RoleChoices(models.TextChoices):
    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Админ'


class ApiUser(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=(validate_name,)
    )
    email = models.EmailField(max_length=MAX_EMAIL_LENGTH, unique=True)
    email_confirmed = models.BooleanField(default=False)
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.CharField(max_length=max(map(len, RoleChoices)),
                            choices=RoleChoices.choices,
                            default=RoleChoices.USER,
                            verbose_name='Роль')
    REQUIRED_FIELDS = ['email', ]

    class Meta:
        ordering = ('username',)
        default_related_name = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == RoleChoices.ADMIN

    @property
    def is_moderator(self):
        return self.role == RoleChoices.MODERATOR
