from django.contrib import admin
from .models import Book, BookApplicability

class BookApplicabilityInline(admin.TabularInline):
    model = BookApplicability
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_display', 'isbn13', 'publisher')
    search_fields = ('title', 'author_display', 'isbn13', 'isbn10')
    ordering = ('title',)
    inlines = [BookApplicabilityInline]

