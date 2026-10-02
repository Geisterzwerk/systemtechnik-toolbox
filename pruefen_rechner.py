# =============================================================================
# pruefen_rechner.py  -  prüft ALLE Rechner mit bekannten Werten und Grenzfällen
# -----------------------------------------------------------------------------
# Starten im Projektordner:
#     python pruefen_rechner.py          nur Fehler + Zusammenfassung
#     python pruefen_rechner.py -v       jede einzelne Prüfung anzeigen
#     python pruefen_rechner.py --gui    zusätzlich jede Rechner-Karte in einem
#                                        versteckten Fenster aufbauen (dauert länger)
#
# WAS WIRD GEPRÜFT?
#   1) BEKANNTE WERTE    pruefung/rechner_faelle.py: Eingabe wie im Fenster getippt
#                        -> stimmt das Ergebnis mit der Rechnung von Hand überein?
#   2) REINE FUNKTIONEN  *_mathe.py, Farbcode, SMD-Code, Normreihen ...
#   3) GRENZFÄLLE        Jeder Formel-Rechner bekommt automatisch leere Felder, 0,
#                        negative, winzige und riesige Werte. Erlaubt ist:
#                        ein Ergebnis ODER eine verständliche Meldung.
#                        FEHLER sind: Absturz, "nan"/"inf"/"None" im Ergebnis,
#                        englische Python-Meldung (z.B. "math domain error").
#   4) VERWEISE          Jede Rechner-ID in den Inhalten gibt es wirklich, keine ID doppelt,
#                        RECHNER_INFO vollständig (Kategorie, Stichworte, Wissensseite),
#                        Schaltungs- und Digitaltechnik-Seiten mit allen Pflichtabschnitten,
#                        jeder Rechner hat mindestens einen Beispielfall.
#
# Die Rechner werden OHNE Fenster geprüft: FormelRechner wird beim Laden durch
# einen "Rekorder" ersetzt, der sich nur Felder und Rechenfunktion merkt.
# Gerechnet wird mit basis.formel_auswerten() - genau wie beim Knopf "Berechnen".
#
# Ergebnis: Exit-Code 0 = alles ok, 1 = mindestens ein Fehler
# =============================================================================

import importlib
import math
import os
import random
import re
import sys

basis_ordner = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, basis_ordner)
sys.stdout.reconfigure(encoding="utf-8")                 # Windows-Konsole: Ω, µ, ² richtig anzeigen

from bauteile import einheiten                           # -> bauteile/einheiten.py
from bauteile import rechner as rechner_paket            # -> bauteile/rechner/__init__.py
from bauteile.rechner import basis                       # -> bauteile/rechner/basis.py
from bauteile.rechner.basis import RechnerFehler
from pruefung.rechner_faelle import FAELLE, FUNKTIONEN   # -> pruefung/rechner_faelle.py

AUSFUEHRLICH = "-v" in sys.argv
MIT_GUI = "--gui" in sys.argv


# =============================================================================
# REKORDER: merkt sich, was ein Rechner an FormelRechner übergeben würde
# =============================================================================
class Rekorder:
    def __init__(self, master, titel, untertitel, felder, berechnen, formel=None):
        self.titel, self.felder, self.berechnen = titel, felder, berechnen


def formel_rechner_sammeln():
    """Lädt alle Rechner-Module und gibt {id: Rekorder} und {id: "Klassenname"} zurück."""
    formel, andere = {}, {}
    for modulname in rechner_paket._MODULE:
        modul = importlib.import_module(modulname)
        original = getattr(modul, "FormelRechner", None)
        if original is not None:
            modul.FormelRechner = Rekorder               # nur für diesen Aufruf austauschen ...
        try:
            for rechner_id, fabrik in modul.RECHNER.items():
                if isinstance(fabrik, type):             # Klasse (interaktive Grafik) -> braucht ein Fenster
                    andere[rechner_id] = fabrik.__name__
                    continue
                ergebnis = fabrik(None)
                if isinstance(ergebnis, Rekorder):
                    formel[rechner_id] = ergebnis
                else:
                    andere[rechner_id] = type(ergebnis).__name__
        finally:
            if original is not None:
                modul.FormelRechner = original           # ... und wieder zurücksetzen
    return formel, andere


