"""
刊登審查排程器 / Listing Review Scheduler

使用 APScheduler 實現自動後台審查：
  1. 每天凌晨 3:00 執行一次全面審查
  2. 當待審查刊登達到 10 筆時立即執行緊急審查

啟動方式：
  - 由 apps.py 在 Django 啟動時自動啟動
  - 無需手動執行管理命令
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
from django.db import connection
from listings.models import Listing

logger = logging.getLogger(__name__)

# 全局排程器實例
scheduler = None


def run_review():
    """執行審查命令（調用管理命令）"""
    try:
        logger.info('🔄 [排程] 開始後台審查...')
        call_command('review_pending_listings', model='bert-base-chinese', verbosity=1)
        logger.info('✓ [排程] 審查完成')
    except Exception as e:
        logger.error(f'❌ [排程] 審查失敗: {str(e)}')


def check_and_review_if_threshold():
    """檢查待審查數量，達到 10 筆時立即審查"""
    try:
        pending_count = Listing.objects.filter(status=Listing.Status.PENDING).count()
        logger.info(f'📊 [排程] 當前待審查刊登: {pending_count} 筆')
        
        if pending_count >= 10:
            logger.info('⚡ [排程] 待審查數量達到 10 筆，觸發緊急審查！')
            run_review()
    except Exception as e:
        logger.error(f'❌ [排程] 檢查失敗: {str(e)}')


def start_scheduler():
    """啟動排程器"""
    global scheduler
    
    if scheduler is not None:
        logger.warning('⚠️ 排程器已經運行中')
        return
    
    try:
        scheduler = BackgroundScheduler()
        
        # 任務 1: 每天凌晨 3:00 執行全面審查
        scheduler.add_job(
            run_review,
            trigger=CronTrigger(hour=3, minute=0),
            id='daily_review_3am',
            name='每天凌晨 3:00 審查',
            replace_existing=True,
            misfire_grace_time=3600  # 容許 1 小時誤差
        )
        logger.info('✓ 已排程: 每天凌晨 3:00 執行審查')
        
        # 任務 2: 每 5 分鐘檢查一次，待審查數量達到 10 筆時觸發
        scheduler.add_job(
            check_and_review_if_threshold,
            trigger='interval',
            minutes=5,
            id='check_threshold_review',
            name='每 5 分鐘檢查待審查數量',
            replace_existing=True,
            max_instances=1  # 防止重複執行
        )
        logger.info('✓ 已排程: 每 5 分鐘檢查待審查數量（達到 10 筆時觸發）')
        
        # 啟動排程器
        scheduler.start()
        logger.info('🚀 後台審查排程器已啟動')
        
    except Exception as e:
        logger.error(f'❌ 無法啟動排程器: {str(e)}')
        scheduler = None


def stop_scheduler():
    """停止排程器"""
    global scheduler
    
    if scheduler is None:
        logger.warning('⚠️ 排程器未運行')
        return
    
    try:
        scheduler.shutdown(wait=False)
        scheduler = None
        logger.info('✓ 排程器已停止')
    except Exception as e:
        logger.error(f'❌ 無法停止排程器: {str(e)}')
