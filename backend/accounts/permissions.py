from rest_framework import permissions


class IsOwnProfile(permissions.BasePermission):
    """
    Allow users to access/edit only their own profile.
    Admins can access any profile.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any profile
        if request.user and request.user.is_staff:
            return True
        
        # User can only access their own profile
        return obj.user == request.user
