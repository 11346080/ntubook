from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Listing
from notifications.models import Notification
from books.models import BookApplicability
            
@receiver(post_save, sender=Listing)
def auto_create_book_applicability(sender, instance, created, **kwargs):
    """
    當「刊登」建立時，自動補入「書籍適用班級」資料。
    """
    if created and instance.origin_class_group:
        BookApplicability.objects.update_or_create(
            book=instance.book,
            class_group=instance.origin_class_group,
            defaults={
                # 如果模型裡沒有 academic_year，就不要傳入
                # 如果你想紀錄課程名稱，可以嘗試加入：
                # 'course_name': f"{instance.origin_academic_year}-{instance.origin_term} 課程",
            }
        )