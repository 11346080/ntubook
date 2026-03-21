from rest_framework import serializers
from .models import Listing, ListingImage


class ListingImageSerializer(serializers.ModelSerializer):
    """刊登圖片序列化器 / Listing Image Serializer"""

    class Meta:
        model = ListingImage
        fields = ['id', 'file_path', 'is_primary', 'sort_order']


class ListingSerializer(serializers.ModelSerializer):
    """刊登序列化器 / Listing Serializer"""

    class Meta:
        model = Listing
        fields = '__all__'


class ListingLatestSerializer(serializers.ModelSerializer):
    """首頁最新刊登序列化器 / Listing Latest Serializer for Homepage"""

    book_title = serializers.SerializerMethodField()
    book_author = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    seller_display_name = serializers.SerializerMethodField()
    seller_department = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id',
            'book_title',
            'book_author',
            'cover_image_url',
            'used_price',
            'condition_level',
            'seller_display_name',
            'seller_department',
            'created_at',
            'primary_image',
        ]

    def get_book_title(self, obj):
        """安全地取得書名，避免 book 為 null 的例外"""
        return obj.book.title if obj.book else '未知書籍'

    def get_book_author(self, obj):
        """安全地取得作者，避免 book 為 null 的例外"""
        return obj.book.author_display if obj.book else '未知作者'

    def get_cover_image_url(self, obj):
        """安全地取得封面 URL，允許 null"""
        return obj.book.cover_image_url if obj.book else None

    def get_seller_display_name(self, obj):
        """安全地取得賣家名稱"""
        try:
            return obj.seller.profile.display_name if obj.seller and obj.seller.profile else '匿名賣家'
        except Exception:
            return '匿名賣家'

    def get_seller_department(self, obj):
        """安全地取得賣家系所，允許 null"""
        try:
            if obj.seller and obj.seller.profile and obj.seller.profile.department:
                return obj.seller.profile.department.name_zh
            return None
        except Exception:
            return None

    def get_primary_image(self, obj):
        """取得首圖 / Get primary image"""
        try:
            primary_image = obj.images.filter(is_primary=True).first()
            if primary_image:
                return ListingImageSerializer(primary_image).data
            # 如果沒有首圖，回傳第一張圖
            first_image = obj.images.order_by('sort_order').first()
            if first_image:
                return ListingImageSerializer(first_image).data
            return None
        except Exception:
            return None
