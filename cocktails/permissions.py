from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):


    # Everyone can get records.
    # Only author or admin can edit/delete records.
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and (request.user.is_staff or obj.author == request.user)