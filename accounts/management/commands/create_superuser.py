from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '建立超級管理員帳號'

    def handle(self, *args, **options):
        username = 'superidol'
        password = '+x'

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'帳號「{username}」已存在，略過建立。')
            )
            return

        user = User.objects.create_superuser(
            username=username,
            password=password,
            email=f'{username}@ntub.edu.tw',
        )
        user.is_staff = True
        user.is_superuser = True
        user.account_status = User.AccountStatus.ACTIVE
        user.save(update_fields=['is_staff', 'is_superuser', 'account_status'])

        self.stdout.write(
            self.style.SUCCESS(
                f'超級管理員建立成功！\n'
                f'  username: {username}\n'
                f'  password: {password}\n'
                f'  is_staff: {user.is_staff}\n'
                f'  is_superuser: {user.is_superuser}\n'
                f'  account_status: {user.account_status}\n'
                f'  請前往 http://localhost:8000/admin/ 登入'
            )
        )
