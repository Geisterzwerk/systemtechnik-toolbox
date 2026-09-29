# =============================================================================
# bauteile/rechner/kondensator_rechner.py
# -----------------------------------------------------------------------------
# Alle RECHNER für die Seite "Kondensator".
#
#   rc_ladekurve       INTERAKTIV: Lade-/Entladekurve mit Schieberegler
#                      (steht in bauteile/grafiken/kurven.py, hier nur registriert)
#   rc_zeit            Wie lange dauert es bis zu Spannung X / Prozent Y?
#   rc_filter          Grenzfrequenz RC-Tief-/Hochpass (2 von 3 Werten)
#   blindwiderstand_c  Xc bei Frequenz f, Strom bei Spannung U
#   energie_c          Ladung und Energie
#   reihe_parallel_c   Reihen- und Parallelschaltung (umgekehrt wie beim Widerstand!)
#   kondensator_code   Aufdruck entschlüsseln: 104, 4n7, 1u0, 104K ...
# =============================================================================

import math

from bauteile.grafiken.kurven import KurvenKarte                    # -> grafiken/kurven.py
from bauteile.rechner import normreihen                             # -> rechner/normreihen.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, anzahl_gegeben, fmt   # -> rechner/basis.py

ZWEI_PI = 2 * math.pi


# =============================================================================
# 1) RC-ZEIT: Wie lange bis ...?
# =============================================================================
def _rc_zeit(w):
    R, C = w["R"], w["C"]
    if R is None or C is None:
        raise RechnerFehler("R und C eingeben")
    tau = R * C
    zeilen = [f"τ = R · C = {fmt(tau, 'zeit')}",
              f"1τ → 63.2 %   2τ → 86.5 %   3τ → 95.0 %   5τ → 99.3 %  (5τ = {fmt(5 * tau, 'zeit')})"]
    U0, Uz, pz = w["U0"], w["Uz"], w["p"]
    if Uz is not None:
        if U0 is None:
            raise RechnerFehler("Für eine Zielspannung auch U0 eingeben")
        pz = Uz / U0
    if pz is not None:
        if not 0 < pz < 1:
            raise RechnerFehler("Ziel muss zwischen 0 und 100 % bzw. zwischen 0 V und U0 liegen")
        t_laden = -tau * math.log(1 - pz)
        t_entladen = -tau * math.log(pz)
        text = f"{pz * 100:.1f} %" + (f" = {fmt(pz * U0, 'spannung')}" if U0 else "")
        zeilen.append(f"Laden auf {text}:   t = {fmt(t_laden, 'zeit')}  ({t_laden / tau:.2f} τ)")
        zeilen.append(f"Entladen auf {text}: t = {fmt(t_entladen, 'zeit')}  ({t_entladen / tau:.2f} τ)")
    return zeilen


def rc_zeit(master):
    return FormelRechner(
        master, "RC-Zeiten", "Wie lange dauert das Laden/Entladen bis zu einem Zielwert?",
        felder=[("R", "Widerstand R", "widerstand", {"einheit": "kΩ"}),
                ("C", "Kapazität C", "kapazitaet"),
                ("U0", "Endspannung U0", "spannung", {"platzhalter": "optional"}),
                ("Uz", "Zielspannung", "spannung", {"platzhalter": "optional"}),
                ("p", "… oder Ziel in %", "prozent", {"platzhalter": "optional"})],
        berechnen=_rc_zeit, formel="Laden: t = −τ · ln(1 − u/U0)     Entladen: t = −τ · ln(u/U0)")


# =============================================================================
# 2) RC-FILTER
# =============================================================================
def _rc_filter(w):
    R, C, f = w["R"], w["C"], w["fg"]
    if anzahl_gegeben(w, "R", "C", "fg") != 2:
        raise RechnerFehler("Genau ZWEI von R, C, fg eingeben")
    zeilen = []
    if f is None:
        f = 1 / (ZWEI_PI * R * C)
        zeilen.append(f"fg = {fmt(f, 'frequenz')}")
    elif C is None:
        C = 1 / (ZWEI_PI * R * f)
        zeilen.append(f"C = {fmt(C, 'kapazitaet')}  (E12: {fmt(normreihen.naechste_werte(C, 'E12')[2], 'kapazitaet')})")
    else:
        R = 1 / (ZWEI_PI * C * f)
        zeilen.append(f"R = {fmt(R, 'widerstand')}  (E24: {fmt(normreihen.naechste_werte(R, 'E24')[2], 'widerstand')})")
    zeilen.append(f"τ = {fmt(R * C, 'zeit')}")
    zeilen.append("Bei fg: Ausgang = 70.7 % (−3 dB), Phase 45°. Danach −20 dB pro Dekade.")
    return zeilen


