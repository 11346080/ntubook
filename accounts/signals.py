from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import User, UserProfile
from notifications.models import Notification

User = get_user_model()


@receiver(pre_save, sender=User)
def cache_user_previous_status(sender, instance, **kwargs):
    """
    在 User.save() 之前，從 DB 查詢舊值並暫存到 instance。
    若為新物件（pk 為空）則跳過。
    用途：供 post_save signal 比對狀態是否真的變更。
    """
    if instance.pk is None:
        return
    try:
        old_instance = User.objects.get(pk=instance.pk)
        instance._previous_status = old_instance.account_status
    except User.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    User 建立時自動建立 UserProfile（若尚未存在）。
    """
    if not created:
        return
    if not hasattr(instance, '_profile_created') or not instance._profile_created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'display_name': instance.username}
        )
        instance._profile_created = True


@receiver(post_save, sender=User)
def notify_user_account_status_change(sender, instance, created, **kwargs):
    """
    當 account_status 真正變更時，發送通知給該使用者。
    只在透過 .save() 變更時觸發；
    admin action 的 queryset.update() 不觸發 post_save，因此不重複。
    """
    if created:
        return
    previous = getattr(instance, '_previous_status', None)
    if previous is None:
        return
    if previous == instance.account_status:
        return

    status_map = {
        'ACTIVE': '帳號已恢復正常',
        'SUSPENDED': '帳號已被停權',
        'RESTRICTED_LISTING': '帳號已被限制刊登功能',
    }
    title_map = {
        'ACTIVE': '帳號恢復正常通知',
        'SUSPENDED': '帳號停權通知',
        'RESTRICTED_LISTING': '帳號限制刊登通知',
    }

    current = instance.account_status
    title = title_map.get(current, f'帳號狀態變更：{current}')
    message = status_map.get(current, f'您的帳號狀態已變更為：{current}。')

    Notification.objects.get_or_create(
        user=instance,
        type_code='ACCOUNT_STATUS_CHANGE',
        title=title,
        defaults={'message': message},
    )
