"""
Custom DRF Authentication Class for app_token (JWT) from cookies and headers.
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

from .jwt_auth import verify_app_token

User = get_user_model()


class AppTokenAuthentication(BaseAuthentication):
    """
    Authenticate using app_token JWT from cookie or X-App-Token header.
    
    Priority:
    1. X-App-Token header (for Next.js Route Handlers)
    2. app_token cookie (for direct browser requests)
    """
    
    def authenticate(self, request):
        # Try to get token from header first (Next.js Route Handlers)
        token = request.META.get('HTTP_X_APP_TOKEN')
        
        # Fallback to cookie
        if not token:
            token = request.COOKIES.get('app_token')
        
        # If no token found, let other authentication methods handle it
        if not token:
            return None
        
        # Verify the token
        payload = verify_app_token(token)
        if not payload:
            raise AuthenticationFailed('Invalid or expired token.')
        
        # Get user from database
        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')
        
        # Return tuple of (user, auth_token)
        return (user, token)
