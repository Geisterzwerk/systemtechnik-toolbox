# =============================================================================
# uebungen/schaltungen.py
# -----------------------------------------------------------------------------
# ÜBUNGEN SCHALTUNGEN (Stufen 1–4): Widerstandsnetzwerke, Dioden, Transistor/MOSFET, RC/RL, OPV,
# Netzteile, Filter, Timer. Jede Aufgabe rechnet mit DENSELBEN Funktionen wie die Rechner und die
# interaktiven Schaltpläne (schaltungen/*_mathe.py) - nichts doppelt, alles schon geprüft.
# Zu jeder Aufgabe gibt es ein Schema (_s_...): gegebene Werte eingetragen, Gesuchtes als "?".
#
# Erzeuger: siehe uebungen/kern.py (Tupel = Rechenaufgabe mit Einheit).
# Werte: Widerstände/Kondensatoren/Spulen aus der E12-Reihe, Spannungen wie in der Praxis üblich.
# Annahmen stehen IMMER in der Aufgabe (z.B. U_BE = 0.7 V, ideale Z-Diode, idealer OPV).
#
# WER RUFT DAS AUF?  uebungen/aufgaben.py (lädt alle Übungs-Module)
# =============================================================================

import math

from schaltungen import dioden_mathe as dm, filter_mathe as fm, netzteil_mathe as ntm  # -> schaltungen/
from schaltungen import netzwerk_mathe as nm, opv_mathe as om, oszillator_mathe as osz
from schaltungen import rc_mathe as rm, verstaerker_mathe as vm
from uebungen.kern import _e12, _f, art                              # -> uebungen/kern.py
from uebungen.schemas import GESUCHT, ORANGE, SCHEMAS                # -> uebungen/schemas.py

U_BE = 0.7                    # V, Basis-Emitter-Spannung (Silizium) - steht so in jeder Aufgabe
U_SAT = 13.0                  # V, Aussteuergrenze eines OPV an ±15 V (Annahme in der Aufgabe)

_R, _U, _I, _C, _L, _T, _F, _P = ("widerstand", "spannung", "strom", "kapazitaet", "induktivitaet", "zeit",
                                  "frequenz", "leistung")


def _r(w):
    return _f(w, _R)


def _u(w):
    return _f(w, _U)


# =============================================================================
# WIDERSTANDSNETZWERKE
# =============================================================================
def _stromteiler(z):
    i = _e12(z, -2, -1)                                              # 10 … 82 mA
    r1, r2 = _e12(z, 2, 4), _e12(z, 2, 4)
    i1 = nm.stromteiler(i, r1, r2)["stroeme"][0]
    return ("Ein Strom teilt sich auf zwei parallele Widerstände auf. Wie gross ist der Strom durch R1?",
            [("I", i, _I), ("R1", r1, _R), ("R2", r2, _R)], ("I1", _I, "Strom durch R1"), i1,
            ["Stromteiler-Regel (zwei Zweige): I1 = I · R2 / (R1 + R2)  – der Strom bevorzugt den KLEINEREN Widerstand",
             f"I1 = {_f(i, _I)} · {_r(r2)} / ({_r(r1)} + {_r(r2)})", f"I1 = {_f(i1, _I)}",
             f"Kontrolle: I2 = I − I1 = {_f(i - i1, _I)}"])


def _s_stromteiler(p, g, ges):
    p.stromquelle(1.5, 1.6, 4.4, "I", g["I"])
    p.leitung((1.5, 1.6), (1.5, 1), (7.2, 1))
    p.leitung((1.5, 4.4), (1.5, 5), (7.2, 5))
    p.knoten(4.4, 1)
    p.knoten(4.4, 5)
    p.widerstand(4.4, 1, 4.4, 5, "R1", g["R1"], seite="links")
    p.widerstand(7.2, 1, 7.2, 5, "R2", g["R2"])
    p.strom(4.4, 1.2, 4.4, 2.0, f"I1 = {GESUCHT}", seite="rechts")


def _pullup(z):
    ub = z.choice([3.3, 5.0, 12.0, 24.0])
    r = z.choice([1e3, 2.2e3, 4.7e3, 10e3, 47e3])
    i = ub / r
    return ("Ein Taster zieht einen Eingang über einen Pull-up-Widerstand nach Masse. Welcher Strom fliesst durch "
            "den Widerstand, solange der Taster GEDRÜCKT ist? (Eingangsstrom vernachlässigen)",
            [("UB", ub, _U), ("R", r, _R)], ("I", _I, "Strom durch R bei gedrücktem Taster"), i,
            ["Gedrückt: Der Taster verbindet den Eingang mit Masse – an R liegt die ganze Spannung UB.",
             f"I = UB / R = {_u(ub)} / {_r(r)} = {_f(i, _I)}",
             "Nicht gedrückt fliesst (fast) kein Strom: Der Eingang liegt dann über R auf UB (HIGH)."])


def _s_pullup(p, g, ges):
    p.versorgung(4, 1, f"UB = {g['UB']}")
    p.widerstand(4, 1, 4, 3.6, "R", g["R"])
    p.knoten(4, 3.6)
    p.leitung((4, 3.6), (7, 3.6))
    p.anschluss(7, 3.6, "Eingang")
    p.schalter(4, 3.6, 4, 5.4, False, "Taster")
    p.masse(4, 5.4)
    p.strom(4, 1.15, 4, 1.85, f"I = {GESUCHT}", seite="links")


def _poti(z):
    ue = z.choice([5.0, 10.0, 12.0])
    rp = z.choice([1e3, 4.7e3, 10e3])
    anteil = z.choice([0.25, 0.5, 0.75])
    rl = _e12(z, 3, 5)                                               # 1 kΩ … 82 kΩ
    e = nm.poti_teiler(ue, rp, anteil, rl)
    return (f"Ein Potentiometer steht auf {anteil * 100:.0f} % (von unten gemessen) und wird mit RL belastet. "
            "Wie gross ist die Ausgangsspannung am Schleifer?",
            [("Ue", ue, _U), ("R_Poti", rp, _R), ("RL", rl, _R)], ("Ua", _U, "Spannung am Schleifer mit Last"), e["ua"],
            [f"1. Poti teilen: R_unten = {anteil * 100:.0f} % · {_r(rp)} = {_r(e['r_unten'])},  R_oben = {_r(e['r_oben'])}",
             f"2. R_unten ∥ RL = {_r(e['r_unten'])} · {_r(rl)} / ({_r(e['r_unten'])} + {_r(rl)}) = {_r(nm.parallel(e['r_unten'], rl))}",
             f"3. Teiler: Ua = Ue · (R_unten ∥ RL) / (R_oben + R_unten ∥ RL) = {_u(e['ua'])}",
             f"Ohne Last wären es {_u(e['ua0'])} – die Last zieht die Spannung nach unten."])


def _s_poti(p, g, ges):
    p.quelle(1.5, 1.6, 5.4, "Ue", g["Ue"])
    p.leitung((1.5, 1.6), (1.5, 1), (4.5, 1))
    p.leitung((1.5, 5.4), (1.5, 6), (7.5, 6))
    xs, ys = p.poti(4.5, 1, 6, 0.5, "R_Poti", g["R_Poti"])
    p.leitung((xs, ys), (7.5, ys))
    p.knoten(7.5, ys)
    p.knoten(7.5, 6)
    p.widerstand(7.5, ys, 7.5, 6, "RL", g["RL"])
    p.leitung((7.5, ys), (9.2, ys), farbe=p.leise, dick=1)
    p.leitung((7.5, 6), (9.2, 6), farbe=p.leise, dick=1)
    p.spannung(9.2, ys + 0.1, 5.9, f"Ua = {GESUCHT}")


def _bruecke(z):
    ue = z.choice([5.0, 10.0, 12.0])
    while True:
        r1, r2, r3, r4 = (_e12(z, 3, 4) for _ in range(4))          # 1 kΩ … 8.2 kΩ
        e = nm.bruecke(ue, r1, r2, r3, r4)
        if abs(e["u_d"]) > 0.05:
            break
    return ("Wheatstone-Brücke: linker Zweig R1 (oben) und R2 (unten), rechter Zweig R3 (oben) und R4 (unten). "
            "Wie gross ist die Brückenspannung U_d = U_links − U_rechts (mit Vorzeichen)?",
            [("Ue", ue, _U), ("R1", r1, _R), ("R2", r2, _R), ("R3", r3, _R), ("R4", r4, _R)],
            ("U_d", _U, "Spannung zwischen den beiden Mittelpunkten"), e["u_d"],
            [f"Linker Teiler: U_links = Ue · R2 / (R1 + R2) = {_u(e['u_links'])}",
             f"Rechter Teiler: U_rechts = Ue · R4 / (R3 + R4) = {_u(e['u_rechts'])}",
             f"U_d = U_links − U_rechts = {_u(e['u_d'])}",
             f"Abgeglichen (U_d = 0) wäre die Brücke bei R4 = R3 · R2 / R1 = {_r(e['r4_abgleich'])}."])


