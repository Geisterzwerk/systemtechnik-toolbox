# =============================================================================
# bauteile/rechner/spule_rechner.py
# -----------------------------------------------------------------------------
# Alle RECHNER für die Seite "Spule".
#
#   rl_kurve           INTERAKTIV: Strom beim Ein-/Ausschalten (bauteile/grafiken/kurven.py)
#   blindwiderstand_l  XL bei Frequenz f
#   rl_zeit            τ = L/R, Endstrom, Strom nach Zeit t
#   abschaltspitze     Induktionsspannung U = L · ΔI / Δt (warum es eine Freilaufdiode braucht)
#   energie_l          gespeicherte Energie
#   lc_resonanz        Resonanzfrequenz (2 von 3 Werten)
#   reihe_parallel_l   Reihen- und Parallelschaltung (ohne Kopplung)
# =============================================================================

import math

from bauteile.grafiken.kurven import KurvenKarte                    # -> grafiken/kurven.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, anzahl_gegeben, fmt   # -> rechner/basis.py

ZWEI_PI = 2 * math.pi


def _xl(w):
    L, f = w["L"], w["f"]
    if L is None or f is None:
        raise RechnerFehler("L und f eingeben")
    XL = ZWEI_PI * f * L
    zeilen = [f"XL = {fmt(XL, 'widerstand')}"]
    if w["R"] is not None:
        Z = math.hypot(w["R"], XL)
        phi = math.degrees(math.atan2(XL, w["R"]))
        zeilen.append(f"Mit Drahtwiderstand {fmt(w['R'], 'widerstand')}: Z = {fmt(Z, 'widerstand')}, φ = {phi:.1f}°")
        if w["U"] is not None:
            zeilen.append(f"Strom bei {fmt(w['U'], 'spannung')}: I = {fmt(w['U'] / Z, 'strom')}")
    elif w["U"] is not None:
        zeilen.append(f"Strom bei {fmt(w['U'], 'spannung')}: I = {fmt(w['U'] / XL, 'strom')}")
    zeilen.append("Strom eilt der Spannung um 90° NACH (ideale Spule)")
    return zeilen


def blindwiderstand_l(master):
    return FormelRechner(
        master, "Blindwiderstand XL", "Je höher die Frequenz, desto grösser XL",
        felder=[("L", "Induktivität L", "induktivitaet"), ("f", "Frequenz f", "frequenz", {"platzhalter": "z.B. 50"}),
                ("R", "Drahtwiderstand (opt.)", "widerstand", {"platzhalter": "optional"}),
                ("U", "Spannung (optional)", "spannung", {"platzhalter": "optional"})],
        berechnen=_xl, formel="XL = 2π · f · L     Z = √(R² + XL²)")


def _rl_zeit(w):
    L, R = w["L"], w["R"]
    if L is None or R is None:
        raise RechnerFehler("L und R (Gesamtwiderstand im Stromkreis) eingeben")
    tau = L / R
    zeilen = [f"τ = L / R = {fmt(tau, 'zeit')}   ·   5τ = {fmt(5 * tau, 'zeit')}"]
    if w["U"] is not None:
        i_end = w["U"] / R
        zeilen.append(f"Endstrom I = U / R = {fmt(i_end, 'strom')}")
        if w["t"] is not None:
            i_t = i_end * (1 - math.exp(-w["t"] / tau))
            zeilen.append(f"Nach {fmt(w['t'], 'zeit')}: i = {fmt(i_t, 'strom')}  ({i_t / i_end * 100:.1f} %)")
    return zeilen


def rl_zeit(master):
    return FormelRechner(
        master, "RL-Zeiten", "Wie schnell steigt der Strom in der Spule?",
        felder=[("L", "Induktivität L", "induktivitaet"), ("R", "Widerstand R", "widerstand"),
                ("U", "Spannung U (opt.)", "spannung", {"platzhalter": "optional"}),
                ("t", "Zeit t (opt.)", "zeit", {"platzhalter": "optional"})],
        berechnen=_rl_zeit, formel="τ = L / R     i(t) = U/R · (1 − e^(−t/τ))")


def _abschaltspitze(w):
    L, I, dt = w["L"], w["I"], w["dt"]
    if None in (L, I, dt):
        raise RechnerFehler("L, Strom und Abschaltzeit eingeben")
    U = L * I / dt
    zeilen = [f"Induzierte Spannung: U = L · ΔI / Δt = {fmt(U, 'spannung')}",
              f"Gespeicherte Energie: W = ½ · L · I² = {fmt(0.5 * L * I * I, 'energie')}"]
    if U > 50:
        zeilen.append("⚠ Diese Spitze zerstört Transistoren/Kontakte → Freilaufdiode, RC-Glied oder TVS verwenden")
    zeilen.append("In der Praxis begrenzen Streukapazitäten und Durchschläge die Spitze – gefährlich bleibt sie trotzdem")
    return zeilen


