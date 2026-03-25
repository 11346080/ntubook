from rest_framework import serializers
from .models import Listing, ListingImage
import base64

# 敏感詞清單（繁體中文）- 與前端一致
SENSITIVE_WORDS = [
    # 賭博相關
    '博彩', '賭博', '賭錢', '娛樂城',
    # 毒品相關
    '毒品', '大麻', '海洛因', '冰毒', '搖頭丸',
    # 色情相關
    '色情', '淫穢', '黃色', '18禁',
    # 暴力相關
    '暴力', '恐怖', '炸彈', '槍支',
    # 詐騙相關
    '詐騙', '欺詐', '洗錢', '非法',
    # 違法相關
    '走私', '販毒', '販運',
    # 仇恨相關
    '仇恨', '歧視', '恐怖分子',
    # 平台特定的敏感詞
    '假貨', '假冒', '翻新', '來路不明',
]

def check_sensitive_words(text: str) -> list:
    """檢查文本中的敏感詞，返回找到的敏感詞列表"""
    if not text:
        return []
    
    found_words = []
    lower_text = text.lower()
    
    for word in SENSITIVE_WORDS:
        if word.lower() in lower_text:
            if word not in found_words:
                found_words.append(word)
    
    return found_words


class ListingImageSerializer(serializers.ModelSerializer):
    """刊登圖片序列化器 / Listing Image Serializer - 返回 base64 編碼的圖片"""
    
    image_base64 = serializers.SerializerMethodField()

    class Meta:
        model = ListingImage
        fields = ['id', 'image_base64', 'mime_type', 'file_name', 'is_primary', 'sort_order']
    
    def get_image_base64(self, obj):
        """將二進制圖片轉換為 base64 data URL"""
        if obj.image_binary:
            encoded = base64.b64encode(obj.image_binary).decode('utf-8')
            # 返回 data URL 格式，前端可直接用到 <img src=...>
            return f"data:{obj.mime_type};base64,{encoded}"
        return None


class BookListingSerializer(serializers.Serializer):
    """書籍基本資訊序列化器 - 用於刊登列表 / Book Basic Info for Listing"""
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    author_display = serializers.CharField(max_length=255)
    isbn13 = serializers.CharField(max_length=20)
    isbn10 = serializers.CharField(allow_null=True)
    cover_image_url = serializers.URLField(allow_null=True)


class SellerBasicSerializer(serializers.Serializer):
    """賣家基本資訊序列化器 / Seller Basic Info"""
    id = serializers.IntegerField()
    display_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    def get_display_name(self, obj):
        """安全地取得賣家顯示名稱"""
        try:
            return obj.profile.display_name if obj.profile else '匿名賣家'
        except:
            return '匿名賣家'

    def get_department(self, obj):
        """安全地取得賣家系所（提供 name_zh）"""
        try:
            if obj.profile and obj.profile.department:
                return {
                    'id': obj.profile.department.id,
                    'name_zh': obj.profile.department.name_zh,
                }
            return None
        except:
            return None


class ListingSerializer(serializers.ModelSerializer):
    """刊登序列化器 - 列表視圖用 / Listing Serializer for List View"""
    
    # 嵌套序列化器 / Nested Serializers
    book = BookListingSerializer(read_only=True)
    seller = SellerBasicSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    condition_level_display = serializers.CharField(source='get_condition_level_display', read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'book',
            'seller',
            'used_price',
            'condition_level',
            'condition_level_display',
            'description',
            'seller_note',
            'status',
            'primary_image',
            'created_at',
            'updated_at',
        ]

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
        except:
            return None


class ListingDetailSerializer(serializers.ModelSerializer):
    """刊登詳情序列化器 - 詳情頁視圖用 / Listing Detail Serializer for Detail View"""
    
    # 嵌套序列化器 / Nested Serializers
    book = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    images = ListingImageSerializer(many=True, read_only=True)
    condition_level_display = serializers.CharField(source='get_condition_level_display', read_only=True)
    origin_class_group = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'book',
            'seller',
            'used_price',
            'condition_level',
            'condition_level_display',
            'description',
            'seller_note',
            'status',
            'origin_academic_year',
            'origin_term',
            'origin_class_group',
            'images',
            'created_at',
            'updated_at',
        ]

    def get_book(self, obj):
        """取得完整書籍資訊 / Get full book info"""
        try:
            if not obj.book:
                return None
            return {
                'id': obj.book.id,
                'title': obj.book.title,
                'author_display': obj.book.author_display,
                'isbn13': obj.book.isbn13,
                'isbn10': obj.book.isbn10,
                'publisher': obj.book.publisher,
                'publication_year': obj.book.publication_year,
                'publication_date_text': obj.book.publication_date_text,
                'edition': obj.book.edition,
                'cover_image_url': obj.book.cover_image_url,
            }
        except:
            return None

    def get_seller(self, obj):
        """取得完整賣家資訊 / Get full seller info"""
        try:
            if not obj.seller:
                return None
            seller_data = {
                'id': obj.seller.id,
                'display_name': obj.seller.profile.display_name if obj.seller.profile else '匿名賣家',
                'department': None,
            }
            if obj.seller.profile and obj.seller.profile.department:
                seller_data['department'] = {
                    'id': obj.seller.profile.department.id,
                    'name_zh': obj.seller.profile.department.name_zh,
                }
            return seller_data
        except:
            return {'id': obj.seller.id if obj.seller else None, 'display_name': '匿名賣家', 'department': None}

    def get_origin_class_group(self, obj):
        """取得原使用班級資訊 / Get origin class group info"""
        try:
            if not obj.origin_class_group:
                return None
            return {
                'id': obj.origin_class_group.id,
                'code': obj.origin_class_group.code,
                'name_zh': obj.origin_class_group.name_zh,
                'department': {
                    'id': obj.origin_class_group.department.id,
                    'code': obj.origin_class_group.department.code,
                    'name_zh': obj.origin_class_group.department.name_zh,
                } if obj.origin_class_group.department else None,
            }
        except:
            return None


