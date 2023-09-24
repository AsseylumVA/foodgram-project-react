from rest_framework import permissions


class IsAuthenticatedOrReadOnlyNotMe(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'me':
            return False
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS):
            return True
        return obj == request.user or request.user.is_staff
