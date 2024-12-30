from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Проверка: доступ разрешён только аутентифицированному администратору."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
