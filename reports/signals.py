from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ModerationAction
from notifications.models import Notification

@receiver(post_save, sender=ModerationAction)
def notify_user_on_moderation(sender, instance, created, **kwargs):
    """
    情境 3：當管理員建立了一筆「審核處置 (ModerationAction)」時，自動通知被檢舉的對象
    """
    if created:
        report = instance.report
        
        # 找出被檢舉人 (這裡假設 Report 模型中紀錄了被檢舉的對象，通常會關聯到 user 或 listing 的 seller)
        # 假設你的檢舉表中有 target_user 這個屬性或方法可以取得被檢舉人
        suspect = report.target_user if hasattr(report, 'target_user') else None
        
        if suspect:
            Notification.objects.create(
                user=suspect,
                type_code='WARNING',
                title='系統管理員通知：您的內容已被審核',
                message=f'您好，關於您的檢舉案件已處理完畢。管理員處置說明：{instance.note}'
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
        # 假設處置註解中有關鍵字或你有一個 action_type 欄位
        # 這裡示範：如果 report 關聯的是某個 Listing
        if report.content_type.model == 'listing' and "下架" in instance.note:
            listing = report.content_object
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
            
        # 2. 自動通知「被檢舉人」 (假設 Report 模型有關聯被檢舉人 suspect_user)
        # 這裡根據你的模型欄位調整，若 report 有 suspect_user 欄位：
        suspect = getattr(report, 'suspect_user', None)
        
        if suspect:
            Notification.objects.create(
                user=suspect,
                type_code='WARNING',
                title='系統審核處置通知',
                message=(
                    f"您好，關於案件號 #{report.id} 的檢舉已有審核結果。\n"
                    f"處置動作：{instance.action_type}\n"
                    f"管理員說明：{instance.note or '無'}"
                )
            )