from django.db import models

class ProgramType(models.Model):
    code = models.CharField('學制代碼', max_length=20, unique=True)
    name_zh = models.CharField('學制名稱', max_length=50)

    class Meta:
        verbose_name = '學制'
        verbose_name_plural = '1. 學制' # 前面加數字可控制 Admin 側邊欄排序

    def __str__(self):
        return self.name_zh

class Department(models.Model):
    program_type = models.ForeignKey(ProgramType, on_delete=models.CASCADE, verbose_name='所屬學制')
    code = models.CharField('系所代碼', max_length=20, unique=True)
    name_zh = models.CharField('系所名稱', max_length=50)

    class Meta:
        verbose_name = '系所'
        verbose_name_plural = '2. 系所'

    def __str__(self):
        return self.name_zh
    
class ClassGroup(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所屬系所')
    code = models.CharField('班級代碼', max_length=20, unique=True)
    name_zh = models.CharField('班級名稱', max_length=50)

    class Meta:
        verbose_name = '班級群組'
        verbose_name_plural = '3. 班級群組'

    def __str__(self):
        return self.name_zh