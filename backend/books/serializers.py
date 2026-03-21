from rest_framework import serializers
from .models import Book, BookApplicability


class BookSerializer(serializers.ModelSerializer):
    """書籍序列化器 / Book Serializer"""

    class Meta:
        model = Book
        fields = '__all__'


class BookApplicabilitySerializer(serializers.ModelSerializer):
    """書籍適用對象序列化器 / Book Applicability Serializer"""

    class Meta:
        model = BookApplicability
        fields = '__all__'
