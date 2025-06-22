import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models

from .constants import MAX_LENGTH_NAME, MAX_LENGTH_SLUG
from .validators import validate_year

User = get_user_model()


class NamedSlugModel(models.Model):
    """Абстрактная модель с полями name и slug."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(NamedSlugModel):
    """Категория."""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NamedSlugModel):
    """Жанр."""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Произведение."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название'
    )
    year = models.SmallIntegerField(
        verbose_name='Год',
        validators=[validate_year]
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанры'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class BaseModel(models.Model):
    """Базовая абстрактная модель отзывов и комментариев."""

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
    """Отзывы."""

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
    """Комментарии."""

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
