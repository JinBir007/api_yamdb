"""users/urls.py

Эндпойнты для приложения users.
"""

from rest_framework.routers import SimpleRouter
from django.urls import include, path

from .views import RegistrationConfirmation, UserRegistrationViewSet

app_name = 'users'

auth_router = SimpleRouter()
auth_router.register('auth/signup', UserRegistrationViewSet, basename='signup')

extra_patterns = [
    path('auth/token/', RegistrationConfirmation.as_view(), name='token'),
] + auth_router.urls

urlpatterns = [
    path('v1/', include(extra_patterns)),
]



# /auth/signup/ - Получение confirmation code по имени и почте
# Должна быть возможность повторного запроса кода подтверждения.

# /auth/token/ - Получение JWT-токена в обмен на username и confirmation code

# /users/me/ - PATCH-запрос на заполнение полей в профиле, GET - на получение данных о себе. Любой авторизованный пользователь
# /users/ - GET на получение списка всех пользователей. Администратор.
# POST - Добавить нового пользователя. Права доступа: Администратор Поля email и username должны быть уникальными.

# /users/{username}/ - GET, POST, PATCH только для админа

# {
#   "username": "zr8VRG.0DB061iHkAroEZahED3JgR-mO-SF71jJHe36iVrCg0K@1j3ZoKAcqlHZ",
#   "email": "user@example.com",
#   "first_name": "string",
#   "last_name": "string",
#   "bio": "string",
#   "role": "user"
# }