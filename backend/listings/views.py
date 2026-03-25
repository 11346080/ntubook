from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

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
    ListingCreateSerializer,
    check_sensitive_words,
    check_image_nsfw
)
from books.models import Book
from core.models import ClassGroup


# ================= 後台審查函數 =================

def async_review_listing(listing_id):
    """
    後台異步審查刊登：執行敏感詞檢查和圖片 NSFW 檢查
    如果審查通過，更新 status 為 AVAILABLE
    如果審查失敗，設置 status 為 REJECTED，並記錄原因
    
    此函數應在線程或 Celery 任務中運行
    """
    try:
        listing = Listing.objects.get(id=listing_id)
        
        # 1. 敏感詞檢查
        title_sensitive = check_sensitive_words(listing.book.title if listing.book else '')
        desc_sensitive = check_sensitive_words(listing.description or '')
        
        sensitive_words = list(set(title_sensitive + desc_sensitive))
        
        if sensitive_words:
            # 審查失敗：設置為 REJECTED
            listing.status = Listing.Status.REJECTED
            listing.reject_reason = f'用詞似有不妥，請重新斟酌筆墨...（敏感詞：{", ".join(sensitive_words)}）'
            listing.save()
            print(f'[REVIEW FAILED] Listing {listing_id}: {listing.reject_reason}')
            return
        
        # 2. 圖片 NSFW 檢查
        images = listing.images.all()
        for image in images:
            if image.image_binary and check_image_nsfw(image.image_binary):
                # 圖片被判定為 NSFW，拒絕此刊登
                listing.status = Listing.Status.REJECTED
                listing.reject_reason = f'圖片內容不符合平台政策，請重新上傳合適的圖片'
                listing.save()
                print(f'[REVIEW FAILED] Listing {listing_id}: Image NSFW check failed')
                return
        
        # 3. 審查通過：設置為 AVAILABLE
        listing.status = Listing.Status.AVAILABLE
        listing.save()
        print(f'[REVIEW PASSED] Listing {listing_id}: Approved and published')
    
    except Listing.DoesNotExist:
        print(f'[ERROR] Listing {listing_id} not found')
    except Exception as e:
        print(f'[ERROR] Failed to review listing {listing_id}: {str(e)}')


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
        'origin_class_group__department',
        'origin_class_group__program_type',
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

    # 學制篩選（透過 origin_class_group → program_type）
    program_type_id = request.GET.get('program_type_id', '').strip()
    if program_type_id:
        listings = listings.filter(
            origin_class_group__program_type_id=program_type_id
        )

    # 系所篩選（透過 origin_class_group → department）
    department_id = request.GET.get('department_id', '').strip()
    if department_id:
        listings = listings.filter(
            origin_class_group__department_id=department_id
        )

    # 年級篩選（origin_class_group.grade_no 乘以 10）
    grade_no = request.GET.get('grade_no', '').strip()
    if grade_no:
        try:
            target_grade_db = int(grade_no) * 10
            listings = listings.filter(origin_class_group__grade_no=target_grade_db)
        except (ValueError, TypeError):
            pass

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
                "used_price": "691",
                "condition_level": "GOOD",
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


