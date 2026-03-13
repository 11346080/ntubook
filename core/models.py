from django.db import models

class ProgramType(models.Model):
    code = models.CharField("學制代碼", max_length=20, unique=True)
    name_zh = models.CharField("學制名稱", max_length=50)

    def __str__(self):
        return self.name_zh

class Department(models.Model):
    code = models.CharField("系所代碼", max_length=20, unique=True)
    name_zh = models.CharField("系所名稱", max_length=50)

    def __str__(self):
        return self.name_zh

class ClassGroup(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="所屬系所")
    code = models.CharField("班級代碼", max_length=20)
    name_zh = models.CharField("班級名稱", max_length=50)

    def __str__(self):
        return f"{self.department.name_zh} - {self.name_zh}"