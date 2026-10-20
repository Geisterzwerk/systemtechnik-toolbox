# =============================================================================
# uebungen/grundlagen.py
# -----------------------------------------------------------------------------
# ÜBUNGEN ELEKTROTECHNIK-GRUNDLAGEN: Ohm, Leistung, Reihe/Parallel, Spannungsteiler, RC-Glied, LED.
# Jede Funktion bekommt einen eigenen Zufallsgenerator z und gibt zurück:
#   (text, gegeben [(Zeichen, Wert, typ)], gesucht (Zeichen, typ, Beschreibung), loesung, weg [Zeilen])
# Angemeldet werden sie unten mit kern.art(...). Das Schaltbild dazu: uebungen/schemas.py.
#
# Gerechnet wird mit den Funktionen, die auch die Rechner benutzen (schaltungen/netzwerk_mathe.py) -
# nichts doppelt. Gegebene Widerstände und Kondensatoren sind Normwerte (E12, IEC 60063).
#
# WER RUFT DAS AUF?  uebungen/aufgaben.py (lädt alle Übungs-Module)
# =============================================================================

import math

from schaltungen import netzwerk_mathe as nm                         # -> schaltungen/netzwerk_mathe.py
from uebungen.kern import _e12, _f, art                              # -> uebungen/kern.py


def _ohm_strom(z):
    u = z.choice([3.3, 5.0, 9.0, 12.0, 24.0, 48.0])
    r = _e12(z, 2, 5)                                                # 100 Ω … 82 kΩ
    i = u / r
    return ("An einem Widerstand liegt eine Spannung. Wie gross ist der Strom durch den Widerstand?",
            [("U", u, "spannung"), ("R", r, "widerstand")], ("I", "strom", "Strom durch den Widerstand"), i,
            ["Ohmsches Gesetz: I = U / R", f"I = {_f(u, 'spannung')} / {_f(r, 'widerstand')}",
             f"I = {_f(i, 'strom')}"])


def _ohm_spannung(z):
    r = _e12(z, 1, 4)                                                # 10 Ω … 8.2 kΩ
    i = _e12(z, -3, -1)                                              # 1 mA … 82 mA
    u = r * i
    return ("Durch einen Widerstand fliesst ein Strom. Welche Spannung fällt am Widerstand ab?",
            [("R", r, "widerstand"), ("I", i, "strom")], ("U", "spannung", "Spannung am Widerstand"), u,
            ["Ohmsches Gesetz: U = R · I", f"U = {_f(r, 'widerstand')} · {_f(i, 'strom')}", f"U = {_f(u, 'spannung')}"])


def _ohm_widerstand(z):
    u = z.choice([1.5, 3.3, 5.0, 9.0, 12.0, 24.0])
    i = _e12(z, -4, -1)                                              # 100 µA … 82 mA
    r = u / i
    return ("An einem Bauteil werden Spannung und Strom gemessen. Wie gross ist sein Widerstand?",
            [("U", u, "spannung"), ("I", i, "strom")], ("R", "widerstand", "Widerstand"), r,
            ["Ohmsches Gesetz: R = U / I", f"R = {_f(u, 'spannung')} / {_f(i, 'strom')}", f"R = {_f(r, 'widerstand')}"])


def _leistung_ui(z):
    u = z.choice([5.0, 12.0, 24.0, 48.0, 230.0])
    i = _e12(z, -2, 1)                                               # 10 mA … 8.2 A
    p = u * i
    return ("Ein Verbraucher nimmt bei einer bestimmten Spannung einen Strom auf. Welche Leistung nimmt er auf?",
            [("U", u, "spannung"), ("I", i, "strom")], ("P", "leistung", "Leistung"), p,
            ["Leistung: P = U · I", f"P = {_f(u, 'spannung')} · {_f(i, 'strom')}", f"P = {_f(p, 'leistung')}"])


def _leistung_r(z):
    r = _e12(z, 1, 4)                                                # 10 Ω … 8.2 kΩ
    i = _e12(z, -3, -1)                                              # 1 mA … 82 mA
    p = i * i * r
    return ("Durch einen Widerstand fliesst ein Strom. Welche Leistung wird im Widerstand in Wärme umgesetzt?",
            [("R", r, "widerstand"), ("I", i, "strom")], ("P", "leistung", "Verlustleistung im Widerstand"), p,
            ["Leistung mit R und I: P = I² · R", f"P = ({_f(i, 'strom')})² · {_f(r, 'widerstand')}",
             f"P = {_f(p, 'leistung')}"])


def _reihe(z):
    r = [_e12(z, 2, 5) for _ in range(3)]
    rg = sum(r)
    return ("Drei Widerstände sind in Reihe geschaltet. Wie gross ist der Gesamtwiderstand?",
            [("R1", r[0], "widerstand"), ("R2", r[1], "widerstand"), ("R3", r[2], "widerstand")],
            ("R_ges", "widerstand", "Gesamtwiderstand"), rg,
            ["Reihenschaltung: die Widerstände addieren sich: R_ges = R1 + R2 + R3",
             f"R_ges = {_f(r[0], 'widerstand')} + {_f(r[1], 'widerstand')} + {_f(r[2], 'widerstand')}",
             f"R_ges = {_f(rg, 'widerstand')}"])