# =============================================================================
# EINGABE WIE IM FENSTER: Text -> Wert in Basiseinheit
# =============================================================================
def feld_optionen(eintrag):
    return eintrag[3] if len(eintrag) > 3 else {}


def texte_umwandeln(felder, texte):
    """{"R": "4k7", "I": "20"} -> {"R": 4700.0, "I": 0.02, ...}  (wie EinheitenEingabe.wert())"""
    unbekannt = set(texte) - {e[0] for e in felder}
    if unbekannt:
        raise KeyError(f"Feld gibt es nicht: {', '.join(sorted(unbekannt))}")
    werte = {}
    for eintrag in felder:
        schluessel, _, typ = eintrag[:3]
        opt = feld_optionen(eintrag)
        text = texte.get(schluessel, "")
        if typ == "auswahl":
            wert = text or opt.get("standard") or opt["werte"][0]
            if wert not in opt["werte"]:
                raise KeyError(f"Option „{wert}“ gibt es im Feld {schluessel} nicht")
            werte[schluessel] = wert
        elif typ == "text":
            werte[schluessel] = text.strip() or None              # wie TextEingabe.wert(): leer -> None
        else:
            info = einheiten.EINHEITEN[typ]
            faktor = dict(info["stufen"])[opt.get("einheit") or info["standard"]]
            umwandeln = einheiten.text_zu_liste if opt.get("liste") else einheiten.text_zu_zahl
            werte[schluessel] = umwandeln(text, typ, faktor)
    return werte


# =============================================================================
# AUSGABE
# =============================================================================
class Zaehler:
    def __init__(self):
        self.ok = 0
        self.fehler = []

    def gut(self, text):
        self.ok += 1
        if AUSFUEHRLICH:
            print(f"  ok     {text}")

    def schlecht(self, text, details=()):
        self.fehler.append(text)
        print(f"  FEHLER {text}")
        for zeile in details:
            print(f"           {zeile}")


def abschnitt(titel):
    print(f"\n=== {titel} " + "=" * max(0, 70 - len(titel)))


# =============================================================================
# 1) BEKANNTE WERTE
# =============================================================================
def bekannte_werte_pruefen(formel, z):
    abschnitt("1) Bekannte Werte (pruefung/rechner_faelle.py)")
    for rechner_id, texte, erwartet, rechnung in FAELLE:
        name = f"{rechner_id} {texte}"
        r = formel.get(rechner_id)
        if r is None:
            z.schlecht(f"{name}: Rechner-ID unbekannt")
            continue
        try:
            werte = texte_umwandeln(r.felder, texte)
        except (KeyError, ValueError) as e:
            z.schlecht(f"{name}: Eingabe nicht lesbar – {e}")
            continue
        text, ok = basis.formel_auswerten(r.felder, r.berechnen, werte)
        if isinstance(erwartet, dict):                   # Meldung erwartet
            if not ok and erwartet["fehler"] in text:
                z.gut(f"{name} -> Meldung „{text}“")
            else:
                z.schlecht(name, [f"erwartet Meldung mit „{erwartet['fehler']}“",
                                  f"bekommen ({'Ergebnis' if ok else 'Meldung'}): {text!r}", f"Rechnung: {rechnung}"])
            continue
        fehlt = [stueck for stueck in erwartet if stueck not in text]
        if ok and not fehlt:
            z.gut(name)
        else:
            z.schlecht(name, [f"fehlt: {fehlt}" if ok else "statt Ergebnis kam eine Meldung",
                              "bekommen: " + text.replace("\n", " | "), f"Rechnung: {rechnung}"])


# =============================================================================
# 2) REINE FUNKTIONEN
# =============================================================================
def gleich(a, b):
    if isinstance(b, bool) or isinstance(a, bool):
        return a == b
    if isinstance(b, (int, float)) and isinstance(a, (int, float)):
        return math.isclose(a, b, rel_tol=1e-3, abs_tol=1e-15)
    if isinstance(b, (list, tuple)) and isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(gleich(x, y) for x, y in zip(a, b))
    return a == b


