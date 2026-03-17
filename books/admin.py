from django.contrib import admin
from .models import Book, BookApplicability

# class BookApplicabilityInline(admin.TabularInline):
#     model = BookApplicability
#     extra = 1
# TODO: 效能問題隔離測試 - 先註冊 BookAdmin 觀察是否正常運作

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_display', 'isbn13', 'publisher')
    search_fields = ('title', 'author_display', 'isbn13', 'isbn10')
    # inlines = [BookApplicabilityInline]  # 暫時移除以測試效能問題