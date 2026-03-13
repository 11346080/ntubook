from django.db import models

class Book(models.Model):
    title = models.CharField("書名", max_length=255)
    author_display = models.CharField("作者", max_length=255)
    isbn13 = models.CharField("ISBN-13", max_length=13, unique=True)
    isbn10 = models.CharField("ISBN-10", max_length=10, blank=True, null=True)
    publisher = models.CharField("出版社", max_length=100)
    publication_date = models.CharField("出版日期", max_length=50, blank=True, null=True)
    edition = models.CharField("版本", max_length=50, blank=True, null=True)
    cover_image_url = models.URLField("封面圖片連結", blank=True, null=True)

    def __str__(self):
        return self.title

class BookApplicability(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='applicabilities', verbose_name="書籍")
    department = models.ForeignKey('core.Department', on_delete=models.CASCADE, verbose_name="適用系所")
    course_name = models.CharField("課程名稱", max_length=100)

    def __str__(self):
        return f"{self.book.title} - {self.course_name}"