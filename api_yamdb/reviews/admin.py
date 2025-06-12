from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Review, Comment, ApiUser

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio','role')}),
)
UserAdmin.list_display += ('role',)
admin.site.register(ApiUser, UserAdmin)


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
