# =============================================================================
# bauteile/rechner/kern.py
# -----------------------------------------------------------------------------
# RECHNER-KERN OHNE OBERFLÄCHE (kein tkinter, kein customtkinter).
# Alles hier kann auch eine Webseite (Django) oder ein Prüfskript benutzen.
#
#   RechnerFehler      Für verständliche Fehlermeldungen: raise RechnerFehler("...")
#   eingaben_pruefen() Prüfungen, die für JEDEN Rechner gelten (z.B. R nie negativ)
#   formel_auswerten() Rechnet wie der Knopf "Berechnen" - nur ohne Fenster
#   anzahl_gegeben()   Wie viele Felder sind ausgefüllt?
#   fmt                Zahl + Einheit schön ausgeben: fmt(4700, "widerstand") -> "4.7 kΩ"
#
#   FormelDaten        Beschreibung eines Formel-Rechners als DATEN:
#                      Titel, Felder, Rechenfunktion, Formeltext.
#                      daten(master)  -> baut die Karte im Fenster (FormelRechner, basis.py)
#                      daten.auswerten(werte) -> rechnet ohne Fenster
#
#   GrafikVerweis      Interaktive Grafik (Klasse mit Fenster) als VERWEIS:
#                      Die Klasse wird erst beim Öffnen geladen. So kann man die
#                      Rechner-Liste laden, ohne dass tkinter importiert wird.
#
# BEISPIEL (in einer *_rechner.py):
#
#   def _ohm(w):                                  # w = {"U": 12.0, "R": 4700.0} in Basiseinheiten
#       return [f"I = {fmt(w['U'] / w['R'], 'strom')}"]
#
#   ohm = FormelDaten("Strom", "aus U und R",
#                     felder=[("U", "Spannung U", "spannung"),
#                             ("R", "Widerstand R", "widerstand", {"einheit": "kΩ"})],
#                     berechnen=_ohm, formel="I = U / R")
#
#   RECHNER = {"ohm": ohm,
#              "rc_ladekurve": GrafikVerweis("bauteile.grafiken.kurven", "KurvenKarte", modus="RC")}
#
# WER RUFT DAS AUF?  alle *_rechner.py und rechner.py, bauteile/rechner/basis.py (Fenster-Teil),
#                    bauteile/rechner/__init__.py (Registry), pruefen_rechner.py
# =============================================================================

import importlib

from bauteile import einheiten                           # -> bauteile/einheiten.py

fmt = einheiten.formatieren                              # Kurzname für Ergebnisse


class RechnerFehler(Exception):
    """Verständliche Meldung an den Benutzer (wird im Ergebnisfeld angezeigt)."""


# Grössen, die physikalisch nie negativ sein können. Eine negative Eingabe wird
# schon VOR dem Rechnen abgefangen - so muss nicht jeder Rechner das selbst prüfen.
# (Spannung, Strom, Leistung, Temperatur und "zahl" dürfen negativ sein.)
NIE_NEGATIV = {"widerstand", "kapazitaet", "induktivitaet", "zeit", "frequenz", "laenge",
               "flaeche", "ladung", "energie", "flussdichte", "prozent"}


def eingaben_pruefen(felder, werte):
    """Prüft alle Eingaben, die für JEDEN Rechner gelten (siehe NIE_NEGATIV)."""
    for eintrag in felder:
        schluessel, beschriftung, typ = eintrag[:3]
        wert = werte.get(schluessel)
        if typ not in NIE_NEGATIV or wert is None:
            continue
        liste = wert if isinstance(wert, list) else [wert]
        if any(w < 0 for w in liste):
            raise RechnerFehler(f"{beschriftung}: darf nicht negativ sein")