class ListingLatestSerializer(serializers.ModelSerializer):
    """首頁最新刊登序列化器 / Listing Latest Serializer for Homepage"""

    book_title = serializers.SerializerMethodField()
    book_author = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    # used_price: Decimal → 字串，去尾端 .00（e.g. "350" 而非 "350.00"）
    used_price = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id',
            'book_title',
            'book_author',
            'cover_image_url',
            'used_price',
            'condition_level',
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

    def get_used_price(self, obj):
        """將 Decimal 轉為整數字串，去尾端 .00"""
        price = float(obj.used_price)
        if price == int(price):
            return str(int(price))
        return str(price)

    def get_primary_image(self, obj):
        """取得首圖 / Get primary image"""
        try:
            primary_image = obj.images.filter(is_primary=True).first()
            if primary_image:
                return ListingImageSerializer(primary_image).data
            first_image = obj.images.order_by('sort_order').first()
            if first_image:
                return ListingImageSerializer(first_image).data
            return None
        except:
            return None


# ================= 創建刊登序列化器 =================

class NewBookSerializer(serializers.Serializer):
    """新增書籍序列化器 / New Book Serializer - 用於建立刊登時新增書籍"""
    isbn13 = serializers.CharField(max_length=20, required=False, allow_blank=True)
    isbn10 = serializers.CharField(max_length=20, required=False, allow_blank=True)
    title = serializers.CharField(max_length=255, required=True)
    author_display = serializers.CharField(max_length=255, required=True)
    publisher = serializers.CharField(max_length=255, required=True)
    publication_date_text = serializers.CharField(max_length=50, required=False, allow_blank=True)
    publication_year = serializers.IntegerField(required=False, allow_null=True)


class ListingCreateSerializer(serializers.Serializer):
    """創建刊登序列化器 / Listing Create Serializer"""
    
    # 書籍部分
    book_id = serializers.IntegerField(required=False, allow_null=True)
    new_book = NewBookSerializer(required=False, allow_null=True)
    
    # 刊登資訊（皆改為 optional：可由 user profile 自動帶入）
    origin_academic_year = serializers.IntegerField(required=False)
    origin_term = serializers.IntegerField(required=False, min_value=1, max_value=2)
    origin_class_group_id = serializers.IntegerField(required=False)
    
    # 定價與書況
    used_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, min_value=0)
    condition_level = serializers.CharField(
        max_length=20,
        required=True,
        help_text="LIKE_NEW | GOOD | FAIR | POOR"
    )
    
    # 描述
    description = serializers.CharField(required=False, allow_blank=True)
    seller_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # 圖片（Base64 字符串列表）
    images = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        min_length=3,
        help_text="Base64 編碼的圖片列表（至少需要3張圖片）"
    )

    def validate(self, data):
        """驗證邏輯：book_id 和 new_book 至少提供一個"""
        book_id = data.get('book_id')
        new_book = data.get('new_book')
        
        if not book_id and not new_book:
            raise serializers.ValidationError({
                'book_id': '請提供書籍 ID 或新書籍資訊',
                'new_book': '請提供書籍 ID 或新書籍資訊'
            })
        
        # 驗證 condition_level
        valid_conditions = ['LIKE_NEW', 'GOOD', 'FAIR', 'POOR']
        if data.get('condition_level') not in valid_conditions:
            raise serializers.ValidationError({
                'condition_level': f'書況等級必須為：{", ".join(valid_conditions)}'
            })
        
        # 驗證圖片（至少 3 張）
        images = data.get('images', [])
        if not images or len(images) < 3:
            raise serializers.ValidationError({
                'images': '至少需要上傳 3 張圖片'
            })
        
        # ✨ 新增：敏感詞檢查
        # 檢查 new_book 中的 title
        if new_book:
            title = new_book.get('title', '')
            sensitive_in_title = check_sensitive_words(title)
            if sensitive_in_title:
                raise serializers.ValidationError({
                    'new_book': f'用詞似有不妥，請重新斟酌筆墨...（敏感詞：{", ".join(sensitive_in_title)}）'
                })

        # 檢查 description
        description = data.get('description', '')
        sensitive_in_desc = check_sensitive_words(description)
        if sensitive_in_desc:
            raise serializers.ValidationError({
                'description': f'用詞似有不妥，請重新斟酌筆墨...（敏感詞：{", ".join(sensitive_in_desc)}）'
            })

        # ✨ 圖片格式限制：只允許 jpg / png
        images = data.get('images', [])
        allowed_mime_prefixes = ('data:image/jpeg', 'data:image/png')
        for i, img in enumerate(images, 1):
            if not any(img.startswith(prefix) for prefix in allowed_mime_prefixes):
                raise serializers.ValidationError({
                    'images': f'第 {i} 張圖片格式不符，僅支援 JPG 與 PNG'
                })

        return data
