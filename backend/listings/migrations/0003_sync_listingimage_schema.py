# Generated migration - DB schema already matches models.py via prior 0003
# This migration exists only to keep Django's migration state in sync
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0002_add_accepted_request_to_listing'),
    ]

    operations = [
        # DB table listing_images already has file_name, image_binary, mime_type
        # (was migrated via the now-missing 0003 on 2026-03-23)
        # No schema change needed.
    ]