def _s_bruecke(p, g, ges):
    p.quelle(1.2, 1.6, 5.4, "Ue", g["Ue"])
    p.leitung((1.2, 1.6), (1.2, 1), (7.4, 1))
    p.leitung((1.2, 5.4), (1.2, 6), (7.4, 6))
    p.knoten(4, 1)
    for x, oben, unten in ((4, "R1", "R2"), (7.4, "R3", "R4")):
        p.widerstand(x, 1, x, 3.5, oben, g[oben], seite="links" if x == 4 else "rechts")
        p.widerstand(x, 3.5, x, 6, unten, g[unten], seite="links" if x == 4 else "rechts")
    p.knoten(4, 6)
    p.messpunkt(4, 3.5, "L", seite="links")
    p.messpunkt(7.4, 3.5, "R")
    a, b = p.p(4.2, 3.5), p.p(7.2, 3.5)
    p.c.create_line(*a, *b, fill="#3B82F6", width=p.dick, arrow="last", arrowshape=(p.u * 0.3, p.u * 0.34, p.u * 0.12))
    p.text(5.7, 3.1, f"U_d = {GESUCHT}", "center", farbe="#3B82F6", fett=True)


# =============================================================================
# DIODEN
# =============================================================================
def _gleichrichter(z):
    u2 = z.choice([6.0, 9.0, 12.0, 15.0, 18.0, 24.0])
    e = dm.gleichrichter("Brücke", u2)
    return ("Ein Trafo liefert die Wechselspannung U2 (Effektivwert) an einen Brückengleichrichter mit Ladeelko. "
            "Auf welche Spannung lädt sich der Elko ohne Last auf? (Silizium-Dioden, UF = 0.7 V)",
            [("U2", u2, _U), ("UF", 0.7, _U)], ("U_C", _U, "Spannung am Ladeelko (Leerlauf)"), e["u_dc"],
            ["1. Spitzenwert: Û = √2 · U2 = " + f"{_u(e['u_spitze'])}",
             "2. In der Brücke leiten immer ZWEI Dioden gleichzeitig: U_C = Û − 2 · UF",
             f"   U_C = {_u(e['u_spitze'])} − 2 · 0.7 V = {_u(e['u_dc'])}",
             "Ein Multimeter zeigt an U2 den Effektivwert – der Elko lädt aber auf den SPITZENwert."])


def _s_gleichrichter(p, g, ges, pfeil=True):
    p.wechselquelle(1.3, 1.6, 4.4, "U2", g["U2"])
    p.leitung((1.3, 1.6), (1.3, 1), (3, 1))
    p.leitung((1.3, 4.4), (1.3, 5), (3, 5))
    p.kasten(3, 0.5, 5.6, 5.5, "Brücke")
    p.text(4.3, 3, "4 × D", "center", klein=True, farbe=p.leise)
    p.leitung((5.6, 1), (7.2, 1))
    p.leitung((5.6, 5), (7.2, 5))
    p.kondensator(7.2, 1, 5, "C", g.get("C", ""), seite="links")
    if pfeil:
        p.leitung((7.2, 1), (8.6, 1), farbe=p.leise, dick=1)
        p.leitung((7.2, 5), (8.6, 5), farbe=p.leise, dick=1)
        p.spannung(8.6, 1.1, 4.9, f"U_C = {GESUCHT}")
    if "UF" in g:
        p.text(4.3, 3.6, f"UF = {g['UF']} je Diode", "center", klein=True, farbe=p.leise)


def _brumm(z):
    u2 = z.choice([9.0, 12.0, 15.0, 18.0])
    i = z.choice([0.1, 0.2, 0.5, 1.0])
    c = z.choice([470e-6, 1000e-6, 2200e-6, 4700e-6])
    e = dm.gleichrichter("Brücke", u2, i, c, f=50.0)
    return ("Brückengleichrichter am 50-Hz-Netz mit Ladeelko C, belastet mit dem Strom I. Wie gross ist die "
            "Brummspannung ΔU (Spitze-Spitze)? Rechne mit der üblichen Näherung ΔU ≈ I / (f_Brumm · C).",
            [("I", i, _I), ("C", c, _C), ("f_Netz", 50.0, _F)], ("ΔU", _U, "Brummspannung Spitze-Spitze"), e["ripple"],
            ["Bei der Brücke wird der Elko in JEDER Halbwelle nachgeladen: f_Brumm = 2 · 50 Hz = 100 Hz",
             f"ΔU ≈ I / (f_Brumm · C) = {_f(i, _I)} / (100 Hz · {_f(c, _C)}) = {_u(e['ripple'])}",
             "Die Näherung liegt auf der sicheren Seite: In Wirklichkeit ist ΔU etwas kleiner, weil der Elko "
             "nicht die ganze Periode lang entladen wird."])


def _s_brumm(p, g, ges):
    _s_gleichrichter(p, {"U2": "50 Hz", "C": g["C"]}, ges, pfeil=False)
    p.leitung((7.2, 1), (9.4, 1))
    p.leitung((7.2, 5), (9.4, 5))
    p.widerstand(9.4, 1, 9.4, 5, "Last", f"I = {g['I']}", seite="links")
    p.leitung((9.4, 1), (10.8, 1), farbe=p.leise, dick=1)
    p.leitung((9.4, 5), (10.8, 5), farbe=p.leise, dick=1)
    p.spannung(10.8, 1.1, 4.9, f"ΔU = {GESUCHT}")


def _z_strom(z):
    while True:
        ue = z.choice([12.0, 15.0, 24.0])
        uz = z.choice([3.3, 5.1, 6.8, 9.1])
        rv = _e12(z, 2, 3)                                           # 100 Ω … 820 Ω
        rl = _e12(z, 3, 4)                                           # 1 kΩ … 8.2 kΩ
        i_rv, i_l = (ue - uz) / rv, uz / rl
        if uz < ue - 2 and i_rv - i_l > 2e-3:
            break
    iz = i_rv - i_l
    return ("Eine Z-Diode stabilisiert die Spannung an einer Last RL. Wie gross ist der Strom durch die Z-Diode? "
            "(Ideale Z-Diode: die Spannung bleibt genau UZ)",
            [("Ue", ue, _U), ("UZ", uz, _U), ("RV", rv, _R), ("RL", rl, _R)], ("IZ", _I, "Strom durch die Z-Diode"), iz,
            [f"1. Strom durch RV: I_RV = (Ue − UZ) / RV = ({_u(ue)} − {_u(uz)}) / {_r(rv)} = {_f(i_rv, _I)}",
             f"2. Laststrom: IL = UZ / RL = {_u(uz)} / {_r(rl)} = {_f(i_l, _I)}",
             f"3. Der Rest fliesst durch die Z-Diode: IZ = I_RV − IL = {_f(iz, _I)}",
             "Wird IL grösser als I_RV, sinkt IZ auf 0 – dann stabilisiert die Z-Diode nicht mehr."])


def _s_z(p, g, ges, rv_wert=None, iz_text=None):
    o, u = 1.6, 5.6                                                  # oben Platz für Name + Wert von RV
    p.quelle(1.3, o + 0.6, u - 0.6, "Ue", g["Ue"])
    p.leitung((1.3, o + 0.6), (1.3, o), (2.2, o))
    p.widerstand(2.2, o, 5, o, "RV", rv_wert if rv_wert is not None else g["RV"])
    p.leitung((5, o), (8, o))
    p.knoten(6, o)
    p.knoten(6, u)
    p.diode(6, u, 6, o, "Z", f"UZ = {g['UZ']}", art="z", seite="links")
    p.widerstand(8, o, 8, u, "RL", g.get("RL", ""))
    p.leitung((1.3, u - 0.6), (1.3, u), (8, u))
    if iz_text:
        p.strom(6, o + 0.2, 6, o + 1.0, iz_text, seite="rechts")


def _s_z_strom(p, g, ges):
    _s_z(p, g, ges, iz_text=f"IZ = {GESUCHT}")


def _z_rv(z):
    ue = z.choice([12.0, 15.0, 24.0])
    uz = z.choice([3.3, 5.1, 6.8, 9.1])
    il = z.choice([0.005, 0.01, 0.02, 0.03])
    iz_min = z.choice([0.002, 0.005])
    rv = (ue - uz) / (il + iz_min)
    return ("Eine Z-Diode soll eine Last mit dem Strom IL versorgen. Damit sie sicher stabilisiert, sollen immer "
            "mindestens IZ_min durch die Z-Diode fliessen. Wie gross darf der Vorwiderstand RV HÖCHSTENS sein?",
            [("Ue", ue, _U), ("UZ", uz, _U), ("IL", il, _I), ("IZ_min", iz_min, _I)],
            ("RV_max", _R, "grösster zulässiger Vorwiderstand"), rv,
            ["Durch RV muss der Laststrom UND der Mindeststrom der Z-Diode fliessen: I_RV = IL + IZ_min",
             f"I_RV = {_f(il, _I)} + {_f(iz_min, _I)} = {_f(il + iz_min, _I)}",
             f"RV_max = (Ue − UZ) / I_RV = ({_u(ue)} − {_u(uz)}) / {_f(il + iz_min, _I)} = {_r(rv)}",
             "Praxis: den nächstKLEINEREN Normwert wählen und die Leistung der Z-Diode im Leerlauf prüfen (dann fliesst alles durch Z)."])


