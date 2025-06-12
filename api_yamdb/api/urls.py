from django.urls import include, path

from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    RegistrationConfirmation,
    ReviewViewSet,
    TitleViewSet,
    UserRegistrationViewSet,
)


v1_router = DefaultRouter()
v1_router.register(r'titles/(\d+)/reviews/', ReviewViewSet)
v1_router.register(r'titles/(\d+)/reviews/(\d+)/comments', CommentViewSet)
v1_router.register(r'categories/', CategoryViewSet)
v1_router.register(r'genres/', GenreViewSet)
v1_router.register(r'titles/', TitleViewSet)

auth_v1_router = SimpleRouter()
auth_v1_router.register('auth/signup',
                        UserRegistrationViewSet,
                        basename='signup')
auth_patterns = [
    path('auth/token/', RegistrationConfirmation.as_view(), name='token'),
] + auth_v1_router.urls

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/', include(auth_patterns)),
]
