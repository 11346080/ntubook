from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

# 將 Profile 嵌進 User 的編輯頁面中
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '詳細個人資料'
    
    # 修正 1：確保這裡有 autocomplete
    autocomplete_fields = ['department'] 

    # 修正 2：直接覆寫查詢邏輯，強迫它只抓必要的資料
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')
    
class UserProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ['department'] # 把它變成搜尋選單

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'is_staff', 'account_status')
    list_filter = ('account_status', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    actions = ['make_suspended', 'make_active']
    
    # def get_queryset(self, request):
    #     return super().get_queryset(request).prefetch_related('userprofile__department')

    # 表單分組設定
    fieldsets = UserAdmin.fieldsets + (
        ('平台自訂權限', {'fields': ('account_status',)}),
    )

    @admin.action(description='批次停權選取的使用者')
    def make_suspended(self, request, queryset):
        updated = queryset.update(account_status='SUSPENDED')
        self.message_user(request, f'成功將 {updated} 名使用者設為停權。')

    @admin.action(description='批次啟用選取的使用者')
    def make_active(self, request, queryset):
        updated = queryset.update(account_status='ACTIVE')
        self.message_user(request, f'成功將 {updated} 名使用者設為啟用。')