def _s_z_rv(p, g, ges):
    _s_z(p, {**g, "RL": f"IL = {g['IL']}"}, ges, rv_wert=GESUCHT)
    p.text(6.0, 6.2, f"IZ ≥ {g['IZ_min']}", "center", klein=True, farbe=p.leise)


# =============================================================================
# TRANSISTOR UND MOSFET
# =============================================================================
def _basiswiderstand(z):
    ust = z.choice([3.3, 5.0])
    ic = z.choice([0.02, 0.05, 0.1, 0.2, 0.5])
    b = z.choice([100, 150, 200, 250])
    ue = z.choice([2, 3, 5])
    ib = ue * ic / b
    rb = (ust - U_BE) / ib
    return ("Ein Mikrocontroller-Pin schaltet über einen NPN-Transistor eine Last mit dem Strom IC. Der Transistor "
            f"soll sicher durchschalten: Übersteuerungsfaktor ü = {ue}. Wie gross muss der Basiswiderstand sein? "
            "(U_BE = 0.7 V)",
            [("U_Pin", ust, _U), ("IC", ic, _I), ("B", float(b), "zahl")],
            ("RB", _R, "Basiswiderstand"), rb,
            [f"1. Nötiger Basisstrom: IB = ü · IC / B = {ue} · {_f(ic, _I)} / {b} = {_f(ib, _I)}",
             f"2. An RB liegt U_Pin − U_BE = {_u(ust)} − 0.7 V = {_u(ust - U_BE)}",
             f"3. RB = {_u(ust - U_BE)} / {_f(ib, _I)} = {_r(rb)}",
             "Praxis: nächstKLEINEREN Normwert wählen (mehr Basisstrom = sicher gesättigt) und den Pin-Strom prüfen."])


def _s_basiswiderstand(p, g, ges):
    p.versorgung(6, 0.9, "+UB")
    p.widerstand(6, 0.9, 6, 3.0, "Last", f"IC = {g['IC']}")
    p.npn(6, 4, "T")
    p.masse(6, 5)
    p.anschluss(1.4, 4, "Pin", seite="links")
    p.widerstand(1.4, 4, 5.1, 4, "RB", GESUCHT)
    p.text(1.4, 4.7, f"U_Pin = {g['U_Pin']}", "center", klein=True)
    p.text(6.6, 4.7, f"B = {g['B']}", "w", klein=True, farbe=p.leise)


def _mosfet_verlust(z):
    i = z.choice([0.5, 1.0, 2.0, 3.0, 5.0, 10.0])
    rds = z.choice([0.005, 0.01, 0.022, 0.05, 0.1])
    p = i * i * rds
    return ("Ein MOSFET schaltet eine Last ein (voll durchgesteuert). Welche Leistung wird im MOSFET in Wärme "
            "umgesetzt? (Umschaltverluste vernachlässigen)",
            [("ID", i, _I), ("R_DS(on)", rds, _R)], ("P", _P, "Verlustleistung im MOSFET"), p,
            ["Eingeschaltet wirkt der MOSFET wie ein kleiner Widerstand R_DS(on):  P = ID² · R_DS(on)",
             f"P = ({_f(i, _I)})² · {_r(rds)} = {_f(p, _P)}",
             "Achtung: R_DS(on) steigt mit der Temperatur (warm oft 1.5 … 2 × grösser als im Datenblatt bei 25 °C)."])


def _s_mosfet(p, g, ges):
    p.versorgung(5, 0.9, "+UB")
    p.widerstand(5, 0.9, 5, 3.0, "Last", "")
    p.nmosfet(5, 4, "")
    p.masse(5, 5)
    p.leitung((2, 4), (4.1, 4))
    p.anschluss(2, 4, "Gate", seite="links")
    p.text(5.5, 3.3, f"ID = {g['ID']}", "w", fett=True, farbe="#EF4444")
    p.text(5.5, 4.2, f"R_DS(on) = {g['R_DS(on)']}", "w", klein=True)
    p.text(5.5, 4.7, f"P = {GESUCHT}", "w", fett=True, farbe=ORANGE)


def _emitterschaltung(z):
    while True:
        ub = z.choice([12.0, 15.0])
        r1, r2 = _e12(z, 4, 5), _e12(z, 3, 5)                       # 10 … 82 kΩ, 1 … 82 kΩ
        rc, re_ = _e12(z, 3, 4), _e12(z, 2, 3)                      # 1 … 8.2 kΩ, 100 … 820 Ω
        e = vm.emitterschaltung(ub, r1, r2, rc, re_, beta=200.0)
        if e["zustand"] == "aktiv" and 0.25 * ub < e["u_ce"] < 0.75 * ub:
            break
    return ("Emitterschaltung mit Basisspannungsteiler R1 (oben) / R2 (unten), RC und RE. Wie gross ist U_CE im "
            "Arbeitspunkt? (B = 200, U_BE = 0.7 V, Basisstrom NICHT vernachlässigen)",
            [("UB", ub, _U), ("R1", r1, _R), ("R2", r2, _R), ("RC", rc, _R), ("RE", re_, _R)],
            ("U_CE", _U, "Kollektor-Emitter-Spannung im Arbeitspunkt"), e["u_ce"],
            [f"1. Ersatzquelle des Teilers: U_Th = UB · R2 / (R1 + R2) = {_u(e['u_th'])},  R_Th = R1 ∥ R2 = {_r(e['r_th'])}",
             f"2. Basismasche: IB = (U_Th − U_BE) / (R_Th + (B + 1) · RE) = {_f(e['i_b'], _I)}",
             f"3. IC = B · IB = {_f(e['i_c'], _I)},  IE = IC + IB = {_f(e['i_e'], _I)}",
             f"4. U_CE = UB − IC · RC − IE · RE = {_u(e['u_ce'])}",
             "Gut ist ein Arbeitspunkt etwa in der Mitte (U_CE ≈ UB/2): dann kann das Signal nach oben und unten schwingen."])


def _s_emitterschaltung(p, g, ges):
    o = 1.4                                                          # oben Platz für UB
    p.leitung((2.5, o), (6, o))
    p.versorgung(4.2, o, f"UB = {g['UB']}")
    p.widerstand(2.5, o, 2.5, o + 2.8, "R1", g["R1"], seite="links")
    p.widerstand(2.5, o + 2.8, 2.5, o + 5.8, "R2", g["R2"], seite="links")
    p.widerstand(6, o, 6, o + 1.8, "RC", g["RC"])
    p.npn(6, o + 2.8, "")
    p.leitung((2.5, o + 2.8), (5.1, o + 2.8))
    p.knoten(2.5, o + 2.8)
    p.widerstand(6, o + 3.8, 6, o + 5.8, "RE", g["RE"])
    p.leitung((2.5, o + 5.8), (6, o + 5.8))
    p.masse(4.2, o + 5.8)
    p.spannung(7.1, o + 1.9, o + 3.7, f"U_CE = {GESUCHT}")


def _konstantstrom(z):
    ub = z.choice([12.0, 15.0, 24.0])
    uref = z.choice([2.5, 3.3, 5.1])
    re_ = _e12(z, 1, 3)                                              # 10 … 820 Ω
    e = vm.konstantstrom_bjt(ub, uref, re_, 10.0)
    return ("Konstantstromquelle: Die Basis eines NPN-Transistors liegt fest auf U_ref, im Emitter sitzt RE. Welcher "
            "Strom fliesst durch die Last im Kollektor? (U_BE = 0.7 V, B = 200)",
            [("U_ref", uref, _U), ("RE", re_, _R)], ("I_Last", _I, "Kollektorstrom = Laststrom"), e["i"],
            ["An RE liegt U_ref − U_BE – unabhängig von der Last:",
             f"IE = (U_ref − U_BE) / RE = ({_u(uref)} − 0.7 V) / {_r(re_)} = {_f((uref - U_BE) / re_, _I)}",
             f"I_Last = IC = IE · B / (B + 1) = {_f(e['i'], _I)}  (fast gleich IE)",
             "Das gilt, solange am Transistor noch genug Spannung bleibt (nicht in Sättigung)."])


