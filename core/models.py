from django.db import models


class ProgramType(models.Model):
    """學制主檔 / Program Type"""
    
    code = models.CharField(max_length=10, unique=True, verbose_name='學制代碼')
    name_zh = models.CharField(max_length=100, verbose_name='中文名稱')
    name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name='英文名稱')
    is_active = models.BooleanField(default=True, verbose_name='是否啟用')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='排序值')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        db_table = 'program_types'
        verbose_name = '學制'
        verbose_name_plural = '學制'
        ordering = ['sort_order', 'code']
        indexes = [
            models.Index(fields=['is_active', 'sort_order'], name='program_types_active_sort_idx'),
        ]

    def __str__(self):
        return f"{self.code} - {self.name_zh}"


class Department(models.Model):
    """系所主檔 / Department"""
    
    program_type = models.ForeignKey(
        ProgramType,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name='學制'
    )
    code = models.CharField(max_length=20, verbose_name='系所代碼')
    name_zh = models.CharField(max_length=100, verbose_name='中文名稱')
    name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name='英文名稱')
    is_active = models.BooleanField(default=True, verbose_name='是否啟用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        db_table = 'departments'
        verbose_name = '系所'
        verbose_name_plural = '系所'
        unique_together = [['program_type', 'code']]
        ordering = ['code']
        indexes = [
            models.Index(fields=['program_type', 'name_zh'], name='dept_prog_name_idx'),
        ]

    def __str__(self):
        return f"{self.code} - {self.name_zh}"


class ClassGroup(models.Model):
    """班級主檔 / Class Group"""
    
    program_type = models.ForeignKey(
        ProgramType,
        on_delete=models.CASCADE,
        related_name='class_groups',
        verbose_name='學制'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='class_groups',
        verbose_name='系所'
    )
    code = models.CharField(max_length=20, unique=True, verbose_name='班級代碼')
    name_zh = models.CharField(max_length=100, verbose_name='班級名稱')
    grade_no = models.PositiveSmallIntegerField(verbose_name='年級')
    section_code = models.CharField(max_length=5, verbose_name='班別代碼')
    is_active = models.BooleanField(default=True, verbose_name='是否啟用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        db_table = 'class_groups'
        verbose_name = '班級'
        verbose_name_plural = '班級'
        ordering = ['code']
        indexes = [
            models.Index(fields=['program_type', 'department', 'grade_no'], name='class_prog_dept_grade_idx'),
            models.Index(fields=['department', 'grade_no', 'section_code'], name='class_dept_grade_sect_idx'),
        ]

    def __str__(self):
        return f"{self.code} - {self.name_zh}"
