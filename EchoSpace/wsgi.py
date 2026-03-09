"""
WSGI config for EchoSpace project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EchoSpace.settings")
application = get_wsgi_application()
