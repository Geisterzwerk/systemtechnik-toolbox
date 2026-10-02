# =============================================================================
# schaltungen/rechner.py
# -----------------------------------------------------------------------------
# RECHNER des Bereichs Schaltungen + Registrierung der interaktiven Schaltpläne.
#
#   stromteiler          Zweigströme beliebig vieler paralleler Widerstände
#   pull_widerstand      Pull-up/-down dimensionieren: R_min (Strom), R_max (Leckstrom, Flanke)
#   poti_last            Fehler eines belasteten Potentiometers
#   schaltung_*          INTERAKTIVE Schaltpläne (schaltungen/grafiken.py)
#
# Spannungsteiler und Brücke gibt es schon (widerstand_rechner.py, messtechnik/rechner.py)
# -> die Seiten benutzen diese Rechner per ID, hier wird nichts kopiert.
#
# Rechnung: schaltungen/netzwerk_mathe.py (ohne GUI, testbar)
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py (_MODULE) -> erstellen(master, "stromteiler")
# =============================================================================

from bauteile.rechner import normreihen                                          # -> bauteile/rechner/normreihen.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt             # -> bauteile/rechner/basis.py
from schaltungen import netzwerk_mathe as nm                                     # -> schaltungen/netzwerk_mathe.py
from schaltungen.grafiken import (BrueckeSchaltung, PotiSchaltung,               # -> schaltungen/grafiken.py
                                  PullSchaltung, SpannungsteilerSchaltung, StromteilerSchaltung)


def _fehler_umwandeln(funktion, *args):
    """ValueError aus netzwerk_mathe.py als verständliche Meldung im Ergebnisfeld zeigen."""
    try:
        return funktion(*args)
    except ValueError as fehler:
        raise RechnerFehler(str(fehler)) from None


# =============================================================================
# 1) STROMTEILER
# =============================================================================
def _stromteiler(w):
    if w["I"] is None or not w["liste"]:
        raise RechnerFehler("Gesamtstrom und mindestens zwei Widerstände eingeben, z.B.  100 300")
    if len(w["liste"]) < 2:
        raise RechnerFehler("Für einen Stromteiler mindestens zwei Widerstände eingeben")
    e = _fehler_umwandeln(nm.stromteiler, w["I"], *w["liste"])
    zeilen = [f"R_ges = {fmt(e['r_ges'], 'widerstand')}   ·   U = I · R_ges = {fmt(e['u'], 'spannung')}"]
    for nummer, (r, i, p) in enumerate(zip(w["liste"], e["stroeme"], e["leistungen"]), start=1):
        zeilen.append(f"I{nummer} = U / {fmt(r, 'widerstand')} = {fmt(i, 'strom')}  "
                      f"({i / w['I'] * 100:.1f} %),  P = {fmt(p, 'leistung')}")
    return zeilen


def stromteiler(master):
    return FormelRechner(
        master, "Stromteiler", "Wie teilt sich ein Strom auf parallele Zweige auf?",
        felder=[("I", "Gesamtstrom I", "strom", {"einheit": "mA"}),
                ("liste", "Zweig-Widerstände", "widerstand", {"liste": True, "platzhalter": "100 300"})],
        berechnen=_stromteiler, formel="I_k = I · R_ges / R_k     zwei Zweige: I1 = I · R2 / (R1 + R2)")


# =============================================================================
# 2) PULL-UP / PULL-DOWN DIMENSIONIEREN
# =============================================================================
def _pull(w):
    ub, i_max = w["Ub"], w["Imax"]
    if ub is None or i_max is None:
        raise RechnerFehler("U_B und den erlaubten Strom bei gedrücktem Taster eingeben")
    if ub <= 0 or i_max <= 0:
        raise RechnerFehler("U_B und Strom müssen grösser als 0 sein")
    r_min = ub / i_max
    zeilen = [f"R_min = U_B / I_max = {fmt(r_min, 'widerstand')}   (sonst zu viel Strom beim Drücken)"]
    grenzen = []
    if w["Ileck"]:
        r_leck = (1 - nm.HIGH_ANTEIL) * ub / w["Ileck"]
        grenzen.append(r_leck)
        zeilen.append(f"R_max (Leckstrom) = 0.3 · U_B / I_leck = {fmt(r_leck, 'widerstand')}   "
                      "(Pegel bleibt sicher über 0.7 · U_B)")
    if w["C"] and w["tr"]:
        r_flanke = w["tr"] / (w["C"] * nm.LOG_9)
        grenzen.append(r_flanke)
        zeilen.append(f"R_max (Flanke) = t_r / (2.2 · C) = {fmt(r_flanke, 'widerstand')}")
    elif w["C"] or w["tr"]:
        zeilen.append("Für die Flanke C UND t_r eingeben")
    r_max = min(grenzen) if grenzen else None
    if r_max is not None and r_max < r_min:
        raise RechnerFehler(f"Kein Widerstand passt: R_min {fmt(r_min, 'widerstand')} > R_max "
                            f"{fmt(r_max, 'widerstand')} → mehr Strom erlauben oder Leckstrom/Kapazität senken")
    # Vorschlag: geometrische Mitte zwischen den Grenzen, als E12-Wert, der sicher innerhalb liegt
    ziel = (r_min * r_max) ** 0.5 if r_max else max(r_min * 10, 4.7e3)
    vorschlag = normreihen.naechste_werte(ziel, "E12")[2]
    if r_max:
        unten = normreihen.naechste_werte(r_min, "E12")[1]          # nächst GRÖSSERER Normwert
        oben = normreihen.naechste_werte(r_max, "E12")[0]           # nächst KLEINERER Normwert
        vorschlag = min(max(vorschlag, unten), oben) if unten <= oben else None
    if vorschlag is None:
        zeilen.append("Kein E12-Wert liegt dazwischen → E24/E96 verwenden oder Grenzen lockern")
    else:
        zeilen.append(f"Vorschlag (E12): {fmt(vorschlag, 'widerstand')}  →  Strom gedrückt "
                      f"{fmt(ub / vorschlag, 'strom')}, Verlust {fmt(ub * ub / vorschlag, 'leistung')}")
    zeilen.append("Typisch: Taster 4.7 … 47 kΩ · I²C 1 … 10 kΩ · interne µC-Pull-ups ca. 20 … 50 kΩ")
    return zeilen


