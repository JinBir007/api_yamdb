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
