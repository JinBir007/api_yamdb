from django.contrib import admin

from models import Review, Comment, Rating


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    """Админка для модели Reviews"""
    list_display = ('title', 'author', 'pub_date')
    list_filter = ('author', 'pub_date')
    search_fields = ('title', 'author')
    ordering = ('pub_date',)


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    """Админка для модели Comments"""
    list_display = ('text', 'author', 'pub_date')
    list_filter = ('author', 'pub_date')
    search_fields = ('text', 'author')
    ordering = ('pub_date',)


@admin.register(Rating)
class RatingsAdmin(admin.ModelAdmin):
    """Админка для модели Ratings"""
    list_display = ('rating', 'author', 'pub_date')
    list_filter = ('author', 'pub_date')
    search_fields = ('rating', 'author')
    ordering = ('pub_date',)