def _s_konstantstrom(p, g, ges):
    p.versorgung(6, 0.8, "+UB")
    p.widerstand(6, 0.8, 6, 2.8, "Last", "")
    p.strom(6, 0.95, 6, 1.5, f"I = {GESUCHT}", seite="links")
    p.npn(6, 3.8, "")
    p.widerstand(6, 4.8, 6, 6.6, "RE", g["RE"])
    p.masse(6, 6.6)
    p.leitung((3, 3.8), (5.1, 3.8))
    p.anschluss(3, 3.8, f"U_ref = {g['U_ref']}", seite="links")


# =============================================================================
# RC- UND RL-GLIEDER
# =============================================================================
def _rc_fg(z):
    r = _e12(z, 2, 5)
    c = _e12(z, -9, -6)                                              # 1 nF … 820 nF
    e = rm.rc_glied("Tiefpass", r, c, 1.0)
    return ("Ein RC-Tiefpass besteht aus R (Längszweig) und C (nach Masse). Wie gross ist die Grenzfrequenz?",
            [("R", r, _R), ("C", c, _C)], ("fg", _F, "Grenzfrequenz (−3 dB)"), e["fg"],
            ["fg = 1 / (2π · R · C)", f"fg = 1 / (2π · {_r(r)} · {_f(c, _C)}) = {_f(e['fg'], _F)}",
             "Bei fg ist X_C = R, die Ausgangsspannung ist auf 70.7 % (−3 dB) gesunken."])


def _s_rc(p, g, ges, f_text=None):
    p.anschluss(1, 1.5)
    p.widerstand(1, 1.5, 4.6, 1.5, "R", g["R"])
    p.leitung((4.6, 1.5), (7.2, 1.5))
    p.knoten(6, 1.5)
    p.kondensator(6, 1.5, 4.5, "C", g["C"], seite="links")
    p.leitung((1, 4.5), (7.2, 4.5))
    p.knoten(6, 4.5)
    p.anschluss(1, 4.5)
    p.anschluss(7.2, 1.5)
    p.anschluss(7.2, 4.5)
    p.text(1, 3, "ein", "center", klein=True, farbe=p.leise)
    p.text(7.2, 3, "aus", "center", klein=True, farbe=p.leise)
    p.text(4, 5.4, f_text or f"fg = {GESUCHT}", "center", farbe=ORANGE, fett=True)


def _s_rc_fg(p, g, ges):
    _s_rc(p, g, ges)


def _rc_amplitude(z):
    r = _e12(z, 3, 4)
    c = _e12(z, -8, -6)
    ue = z.choice([1.0, 5.0, 10.0])
    fg = rm.rc_glied("Tiefpass", r, c, 1.0)["fg"]
    f = float(f"{fg * z.choice([0.5, 1.0, 2.0, 5.0, 10.0]):.2g}")
    e = rm.rc_glied("Tiefpass", r, c, f)
    ua = ue * e["betrag"]
    return ("An einem RC-Tiefpass liegt eine Sinusspannung Ue (Effektivwert) mit der Frequenz f. Wie gross ist die "
            "Ausgangsspannung (Effektivwert, unbelastet)?",
            [("Ue", ue, _U), ("f", f, _F), ("R", r, _R), ("C", c, _C)], ("Ua", _U, "Ausgangsspannung"), ua,
            [f"1. Grenzfrequenz: fg = 1 / (2π · R · C) = {_f(e['fg'], _F)}",
             f"2. Verhältnis x = f / fg = {f / e['fg']:.3g}",
             f"3. Tiefpass: Ua / Ue = 1 / √(1 + x²) = {e['betrag']:.4g}  ({e['db']:.1f} dB)",
             f"4. Ua = {_u(ue)} · {e['betrag']:.4g} = {_u(ua)}",
             "Weit über fg sinkt die Spannung um 20 dB pro Dekade (10-fache Frequenz -> 1/10 der Spannung)."])


def _s_rc_amplitude(p, g, ges):
    _s_rc(p, g, ges, f_text=f"Ue = {g['Ue']}, f = {g['f']} ·  Ua = {GESUCHT}")


def _rl_tau(z):
    l = _e12(z, -3, 0)                                               # 1 mH … 820 mH
    r = _e12(z, 1, 3)                                                # 10 … 820 Ω
    tau = l / r
    return ("Eine Spule mit Vorwiderstand wird an eine Gleichspannung geschaltet. Wie gross ist die Zeitkonstante?",
            [("L", l, _L), ("R", r, _R)], ("τ", _T, "Zeitkonstante des RL-Glieds"), tau,
            ["Zeitkonstante beim RL-Glied: τ = L / R", f"τ = {_f(l, _L)} / {_r(r)} = {_f(tau, _T)}",
             "Nach 5 τ hat der Strom praktisch seinen Endwert U / R erreicht."])


def _s_rl(p, g, ges):
    o, u = 1.6, 5.6                                                  # oben Platz für Name + Wert von R
    p.quelle(1.5, o + 0.6, u - 0.6, "U", "")
    p.leitung((1.5, o + 0.6), (1.5, o), (2.6, o))
    p.widerstand(2.6, o, 5.4, o, "R", g["R"])
    p.leitung((5.4, o), (6.8, o))
    p.spule(6.8, o, 6.8, u, "L", g["L"])
    p.leitung((1.5, u - 0.6), (1.5, u), (6.8, u))
    p.text(4, u + 0.6, f"τ = {GESUCHT}", "center", farbe=ORANGE, fett=True)


def _rc_entladen(z):
    u0 = z.choice([5.0, 10.0, 12.0, 24.0])
    r = _e12(z, 3, 5)
    c = _e12(z, -7, -4)
    tau = r * c
    k = z.choice([0.5, 1.0, 2.0, 3.0])
    t = float(f"{k * tau:.3g}")
    u = u0 * math.exp(-t / tau)
    return ("Ein auf U0 geladener Kondensator wird zum Zeitpunkt t = 0 über einen Widerstand entladen. Welche "
            "Spannung hat er nach der Zeit t?",
            [("U0", u0, _U), ("R", r, _R), ("C", c, _C), ("t", t, _T)], ("uC", _U, "Kondensatorspannung nach t"), u,
            [f"1. τ = R · C = {_r(r)} · {_f(c, _C)} = {_f(tau, _T)}",
             "2. Entladekurve: uC = U0 · e^(−t/τ)",
             f"   t/τ = {t / tau:.3g}  ->  uC = {_u(u0)} · e^(−{t / tau:.3g}) = {_u(u)}",
             "Merkhilfe: nach 1 τ bleiben 37 %, nach 2 τ 14 %, nach 3 τ 5 % der Anfangsspannung."])


def _s_rc_entladen(p, g, ges):
    x_c = 3.4
    p.kondensator(x_c, 1.4, 4.6, "C", g["C"], seite="rechts")
    p.text(x_c + 0.6, 4.1, f"U0 = {g['U0']}", "w", klein=True, farbe=p.leise)
    p.leitung((x_c, 1.4), (x_c, 1), (5.0, 1))
    p.schalter(5.0, 1, 6.2, 1, False, "t = 0")
    p.leitung((6.2, 1), (7.6, 1))
    p.widerstand(7.6, 1, 7.6, 5, "R", g["R"])
    p.leitung((x_c, 4.6), (x_c, 5), (7.6, 5))
    p.leitung((x_c, 1.4), (2.2, 1.4), farbe=p.leise, dick=1)
    p.leitung((x_c, 4.6), (2.2, 4.6), farbe=p.leise, dick=1)
    p.spannung(2.2, 1.5, 4.5, f"uC = {GESUCHT}", seite="links")
    p.text(5.6, 5.6, f"gesucht nach t = {g['t']}", "center", klein=True, farbe=p.leise)


def _opv_verstaerker(z, art_name):
    while True:
        r1, r2 = _e12(z, 3, 4), _e12(z, 3, 5)
        ue = z.choice([0.1, 0.2, 0.5, 1.0, -0.2, -0.5])
        e = om.verstaerker(art_name, r1, r2, ue, 15.0)
        if not e["begrenzt"] and 0.2 < abs(e["u_a"]) < U_SAT:
            return r1, r2, ue, e


def _opv_nichtinv(z):
    r1, r2, ue, e = _opv_verstaerker(z, "nichtinvertierend")
    return ("Nichtinvertierender Verstärker: R2 vom Ausgang zum −Eingang, R1 vom −Eingang nach Masse. Wie gross ist "
            "die Ausgangsspannung? (idealer OPV an ±15 V)",
            [("Ue", ue, _U), ("R1", r1, _R), ("R2", r2, _R)], ("Ua", _U, "Ausgangsspannung"), e["u_a"],
            [f"Verstärkung: V = 1 + R2 / R1 = 1 + {_r(r2)} / {_r(r1)} = {e['vu']:.4g}",
             f"Ua = V · Ue = {e['vu']:.4g} · {_u(ue)} = {_u(e['u_a'])}",
             "Gleiches Vorzeichen wie Ue – der nichtinvertierende Verstärker dreht das Signal nicht um."])


