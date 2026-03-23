from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
import base64
import json
import uuid

from .models import Listing, ListingImage
from .forms import ListingCreateForm
from .serializers import (
    ListingSerializer, 
    ListingLatestSerializer, 
    ListingDetailSerializer,
    ListingCreateSerializer
)
from books.models import Book
from core.models import ClassGroup


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


class ListingPagination(PageNumberPagination):
    """刊登 API 分頁器"""
    page_size = 24
    page_size_query_param = 'page_size'
    max_page_size = 100


def _get_listings_response(request):
    """
    Helper function to get paginated listings response
    不使用 @api_view 裝飾器，可以被其他 API 視圖調用
    """
    # Filter only active, non-deleted listings
    listings = Listing.objects.filter(
        status=Listing.Status.AVAILABLE,
        deleted_at__isnull=True
    ).select_related(
        'book',
        'seller',
        'seller__profile',
        'origin_class_group__department'
    ).prefetch_related('images')
    
    # 關鍵字搜尋
    keyword = request.GET.get('keyword', '').strip()
    if keyword:
        listings = listings.filter(
            Q(book__title__icontains=keyword) |
            Q(book__author_display__icontains=keyword) |
            Q(book__isbn13__icontains=keyword) |
            Q(description__icontains=keyword)
        )
    
    # 排序（保持原有邏輯）
    sort = request.GET.get('sort', '-created_at').strip()
    allowed_sorts = ['-created_at', 'created_at', 'used_price', '-used_price']
    if sort in allowed_sorts:
        listings = listings.order_by(sort)
    else:
        listings = listings.order_by('-created_at')
    
    # 分頁
    paginator = ListingPagination()
    paginated_listings = paginator.paginate_queryset(listings, request)
    serializer = ListingSerializer(paginated_listings, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def listing_list_api(request):
    """
    取得所有刊登的 JSON API 端點 / Get all listings API endpoint
    公開存取 / Public access
    只顯示活躍的刊登 / Shows only active listings
    
    Query Parameters (可選):
    - keyword: 搜尋關鍵字（搜尋書名、作者、ISBN、說明）
    - sort: 排序方式 (default: -created_at)
    - page: 頁碼 (default: 1)
    - page_size: 每頁筆數 (default: 24, max: 100)
    """
    return _get_listings_response(request)


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


@api_view(['GET'])
@permission_classes([AllowAny])
def listing_detail_api(request, listing_id):
    """
    取得單一刊登的詳細資訊 JSON API 端點 / Get single listing detail API endpoint
    公開存取 / Public access
    
    Parameters:
    - listing_id: 刊登 ID
    
    Response (200):
    {
        "success": true,
        "data": {
            "id": 1,
            "book": {
                "id": 1,
                "title": "書名",
                "author_display": "作者",
                "isbn13": "...",
                "isbn10": "...",
                "publisher": "出版社",
                "publication_year": 2020,
                "publication_date_text": "2020-01-01",
                "edition": "1st",
                "cover_image_url": "URL"
            },
            "seller": {
                "id": 1,
                "display_name": "賣家暱稱",
                "department": {
                    "id": 1,
                    "name_zh": "資管系"
                }
            },
            "used_price": 350.00,
            "condition_level": "GOOD",
            "condition_level_display": "良好",
            "description": "商品描述...",
            "seller_note": "賣家備註...",
            "status": "PUBLISHED",
            "origin_academic_year": 2023,
            "origin_term": 1,
            "origin_class_group": {
                "id": 1,
                "code": "...",
                "name_zh": "班級名稱",
                "department": {...}
            },
            "images": [
                {"id": 1, "file_path": "...", "is_primary": true, "sort_order": 0}
            ],
            "created_at": "ISO datetime",
            "updated_at": "ISO datetime"
        }
    }
    
    Response (404):
    {
        "success": false,
        "error": {
            "code": "NOT_FOUND",
            "message": "查無此書籍刊登"
        }
    }
    """
    try:
        # 獲取刊登（只顯示活躍的刊登）
        listing = Listing.objects.select_related(
            'book',
            'seller__profile',
            'seller__profile__department',
            'origin_class_group__department'
        ).prefetch_related('images').get(
            id=listing_id,
            status=Listing.Status.AVAILABLE,
            deleted_at__isnull=True
        )
        
        serializer = ListingDetailSerializer(listing)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    except Listing.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '查無此書籍刊登'
            }
        }, status=404)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': f'無法載入書籍詳情: {str(e)}'
            }
        }, status=400)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def listing_list_or_create_api(request):
    """
    處理 /api/listings/ 根路由的 GET 和 POST 請求
    - GET: 列表查詢（公開）
    - POST: 建立新刊登（需要登入）
    """
    if request.method == 'POST':
        # 檢查認證
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOT_AUTHENTICATED',
                    'message': '需要登入才能建立刊登'
                }
            }, status=401)
        
        # 調用建立刊登視圖
        return create_listing_api(request)
    
    else:  # GET
        return _get_listings_response(request)


