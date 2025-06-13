"""api/permissions.py

Permissions для приложения api.
"""

from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)


class IsUserOrModeratorOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение уровня user/moderator."""

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if request.user.role == 'admin' or request.user.is_superuser:
                return True
            if request.user.role == 'user' and hasattr(obj, 'author'):
                return (request.method in SAFE_METHODS
                        or obj.author == request.user)
            if request.user.role == 'user':
                return request.method in SAFE_METHODS
            if request.user.role == 'moderator' and hasattr(obj, 'author'):
                return True
            if request.user.role == 'moderator':
                return request.method in SAFE_METHODS
        else:
            return request.method in SAFE_METHODS


class IsAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение уровня admin."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user and request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        return False


class OnlyAdminHasAccess(IsAuthenticatedOrReadOnly):
    """Разрешение уровня admin даже на чтение."""

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        return False
