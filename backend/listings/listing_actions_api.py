"""
刊登管理 API 端點 (完整實現)
Listing Management API Endpoints (Complete Implementation)
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from listings.models import Listing, ListingImage
from listings.serializers import ListingDetailSerializer
from books.models import Book


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_purchase_request(request, request_id):
    """
    賣家接受預約請求 / Seller accepts purchase request
    """
    try:
        from purchase_requests.models import PurchaseRequest
        
        pr = PurchaseRequest.objects.get(id=request_id)
        
        # 檢查是否為賣家
        if pr.listing.seller_id != request.user.id:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '只有賣家才能接受此請求'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 檢查狀態
        if pr.status != PurchaseRequest.Status.PENDING:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': '此請求已非待處理狀態'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新請求和刊登狀態
        pr.status = PurchaseRequest.Status.ACCEPTED
        pr.responded_at = timezone.now()
        pr.contact_released_at = timezone.now()
        pr.save(update_fields=['status', 'responded_at', 'contact_released_at', 'updated_at'])
        
        pr.listing.status = Listing.Status.RESERVED
        pr.listing.save(update_fields=['status', 'updated_at'])
        
        # 創建通知 (可選)
        from notifications.models import Notification
        Notification.objects.create(
            user=pr.buyer,
            type_code='REQUEST_ACCEPTED',
            title='預約請求已接受',
            message=f'您的「{pr.listing.book.title}」預約已被賣家接受',
            related_request_id=pr.id
        )
        
        return Response({
            'success': True,
            'data': {
                'status': pr.status,
                'listing_status': pr.listing.status
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_purchase_request(request, request_id):
    """
    賣家拒絕預約請求 / Seller rejects purchase request
    """
    try:
        from purchase_requests.models import PurchaseRequest
        
        pr = PurchaseRequest.objects.get(id=request_id)
        
        # 檢查是否為賣家
        if pr.listing.seller_id != request.user.id:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '只有賣家才能拒絕此請求'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 檢查狀態
        if pr.status != PurchaseRequest.Status.PENDING:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': '此請求已非待處理狀態'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新請求狀態
        pr.status = PurchaseRequest.Status.REJECTED
        pr.responded_at = timezone.now()
        pr.save(update_fields=['status', 'responded_at', 'updated_at'])
        
        # 創建通知
        from notifications.models import Notification
        Notification.objects.create(
            user=pr.buyer,
            type_code='REQUEST_REJECTED',
            title='預約請求已拒絕',
            message=f'您的「{pr.listing.book.title}」預約已被賣家拒絕',
            related_request_id=pr.id
        )
        
        return Response({
            'success': True,
            'data': {
                'status': pr.status
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_purchase_request(request, request_id):
    """
    取消預約請求 (買家或賣家) / Cancel purchase request (buyer or seller)
    """
    try:
        from purchase_requests.models import PurchaseRequest
        
        pr = PurchaseRequest.objects.get(id=request_id)
        
        is_buyer = pr.buyer_id == request.user.id
        is_seller = pr.listing.seller_id == request.user.id
        
        if not (is_buyer or is_seller):
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '您無權取消此請求'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 檢查狀態
        if pr.status not in [PurchaseRequest.Status.PENDING, PurchaseRequest.Status.ACCEPTED]:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': '此請求無法取消'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新狀態
        if is_buyer:
            pr.status = PurchaseRequest.Status.CANCELLED_BY_BUYER
        else:
            pr.status = PurchaseRequest.Status.CANCELLED_BY_SELLER
            # 賣家取消時恢復刊登狀態
            if pr.listing.status == Listing.Status.RESERVED:
                pr.listing.status = Listing.Status.PUBLISHED
                pr.listing.save(update_fields=['status', 'updated_at'])
        
        pr.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'success': True,
            'data': {
                'status': pr.status,
                'listing_status': pr.listing.status
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def listing_off_shelf(request, listing_id):
    """
    下架刊登 / Take listing off shelf
    """
    try:
        listing = Listing.objects.get(id=listing_id)
        
        # 檢查是否為擁有者
        if listing.seller_id != request.user.id:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '只有賣家才能下架此刊登'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 檢查狀態
        if listing.status not in [Listing.Status.PUBLISHED, Listing.Status.RESERVED]:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': f'狀態為 {listing.get_status_display()} 的刊登不能下架'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新狀態
        off_shelf_reason = request.data.get('off_shelf_reason', '')
        listing.status = Listing.Status.OFF_SHELF
        listing.off_shelf_reason = off_shelf_reason
        listing.off_shelf_at = timezone.now()
        listing.save(update_fields=['status', 'off_shelf_reason', 'off_shelf_at', 'updated_at'])
        
        return Response({
            'success': True,
            'data': {
                'status': listing.status,
                'off_shelf_at': listing.off_shelf_at.isoformat()
            }
        })
    
    except Listing.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '刊登不存在'
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def listing_mark_sold(request, listing_id):
    """
    標記刊登為已售 / Mark listing as sold
    """
    try:
        listing = Listing.objects.get(id=listing_id)
        
        # 檢查是否為擁有者
        if listing.seller_id != request.user.id:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '只有賣家才能標記此刊登為已售'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 檢查狀態
        if listing.status not in [Listing.Status.PUBLISHED, Listing.Status.RESERVED]:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': f'狀態為 {listing.get_status_display()} 的刊登不能標記為已售'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新狀態
        listing.status = Listing.Status.SOLD
        listing.sold_at = timezone.now()
        
        # 若有接受的預約請求，需要更新
        accepted_request_id = request.data.get('accepted_request_id')
        if accepted_request_id:
            from purchase_requests.models import PurchaseRequest
            pr = PurchaseRequest.objects.filter(
                id=accepted_request_id,
                listing=listing,
                status=PurchaseRequest.Status.ACCEPTED
            ).first()
            if pr:
                pr.completed_at = timezone.now()
                pr.save(update_fields=['completed_at'])
        
        listing.save(update_fields=['status', 'sold_at', 'updated_at'])
        
        return Response({
            'success': True,
            'data': {
                'status': listing.status,
                'sold_at': listing.sold_at.isoformat()
            }
        })
    
    except Listing.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '刊登不存在'
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def listing_relist(request, listing_id):
    """
    重新上架刊登 / Relist a listing
    """
    try:
        listing = Listing.objects.get(id=listing_id)
        
        # 檢查是否為擁有者
        if listing.seller_id != request.user.id:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': '只有賣家才能重新上架此刊登'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 檢查狀態
        if listing.status not in [Listing.Status.OFF_SHELF, Listing.Status.SOLD]:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': '此刊登無法重新上架'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新狀態
        listing.status = Listing.Status.PUBLISHED
        listing.off_shelf_reason = None
        listing.sold_at = None
        listing.save(update_fields=['status', 'off_shelf_reason', 'sold_at', 'updated_at'])
        
        return Response({
            'success': True,
            'data': {
                'status': listing.status
            }
        })
    
    except Listing.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '刊登不存在'
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
