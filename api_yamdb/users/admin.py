from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

admin.site.empty_value_display = 'Не задано'
UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio', 'role')}),
)
UserAdmin.list_display += ('role',)
admin.site.register(User, UserAdmin)