def rc_filter(master):
    return FormelRechner(
        master, "RC-Filter (Tief-/Hochpass)", "Zwei Werte eingeben, der dritte wird berechnet",
        felder=[("R", "Widerstand R", "widerstand", {"einheit": "kΩ"}),
                ("C", "Kapazität C", "kapazitaet", {"einheit": "nF"}),
                ("fg", "Grenzfrequenz fg", "frequenz")],
        berechnen=_rc_filter, formel="fg = 1 / (2π · R · C)")


# =============================================================================
# 3) BLINDWIDERSTAND
# =============================================================================
def _xc(w):
    C, f = w["C"], w["f"]
    if C is None or f is None:
        raise RechnerFehler("C und f eingeben")
    Xc = 1 / (ZWEI_PI * f * C)
    zeilen = [f"Xc = {fmt(Xc, 'widerstand')}"]
    if w["U"] is not None:
        I = w["U"] / Xc
        zeilen.append(f"Strom bei {fmt(w['U'], 'spannung')} (eff): I = {fmt(I, 'strom')}")
        zeilen.append(f"Blindleistung Q = {fmt(w['U'] * I, 'leistung').replace('W', 'var')}")
    zeilen.append("Strom eilt der Spannung um 90° VORAUS")
    return zeilen


def blindwiderstand_c(master):
    return FormelRechner(
        master, "Blindwiderstand Xc", "Je höher die Frequenz, desto kleiner Xc",
        felder=[("C", "Kapazität C", "kapazitaet"), ("f", "Frequenz f", "frequenz", {"platzhalter": "z.B. 50"}),
                ("U", "Spannung (optional)", "spannung", {"platzhalter": "optional"})],
        berechnen=_xc, formel="Xc = 1 / (2π · f · C)")


# =============================================================================
# 4) ENERGIE & LADUNG
# =============================================================================
def _energie_c(w):
    C, U = w["C"], w["U"]
    if C is None or U is None:
        raise RechnerFehler("C und U eingeben")
    W = 0.5 * C * U * U
    zeilen = [f"Ladung Q = C · U = {fmt(C * U, 'ladung')}", f"Energie W = ½ · C · U² = {fmt(W, 'energie')}"]
    if w["t"] is not None:
        zeilen.append(f"Mittlere Leistung bei Entladung in {fmt(w['t'], 'zeit')}: {fmt(W / w['t'], 'leistung')}")
    if W > 0.1:
        zeilen.append("⚠ Energie gross genug für Funken/Verbrennungen – vor Arbeiten entladen!")
    return zeilen


def energie_c(master):
    return FormelRechner(
        master, "Ladung & Energie", "Wie viel Energie steckt im Kondensator?",
        felder=[("C", "Kapazität C", "kapazitaet"), ("U", "Spannung U", "spannung"),
                ("t", "Entladezeit (optional)", "zeit", {"platzhalter": "optional"})],
        berechnen=_energie_c, formel="Q = C · U     W = ½ · C · U²")


# =============================================================================
# 5) REIHE / PARALLEL
# =============================================================================
def _reihe_parallel_c(w):
    werte = w["liste"]
    if not werte or any(c <= 0 for c in werte):
        raise RechnerFehler("Kapazitäten eingeben (alle > 0), z.B.  100n 220n 47n")
    parallel = sum(werte)
    reihe = 1 / sum(1 / c for c in werte)
    zeilen = [f"{len(werte)} Kondensatoren",
              f"Parallel: C = {fmt(parallel, 'kapazitaet')}   (addieren sich)",
              f"Reihe:    C = {fmt(reihe, 'kapazitaet')}   (kleiner als der kleinste)"]
    if len(werte) > 1:
        zeilen.append("Reihe: Spannung teilt sich UMGEKEHRT zu C auf (kleines C → grosse Spannung)")
    return zeilen


