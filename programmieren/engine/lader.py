# =============================================================================
# programmieren/engine/lader.py
# -----------------------------------------------------------------------------
# Der LADER findet automatisch alle Themen-Dateien und liest sie ein.
#
# SO FUNKTIONIERT ES:
#   programmieren/inhalte/
#       01_grundlagen/            <- ein Ordner = eine KATEGORIE
#           _kategorie.py         <- Name + Icon der Kategorie
#           variablen.py          <- eine Datei = ein THEMA (eine Wiki-Seite)
#           datentypen.py
#       02_kontrollstrukturen/
#           ...
#
#   - Die Zahl vorne im Ordnernamen (01_, 02_) bestimmt die Reihenfolge.
#   - Dateien, die mit "_" beginnen, sind KEINE Themen (z.B. _kategorie.py, _vorlage.py).
#   - Jede Themen-Datei enthält ein Dictionary namens THEMA = {...}
#
#   => Neues Thema? Einfach neue .py Datei in den passenden Ordner legen.
#      Der Code hier muss NIE angepasst werden.
#
# WICHTIG: Diese Datei benutzt KEIN tkinter. Sie liefert nur Daten.
#          Die Darstellung passiert in engine/seite.py.
# =============================================================================

import importlib.util
import os

import config  # -> config.py (Pfad zum inhalte-Ordner)


# =============================================================================
# DATENKLASSEN
# =============================================================================
class Thema:
    """
    Ein einzelnes Thema (= eine Wiki-Seite), z.B. "While-Schleife".
    Die Daten kommen aus dem THEMA-Dictionary der jeweiligen Datei.
    """

    def __init__(self, thema_id, daten, kategorie):
        self.id = thema_id                                   # Dateiname ohne .py, z.B. "while_schleife"
        self.kategorie = kategorie                           # Objekt der Klasse Kategorie (unten)
        self.daten = daten                                   # das ganze Dictionary (für seite.py)

        # Häufig benutzte Felder direkt als Attribut (mit Standardwerten)
        self.titel = daten.get("titel", thema_id)
        self.kurz = daten.get("kurz", "")
        self.reihenfolge = daten.get("reihenfolge", 999)
        self.stichworte = daten.get("stichworte", [])

    def __repr__(self):          # schönere Ausgabe beim print() / Debuggen
        return f"<Thema {self.id}: {self.titel}>"


class Kategorie:
    """Eine Kategorie (= ein Ordner), z.B. "Grundlagen". Enthält mehrere Themen."""

    def __init__(self, ordner_name, name, icon, beschreibung):
        self.ordner = ordner_name       # z.B. "01_grundlagen"
        self.name = name                # z.B. "Grundlagen"
        self.icon = icon                # z.B. "📘"
        self.beschreibung = beschreibung
        self.themen = []                # Liste von Thema-Objekten

    def __repr__(self):
        return f"<Kategorie {self.name} ({len(self.themen)} Themen)>"


# =============================================================================
# LADEN
# =============================================================================
def _modul_aus_datei(pfad):
    """
    Lädt eine .py Datei direkt über ihren Pfad.
    (Normales 'import' geht hier nicht, weil Ordnernamen wie '01_grundlagen'
     mit einer Zahl beginnen - das mag Python bei 'import' nicht.)
    """
    name = "thema_" + os.path.splitext(os.path.basename(pfad))[0]
    spec = importlib.util.spec_from_file_location(name, pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)        # führt die Datei aus -> THEMA existiert danach
    return modul


def alle_laden(inhalte_pfad=None):
    """
    Durchsucht den inhalte-Ordner und gibt zurück:
        kategorien   Liste von Kategorie-Objekten (sortiert)
        themen       Dictionary  id -> Thema  (für schnellen Zugriff / "Siehe auch")
        fehler       Liste mit Fehlermeldungen (z.B. Tippfehler in einer Themen-Datei)
    """
    inhalte_pfad = inhalte_pfad or config.INHALTE_PROGRAMMIEREN
    kategorien, themen, fehler = [], {}, []

    if not os.path.isdir(inhalte_pfad):
        return kategorien, themen, [f"Ordner nicht gefunden: {inhalte_pfad}"]

    # ---- 1) Alle Kategorie-Ordner durchgehen (alphabetisch -> 01_, 02_, ...) ----
    for ordner in sorted(os.listdir(inhalte_pfad)):
        ordner_pfad = os.path.join(inhalte_pfad, ordner)
        if not os.path.isdir(ordner_pfad) or ordner.startswith(("_", ".")):
            continue

        # Kategorie-Infos aus _kategorie.py lesen (falls vorhanden)
        name = ordner.split("_", 1)[-1].capitalize()  # Fallback: "01_grundlagen" -> "Grundlagen"
        icon, beschreibung = "📁", ""
        info_datei = os.path.join(ordner_pfad, "_kategorie.py")
        if os.path.exists(info_datei):
            try:
                info = _modul_aus_datei(info_datei)
                name = getattr(info, "NAME", name)
                icon = getattr(info, "ICON", icon)
                beschreibung = getattr(info, "BESCHREIBUNG", "")
            except Exception as e:
                fehler.append(f"{ordner}/_kategorie.py: {e}")

        kategorie = Kategorie(ordner, name, icon, beschreibung)

        # ---- 2) Alle Themen-Dateien in diesem Ordner laden ----
        for datei in os.listdir(ordner_pfad):
            if not datei.endswith(".py") or datei.startswith("_"):
                continue
            thema_id = datei[:-3]
            try:
                modul = _modul_aus_datei(os.path.join(ordner_pfad, datei))
                daten = getattr(modul, "THEMA", None)
                if not isinstance(daten, dict):
                    fehler.append(f"{ordner}/{datei}: kein THEMA-Dictionary gefunden")
                    continue
                if thema_id in themen:
                    fehler.append(f"{ordner}/{datei}: Name '{thema_id}' existiert doppelt")
                    continue
                thema = Thema(thema_id, daten, kategorie)
                kategorie.themen.append(thema)
                themen[thema_id] = thema
            except Exception as e:
                # Ein kaputtes Thema soll NICHT die ganze App abstürzen lassen
                fehler.append(f"{ordner}/{datei}: {type(e).__name__}: {e}")

        # Themen nach 'reihenfolge' sortieren, bei Gleichstand nach Titel
        kategorie.themen.sort(key=lambda t: (t.reihenfolge, t.titel.lower()))
        if kategorie.themen:
            kategorien.append(kategorie)

    return kategorien, themen, fehler
