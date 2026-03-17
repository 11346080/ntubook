from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ModerationAction
from notifications.models import Notification


@receiver(post_save, sender=ModerationAction)
def handle_moderation_action(sender, instance, created, **kwargs):
    """
    當管理員建立了一筆「審核處置 (ModerationAction)」時的單一處理流程：
    1. 通知被檢舉對象
    2. 將檢舉狀態改為「已解決」(RESOLVED)
    3. 若處置包含「下架」，則將刊登強制下架
    """
    if not created:
        return

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
            # 若 action_taken 包含「下架」，則自動將刊登下架
            if instance.action_taken and "下架" in instance.action_taken:
                listing.status = 'OFF_SHELF'
                listing.save()

    # 發送通知給被檢舉人
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

    # 將檢舉狀態改為「已解決」(RESOLVED)
    if report.status != 'RESOLVED':
        report.status = 'RESOLVED'
        report.save()
