from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models

User = get_user_model()
# TODO: Добавить поле title


class Review(models.Model):
    """Отзывы"""
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Отзывы')
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
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
                fields=['author', 'title'],
                name='review_author')
        ]

    def __str__(self) -> str:
        return self.text[:50]


class Comment(models.Model):
    """Комментарии"""
    text = models.TextField(
        verbose_name='Текст комментария',
        related_name='comments')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:50]


class Rating(models.Model):
    """Рейтинг"""
    rating = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5)], verbose_name='Рейтинг')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
