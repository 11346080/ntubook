from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile

# 當 CustomUser 儲存後(post_save)觸發
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    當系統中新建了一個 CustomUser 時，自動建立對應的 UserProfile
    """
    if created:  # 只有在「新增」時才觸發，修改時不觸發
        # 預設將顯示暱稱設為帳號名稱
        UserProfile.objects.create(user=instance, display_name=instance.username)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    當 CustomUser 被儲存(更新)時，也連動儲存 UserProfile
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=CustomUser)
def suspend_user_listings(sender, instance, **kwargs):
    """
    情境 2：當使用者被「停權」(SUSPENDED) 時，自動將他所有上架中的書籍強制下架
    """
    if instance.account_status == 'SUSPENDED':
        # 為了避免 Circular Import (循環匯入) 的錯誤，我們在函式內部再 import Listing
        from listings.models import Listing
        
        # 找出這個賣家所有「上架中」(PUBLISHED) 的書，一次性批次更新為「下架」(OFF_SHELF)
        Listing.objects.filter(
            seller=instance,
            status='PUBLISHED'
        ).update(status='OFF_SHELF')
        
from django.db.models.signals import post_save, pre_delete # 修改 import

@receiver(pre_delete, sender=CustomUser)
def notify_admin_on_user_delete(sender, instance, **kwargs):
    """
    當使用者帳號即將被刪除前，可以進行最後的清理或紀錄。
    """
    print(f"警告：使用者 {instance.username} 正在被刪除。")
    # 這裡可以寫入日誌或清理該使用者的私有上傳檔案