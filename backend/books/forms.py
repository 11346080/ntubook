from django import forms

from .models import Book


class BookForm(forms.ModelForm):

    publication_year = forms.IntegerField(
        required=False,
        min_value=1900,
        max_value=2100,
        widget=forms.NumberInput(attrs={
            'placeholder': '例：2024',
            'style': 'width: 120px;',
        }),
        label='出版年份',
        help_text='僅填入西元年份，如 2024',
    )

    class Meta:
        model = Book
        fields = [
            'isbn13', 'isbn10',
            'title', 'author_display', 'publisher',
            'publication_year',
            'edition', 'language_code',
            'cover_image_url',
            'metadata_source', 'metadata_status',
        ]
