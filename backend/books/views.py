from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Book, BookApplicability, BookFavorite
from .serializers import BookSerializer, BookApplicabilitySerializer
from .isbn_service import lookup_isbn


@api_view(['GET'])
@permission_classes([AllowAny])
def book_list_api(request):
    """
    取得所有書籍的 JSON API 端點 / Get all books API endpoint
    公開存取 / Public access
    """
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def bookapplicability_list_api(request):
    """
    取得所有書籍適用對象的 JSON API 端點 / Get all book applicabilities API endpoint
    公開存取 / Public access
    """
    applicabilities = BookApplicability.objects.all()
    serializer = BookApplicabilitySerializer(applicabilities, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def isbn_lookup_api(request):
    """
    ISBN 查詢 API（本地優先，外部 API 回填）

    Request:
        POST /api/books/isbn/lookup/
        Body: { "isbn": "9789576097690" }

    Response (200):
        {
            "success": true,
            "data": {
                "source": "local" | "external_api" | "not_found",
                "is_new": bool,
                "book_id": int | null,
                "book": {
                    "id", "isbn13", "isbn10", "title",
                    "author_display", "publisher",
                    "publication_year", "publication_date_text",
                    "edition", "cover_image_url"
                } | null,
                "message": "人類可讀訊息"
            }
        }
    """
    isbn = (request.data.get('isbn') or '').strip()
    print(f'[ISBN API] 進入 ISBN 查詢 API, isbn={isbn}')

    if not isbn:
        return Response({
            'success': False,
            'error': {
                'code': 'MISSING_ISBN',
                'message': '請提供 ISBN'
            }
        }, status=400)

    result = lookup_isbn(isbn)
    print(
        f'[ISBN API] lookup_isbn 回傳, source={result["source"]}, '
        f'is_new={result.get("is_new")}, book_id={result.get("book_id")}, '
        f'message={result.get("message")}'
    )

    if result['source'] == 'not_found':
        return Response({
            'success': False,
            'data': {
                'source': 'not_found',
                'is_new': False,
                'book_id': None,
                'book': None,
                'message': result['message'],
            }
        }, status=200)

    return Response({
        'success': True,
        'data': {
            'source': result['source'],
            'is_new': result['is_new'],
            'book_id': result['book_id'],
            'book': result.get('book'),
            'message': result['message'],
        }
    }, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_favorites_api(request):
    """
    獲取當前使用者的收藏書籍列表 / Get current user's favorite books
    需要登入 / Requires authentication

    Response (200):
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "book": {
                    "id": 1,
                    "title": "書名",
                    "author_display": "作者",
                    "cover_image_url": "..."
                },
                "listing": {
                    "id": 1,
                    "used_price": 350,
                    "status": "PUBLISHED"
                } or null,
                "created_at": "ISO datetime"
            }
        ]
    }
    """
    try:
        from listings.models import Listing

        # 獲取使用者的所有收藏
        favorites = BookFavorite.objects.filter(
            user=request.user
        ).select_related('book').order_by('-created_at')

        data = []
        for fav in favorites:
            # 找到這本書最新的已發佈刊登
            listing = Listing.objects.filter(
                book=fav.book,
                status='PUBLISHED'
            ).select_related('seller__profile').first()

            fav_data = {
                'id': fav.id,
                'book': {
                    'id': fav.book.id,
                    'title': fav.book.title,
                    'author_display': fav.book.author_display or '',
                    'cover_image_url': fav.book.cover_image_url,
                },
                'listing': None,
                'created_at': fav.created_at.isoformat(),
            }

            if listing:
                fav_data['listing'] = {
                    'id': listing.id,
                    'used_price': float(listing.used_price),
                    'status': listing.status,
                }

            data.append(fav_data)

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
                'message': f'無法載入收藏列表: {str(e)}'
            }
        }, status=400)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_toggle_api(request, book_id):
    """
    添加或移除書籍收藏 / Add or remove book favorite
    需要登入 / Requires authentication

    POST: 添加收藏 / Add favorite
    DELETE: 移除收藏 / Remove favorite

    Response (201/204):
    {
        "success": true,
        "data": { "id": 1, "book_id": 1 }
    }
    """
    try:
        book = Book.objects.get(id=book_id)

        if request.method == 'POST':
            favorite, created = BookFavorite.objects.get_or_create(
                user=request.user,
                book=book
            )

            if created:
                return Response({
                    'success': True,
                    'data': {
                        'id': favorite.id,
                        'book_id': book.id
                    }
                }, status=201)
            else:
                return Response({
                    'success': True,
                    'message': '已收藏',
                    'data': {
                        'id': favorite.id,
                        'book_id': book.id
                    }
                }, status=200)

        elif request.method == 'DELETE':
            deleted_count, _ = BookFavorite.objects.filter(
                user=request.user,
                book=book
            ).delete()

            if deleted_count > 0:
                return Response({
                    'success': True,
                    'message': '已移除收藏'
                }, status=200)
            else:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': '收藏不存在'
                    }
                }, status=404)

    except Book.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '書籍不存在'
            }
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            }
        }, status=400)