def _parallel(z):
    r1, r2 = _e12(z, 2, 5), _e12(z, 2, 5)
    rg = nm.parallel(r1, r2)
    return ("Zwei Widerstände sind parallel geschaltet. Wie gross ist der Gesamtwiderstand?",
            [("R1", r1, "widerstand"), ("R2", r2, "widerstand")], ("R_ges", "widerstand", "Gesamtwiderstand"), rg,
            ["Parallelschaltung von zwei Widerständen: R_ges = (R1 · R2) / (R1 + R2)",
             f"R_ges = ({_f(r1, 'widerstand')} · {_f(r2, 'widerstand')}) / ({_f(r1, 'widerstand')} + {_f(r2, 'widerstand')})",
             f"R_ges = {_f(rg, 'widerstand')}",
             "Kontrolle: R_ges ist immer kleiner als der kleinste Einzelwiderstand."])


def _teiler(z):
    ue = z.choice([5.0, 9.0, 12.0, 15.0, 24.0])
    r1, r2 = _e12(z, 2, 5), _e12(z, 2, 5)
    ua = nm.spannungsteiler(ue, r1, r2)["ua0"]
    return ("Ein unbelasteter Spannungsteiler: R1 liegt oben, R2 unten. Wie gross ist die Ausgangsspannung an R2?",
            [("Ue", ue, "spannung"), ("R1", r1, "widerstand"), ("R2", r2, "widerstand")],
            ("Ua", "spannung", "Ausgangsspannung an R2"), ua,
            ["Spannungsteiler-Regel: Ua = Ue · R2 / (R1 + R2)",
             f"Ua = {_f(ue, 'spannung')} · {_f(r2, 'widerstand')} / ({_f(r1, 'widerstand')} + {_f(r2, 'widerstand')})",
             f"Ua = {_f(ua, 'spannung')}"])


def _teiler_belastet(z):
    ue = z.choice([5.0, 9.0, 12.0, 15.0, 24.0])
    r1, r2 = _e12(z, 3, 5), _e12(z, 3, 5)                            # 1 kΩ … 82 kΩ
    rl = _e12(z, 3, 6)                                               # 1 kΩ … 820 kΩ
    e = nm.spannungsteiler(ue, r1, r2, rl)
    return ("Ein Spannungsteiler (R1 oben, R2 unten) wird mit einem Lastwiderstand RL parallel zu R2 belastet. "
            "Wie gross ist die Ausgangsspannung?",
            [("Ue", ue, "spannung"), ("R1", r1, "widerstand"), ("R2", r2, "widerstand"), ("RL", rl, "widerstand")],
            ("Ua", "spannung", "Ausgangsspannung mit Last"), e["ua"],
            ["1. R2 und RL parallel: R2∥RL = (R2 · RL) / (R2 + RL)",
             f"   R2∥RL = ({_f(r2, 'widerstand')} · {_f(rl, 'widerstand')}) / ({_f(r2, 'widerstand')} + {_f(rl, 'widerstand')}) = {_f(e['r_unten'], 'widerstand')}",
             "2. Spannungsteiler-Regel mit R2∥RL: Ua = Ue · R2∥RL / (R1 + R2∥RL)",
             f"   Ua = {_f(ue, 'spannung')} · {_f(e['r_unten'], 'widerstand')} / ({_f(r1, 'widerstand')} + {_f(e['r_unten'], 'widerstand')})",
             f"   Ua = {_f(e['ua'], 'spannung')}",
             f"Zum Vergleich ohne Last: {_f(e['ua0'], 'spannung')} - die Last zieht die Spannung nach unten."])


def _rc_tau(z):
    r = _e12(z, 2, 6)                                                # 100 Ω … 820 kΩ
    c = _e12(z, -9, -4)                                              # 1 nF … 82 µF
    tau = r * c
    return ("Ein Kondensator wird über einen Widerstand geladen. Wie gross ist die Zeitkonstante τ?",
            [("R", r, "widerstand"), ("C", c, "kapazitaet")], ("τ", "zeit", "Zeitkonstante"), tau,
            ["Zeitkonstante: τ = R · C", f"τ = {_f(r, 'widerstand')} · {_f(c, 'kapazitaet')}", f"τ = {_f(tau, 'zeit')}",
             "Nach 5 τ gilt der Kondensator als voll geladen (über 99 %)."])


