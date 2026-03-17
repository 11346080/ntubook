from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseRequest
from notifications.models import Notification

@receiver(post_save, sender=PurchaseRequest)
def handle_purchase_logic(sender, instance, created, **kwargs):
    # 1. 建立時通知賣家
    if created:
        Notification.objects.create(
            user=instance.listing.seller,
            type_code='SYSTEM',
            title='新的預約請求',
            message=f'買家 {instance.buyer.username} 想要預約您的《{instance.listing.book.title}》。'
        )

    # 2. 狀態變更連動 Listing 狀態
    listing = instance.listing
    if instance.status == 'ACCEPTED':
        if listing.status != 'RESERVED':
            listing.status = 'RESERVED'
            listing.save()
            
    elif instance.status == 'COMPLETED':
        if listing.status != 'SOLD':
            listing.status = 'SOLD' # 交易完成改為已售出
            listing.save()
            
    elif instance.status in ['REJECTED', 'CANCELLED_BY_BUYER', 'CANCELLED_BY_SELLER']:
        # 如果預約取消且目前刊登是保留狀態，則自動回歸上架
        if listing.status == 'RESERVED':
            listing.status = 'PUBLISHED'
            listing.save()