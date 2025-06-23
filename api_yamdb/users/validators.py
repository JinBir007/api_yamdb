from re import sub

from django.core.exceptions import ValidationError

from .constants import FORBIDDEN_NAMES, FORBIDDEN_SYMBOLS


def validate_name(value):
    if value.lower() in FORBIDDEN_NAMES:
        raise ValidationError(f'Недопустимое имя пользователя {value}')
    incorrect_entries = sub(FORBIDDEN_SYMBOLS, '', value)
    if len(incorrect_entries) > 0:
        raise ValidationError(f'Недопустимые символы {incorrect_entries}')
    return value
