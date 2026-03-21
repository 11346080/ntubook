"""
ASGI config for ntub_usedbooks project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')

application = get_asgi_application()