def _opv_inv(z):
    r1, r2, ue, e = _opv_verstaerker(z, "invertierend")
    return ("Invertierender Verstärker: Ue über R1 an den −Eingang, R2 vom Ausgang zum −Eingang, +Eingang an Masse. "
            "Wie gross ist die Ausgangsspannung (mit Vorzeichen)? (idealer OPV an ±15 V)",
            [("Ue", ue, _U), ("R1", r1, _R), ("R2", r2, _R)], ("Ua", _U, "Ausgangsspannung"), e["u_a"],
            [f"Verstärkung: V = −R2 / R1 = −{_r(r2)} / {_r(r1)} = {e['vu']:.4g}",
             f"Ua = V · Ue = {e['vu']:.4g} · {_u(ue)} = {_u(e['u_a'])}",
             "Das Minus heisst: Das Signal wird umgedreht (180° Phasenverschiebung)."])


def _s_opv(p, g, ges, invertierend):
    o = p.opv(5.5, 3.6, plus_oben=False)                             # − oben, + unten
    mx, my = o["minus"]
    px, py = o["plus"]
    ax, ay = o["aus"]
    p.leitung((ax, ay), (8.6, ay))
    p.knoten(7.6, ay)
    p.leitung((mx, my), (3.6, my), (3.6, 1.6))
    p.knoten(3.6, my)
    p.widerstand(3.6, 1.6, 7.6, 1.6, "R2", g["R2"])
    p.leitung((7.6, 1.6), (7.6, ay))
    if invertierend:                                                 # Ue über R1 an −, + an Masse
        p.widerstand(0.8, my, 3.6, my, "R1", g["R1"])
        p.anschluss(0.8, my)
        p.text(0.8, my + 0.5, f"Ue = {g['Ue']}", "center", klein=True)
        p.leitung((px, py), (3.0, py), (3.0, 6.2))
        p.masse(3.0, 6.2)
    else:                                                            # Ue an +, R1 von − nach Masse (links)
        p.widerstand(1.4, my, 3.6, my, "R1", g["R1"], laenge=1.2)
        p.masse(1.4, my)
        p.leitung((px, py), (1.8, py))
        p.anschluss(1.8, py)
        p.text(1.8, py + 0.5, f"Ue = {g['Ue']}", "center", klein=True)
    p.anschluss(8.6, ay)
    p.text(8.6, ay + 0.55, f"Ua = {GESUCHT}", "center", farbe="#3B82F6", fett=True)


def _s_opv_nichtinv(p, g, ges):
    _s_opv(p, g, ges, invertierend=False)


def _s_opv_inv(p, g, ges):
    _s_opv(p, g, ges, invertierend=True)


def _addierer(z):
    while True:
        u1, u2 = z.choice([0.5, 1.0, 2.0, -1.0]), z.choice([0.2, 0.5, 1.5, -0.5])
        r1, r2, rf = _e12(z, 3, 5), _e12(z, 3, 5), _e12(z, 3, 5)
        e = om.addierer([u1, u2], [r1, r2], rf)
        if not e["begrenzt"] and 0.1 < abs(e["u_a"]) < U_SAT:
            break
    return ("Invertierender Addierer: U1 über R1 und U2 über R2 an den −Eingang, Rf vom Ausgang zum −Eingang. "
            "Wie gross ist die Ausgangsspannung? (idealer OPV an ±15 V)",
            [("U1", u1, _U), ("U2", u2, _U), ("R1", r1, _R), ("R2", r2, _R), ("Rf", rf, _R)],
            ("Ua", _U, "Ausgangsspannung"), e["u_a"],
            ["Am −Eingang ist virtuelle Masse (0 V) – die Eingangsströme addieren sich und fliessen durch Rf:",
             f"Ua = −Rf · (U1 / R1 + U2 / R2) = −{_r(rf)} · ({_u(u1)} / {_r(r1)} + {_u(u2)} / {_r(r2)})",
             f"Ua = {_u(e['u_a'])}",
             "Mit gleichen Widerständen ist Ua einfach die (umgedrehte) Summe – darum der Name Addierer."])


def _s_addierer(p, g, ges):
    o = p.opv(6, 4.4)
    mx, my = o["minus"]
    px, py = o["plus"]
    ax, ay = o["aus"]
    p.leitung((mx, my), (4.4, my))
    p.knoten(4.4, my)
    for y, name, u in ((2.4, "R1", "U1"), (my, "R2", "U2")):
        p.widerstand(1.2, y, 4.4, y, name, g[name])
        p.anschluss(1.2, y)
        p.text(1.2, y + 0.5, f"{u} = {g[u]}", "center", klein=True)
    p.leitung((4.4, 2.4), (4.4, my))
    p.knoten(4.4, 2.4)
    p.leitung((4.4, 2.4), (4.4, 1.4))
    p.widerstand(4.4, 1.4, 8.2, 1.4, "Rf", g["Rf"])
    p.leitung((8.2, 1.4), (8.2, ay))
    p.leitung((ax, ay), (9.2, ay))
    p.knoten(8.2, ay)
    p.anschluss(9.2, ay)
    p.text(9.2, ay + 0.55, f"Ua = {GESUCHT}", "center", farbe="#3B82F6", fett=True)
    p.leitung((px, py), (5.0, py), (5.0, 6.6))
    p.masse(5.0, 6.6)


def _differenz(z):
    while True:
        u1, u2 = z.choice([1.0, 1.5, 2.0, 2.5]), z.choice([1.2, 1.8, 2.2, 3.0])
        r1, r2 = _e12(z, 3, 5), _e12(z, 3, 5)
        e = om.differenz(u1, u2, r1, r2)
        if not e["begrenzt"] and 0.1 < abs(e["u_a"]) < U_SAT and u1 != u2:
            break
    return ("Differenzverstärker mit vier Widerständen (zweimal R1, zweimal R2): U1 kommt über R1 an den −Eingang, "
            "U2 über R1 an den +Eingang. Wie gross ist die Ausgangsspannung? (idealer OPV an ±15 V)",
            [("U1", u1, _U), ("U2", u2, _U), ("R1", r1, _R), ("R2", r2, _R)], ("Ua", _U, "Ausgangsspannung"), e["u_a"],
            ["Bei gleichen Widerstandspaaren verstärkt die Schaltung nur die DIFFERENZ:",
             f"Ua = R2 / R1 · (U2 − U1) = {_r(r2)} / {_r(r1)} · ({_u(u2)} − {_u(u1)})",
             f"Ua = {e['a_d']:.4g} · {_u(u2 - u1)} = {_u(e['u_a'])}",
             f"Die Gleichtaktspannung (U1 + U2)/2 = {_u(e['u_cm'])} wird (bei genauen Widerständen) nicht verstärkt."])


def _s_differenz(p, g, ges):
    o = p.opv(6.2, 3.6, plus_oben=False)
    mx, my = o["minus"]
    px, py = o["plus"]
    ax, ay = o["aus"]
    p.widerstand(1.2, my, 4.4, my, "R1", g["R1"])
    p.widerstand(1.2, py, 4.4, py, "R1 ", g["R1"], seite="unten")
    p.leitung((4.4, my), (mx, my))
    p.leitung((4.4, py), (px, py))
    p.knoten(4.4, my)
    p.knoten(4.6, py)
    p.leitung((4.4, my), (4.4, 1.2))
    p.widerstand(4.4, 1.2, 8.4, 1.2, "R2", g["R2"])
    p.leitung((8.4, 1.2), (8.4, ay))
    p.leitung((ax, ay), (9.2, ay))
    p.widerstand(4.6, py, 4.6, 6.6, "R2 ", g["R2"], seite="links")
    p.masse(4.6, 6.6)
    for y, u in ((my, "U1"), (py, "U2")):
        p.anschluss(1.2, y)
        p.text(1.0, y, f"{u} = {g[u]}", "e", klein=True)
    p.anschluss(9.2, ay)
    p.text(9.2, ay + 0.55, f"Ua = {GESUCHT}", "center", farbe="#3B82F6", fett=True)


def _schmitt(z):
    r1 = _e12(z, 3, 4)
    rf = _e12(z, 4, 6)                                               # 10 kΩ … 820 kΩ
    e = om.schmitt_schwellen("invertierend", r1, rf, 0.0, U_SAT, -U_SAT)
    return ("Invertierender Schmitt-Trigger: Signal am −Eingang, Mitkopplung Rf vom Ausgang zum +Eingang, R1 vom "
            "+Eingang nach Masse. Der Ausgang springt zwischen +13 V und −13 V. Bei welcher Eingangsspannung "
            "kippt der Ausgang von +13 V nach −13 V (obere Schaltschwelle)?",
            [("R1", r1, _R), ("Rf", rf, _R), ("U_sat", U_SAT, _U)], ("U_T+", _U, "obere Schaltschwelle"), e["u_tp"],
            ["Der +Eingang bekommt einen Teil der Ausgangsspannung (Spannungsteiler Rf / R1):",
             "U_T+ = U_sat · R1 / (R1 + Rf)",
             f"U_T+ = 13 V · {_r(r1)} / ({_r(r1)} + {_r(rf)}) = {_u(e['u_tp'])}",
             f"Untere Schwelle symmetrisch: U_T− = {_u(e['u_tm'])}, Hysterese = {_u(e['hysterese'])}"])


