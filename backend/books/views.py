from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Book, BookApplicability
from .serializers import BookSerializer, BookApplicabilitySerializer


@api_view(['GET'])
def book_list_api(request):
    """取得所有書籍的 JSON API 端點 / Get all books API endpoint"""
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def bookapplicability_list_api(request):
    """取得所有書籍適用對象的 JSON API 端點 / Get all book applicabilities API endpoint"""
    applicabilities = BookApplicability.objects.all()
    serializer = BookApplicabilitySerializer(applicabilities, many=True)
    return Response(serializer.data)
