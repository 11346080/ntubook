# Generated migration - syncs DB schema with current ListingImage model
# DB currently has file_path (from 0001) but needs file_name, image_binary, mime_type
# file_path will be dropped after new columns are added and populated
from django.db import migrations, models


def populate_image_columns(apps, schema_editor):
    """Populate file_name, image_binary, mime_type from existing data.
    Safe: only copies from file_path if it actually exists in the DB.
    """
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'listing_images'
              AND COLUMN_NAME = 'file_path'
        """)
        has_file_path = cursor.fetchone() is not None

    ListingImage = apps.get_model('listings', 'ListingImage')
    if has_file_path:
        for img in ListingImage.objects.all():
            try:
                fp = img.file_path
            except Exception:
                fp = None
            if fp:
                parts = fp.rsplit('.', 1)
                img.file_name = fp
                img.mime_type = f'image/{parts[-1]}' if len(parts) > 1 else 'image/jpeg'
                img.save(update_fields=['file_name', 'mime_type'])


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0002_add_accepted_request_to_listing'),
    ]

    operations = [
        # Step 1: Add the new columns
        migrations.AddField(
            model_name='listingimage',
            name='file_name_new',
            field=models.CharField(max_length=255, default='', verbose_name='原檔案名稱'),
        ),
        migrations.AddField(
            model_name='listingimage',
            name='image_binary_new',
            field=models.BinaryField(default=b'', verbose_name='圖片二進制數據'),
        ),
        migrations.AddField(
            model_name='listingimage',
            name='mime_type_new',
            field=models.CharField(max_length=50, default='image/jpeg', verbose_name='MIME 類型'),
        ),
        # Step 2: Copy data from file_path to new columns (only if file_path exists)
        migrations.RunPython(populate_image_columns, reverse_code=migrations.RunPython.noop),
        # Step 3: Drop file_path and rename new columns
        migrations.RemoveField(
            model_name='listingimage',
            name='file_path',
        ),
        migrations.RenameField(
            model_name='listingimage',
            old_name='file_name_new',
            new_name='file_name',
        ),
        migrations.RenameField(
            model_name='listingimage',
            old_name='image_binary_new',
            new_name='image_binary',
        ),
        migrations.RenameField(
            model_name='listingimage',
            old_name='mime_type_new',
            new_name='mime_type',
        ),
    ]