def _s_schmitt(p, g, ges):
    o = p.opv(5.6, 3.4, plus_oben=False)                             # − oben (Signal), + unten (Mitkopplung)
    mx, my = o["minus"]
    px, py = o["plus"]
    ax, ay = o["aus"]
    p.leitung((mx, my), (1.2, my))
    p.anschluss(1.2, my)
    p.text(1.2, my - 0.5, "Ue", "center", klein=True)
    p.leitung((px, py), (3.8, py))
    p.knoten(3.8, py)
    p.widerstand(1.6, py, 3.8, py, "R1", g["R1"], seite="unten", laenge=1.2)
    p.masse(1.6, py)
    p.leitung((3.8, py), (3.8, 5.6))
    p.widerstand(3.8, 5.6, 7.8, 5.6, "Rf", g["Rf"], seite="unten")
    p.leitung((7.8, 5.6), (7.8, ay))
    p.leitung((ax, ay), (9, ay))
    p.knoten(7.8, ay)
    p.anschluss(9, ay)
    p.text(9, ay - 0.55, "±13 V", "center", klein=True)
    p.text(1.2, 1.4, f"U_T+ = {GESUCHT}", "w", farbe=ORANGE, fett=True)


def _integrator(z):
    while True:
        r = _e12(z, 3, 5)
        c = _e12(z, -8, -6)
        ue = z.choice([0.5, 1.0, 2.0, -1.0])
        t = float(f"{r * c * z.choice([0.5, 1.0, 2.0, 5.0]):.2g}")
        ua = -ue * t / (r * c)
        if 0.2 < abs(ua) < U_SAT:
            break
    k = om.integrator_kennwerte(r, c, ue)
    return ("Ein Integrator (R am −Eingang, C in der Gegenkopplung) startet bei Ua = 0 V. Am Eingang liegt eine "
            "konstante Spannung Ue. Welche Ausgangsspannung hat er nach der Zeit t? (idealer OPV an ±15 V)",
            [("Ue", ue, _U), ("R", r, _R), ("C", c, _C), ("t", t, _T)], ("Ua", _U, "Ausgangsspannung nach t"), ua,
            ["Konstanter Strom I = Ue / R lädt C – die Ausgangsspannung ändert sich linear (Rampe):",
             f"Steigung = −Ue / (R · C) = {k['steigung']:.4g} V/s",
             f"Ua(t) = −Ue · t / (R · C) = −{_u(ue)} · {_f(t, _T)} / {_f(r * c, _T)} = {_u(ua)}",
             "Ohne Rücksetzen läuft der Integrator irgendwann in die Begrenzung (±13 V)."])


def _s_integrator(p, g, ges):
    o = p.opv(5.6, 3.8)
    mx, my = o["minus"]
    px, py = o["plus"]
    ax, ay = o["aus"]
    p.widerstand(1.2, my, 4.2, my, "R", g["R"])
    p.anschluss(1.2, my)
    p.text(1.2, my + 0.5, f"Ue = {g['Ue']}", "center", klein=True)
    p.leitung((4.2, my), (mx, my))
    p.knoten(4.2, my)
    p.leitung((4.2, my), (4.2, 1.4), (5.2, 1.4))
    p.kondensator_waagrecht(5.2, 6.4, 1.4, "C", g["C"])
    p.leitung((6.4, 1.4), (7.8, 1.4), (7.8, ay))
    p.leitung((ax, ay), (9, ay))
    p.leitung((px, py), (4.2, py), (4.2, 6.0))
    p.masse(4.2, 6.0)
    p.anschluss(9, ay)
    p.text(9, ay + 0.55, f"Ua(t) = {GESUCHT}", "center", farbe="#3B82F6", fett=True)
    p.text(9, ay + 1.05, f"t = {g['t']}", "center", klein=True, farbe=p.leise)


# =============================================================================
# NETZTEILE UND QUELLEN
# =============================================================================
def _linearregler(z):
    ua = z.choice([3.3, 5.0, 12.0])
    ue = ua + z.choice([2.0, 4.0, 7.0, 10.0])
    i = z.choice([0.1, 0.25, 0.5, 1.0])
    p = (ue - ua) * i
    return ("Ein Linearregler macht aus Ue eine feste Ausgangsspannung Ua und liefert den Strom I. Welche Leistung "
            "muss er als Wärme abgeben? (Eigenstromverbrauch vernachlässigen)",
            [("Ue", ue, _U), ("Ua", ua, _U), ("I", i, _I)], ("P", _P, "Verlustleistung im Regler"), p,
            ["Der Regler 'verbrennt' die Spannungsdifferenz:  P = (Ue − Ua) · I",
             f"P = ({_u(ue)} − {_u(ua)}) · {_f(i, _I)} = {_f(p, _P)}",
             f"Wirkungsgrad nur Ua / Ue = {ua / ue * 100:.0f} % – ab etwa 1 W braucht es meist einen Kühlkörper."])


def _s_regler(p, g, ges, regler_text="Regler", r_text=None):
    p.quelle(1.3, 1.8, 4.6, "Ue", g.get("Ue", ""))
    p.leitung((1.3, 1.8), (1.3, 1.2), (3.4, 1.2))
    p.kasten(3.4, 0.6, 6.0, 2.2, regler_text)
    p.leitung((6.0, 1.2), (8.6, 1.2))
    p.leitung((1.3, 4.6), (1.3, 5.4), (8.6, 5.4))
    p.leitung((4.7, 2.2), (4.7, 5.4))
    p.knoten(4.7, 5.4)
    p.widerstand(8.6, 1.2, 8.6, 5.4, "Last", r_text or f"I = {g.get('I', '')}")


def _s_linearregler(p, g, ges):
    _s_regler(p, g, ges)
    p.text(7.2, 0.8, f"Ua = {g['Ua']}", "center", klein=True)
    p.text(4.7, 6.1, f"P = {GESUCHT}", "center", farbe=ORANGE, fett=True)


def _lm317(z):
    r1 = 240.0
    r2 = _e12(z, 2, 4)                                               # 100 Ω … 8.2 kΩ
    ua = ntm.lm317_spannung(r1, r2)
    return ("Einstellbarer Regler LM317: R1 zwischen OUT und ADJ, R2 von ADJ nach Masse. Wie gross ist die "
            "Ausgangsspannung? (U_REF = 1.25 V, I_ADJ = 50 µA)",
            [("R1", r1, _R), ("R2", r2, _R)], ("Ua", _U, "Ausgangsspannung"), ua,
            ["Zwischen OUT und ADJ hält der LM317 genau U_REF = 1.25 V – durch R1 fliesst 1.25 V / R1.",
             "Ua = U_REF · (1 + R2 / R1) + I_ADJ · R2",
             f"Ua = 1.25 V · (1 + {_r(r2)} / 240 Ω) + 50 µA · {_r(r2)} = {_u(ua)}",
             "Der Anteil I_ADJ · R2 ist klein – viele rechnen ihn weg (Datenblatt: I_ADJ typisch 50 µA)."])


def _s_lm317(p, g, ges):
    p.leitung((1, 1.2), (3, 1.2))
    p.anschluss(1, 1.2)
    p.text(1, 1.7, "Ue", "center", klein=True)
    p.kasten(3, 0.6, 5.4, 2.2, "LM317")
    p.leitung((5.4, 1.2), (8.4, 1.2))
    p.knoten(7, 1.2)
    p.widerstand(7, 1.2, 7, 3.6, "R1", g["R1"])
    p.leitung((4.2, 2.2), (4.2, 3.6), (7, 3.6))
    p.knoten(7, 3.6)
    p.widerstand(7, 3.6, 7, 6.2, "R2", g["R2"])
    p.masse(7, 6.2)
    p.anschluss(8.4, 1.2)
    p.text(8.4, 1.75, f"Ua = {GESUCHT}", "center", farbe="#3B82F6", fett=True)
    p.text(4.2, 3.0, "ADJ", "e", klein=True, farbe=p.leise)


