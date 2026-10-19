#!/usr/bin/env python
# =============================================================================
# web/manage.py  -  Startpunkt der WEBVERSION (Django)
# -----------------------------------------------------------------------------
# Im Ordner web/ starten:
#     python manage.py runserver                 -> http://127.0.0.1:8000  (nur dein PC)
#     python manage.py runserver 0.0.0.0:8000    -> auch Kollegen im selben Netz (siehe web/README.md)
#
# WER RUFT DAS AUF?  du im Terminal. Einstellungen: web/systemlab_web/settings.py
# =============================================================================
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systemlab_web.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as fehler:
        raise ImportError("Django fehlt – installieren mit:  python -m pip install -r web/requirements.txt") from fehler
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
