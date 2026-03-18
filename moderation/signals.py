from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ModerationAction


@receiver(post_save, sender=ModerationAction)
def link_moderation_action_to_report(sender, instance, created, **kwargs):
    """
    ModerationAction 建立且關聯 Report 時，
    自動將 Report 標記為 RESOLVED，並寫入 handled_by / handled_at。
    """
    if not created or instance.report_id is None:
        return

    report = instance.report

    if report.status in ('OPEN', 'IN_REVIEW'):
        report.status = 'RESOLVED'
        report.handled_by = instance.admin
        report.handled_at = timezone.now()
        if not report.resolution_note:
            report.resolution_note = (
                f'管理員處置：'
                f'{instance.get_action_type_display()} — {instance.reason}'
            )
        report.save(
            update_fields=[
                'status', 'handled_by', 'handled_at',
                'resolution_note', 'updated_at',
            ]
        )
