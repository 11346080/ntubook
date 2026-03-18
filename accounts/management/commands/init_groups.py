from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = '初始化後台管理群組與基本權限策略'

    GROUPS = {
        'Admin Managers': {
            'label': '系統管理員',
            'perms': '__all__',
        },
        'Content Moderators': {
            'label': '內容審核員',
            'perms': {
                'moderation': ['add_report', 'change_report', 'delete_report', 'view_report'],
                'listings': ['change_listing', 'view_listing', 'delete_listing'],
                'books': ['change_book', 'view_book'],
                'purchase_requests': ['change_purchaserequest', 'view_purchaserequest'],
            },
        },
        'Support Staff': {
            'label': '客服人員',
            'perms': {
                'listings': ['view_listing'],
                'purchase_requests': ['view_purchaserequest'],
                'accounts': ['view_user', 'change_user'],
                'notifications': ['change_notification', 'view_notification'],
            },
        },
    }

    def handle(self, *args, **options):
        created_groups = []
        created_perms = 0

        for group_name, config in self.GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                created_groups.append(group_name)
                self.stdout.write(
                    self.style.SUCCESS(f'  + 建立群組：「{group_name}」({config["label"]})')
                )

            perms = config['perms']

            if perms == '__all__':
                # Admin Managers = 全部權限（is_staff 即可決定）
                continue

            for app_label, perm_codenames in perms.items():
                for codename in perm_codenames:
                    try:
                        perm = Permission.objects.get(
                            codename=codename,
                            content_type__app_label=app_label,
                        )
                        group.permissions.add(perm)
                        created_perms += 1
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'    ! 找不到權限 {app_label}.{codename}，略過'
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n初始化完成：\n'
                f'  新建立群組：{len(created_groups)} 個\n'
                f'  新指派權限：{created_perms} 筆\n\n'
                f'建議指派方式：\n'
                f'  - 全體後台管理員 → Admin Managers\n'
                f'  - 審核人員     → Content Moderators\n'
                f'  - 客服 / 營運  → Support Staff\n'
                f'\n'
                f'在 Admin Site → Users 頁面可將使用者加入群組。'
            )
        )
