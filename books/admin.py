from django.contrib import admin
from .models import Book, BookApplicability

admin.site.register(Book)
admin.site.register(BookApplicability)