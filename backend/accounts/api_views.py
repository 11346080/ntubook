"""
用戶認證與個人資料 API 端點
Authentication & Profile Management API Endpoints
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import UserProfile
from .serializers import UserProfileSerializer

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_api(request):
    """
    獲取當前登入用戶的基本信息
    Get current logged-in user's basic information
    """
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user) if hasattr(user, 'profile') else None
        
        return Response({
            'success': True,
            'data': {
                'user_id': user.id,
                'email': user.email,
                'username': user.username,
                'has_profile': profile is not None,
                'account_status': getattr(profile, 'account_status', 'ACTIVE') if profile else 'ACTIVE',
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """
    獲取或更新用戶個人資料 / Get or Update user profile
    需要登入 / Requires authentication
    """
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '用戶資料不存在'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    elif request.method == 'PATCH':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'data': serializer.data
            })
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_profile_api(request):
    """
    首次登入時建立用戶資料 / Create user profile on first login
    """
    # 檢查是否已有 profile
    if UserProfile.objects.filter(user=request.user).exists():
        return Response({
            'success': False,
            'error': {
                'code': 'ALREADY_EXISTS',
                'message': '用戶資料已存在'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)
