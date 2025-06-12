from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import path, include

from .views import (ReviewViewSet,
                    CommentViewSet,
                    RegistrationConfirmation,
                    UserRegistrationViewSet)


v1_router = DefaultRouter()
v1_router.register(r'titles/(\d+)/reviews/', ReviewViewSet)
v1_router.register(r'titles/(\d+)/reviews/(\d+)/comments', CommentViewSet)

auth_v1_router = SimpleRouter()
auth_v1_router.register('auth/signup',
                        UserRegistrationViewSet,
                        basename='signup')
auth_patterns = [
    path('auth/token/', RegistrationConfirmation.as_view(), name='token'),
] + auth_v1_router.urls

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
