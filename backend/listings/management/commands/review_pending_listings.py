"""
離線批次內容審查程式 / Offline Batch Content Review System
= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

目的 (Purpose):
  獨立於 Web 伺服器的後台審查程式，負責審核待審查 (PENDING) 的刊登。
  
架構 (Architecture):
  ┌─────────────────┐
  │   Web API       │
  │ (極速回應)      │  ── 接收資料、儲存 (status=PENDING)、立即回傳
  │ CreateView      │
  └────────┬────────┘
           │
           ▼
        🗄 DB (PENDING)
           ▲
           │
  ┌────────┴────────┐
  │ Management Cmd  │  ── 執行 AI 審查、更新狀態
  │  (後台 Cron)    │  ── 只載入一次模型到記憶
  └─────────────────┘

使用方法 (Usage):
  python manage.py review_pending_listings [options]

選項:
  --batch-size NUM      : 每次批次的筆數 (default: 10)
  --max-workers NUM     : 並行處理的線程數 (default: 1, 不建議超過 2)
  --model MODEL         : 指定模型名稱 (default: uer/roberta-base-finetuned-cluecorpussmall)
  --dry-run             : 模擬執行，不實際修改資料庫
  --verbose             : 詳細輸出

流程 (Process):
  1. 檢查環境（初始化 Django、驗證 GPU 可用性）
  2. 【只載入一次】Hugging Face 分類模型
  3. 撈取所有 PENDING 狀態的 Listing
  4. 批次迴圈：
     ├─ 文本分類審查（title + description）
     ├─ 圖片 NSFW 審查（ListingImage）
     └─ 風險評分 (risk_score)
  5. 批量更新資料庫 (bulk_update)
  6. 終端機日誌（精美格式化）

模型資訊 (Model Info):
  Default: uer/roberta-base-finetuned-cluecorpussmall
  ├─ 任務: Text Classification (binary: positive/negative)
  ├─ 語言: 中文
  ├─ 大小: ~383 MB
  └─ 推薦: GPU 或多核 CPU
"""

import os
import sys
import time
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, Prefetch
from django.utils import timezone

# ─── 導入模型和函數 ───
from listings.models import Listing, ListingImage
from listings.serializers import check_sensitive_words, check_image_nsfw