def funktionen_pruefen(z):
    abschnitt("2) Reine Rechenfunktionen")
    for beschreibung, aufruf, erwartet in FUNKTIONEN:
        try:
            ergebnis = aufruf()
        except Exception as e:
            if isinstance(erwartet, dict) and isinstance(e, erwartet["wirft"]):
                z.gut(f"{beschreibung} -> {type(e).__name__}: {e}")
            else:
                z.schlecht(beschreibung, [f"Absturz {type(e).__name__}: {e}"])
            continue
        if isinstance(erwartet, dict):
            z.schlecht(beschreibung, [f"erwartet {erwartet['wirft'].__name__}, bekommen {ergebnis!r}"])
        elif gleich(ergebnis, erwartet):
            z.gut(f"{beschreibung} = {ergebnis!r}")
        else:
            z.schlecht(beschreibung, [f"erwartet {erwartet!r}", f"bekommen {ergebnis!r}"])


# =============================================================================
# 3) GRENZFÄLLE (automatisch erzeugt)
# =============================================================================
# typischer Wert je Grösse (Basiseinheit) - daraus werden die Grenzfälle gebildet
TYPISCH = {"spannung": 12.0, "strom": 0.1, "widerstand": 1e3, "leistung": 1.0, "kapazitaet": 1e-6,
           "induktivitaet": 0.01, "zeit": 1e-3, "frequenz": 50.0, "energie": 1.0, "ladung": 30e-9,
           "flussdichte": 1.0, "laenge": 0.1, "flaeche": 1.5e-6, "temperatur": 25.0, "prozent": 0.5,
           "zahl": 100.0, "volumenstrom": 1e-3, "geschwindigkeit": 1.0}
FAKTOREN = [0.0, -1.0, 1e-9, 1e9, 1.0, 2.0, 0.3]        # × typischer Wert
TEXTE = ["", "104", "4n7", "abc", "1", "999", "0", "R47", "105K", "1u0", "pp"]
ZUFALL_PRO_RECHNER = 400

PYTHON_MELDUNG = re.compile(r"^[a-z]")                   # englische Python-Meldungen beginnen klein
UNSINN = re.compile(r"\b(nan|inf|None)\b")


def feld_werte(eintrag):
    """Alle Testwerte für ein Feld (None = leer)."""
    schluessel, _, typ = eintrag[:3]
    opt = feld_optionen(eintrag)
    if typ == "auswahl":
        return list(opt["werte"])
    if typ == "text":
        return TEXTE
    t = TYPISCH.get(typ, 1.0)
    if opt.get("liste"):
        return [None, [t], [t, 2.2 * t], [0.0, t], [-t, t], [1e-9 * t, 1e9 * t], [t] * 5]
    return [None] + [f * t for f in FAKTOREN]


def standard_werte(felder):
    """Alle Felder mit einem typischen Wert gefüllt (Auswahl: erste Option)."""
    werte = {}
    for eintrag in felder:
        werte[eintrag[0]] = feld_werte(eintrag)[0 if eintrag[2] in ("auswahl",) else 1]
    return werte


def bewerten(felder, berechnen, werte):
    """None = in Ordnung, sonst Beschreibung des Problems."""
    try:
        basis.eingaben_pruefen(felder, werte)
        zeilen = berechnen(werte)
    except RechnerFehler:
        return None
    except (ZeroDivisionError, OverflowError):
        return None                                      # formel_auswerten() zeigt eine klare Meldung
    except ValueError as e:
        return f"Python-Meldung statt Erklärung: „{e}“" if PYTHON_MELDUNG.match(str(e)) else None
    except Exception as e:
        return f"ABSTURZ {type(e).__name__}: {e}"
    if not isinstance(zeilen, list) or not all(isinstance(s, str) for s in zeilen):
        return f"Ergebnis ist keine Liste von Texten: {zeilen!r}"
    text = " ".join(zeilen)
    treffer = UNSINN.search(text)
    if treffer:
        return f"„{treffer.group()}“ im Ergebnis"
    return None


