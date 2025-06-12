from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
)


v1_router = DefaultRouter()
v1_router.register(r'titles/(\d+)/reviews/', ReviewViewSet)
v1_router.register(r'titles/(\d+)/reviews/(\d+)/comments', CommentViewSet)
v1_router.register(r'categories/', CategoryViewSet)
v1_router.register(r'genres/', GenreViewSet)
v1_router.register(r'titles/', TitleViewSet)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]