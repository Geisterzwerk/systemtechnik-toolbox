# =============================================================================
# web/systemlab_web/settings.py  -  Einstellungen der Webversion
# -----------------------------------------------------------------------------
# Stufe 1 (lokal): KEINE Datenbank, keine Benutzerkonten. Alle Inhalte kommen direkt
# aus dem Projekt (bauteile/, schaltungen/, programmieren/ ...) - genau wie in der Desktop-App.
#
# Einstellungen über Umgebungsvariablen (nichts Geheimes im Code -> wichtig für GitHub):
#   SYSTEMLAB_DEBUG=0          Fehlerseiten ohne Details (für online). Standard: 1 (lokal)
#   SYSTEMLAB_SECRET_KEY=...   Pflicht, sobald DEBUG=0
#   SYSTEMLAB_HOSTS=*          erlaubte Adressen, z.B. "192.168.1.20,localhost" oder "*" (im eigenen Netz)
#
# WER RUFT DAS AUF?  Django (über web/manage.py, wsgi.py, asgi.py)
# =============================================================================

import os
import sys
from pathlib import Path

WEB_ORDNER = Path(__file__).resolve().parent.parent           # .../systemtechnik-toolbox/web
PROJEKT_ORDNER = WEB_ORDNER.parent                              # .../systemtechnik-toolbox

# Damit "import bauteile", "import config" ... wie in der Desktop-App funktionieren
if str(PROJEKT_ORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKT_ORDNER))

DEBUG = os.environ.get("SYSTEMLAB_DEBUG", "1") == "1"

SECRET_KEY = os.environ.get("SYSTEMLAB_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError("SYSTEMLAB_SECRET_KEY fehlt – online nie ohne eigenen geheimen Schlüssel starten!")
    SECRET_KEY = "nur-lokal-zum-entwickeln-nicht-online-benutzen"

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("SYSTEMLAB_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "wiki",                        # -> web/wiki/     Startseite, Bereiche, Wissensseiten, Suche
    "rechner",                     # -> web/rechner/  Rechner (Formel-Rechner + Farbcode)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "systemlab_web.urls"
WSGI_APPLICATION = "systemlab_web.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [WEB_ORDNER / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": ["django.template.context_processors.request",
                                       "wiki.kontext.allgemein"]},       # -> web/wiki/kontext.py
}]

DATABASES = {}                     # Stufe 1 braucht keine Datenbank (kommt mit den Benutzerkonten)

LANGUAGE_CODE = "de-ch"
TIME_ZONE = "Europe/Zurich"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [WEB_ORDNER / "static",
                    ("bilder", PROJEKT_ORDNER / "images")]      # Bilder der Wissensseiten: /static/bilder/...
STATIC_ROOT = WEB_ORDNER / "staticfiles"                        # nur für online (collectstatic), nicht im Repo

# Welche Rechner sind im Web schon freigeschaltet? (IDs aus bauteile/rechner/rechner_info.py)
# Formel-Rechner funktionieren automatisch - einfach eine ID ergänzen.
WEB_RECHNER = ["ohm_leistung", "spannungsteiler", "farbcode", "rc_zeit", "dmm_genauigkeit"]