def create_listing_api(request):
    """
    建立新刊登 API 端點 / Create listing API endpoint
    需要登入 / Requires authentication
    
    Request body:
    {
        "book_id": int|null,
        "new_book": {
            "isbn13": "...",
            "isbn10": "...|null",
            "title": "...",
            "author_display": "...",
            "publisher": "...",
            "publication_date_text": "...|null",
            "edition": "...|null"
        } or null,
        "origin_academic_year": int,
        "origin_term": 1|2,
        "origin_class_group_id": int,
        "used_price": decimal,
        "condition_level": "LIKE_NEW|GOOD|FAIR|POOR",
        "description": "text|null",
        "seller_note": "text|null",
        "images": ["base64_string_1", "base64_string_2", ...]
    }
    
    Response (201):
    {
        "success": true,
        "data": {
            "id": 1,
            "book": {...},
            "seller": {...},
            "used_price": 350.00,
            "status": "PUBLISHED",
            ...
        }
    }
    
    Response (400|403|404):
    {
        "success": false,
        "error": {
            "code": "VALIDATION_ERROR|CLASS_GROUP_NOT_FOUND|BOOK_NOT_FOUND",
            "message": "錯誤訊息"
        }
    }
    """
    try:
        # 驗證請求資料
        serializer = ListingCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '提交資料不符合格式',
                    'details': serializer.errors
                }
            }, status=400)
        
        data = serializer.validated_data
        
        # 1. 處理書籍（create or get）
        book = None
        if data.get('book_id'):
            try:
                book = Book.objects.get(id=data['book_id'])
            except Book.DoesNotExist:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'BOOK_NOT_FOUND',
                        'message': f'書籍 ID {data["book_id"]} 不存在'
                    }
                }, status=404)
        elif data.get('new_book'):
            new_book_data = data['new_book']
            isbn13 = new_book_data.get('isbn13') or ''
            
            # 如果提供了 ISBN-13，先檢查是否已存在
            if isbn13:
                try:
                    book = Book.objects.get(isbn13=isbn13)
                except Book.DoesNotExist:
                    book = None
            else:
                book = None
            
            # 如果書籍不存在，建立新書籍
            if not book:
                # 如果沒有 ISBN-13，生成一個唯一的佔位符
                if not isbn13:
                    isbn13 = f"MANUAL-{uuid.uuid4().hex[:12].upper()}"
                
                # 建立新書籍
                book = Book.objects.create(
                    isbn13=isbn13,
                    isbn10=new_book_data.get('isbn10') or '',
                    title=new_book_data['title'],
                    author_display=new_book_data['author_display'],
                    publisher=new_book_data['publisher'],
                    publication_date_text=new_book_data.get('publication_date_text'),
                    edition=new_book_data.get('edition'),
                    metadata_source='MANUAL',
                    metadata_status='MANUALLY_CONFIRMED'
                )
        
        if not book:
            return Response({
                'success': False,
                'error': {
                    'code': 'BOOK_ERROR',
                    'message': '無法建立或取得書籍資訊'
                }
            }, status=400)
        
        # 2. 驗證班級
        try:
            class_group = ClassGroup.objects.get(id=data['origin_class_group_id'])
        except ClassGroup.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'CLASS_GROUP_NOT_FOUND',
                    'message': f'班級 ID {data["origin_class_group_id"]} 不存在'
                }
            }, status=404)
        
        # 3. 建立刊登
        listing = Listing.objects.create(
            seller=request.user,
            book=book,
            origin_academic_year=data['origin_academic_year'],
            origin_term=data['origin_term'],
            origin_class_group=class_group,
            used_price=data['used_price'],
            condition_level=data['condition_level'],
            description=data.get('description') or '',
            seller_note=data.get('seller_note'),
            status=Listing.Status.AVAILABLE
        )
        
        # 4. 處理圖片上傳 - 直接存到數據庫
        images = data.get('images', [])
        for idx, base64_string in enumerate(images, 1):
            try:
                # 從 base64 提取 MIME type 和實際資料
                # 格式: data:image/jpeg;base64,/9j/4AAQSkZJRg==...
                if base64_string.startswith('data:'):
                    header, base64_data = base64_string.split(',', 1)
                    # 從 header 提取 mime type (如: image/jpeg)
                    mime_type = header.split(';')[0].replace('data:', '')
                    ext = mime_type.split('/')[-1]  # jpeg, png, webp, gif
                else:
                    base64_data = base64_string
                    mime_type = 'image/jpeg'
                    ext = 'jpg'  # 預設副檔名
                
                # 解碼 base64 為二進制
                image_binary = base64.b64decode(base64_data)
                file_name = f'listing_{listing.id}_img_{idx}.{ext}'
                
                # 直接存到數據庫（不保存到文件系統）
                listing_image = ListingImage.objects.create(
                    listing=listing,
                    image_binary=image_binary,  # 二進制數據直接存數據庫
                    mime_type=mime_type,  # 保存 MIME type 以便前端正確顯示
                    file_name=file_name,
                    is_primary=(idx == 1),  # 第一張為主圖
                    sort_order=idx - 1
                )
                print(f'✓ 圖片已存入數據庫: ListingImage {listing_image.id} ({file_name}, {len(image_binary)} bytes)')
                
            except Exception as img_error:
                print(f'圖片上傳錯誤 ({idx}): {str(img_error)}')
                # 記錄錯誤但繼續，不阻擋整個流程
                continue
        
        # 5. 序列化回傳
        output_serializer = ListingDetailSerializer(listing)
        
        return Response({
            'success': True,
            'data': output_serializer.data
        }, status=201)
    
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_JSON',
                'message': 'POST 資料必須為有效的 JSON 格式'
            }
        }, status=400)
    
    except Exception as e:
        import traceback
        print(f'建立刊登錯誤: {str(e)}')
        traceback.print_exc()
        return Response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': f'伺服器錯誤: {str(e)}'
            }
        }, status=500)

