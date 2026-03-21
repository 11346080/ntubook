from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Book, BookApplicability
from .serializers import BookSerializer, BookApplicabilitySerializer


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
