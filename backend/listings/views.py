from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Listing
from .forms import ListingCreateForm
from .serializers import ListingSerializer, ListingLatestSerializer


class ListingListView(ListView):
    """刊登列表頁（含關鍵字搜尋、ISBN 篩選、價格區間、排序）"""
    model = Listing
    template_name = 'listings/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 24

    def get_queryset(self):
        qs = Listing.objects.filter(
            status=Listing.Status.AVAILABLE,
            deleted_at__isnull=True
        ).select_related(
            'book',
            'seller__profile',
            'origin_class_group__department'
        ).prefetch_related('images')

        # 關鍵字搜尋（書名 / 作者）
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(book__title__icontains=q) |
                Q(book__author_display__icontains=q)
            )

        # ISBN 篩選
        isbn = self.request.GET.get('isbn', '').strip()
        if isbn:
            qs = qs.filter(
                Q(book__isbn13__icontains=isbn) |
                Q(book__isbn10__icontains=isbn)
            )

        # 價格區間
        min_price = self.request.GET.get('min_price', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()
        if min_price:
            try:
                qs = qs.filter(used_price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                qs = qs.filter(used_price__lte=float(max_price))
            except ValueError:
                pass

        # 排序
        sort = self.request.GET.get('sort', '-created_at').strip()
        allowed_sorts = ['-created_at', 'created_at', 'used_price', '-used_price']
        if sort in allowed_sorts:
            qs = qs.order_by(sort)
        else:
            qs = qs.order_by('-created_at')

        return qs


class ListingDetailView(DetailView):
    """刊登詳情頁"""
    model = Listing
    template_name = 'listings/listing_detail.html'
    context_object_name = 'listing'

    def get_queryset(self):
        return Listing.objects.select_related(
            'book',
            'seller__profile',
            'origin_class_group__department'
        ).prefetch_related('images')


class ListingCreateView(LoginRequiredMixin, CreateView):
    """建立刊登頁"""
    model = Listing
    form_class = ListingCreateForm
    template_name = 'listings/listing_create.html'

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.status = Listing.Status.AVAILABLE
        return super().form_valid(form)


# ================= API Views =================


@api_view(['GET'])
@permission_classes([AllowAny])
def listing_list_api(request):
    """
    取得所有刊登的 JSON API 端點 / Get all listings API endpoint
    公開存取 / Public access
    只顯示活躍的刊登 / Shows only active listings
    """
    # Filter only active, non-deleted listings
    listings = Listing.objects.filter(
        status=Listing.Status.AVAILABLE,
        deleted_at__isnull=True
    ).select_related(
        'book',
        'seller',
        'origin_class_group__department'
    ).prefetch_related('images')
    
    serializer = ListingSerializer(listings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def latest_listings_api(request):
    """
    取得最新 6 筆刊登的 JSON API 端點 / Get latest 6 listings API endpoint
    用於首頁展示 / For homepage display
    
    Query Parameters (可選):
    - count: 返回筆數，預設 6 (最多 20)
    
    Response:
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "book_title": "書名",
                "book_author": "作者",
                "cover_image_url": "URL",
                "used_price": 100.00,
                "condition_level": "GOOD",
                "seller_display_name": "賣家",
                "seller_department": "系所",
                "created_at": "ISO datetime",
                "primary_image": {...}
            }
        ]
    }
    """
    try:
        # 獲取請求參數
        count = int(request.GET.get('count', 6))
        count = min(count, 20)  # 最多 20 筆，防止 DoS
        
        # 查詢：最新的、可購買的、未刪除的刊登
        listings = Listing.objects.filter(
            status=Listing.Status.AVAILABLE,
            deleted_at__isnull=True
        ).select_related(
            'book',                              # Listing -> Book (ForeignKey)
            'seller',                            # Listing -> User (ForeignKey)
            'seller__profile',                   # User -> UserProfile (OneToOne)
            'seller__profile__department'        # UserProfile -> Department (ForeignKey)
        ).prefetch_related(
            'images'                             # Listing -> ListingImage (Reverse)
        ).order_by('-created_at')[:count]
        
        serializer = ListingLatestSerializer(listings, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': f'無法載入最新書籍: {str(e)}'
            }
        }, status=400)

