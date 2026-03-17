from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseRequest, Listing
from notifications.models import Notification
from books.models import BookApplicability

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
            
@receiver(post_save, sender=PurchaseRequest)
def finalize_transaction_on_completion(sender, instance, **kwargs):
    """
    當預約請求狀態變為「已完成」(COMPLETED) 時：
    1. 自動將刊登狀態改為「已售出/下架」(OFF_SHELF)。
    2. 發送成交感謝通知給買賣雙方。
    """
    if instance.status == 'COMPLETED':
        listing = instance.listing
        if listing.status != 'OFF_SHELF':
            listing.status = 'OFF_SHELF'
            listing.save()
            
            # 自動通知賣家成交
            Notification.objects.create(
                user=listing.seller,
                type_code='SYSTEM',
                title='交易成功！',
                message=f'您的書籍《{listing.book.title}》已完成交易，系統已自動將其下架。'
            )
            
@receiver(post_save, sender=Listing)
def auto_create_book_applicability(sender, instance, created, **kwargs):
    """
    當「刊登」建立時，自動補入「書籍適用班級」資料。
    """
    # 只有在新建刊登，且有填寫班級、學年、學期資訊時才執行
    if created and instance.origin_class_group and instance.origin_academic_year and instance.origin_term:
        # 使用 update_or_create 確保唯一性 (book, academic_year, term, class_group)
        BookApplicability.objects.update_or_create(
            book=instance.book,
            academic_year=instance.origin_academic_year,
            term=instance.origin_term,
            class_group=instance.origin_class_group,
            defaults={
                'source_type': 'FROM_LISTING', # 標記來源
                'source_listing_id': instance.id
            }
        )