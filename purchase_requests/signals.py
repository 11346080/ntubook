from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import PurchaseRequest
from notifications.models import Notification


@receiver(pre_save, sender=PurchaseRequest)
def cache_pr_previous_status(sender, instance, **kwargs):
    if instance.pk is None:
        return
    try:
        old = PurchaseRequest.objects.get(pk=instance.pk)
        instance._previous_status = old.status
    except PurchaseRequest.DoesNotExist:
        pass


@receiver(post_save, sender=PurchaseRequest)
def sync_timestamps_on_pr_status_change(sender, instance, created, **kwargs):
    """
    PurchaseRequest 狀態變更時，自動寫入對應時間戳記。

    採用方案 A：使用 queryset.update()，不觸發 post_save，
    避免與 notify_on_pr_status_change 搶佔 _previous_status。
    """
    if created:
        return
    previous = getattr(instance, '_previous_status', None)
    if previous is None:
        return
    if previous == instance.status:
        return

    now = timezone.now()
    kwargs_update = {'updated_at': now}

    if instance.status == PurchaseRequest.Status.ACCEPTED:
        kwargs_update['responded_at'] = now
        kwargs_update['contact_released_at'] = now
    elif instance.status == PurchaseRequest.Status.REJECTED:
        kwargs_update['responded_at'] = now
    elif instance.status in (
        PurchaseRequest.Status.CANCELLED_BY_BUYER,
        PurchaseRequest.Status.CANCELLED_BY_SELLER,
    ):
        kwargs_update['cancelled_at'] = now

    PurchaseRequest.objects.filter(pk=instance.pk).update(**kwargs_update)


@receiver(post_save, sender=PurchaseRequest)
def notify_on_pr_status_change(sender, instance, created, **kwargs):
    """
    PurchaseRequest 狀態變更時，通知買家與賣家。
    _previous_status 由 cache_pr_previous_status 在第一次 pre_save 時寫入，
    整個信號鏈中不會被覆寫（sync_timestamps 已改用 queryset.update，不觸發 signal）。
    """
    if created:
        return
    previous = getattr(instance, '_previous_status', None)
    if previous is None:
        return
    if previous == instance.status:
        return

    title = instance.listing.book.title[:30]

    cfg_map = {
        PurchaseRequest.Status.ACCEPTED: {
            'buyer_title': '預約請求已被接受',
            'buyer_msg': f'您對「{title}」的預約請求已被接受，請查看聯絡資訊完成交易。',
            'seller_title': '您已接受預約請求',
            'seller_msg': f'您已接受買家對「{title}」的預約請求。',
        },
        PurchaseRequest.Status.REJECTED: {
            'buyer_title': '預約請求已被拒絕',
            'buyer_msg': f'您對「{title}」的預約請求已被拒絕。',
            'seller_title': '您已拒絕預約請求',
            'seller_msg': f'您已拒絕買家對「{title}」的預約請求。',
        },
        PurchaseRequest.Status.CANCELLED_BY_BUYER: {
            'buyer_title': '您已取消預約請求',
            'buyer_msg': f'您已取消對「{title}」的預約請求。',
            'seller_title': '買家已取消預約請求',
            'seller_msg': f'買家已取消對「{title}」的預約請求。',
        },
        PurchaseRequest.Status.CANCELLED_BY_SELLER: {
            'buyer_title': '預約請求已被賣家取消',
            'buyer_msg': f'賣家已取消對「{title}」的預約請求。',
            'seller_title': '您已取消預約請求',
            'seller_msg': f'您已取消對「{title}」的預約請求。',
        },
        PurchaseRequest.Status.EXPIRED: {
            'buyer_title': '預約請求已過期',
            'buyer_msg': f'您對「{title}」的預約請求已過期。',
            'seller_title': '預約請求已過期',
            'seller_msg': f'買家對「{title}」的預約請求已過期。',
        },
    }

    cfg = cfg_map.get(instance.status)
    if not cfg:
        return

    Notification.objects.get_or_create(
        user=instance.buyer,
        type_code='PURCHASE_REQUEST_STATUS_CHANGE',
        title=cfg['buyer_title'],
        defaults={
            'message': cfg['buyer_msg'],
            'related_listing': instance.listing,
            'related_request': instance,
        },
    )
    Notification.objects.get_or_create(
        user=instance.listing.seller,
        type_code='PURCHASE_REQUEST_STATUS_CHANGE',
        title=cfg['seller_title'],
        defaults={
            'message': cfg['seller_msg'],
            'related_listing': instance.listing,
            'related_request': instance,
        },
    )