def _innenwiderstand(z):
    while True:                                                      # spürbarer Spannungseinbruch (≥ 2 %)
        u0 = z.choice([4.5, 9.0, 12.0, 24.0])
        rl = _e12(z, 0, 2)                                           # 1 Ω … 82 Ω
        ri_echt = _e12(z, -1, 1)                                     # 0.1 Ω … 8.2 Ω
        u_last = float(f"{u0 * rl / (rl + ri_echt):.3g}")            # gemessen: 3 Stellen
        if u0 - u_last >= 0.02 * u0:
            break
    e = ntm.innenwiderstand(u0, u_last, r_last=rl)
    return ("An einer Spannungsquelle werden zwei Messungen gemacht: ohne Last (Leerlauf) und mit dem Lastwiderstand RL. "
            "Wie gross ist der Innenwiderstand der Quelle?",
            [("U_Leerlauf", u0, _U), ("U_Last", u_last, _U), ("RL", rl, _R)], ("Ri", _R, "Innenwiderstand"), e["r_i"],
            [f"1. Laststrom: I = U_Last / RL = {_u(u_last)} / {_r(rl)} = {_f(e['i'], _I)}",
             f"2. Am Innenwiderstand fällt die Differenz ab: U_Ri = U_Leerlauf − U_Last = {_u(u0 - u_last)}",
             f"3. Ri = U_Ri / I = {_r(e['r_i'])}",
             f"Kurzschlussstrom wäre I_k = U_Leerlauf / Ri = {_f(e['i_kurz'], _I)}."])


def _s_innen(p, g, ges):
    p.kasten(0.6, 0.5, 4.2, 5.7, "")
    p.text(2.4, 5.3, "Quelle", "center", klein=True, farbe=p.leise)
    p.quelle(1.6, 1.8, 4.0, "U0", g["U_Leerlauf"])
    p.leitung((1.6, 1.8), (1.6, 1.2), (2.4, 1.2))
    p.widerstand(2.4, 1.2, 4.2, 1.2, "", "", laenge=1.0)
    p.text(3.3, 1.85, f"Ri = {GESUCHT}", "center", fett=True, farbe=ORANGE)
    p.leitung((1.6, 4.0), (1.6, 4.8), (4.2, 4.8))
    p.leitung((4.2, 1.2), (7, 1.2))
    p.leitung((4.2, 4.8), (7, 4.8))
    p.widerstand(7, 1.2, 7, 4.8, "RL", g["RL"], seite="links")
    p.leitung((7, 1.2), (8.2, 1.2), farbe=p.leise, dick=1)
    p.leitung((7, 4.8), (8.2, 4.8), farbe=p.leise, dick=1)
    p.spannung(8.2, 1.3, 4.7, f"U_Last = {g['U_Last']}")


def _buck(z):
    ue = z.choice([12.0, 24.0, 48.0])
    ua = z.choice([3.3, 5.0, 9.0])
    if ua >= ue:
        ua = 5.0
    d = ua / ue
    return ("Ein Abwärtswandler (Buck-Converter) macht aus Ue die kleinere Spannung Ua. Wie gross ist der Tastgrad D "
            "des Schalters? (idealer Wandler, nicht lückender Betrieb)",
            [("Ue", ue, _U), ("Ua", ua, _U)], ("D", "prozent", "Tastgrad (Einschaltdauer / Periode)"), d,
            ["Beim idealen Buck-Wandler gilt: Ua = D · Ue  ->  D = Ua / Ue",
             f"D = {_u(ua)} / {_u(ue)} = {d:.4g} = {d * 100:.1f} %",
             "Anders als beim Linearregler wird die Differenz NICHT verbrannt – Wirkungsgrade über 90 % sind üblich."])


def _s_buck(p, g, ges):
    p.quelle(1.2, 1.8, 4.6, "Ue", g["Ue"])
    p.leitung((1.2, 1.8), (1.2, 1.2), (2.2, 1.2))
    p.schalter(2.2, 1.2, 3.4, 1.2, False, f"D = {GESUCHT}")
    p.leitung((3.4, 1.2), (4.4, 1.2))
    p.knoten(4.4, 1.2)
    p.diode(4.4, 5.4, 4.4, 1.2, "D1", "", seite="links")
    p.spule(4.4, 1.2, 7.2, 1.2, "L", "")
    p.leitung((7.2, 1.2), (8.6, 1.2))
    p.knoten(7.6, 1.2)
    p.kondensator(7.6, 1.2, 5.4, "C", "", seite="links")
    p.widerstand(8.6, 1.2, 8.6, 5.4, "Last", f"Ua = {g['Ua']}")
    p.leitung((1.2, 4.6), (1.2, 5.4), (8.6, 5.4))


# =============================================================================
# FILTER UND TIMER
# =============================================================================
def _lc_resonanz(z):
    l = _e12(z, -6, -2)                                              # 1 µH … 8.2 mH
    c = _e12(z, -11, -6)                                             # 10 pF … 820 nF
    e = fm.lc_tiefpass(l, c, 50.0)
    return ("Ein LC-Kreis besteht aus der Spule L und dem Kondensator C. Bei welcher Frequenz ist er in Resonanz?",
            [("L", l, _L), ("C", c, _C)], ("f0", _F, "Resonanzfrequenz"), e["f0"],
            ["Thomsonsche Schwingungsformel: f0 = 1 / (2π · √(L · C))",
             f"f0 = 1 / (2π · √({_f(l, _L)} · {_f(c, _C)})) = {_f(e['f0'], _F)}",
             f"Bei f0 sind X_L und X_C gleich gross (je {_r(e['z0'])} – der Kennwiderstand √(L/C))."])


def _s_lc(p, g, ges):
    p.anschluss(1, 1.5)
    p.spule(1, 1.5, 4.8, 1.5, "L", g["L"])
    p.leitung((4.8, 1.5), (7, 1.5))
    p.knoten(6, 1.5)
    p.kondensator(6, 1.5, 4.5, "C", g["C"], seite="links")
    p.leitung((1, 4.5), (7, 4.5))
    p.anschluss(1, 4.5)
    p.text(4, 5.4, f"f0 = {GESUCHT}", "center", farbe=ORANGE, fett=True)


def _sallen_key(z):
    r1, r2 = _e12(z, 3, 5), _e12(z, 3, 5)
    c1, c2 = _e12(z, -9, -7), _e12(z, -9, -7)
    e = fm.sallen_key("Tiefpass", r1, r2, c1, c2)
    return ("Aktiver Tiefpass 2. Ordnung (Sallen-Key, Verstärkung 1). Wie gross ist die Kennfrequenz f0?",
            [("R1", r1, _R), ("R2", r2, _R), ("C1", c1, _C), ("C2", c2, _C)], ("f0", _F, "Kennfrequenz"), e["f0"],
            ["Kennfrequenz: f0 = 1 / (2π · √(R1 · R2 · C1 · C2))",
             f"f0 = 1 / (2π · √({_r(r1)} · {_r(r2)} · {_f(c1, _C)} · {_f(c2, _C)})) = {_f(e['f0'], _F)}",
             f"Die Güte hängt vom Verhältnis der Bauteile ab: hier Q = {e['q']:.3g} "
             "(0.707 = Butterworth, maximal flach)."])


def _s_sallen_key(p, g, ges):
    o = p.opv(7.4, 3.8, plus_oben=True)
    px, py = o["plus"]
    mx, my = o["minus"]
    ax, ay = o["aus"]
    p.anschluss(0.6, py)
    p.widerstand(0.6, py, 3.0, py, "R1", g["R1"])
    p.widerstand(3.0, py, 5.2, py, "R2", g["R2"])
    p.leitung((5.2, py), (px, py))
    p.knoten(5.2, py)
    p.kondensator(5.2, py, 6.8, "C2", g["C2"], seite="links")
    p.masse(5.2, 6.8)
    p.knoten(3.0, py)
    p.leitung((3.0, py), (3.0, 1.6))
    p.kondensator_waagrecht(3.0, 5.4, 1.6, "C1", g["C1"])
    p.leitung((5.4, 1.6), (9.2, 1.6), (9.2, ay))
    p.leitung((mx, my), (6.0, my), (6.0, 5.8), (9.2, 5.8), (9.2, ay))
    p.leitung((ax, ay), (9.8, ay))
    p.knoten(9.2, ay)
    p.anschluss(9.8, ay)
    p.text(5, 7.6, f"f0 = {GESUCHT}", "center", farbe=ORANGE, fett=True)


def _ne555_astabil(z):
    r1, r2 = _e12(z, 3, 5), _e12(z, 3, 5)
    c = _e12(z, -9, -5)
    e = osz.ne555_astabil(r1, r2, c)
    return ("NE555 als astabiler Multivibrator (Grundschaltung mit R1, R2 und C). Mit welcher Frequenz schwingt er?",
            [("R1", r1, _R), ("R2", r2, _R), ("C", c, _C)], ("f", _F, "Frequenz des Rechtecksignals"), e["f"],
            [f"Laden über R1 + R2: t_H = ln2 · (R1 + R2) · C = {_f(e['t_h'], _T)}",
             f"Entladen über R2:  t_L = ln2 · R2 · C = {_f(e['t_l'], _T)}",
             f"f = 1 / (t_H + t_L) = 1.44 / ((R1 + 2 · R2) · C) = {_f(e['f'], _F)}",
             f"Tastgrad = t_H / T = {e['tastgrad'] * 100:.1f} % – in dieser Grundschaltung immer über 50 %."])


