"""users/admin.py

Настройка модуля администрирования для приложения users.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ApiUser

admin.site.empty_value_display = 'Не задано'
UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio','role')}),
)
UserAdmin.list_display += ('role',)
admin.site.register(ApiUser, UserAdmin)
