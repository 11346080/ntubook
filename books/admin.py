from django.contrib import admin
from .models import Book, BookApplicability

class BookApplicabilityInline(admin.TabularInline):
    model = BookApplicability
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_display', 'isbn13', 'publisher')
    search_fields = ('title', 'author_display', 'isbn13', 'isbn10')
    inlines = [BookApplicabilityInline] # 可以在編輯書本時，直接新增適用課程

