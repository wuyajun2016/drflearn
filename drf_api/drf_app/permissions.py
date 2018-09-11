from rest_framework import permissions


# 在view中调用自定义的权限：permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly)
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user



