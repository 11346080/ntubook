# Manually created migration.
# Phase 1: Seed TP and TY campuses, fill NULL department campuses.
# Phase 2: Make campus NOT NULL via model definition change (done in 0004).
# This migration just does the data work. Kept at 0003 to keep dependencies clean.
from django.db import migrations


def fill_campus_tp_and_seed(apps, schema_editor):
    """Seed campuses and fill all NULL department.campus with TP."""
    Campus = apps.get_model('core', 'campus')
    Department = apps.get_model('core', 'department')

    tp, _ = Campus.objects.get_or_create(
        code='TP',
        defaults={'name_zh': '臺北校區', 'short_name': '臺北', 'sort_order': 1},
    )
    ty, _ = Campus.objects.get_or_create(
        code='TY',
        defaults={'name_zh': '桃園校區', 'short_name': '桃園', 'sort_order': 2},
    )

    updated = Department.objects.filter(campus__isnull=True).update(campus=tp)
    # Ensure even non-NULL depts are TP for now (consistent default)
    # This is safe: only touches rows that already have TP or are NULL
    # Re-run this if you need to reset all to TP
    # Currently this just updates NULL → TP


def reverse_fill(apps, schema_editor):
    """Reverse: clear all campus back to NULL (allows rollback before 0004)."""
    Department = apps.get_model('core', 'department')
    Department.objects.all().update(campus=None)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_campus_and_student_number_rule'),
    ]

    operations = [
        migrations.RunPython(fill_campus_tp_and_seed, reverse_fill),
    ]