def _s_ne555(p, g, ges, astabil=True):
    p.kasten(4.4, 1.6, 7.4, 5.6, "NE555")
    p.versorgung(3, 1.0, "+UB")
    if astabil:
        p.widerstand(3, 1.0, 3, 2.6, "R1", g["R1"], seite="links")
        p.widerstand(3, 2.6, 3, 4.4, "R2", g["R2"], seite="links")
        p.leitung((3, 2.6), (4.4, 2.6))
        p.knoten(3, 2.6)
        p.text(4.5, 2.6, "7", "w", klein=True, farbe=p.leise)
    else:
        p.widerstand(3, 1.0, 3, 4.4, "R", g["R"], seite="links")
    p.leitung((3, 4.4), (4.4, 4.4))
    p.knoten(3, 4.4)
    p.text(4.5, 4.4, "6/2" if astabil else "6/7", "w", klein=True, farbe=p.leise)
    p.kondensator(3, 4.4, 6.6, "C", g["C"], seite="links")
    p.masse(3, 6.6)
    p.leitung((7.4, 3.6), (9, 3.6))
    p.anschluss(9, 3.6)
    p.text(7.3, 3.6, "3", "e", klein=True, farbe=p.leise)
    p.text(9, 4.2, (f"f = {GESUCHT}" if astabil else f"t = {GESUCHT}"), "center", farbe=ORANGE, fett=True)
    if not astabil:
        p.text(5.9, 6.1, "Trigger an Pin 2", "center", klein=True, farbe=p.leise)


def _s_ne555_astabil(p, g, ges):
    _s_ne555(p, g, ges, True)


def _ne555_mono(z):
    r = _e12(z, 3, 6)
    c = _e12(z, -8, -4)
    t = osz.ne555_mono(r, c)["t"]
    return ("NE555 als Monoflop: Ein kurzer Triggerimpuls startet einen Ausgangsimpuls. Wie lange dauert er?",
            [("R", r, _R), ("C", c, _C)], ("t", _T, "Impulsdauer"), t,
            ["C lädt über R von 0 bis 2/3 · UB:  t = ln3 · R · C ≈ 1.1 · R · C",
             f"t = 1.0986 · {_r(r)} · {_f(c, _C)} = {_f(t, _T)}",
             "Die Dauer hängt nicht von UB ab – die Schaltschwellen sind ja Anteile von UB."])


def _s_ne555_mono(p, g, ges):
    _s_ne555(p, g, ges, False)


# =============================================================================
# ANMELDEN: (id, Titel, Bereich, Thema, Stufe, Wissensseiten, Erzeuger) + Schema (Spalten, Zeilen, Funktion)
# =============================================================================
S = "Schaltungen"
_LISTE = [
    # Widerstandsnetzwerke
    ("stromteiler", "Stromteiler: Teilstrom berechnen", "Widerstandsnetzwerke", 1, "stromteiler", _stromteiler, (8.6, 6, _s_stromteiler)),
    ("pullup_strom", "Pull-up-Widerstand: Strom bei gedrücktem Taster", "Widerstandsnetzwerke", 1, "pull_up_down", _pullup, (9, 6.4, _s_pullup)),
    ("bruecke_ud", "Wheatstone-Brücke: Brückenspannung", "Widerstandsnetzwerke", 2, "wheatstone_bruecke", _bruecke, (9, 6.6, _s_bruecke)),
    ("poti_last", "Potentiometer mit Last", "Widerstandsnetzwerke", 3, "potentiometer", _poti, (10.4, 6.6, _s_poti)),
    # Dioden
    ("gleichrichter_uc", "Brückengleichrichter: Spannung am Ladeelko", "Dioden & Schutz", 2, "gleichrichter_ladeelko", _gleichrichter, (9.6, 6, _s_gleichrichter)),
    ("z_diode_strom", "Z-Diode: Strom durch die Z-Diode", "Dioden & Schutz", 2, "z_stabilisierung", _z_strom, (9, 6.4, _s_z_strom)),
    ("ladeelko_brumm", "Ladeelko: Brummspannung", "Dioden & Schutz", 3, "gleichrichter_ladeelko", _brumm, (12.6, 6.2, _s_brumm)),
    ("z_diode_rv", "Z-Diode: Vorwiderstand dimensionieren", "Dioden & Schutz", 3, "z_stabilisierung", _z_rv, (9, 6.8, _s_z_rv)),
    # Transistor / MOSFET
    ("mosfet_verlust", "MOSFET: Verlustleistung eingeschaltet", "Transistor & MOSFET", 1, "mosfet_schalter", _mosfet_verlust, (9, 6, _s_mosfet)),
    ("basiswiderstand", "Transistor als Schalter: Basiswiderstand", "Transistor & MOSFET", 2, "transistorschalter", _basiswiderstand, (9, 6.2, _s_basiswiderstand)),
    ("konstantstrom", "Konstantstromquelle mit Transistor", "Transistor & MOSFET", 3, "konstantstromquelle", _konstantstrom, (9, 7.4, _s_konstantstrom)),
    ("emitterschaltung_uce", "Emitterschaltung: Arbeitspunkt U_CE", "Transistor & MOSFET", 4, "emitterschaltung", _emitterschaltung, (9, 8.0, _s_emitterschaltung)),
    # RC / RL
    ("rc_grenzfrequenz", "RC-Tiefpass: Grenzfrequenz", "RC & RL", 2, "rc_tiefpass_hochpass", _rc_fg, (8.4, 6, _s_rc_fg)),
    ("rl_tau", "RL-Glied: Zeitkonstante", "RC & RL", 2, "rl_ein_ausschalten", _rl_tau, (8.4, 6.8, _s_rl)),
    ("rc_entladen", "RC-Glied: Spannung beim Entladen", "RC & RL", 2, "rc_laden_entladen", _rc_entladen, (8.8, 6.2, _s_rc_entladen)),
    ("rc_amplitude", "RC-Tiefpass: Ausgangsspannung bei f", "RC & RL", 3, "rc_tiefpass_hochpass", _rc_amplitude, (8.4, 6, _s_rc_amplitude)),
    # OPV
    ("opv_nichtinvertierend", "OPV: nichtinvertierender Verstärker", "Operationsverstärker", 2, "opv_verstaerker", _opv_nichtinv, (9.6, 7, _s_opv_nichtinv)),
    ("opv_invertierend", "OPV: invertierender Verstärker", "Operationsverstärker", 2, "opv_verstaerker", _opv_inv, (9.6, 7, _s_opv_inv)),
    ("opv_addierer", "OPV: Addierer", "Operationsverstärker", 3, "opv_addierer", _addierer, (10, 7.4, _s_addierer)),
    ("opv_differenz", "OPV: Differenzverstärker", "Operationsverstärker", 3, "differenz_instrumentenverstaerker", _differenz, (10, 7.4, _s_differenz)),
    ("schmitt_trigger", "Schmitt-Trigger: Schaltschwelle", "Operationsverstärker", 4, "komparator_schmitt_trigger", _schmitt, (10, 7.4, _s_schmitt)),
    ("integrator", "OPV-Integrator: Ausgangsspannung nach t", "Operationsverstärker", 4, "integrator_differenzierer", _integrator, (10, 6.8, _s_integrator)),
    # Netzteile
    ("linearregler_verlust", "Linearregler: Verlustleistung", "Netzteile & Quellen", 2, "linearregler", _linearregler, (9.8, 6.6, _s_linearregler)),
    ("innenwiderstand", "Spannungsquelle: Innenwiderstand", "Netzteile & Quellen", 3, "quellenmodell", _innenwiderstand, (11.2, 6.2, _s_innen)),
    ("lm317", "LM317: Ausgangsspannung", "Netzteile & Quellen", 3, "linearregler", _lm317, (9.4, 7.2, _s_lm317)),
    ("buck_tastgrad", "Abwärtswandler: Tastgrad", "Netzteile & Quellen", 3, "schaltregler_buck_boost", _buck, (9.8, 6.4, _s_buck)),
    # Filter / Timer
    ("ne555_mono", "NE555 Monoflop: Impulsdauer", "Filter & Timer", 2, "ne555_timer", _ne555_mono, (9.6, 7.4, _s_ne555_mono)),
    ("lc_resonanz", "LC-Kreis: Resonanzfrequenz", "Filter & Timer", 3, "lc_tiefpass", _lc_resonanz, (8.4, 6, _s_lc)),
    ("ne555_astabil", "NE555 astabil: Frequenz", "Filter & Timer", 3, "ne555_timer", _ne555_astabil, (9.6, 7.4, _s_ne555_astabil)),
    ("sallen_key_f0", "Sallen-Key-Tiefpass: Kennfrequenz", "Filter & Timer", 4, "aktive_filter_sallen_key", _sallen_key, (10.6, 8.2, _s_sallen_key)),
]
for _id, _titel, _thema, _stufe, _seite, _erz, _schema in _LISTE:
    art(_id, _titel, S, _thema, _stufe, [(S, _seite)], _erz)
    SCHEMAS[_id] = _schema
