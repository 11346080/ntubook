from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'student_no', 'program_type', 'department', 'class_group', 'grade_no']
    search_fields = ['user__username', 'user__email', 'display_name', 'student_no']
    list_filter = ['program_type', 'department', 'grade_no']