def grenzfaelle_pruefen(formel, z):
    abschnitt("3) Grenzfälle (leer, 0, negativ, winzig, riesig)")
    zufall = random.Random(2026)                         # fester Startwert -> jedes Mal gleiche Fälle
    for rechner_id, r in formel.items():
        probleme = {}                                    # Problem -> erstes Beispiel

        def testen(werte):
            problem = bewerten(r.felder, r.berechnen, werte)
            if problem and problem not in probleme:
                probleme[problem] = dict(werte)

        testen({e[0]: None if e[2] not in ("auswahl", "text") else feld_werte(e)[0] for e in r.felder})
        grund = standard_werte(r.felder)
        testen(grund)
        for eintrag in r.felder:                         # jedes Feld einzeln durch alle Testwerte
            for wert in feld_werte(eintrag):
                testen({**grund, eintrag[0]: wert})
        for _ in range(ZUFALL_PRO_RECHNER):              # zufällige Kombinationen
            testen({e[0]: zufall.choice(feld_werte(e)) for e in r.felder})

        if probleme:
            for problem, beispiel in probleme.items():
                z.schlecht(f"{rechner_id}: {problem}", [f"z.B. mit {beispiel}"])
        else:
            z.gut(f"{rechner_id}")


# =============================================================================
# 4) VERWEISE & METADATEN (RECHNER_INFO)
# =============================================================================
PFLICHT_ABSCHNITTE = ("Funktion", "Dimensionierung", "Betriebszustände", "Messpunkte", "Grenzfälle")
PFLICHT_DIGITAL = ("Grundlagen", "Vorgehen", "Beispiel", "Praxis")      # digitaltechnik/inhalte/_vorlage.py
PFLICHTFELDER = ("titel", "kategorie", "unterkategorie", "beschreibung", "stichworte", "wissensseite")


def verweise_pruefen(formel, andere, z):
    abschnitt("4) Verweise & Metadaten (bauteile/rechner/rechner_info.py)")
    from bauteile.rechner.rechner_info import KATEGORIEN, RECHNER_INFO, wissensseiten_laden

    # ---- doppelte Rechner-IDs in verschiedenen Modulen ----
    gesehen = {}
    for modulname in rechner_paket._MODULE:
        for rechner_id in importlib.import_module(modulname).RECHNER:
            if rechner_id in gesehen:
                z.schlecht(f"Rechner-ID „{rechner_id}“ doppelt: {gesehen[rechner_id]} und {modulname}")
            gesehen[rechner_id] = modulname
    registry = rechner_paket.registry()

    # ---- Wissensseiten: jede Rechner-ID auf einer Seite muss es geben ----
    seiten, meldungen = wissensseiten_laden()
    for meldung in meldungen:
        z.schlecht(meldung)
    for seite_id, seite in seiten.items():
        for rechner_id in seite["rechner"]:
            if rechner_id in registry:
                z.gut(f"Seite {seite_id}: {rechner_id}")
            else:
                z.schlecht(f"Seite {seite_id}: „{rechner_id}“ ist in keinem Rechner-Modul registriert")

    # ---- Metadaten ----
    for rechner_id in sorted(set(registry) - set(RECHNER_INFO)):
        z.schlecht(f"{rechner_id}: fehlt in RECHNER_INFO (erscheint nicht im Rechner-Tab)")
    for rechner_id in sorted(set(RECHNER_INFO) - set(registry)):
        z.schlecht(f"RECHNER_INFO „{rechner_id}“: diesen Rechner gibt es nicht (Tippfehler?)")
    for rechner_id, info in RECHNER_INFO.items():
        probleme = [f"Feld „{f}“ fehlt oder ist leer" for f in PFLICHTFELDER if not info.get(f)]
        probleme += [f"unbekanntes Feld „{f}“" for f in info if f not in PFLICHTFELDER]
        if info.get("kategorie") and info["kategorie"] not in KATEGORIEN:
            probleme.append(f"Kategorie „{info['kategorie']}“ ungültig (erlaubt: {', '.join(KATEGORIEN)})")
        if len(info.get("stichworte", [])) < 3:
            probleme.append("mindestens 3 Stichworte für die Suche angeben")
        seite_id = info.get("wissensseite")
        if seite_id and seite_id not in seiten:
            probleme.append(f"Wissensseite „{seite_id}“ gibt es nicht")
        elif seite_id and rechner_id not in seiten[seite_id]["rechner"]:
            probleme.append(f"Wissensseite „{seite_id}“ zeigt diesen Rechner gar nicht (dort in \"rechner\" eintragen)")
        if probleme:
            z.schlecht(f"RECHNER_INFO {rechner_id}", probleme)
        else:
            z.gut(f"RECHNER_INFO {rechner_id}")

    # ---- Schaltungsseiten: Pflichtabschnitte (README: "keine reine Bildergalerie") ----
    from programmieren.engine import lader
    _, schaltungen, _ = lader.alle_laden(os.path.join(basis_ordner, "schaltungen", "inhalte"))
    for thema in schaltungen.values():
        text = thema.daten.get("erklaerung", "")
        fehlt = [f"## {a}" for a in PFLICHT_ABSCHNITTE if f"## {a}" not in text]
        fehlt += [f"„{f}“" for f in ("fehler", "rechner", "grafiken") if not thema.daten.get(f)]
        if fehlt:
            z.schlecht(f"Schaltung {thema.id}: es fehlt " + ", ".join(fehlt))
        else:
            z.gut(f"Schaltung {thema.id}: alle Pflichtabschnitte")
    _, digital, _ = lader.alle_laden(os.path.join(basis_ordner, "digitaltechnik", "inhalte"))
    for thema in digital.values():
        text = thema.daten.get("erklaerung", "")
        fehlt = [f"## {a}" for a in PFLICHT_DIGITAL if f"## {a}" not in text]
        fehlt += [f"„{f}“" for f in ("fehler", "rechner") if not thema.daten.get(f)]
        if fehlt:
            z.schlecht(f"Digitaltechnik {thema.id}: es fehlt " + ", ".join(fehlt))
        else:
            z.gut(f"Digitaltechnik {thema.id}: alle Pflichtabschnitte")

    # ---- Rechner, die nirgends gezeigt werden / ohne Beispielfall ----
    benutzt = {rid for seite in seiten.values() for rid in seite["rechner"]}
    for rechner_id in sorted(set(registry) - benutzt):
        print(f"  Hinweis: Rechner „{rechner_id}“ ist nur im Rechner-Tab, auf keiner Wissensseite")
    mit_fall = {f[0] for f in FAELLE}
    for rechner_id in sorted(set(formel) - mit_fall):
        z.schlecht(f"{rechner_id}: kein Beispielfall in pruefung/rechner_faelle.py")


