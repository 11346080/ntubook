"""
外部 ISBN 查詢服務 / External ISBN Lookup Service
用於向 Caves Books 外部 API 查詢書目資料，並寫入本地 books 資料表。
"""

import re
import logging
from typing import TypedDict
from typing_extensions import NotRequired

import requests
from django.conf import settings
from django.db import transaction

from .models import Book
from .validators import parse_year_from_text

logger = logging.getLogger(__name__)


# =============================================================================
# External API response types
# =============================================================================

class CavesGoodsItem(TypedDict):
    """Caves Books API GoodsList item 欄位型別"""
    Name: str
    Author: str
    TypName: str
    EAN: str
    PublishDate: str
    PicFile: NotRequired[str]
    Price: NotRequired[str]


class CavesApiResponse(TypedDict):
    """Caves Books API 完整回應型別"""
    rtnCode: int
    rtnMsg: str
    GoodsList: list[CavesGoodsItem]


class BookLookupResult(TypedDict):
    """
    ISBN 查詢結果（統一回傳格式）
    source: 'local' | 'external_api' | 'not_found'
    is_new: bool          — 是否為本次新建的書籍（寫入 DB）
    book_id: int | None   — 本地 books 表的 id
    book: NotRequired[dict]  — 書籍資料（用於前端 auto-fill）
    message: str          — 人類可讀狀態訊息
    """
    source: str
    is_new: bool
    book_id: int | None
    book: NotRequired[dict]
    message: str


# =============================================================================
# ISBN 格式驗證
# =============================================================================

ISBN13_RE = re.compile(r'^[0-9]{13}$')
ISBN10_RE = re.compile(r'^[0-9]{9}[0-9X]$', re.IGNORECASE)


def normalize_isbn(raw: str) -> str | None:
    """
    將任意輸入正規化為 ISBN-13（純數字字串）或 ISBN-10。
    移除所有連字號、空格、X/x，只保留有效字元。
    若無法構成有效 ISBN，回傳 None。
    """
    if not raw:
        return None
    cleaned = re.sub(r'[-\s]', '', raw.strip()).upper()
    if ISBN13_RE.match(cleaned):
        return cleaned
    if ISBN10_RE.match(cleaned):
        return cleaned
    return None


# =============================================================================
# 欄位 Mapping（外部 API → books 表）
# =============================================================================

def _build_cover_url(pic_file: str | None) -> str | None:
    """
    將 PicFile 名稱轉換為完整圖片 URL。
    已知 Caves Books 圖片格式：
      https://www.cavesbooks.com.tw/eckm/images/{PicDirName}/{PicFile}
    由於 GoodsList 中只回傳 PicFile（不含目錄），使用已知的固定目錄。
    """
    if not pic_file:
        return None
    # 嘗試直接用完整 URL；若失敗則回傳 None（不阻斷流程）
    return f"https://www.cavesbooks.com.tw/eckm/images/FLEL6SWMgX/{pic_file}"


def _parse_publication_date(raw_date: str | None) -> tuple[int | None, str | None]:
    """
    解析 Caves API 的 PublishDate 欄位。
    Caves 範例值: "2009", "2019", "2024"（僅西元年份字串）

    回傳:
      (publication_year: int | None, publication_date_text: str | None)
    """
    if not raw_date:
        return None, None
    # 直接把字串當年份處理（多數情況只給年份）
    year = parse_year_from_text(raw_date)
    return year, raw_date or None


def map_caves_item_to_book_fields(item: CavesGoodsItem) -> dict:
    """
    將 Caves Books API 回傳的單筆 GoodsList item
    映射為 Django Book model 的建立/更新欄位。
    """
    raw_date = item.get('PublishDate', '')
    pub_year, pub_text = _parse_publication_date(raw_date)

    # EAN → isbn13（必定有值）
    isbn13 = item.get('EAN', '').strip()
    # 嘗試從 Name 或其他欄位推估 isbn10（目前 Caves 只給 EAN）
    isbn10: str | None = None

    # 解析版次（Name 中可能含 "/e" 或 "/第N版"）
    edition: str | None = None
    name = item.get('Name', '')
    m = re.search(r'[/\s](第?[一二三四五六七八九十百千零\d]+版)[/\s　]?', name)
    if m:
        edition = m.group(1)
    m2 = re.search(r'/e[/面書版]', name, re.IGNORECASE)
    if m2 and not edition:
        edition = None  # /e 不足以斷定版次，略過

    return {
        'isbn13': isbn13,
        'isbn10': isbn10,
        'title': name,
        'author_display': item.get('Author', ''),
        'publisher': item.get('TypName', ''),
        'publication_year': pub_year,
        'publication_date_text': pub_text,
        'edition': edition,
        'cover_image_url': _build_cover_url(item.get('PicFile')),
        'metadata_source': Book.MetadataSource.MYTB,
        'metadata_status': Book.MetadataStatus.NEEDS_REVIEW,
    }


# =============================================================================
# 外部 API 呼叫
# =============================================================================