def pull_widerstand(master):
    return FormelRechner(
        master, "Pull-up / Pull-down dimensionieren", "Grenzen für R aus Strom, Leckstrom und Flanke",
        felder=[("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 3.3"}),
                ("Imax", "Strom gedrückt max.", "strom", {"einheit": "mA", "platzhalter": "z.B. 1"}),
                ("Ileck", "Leckstrom (opt.)", "strom", {"einheit": "µA", "platzhalter": "Datenblatt, z.B. 1"}),
                ("C", "Kapazität (opt.)", "kapazitaet", {"einheit": "pF", "platzhalter": "Pin + Leitung"}),
                ("tr", "Flanke t_r max (opt.)", "zeit", {"einheit": "µs", "platzhalter": "10 → 90 %"})],
        berechnen=_pull, formel="R_min = U_B / I_max     R_max = 0.3 · U_B / I_leck     R_max = t_r / (2.2 · C)")


# =============================================================================
# 3) POTENTIOMETER MIT LAST
# =============================================================================
def _poti(w):
    if None in (w["Ue"], w["Rp"], w["RL"]):
        raise RechnerFehler("Ue, R_P und R_L eingeben")
    anteil = 0.5 if w["a"] is None else w["a"]
    e = _fehler_umwandeln(nm.poti_teiler, w["Ue"], w["Rp"], anteil, w["RL"])
    kurve = nm.poti_kennlinie(w["Rp"], w["RL"], punkte=101)
    groesster = min(kurve, key=lambda k: k[1] - k[0])               # grösste Abweichung nach unten
    zeilen = [f"Bei {anteil * 100:g} %: Ua = {fmt(e['ua'], 'spannung')}  (ohne Last {fmt(e['ua0'], 'spannung')}, "
              f"Fehler {fmt(e['fehler'], 'spannung')})",
              f"Grösster Fehler bei ca. {groesster[0] * 100:.0f} %: {(groesster[1] - groesster[0]) * 100:+.1f} % von Ue",
              f"R_L / R_P = {w['RL'] / w['Rp']:.3g}   ·   Laststrom {fmt(e['i_last'], 'strom')}"]
    if w["RL"] < 10 * w["Rp"]:
        zeilen.append("⚠ R_L < 10 · R_P → kleineres Poti oder Spannungsfolger (OPV) dazwischen")
    return zeilen


def poti_last(master):
    return FormelRechner(
        master, "Potentiometer mit Last", "Wie stark verbiegt eine Last die Poti-Kennlinie?",
        felder=[("Ue", "Eingang Ue", "spannung", {"platzhalter": "z.B. 10"}),
                ("Rp", "Poti R_P", "widerstand", {"einheit": "kΩ"}),
                ("RL", "Last R_L", "widerstand", {"einheit": "kΩ"}),
                ("a", "Schleiferstellung", "prozent", {"platzhalter": "50"})],
        berechnen=_poti, formel="Ua = Ue · (R_u || R_L) / (R_o + R_u || R_L),   R_u = α · R_P")


# =============================================================================
# REGISTRIERUNG (IDs müssen sich von allen anderen unterscheiden)
# =============================================================================
RECHNER = {
    "stromteiler": stromteiler,
    "pull_widerstand": pull_widerstand,
    "poti_last": poti_last,
    "schaltung_spannungsteiler": SpannungsteilerSchaltung,
    "schaltung_stromteiler": StromteilerSchaltung,
    "schaltung_pull": PullSchaltung,
    "schaltung_poti": PotiSchaltung,
    "schaltung_bruecke": BrueckeSchaltung,
}
