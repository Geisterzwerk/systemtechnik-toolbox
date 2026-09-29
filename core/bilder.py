# =============================================================================
# core/bilder.py
# -----------------------------------------------------------------------------
# Bilder finden und laden - ohne Absturz, wenn eins fehlt.
#
# SUCHREIHENFOLGE:
#   1. Voller Pfad angegeben und vorhanden -> nehmen
#   2. Nur Dateiname -> in <Projekt>/images/ suchen
#   3. Nicht gefunden -> im GANZEN Projektordner suchen
#      (alle Unterordner, Gross-/Kleinschreibung egal)
#   4. Immer noch nichts -> None (die Seite zeigt dann einen Hinweis)
#
# FUNKTIONEN:
#   pil_laden(pfad)                  -> PIL-Bild (für ResponsiveBild in core/layout.py)
#   bild_laden(pfad, groesse, ...)   -> CTkImage mit fester Grösse
#   icon_laden(dateiname, groesse)   -> quadratisches Icon (Sidebar-Buttons)
# =============================================================================

import os

import customtkinter as ctk
from PIL import Image

import config  # -> config.py (Pfade)

_BILD_ENDUNGEN = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico")
_IGNORIERTE_ORDNER = {".git", "__pycache__", ".venv", "venv", ".vscode"}

_datei_index = None      # dateiname (klein) -> voller Pfad (wird beim 1. Bedarf aufgebaut)
_pil_cache = {}          # pfad -> PIL-Bild
_ctk_cache = {}          # (pfad, breite, hoehe) -> CTkImage


def _im_projekt_suchen(dateiname):
    """Sucht eine Bilddatei in ALLEN Unterordnern des Projekts (Gross/Klein egal)."""
    global _datei_index
    if _datei_index is None:
        _datei_index = {}
        for ordner, unterordner, dateien in os.walk(config.BASIS_PFAD):
            unterordner[:] = [u for u in unterordner if u not in _IGNORIERTE_ORDNER]
            for d in dateien:
                if d.lower().endswith(_BILD_ENDUNGEN):
                    _datei_index.setdefault(d.lower(), os.path.join(ordner, d))
    return _datei_index.get(dateiname.lower())


def pfad_finden(pfad):
    """Gibt den echten Pfad eines Bildes zurück oder None."""
    if not os.path.isabs(pfad):
        pfad = os.path.join(config.BILDER_PFAD, pfad)
    if os.path.exists(pfad):
        return pfad
    gefunden = _im_projekt_suchen(os.path.basename(pfad))
    if gefunden is None:
        print(f"[bilder.py] Bild nicht gefunden: {os.path.basename(pfad)}\n"
              f"            erwartet in: {config.BILDER_PFAD}")
    return gefunden


def pil_laden(pfad):
    """Lädt ein Bild als PIL-Image (oder None)."""
    echt = pfad_finden(pfad)
    if echt is None:
        return None
    if echt not in _pil_cache:
        try:
            _pil_cache[echt] = Image.open(echt)
            _pil_cache[echt].load()
        except Exception as fehler:
            print(f"[bilder.py] Bild konnte nicht geladen werden ({echt}): {fehler}")
            return None
    return _pil_cache[echt]


def bild_laden(pfad, groesse=None, max_breite=None):
    """
    Lädt ein Bild als CTkImage mit FESTER Grösse.
    (Für Bilder, die mitwachsen sollen: ResponsiveBild in core/layout.py)
    """
    pil = pil_laden(pfad)
    if pil is None:
        return None
    breite, hoehe = pil.size
    if groesse is not None:
        breite, hoehe = groesse
    elif max_breite is not None and breite > max_breite:
        faktor = max_breite / breite
        breite, hoehe = int(breite * faktor), int(hoehe * faktor)
    schluessel = (id(pil), breite, hoehe)
    if schluessel not in _ctk_cache:
        _ctk_cache[schluessel] = ctk.CTkImage(light_image=pil, dark_image=pil, size=(breite, hoehe))
    return _ctk_cache[schluessel]


def icon_laden(dateiname, groesse=24):
    """Kleines quadratisches Icon aus /images (z.B. 'resistor.png')."""
    return bild_laden(dateiname, groesse=(groesse, groesse))
