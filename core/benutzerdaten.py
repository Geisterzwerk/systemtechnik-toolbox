# =============================================================================
# core/benutzerdaten.py
# -----------------------------------------------------------------------------
# "ZULETZT GEÖFFNET" und "FAVORITEN" - werden in benutzerdaten.json im Projektordner gespeichert
# (steht in .gitignore, gehört also nur dir).
#
# Ein Eintrag ist ein kleines dict:
#   {"art": "seite" oder "rechner", "bereich": "Schaltungen", "id": "lc_tiefpass", "titel": "LC-Tiefpass",
#    "icon": "📶"}
#
#   zuletzt_merken(eintrag)      -> vorne einfügen (doppelte entfernen, höchstens MAX_ZULETZT)
#   zuletzt()                    -> Liste
#   favorit_umschalten(eintrag)  -> True, wenn jetzt Favorit
#   ist_favorit(eintrag)
#   favoriten()                  -> Liste
#
#   FavoritKnopf(leiste, app, eintrag_holen)
#       Stern-Knopf für die Kopfleisten der Bereiche (☆ / ⭐). eintrag_holen() liefert den Eintrag der
#       gerade offenen Seite oder None (dann ist der Knopf grau).
#
# WER RUFT DAS AUF?  main.py (App.geoeffnet, App.favorit_umschalten), gui/startseite_gui.py,
#                    bauteile/engine/wiki_bereich.py, gui/programmieren_gui.py, gui/rechner_gui.py
# =============================================================================

import json
import os

import customtkinter as ctk

import config                                                          # -> config.py

# Testläufe setzen SYSTEMLAB_BENUTZERDATEN auf eine eigene Datei -> deine echten Favoriten bleiben unberührt
DATEI = os.environ.get("SYSTEMLAB_BENUTZERDATEN") or os.path.join(config.BASIS_PFAD, "benutzerdaten.json")
MAX_ZULETZT = 8
_daten = None


def _laden():
    global _daten
    if _daten is None:
        try:
            with open(DATEI, encoding="utf-8") as f:
                _daten = json.load(f)
        except (OSError, ValueError):
            _daten = {}
        _daten.setdefault("zuletzt", [])
        _daten.setdefault("favoriten", [])
    return _daten


def _speichern():
    try:
        with open(DATEI, "w", encoding="utf-8") as f:
            json.dump(_laden(), f, ensure_ascii=False, indent=1)
    except OSError as fehler:                                         # z.B. schreibgeschützter Ordner
        print("[Benutzerdaten] konnte nicht speichern:", fehler)


def _schluessel(eintrag):
    return eintrag["art"], eintrag["bereich"], eintrag["id"]


def zuletzt_merken(eintrag):
    daten = _laden()
    liste = [e for e in daten["zuletzt"] if _schluessel(e) != _schluessel(eintrag)]
    daten["zuletzt"] = ([dict(eintrag)] + liste)[:MAX_ZULETZT]
    _speichern()


def zuletzt():
    return list(_laden()["zuletzt"])


def ist_favorit(eintrag):
    return eintrag is not None and any(_schluessel(e) == _schluessel(eintrag) for e in _laden()["favoriten"])


def favorit_umschalten(eintrag):
    daten = _laden()
    if ist_favorit(eintrag):
        daten["favoriten"] = [e for e in daten["favoriten"] if _schluessel(e) != _schluessel(eintrag)]
        neu = False
    else:
        daten["favoriten"].append(dict(eintrag))
        neu = True
    _speichern()
    return neu


def favoriten():
    return list(_laden()["favoriten"])


# =============================================================================
# STERN-KNOPF FÜR DIE KOPFLEISTEN
# =============================================================================
class FavoritKnopf(ctk.CTkButton):
    """☆ = kein Favorit, ⭐ = Favorit, grau = gerade keine Seite offen (Übersicht)."""

    def __init__(self, master, eintrag_holen, **kwargs):
        super().__init__(master, text="☆", width=40, height=36, font=(config.SCHRIFT, 16),
                         fg_color="transparent", border_width=1, border_color=config.FARBEN["rahmen"],
                         text_color=config.FARBEN["text"], command=self._klick, **kwargs)
        self.fk_eintrag_holen = eintrag_holen
        self.aktualisieren()

    def _klick(self):
        eintrag = self.fk_eintrag_holen()
        if eintrag is not None:
            favorit_umschalten(eintrag)
        self.aktualisieren()

    def aktualisieren(self):
        eintrag = self.fk_eintrag_holen()
        if eintrag is None:
            self.configure(text="☆", state="disabled")
        else:
            self.configure(text="⭐" if ist_favorit(eintrag) else "☆", state="normal")
