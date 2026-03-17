from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ModerationAction
from notifications.models import Notification


@receiver(post_save, sender=ModerationAction)
def notify_user_on_moderation(sender, instance, created, **kwargs):
    """
    當管理員建立了一筆「審核處置 (ModerationAction)」時，自動通知被檢舉的對象
    """
    if created:
        report = instance.report

        # 根據 target_type 找出被檢舉人
        suspect = None
        if report.target_type == 'user' and report.target_user_id:
            from accounts.models import CustomUser
            suspect = CustomUser.objects.filter(id=report.target_user_id).first()
        elif report.target_type == 'listing' and report.target_listing_id:
            from listings.models import Listing
            listing = Listing.objects.filter(id=report.target_listing_id).first()
            if listing:
                suspect = listing.seller

        if suspect:
            Notification.objects.create(
                user=suspect,
                type_code='WARNING',
                title='系統管理員通知：您的內容已被審核',
                message=f'您好，關於您的檢舉案件已處理完畢。管理員處置說明：{instance.resolution_note}'
            )

        # 同時自動將該筆檢舉的狀態改為「已解決」(RESOLVED)
        if report.status != 'RESOLVED':
            report.status = 'RESOLVED'
            report.save()


@receiver(post_save, sender=ModerationAction)
def auto_execute_penalty(sender, instance, created, **kwargs):
    """
    當管理員對檢舉做出處置時，自動執行對應動作：
    例如：若處置包含「下架內容」，則自動找到該檢舉關聯的刊登並下架。
    """
    if created:
        report = instance.report
        # 根據 target_type 處理
        if report.target_type == 'listing' and report.target_listing_id:
            from listings.models import Listing
            listing = Listing.objects.filter(id=report.target_listing_id).first()
            if listing and instance.action_taken and "下架" in instance.action_taken:
                listing.status = 'OFF_SHELF'
                listing.save()


@receiver(post_save, sender=ModerationAction)
def sync_report_and_notify_user(sender, instance, created, **kwargs):
    """
    當建立處置後，自動更新檢舉案件狀態並通知相關人員。
    """
    if created and instance.report:
        report = instance.report

        # 1. 更新檢舉單狀態為「已解決 (RESOLVED)」
        if report.status != 'RESOLVED':
            report.status = 'RESOLVED'
            report.save()

        # 2. 自動通知「被檢舉人」
        suspect = None
        if report.target_type == 'user' and report.target_user_id:
            from accounts.models import CustomUser
            suspect = CustomUser.objects.filter(id=report.target_user_id).first()
        elif report.target_type == 'listing' and report.target_listing_id:
            from listings.models import Listing
            listing = Listing.objects.filter(id=report.target_listing_id).first()
            if listing:
                suspect = listing.seller

        if suspect:
            Notification.objects.create(
                user=suspect,
                type_code='WARNING',
                title='系統審核處置通知',
                message=(
                    f"您好，關於案件號 #{report.id} 的檢舉已有審核結果。\n"
                    f"處置動作：{instance.action_taken}\n"
                    f"管理員說明：{instance.resolution_note or '無'}"
                )
            )
