from django.db import models
from core.models import ClassGroup

class Book(models.Model):
    isbn13 = models.CharField('ISBN-13', max_length=13, unique=True)
    isbn10 = models.CharField('ISBN-10', max_length=10, blank=True, null=True)
    title = models.CharField('書名', max_length=255)
    author_display = models.CharField('作者', max_length=255)
    publisher = models.CharField('出版社', max_length=255)
    publication_date = models.CharField('出版日期', max_length=50, blank=True, null=True) # 使用字串保留格式彈性
    edition = models.CharField('版本', max_length=50, blank=True, null=True)
    cover_image_url = models.URLField('封面圖片連結', blank=True, null=True)

    class Meta:
        verbose_name = '書籍庫'
        verbose_name_plural = '1. 書籍庫'

    def __str__(self):
        return self.title

class BookApplicability(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='applicabilities', verbose_name='書籍')
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, verbose_name='適用班級')
    course_name = models.CharField('課程名稱', max_length=100)

    class Meta:
        verbose_name = '適用課程'
        verbose_name_plural = '2. 適用課程'

    def __str__(self):
        return f"{self.book.title} - {self.course_name}"