def reihe_parallel_c(master):
    return FormelRechner(
        master, "Reihen- & Parallelschaltung", "Achtung: genau umgekehrt wie beim Widerstand!",
        felder=[("liste", "Kapazitäten", "kapazitaet", {"liste": True, "einheit": "nF", "platzhalter": "100 220 47"})],
        berechnen=_reihe_parallel_c, formel="Parallel: C = C1 + C2 + …     Reihe: 1/C = 1/C1 + 1/C2 + …")


# =============================================================================
# 6) KONDENSATOR-CODE
# =============================================================================
TOLERANZ_BUCHSTABE = {"B": "±0.1 pF", "C": "±0.25 pF", "D": "±0.5 pF", "F": "±1 %", "G": "±2 %",
                      "J": "±5 %", "K": "±10 %", "M": "±20 %", "Z": "+80 / −20 %"}


def kondensator_entschluesseln(code):
    """'104K' -> (1e-7, ['Erklärung', ...])"""
    c = code.strip().replace(" ", "").replace("µ", "u").replace("μ", "u")
    if not c:
        raise RechnerFehler("Code eingeben, z.B. 104, 4n7, 1u0, 104K")
    info = []
    # Toleranzbuchstabe am Ende abtrennen (nur bei Zifferncodes)
    if len(c) >= 3 and c[-1].upper() in TOLERANZ_BUCHSTABE and c[:-1].isdigit():
        info.append(f"Toleranz {c[-1].upper()} = {TOLERANZ_BUCHSTABE[c[-1].upper()]}")
        c = c[:-1]
    # Buchstabe als Komma: 4n7, 1u0, p47, 2m2
    for zeichen, faktor in (("p", 1e-12), ("n", 1e-9), ("u", 1e-6), ("m", 1e-3)):
        teile = c.lower().split(zeichen)
        if len(teile) == 2 and (teile[0] + teile[1]).isdigit():
            wert = float(f"{teile[0] or '0'}.{teile[1] or '0'}") * faktor
            return wert, [f"„{zeichen}“ steht für das Komma"] + info
    if c.isdigit() and len(c) == 3:
        wert = int(c[:2]) * 10 ** int(c[2]) * 1e-12
        info.insert(0, f"{c[:2]} × 10^{c[2]} pF")
        if c[2] == "0":
            info.append("Achtung: „100“ kann auch direkt 100 pF bedeuten (ältere Beschriftung) – im Zweifel messen")
        return wert, info
    if c.isdigit() and len(c) <= 2:
        return int(c) * 1e-12, ["1–2 Ziffern: Wert direkt in pF"] + info
    raise RechnerFehler(f"„{code}“ ist kein bekanntes Format (Beispiele: 104, 4n7, 1u0, 104K)")


def _kondensator_code(w):
    wert, info = kondensator_entschluesseln(w["code"] or "")
    return [f"C = {fmt(wert, 'kapazitaet', 5)}"] + info


def kondensator_code(master):
    return FormelRechner(
        master, "Aufdruck entschlüsseln", "Keramik-/Folienkondensatoren: 104, 4n7, 1u0, 104K",
        felder=[("code", "Aufdruck", "text", {"platzhalter": "z.B. 104K"})],
        berechnen=_kondensator_code,
        formel="3 Ziffern: 2 Ziffern + Anzahl Nullen in pF   ·   104 = 10 · 10⁴ pF = 100 nF")


# =============================================================================
# REGISTRIERUNG
# =============================================================================
RECHNER = {
    "rc_ladekurve": lambda master: KurvenKarte(master, modus="RC"),
    "rc_zeit": rc_zeit,
    "rc_filter": rc_filter,
    "blindwiderstand_c": blindwiderstand_c,
    "energie_c": energie_c,
    "reihe_parallel_c": reihe_parallel_c,
    "kondensator_code": kondensator_code,
}
