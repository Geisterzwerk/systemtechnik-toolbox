# =============================================================================
# web/systemlab_web/settings.py  -  Einstellungen der Webversion
# -----------------------------------------------------------------------------
# Alle Inhalte kommen direkt aus dem Projekt (bauteile/, schaltungen/, programmieren/ ...) - genau wie
# in der Desktop-App. Die DATENBANK (SQLite, in Python eingebaut) enthält NUR Benutzerkonten, Sitzungen und
# die Login-Sperre (web/konto/). Liegt in web/daten/ -> steht in .gitignore, kommt nie auf GitHub.
#
# Einmal einrichten (im Ordner web/):   py manage.py migrate          Tabellen anlegen
#                                       py manage.py createsuperuser  dein Admin-Konto (alles frei)
#
# Einstellungen über Umgebungsvariablen (nichts Geheimes im Code -> wichtig für GitHub):
#   SYSTEMLAB_DEBUG=0          Fehlerseiten ohne Details (für online). Standard: 1 (lokal)
#   SYSTEMLAB_SECRET_KEY=...   Pflicht, sobald DEBUG=0
#   SYSTEMLAB_HOSTS=*          erlaubte Adressen, z.B. "192.168.1.20,localhost" oder "*" (im eigenen Netz)
#   SYSTEMLAB_DB=...           Pfad der Datenbank-Datei (Standard: web/daten/systemlab.sqlite3)
#   SYSTEMLAB_ADMIN_PFAD=...   Adresse der Verwaltung (Standard: verwaltung/) - online etwas Unerratbares
#   SYSTEMLAB_REGISTRIERUNG=0  niemand kann sich selbst ein Konto anlegen (nur du in der Verwaltung)
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
    "django.contrib.admin",        # Verwaltung (Konten, Abo-Gruppe) - Adresse: ADMIN_PFAD unten
    "django.contrib.auth",         # Benutzer, Passwörter (sicher gehasht), Gruppen
    "django.contrib.contenttypes",
    "django.contrib.sessions",     # angemeldet bleiben (Cookie mit zufälliger Sitzungs-ID)
    "django.contrib.messages",     # Meldungen nach dem Speichern ("Passwort geändert")
    "django.contrib.staticfiles",
    "konto",                       # -> web/konto/     Anmelden, Registrieren, Konto, Abo-Zugang, Abo-Seite
    "ueben",                       # -> web/ueben/     Übungen lösen, Übungsblatt erstellen (nur mit Abo)
    "wiki",                        # -> web/wiki/     Startseite, Bereiche, Wissensseiten, Suche
    "rechner",                     # -> web/rechner/  Rechner (Formel-Rechner + Farbcode)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # komprimiert die Seiten (Animationen: 680 KB -> ca. 100 KB). Django maskiert den CSRF-Schlüssel bei
    # jeder Antwort neu - darum ist Komprimierung hier unbedenklich (Stichwort BREACH).
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",         # Schutz für Formulare, die etwas speichern (POST)
    "django.contrib.auth.middleware.AuthenticationMiddleware",    # request.user
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "systemlab_web.urls"
WSGI_APPLICATION = "systemlab_web.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [WEB_ORDNER / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": ["django.template.context_processors.request",
                                       "django.contrib.auth.context_processors.auth",
                                       "django.contrib.messages.context_processors.messages",
                                       "wiki.kontext.allgemein"]},       # -> web/wiki/kontext.py
}]

DATENBANK = Path(os.environ.get("SYSTEMLAB_DB") or WEB_ORDNER / "daten" / "systemlab.sqlite3")
DATENBANK.parent.mkdir(parents=True, exist_ok=True)              # SQLite legt den Ordner nicht selbst an
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": DATENBANK}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- Benutzerkonten: SICHERHEIT (Obsidian 03_Sicherheit, Phase 3) -> web/konto/ ----
# Passwörter: Django speichert nur einen Hash (PBKDF2-SHA256 mit sehr vielen Durchläufen + Salz), nie das
# Passwort selbst. Regeln: mindestens 10 Zeichen, nicht ähnlich wie der Benutzername, nicht in der Liste der
# 20'000 häufigsten Passwörter, nicht nur Ziffern.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "/konto/anmelden/"
LOGIN_REDIRECT_URL = "/konto/"
SESSION_COOKIE_AGE = 14 * 24 * 3600            # angemeldet bleiben: 14 Tage
SESSION_COOKIE_HTTPONLY = True                 # JavaScript kommt nicht an das Sitzungs-Cookie
SESSION_COOKIE_SAMESITE = "Lax"                # Cookie nicht bei Formularen von fremden Seiten mitschicken
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = not DEBUG     # online nur über HTTPS
X_FRAME_OPTIONS = "DENY"                       # Seite darf nicht in fremde Seiten eingebettet werden

# Verwaltung (Django-Admin) NICHT unter /admin/ - dort suchen Angreifer zuerst
ADMIN_PFAD = os.environ.get("SYSTEMLAB_ADMIN_PFAD", "verwaltung/").strip("/") + "/"
REGISTRIERUNG_OFFEN = os.environ.get("SYSTEMLAB_REGISTRIERUNG", "1") == "1"
# Login-Sperre (web/konto/sperre.py): so viele Fehlversuche in SPERRE_MINUTEN, dann gesperrt
SPERRE_MINUTEN = 15
SPERRE_PRO_NAME = 5                            # pro Benutzername (schützt ein Konto vor Ausprobieren)
SPERRE_PRO_ADRESSE = 20                        # pro Absender (schützt vor einem Angreifer mit vielen Namen)
REGISTRIERUNG_PRO_STUNDE = 5                   # neue Konten pro Absender und Stunde

LANGUAGE_CODE = "de-ch"
TIME_ZONE = "Europe/Zurich"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [WEB_ORDNER / "static",
                    ("bilder", PROJEKT_ORDNER / "images")]      # Bilder der Wissensseiten: /static/bilder/...
STATIC_ROOT = WEB_ORDNER / "staticfiles"                        # nur für online (collectstatic), nicht im Repo

# ---- Rechner im Web (IDs aus bauteile/rechner/rechner_info.py) -> web/rechner/formular.py ----
# Alle Formel-Rechner (FormelDaten) laufen im Web automatisch - auch jeder neue.
WEB_ALLE_FORMEL_RECHNER = True
# Alle interaktiven Schaltpläne (schaltungen/grafiken*.py) und Animationen (web/wiki/grafiken.py ANIMATIONEN)
# auch einzeln unter /rechner/<id>/
WEB_ALLE_SCHALTUNGEN = True
# Rechner mit eigener Webseite (keine FormelDaten): "farbcode" = Farbcode -> Wert und Wert -> Farbcode (THT),
# "smd_code" = SMD-Aufdruck entschlüsseln
WEB_RECHNER_EXTRA = ["farbcode", "smd_code"]
# Auf der Startseite hervorgehoben (die übrigen stehen unter /rechner/)
WEB_RECHNER_EMPFOHLEN = ["ohm_leistung", "spannungsteiler", "farbcode", "rc_zeit", "dmm_genauigkeit"]

# ---- Rückmeldungen ("Fehler melden") -> web/wiki/rueckmeldung.py ----
# Stufe 1 (lokal): eine Datei, nicht im Repo (.gitignore). Ansehen: python manage.py rueckmeldungen
RUECKMELDUNGEN_DATEI = WEB_ORDNER / "daten" / "rueckmeldungen.jsonl"
