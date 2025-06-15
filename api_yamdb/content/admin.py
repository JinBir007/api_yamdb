from django.contrib import admin

from .models import Category, Genre, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для модели Category."""

    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Админка для модели Genre."""

    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Админка для модели Title."""

    list_display = ('name', 'year', 'description', 'genres_list', 'category')
    list_filter = ('year',)
    search_fields = ('name',)

    def genres_list(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    genres_list.short_description = 'Genres'
