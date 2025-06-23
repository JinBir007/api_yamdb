from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)


class IsAuthorOrModeratorOrAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение уровня user/moderator."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                and (obj.author == request.user
                     or request.user.is_moderator
                     or request.user.is_admin))


class IsAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение уровня admin."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False


class OnlyAdminHasAccess(IsAuthenticatedOrReadOnly):
    """Разрешение уровня admin даже на чтение."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_admin
        return False