def abschaltspitze(master):
    return FormelRechner(
        master, "Abschalt-Spannungsspitze", "Was passiert, wenn der Strom schlagartig unterbrochen wird?",
        felder=[("L", "Induktivität L", "induktivitaet"), ("I", "Strom vorher", "strom", {"einheit": "mA"}),
                ("dt", "Abschaltzeit Δt", "zeit", {"einheit": "µs", "platzhalter": "z.B. 1"})],
        berechnen=_abschaltspitze, formel="u = L · di / dt")


def _energie_l(w):
    if w["L"] is None or w["I"] is None:
        raise RechnerFehler("L und I eingeben")
    return [f"Energie W = ½ · L · I² = {fmt(0.5 * w['L'] * w['I'] ** 2, 'energie')}"]


def energie_l(master):
    return FormelRechner(
        master, "Energie im Magnetfeld", "Die Energie steckt im Magnetfeld (beim Kondensator im elektrischen Feld)",
        felder=[("L", "Induktivität L", "induktivitaet"), ("I", "Strom I", "strom")],
        berechnen=_energie_l, formel="W = ½ · L · I²")


def _lc(w):
    L, C, f = w["L"], w["C"], w["f"]
    if anzahl_gegeben(w, "L", "C", "f") != 2:
        raise RechnerFehler("Genau ZWEI von L, C, f0 eingeben")
    zeilen = []
    if f is None:
        f = 1 / (ZWEI_PI * math.sqrt(L * C))
        zeilen.append(f"f0 = {fmt(f, 'frequenz')}")
    elif C is None:
        C = 1 / ((ZWEI_PI * f) ** 2 * L)
        zeilen.append(f"C = {fmt(C, 'kapazitaet')}")
    else:
        L = 1 / ((ZWEI_PI * f) ** 2 * C)
        zeilen.append(f"L = {fmt(L, 'induktivitaet')}")
    zeilen.append(f"Kennwiderstand Z0 = √(L/C) = {fmt(math.sqrt(L / C), 'widerstand')}")
    zeilen.append("Bei f0 gilt XL = XC. Reihenkreis: Z minimal · Parallelkreis: Z maximal")
    return zeilen


def lc_resonanz(master):
    return FormelRechner(
        master, "LC-Schwingkreis", "Zwei Werte eingeben, der dritte wird berechnet",
        felder=[("L", "Induktivität L", "induktivitaet", {"einheit": "µH"}),
                ("C", "Kapazität C", "kapazitaet", {"einheit": "nF"}), ("f", "Resonanz f0", "frequenz", {"einheit": "kHz"})],
        berechnen=_lc, formel="f0 = 1 / (2π · √(L · C))")


def _reihe_parallel_l(w):
    werte = w["liste"]
    if not werte or any(v <= 0 for v in werte):
        raise RechnerFehler("Induktivitäten eingeben (alle > 0), z.B.  10m 22m")
    return [f"{len(werte)} Spulen (ohne magnetische Kopplung)",
            f"Reihe:    L = {fmt(sum(werte), 'induktivitaet')}",
            f"Parallel: L = {fmt(1 / sum(1 / v for v in werte), 'induktivitaet')}",
            "Wie beim Widerstand. Gekoppelte Spulen (gemeinsamer Kern) verhalten sich anders!"]


def reihe_parallel_l(master):
    return FormelRechner(
        master, "Reihen- & Parallelschaltung", "Gleich wie beim Widerstand – solange die Spulen sich nicht beeinflussen",
        felder=[("liste", "Induktivitäten", "induktivitaet", {"liste": True, "platzhalter": "10 22 4.7"})],
        berechnen=_reihe_parallel_l, formel="Reihe: L = L1 + L2 + …     Parallel: 1/L = 1/L1 + 1/L2 + …")


RECHNER = {
    "rl_kurve": lambda master: KurvenKarte(master, modus="RL"),
    "blindwiderstand_l": blindwiderstand_l,
    "rl_zeit": rl_zeit,
    "abschaltspitze": abschaltspitze,
    "energie_l": energie_l,
    "lc_resonanz": lc_resonanz,
    "reihe_parallel_l": reihe_parallel_l,
}
