from django.contrib import admin
from .models import ProgramType, Department, ClassGroup

@admin.register(ProgramType)
class ProgramTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_zh')
    search_fields = ('code', 'name_zh')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    # 必須保留 search_fields，UserProfileInline 的 autocomplete 才能運作
    list_display = ('code', 'name_zh', 'program_type')
    list_filter = ('program_type',)
    search_fields = ('code', 'name_zh') 

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_zh', 'department')
    list_filter = ('department__program_type', 'department')
    search_fields = ('code', 'name_zh')
    # 如果新增班級也要選系所，這裡也建議加上
    autocomplete_fields = ['department']