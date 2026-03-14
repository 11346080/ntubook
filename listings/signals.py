from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseRequest
from notifications.models import Notification

@receiver(post_save, sender=PurchaseRequest)
def create_purchase_notification(sender, instance, created, **kwargs):
    """
    當有買家發起預約請求(PurchaseRequest)時，自動發送通知給賣家
    """
    if created:
        book_title = instance.listing.book.title
        buyer_name = instance.buyer.username
        
        # 建立一筆通知紀錄給賣家
        Notification.objects.create(
            user=instance.listing.seller,  # 接收者：賣家
            type_code='SYSTEM',            # 通知類型
            title='您有一筆新的二手書預約請求！',
            message=f'買家 {buyer_name} 想要預約您的書籍《{book_title}》。請盡快至系統查看並回覆。'
        )
        
@receiver(post_save, sender=PurchaseRequest)
def update_listing_status_on_accept(sender, instance, **kwargs):
    """
    情境 1：當預約請求被賣家「接受」(ACCEPTED) 時，自動將該二手書刊登狀態改為「保留中」(RESERVED)
    """
    # 如果這個請求的狀態變成了 ACCEPTED
    if instance.status == 'ACCEPTED':
        listing = instance.listing
        # 檢查刊登狀態，如果還不是保留中，就幫它改過去並儲存
        if listing.status != 'RESERVED':
            listing.status = 'RESERVED'
            listing.save()