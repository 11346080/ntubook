# Generated manually — books.0003: 最終 schema 改造
#
# 變動摘要：
#   - 新增 publication_year（PositiveSmallIntegerField，nullable）
#   - 移除 publication_date（DateField）
#   - 清理 MetadataSource choices：移除 GOOGLE_BOOKS / LOCAL
#   - 清理 MetadataStatus choices：移除 AUTO_IMPORTED
#   - publication_year 加 MinValueValidator(1900) / MaxValueValidator(2100)
#
# data migration：解析舊資料填入 publication_year
#   優先取 publication_date.year；次取 publication_date_text 前4位數字
#   GOOGLE_BOOKS / LOCAL → MANUAL
#   AUTO_IMPORTED → NEEDS_REVIEW

import re

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


def _parse_year(value: str | None) -> int | None:
    """從日期字串解析西元年份。與 validators.parse_year_from_text 同邏輯。"""
    if not value:
        return None
    m = re.match(r'^(\d{4})', str(value).strip())
    if m:
        year = int(m.group(1))
        if 1900 <= year <= 2100:
            return year
    for sep in ('-', '/'):
        if sep in str(value):
            part = str(value).split(sep)[0].strip()
            if part.isdigit() and len(part) == 4:
                year = int(part)
                if 1900 <= year <= 2100:
                    return year
    return None


def _migrate_publication_year(apps, schema_editor):
    Book = apps.get_model('books', 'Book')
    migrated = 0
    for book in Book.objects.all():
        new_year = None
        if book.publication_date is not None:
            new_year = book.publication_date.year
        elif book.publication_date_text:
            new_year = _parse_year(book.publication_date_text)
        if new_year is not None:
            book.publication_year = new_year
            book.save(update_fields=['publication_year'])
            migrated += 1
    # 舊 choices 值映射（目前 DB 皆為 0 筆，仍需寫以確保可重放）
    Book.objects.filter(metadata_source__in=('GOOGLE_BOOKS', 'LOCAL')).update(
        metadata_source='MANUAL'
    )
    Book.objects.filter(metadata_status='AUTO_IMPORTED').update(
        metadata_status='NEEDS_REVIEW'
    )


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_add_source_listing_to_bookapplicability'),
    ]

    operations = [
        # Step 1：新增 publication_year（nullable，暫不附 validators，避免舊資料進不去）
        migrations.AddField(
            model_name='book',
            name='publication_year',
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name='出版年份',
            ),
        ),

        # Step 2：資料遷移（填 publication_year + 映射舊 choices 值）
        # 單參數，回滾時自動拋 IrreversibleError
        migrations.RunPython(_migrate_publication_year),

        # Step 3：更新 publication_year，加入 validators（此後新資料強制 1900~2100）
        migrations.AlterField(
            model_name='book',
            name='publication_year',
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[MinValueValidator(1900), MaxValueValidator(2100)],
                verbose_name='出版年份',
            ),
        ),

        # Step 4：移除舊 DateField（此時所有非 null 記錄的年份已遷入 publication_year）
        migrations.RemoveField(
            model_name='book',
            name='publication_date',
        ),
    ]
