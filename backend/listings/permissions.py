from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow listing owners to edit their own listings.
    Others can only read.
    Admins have full access.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any listing
        if request.user and request.user.is_staff:
            return True
        
        # Read permissions allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to listing owner
        return obj.seller == request.user


class IsListingOwner(permissions.BasePermission):
    """
    Allow only listing owners to delete/edit their listings.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any listing
        if request.user and request.user.is_staff:
            return True
        
        # Owner can edit/delete their own listing
        return obj.seller == request.user
