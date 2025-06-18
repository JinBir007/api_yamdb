from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    ReviewViewSet, CommentViewSet, UserRegistrationViewSet, UserViewSet,
    RegistrationConfirmation, UsersMeViewSet, CategoryViewSet, GenreViewSet,
    TitleViewSet)

v1_router = DefaultRouter()
v1_router.register(r'categories', CategoryViewSet, basename='category')
v1_router.register(r'genres', GenreViewSet, basename='genres')
v1_router.register(r'titles', TitleViewSet, basename='titles')
v1_router.register(r'titles/(\d+)/reviews/', ReviewViewSet)
v1_router.register(r'titles/(\d+)/reviews/(\d+)/comments', CommentViewSet)
v1_router.register(r'auth/signup',
                   UserRegistrationViewSet,
                   basename='auth_signup')
v1_router.register(r'users', UserViewSet)

urlpatterns = [
    path(r'v1/users/me/', UsersMeViewSet.as_view(
        {'get': 'retrieve', 'patch': 'partial_update'}),
        name='auth_tokusers_meen'),
    path(r'v1/', include(v1_router.urls)),
    path(r'v1/auth/token/',
         RegistrationConfirmation.as_view(), name='auth_token'),
]
