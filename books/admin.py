from django.contrib import admin
from .models import Book, BookApplicability, BookFavorite


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'isbn13', 'title', 'author_display', 'publisher', 'metadata_source', 'metadata_status']
    search_fields = ['isbn13', 'isbn10', 'title', 'author_display', 'publisher']
    list_filter = ['metadata_source', 'metadata_status', 'language_code']


@admin.register(BookApplicability)
class BookApplicabilityAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'academic_year', 'term', 'class_group', 'source_type']
    search_fields = ['book__title', 'book__isbn13']
    list_filter = ['source_type', 'academic_year', 'term', 'class_group__program_type']


@admin.register(BookFavorite)
class BookFavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'book', 'created_at']
    search_fields = ['user__username', 'book__title', 'book__isbn13']
    list_filter = ['book__metadata_status']
