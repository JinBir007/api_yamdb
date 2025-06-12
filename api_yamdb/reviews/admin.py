from django.contrib import admin

from .models import Review, Comment


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    """Админка для модели Reviews"""
    list_display = ('text', 'score', 'pub_date')
    list_filter = ('score', 'pub_date')
    search_fields = ('text',)


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    """Админка для модели Comments"""
    list_display = ('text', 'review', 'pub_date')
    list_filter = ('review', 'pub_date')
    search_fields = ('text',)