# =============================================================================
# 5) OBERFLÄCHE (nur mit --gui)
# =============================================================================
def oberflaeche_pruefen(z):
    abschnitt("5) Jede Rechner-Karte im versteckten Fenster aufbauen")
    import customtkinter as ctk
    fenster = ctk.CTk()
    fenster.withdraw()
    for rechner_id in rechner_paket.registry():
        try:
            karte = rechner_paket.erstellen(fenster, rechner_id)
            karte.grid(row=0, column=0)
            fenster.update_idletasks()
            if hasattr(karte, "fr_rechnen"):
                karte.fr_rechnen()                       # leere Felder -> muss eine Meldung zeigen
            karte.destroy()
            z.gut(rechner_id)
        except Exception as e:
            z.schlecht(f"{rechner_id}: {type(e).__name__}: {e}")
    fenster.destroy()


# =============================================================================
def main():
    z = Zaehler()
    formel, andere = formel_rechner_sammeln()
    print(f"{len(formel)} Formel-Rechner, {len(andere)} interaktive Grafiken/Karten "
          f"({', '.join(sorted(andere))})")
    bekannte_werte_pruefen(formel, z)
    funktionen_pruefen(z)
    grenzfaelle_pruefen(formel, z)
    verweise_pruefen(formel, andere, z)
    if MIT_GUI:
        oberflaeche_pruefen(z)
    print(f"\n{z.ok} Prüfungen ok, {len(z.fehler)} Fehler")
    if not MIT_GUI:
        print("(Oberfläche nicht geprüft – dafür:  python pruefen_rechner.py --gui)")
    return 1 if z.fehler else 0


if __name__ == "__main__":
    sys.exit(main())
