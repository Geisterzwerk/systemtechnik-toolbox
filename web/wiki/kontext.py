# =============================================================================
# web/wiki/kontext.py  -  Werte, die JEDE Seite braucht (Navigation, Farben)
#
#   bereiche_nav   Bereiche für das Menü oben          -> web/wiki/inhalt.py
#   farben         Farben aus config.py als CSS-Variablen (hell + dunkel) - eine Quelle für
#                  Desktop-App und Webseite, keine Farbe doppelt im CSS
#   syntax         Farben für Code (config.CODE_FARBEN) als --c-keyword, --c-string ...
#   statisch_version  ?v=... hinter CSS/JS, damit Browser nach Änderungen nichts Altes zeigen
#
# WER RUFT DAS AUF?  Django vor jedem Template (eingetragen in settings.py, TEMPLATES)
# =============================================================================

import os

from django.conf import settings

import config                                                          # -> config.py
from wiki import inhalt                                                # -> web/wiki/inhalt.py


def statisch_version():
    """Zeitstempel der neuesten CSS-/JS-Datei. Steht als ?v=... hinter der Adresse: Nach einer Änderung
    lädt jeder Browser die neue Datei, statt die alte aus seinem Zwischenspeicher zu nehmen."""
    ordner = settings.WEB_ORDNER / "static"
    return max(int(os.path.getmtime(ordner / name)) for name in ("systemlab.css", "systemlab.js"))


def allgemein(request):
    return {"bereiche_nav": inhalt.bereich_infos(), "statisch_version": statisch_version(),
            "farben": [{"name": name.replace("_", "-"), "hell": hell, "dunkel": dunkel}
                       for name, (hell, dunkel) in config.FARBEN.items()],
            "code_farben": config.TEXT_FARBEN,
            "syntax": [{"name": name.replace("_", "-"), "hell": config.CODE_FARBEN["Light"][name],
                        "dunkel": config.CODE_FARBEN["Dark"][name]} for name in config.CODE_FARBEN["Light"]]}
