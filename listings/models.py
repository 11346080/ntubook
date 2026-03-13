from django.db import models
from django.conf import settings

class Listing(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', '草稿'), ('PENDING', '審核中'), ('PUBLISHED', '已上架'),
        ('RESERVED', '已保留'), ('SOLD', '已售出'), ('OFF_SHELF', '已下架')
    ]
    CONDITION_CHOICES = [
        ('NEW', '全新'), ('GOOD', '良好'), ('FAIR', '普通'), ('POOR', '較差')
    ]

    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, related_name='listings')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    
    # 課程資訊
    origin_academic_year = models.IntegerField("開課學年")
    origin_term = models.IntegerField("開課學期")
    origin_class_group = models.ForeignKey('core.ClassGroup', on_delete=models.SET_NULL, null=True)
    
    # 銷售資訊
    used_price = models.DecimalField("二手價", max_digits=8, decimal_places=0)
    condition_level = models.CharField("書況", max_length=10, choices=CONDITION_CHOICES)
    description = models.TextField("商品說明", blank=True, null=True)
    seller_note = models.TextField("賣家備註", blank=True, null=True)
    status = models.CharField("狀態", max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField("刪除時間(軟刪除)", blank=True, null=True)

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing_images')
    file_path = models.URLField("圖片連結或路徑")
    is_primary = models.BooleanField("是否為封面", default=False)
    sort_order = models.IntegerField("排序", default=0)

class BookFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '待處理'),
        ('accepted', '已接受'),
        ('rejected', '已拒絕'),
        ('completed', '已完成'),
        ('canceled', '已取消'),
    ]

    # 哪一筆刊登
    listing = models.ForeignKey(
        'Listing', 
        on_delete=models.CASCADE, 
        related_name='purchase_requests',
        verbose_name="刊登商品"
    )
    
    # 誰提出購買
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='purchase_requests',
        verbose_name="買家"
    )
    
    # 買家可以留一段訊息給賣家
    message = models.TextField("留言訊息", blank=True)
    
    # 請求的狀態
    status = models.CharField("狀態", max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 時間戳記
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

    def __str__(self):
        return f"{self.buyer.username} 預約了 {self.listing.book.title}"
    
    class Meta:
        verbose_name = "預約請求"
        verbose_name_plural = "預約請求"