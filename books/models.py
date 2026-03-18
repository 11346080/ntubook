from django.conf import settings
from django.db import models


class Book(models.Model):
    """書籍主檔 / Book"""

    class MetadataSource(models.TextChoices):
        GOOGLE_BOOKS = 'GOOGLE_BOOKS', 'Google Books'
        MANUAL = 'MANUAL', '手動輸入'
        LOCAL = 'LOCAL', '本地資料'

    class MetadataStatus(models.TextChoices):
        AUTO_IMPORTED = 'AUTO_IMPORTED', '自動匯入'
        MANUALLY_CONFIRMED = 'MANUALLY_CONFIRMED', '已手動確認'
        NEEDS_REVIEW = 'NEEDS_REVIEW', '需審核'

    isbn13 = models.CharField(max_length=20, unique=True, verbose_name='ISBN-13')
    isbn10 = models.CharField(max_length=20, blank=True, null=True, verbose_name='ISBN-10')
    title = models.CharField(max_length=255, verbose_name='書名')
    author_display = models.CharField(max_length=255, verbose_name='作者')
    publisher = models.CharField(max_length=255, verbose_name='出版社')
    publication_date = models.DateField(blank=True, null=True, verbose_name='出版日期')
    publication_date_text = models.CharField(max_length=50, blank=True, null=True, verbose_name='出版日期原始字串')
    edition = models.CharField(max_length=50, blank=True, null=True, verbose_name='版次')
    language_code = models.CharField(max_length=20, default='zh-TW', verbose_name='語言代碼')
    cover_image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='封面圖片')
    metadata_source = models.CharField(
        max_length=30,
        choices=MetadataSource.choices,
        default=MetadataSource.MANUAL,
        verbose_name='書目資料來源'
    )
    metadata_status = models.CharField(
        max_length=30,
        choices=MetadataStatus.choices,
        default=MetadataStatus.NEEDS_REVIEW,
        verbose_name='書目狀態'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        db_table = 'books'
        verbose_name = '書籍'
        verbose_name_plural = '書籍'
        ordering = ['title']
        indexes = [
            models.Index(fields=['isbn10'], name='books_isbn10_idx'),
            models.Index(fields=['title'], name='books_title_idx'),
            models.Index(fields=['author_display'], name='books_author_idx'),
            models.Index(fields=['publisher'], name='books_publisher_idx'),
        ]

    def __str__(self):
        return f"{self.isbn13} - {self.title}"


class BookApplicability(models.Model):
    """書籍適用對象 / Book Applicability"""

    class SourceType(models.TextChoices):
        FROM_LISTING = 'FROM_LISTING', '來自刊登'
        ADMIN_CURATED = 'ADMIN_CURATED', '管理員精選'

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='applicabilities',
        verbose_name='書籍'
    )
    academic_year = models.PositiveSmallIntegerField(verbose_name='學年')
    term = models.PositiveSmallIntegerField(verbose_name='學期')
    class_group = models.ForeignKey(
        'core.ClassGroup',
        on_delete=models.CASCADE,
        related_name='book_applicabilities',
        verbose_name='班級'
    )
    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.ADMIN_CURATED,
        verbose_name='來源類型'
    )
    source_listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='applicabilities',
        verbose_name='來源刊登'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        db_table = 'book_applicabilities'
        verbose_name = '書籍適用對象'
        verbose_name_plural = '書籍適用對象'
        ordering = ['book', 'academic_year', 'term']
        unique_together = [['book', 'academic_year', 'term', 'class_group']]
        indexes = [
            models.Index(fields=['class_group', 'academic_year', 'term'], name='book_app_class_yr_term_idx'),
            models.Index(fields=['book', 'academic_year', 'term'], name='book_app_book_yr_term_idx'),
        ]

    def __str__(self):
        return f"{self.book.title} - {self.academic_year}/{self.term} - {self.class_group.code}"


class BookFavorite(models.Model):
    """書籍收藏 / Book Favorite"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_favorites',
        verbose_name='使用者'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='書籍'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    class Meta:
        db_table = 'book_favorites'
        verbose_name = '書籍收藏'
        verbose_name_plural = '書籍收藏'
        ordering = ['-created_at']
        unique_together = [['user', 'book']]
        indexes = [
            models.Index(fields=['book', 'created_at'], name='book_fav_book_created_idx'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
