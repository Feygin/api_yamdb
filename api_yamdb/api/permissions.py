from rest_framework import permissions


class IsAuthorAdminModerOrReadOnly(permissions.BasePermission):
    """
    Права доступа, позволяющие пользователю выполнять действия с объектом.

    Разрешения:
        - Для анонимных пользователей: доступ только к безопасным методам.
        - Для аутентифицированных пользователей: доступ к безопасным методам,
          а также право редактировать или удалять свои объекты.
        - Для авторов объекта: могут редактировать и удалять свои объекты.
        - Для модераторов и администраторов:
          имеют право редактировать и удалять любые объекты.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Для небозопасных методов доступ предоставляется
    только админу.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsAdmin(permissions.BasePermission):
    """Проверка: доступ разрешён только аутентифицированному администратору."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