@api_view(['GET', 'DELETE'])
@permission_classes([AllowAny])
def listing_detail_api(request, listing_id):
    """
    取得單一刊登的詳細資訊或刪除刊登 / Get or delete single listing
    - GET: 公開存取 / Public access
    - DELETE: 需要認證且為刊登擁有者 / Requires authentication and ownership
    
    Parameters:
    - listing_id: 刊登 ID
    
    GET Response (200):
    {
        "success": true,
        "data": { ... }
    }
    
    DELETE Response (200):
    {
        "success": true,
        "message": "刊登已刪除"
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
        if request.method == 'GET':
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
        
        elif request.method == 'DELETE':
            # 驗證權限
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': '需要登入才能刪除刊登'
                    }
                }, status=401)
            
            listing = Listing.objects.get(id=listing_id)
            
            # 檢查是否為刊登擁有者
            if listing.seller_id != request.user.id:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': '只有刊登者才能刪除此刊登'
                    }
                }, status=403)
            
            # 只允許刪除草稿或已拒絕的刊登
            if listing.status not in [Listing.Status.DRAFT, Listing.Status.REJECTED, Listing.Status.OFF_SHELF]:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_STATUS',
                        'message': f'狀態為 {listing.get_status_display()} 的刊登不能刪除'
                    }
                }, status=400)
            
            # 以 soft delete 方式刪除
            listing.deleted_at = timezone.now()
            listing.save(update_fields=['deleted_at'])
            
            return Response({
                'success': True,
                'message': '刊登已刪除'
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
                'code': 'ERROR',
                'message': f'操作失敗: {str(e)}'
            }
        }, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_purchase_request_for_listing(request, listing_id):
    """
    為特定刊登建立預約請求 / Create a purchase request for a listing
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
        from purchase_requests.models import PurchaseRequest
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
        if listing.status not in [Listing.Status.AVAILABLE]:
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
            "publication_date_text": "...|null"
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
                # 取得 publication_year（從 new_book 或解析 publication_date_text）
                pub_year = new_book_data.get('publication_year')
                if not pub_year:
                    import re
                    pd_text = new_book_data.get('publication_date_text') or ''
                    m = re.search(r'\b(19|20)\d{2}\b', pd_text)
                    if m:
                        pub_year = int(m.group(0))

                # 建立新書籍
                book = Book.objects.create(
                    isbn13=isbn13,
                    isbn10=new_book_data.get('isbn10') or '',
                    title=new_book_data['title'],
                    author_display=new_book_data['author_display'],
                    publisher=new_book_data['publisher'],
                    publication_year=pub_year,
                    publication_date_text=new_book_data.get('publication_date_text'),
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
        
        # 2. 取得 class_group：優先取 payload，沒有則從 user profile 取得
        origin_class_group_id = data.get('origin_class_group_id')
        origin_academic_year = data.get('origin_academic_year')
        origin_term = data.get('origin_term')

        if not origin_class_group_id or not origin_academic_year or not origin_term:
            # 從 user profile 自動帶入
            try:
                from accounts.models import UserProfile
                profile = UserProfile.objects.select_related(
                    'class_group', 'class_group__department', 'class_group__program_type'
                ).get(user=request.user)
                if not origin_class_group_id and profile.class_group:
                    origin_class_group_id = profile.class_group.id
                if not origin_academic_year and profile.grade_no:
                    # grade_no 在 DB 是 (入學年 * 10 + 年級)，取 grade_no // 10 + (grade_no % 10) - 1
                    # 但最簡單：取 current year 作為 academic year
                    import datetime
                    origin_academic_year = datetime.date.today().year
                if not origin_term:
                    import datetime
                    month = datetime.date.today().month
                    origin_term = 1 if month < 7 else 2
            except Exception:
                pass

        if not origin_class_group_id:
            return Response({
                'success': False,
                'error': {
                    'code': 'CLASS_GROUP_REQUIRED',
                    'message': '請先填寫個人資料（班級），或提供 origin_class_group_id'
                }
            }, status=400)

        if not origin_academic_year:
            return Response({
                'success': False,
                'error': {
                    'code': 'ACADEMIC_YEAR_REQUIRED',
                    'message': '無法自動推算課程年份，請提供 origin_academic_year'
                }
            }, status=400)

        if not origin_term:
            return Response({
                'success': False,
                'error': {
                    'code': 'TERM_REQUIRED',
                    'message': '無法自動推算學期，請提供 origin_term'
                }
            }, status=400)

        try:
            class_group = ClassGroup.objects.get(id=origin_class_group_id)
        except ClassGroup.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'CLASS_GROUP_NOT_FOUND',
                    'message': f'班級 ID {data["origin_class_group_id"]} 不存在'
                }
            }, status=404)
        
        # 3. 建立刊登 (狀態為 PENDING，待後台異步審核)
        listing = Listing.objects.create(
            seller=request.user,
            book=book,
            origin_academic_year=origin_academic_year,
            origin_term=origin_term,
            origin_class_group=class_group,
            used_price=data['used_price'],
            condition_level=data['condition_level'],
            description=data.get('description') or '',
            seller_note=data.get('seller_note'),
            status=Listing.Status.PENDING
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
                
                # 解碼 base64
                image_data = base64.b64decode(base64_data)
                
                # 直接存到數據庫（不保存到文件系統）
                file_name = f'listing_{listing.id}_img_{idx}.{ext}'
                listing_image = ListingImage.objects.create(
                    listing=listing,
                    image_binary=image_data,  # 二進制數據直接存數據庫
                    mime_type=mime_type,  # 保存 MIME type 以便前端正確顯示
                    file_name=file_name,
                    is_primary=(idx == 1),  # 第一張為主圖
                    sort_order=idx - 1
                )
                print(f'✓ 圖片已存入數據庫: ListingImage {listing_image.id} ({file_name}, {len(image_data)} bytes)')
                
            except Exception as img_error:
                print(f'圖片上傳錯誤 ({idx}): {str(img_error)}')
                # 記錄錯誤但繼續，不阻擋整個流程
                continue
        
        # 5. 序列化回傳
        output_serializer = ListingDetailSerializer(listing)
        
        # ⚠️ 不在此處進行任何 AI 審查
        # AI 審查已脫鉤至後台獨立批次處理程式 (management command)
        # Web API 只負責快速接收資料、儲存至資料庫，立即回傳
        
        return Response({
            'success': True,
            'data': output_serializer.data,
            'message': '書卷已遞交至藏經閣，審核官正在審閱中...'
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


# ================= 我的刊登 API =================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_listings_api(request):
    """
    獲取推薦的刊登：大他一屆的學長姐所刊登的書籍 / Get recommended listings
    需要登入 / Requires authentication
    
    邏輯：根據當前用戶的班級 → 找出「下一屆」（年級+1）的刊登列表
    
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
        # 獲取當前用戶的個人資料
        user_profile = request.user.profile if hasattr(request.user, 'profile') else None
        
        if not user_profile or not user_profile.class_group or not user_profile.grade_no:
            # 如果用戶沒有填寫班級或年級，返回空值
            return Response({
                'success': True,
                'data': [],
                'count': 0,
                'message': '請先填寫個人資料才能查看推薦書籍'
            })
        
        # 計算推薦目標年級（大他一屆 = grade_no + 1）
        target_grade = user_profile.grade_no + 1
        current_class_group = user_profile.class_group
        
        # 檢查是否超過最高年級（假設最多 4 年級）
        if target_grade > 4:
            return Response({
                'success': True,
                'data': [],
                'count': 0,
                'message': '您已是最高年級，無上屆推薦'
            })
        
        # 獲取請求參數
        count = int(request.GET.get('count', 6))
        count = min(count, 20)  # 最多 20 筆，防止 DoS
        
        # 查詢：來自相同班級、高一年級、已發佈的刊登
        # 使用 ClassGroup 的 grade_no 欄位來篩選
        # 絕對排除自己的書籍
        from core.models import ClassGroup as CG
        
        target_class_groups = CG.objects.filter(
            department=current_class_group.department,
            program_type=current_class_group.program_type,
            grade_no=target_grade
        ).values_list('id', flat=True)
        
        listings = Listing.objects.filter(
            origin_class_group_id__in=target_class_groups,
            status=Listing.Status.AVAILABLE,
            deleted_at__isnull=True
        ).exclude(
            seller=request.user  # 絕對不推薦自己刊登的書
        ).select_related(
            'book',
            'seller',
            'seller__profile',
            'seller__profile__department'
        ).prefetch_related(
            'images'
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
                'message': f'無法載入推薦書籍: {str(e)}'
            }
        }, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def listing_image_api(request, listing_id, image_id):
    """
    讀取指定刊登的圖片 / Get listing image binary data
    公開存取 / Public access
    
    URL: /api/listings/<listing_id>/images/<image_id>/
    
    Response (200):
        圖片的二進制資料，Content-Type 為 image 的 MIME type
    """
    try:
        image = ListingImage.objects.select_related('listing').get(
            id=image_id,
            listing_id=listing_id
        )
        
        if not image.image_binary:
            return Response(
                {'success': False, 'error': {'code': 'NO_IMAGE', 'message': '圖片資料為空'}},
                status=404
            )
        
        return HttpResponse(
            image.image_binary,
            content_type=image.mime_type or 'image/jpeg'
        )
    except ListingImage.DoesNotExist:
        return Response(
            {'success': False, 'error': {'code': 'NOT_FOUND', 'message': '找不到圖片'}},
            status=404
        )
    except Exception as e:
        return Response(
            {'success': False, 'error': {'code': 'ERROR', 'message': str(e)}},
            status=400
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_listings_api(request):
    """
    獲取當前登入用戶的所有刊登（包括所有狀態）/ Get current user's all listings
    需要登入 / Requires authentication
    
    Response (200):
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "book": {
                    "title": "書名",
                    "author_display": "作者"
                },
                "used_price": 350.00,
                "status": "PENDING|DRAFT|AVAILABLE|RESERVED|SOLD|OFF_SHELF|REJECTED",
                "status_display": "審核中|已上架|已售出|已退回|...",
                "reject_reason": "...|null",
                "listing_images": [
                    { "id": 1, "image_base64": "data:image/jpeg;base64,...", "mime_type": "image/jpeg", "is_primary": true }
                ],
                "created_at": "ISO datetime"
            }
        ]
    }
    """
    try:
        # 查詢當前用戶的所有刊登（包括所有狀態）
        listings = Listing.objects.filter(
            seller=request.user
        ).select_related(
            'book'
        ).prefetch_related('images').order_by('-created_at')
        
        # 序列化簡化版本（用於列表顯示）
        data = []
        for listing in listings:
            images = list(listing.images.values('file_path'))
            
            data.append({
                'id': listing.id,
                'book': {
                    'id': listing.book.id if listing.book else None,
                    'title': listing.book.title if listing.book else '未知書籍',
                    'author_display': listing.book.author_display if listing.book else '未知作者',
                },
                'used_price': float(listing.used_price),
                'condition_level': listing.condition_level,
                'status': listing.status,
                'status_display': status_display_map.get(listing.status, listing.status),
                'reject_reason': listing.reject_reason,
                'listing_images': images_serializer.data,
                'created_at': listing.created_at.isoformat(),
            })

        return Response({
            'success': True,
            'data': data,
            'count': len(data)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': f'無法載入刊登列表: {str(e)}'
            }
        }, status=400)

