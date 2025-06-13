"""users/exceptions.py

Исключения для приложения users.
"""

from rest_framework import status
from rest_framework.exceptions import ValidationError


class WrongUsernameOrCode(ValidationError):
    """Пользователь прислал некорректные данные для получения токена."""

    status_code = status.HTTP_400_BAD_REQUEST


class WrongEmail(ValidationError):
    """Пользователь прислал некорректный адрес электронной почты."""

    status_code = status.HTTP_400_BAD_REQUEST
