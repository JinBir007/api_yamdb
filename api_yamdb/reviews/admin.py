from django.contrib import admin

from .models import Category, Genre, Title, Review, Comment


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

    @admin.display(description='Genres')
    def genres_list(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка для модели Reviews."""

    list_display = ('text', 'score', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для модели Comments."""

    list_display = ('text', 'review_id', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text',)