# Generated migration file for adding Campus FK to Department

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_campus_studentnumberrule'),
    ]

    operations = [
        # 添加 campus FK 到 Department (可為 null，以支援舊資料)
        migrations.AddField(
            model_name='department',
            name='campus',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='departments',
                to='core.campus',
                verbose_name='校區'
            ),
        ),
        
        # 更新 Department 的 Meta 資訊
        migrations.AlterModelOptions(
            name='department',
            options={
                'verbose_name': '系所',
                'verbose_name_plural': '系所',
                'db_table': 'departments',
                'ordering': ['campus__code', 'code'],
                'indexes': [
                    models.Index(
                        fields=['campus', 'program_type', 'name_zh'],
                        name='dept_campus_prog_name_idx'
                    ),
                    models.Index(
                        fields=['is_active', 'campus', 'program_type'],
                        name='dept_active_campus_prog_idx'
                    ),
                ],
                'unique_together': {('campus', 'program_type', 'code')},
            },
        ),
    ]