def _fetch_from_caves_api(isbn13: str, timeout: int = 8) -> CavesApiResponse | None:
    """
    向 Caves Books 外部 API 發送 ISBN 查詢。

    URL 格式: https://ec35api.cavesbooks.com.tw/api/SearchTB?key1={isbn}&querytype1=EAN
    """
    base_url = getattr(settings, 'CAVES_BOOKS_API_URL', None)
    if not base_url:
        logger.warning('[ISBN Lookup] CAVES_BOOKS_API_URL not configured in settings')
        return None

    url = f"{base_url}?key1={isbn13}&querytype1=EAN"
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code != 200:
            logger.warning(f'[ISBN Lookup] Caves API returned HTTP {resp.status_code} for {isbn13}')
            return None
        return resp.json()
    except requests.Timeout:
        logger.warning(f'[ISBN Lookup] Caves API timeout for {isbn13}')
        return None
    except requests.RequestException as exc:
        logger.warning(f'[ISBN Lookup] Caves API request error: {exc}')
        return None


# =============================================================================
# 主查詢邏輯
# =============================================================================

def lookup_isbn(raw_isbn: str) -> BookLookupResult:
    """
    ISBN 查詢主函式。

    流程：
      1. 驗證並正規化 ISBN 格式（支援 ISBN-13 與 ISBN-10）
      2. 先查詢本地 books 表（以 isbn13 為主 key）
      3. 本地沒有 → 呼叫 Caves Books 外部 API
      4. API 有結果 → 解析 mapping → get_or_create 寫入 books 表
      5. 回傳統一的 BookLookupResult

    參數:
        raw_isbn: 使用者輸入的原始 ISBN 字串（可含連字號、空格）

    回傳:
        BookLookupResult（固定格式，前端可直接使用）
    """
    # Step 1: 格式驗證
    isbn = normalize_isbn(raw_isbn)
    if not isbn:
        return BookLookupResult(
            source='not_found',
            is_new=False,
            book_id=None,
            message='ISBN 格式不正確，請確認輸入 10 位或 13 位數字',
        )

    # Step 2: 查本地資料庫
    # 先以 isbn13 查（最常見）
    if len(isbn) == 13:
        qs = Book.objects.filter(isbn13=isbn)
    else:
        qs = Book.objects.filter(isbn10=isbn)

    print(f'[ISBN Service] 查本地 books 表, isbn={isbn}')
    local_book = qs.first()
    if local_book:
        print(f'[ISBN Service] 本地命中, book_id={local_book.id}')
        return BookLookupResult(
            source='local',
            is_new=False,
            book_id=local_book.id,
            book={
                'id': local_book.id,
                'isbn13': local_book.isbn13,
                'isbn10': local_book.isbn10,
                'title': local_book.title,
                'author_display': local_book.author_display,
                'publisher': local_book.publisher,
                'publication_year': local_book.publication_year,
                'publication_date_text': local_book.publication_date_text,
                'edition': local_book.edition,
                'cover_image_url': local_book.cover_image_url,
            },
            message='已從本地資料庫找到此書籍',
        )

    # Step 3: 呼叫外部 API（僅支援 ISBN-13）
    if len(isbn) == 10:
        return BookLookupResult(
            source='not_found',
            is_new=False,
            book_id=None,
            message='ISBN-10 尚無法自動查詢外部資料庫，請改用 ISBN-13 或手動填入書籍資訊',
        )

    print(f'[ISBN Service] 本地無, 呼叫外部 API Caves, isbn={isbn}')
    caves_resp = _fetch_from_caves_api(isbn)
    if not caves_resp:
        print('[ISBN Service] 外部 API 回傳 None（timeout/錯誤/非 200）')
        return BookLookupResult(
            source='not_found',
            is_new=False,
            book_id=None,
            message='無法連線至外部書目資料庫，請稍後再試或手動填入書籍資訊',
        )

    print(f'[ISBN Service] 外部 API 回傳成功, rtnCode={caves_resp.get("rtnCode")}, GoodsList 長度={len(caves_resp.get("GoodsList") or [])}')

    # Step 4: 解析 API 回應
    goods_list = caves_resp.get('GoodsList') or []
    if not goods_list:
        print('[ISBN Service] GoodsList 為空，查無書籍')
        return BookLookupResult(
            source='not_found',
            is_new=False,
            book_id=None,
            message='此 ISBN 在外部資料庫查無書籍，請確認 ISBN 是否正確',
        )

    item: CavesGoodsItem = goods_list[0]
    fields = map_caves_item_to_book_fields(item)

    # Step 5: get_or_create（避免併發重複寫入，isbn13 有 unique=True DB 約束保護）
    print(f'[ISBN Service] 即將寫入 books 表, isbn13={fields["isbn13"]}')
    with transaction.atomic():
        book, created = Book.objects.get_or_create(
            isbn13=fields['isbn13'],
            defaults={
                k: v for k, v in fields.items()
                if k not in ('isbn13',)  # isbn13 已作為 key 傳入
            },
        )
        if created:
            logger.info(f'[ISBN Lookup] 新書已寫入 books 表: id={book.id}, isbn13={book.isbn13}')
            print(f'[ISBN Service] 新書寫入成功, book_id={book.id}')
        else:
            logger.info(f'[ISBN Lookup] 書籍已存在: id={book.id}, isbn13={book.isbn13} (併發建立攔截)')
            print(f'[ISBN Service] 書籍已存在（併發）, book_id={book.id}')

    return BookLookupResult(
        source='external_api',
        is_new=created,
        book_id=book.id,
        book={
            'id': book.id,
            'isbn13': book.isbn13,
            'isbn10': book.isbn10,
            'title': book.title,
            'author_display': book.author_display,
            'publisher': book.publisher,
            'publication_year': book.publication_year,
            'publication_date_text': book.publication_date_text,
            'edition': book.edition,
            'cover_image_url': book.cover_image_url,
        },
        message='已從外部書目資料庫取得並寫入本地資料庫',
    )
