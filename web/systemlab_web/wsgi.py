# web/systemlab_web/wsgi.py  -  Einstieg für einen Webserver (online, z.B. gunicorn). Lokal: manage.py runserver
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systemlab_web.settings")
application = get_wsgi_application()
