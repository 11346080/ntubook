from django.contrib import admin

from .models import Campus, ProgramType, Department, ClassGroup, StudentNumberRule
from ntub_usedbooks.admin import ntub_admin_site


class CampusAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name_zh', 'short_name', 'is_active', 'sort_order', 'created_at']
    search_fields = ['code', 'name_zh', 'short_name']
    list_filter = ['is_active']
    ordering = ['sort_order', 'code']
    list_per_page = 100
    readonly_fields = ['created_at', 'updated_at']


class ProgramTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name_zh', 'is_active', 'sort_order', 'created_at']
    search_fields = ['code', 'name_zh', 'name_en']
    list_filter = ['is_active']
    ordering = ['sort_order', 'code']
    list_per_page = 100
    readonly_fields = ['created_at', 'updated_at']


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name_zh', 'campus', 'program_type', 'is_active', 'created_at']
    search_fields = ['code', 'name_zh', 'name_en']
    list_filter = ['is_active', 'program_type', 'campus']
    ordering = ['program_type__code', 'code']
    list_per_page = 100
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['campus', 'program_type']


class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name_zh', 'department', 'grade_no', 'section_code', 'is_active', 'created_at']
    search_fields = ['code', 'name_zh']
    list_filter = ['is_active', 'grade_no', 'department__program_type', 'department__campus']
    ordering = ['department__program_type__code', 'department__code', 'grade_no', 'section_code']
    list_per_page = 100
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['department']


class StudentNumberRuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'program_type', 'department', 'admission_year_digits', 'note', 'is_active', 'created_at']
    search_fields = ['department__code', 'department__name_zh', 'note']
    list_filter = ['is_active', 'program_type']
    ordering = ['program_type__sort_order', 'department__code']
    list_per_page = 100
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['program_type', 'department']


ntub_admin_site.register(Campus, CampusAdmin)
ntub_admin_site.register(ProgramType, ProgramTypeAdmin)
ntub_admin_site.register(Department, DepartmentAdmin)
ntub_admin_site.register(ClassGroup, ClassGroupAdmin)
ntub_admin_site.register(StudentNumberRule, StudentNumberRuleAdmin)
