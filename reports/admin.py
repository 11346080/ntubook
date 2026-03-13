from django.contrib import admin
from .models import Report, ModerationAction

admin.site.register(Report)
admin.site.register(ModerationAction)