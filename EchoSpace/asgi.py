"""
ASGI config for EchoSpace project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EchoSpace.settings")
application = get_asgi_application()
