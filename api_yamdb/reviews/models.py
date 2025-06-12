from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models

from content.models import Title

User = get_user_model()

CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Админ'),
)


class ApiUser(AbstractUser):
    """Пользователь."""

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
    """Код подтверждения почты."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE)


class BaseModel(models.Model):
    """Базовая абстрактная модель отзывов и комментариев"""
    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Отзывы')
    text = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации')

    class Meta:
        abstract = True


class Review(BaseModel):
    """Отзывы"""
    score = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(10)], verbose_name='Оценка')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        validators = [
            models.UniqueConstraint(
                fields=['author', 'title_id'],
                name='review_author')
        ]

    def __str__(self) -> str:
        return self.text[:50]


class Comment(BaseModel):
    """Комментарии"""
    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарии')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:50]
