from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from .permissions import IsAdminOrReadOnly


class BaseViewSet(CreateModelMixin,
                  ListModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    """Базовый ViewSet для моделей с полями name и slug."""

    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering = ['name']
    lookup_field = 'slug'
