from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0004_merge_20260324_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='reject_reason',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='退回原因'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='status',
            field=models.CharField(choices=[('PENDING', '待審核'), ('AVAILABLE', '可購買'), ('RESERVED', '已保留'), ('SOLD', '已售出'), ('OFF_SHELF', '已下架'), ('REJECTED', '已退回'), ('REMOVED', '已移除'), ('DELETED', '已刪除')], default='PENDING', max_length=20, verbose_name='刊登狀態'),
        ),
    ]
