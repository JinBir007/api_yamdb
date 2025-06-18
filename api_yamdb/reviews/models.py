from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models

from content.models import Title

User = get_user_model()


class BaseModel(models.Model):
    """Базовая абстрактная модель отзывов и комментариев"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='%(class)s_titles',
        verbose_name='Отзывы')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
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
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title_id'),
                name='review_author')
        ]

    def __str__(self) -> str:
        return self.text[:50]


class Comment(BaseModel):
    """Комментарии"""
    review = models.ForeignKey(
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
