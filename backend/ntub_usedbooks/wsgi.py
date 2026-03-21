"""
WSGI config for ntub_usedbooks project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')

application = get_wsgi_application()
