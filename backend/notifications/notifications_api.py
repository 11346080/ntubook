"""
通知管理 API 端點 (完整實現)
Notification Management API Endpoints (Complete Implementation)
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from notifications.models import Notification
from notifications.serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_list_api(request):
    """
    獲取通知列表 / Get notifications list
    
    Query Parameters:
    - page: 分頁頁碼 (可選)
    - limit: 每頁筆數，預設 20，最大 100 (可選)
    - unread_only: 只顯示未讀通知 (可選)
    - type_filter: 按類型篩選 (可選)
    """
    try:
        # 獲取查詢參數
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 20)), 100)
        unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
        type_filter = request.query_params.get('type_filter', '')
        
        # 基礎查詢
        queryset = Notification.objects.filter(user=request.user).order_by('-created_at')
        
        # 篩選未讀
        if unread_only:
            queryset = queryset.filter(is_read=False)
        
        # 篩選類型
        if type_filter:
            queryset = queryset.filter(type_code=type_filter)
        
        # 計算分頁
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        
        notifications = queryset[start:end]
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({
            'success': True,
            'data': {
                'notifications': serializer.data,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_unread_count_api(request):
    """
    獲取未讀通知數量 / Get unread notifications count
    """
    try:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'unread_count': unread_count
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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def notification_read_api(request, notification_id):
    """
    標記單個通知為已讀 / Mark single notification as read
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # 檢查權限
        if notification.user_id != request.user.id:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '您無權修改此通知'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 更新狀態
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])
        
        serializer = NotificationSerializer(notification)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '通知不存在'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def notifications_read_all_api(request):
    """
    標記所有通知為已讀 / Mark all notifications as read
    
    Optional Request Body:
    - type_filter: 只標記某類型通知為已讀 (可選)
    """
    try:
        queryset = Notification.objects.filter(
            user=request.user,
            is_read=False
        )
        
        # 可選的類型篩選
        type_filter = request.data.get('type_filter', '')
        if type_filter:
            queryset = queryset.filter(type_code=type_filter)
        
        # 更新所有
        affected_count = queryset.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'success': True,
            'data': {
                'affected_count': affected_count
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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def notification_delete_api(request, notification_id):
    """
    刪除單個通知 / Delete single notification
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # 檢查權限
        if notification.user_id != request.user.id:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '您無權刪除此通知'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        notification.delete()
        
        return Response({
            'success': True,
            'data': {
                'message': '通知已刪除'
            }
        })
    
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '通知不存在'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def notifications_delete_all_api(request):
    """
    刪除所有通知 / Delete all notifications
    
    Optional Request Body:
    - type_filter: 只刪除某類型通知 (可選)
    """
    try:
        queryset = Notification.objects.filter(user=request.user)
        
        # 可選的類型篩選
        type_filter = request.data.get('type_filter', '')
        if type_filter:
            queryset = queryset.filter(type_code=type_filter)
        
        # 刪除所有
        affected_count, _ = queryset.delete()
        
        return Response({
            'success': True,
            'data': {
                'affected_count': affected_count
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
