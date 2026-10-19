# =============================================================================
# web/wiki/kontext.py  -  Werte, die JEDE Seite braucht (Navigation, Farben)
#
#   bereiche_nav   Bereiche für das Menü oben          -> web/wiki/inhalt.py
#   farben         Farben aus config.py als CSS-Variablen (hell + dunkel) - eine Quelle für
#                  Desktop-App und Webseite, keine Farbe doppelt im CSS
#   syntax         Farben für Code (config.CODE_FARBEN) als --c-keyword, --c-string ...
#
# WER RUFT DAS AUF?  Django vor jedem Template (eingetragen in settings.py, TEMPLATES)
# =============================================================================

import config                                                          # -> config.py
from wiki import inhalt                                                # -> web/wiki/inhalt.py


def allgemein(request):
    return {"bereiche_nav": inhalt.bereich_infos(),
            "farben": [{"name": name.replace("_", "-"), "hell": hell, "dunkel": dunkel}
                       for name, (hell, dunkel) in config.FARBEN.items()],
            "code_farben": config.TEXT_FARBEN,
            "syntax": [{"name": name.replace("_", "-"), "hell": config.CODE_FARBEN["Light"][name],
                        "dunkel": config.CODE_FARBEN["Dark"][name]} for name in config.CODE_FARBEN["Light"]]}
