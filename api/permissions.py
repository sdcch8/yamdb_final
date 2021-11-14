from rest_framework import permissions
from users.models import User


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user.is_authenticated):
            return (request.user.role == User.ADMIN
                    or request.user.is_superuser is True)
        return False


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if (request.user.is_authenticated):
            return (request.user.role == User.ADMIN
                    or request.user.is_superuser is True)


class IsOwnerOrAdminOrModeratorOrReadOnly(
        permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS
                or request.user.role == User.ADMIN
                or (request.method in ['GET', 'DELETE']
                    and request.user.role == User.MODERATOR))
