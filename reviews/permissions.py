from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Разрешение для автора или чтение для авторизованных."""

    def has_object_permission(self, request, view, obj):
        """Доступ для автора объекта."""
        return request.method in SAFE_METHODS or obj.author == request.user
