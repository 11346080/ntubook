"""
舉報管理 API 端點 (完整實現)
Report Management API Endpoints (Complete Implementation)
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from moderation.models import Report
from moderation.serializers import ReportSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report_api(request):
    """
    創建舉報 / Create a report
    
    Request Body:
    - report_type: 舉報類型 ('LISTING_ISSUE' 或 'USER_BEHAVIOR') [必要]
    - listing_id: 若舉報刊登，需要提供 (可選)
    - reported_user_id: 若舉報用戶，需要提供 (可選)
    - reason: 舉報原因代碼 (必要) 
      LISTING: 'FAKE_ITEM', 'HARMFUL_ITEM', 'PROHIBITED_ITEM', 'POOR_QUALITY', 'OTHER'
      USER: 'FRAUD', 'ABUSE', 'IMPERSONATION', 'HARASSMENT', 'OTHER'
    - description: 舉報詳細說明 (必要)
    - evidence_images: 舉報證據圖片 (可選)
    """
    try:
        report_type = request.data.get('report_type', '')
        reason = request.data.get('reason', '')
        description = request.data.get('description', '')
        listing_id = request.data.get('listing_id')
        reported_user_id = request.data.get('reported_user_id')
        
        # 驗證必要欄位
        if not report_type or not reason or not description:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '舉報類型、原因和說明為必要欄位'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證舉報類型
        if report_type not in ['LISTING_ISSUE', 'USER_BEHAVIOR']:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_TYPE',
                    'message': '無效的舉報類型'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證舉報對象
        if report_type == 'LISTING_ISSUE':
            if not listing_id:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_TARGET',
                        'message': '舉報刊登需要提供刊登ID'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from listings.models import Listing
            try:
                listing = Listing.objects.get(id=listing_id)
            except Listing.DoesNotExist:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': '刊登不存在'
                    }
                }, status=status.HTTP_404_NOT_FOUND)
        
        elif report_type == 'USER_BEHAVIOR':
            if not reported_user_id:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_TARGET',
                        'message': '舉報用戶需要提供用戶ID'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from accounts.models import User
            try:
                User.objects.get(id=reported_user_id)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': '用戶不存在'
                    }
                }, status=status.HTTP_404_NOT_FOUND)
        
        # 檢查自我舉報
        if report_type == 'USER_BEHAVIOR' and reported_user_id == request.user.id:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '不能舉報自己'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 創建舉報
        report = Report.objects.create(
            reporter=request.user,
            report_type=report_type,
            reason=reason,
            description=description,
            listing_id=listing_id if report_type == 'LISTING_ISSUE' else None,
            reported_user_id=reported_user_id if report_type == 'USER_BEHAVIOR' else None,
            status=Report.Status.PENDING
        )
        
        # 記錄活動
        logger.info(f'Report created: ID={report.id}, Type={report_type}, Reporter={request.user.id}')
        
        serializer = ReportSerializer(report)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f'Error creating report: {str(e)}')
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_reports_api(request):
    """
    獲取我的舉報列表 / Get my reports list
    
    Query Parameters:
    - page: 分頁頁碼 (可選)
    - limit: 每頁筆數，預設 20，最大 100 (可選)
    - status: 篩選狀態 (可選)
    """
    try:
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 20)), 100)
        status_filter = request.query_params.get('status', '')
        
        queryset = Report.objects.filter(reporter=request.user).order_by('-created_at')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        
        reports = queryset[start:end]
        serializer = ReportSerializer(reports, many=True)
        
        return Response({
            'success': True,
            'data': {
                'reports': serializer.data,
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
def report_detail_api(request, report_id):
    """
    獲取舉報詳情 / Get report detail
    """
    try:
        report = Report.objects.get(id=report_id)
        
        # 只有舉報者和審查員可以查看
        if report.reporter_id != request.user.id and not request.user.is_staff:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '您無權查看此舉報'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ReportSerializer(report)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    except Report.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '舉報不存在'
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
def report_update_status_api(request, report_id):
    """
    更新舉報狀態 (僅管理員) / Update report status (Admin only)
    
    Request Body:
    - status: 新狀態 ('PENDING', 'INVESTIGATING', 'RESOLVED', 'REJECTED')
    - resolution: 解決說明 (可選)
    - action_taken: 採取的行動 (可選)
    """
    try:
        report = Report.objects.get(id=report_id)
        
        # 檢查管理員權限
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '僅管理員可以更新舉報狀態'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '新狀態為必要欄位'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 驗證狀態值
        valid_statuses = [s[0] for s in Report.Status.choices]
        if new_status not in valid_statuses:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': f'無效的狀態值。有效值：{valid_statuses}'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新狀態
        report.status = new_status
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        
        if new_status == Report.Status.RESOLVED:
            report.resolution = request.data.get('resolution', '')
            report.action_taken = request.data.get('action_taken', '')
        
        report.save()
        
        # 記錄活動
        logger.info(f'Report updated: ID={report.id}, Status={new_status}, Reviewer={request.user.id}')
        
        serializer = ReportSerializer(report)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    except Report.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '舉報不存在'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error updating report: {str(e)}')
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)