class Command(BaseCommand):
    """
    Django 管理指令：review_pending_listings
    
    獨立於 Web 伺服器之外的後台批次審查程式
    """
    
    help = '審查待審查的刊登 (PENDING status)，使用 AI 模型進行內容和圖片驗證'
    
    # ─── 類變數：全局模型（只載入一次）───
    classifier = None
    
    def add_arguments(self, parser):
        """定義命令行參數"""
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='每次批次處理的筆數 (default: 10)'
        )
        parser.add_argument(
            '--max-workers',
            type=int,
            default=1,
            help='並行處理的線程數 (default: 1, 不建議超過 2，會消耗大量 GPU 記憶)'
        )
        parser.add_argument(
            '--model',
            type=str,
            default='uer/roberta-base-finetuned-cluecorpussmall',
            help='Hugging Face 模型名稱'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='模擬執行，不實際修改資料庫'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='詳細輸出'
        )
    
    def handle(self, *args, **options):
        """
        管理指令的主入口
        
        流程:
          1. 顯示歡迎文字和配置資訊
          2. 【單次】載入 Hugging Face 模型
          3. 撈取 PENDING 的 Listing
          4. 批次迴圈進行審查
          5. 結束統計
        """
        
        # ─── 解析參數 ───
        batch_size = options.get('batch_size', 10)
        max_workers = options.get('max_workers', 1)
        model_name = options.get('model', 'uer/roberta-base-finetuned-cluecorpussmall')
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)
        
        # ─── 終端機美化 ───
        self._print_banner()
        self._print_config(batch_size, max_workers, model_name, dry_run, verbose)
        
        try:
            # ─── 初始化 ───
            self.stdout.write(
                self.style.SUCCESS('🔄 正在初始化審查引擎...')
            )
            self._initialize(model_name)
            
            # ─── 撈取待審查的刊登 ───
            pending_listings = self._fetch_pending_listings()
            
            if not pending_listings:
                self.stdout.write(
                    self.style.WARNING('📚 藏經閣無待審查書籍，審查機制進入休眠...')
                )
                return
            
            total_count = len(pending_listings)
            self.stdout.write(
                self.style.SUCCESS(f'📖 開始巡視藏經閣... 共發現 {total_count} 卷待審查書籍')
            )
            
            # ─── 批次處理迴圈 ───
            reviewed_listings = []
            published_count = 0
            rejected_count = 0
            
            for idx, listing in enumerate(pending_listings, 1):
                self.stdout.write(f'\n[{idx}/{total_count}] 正在審閱書籍: {listing.book.title if listing.book else "未知"}')
                
                # 執行內容和圖片審查
                is_passed = self._review_listing(listing, verbose)
                
                reviewed_listings.append(listing)
                
                if listing.status == Listing.Status.AVAILABLE:
                    published_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ 審查通過，已發佈'))
                else:
                    rejected_count += 1
                    self.stdout.write(self.style.ERROR(f'  ✗ 審查未通過，已拒絕'))
                    if verbose and listing.reject_reason:
                        self.stdout.write(f'     原因: {listing.reject_reason}')
            
            # ─── 批量更新資料庫 ───
            if not dry_run:
                self._bulk_update_listings(reviewed_listings)
                self.stdout.write(
                    self.style.SUCCESS(f'\n💾 已將審查結果寫入藏經閣...')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'\n🔍 [模擬模式] 未實際更新資料庫')
                )
            
            # ─── 完成統計 ───
            self._print_summary(total_count, published_count, rejected_count)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ 審查過程出錯: {str(e)}')
            )
            if verbose:
                import traceback
                traceback.print_exc()
            raise CommandError(str(e))
    
    def _initialize(self, model_name):
        """
        初始化：載入 Hugging Face 模型（只一次）
        
        注意：模型會被載入到記憶並保持在類變數中
        """
        try:
            # 檢查 GPU 可用性
            import torch
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.stdout.write(f'   📱 計算設備: {device.upper()}')
            
            # 載入模型和 tokenizer
            from transformers import pipeline
            
            self.stdout.write(f'   📚 正在載入模型: {model_name}')
            self.classifier = pipeline(
                "text-classification",
                model=model_name,
                device=0 if device == 'cuda' else -1,  # -1 for CPU
                truncation=True,
                max_length=512
            )
            
            self.stdout.write(
                self.style.SUCCESS('   ✓ 模型已載入，審查引擎就緒')
            )
        except ImportError:
            self.stdout.write(
                self.style.WARNING(
                    '   ⚠️ 無法導入 transformers/torch，請執行:\n'
                    '      pip install transformers torch'
                )
            )
            raise CommandError('Missing required packages')
        except Exception as e:
            raise CommandError(f'Failed to load model: {str(e)}')
    
    def _fetch_pending_listings(self):
        """撈取所有待審查的刊登"""
        return Listing.objects.filter(
            status=Listing.Status.PENDING,
            deleted_at__isnull=True
        ).select_related(
            'book',
            'seller',
            'seller__profile'
        ).prefetch_related(
            Prefetch('images', queryset=ListingImage.objects.all())
        ).order_by('created_at')
    
    def _review_listing(self, listing, verbose=False):
        """
        審查單一刊登
        
        邏輯:
          1. 文本分類 (title + description) → 計算風險分數
          2. 圖片 NSFW 檢查 (ListingImage) → 檢查是否不適當
          3. 綜合判斷 → 設置 status 和 reject_reason
        
        Args:
            listing: Listing instance
            verbose: 是否輸出詳細日誌
        
        Returns:
            bool: True if passed, False if rejected
        """
        
        # ─── 準備審查文本 ───
        title = listing.book.title if listing.book else ""
        description = listing.description or ""
        review_text = f"{title} {description}".strip()
        
        if not review_text:
            # 如果沒有文本，標記為通過（但應避免此情況）
            listing.status = Listing.Status.AVAILABLE
            listing.risk_score = Decimal('0.00')
            return True
        
        # ─── 1. 文本分類審查 ───
        try:
            # 使用 NLP 模型進行分類
            result = self.classifier(review_text)
            
            # 結果格式: [{'label': 'positive'/'negative', 'score': 0.95}]
            label = result[0]['label']  # 'positive' or 'negative'
            score = result[0]['score']  # 0~1
            
            # 計算風險分數
            if label == 'negative':
                risk_score = Decimal(str(score))
            else:
                risk_score = Decimal(str(1 - score))
            
            # 詳細輸出 AI 審查結果
            if verbose:
                self.stdout.write(f'     [AI審查] 模型判斷: {label.upper()} | 分數: {score:.4f} | 風險等級: {risk_score:.2f}')
            
            if risk_score > Decimal('0.60'):
                # 風險分數過高，拒絕刊登
                listing.status = Listing.Status.REJECTED
                listing.reject_reason = f'AI 判讀內容似有不妥，請重新斟酌措辭... (風險分數: {risk_score:.2f})'
                listing.risk_score = risk_score
                return False
            
        except Exception as e:
            # 模型推理失敗，保守起見拒絕
            listing.status = Listing.Status.REJECTED
            listing.reject_reason = f'內容審查服務暫時不可用，請稍後重試 (Error: {str(e)[:50]})'
            listing.risk_score = Decimal('0.50')
            return False
        
        # ─── 2. 敏感詞檢查（備用） ───
        sensitive_words = check_sensitive_words(review_text)
        if sensitive_words:
            listing.status = Listing.Status.REJECTED
            listing.reject_reason = f'用詞似有不妥，請重新斟酌筆墨... (敏感詞: {", ".join(sensitive_words[:3])})'
            listing.risk_score = risk_score if 'risk_score' in locals() else Decimal('0.75')
            return False
        
        # ─── 3. 圖片 NSFW 檢查 ───
        images = listing.images.all()
        for image in images:
            if image.image_binary and check_image_nsfw(image.image_binary):
                # 圖片被判定為 NSFW，拒絕此刊登
                listing.status = Listing.Status.REJECTED
                listing.reject_reason = '圖片內容不符合平台政策，請重新上傳合適的圖片'
                listing.risk_score = Decimal('0.90')
                return False
        
        # ─── 4. 全部通過：設置為 AVAILABLE ───
        listing.status = Listing.Status.AVAILABLE
        listing.risk_score = risk_score if 'risk_score' in locals() else Decimal('0.00')
        return True
    
    def _bulk_update_listings(self, listings):
        """批量更新資料庫"""
        update_fields = ['status', 'reject_reason', 'risk_score', 'updated_at']
        Listing.objects.bulk_update(listings, update_fields, batch_size=100)
    
    # ─── 終端機美化函數 ───
    
    def _print_banner(self):
        """顯示歡迎文字"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     📚 北商傳書 - 離線批次審查系統                      ║
║     Offline Batch Review System                          ║
║                                                           ║
║     使以審查待審查刊登，運用 AI 辨識不當內容            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        self.stdout.write(self.style.SUCCESS(banner))
    
    def _print_config(self, batch_size, max_workers, model_name, dry_run, verbose):
        """顯示配置資訊"""
        config_text = f"""
⚙️  配置資訊
   ├─ 批次大小: {batch_size}
   ├─ 最大線程數: {max_workers}
   ├─ 模型: {model_name}
   ├─ 模式: {'[模擬] ' if dry_run else '[實際執行] '}DRY-RUN
   └─ 詳細輸出: {'是' if verbose else '否'}
"""
        self.stdout.write(self.style.WARNING(config_text))
    
    def _print_summary(self, total, published, rejected):
        """顯示完成統計"""
        summary = f"""
📊 審查完成統計
   ├─ 總審查筆數: {total}
   ├─ 已發佈: {published} ✓
   ├─ 已拒絕: {rejected} ✗
   └─ 通過率: {(published/total*100):.1f}%

✨ 藏經閣已整理完畢，待續...
"""
        self.stdout.write(self.style.SUCCESS(summary))
        self.stdout.write(f'⏰ 完成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
