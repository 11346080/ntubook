from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import PurchaseRequest
from .serializers import PurchaseRequestSerializer


# =============================================================================
# 預約請求列表（會員視角：買家視角 + 賣家視角合併一頁）
# GET ?role=buyer  ?role=seller  ?role= (預設顯示兩者)
# =============================================================================
class PurchaseRequestListView(LoginRequiredMixin, ListView):
    model = PurchaseRequest
    template_name = 'purchase_requests/request_list.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        role = self.request.GET.get('role', '')
        user = self.request.user
        if role == 'buyer':
            return PurchaseRequest.objects.filter(buyer=user).select_related(
                'listing__book', 'listing__seller__profile'
            )
        elif role == 'seller':
            return PurchaseRequest.objects.filter(
                listing__seller=user
            ).select_related('listing__book', 'buyer__profile')
        # default: 我的請求（買家視角）
        return PurchaseRequest.objects.filter(buyer=user).select_related(
            'listing__book', 'listing__seller__profile'
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_role'] = self.request.GET.get('role', 'buyer')
        # 賣家視角：收到的請求
        ctx['seller_requests'] = PurchaseRequest.objects.filter(
            listing__seller=self.request.user
        ).select_related('listing__book', 'buyer__profile')[:10]
        return ctx


# =============================================================================
# 預約請求詳情
# =============================================================================
class PurchaseRequestDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'purchase_requests/request_detail.html'
    context_object_name = 'purchase_request'

    def get_queryset(self):
        return PurchaseRequest.objects.filter(
            buyer=self.request.user
        ) | PurchaseRequest.objects.filter(
            listing__seller=self.request.user
        )


# =============================================================================
# 接受請求（僅賣家可操作）
# =============================================================================
def accept_request(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    if pr.listing.seller != request.user:
        messages.error(request, '您無權操作此請求。')
        return redirect('purchase_requests:request_list')
    if pr.status != PurchaseRequest.Status.PENDING:
        messages.warning(request, '此請求已非等待中狀態，無法接受。')
        return redirect('purchase_requests:request_list')

    pr.status = PurchaseRequest.Status.ACCEPTED
    pr.responded_at = timezone.now()
    pr.contact_released_at = timezone.now()
    pr.save(update_fields=['status', 'responded_at', 'contact_released_at', 'updated_at'])

    # 保留刊登
    pr.listing.status = 'RESERVED'
    pr.listing.save(update_fields=['status', 'updated_at'])

    messages.success(request, f'已接受預約請求 #{pr.id}。')
    return redirect('purchase_requests:request_list')


# =============================================================================
# 拒絕請求（僅賣家可操作）
# =============================================================================
def reject_request(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    if pr.listing.seller != request.user:
        messages.error(request, '您無權操作此請求。')
        return redirect('purchase_requests:request_list')
    if pr.status != PurchaseRequest.Status.PENDING:
        messages.warning(request, '此請求已非等待中狀態，無法拒絕。')
        return redirect('purchase_requests:request_list')

    pr.status = PurchaseRequest.Status.REJECTED
    pr.responded_at = timezone.now()
    pr.save(update_fields=['status', 'responded_at', 'updated_at'])

    messages.info(request, f'已拒絕預約請求 #{pr.id}。')
    return redirect('purchase_requests:request_list')


# =============================================================================
# 取消請求（買家或賣家）
# =============================================================================
def cancel_request(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    role = request.GET.get('role', 'buyer')
    is_buyer = (pr.buyer == request.user)
    is_seller = (pr.listing.seller == request.user)

    if not (is_buyer or is_seller):
        messages.error(request, '您無權操作此請求。')
        return redirect('purchase_requests:request_list')

    if pr.status != PurchaseRequest.Status.PENDING:
        messages.warning(request, '此請求已非等待中狀態，無法取消。')
        return redirect('purchase_requests:request_list')

    if is_buyer:
        pr.status = PurchaseRequest.Status.CANCELLED_BY_BUYER
    else:
        pr.status = PurchaseRequest.Status.CANCELLED_BY_SELLER
        # 取消時：若為賣家取消，且刊登是 RESERVED，則恢復為 AVAILABLE
        if pr.listing.status == 'RESERVED':
            pr.listing.status = 'AVAILABLE'
            pr.listing.save(update_fields=['status', 'updated_at'])

    pr.save(update_fields=['status', 'updated_at'])
    messages.info(request, f'已取消預約請求 #{pr.id}。')
    return redirect('purchase_requests:request_list')


# ================= API Views =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchaserequest_list_api(request):
    """
    取得預約請求的 JSON API 端點 / Get purchase requests API endpoint
    僅限已登入使用者 / Authentication required
    
    用户只能看到自己的请求（作为买家或卖家）
    Admin可以看到所有请求
    """
    if request.user.is_staff:
        # Admin can see all requests
        requests = PurchaseRequest.objects.all()
    else:
        # Regular users can only see their own requests
        requests = PurchaseRequest.objects.filter(
            buyer=request.user
        ) | PurchaseRequest.objects.filter(
            listing__seller=request.user
        )
    
    serializer = PurchaseRequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_requests_api(request):
    """
    獲取當前使用者的預約請求（買家視角）/ Get current user's purchase requests (buyer view)
    需要登入 / Requires authentication
    
    Response (200):
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "listing": {
                    "id": 1,
                    "book": { "title": "書名" },
                    "used_price": 350.00,
                    "seller": {
                        "profile": { "display_name": "賣家暱稱" }
                    }
                },
                "status": "PENDING",
                "buyer_message": "...",
                "created_at": "ISO datetime"
            }
        ]
    }
    """
    try:
        # 獲取當前使用者作為買家的所有預約
        requests = PurchaseRequest.objects.filter(
            buyer=request.user
        ).select_related(
            'listing__book',
            'listing__seller__profile'
        ).order_by('-created_at')
        
        data = []
        for req in requests:
            req_data = {
                'id': req.id,
                'listing': {
                    'id': req.listing.id,
                    'book': {
                        'title': req.listing.book.title if req.listing.book else '未知書籍',
                    },
                    'used_price': float(req.listing.used_price),
                    'seller': None,
                },
                'status': req.status,
                'buyer_message': req.buyer_message,
                'created_at': req.created_at.isoformat(),
                'role': 'buyer',
            }
            
            if req.listing.seller and req.listing.seller.profile:
                req_data['listing']['seller'] = {
                    'profile': {
                        'display_name': req.listing.seller.profile.display_name,
                    }
                }
            
            data.append(req_data)
        
        return Response({
            'success': True,
            'data': data,
            'count': len(data)
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': f'無法載入預約列表: {str(e)}'
            }
        }, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_purchase_request_api(request, listing_id):
    """
    為特定刊登創建預約請求 / Create a purchase request for a listing
    需要登入 / Requires authentication
    
    Request Body:
    {
        "buyer_message": "我想要這本書"
    }
    
    Response (201):
    {
        "success": true,
        "data": {
            "id": 1,
            "listing_id": 1,
            "status": "PENDING",
            "buyer_message": "...",
            "created_at": "ISO datetime"
        }
    }
    """
    try:
        from listings.models import Listing
        from django.db import IntegrityError
        
        # 檢查刊登是否存在
        try:
            listing = Listing.objects.select_related('book', 'seller__profile').get(id=listing_id)
        except Listing.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': '刊登不存在'
                }
            }, status=404)
        
        # 檢查刊登狀態
        if listing.status not in ['PUBLISHED', 'AVAILABLE']:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': '此刊登無法預約'
                }
            }, status=400)
        
        # 檢查是否為自己的刊登
        if listing.seller_id == request.user.id:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_OPERATION',
                    'message': '不能預約自己的刊登'
                }
            }, status=400)
        
        # 檢查是否已經預約過
        existing = PurchaseRequest.objects.filter(
            listing=listing,
            buyer=request.user,
            status__in=['PENDING', 'ACCEPTED']
        ).first()
        
        if existing:
            return Response({
                'success': False,
                'error': {
                    'code': 'ALREADY_EXISTS',
                    'message': '你已經預約過此刊登'
                }
            }, status=400)
        
        # 獲取留言
        buyer_message = request.data.get('buyer_message', '').strip()
        
        # 創建預約請求
        try:
            purchase_request = PurchaseRequest.objects.create(
                listing=listing,
                buyer=request.user,
                buyer_message=buyer_message,
                status=PurchaseRequest.Status.PENDING
            )
            
            return Response({
                'success': True,
                'data': {
                    'id': purchase_request.id,
                    'listing_id': listing.id,
                    'status': purchase_request.status,
                    'buyer_message': purchase_request.buyer_message,
                    'created_at': purchase_request.created_at.isoformat(),
                }
            }, status=201)
        
        except IntegrityError as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'DUPLICATE',
                    'message': '預約請求已存在'
                }
            }, status=400)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            }
        }, status=400)

