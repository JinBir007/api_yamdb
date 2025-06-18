from django.contrib import admin

from .models import Review, Comment


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
