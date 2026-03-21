from django.contrib import admin

from .models import ProgramType, Department, ClassGroup
from ntub_usedbooks.admin import ntub_admin_site


class ProgramTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name_zh', 'name_en', 'is_active', 'sort_order', 'created_at']
    search_fields = ['code', 'name_zh', 'name_en']
    list_filter = ['is_active']
    ordering = ['sort_order', 'code']
    list_per_page = 100
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本資訊', {
            'fields': ('code', 'name_zh', 'name_en'),
        }),
        ('系統設定', {
            'fields': ('is_active', 'sort_order'),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name_zh', 'name_en', 'program_type', 'is_active', 'created_at']
    search_fields = ['code', 'name_zh', 'name_en']
    list_filter = ['is_active', 'program_type']
    ordering = ['program_type__code', 'code']
    list_per_page = 100
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['program_type']

    fieldsets = (
        ('所屬學制', {
            'fields': ('program_type',),
        }),
        ('基本資訊', {
            'fields': ('code', 'name_zh', 'name_en'),
        }),
        ('系統設定', {
            'fields': ('is_active',),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


class ClassGroupAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'code', 'name_zh', 'grade_no', 'section_code',
        'department', 'program_type', 'is_active', 'created_at',
    ]
    search_fields = ['code', 'name_zh']
    list_filter = ['is_active', 'program_type', 'grade_no']
    ordering = ['program_type__code', 'department__code', 'grade_no', 'section_code']
    list_per_page = 100
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['program_type', 'department']

    fieldsets = (
        ('隸屬關係', {
            'fields': ('program_type', 'department'),
        }),
        ('班級資訊', {
            'fields': ('code', 'name_zh', 'grade_no', 'section_code'),
        }),
        ('系統設定', {
            'fields': ('is_active',),
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


ntub_admin_site.register(ProgramType, ProgramTypeAdmin)
ntub_admin_site.register(Department, DepartmentAdmin)
ntub_admin_site.register(ClassGroup, ClassGroupAdmin)
