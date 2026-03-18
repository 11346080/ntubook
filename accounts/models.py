from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for NTUB Used Books platform."""
    
    class Meta:
        db_table = 'users_user'
