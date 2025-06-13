from django.db import models


    class Category(models.Model):
        """Категория."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

        def __str__(self):
            return self.name


class Genre(models.Model):
    """Жанр."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведение."""

    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles'
    )

    def __str__(self):
        return self.name
