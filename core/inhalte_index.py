# =============================================================================
# core/inhalte_index.py
# -----------------------------------------------------------------------------
# INDEX ÜBER ALLE INHALTE - ohne Fenster (kein tkinter), darum auch für die Webversion.
#
#   gesamtindex()   einmal aufgebaut, dann gemerkt:
#                   {"eintraege": {schluessel: Eintrag}, "bereiche": {...}, "suche": Suchmaschine}
#   interaktiv(id)  ist der Rechner eine interaktive Grafik/Simulation?
#   eintrag_dict(e) Eintrag als dict (für Zuletzt / Favoriten)
#   BEREICH_ORDNER  Bereich -> Inhalts-Ordner      BEREICH_ICON  Bereich -> Icon
#   BEREICH_TEXT    Bereich -> Kurzbeschreibung (Kacheln auf der Startseite)
#
# Die Suchlogik (Punkte, Tippfehler-Toleranz): programmieren/engine/suche.py -> Suchmaschine
# WER RUFT DAS AUF?  main.py (BEREICHE), gui/gesamtsuche.py (Startseite im Fenster), web/wiki/ (Webversion)
# =============================================================================

import os
import threading

import config                                                          # -> config.py
import bauteile.rechner as rechner_registry                            # -> bauteile/rechner/__init__.py
from bauteile.rechner.rechner_info import KATEGORIEN, RECHNER_INFO     # -> bauteile/rechner/rechner_info.py
from programmieren.engine import lader                                 # -> programmieren/engine/lader.py
from programmieren.engine.suche import Suchmaschine                    # -> programmieren/engine/suche.py

# Bereich (Tab-Name in main.py) -> Inhalts-Ordner
BEREICH_ORDNER = {"Bauteile": "bauteile/inhalte", "Schaltungen": "schaltungen/inhalte",
                  "Digitaltechnik": "digitaltechnik/inhalte", "Messtechnik": "messtechnik/inhalte",
                  "Programmieren": "programmieren/inhalte", "Server / Linux": "server/inhalte"}
BEREICH_ICON = {"Bauteile": "🔧", "Schaltungen": "🔌", "Digitaltechnik": "💾", "Messtechnik": "📏",
                "Programmieren": "💻", "Server / Linux": "🐧", "Rechner": "🧮"}

# Kurzbeschreibung je Bereich (Startseite im Fenster UND im Web)
BEREICH_TEXT = {
    "Bauteile": "Widerstand, Kondensator, Diode, Spule, ...",
    "Schaltungen": "Von Spannungsteiler bis Endstufe – mit interaktiven Schaltplänen",
    "Digitaltechnik": "Zahlen, Logik, Schaltnetze, Schaltwerke, Busse und Speicher",
    "Rechner": "Alle Rechner an einem Ort – Suche, nach Thema oder A–Z",
    "Programmieren": "Python, C++ und C# nachschlagen - mit Suche",
    "Messtechnik": "Messgeräte, Messfehler, Sensoren, AD-Wandler",
    "Server / Linux": "Ubuntu Server per Konsole: Befehle, sudo, Dienste, Netzwerk, Sicherheit",
}

_index = None
_SPERRE = threading.Lock()        # Webversion: mehrere Anfragen gleichzeitig -> nur einer baut den Index


class Eintrag:
    """Ein Suchtreffer: Wissensseite oder Rechner (Felder so, wie die Suchmaschine sie erwartet)."""

    def __init__(self, art, bereich, eintrag_id, titel, kurz, stichworte, reihenfolge, daten, icon, ort):
        self.art, self.bereich, self.id = art, bereich, eintrag_id
        self.titel, self.kurz, self.stichworte = titel, kurz, stichworte
        self.reihenfolge, self.daten, self.icon, self.ort = reihenfolge, daten, icon, ort


def interaktiv(rechner_id):
    """Interaktive Grafik/Simulation (Titel endet bei uns immer mit „(interaktiv)“)."""
    info = RECHNER_INFO.get(rechner_id, {})
    return "interaktiv" in info.get("titel", "").lower()


def gesamtindex():
    """
    Rückgabe: {"eintraege": {schluessel: Eintrag}, "bereiche": {bereich: {"kategorien", "seiten", "rechner",
               "simulationen", "befehle"}}, "suche": Suchmaschine}
    """
    with _SPERRE:
        if _index is None:
            _index_bauen()
    return _index


def _index_bauen():
    global _index
    eintraege, bereiche = {}, {}
    for bereich, ordner in BEREICH_ORDNER.items():
        kategorien, themen, _fehler = lader.alle_laden(os.path.join(config.BASIS_PFAD, ordner))
        rechner_ids, befehle = set(), 0
        for thema in themen.values():
            daten = thema.daten
            ids = set(daten.get("rechner", [])) | set(daten.get("grafiken", []))
            rechner_ids |= ids
            befehle += sum(len(g.get("zeilen", [])) for g in daten.get("befehle", []))
            eintraege[f"{bereich}:{thema.id}"] = Eintrag(
                "seite", bereich, thema.id, thema.titel, thema.kurz, thema.stichworte, thema.reihenfolge, daten,
                thema.kategorie.icon, f"{bereich} › {thema.kategorie.name}")
        bereiche[bereich] = {"kategorien": kategorien, "seiten": len(themen), "befehle": befehle,
                             "rechner": len([r for r in rechner_ids if not interaktiv(r)]),
                             "simulationen": len([r for r in rechner_ids if interaktiv(r)])}
    vorhanden = rechner_registry.registry()
    anzahl = 0
    for nummer, (rid, info) in enumerate(RECHNER_INFO.items()):
        if rid not in vorhanden:
            continue
        anzahl += 1
        icon = KATEGORIEN.get(info["kategorie"], ("🧮",))[0]
        eintraege[f"Rechner:{rid}"] = Eintrag(
            "rechner", "Rechner", rid, info["titel"], info["beschreibung"],
            info["stichworte"] + [info["unterkategorie"], info["kategorie"]], 500 + nummer, {}, icon,
            f"Rechner › {info['kategorie']} › {info['unterkategorie']}")
    bereiche["Rechner"] = {"kategorien": list(KATEGORIEN.items()), "seiten": 0, "befehle": 0,
                           "rechner": len([r for r in vorhanden if r in RECHNER_INFO and not interaktiv(r)]),
                           "simulationen": len([r for r in vorhanden if r in RECHNER_INFO and interaktiv(r)])}
    # erst ganz am Schluss sichtbar machen - nie halb fertig
    _index = {"eintraege": eintraege, "bereiche": bereiche, "suche": Suchmaschine(eintraege),
              "anzahl_rechner": anzahl}


def eintrag_dict(e):
    return {"art": e.art, "bereich": e.bereich, "id": e.id, "titel": e.titel, "icon": e.icon}
