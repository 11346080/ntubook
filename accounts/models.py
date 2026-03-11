from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 這裡可以擴充北商學生專屬的欄位
    student_id = models.CharField("學號", max_length=20, unique=True, blank=True, null=True)
    department = models.CharField("系所", max_length=50, blank=True)
    
    # 未來還可以加：手機號碼、大頭貼、評價星星數等等...

    def __str__(self):
        return self.username