def _rc_laden(z):
    ue = z.choice([5.0, 10.0, 12.0, 24.0])
    r = _e12(z, 3, 5)                                                # 1 kΩ … 82 kΩ
    c = _e12(z, -7, -4)                                              # 100 nF … 82 µF
    tau = r * c
    faktor = z.choice([0.5, 1.0, 2.0, 3.0])
    t = float(f"{faktor * tau:.3g}")                                 # glatte Zeitangabe
    uc = ue * (1 - math.exp(-t / tau))
    return ("Ein leerer Kondensator wird zum Zeitpunkt t = 0 über einen Widerstand an eine Gleichspannung geschaltet. "
            "Welche Spannung hat der Kondensator nach der Zeit t?",
            [("Ue", ue, "spannung"), ("R", r, "widerstand"), ("C", c, "kapazitaet"), ("t", t, "zeit")],
            ("uC", "spannung", "Kondensatorspannung zum Zeitpunkt t"), uc,
            ["1. Zeitkonstante: τ = R · C", f"   τ = {_f(r, 'widerstand')} · {_f(c, 'kapazitaet')} = {_f(tau, 'zeit')}",
             "2. Ladekurve: uC = Ue · (1 − e^(−t/τ))",
             f"   t/τ = {_f(t, 'zeit')} / {_f(tau, 'zeit')} = {t / tau:.3g}",
             f"   uC = {_f(ue, 'spannung')} · (1 − e^(−{t / tau:.3g})) = {_f(uc, 'spannung')}",
             "Merkhilfe: nach 1 τ sind es 63 %, nach 2 τ 86 %, nach 3 τ 95 % der Endspannung."])


def _led_vorwiderstand(z):
    ub = z.choice([5.0, 9.0, 12.0, 24.0])
    uf = z.choice([1.8, 2.0, 2.1, 3.0, 3.2])                         # Werte stehen in der Aufgabe (Datenblatt)
    i_f = z.choice([0.002, 0.005, 0.01, 0.015, 0.02])
    r = (ub - uf) / i_f
    return ("Eine LED soll an einer Gleichspannung betrieben werden. Laut Datenblatt gelten die Flussspannung UF "
            "und der Strom IF. Wie gross muss der Vorwiderstand sein (genauer Wert, noch kein Normwert)?",
            [("UB", ub, "spannung"), ("UF", uf, "spannung"), ("IF", i_f, "strom")],
            ("RV", "widerstand", "Vorwiderstand"), r,
            ["Am Vorwiderstand liegt der Rest der Spannung: U_R = UB − UF",
             f"U_R = {_f(ub, 'spannung')} − {_f(uf, 'spannung')} = {_f(ub - uf, 'spannung')}",
             "Ohmsches Gesetz: RV = U_R / IF", f"RV = {_f(ub - uf, 'spannung')} / {_f(i_f, 'strom')} = {_f(r, 'widerstand')}",
             "In der Praxis den nächsten GRÖSSEREN Normwert wählen (der Strom wird dann etwas kleiner)."])




# ---- anmelden: (id, Titel, Bereich, Thema, Stufe, Wissensseiten, Erzeuger) -> uebungen/kern.py art() ----
W, T = ("Bauteile", "widerstand"), ("Schaltungen", "spannungsteiler")
K, RC, LED = ("Bauteile", "kondensator"), ("Schaltungen", "rc_laden_entladen"), ("Bauteile", "led")
art("ohm_strom", "Ohmsches Gesetz: Strom berechnen", "Grundlagen", "Ohmsches Gesetz", 1, [W], _ohm_strom)
art("ohm_spannung", "Ohmsches Gesetz: Spannung berechnen", "Grundlagen", "Ohmsches Gesetz", 1, [W], _ohm_spannung)
art("ohm_widerstand", "Ohmsches Gesetz: Widerstand berechnen", "Grundlagen", "Ohmsches Gesetz", 1, [W], _ohm_widerstand)
art("leistung_ui", "Leistung aus Spannung und Strom", "Grundlagen", "Leistung", 1, [W], _leistung_ui)
art("leistung_r", "Verlustleistung im Widerstand", "Grundlagen", "Leistung", 2, [W], _leistung_r)
art("reihe", "Reihenschaltung von Widerständen", "Grundlagen", "Widerstandsnetzwerke", 1, [W, T], _reihe)
art("parallel", "Parallelschaltung von Widerständen", "Grundlagen", "Widerstandsnetzwerke", 1, [W, T], _parallel)
art("teiler", "Spannungsteiler (unbelastet)", "Schaltungen", "Spannungsteiler", 2, [T], _teiler)
art("teiler_belastet", "Spannungsteiler (belastet)", "Schaltungen", "Spannungsteiler", 2, [T], _teiler_belastet)
art("rc_tau", "RC-Glied: Zeitkonstante τ", "Schaltungen", "RC-Glied", 2, [K, RC], _rc_tau)
art("rc_laden", "RC-Glied: Spannung beim Laden", "Schaltungen", "RC-Glied", 3, [K, RC], _rc_laden)
art("led_vorwiderstand", "LED-Vorwiderstand", "Bauteile", "Dioden & LED", 2, [LED], _led_vorwiderstand)
