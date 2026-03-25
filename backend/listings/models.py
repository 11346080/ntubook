from django.conf import settings
from django.db import models


class Listing(models.Model):
    """刊登資料 / Listing"""

    class ConditionLevel(models.TextChoices):
        LIKE_NEW = 'LIKE_NEW', '幾全新'
        GOOD = 'GOOD', '良好'
        FAIR = 'FAIR', '普通'
        POOR = 'POOR', '差'

    class Status(models.TextChoices):
        PENDING = 'PENDING', '待審核'
        AVAILABLE = 'AVAILABLE', '可購買'
        RESERVED = 'RESERVED', '已保留'
        SOLD = 'SOLD', '已售出'
        OFF_SHELF = 'OFF_SHELF', '已下架'
        REJECTED = 'REJECTED', '已退回'
        REMOVED = 'REMOVED', '已移除'
        DELETED = 'DELETED', '已刪除'

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
        verbose_name='賣家'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='listings',
        verbose_name='書籍'
    )
    origin_academic_year = models.PositiveSmallIntegerField(verbose_name='原使用學年')
    origin_term = models.PositiveSmallIntegerField(verbose_name='原使用學期')
    origin_class_group = models.ForeignKey(
        'core.ClassGroup',
        on_delete=models.RESTRICT,
        related_name='origin_listings',
        verbose_name='原使用班級'
    )
    used_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='二手價'
    )
    condition_level = models.CharField(
        max_length=20,
        choices=ConditionLevel.choices,
        default=ConditionLevel.GOOD,
        verbose_name='書況等級'
    )
    description = models.TextField(blank=True, null=True, verbose_name='商品描述')
    seller_note = models.TextField(blank=True, null=True, verbose_name='賣家備註')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='刊登狀態'
    )
    off_shelf_reason = models.CharField(max_length=255, blank=True, null=True, verbose_name='下架原因')
    reject_reason = models.CharField(max_length=500, blank=True, null=True, verbose_name='退回原因')
    accepted_request = models.ForeignKey(
        'purchase_requests.PurchaseRequest',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='accepted_listing',
        verbose_name='已接受請求'
    )
    risk_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='驗證風險分數'
    )
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='軟刪除時間')
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='deleted_listings',
        verbose_name='刪除者'
    )
    reserved_at = models.DateTimeField(blank=True, null=True, verbose_name='保留時間')
    sold_at = models.DateTimeField(blank=True, null=True, verbose_name='售出時間')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        db_table = 'listings'
        verbose_name = '刊登'
        verbose_name_plural = '刊登'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', 'status', 'created_at'], name='listings_seller_status_idx'),
            models.Index(fields=['book', 'status', 'created_at'], name='listings_book_status_idx'),
            models.Index(fields=['status', 'created_at'], name='listings_status_created_idx'),
            models.Index(fields=['origin_class_group', 'origin_academic_year', 'origin_term'], name='listings_origin_cohort_idx'),
            models.Index(fields=['deleted_at'], name='listings_deleted_at_idx'),
        ]

    def __str__(self):
        return f"[{self.id}] {self.book.title} @ {self.used_price}"


class ListingImage(models.Model):
    """刊登圖片 / Listing Image"""

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='刊登'
    )
    file_name = models.CharField(max_length=255, default='', verbose_name='原檔案名稱')
    image_binary = models.BinaryField(verbose_name='圖片二進制數據', default=b'')
    mime_type = models.CharField(max_length=50, default='image/jpeg', verbose_name='MIME 類型')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='排序值')
    is_primary = models.BooleanField(default=False, verbose_name='是否為首圖')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    class Meta:
        db_table = 'listing_images'
        verbose_name = '刊登圖片'
        verbose_name_plural = '刊登圖片'
        ordering = ['listing', 'sort_order']
        indexes = [
            models.Index(fields=['listing', 'sort_order'], name='listing_img_listing_sort_idx'),
            models.Index(fields=['listing', 'is_primary'], name='listing_img_primary_idx'),
        ]

    def __str__(self):
        return f"{self.listing.id} - {self.file_name}"
