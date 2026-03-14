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