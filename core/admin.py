from django.contrib import admin
from .models import ProgramType, Department, ClassGroup

admin.site.register(ProgramType)
admin.site.register(Department)
admin.site.register(ClassGroup)