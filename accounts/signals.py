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
        
        # 找出這個賣家所有「上架中」(AVAILABLE) 的書，一次性批次更新為「下架」(OFF_SHELF)
        Listing.objects.filter(
            seller=instance, 
            status='AVAILABLE'
        ).update(status='OFF_SHELF')