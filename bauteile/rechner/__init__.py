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
#   transistor_rechner.py    ... Zusatz-Rechner Bipolartransistor (PNP, Schaltzustand, PWM-Verluste)
#   relais_rechner.py        ... "Relais" (inkl. Freilauf-Vergleich, auch auf Diode/MOSFET)
#   messtechnik/rechner.py   ... Bereich Messtechnik (liegt im Ordner messtechnik/)
#   schaltungen/rechner.py   ... Bereich Schaltungen (inkl. interaktive Schaltpläne)
#
#   *_mathe.py               reine Rechenfunktionen (ohne GUI, einzeln testbar):
#                            transistor_mathe.py, relais_mathe.py
#
# Eine Themen-Datei (bauteile/inhalte/...) nennt ihre Rechner per ID:
#     "rechner": ["ohm_leistung", "spannungsteiler"]
# Auch interaktive Grafiken sind hier registriert und können im Wissen-Teil
# über  "grafiken": ["trafo_animation"]  eingebunden werden.
#
# NEUE RECHNER-DATEI? Unten in _MODULE eintragen (voller Modulname).
#
# WARUM WERDEN DIE MODULE ERST SPÄTER GELADEN?
#   Grafiken brauchen oft Bausteine aus diesem Paket (z.B. rechner/basis.py),
#   und die Rechner brauchen umgekehrt die Grafiken. Würden hier oben alle
#   Rechner sofort importiert, entstünde ein Import-Kreis.
#   Deshalb: Registry erst beim ersten erstellen() aufbauen (registry()).
# =============================================================================

import importlib

_MODULE = [
    "bauteile.rechner.widerstand_rechner",     # -> rechner/widerstand_rechner.py
    "bauteile.rechner.kondensator_rechner",    # -> rechner/kondensator_rechner.py
    "bauteile.rechner.spule_rechner",          # -> rechner/spule_rechner.py
    "bauteile.rechner.trafo_rechner",          # -> rechner/trafo_rechner.py
    "bauteile.rechner.halbleiter_rechner",     # -> rechner/halbleiter_rechner.py
    "bauteile.rechner.transistor_rechner",     # -> rechner/transistor_rechner.py
    "bauteile.rechner.relais_rechner",         # -> rechner/relais_rechner.py
    "messtechnik.rechner",                     # -> messtechnik/rechner.py
    "schaltungen.rechner",                     # -> schaltungen/rechner.py
    "digitaltechnik.rechner",                  # -> digitaltechnik/rechner.py
]

_REGISTRY = {}


def registry():
    """ID -> Fabrik-Funktion aller Rechner. Wird beim ersten Aufruf aufgebaut."""
    if not _REGISTRY:
        for name in _MODULE:
            modul = importlib.import_module(name)
            for rechner_id in modul.RECHNER:
                if rechner_id in _REGISTRY:            # gleiche ID zweimal -> sofort sichtbar machen
                    print(f"[rechner] WARNUNG: Rechner-ID '{rechner_id}' ist doppelt vergeben ({name})")
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
