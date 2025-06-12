"""api/exceptions.py

Исключения.
"""

from rest_framework import status
from rest_framework.exceptions import ValidationError


class WrongUsernameOrToken(ValidationError):
    """Пользователь прислал некорректные данные для получения токена."""

    status_code = status.HTTP_400_BAD_REQUEST