def formel_auswerten(felder, berechnen, werte):
    """
    Rechnet genau so wie der Knopf "Berechnen" - nur ohne Fenster.
      felder     Felddefinitionen wie bei FormelDaten
      berechnen  Rechenfunktion des Rechners
      werte      {"U": 12.0, "R": None, ...} in Basiseinheiten
    Rückgabe: (text, ok)   ok = False -> text ist eine Fehlermeldung
    """
    try:
        eingaben_pruefen(felder, werte)
        zeilen = berechnen(werte)
    except RechnerFehler as fehler:
        return str(fehler), False
    except ZeroDivisionError:
        # Welche Felder sind 0? -> konkret nennen statt nur "Division durch 0"
        nullen = [e[1] for e in felder if werte.get(e[0]) == 0
                  or (isinstance(werte.get(e[0]), list) and 0 in werte[e[0]])]
        if nullen:
            return f"Division durch 0 – darf nicht 0 sein: {', '.join(nullen)}", False
        return "Division durch 0 – die Eingaben passen so nicht zusammen", False
    except OverflowError:
        return "Ergebnis ist zu gross – Eingaben prüfen (Einheit richtig?)", False
    except ValueError as fehler:
        return f"Ungültige Eingabe: {fehler}", False
    return "\n".join(zeilen), True


def anzahl_gegeben(werte, *schluessel):
    """Wie viele der genannten Felder sind ausgefüllt?"""
    return sum(werte[s] is not None for s in schluessel)


# =============================================================================
# FORMEL-RECHNER ALS DATEN
# =============================================================================
class FormelDaten:
    """
    felder: Liste von (schluessel, beschriftung, typ, optionen)
        typ       Einheiten-Typ aus bauteile/einheiten.py  ODER  "auswahl"  ODER  "text"
        optionen  dict (optional):
                    "einheit": "kΩ"          Startwert im Dropdown
                    "platzhalter": "z.B. 12"
                    "liste": True            mehrere Werte in einem Feld
                    "werte": [...]           nur bei typ "auswahl"
    berechnen(werte) -> Liste von Textzeilen (oder raise RechnerFehler)
    formel    kleiner grauer Text unter dem Ergebnis, z.B. "R = U / I"
    """

    def __init__(self, titel, untertitel, felder, berechnen, formel=None):
        self.titel = titel
        self.untertitel = untertitel
        self.felder = felder
        self.berechnen = berechnen
        self.formel = formel

    def __call__(self, master):
        """Karte im Fenster bauen. basis.py (mit customtkinter) wird erst JETZT geladen."""
        from bauteile.rechner.basis import FormelRechner          # -> rechner/basis.py
        return FormelRechner(master, self.titel, self.untertitel, self.felder, self.berechnen, self.formel)

    def auswerten(self, werte):
        """Rechnen ohne Fenster -> (text, ok)"""
        return formel_auswerten(self.felder, self.berechnen, werte)

    def __repr__(self):
        return f"FormelDaten({self.titel!r})"


# =============================================================================
# INTERAKTIVE GRAFIK ALS VERWEIS
# =============================================================================
class GrafikVerweis:
    """
    GrafikVerweis("schaltungen.grafiken_filter", "LcFilterSchaltung")
    GrafikVerweis("bauteile.grafiken.kurven", "KurvenKarte", modus="RC")   # mit Optionen

    verweis(master)   -> Modul laden, Klasse holen, Karte bauen (wie früher die Klasse selbst).
                         Ist die Klasse ein SchaltungsModell (ohne Fenster), baut karte_bauen()
                         die Fenster-Karte drumherum (bauteile/grafiken/schaltung_karte.py).
    verweis.klasse()  -> die Klasse (lädt das Modul, also tkinter!)
    """

    def __init__(self, modul, klassen_name, **optionen):
        self.modul = modul
        self.klassen_name = klassen_name
        self.optionen = optionen

    def klasse(self):
        return getattr(importlib.import_module(self.modul), self.klassen_name)

    def __call__(self, master):
        klasse = self.klasse()
        if hasattr(klasse, "karte_bauen"):             # reines Modell (Schaltung) -> Fenster-Karte drumherum
            return klasse.karte_bauen(master, **self.optionen)
        return klasse(master, **self.optionen)

    def __repr__(self):
        return f"GrafikVerweis({self.modul}.{self.klassen_name})"
