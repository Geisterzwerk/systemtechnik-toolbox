# =============================================================================
# bauteile/rechner/  -> Alle Rechner der Bauteil-Seiten
#
#   basis.py                 Bausteine: EinheitenEingabe, FormelRechner, ...
#   normreihen.py            E-Reihen (E6 ... E96)
#   widerstand_rechner.py    Rechner für die Seite "Widerstand"
#   kondensator_rechner.py   ... "Kondensator"   (inkl. interaktive Ladekurve)
#   spule_rechner.py         ... "Spule"         (inkl. interaktive RL-Kurve)
#   trafo_rechner.py         ... "Transformator" (inkl. Animation)
#   dioden_rechner.py        ... "Diode"         (inkl. interaktive Kennlinie)
#   transistor_rechner.py    ... "Transistor"    (inkl. Simulator)
#   relais_rechner.py        ... "Relais"
#
#   *_mathe.py               reine Rechenfunktionen (ohne GUI, einzeln testbar):
#                            dioden_mathe.py, transistor_mathe.py, relais_mathe.py
#
# Auch interaktive Grafiken sind hier registriert und können im Wissen-Teil
# über  "grafiken": ["trafo_animation"]  eingebunden werden.
#
# Eine Themen-Datei (bauteile/inhalte/...) nennt ihre Rechner per ID:
#     "rechner": ["ohm_leistung", "spannungsteiler"]
# erstellen(master, "ohm_leistung") baut dann die passende Karte.
#
# NEUE RECHNER-DATEI? Unten in _MODULE eintragen (nur der Dateiname ohne .py).
#
# WARUM WERDEN DIE MODULE ERST SPÄTER GELADEN?
#   Grafiken wie grafiken/dioden_kennlinie.py brauchen die Mathe aus diesem Paket
#   (rechner/dioden_mathe.py), und dioden_rechner.py braucht umgekehrt die Grafik.
#   Würden hier oben alle Rechner sofort importiert, entstünde ein Import-Kreis.
#   Deshalb: Registry erst beim ersten erstellen() aufbauen (registry()).
# =============================================================================

import importlib

_MODULE = ["widerstand_rechner", "kondensator_rechner", "spule_rechner", "trafo_rechner",
           "dioden_rechner", "transistor_rechner", "relais_rechner"]

_REGISTRY = {}


def registry():
    """ID -> Fabrik-Funktion aller Rechner. Wird beim ersten Aufruf aufgebaut."""
    if not _REGISTRY:
        for name in _MODULE:
            modul = importlib.import_module(f"bauteile.rechner.{name}")     # -> rechner/<name>.py
            _REGISTRY.update(modul.RECHNER)
    return _REGISTRY


def erstellen(master, rechner_id):
    """Baut die Rechner-Karte mit der ID 'rechner_id' (oder einen Hinweis, falls unbekannt)."""
    fabrik = registry().get(rechner_id)
    if fabrik is None:
        from core.layout import Karte, WrapLabel      # nur hier gebraucht
        karte = Karte(master, titel="Rechner fehlt")
        WrapLabel(karte.body, text=f"Kein Rechner mit der ID „{rechner_id}“ gefunden.").grid(
            row=0, column=0, sticky="ew")
        return karte
    return fabrik(master)
