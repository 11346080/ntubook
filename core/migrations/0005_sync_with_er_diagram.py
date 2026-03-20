# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_campus_and_student_number_rule'),
    ]

    operations = [
        # ── Step 1: Remove campus FK from Department ──────────────────────
        migrations.RemoveField(model_name='department', name='campus'),

        # ── Step 2: Restore Department unique_together to (program_type, code) ──
        migrations.AlterUniqueTogether(
            name='department',
            unique_together={('program_type', 'code')},
        ),

        # ── Step 3: Remove old index, add new index on Department ──────────
        migrations.RemoveIndex(model_name='department', name='dept_campus_prog_name_idx'),
        migrations.AddIndex(
            model_name='department',
            index=models.Index(fields=['program_type', 'name_zh'], name='dept_prog_name_idx'),
        ),

        # ── Step 4: Add program_type FK to ClassGroup ─────────────────────
        migrations.AddField(
            model_name='classgroup',
            name='program_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='class_groups',
                to='core.programtype',
                verbose_name='學制',
            ),
        ),

        # ── Step 5: Replace class_dept_grade_idx with class_prog_dept_grade_idx ──
        migrations.RemoveIndex(model_name='classgroup', name='class_dept_grade_idx'),
        migrations.AddIndex(
            model_name='classgroup',
            index=models.Index(
                fields=['program_type', 'department', 'grade_no'],
                name='class_prog_dept_grade_idx',
            ),
        ),
    ]
