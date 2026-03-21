from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Listing
from books.models import BookApplicability
from notifications.models import Notification


@receiver(pre_save, sender=Listing)
def cache_listing_previous_status(sender, instance, **kwargs):
    """
    在 Listing.save() 之前，從 DB 查詢舊值並暫存。
    """
    if instance.pk is None:
        return
    try:
        old = Listing.objects.get(pk=instance.pk)
        instance._previous_status = old.status
    except Listing.DoesNotExist:
        pass


@receiver(post_save, sender=Listing)
def sync_book_applicability_on_listing_create(sender, instance, created, **kwargs):
    """
    Listing 建立且 origin_class_group 存在時，
    自動在 BookApplicability 中建立或更新記錄（來源 = FROM_LISTING）。
    """
    if not created:
        return
    if instance.origin_class_group_id is None:
        return

    BookApplicability.objects.get_or_create(
        book=instance.book,
        academic_year=instance.origin_academic_year,
        term=instance.origin_term,
        class_group=instance.origin_class_group,
        defaults={
            'source_type': BookApplicability.SourceType.FROM_LISTING,
            'source_listing': instance,
        },
    )


@receiver(post_save, sender=Listing)
def notify_on_listing_status_change(sender, instance, created, **kwargs):
    """
    Listing 狀態真正變更時，通知賣家。
    只在透過 .save() 變更時觸發；
    admin action 的 queryset 批次更新不觸發 post_save，不重複。
    """
    if created:
        return
    previous = getattr(instance, '_previous_status', None)
    if previous is None:
        return
    if previous == instance.status:
        return

    cfg = {
        Listing.Status.AVAILABLE: {
            'title': '刊登恢復上架通知',
            'msg': f'您的刊登「{instance.book.title[:30]}」已恢復為可購買。',
        },
        Listing.Status.RESERVED: {
            'title': '刊登保留通知',
            'msg': f'您的刊登「{instance.book.title[:30]}」已被買家保留。',
        },
        Listing.Status.SOLD: {
            'title': '刊登售出通知',
            'msg': f'恭喜！您的刊登「{instance.book.title[:30]}」已成功售出。',
        },
        Listing.Status.OFF_SHELF: {
            'title': '刊登下架通知',
            'msg': f'您的刊登「{instance.book.title[:30]}」已由您主動下架。',
        },
        Listing.Status.REMOVED: {
            'title': '刊登移除通知',
            'msg': f'您的刊登「{instance.book.title[:30]}」已被管理員移除。',
        },
    }.get(instance.status)

    if not cfg:
        return

    Notification.objects.get_or_create(
        user=instance.seller,
        type_code='LISTING_STATUS_CHANGE',
        title=cfg['title'],
        defaults={
            'message': cfg['msg'],
            'related_listing': instance,
        },
    )
