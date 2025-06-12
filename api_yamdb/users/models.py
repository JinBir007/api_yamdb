"""users/models.py

Описание моделей данных для приложения users.
"""

from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Админ'),
)


class ApiUser(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(unique=True, blank=False, null=False)
    email_confirmed = models.BooleanField(default=False)
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.CharField(max_length=12,
                            choices=CHOICES,
                            default='user',
                            verbose_name='Роль')
    REQUIRED_FIELDS = ['email',]

    class Meta:
        ordering = ('username',)
        default_related_name = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class EmailConfirmation(models.Model):
    """Модель кода подтверждения электронной почты."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE)
