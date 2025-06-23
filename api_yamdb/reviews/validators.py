import datetime

from django.core.exceptions import ValidationError


def current_year():
    """Возвращает текущий год."""
    return datetime.datetime.now().year


def validate_year(value):
    """Валидатор для проверки года."""
    if value > current_year():
        raise ValidationError(
            'Год не может быть больше текущего.'
        )
