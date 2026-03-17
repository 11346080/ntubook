from django.db import models
from accounts.models import CustomUser
from books.models import Book
from core.models import ClassGroup

class Listing(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('PENDING', '審核中'),
        ('PUBLISHED', '上架中'),
        ('RESERVED', '已保留'),
        ('SOLD', '已售出'),
        ('OFF_SHELF', '已下架'),
    ]
    CONDITION_CHOICES = [
        ('NEW', '全新'), ('GOOD', '良好'), 
        ('FAIR', '普通'), ('POOR', '較差'),
    ]

    book = models.ForeignKey(Book, on_delete=models.RESTRICT, verbose_name='書籍')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='listings', verbose_name='賣家')
    origin_academic_year = models.PositiveSmallIntegerField('原始學年度')
    origin_term = models.PositiveSmallIntegerField('原始學期', choices=[(1, '上學期'), (2, '下學期')])
    origin_class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, verbose_name='原始課程班級')
    
    used_price = models.DecimalField('二手售價', max_digits=8, decimal_places=0)
    condition_level = models.CharField('書況等級', max_length=10, choices=CONDITION_CHOICES)
    description = models.TextField('商品說明', blank=True)
    seller_note = models.TextField('賣家備註', blank=True)
    status = models.CharField('刊登狀態', max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    created_at = models.DateTimeField('建立時間', auto_now_add=True)
    updated_at = models.DateTimeField('更新時間', auto_now=True)
    deleted_at = models.DateTimeField('刪除(下架)時間', null=True, blank=True)

    class Meta:
        verbose_name = '二手書刊登'
        verbose_name_plural = '1. 二手書刊登'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.book.title} - ${self.used_price}"

    # 衍生欄位：判斷是否可供前端搜尋展示
    @property
    def is_visible_in_search(self):
        return self.status == 'PUBLISHED' and self.deleted_at is None

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing_images', verbose_name='所屬刊登')
    file_path = models.ImageField('圖片', upload_to='listings/%Y/%m/')
    is_primary = models.BooleanField('是否為主圖', default=False)
    sort_order = models.PositiveSmallIntegerField('排序', default=0)

    class Meta:
        verbose_name = '刊登圖片'
        verbose_name_plural = '2. 刊登圖片'
        ordering = ['sort_order', '-is_primary']

class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', '待處理'), ('ACCEPTED', '已接受'), ('REJECTED', '已拒絕'),
        ('CANCELLED_BY_BUYER', '買家取消'), ('CANCELLED_BY_SELLER', '賣家取消'),
        ('EXPIRED', '已過期'),
    ]
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='purchase_requests', verbose_name='刊登商品')
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchase_requests', verbose_name='買家')
    status = models.CharField('請求狀態', max_length=20, choices=STATUS_CHOICES, default='PENDING')
    buyer_message = models.TextField('買家留言', blank=True)
    risk_score = models.DecimalField('風險分數', max_digits=5, decimal_places=2, null=True, blank=True)
    expires_at = models.DateTimeField('過期時間', null=True, blank=True)
    created_at = models.DateTimeField('建立時間', auto_now_add=True)
    responded_at = models.DateTimeField('回應時間', null=True, blank=True)

    class Meta:
        verbose_name = '預約請求'
        verbose_name_plural = '3. 預約請求'
        
class BookFavorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites', verbose_name='使用者')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='書籍')
    created_at = models.DateTimeField('收藏時間', auto_now_add=True)

    class Meta:
        verbose_name = '書籍收藏'
        verbose_name_plural = '4. 書籍收藏'
        unique_together = ('user', 'book')