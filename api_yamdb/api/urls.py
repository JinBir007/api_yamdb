from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import ReviewViewSet, CommentViewSet


v1_router = DefaultRouter()
v1_router.register(r'titles/(\d+)/reviews/', ReviewViewSet)
v1_router.register(r'titles/(\d+)/reviews/(\d+)/comments', CommentViewSet)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
