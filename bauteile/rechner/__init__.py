# =============================================================================
# bauteile/rechner/  -> Alle Rechner der Bauteil-Seiten
#
#   basis.py                 Bausteine: EinheitenEingabe, FormelRechner, ...
#   normreihen.py            E-Reihen (E6 ... E96)
#   widerstand_rechner.py    Rechner für die Seite "Widerstand"
#   kondensator_rechner.py   ... "Kondensator"   (inkl. interaktive Ladekurve)
#   spule_rechner.py         ... "Spule"         (inkl. interaktive RL-Kurve)
#   trafo_rechner.py         ... "Transformator" (inkl. Animation)
#   halbleiter_rechner.py    ... Diode, Z-Diode, LED, Transistor, MOSFET (Etappe 3)
#
# Eine Themen-Datei (bauteile/inhalte/...) nennt ihre Rechner per ID:
#     "rechner": ["ohm_leistung", "spannungsteiler"]
# Auch interaktive Grafiken sind hier registriert und können im Wissen-Teil
# über  "grafiken": ["trafo_animation"]  eingebunden werden.
#
# NEUE RECHNER-DATEI? Unten importieren und in _MODULE eintragen.
# =============================================================================

from bauteile.rechner import (halbleiter_rechner,    # -> rechner/halbleiter_rechner.py
                              kondensator_rechner,   # -> rechner/kondensator_rechner.py
                              spule_rechner,         # -> rechner/spule_rechner.py
                              trafo_rechner,         # -> rechner/trafo_rechner.py
                              widerstand_rechner)    # -> rechner/widerstand_rechner.py

_MODULE = [widerstand_rechner, kondensator_rechner, spule_rechner, trafo_rechner, halbleiter_rechner]

REGISTRY = {}
for _modul in _MODULE:
    REGISTRY.update(_modul.RECHNER)


def erstellen(master, rechner_id):
    """Baut die Rechner-Karte mit der ID 'rechner_id' (oder einen Hinweis, falls unbekannt)."""
    fabrik = REGISTRY.get(rechner_id)
    if fabrik is None:
        from core.layout import Karte, WrapLabel      # nur hier gebraucht
        karte = Karte(master, titel="Rechner fehlt")
        WrapLabel(karte.body, text=f"Kein Rechner mit der ID „{rechner_id}“ gefunden.").grid(
            row=0, column=0, sticky="ew")
        return karte
    return fabrik(master)
