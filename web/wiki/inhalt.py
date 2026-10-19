# =============================================================================
# web/wiki/inhalt.py
# -----------------------------------------------------------------------------
# DATEN FÜR DIE WEBSEITEN - kommen 1:1 aus dem Projekt, nichts wird kopiert:
#   core/inhalte_index.py   alle Bereiche, Kategorien, Seiten und Rechner + Suche
#
#   BEREICHE                [(slug, name), ...]   slug = Teil der Adresse, z.B. /schaltungen/
#   bereich_name(slug)      "schaltungen" -> "Schaltungen" (oder None)
#   bereich_slug(name)      "Server / Linux" -> "server"
#   kategorien(name)        Kategorien des Bereichs (mit .themen)
#   thema(name, thema_id)   Eintrag (titel, kurz, daten, ...) oder None
#   verweis(name, id)       Link-Ziel für "Siehe auch": zuerst im selben Bereich, sonst überall
#   bild_pfad(datei)        echter Pfad eines Bildes (images/ oder Unterordner)
#
# WER RUFT DAS AUF?  web/wiki/views.py, web/wiki/kontext.py, web/rechner/views.py
# =============================================================================

import os

import config                                                          # -> config.py
from core.inhalte_index import (BEREICH_ICON, BEREICH_TEXT,           # -> core/inhalte_index.py
                                gesamtindex)

BEREICHE = [("bauteile", "Bauteile"), ("schaltungen", "Schaltungen"), ("digitaltechnik", "Digitaltechnik"),
            ("messtechnik", "Messtechnik"), ("programmieren", "Programmieren"), ("server", "Server / Linux")]
_NAME = dict(BEREICHE)
_SLUG = {name: slug for slug, name in BEREICHE}

_bilder = None


def bereich_name(slug):
    return _NAME.get(slug)


def bereich_slug(name):
    return _SLUG.get(name)


def bereich_infos():
    """Für Startseite und Navigation: [{"slug", "name", "icon", "text", "seiten", "rechner", "simulationen"}]"""
    index = gesamtindex()
    return [{"slug": slug, "name": name, "icon": BEREICH_ICON[name], "text": BEREICH_TEXT[name],
             **{k: index["bereiche"][name][k] for k in ("seiten", "rechner", "simulationen", "befehle")}}
            for slug, name in BEREICHE]


def kategorien(name):
    return gesamtindex()["bereiche"][name]["kategorien"]


def thema(name, thema_id):
    return gesamtindex()["eintraege"].get(f"{name}:{thema_id}")


def verweis(name, thema_id):
    """'Siehe auch'-Ziel: (slug, id, titel) - zuerst im eigenen Bereich, sonst im ersten Bereich, der es hat."""
    for bereich in [name] + [n for _, n in BEREICHE if n != name]:
        e = thema(bereich, thema_id)
        if e is not None:
            return {"slug": bereich_slug(bereich), "id": thema_id, "titel": e.titel, "icon": e.icon}
    return None


def bild_pfad(datei):
    """Bild suchen wie die Desktop-App (core/bilder.py): images/datei, sonst irgendwo unter images/."""
    global _bilder
    direkt = os.path.join(config.BILDER_PFAD, datei)
    if os.path.isfile(direkt):
        return direkt
    if _bilder is None:
        _bilder = {}
        for ordner, _unter, dateien in os.walk(config.BILDER_PFAD):
            for d in dateien:
                _bilder.setdefault(d.lower(), os.path.join(ordner, d))
    return _bilder.get(os.path.basename(datei).lower())


def bild_url(datei):
    """Adresse eines Bildes für <img src=...> (über /static/bilder/, siehe settings.py)."""
    pfad = bild_pfad(datei)
    if pfad is None:
        return None
    relativ = os.path.relpath(pfad, config.BILDER_PFAD).replace(os.sep, "/")
    return "/static/bilder/" + relativ
