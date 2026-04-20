"""WSGI entry point for traditional Django hosting."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "study_girl.settings")
application = get_wsgi_application()
