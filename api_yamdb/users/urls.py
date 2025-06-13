"""users/urls.py

Эндпойнты для приложения users.
"""

from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import include, path

from .views import (RegistrationConfirmation,
                    UsersMeViewSet,
                    UserRegistrationViewSet,
                    UserViewSet)

app_name = 'users'

auth_router = SimpleRouter()
auth_router.register('auth/signup',
                     UserRegistrationViewSet,
                     basename='auth_signup')
user_router = DefaultRouter()
user_router.register('users', UserViewSet)

extra_patterns = auth_router.urls + [
    path('auth/token/', RegistrationConfirmation.as_view(), name='auth_token'),
    path('users/me/', UsersMeViewSet.as_view(
        {'get': 'retrieve', 'patch': 'partial_update'}),
        name='auth_tokusers_meen'),
] + user_router.urls

urlpatterns = [
    path('v1/', include(extra_patterns)),
]
