from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if (request.user.is_admin
               or obj.author == request.user):
                return True
        return request.method in permissions.SAFE_METHODS
