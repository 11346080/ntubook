from django.contrib import admin
from .models import ProgramType, Department, ClassGroup


@admin.register(ProgramType)
class ProgramTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_zh', 'name_en', 'is_active', 'sort_order']
    search_fields = ['code', 'name_zh', 'name_en']
    list_filter = ['is_active']
    ordering = ['sort_order', 'code']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_zh', 'program_type', 'is_active']
    search_fields = ['code', 'name_zh']
    list_filter = ['is_active', 'program_type']
    ordering = ['code']


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_zh', 'department', 'grade_no', 'section_code', 'is_active']
    search_fields = ['code', 'name_zh']
    list_filter = ['is_active', 'program_type', 'grade_no']
    ordering = ['code']
