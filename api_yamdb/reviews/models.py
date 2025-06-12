from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models

from content.models import Title

User = get_user_model()


class Review(models.Model):
    """Отзывы"""
    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Отзывы')
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Отзывы')
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(10)], verbose_name='Оценка')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title_id'],
                name='review_author')
        ]

    def __str__(self) -> str:
        return self.text[:50]


class Comment(models.Model):
    """Комментарии"""
    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарии')
    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Комментарии')
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:50]
