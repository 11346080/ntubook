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
        # 從 Listing 的現有欄位組出 course_name
        course_name = f"{instance.origin_academic_year}學年度第{instance.origin_term}學期 {instance.origin_class_group.name_zh}"
        BookApplicability.objects.update_or_create(
            book=instance.book,
            class_group=instance.origin_class_group,
            defaults={
                'course_name': course_name,
            }
        )