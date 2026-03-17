from django.contrib import admin
from .models import ProgramType, Department, ClassGroup

@admin.register(ProgramType)
class ProgramTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_zh')
    search_fields = ('code', 'name_zh')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_zh', 'program_type')
    list_filter = ('program_type',)
    search_fields = ('code', 'name_zh')

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_zh', 'department')
    list_filter = ('department__program_type', 'department')
    search_fields = ('code', 'name_zh')