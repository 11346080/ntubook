from django.contrib import admin
from django import forms
from .models import Book, BookApplicability

class BookAdminForm(forms.ModelForm):
    """Book 表單驗證：最小化 ISBN 格式驗證"""
    class Meta:
        model = Book
        fields = '__all__'

    def clean_isbn13(self):
        isbn13 = self.cleaned_data.get('isbn13')
        if isbn13:
            # 最小驗證：必須是 13 碼數字
            if len(isbn13) != 13 or not isbn13.isdigit():
                raise forms.ValidationError('ISBN-13 必須是 13 碼數字')
        return isbn13

    def clean_isbn10(self):
        isbn10 = self.cleaned_data.get('isbn10')
        if isbn10:
            # 最小驗證：必須是 10 碼（允許結尾為 X）
            if len(isbn10) != 10:
                raise forms.ValidationError('ISBN-10 必須是 10 碼')
            # 檢查是否為數字或最後一碼為 X
            if not (isbn10[:-1].isdigit() and (isbn10[-1].isdigit() or isbn10[-1].upper() == 'X')):
                raise forms.ValidationError('ISBN-10 格式必須符合規範（前9碼為數字，第10碼可為數字或X）')
        return isbn10

class BookApplicabilityInline(admin.TabularInline):
    model = BookApplicability
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookAdminForm
    list_display = ('title', 'author_display', 'isbn13', 'publisher')
    search_fields = ('title', 'author_display', 'isbn13', 'isbn10')
    list_filter = ('publisher',)
    ordering = ('title',)
    list_per_page = 25
    inlines = [BookApplicabilityInline]

    # fieldsets 分組
    fieldsets = (
        ('基本識別', {
            'fields': ('isbn13', 'isbn10', 'title', 'author_display')
        }),
        ('出版資訊', {
            'fields': ('publisher', 'publication_date', 'edition')
        }),
        ('其他資訊', {
            'fields': ('cover_image_url',),
            'classes': ('collapse',)
        }),
    )

    actions = ['export_as_csv']

    @admin.action(description='匯出為 CSV')
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="books.csv"'
        writer = csv.writer(response)
        writer.writerow(['isbn13', 'isbn10', 'title', 'author_display', 'publisher', 'publication_date', 'edition'])
        for obj in queryset:
            writer.writerow([obj.isbn13, obj.isbn10, obj.title, obj.author_display, obj.publisher, obj.publication_date, obj.edition])
        return response
