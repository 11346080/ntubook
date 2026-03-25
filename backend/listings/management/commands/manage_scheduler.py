"""
Django 管理命令：控制並查看刊登審查排程器狀態

使用方式：
  python manage.py manage_scheduler --status     # 查看排程狀態
  python manage.py manage_scheduler --start      # 啟動排程器
  python manage.py manage_scheduler --stop       # 停止排程器
  python manage.py manage_scheduler --list       # 列出所有排程任務
"""

from django.core.management.base import BaseCommand, CommandError
from listings.scheduler import scheduler, start_scheduler, stop_scheduler


class Command(BaseCommand):
    help = '管理刊登審查排程器（檢視狀態、啟動、停止）'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            action='store_true',
            help='查看排程器狀態'
        )
        parser.add_argument(
            '--start',
            action='store_true',
            help='啟動排程器'
        )
        parser.add_argument(
            '--stop',
            action='store_true',
            help='停止排程器'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='列出所有排程任務'
        )
    
    def handle(self, *args, **options):
        if options['status']:
            self._show_status()
        elif options['start']:
            self._start()
        elif options['stop']:
            self._stop()
        elif options['list']:
            self._list_jobs()
        else:
            self._show_status()
    
    def _show_status(self):
        """查看排程器狀態"""
        if scheduler is None:
            self.stdout.write(
                self.style.ERROR('❌ 排程器未運行\n')
            )
            self.stdout.write('💡 使用以下命令啟動:\n')
            self.stdout.write(self.style.SUCCESS('   python manage.py manage_scheduler --start\n'))
        else:
            self.stdout.write(
                self.style.SUCCESS('✓ 排程器運行中\n')
            )
            self.stdout.write('📋 排程任務：\n')
            if scheduler.running:
                for job in scheduler.get_jobs():
                    self.stdout.write(f'   ✓ {job.name}: {job.trigger}')
            else:
                self.stdout.write('   (無任務)')
    
    def _start(self):
        """啟動排程器"""
        if scheduler is not None and scheduler.running:
            self.stdout.write(
                self.style.WARNING('⚠️  排程器已在運行')
            )
        else:
            start_scheduler()
            self.stdout.write(
                self.style.SUCCESS('✓ 排程器已啟動')
            )
    
    def _stop(self):
        """停止排程器"""
        if scheduler is None or not scheduler.running:
            self.stdout.write(
                self.style.WARNING('⚠️  排程器未運行')
            )
        else:
            stop_scheduler()
            self.stdout.write(
                self.style.SUCCESS('✓ 排程器已停止')
            )
    
    def _list_jobs(self):
        """列出所有排程任務"""
        if scheduler is None:
            self.stdout.write(
                self.style.ERROR('❌ 排程器未初始化')
            )
            return
        
        jobs = scheduler.get_jobs()
        
        if not jobs:
            self.stdout.write('📭 無排程任務')
            return
        
        self.stdout.write('📋 排程任務清單：\n')
        for i, job in enumerate(jobs, 1):
            self.stdout.write(
                f'{i}. {self.style.SUCCESS(job.name)}'
            )
            self.stdout.write(f'   ID: {job.id}')
            self.stdout.write(f'   觸發器: {job.trigger}')
            self.stdout.write(f'   下次執行: {job.next_run_time}\n')
