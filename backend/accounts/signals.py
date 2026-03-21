from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import User, UserProfile
from notifications.models import Notification

# Allauth signals - 條件導入，只在可用時才註冊 receiver
ALLAUTH_AVAILABLE = False
pre_social_login = None
post_social_login = None

try:
    from allauth.socialaccount.signals import pre_social_login, post_social_login
    ALLAUTH_AVAILABLE = True
except ImportError:
    pass

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


# ========== Allauth Integration Signals ==========
# 只在 allauth 可用時才註冊信號处理器

if ALLAUTH_AVAILABLE and pre_social_login is not None:
    @receiver(pre_social_login)
    def check_ntub_email(sender, request, sociallogin, **kwargs):
        """
        在社交登入前檢查是否為 @ntub.edu.tw 帳號。
        (可選：若要嚴格限制，可在此 raise 異常)
        """
        email = sociallogin.email_address or sociallogin.account.extra_data.get('email', '')
        if email and not email.endswith('@ntub.edu.tw'):
            # 可選：記錄警告，但不中斷流程
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Non-NTUB email attempting login: {email}")
            # 若要拒絕，可以 raise ValidationError
            # from django.core.exceptions import ValidationError
            # raise ValidationError(f"Only @ntub.edu.tw accounts are allowed. Got: {email}")


if ALLAUTH_AVAILABLE and post_social_login is not None:
    @receiver(post_social_login)
    def link_to_local_user_if_exists(sender, request, sociallogin, **kwargs):
        """
        社交登入後的額外處理。
        在此階段可能需要額外的邏輯，但主要邏輯在 adapter 中已經處理。
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            user = sociallogin.user
            email = sociallogin.email_address or user.email
            
            logger.info(
                f"Social login completed for user {user.username} with email {email}"
            )
            
            # 驗證 UserProfile 是否已更新
            if hasattr(user, 'profile'):
                profile = user.profile
                logger.info(
                    f"UserProfile details: student_no={profile.student_no}, "
                    f"grade_no={profile.grade_no}, "
                    f"department={profile.department}"
                )
        
        except Exception as e:
            logger.error(f"Exception in post_social_login: {str(e)}", exc_info=True)
