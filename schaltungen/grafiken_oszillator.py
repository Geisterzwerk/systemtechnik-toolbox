# =============================================================================
# schaltungen/grafiken_oszillator.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE für Timer, Oszillatoren und Watchdog.
# Spannung = blau, Strom = rot, Messpunkte = orange.
#
#   Ne555Schaltung            NE555 astabil (auch mit Diode für Tastgrad < 50 %) und monostabil
#   MultivibratorSchaltung    astabiler Multivibrator mit zwei Transistoren (negativer Basis-Ausschlag!)
#   FunktionsgeneratorSchaltung  Rechteck und Dreieck aus Schmitt-Trigger + Integrator
#   WatchdogSchaltung         µC + Watchdog-IC: Trigger, Zähler, Reset über der Zeit (auch Fenster-Watchdog)
#   VcoSchaltung              spannungsgesteuerter Oszillator: f proportional zur Steuerspannung
#
# Rechnung: schaltungen/oszillator_mathe.py
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_ne555")
# =============================================================================

from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN       # -> bauteile/grafiken/schaltplan.py
from schaltungen import oszillator_mathe as om                           # -> schaltungen/oszillator_mathe.py
from schaltungen.grafiken import _r, _u                                  # -> schaltungen/grafiken.py
from schaltungen.grafiken_dioden import FEHLER, _MitDiagramm             # -> schaltungen/grafiken_dioden.py
from schaltungen.grafiken_rc import LOG_C, LOG_R, _f, _punkt, _t         # -> schaltungen/grafiken_rc.py

LOG_S = {"einheit": "ms", "log": True, "grenzen": (1e-6, 1e3)}


def _c(wert):
    return fmt(wert, "kapazitaet", 3)


# =============================================================================
# NE555
# =============================================================================
class Ne555Schaltung(_MitDiagramm):
    TITEL = "🔌 NE555: Taktgeber und Monoflop (interaktiv)"
    UNTERTITEL = "Der Kondensator pendelt zwischen 1/3 und 2/3 der Versorgung – daraus entstehen Frequenz und Impulsdauer"
    VARIANTEN = ["astabil", "astabil mit Diode", "monostabil"]
    REGLER = [("ub", "Versorgung U_B", "spannung", 4.5, 15.0, 9.0, {"einheit": "V", "grenzen": (4.5, 18)}),
              ("r1", "R1 (monostabil: R)", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("r2", "R2", "widerstand", 1e3, 1e6, 47e3, LOG_R),
              ("c", "C", "kapazitaet", 1e-9, 100e-6, 100e-9, LOG_C)]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.2, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Im NE555 vergleichen zwei Komparatoren die Kondensatorspannung mit 1/3 und 2/3 "
        "von U_B und setzen ein Flipflop. ASTABIL: C lädt über R1 + R2 bis 2/3 U_B (Ausgang HIGH), dann entlädt "
        "ihn Pin 7 über R2 bis 1/3 U_B (Ausgang LOW) – und wieder von vorn. Weil das Laden über R1 + R2 und das "
        "Entladen nur über R2 läuft, ist HIGH immer länger als LOW (Tastgrad > 50 %). Eine DIODE parallel zu R2 "
        "lässt C nur über R1 laden – so sind auch Tastgrade unter 50 % möglich. MONOSTABIL: Ein kurzer LOW-Impuls "
        "an Pin 2 startet einen Ausgangsimpuls der Dauer 1.1 · R · C – unabhängig davon, wie lange getriggert wird. "
        "Weil nur Verhältnisse von U_B zählen, hängt die Zeit nicht von der Versorgung ab.")

    def sk_rechnen(self, w, v):
        if v == "monostabil":
            return om.ne555_kurven("monostabil", w["ub"], w["r1"], 0, w["c"])
        return om.ne555_kurven("astabil", w["ub"], w["r1"], w["r2"], w["c"], diode=v == "astabil mit Diode")

    def sk_zeichnen(self, p, w, e, v):
        x0, x1, y0, y1 = 6.4, 9.6, 2.6, 7.4
        x_r, y_r, y_g = 4.0, 1.0, 8.8
        p.kasten(x0, y0, x1, y1, "")
        p.text((x0 + x1) / 2, (y0 + y1) / 2, "NE555", "center", fett=True)
        pins = {"7": (x0, 3.4), "6": (x0, 5.0), "2": (x0, 5.8), "3": (x1, 5.0), "8": (7.2, y0), "4": (8.8, y0),
                "1": (7.2, y1), "5": (8.8, y1)}
        for nr, (x, y) in pins.items():
            dx = 0.25 if x == x0 else (-0.25 if x == x1 else 0)
            dy = 0.35 if y == y0 else (-0.35 if y == y1 else 0)
            p.text(x + dx, y + dy, nr, "center", klein=True, farbe=p.leise)
        p.versorgung(x_r, y_r, f"U_B = {_u(w['ub'])}")
        p.leitung((x_r, y_r), (8.8, y_r))
        p.leitung((7.2, y0), (7.2, y_r))
        p.leitung((8.8, y0), (8.8, y_r))
        p.knoten(7.2, y_r)
        p.leitung((7.2, y1), (7.2, y_g))
        p.kondensator(8.8, y1, y_g, "", "10 nF", seite="rechts")
        p.leitung((x_r, y_g), (8.8, y_g))
        p.masse(6.0, y_g)
        p.leitung((x1, 5.0), (11.4, 5.0))
        p.anschluss(11.4, 5.0, "OUT")
        p.messpunkt(10.5, 5.0, "M2", seite="rechts")
        if v == "monostabil":
            y_k = 4.4
            p.widerstand(x_r, y_r, x_r, y_k, "R", _r(w["r1"]), seite="links")
            p.leitung((x_r, y_k), (5.4, y_k), (5.4, 3.4), (x0, 3.4))
            p.leitung((5.4, y_k), (5.4, 5.0), (x0, 5.0))
            p.knoten(x_r, y_k)
            p.knoten(5.4, y_k)
            p.kondensator(x_r, y_k, y_g, "C", _c(w["c"]), seite="links")
            p.leitung((x0, 5.8), (5.0, 5.8), (5.0, 7.7))               # Trigger von unten, ohne Kreuzung
            p.anschluss(5.0, 7.7)
            p.text(5.0, 8.05, "Trigger", "n", klein=True, fett=True)
            p.messpunkt(x_r, y_k, "M1", seite="rechts")
        else:
            y_d, y_k = 3.4, 5.6
            p.widerstand(x_r, y_r, x_r, y_d, "R1", _r(w["r1"]), seite="links")
            p.widerstand(x_r, y_d, x_r, y_k, "R2", _r(w["r2"]), seite="links")
            p.leitung((x_r, y_d), (x0, y_d))
            p.knoten(x_r, y_d)
            p.leitung((x_r, y_k), (5.4, y_k), (5.4, 5.0), (x0, 5.0))
            p.leitung((5.4, y_k), (5.4, 5.8), (x0, 5.8))
            p.knoten(x_r, y_k)
            p.knoten(5.4, y_k)
            p.kondensator(x_r, y_k, y_g, "C", _c(w["c"]), seite="links")
            p.messpunkt(x_r, 7.0, "M1", seite="rechts")
            if v == "astabil mit Diode":
                p.leitung((x_r, y_d), (2.4, y_d), (2.4, 3.8))
                p.diode(2.4, 3.8, 2.4, 5.2, "D", "", seite="links")
                p.leitung((2.4, 5.2), (2.4, y_k), (x_r, y_k))
        p.knoten(x_r, y_g)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.0, 22.8
        u = w["ub"]
        p.diagramm(gx0, 1.0, gx1, 4.6, [(e["u_c"], SPANNUNG, None, False)], 0.0, u * 1.05,
                   "u_C am Kondensator (M1)", [(2 * u / 3, f"⅔ U_B = {_u(2 * u / 3)}"), (u / 3, f"⅓ U_B = {_u(u / 3)}")],
                   zeit_text="")
        kurven = [(e["aus"], STROM, None, False)]
        if v == "monostabil":
            kurven.insert(0, (e["trigger"], p.leise, 1, True))
        p.diagramm(gx0, 6.0, gx1, 9.4, kurven, -0.05 * u, u * 1.1,
                   "Ausgang Pin 3 (M2)" + ("  ·  Trigger gestrichelt" if v == "monostabil" else ""),
                   einheit="spannung", t_ende=e["dauer"])

    def sk_info(self, w, e, v):
        if v == "monostabil":
            return [f"Impulsdauer t = ln3 · R · C = 1.1 · {_r(w['r1'])} · {_c(w['c'])} = {_t(e['t'])}",
                    "Der Trigger (Pin 2 kurz unter ⅓ U_B) muss kürzer sein als der Impuls; während des Impulses "
                    "wirkt ein neuer Trigger nicht (nicht nachtriggerbar)"], OK
        diode = v == "astabil mit Diode"
        zeilen = [(f"t_H = ln2 · R1 · C = {_t(e['t_h'])}" if diode else
                   f"t_H = ln2 · (R1 + R2) · C = {_t(e['t_h'])}") + f"   ·   t_L = ln2 · R2 · C = {_t(e['t_l'])}",
                  f"f = 1 / (t_H + t_L) = {_f(e['f'])}   ·   Tastgrad {e['tastgrad'] * 100:.1f} %"]
        if w["r1"] < 1e3:
            zeilen.append("⚠ R1 < 1 kΩ: Beim Entladen fliesst U_B / R1 in Pin 7 – zu viel Strom")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# ASTABILER MULTIVIBRATOR
# =============================================================================
class MultivibratorSchaltung(_MitDiagramm):
    TITEL = "🔌 Astabiler Multivibrator mit zwei Transistoren (interaktiv)"
    UNTERTITEL = "Zwei Transistoren schalten sich gegenseitig ab – die Kondensatoren bestimmen, wie lange"
    VARIANTEN = []
    REGLER = [("ub", "Versorgung U_B", "spannung", 3.0, 12.0, 5.0, {"einheit": "V", "grenzen": (1.0, 30)}),
              ("rc", "Kollektorwiderstand R_C", "widerstand", 220.0, 10e3, 1e3, LOG_R),
              ("rb1", "R_B1", "widerstand", 1e3, 1e6, 47e3, LOG_R),
              ("rb2", "R_B2", "widerstand", 1e3, 1e6, 47e3, LOG_R),
              ("c1", "C1", "kapazitaet", 1e-9, 100e-6, 10e-6, LOG_C),
              ("c2", "C2", "kapazitaet", 1e-9, 100e-6, 10e-6, LOG_C)]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.2, 10)
    SEITENVERHAELTNIS = 0.5
    BETA = 100.0
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Leitet T1, springt sein Kollektor auf fast 0 V. Diese negative Flanke gibt C1 an die "
        "Basis von T2 weiter – die Basis springt auf etwa −(U_B − 0.9 V) und T2 sperrt. Erst wenn C1 über R_B2 so "
        "weit umgeladen ist, dass die Basis wieder +0.7 V erreicht, leitet T2 – und schaltet über C2 jetzt T1 ab. "
        "So kippt die Schaltung hin und her: t = ln2 · R_B · C je Hälfte. Achtung: Die Basis-Emitter-Strecke "
        "verträgt in Sperrrichtung nur etwa 5 … 6 V – bei höherer Versorgung braucht es eine Diode in Reihe zur "
        "Basis. Damit die Transistoren sicher sättigen, muss R_B ≤ β · R_C sein.")

    def sk_rechnen(self, w, v):
        return om.multivibrator_kurven(w["ub"], w["rc"], w["rb1"], w["rb2"], w["c1"], w["c2"])

    def sk_zeichnen(self, p, w, e, v):
        x1, x2, xb1, xb2, y_r, y_t, y_g = 2.4, 9.6, 4.6, 7.4, 1.0, 6.6, 8.8
        p.versorgung(6.0, y_r, f"U_B = {_u(w['ub'])}")
        p.leitung((x1, y_r), (x2, y_r))
        p.npn(x1, y_t, "T1", seite="links", basis_rechts=True)
        p.npn(x2, y_t, "T2", seite="rechts")
        p.widerstand(x1, y_r, x1, 4.4, "R_C1", _r(w["rc"]), seite="links")
        p.widerstand(x2, y_r, x2, 4.4, "R_C2", _r(w["rc"]), seite="rechts")
        p.widerstand(xb1, y_r, xb1, 3.2, "R_B1", _r(w["rb1"]), seite="links")
        p.widerstand(xb2, y_r, xb2, 3.2, "R_B2", _r(w["rb2"]), seite="rechts")
        for x in (x1, x2, xb1, xb2):
            p.knoten(x, y_r)
        p.leitung((x1, 4.4), (x1, y_t - 1))
        p.leitung((x2, 4.4), (x2, y_t - 1))
        p.leitung((xb1, 3.2), (xb1, y_t), (x1 + 0.9, y_t))                      # Basis T1
        p.leitung((xb2, 3.2), (xb2, y_t), (x2 - 0.9, y_t))                      # Basis T2
        p.leitung((x1, 4.4), (4.9, 4.4))                                        # C1: Kollektor T1 -> Basis T2
        p.kondensator_waagrecht(4.9, xb2, 4.4, "C1", _c(w["c1"]))
        p.leitung((x2, 5.4), (7.1, 5.4))                                        # C2: Kollektor T2 -> Basis T1
        p.kondensator_waagrecht(xb1, 7.1, 5.4, "", "")
        p.text(5.75, 6.2, f"C2  {_c(w['c2'])}", "center", klein=True, farbe=p.leise)
        for x, y in ((x1, 4.4), (x2, 5.4), (xb2, 4.4), (xb1, 5.4)):
            p.knoten(x, y)
        p.leitung((x1, y_t + 1), (x1, y_g), (x2, y_g), (x2, y_t + 1))
        p.masse(6.0, y_g)
        p.messpunkt(x1, 4.4, "M1", seite="links")
        p.messpunkt(xb2, y_t, "M2", seite="rechts")
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.0, 22.8
        u = w["ub"]
        p.diagramm(gx0, 1.0, gx1, 4.4, [(e["ce1"], SPANNUNG, None, False), (e["ce2"], STROM, 1, True)], 0.0, u * 1.08,
                   "U_CE1 (blau, M1) und U_CE2 (rot)", zeit_text="", einheit="spannung")
        lo = min(e["u_be_min"], -5.5) * 1.1
        p.diagramm(gx0, 5.8, gx1, 9.4, [(e["be2"], SPANNUNG, None, False)], lo, 1.5,
                   "U_BE2 an der Basis von T2 (M2)", [(-5.0, "−5 V Grenze"), (0.7, "0.7 V")], einheit="spannung",
                   t_ende=e["dauer"])

    def sk_info(self, w, e, v):
        zeilen = [f"t1 = {e['faktor']:.3f} · R_B1 · C1 = {_t(e['t1'])}   ·   t2 = {_t(e['t2'])}   ·   "
                  f"f = {_f(e['f'])}   ·   Tastgrad {e['tastgrad'] * 100:.0f} %",
                  f"I_C = (U_B − 0.2 V) / R_C = {fmt(e['i_c'], 'strom')}   ·   I_B = {fmt(e['i_b'], 'strom')}   ·   "
                  f"Übersteuerung β·I_B / I_C = {e['ueberst']:.2g} (β = {self.BETA:g})"]
        farbe = OK
        if not e["gesaettigt"]:
            zeilen.append("⚠ R_B zu gross: Die Transistoren sättigen nicht (R_B ≤ β · R_C) – unsaubere Flanken")
            farbe = WARN
        if e["u_be_min"] < -5.0:
            zeilen.append(f"⚠ Basis bis {_u(e['u_be_min'])}: Über ≈ 5 V Sperrspannung bricht die B-E-Strecke durch "
                          "(Diode in Reihe zur Basis)")
            farbe = WARN
        return zeilen, farbe


# =============================================================================
# RECHTECK-/DREIECKGENERATOR
# =============================================================================
class FunktionsgeneratorSchaltung(_MitDiagramm):
    TITEL = "🔌 Rechteck-/Dreieckgenerator mit zwei OPV (interaktiv)"
    UNTERTITEL = "Ein Schmitt-Trigger schaltet einen Integrator um – der Integrator schaltet den Schmitt-Trigger zurück"
    VARIANTEN = []
    REGLER = [("usat", "Ausgangsspannung ±U_sat", "spannung", 3.0, 15.0, 12.0, {"einheit": "V", "grenzen": (0.5, 50)}),
              ("r1", "R1", "widerstand", 1e3, 100e3, 10e3, LOG_R),
              ("r2", "R2 (Mitkopplung)", "widerstand", 1e3, 1e6, 20e3, LOG_R),
              ("r", "R (Integrator)", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("c", "C (Integrator)", "kapazitaet", 1e-9, 10e-6, 100e-9, LOG_C)]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.6, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  OPV1 ist ein nichtinvertierender Schmitt-Trigger: Sein Ausgang ist +U_sat oder "
        "−U_sat (Rechteck). OPV2 integriert diese Spannung – bei konstantem Eingang steigt bzw. fällt sein Ausgang "
        "linear (Dreieck) mit der Steigung U_sat / (R · C). Das Dreieck führt über R1 zurück zum Schmitt-Trigger. "
        "Erreicht es die Schaltschwelle ±U_sat · R1 / R2, kippt das Rechteck und der Integrator läuft in die "
        "andere Richtung. So entsteht eine Schwingung mit f = R2 / (4 · R1 · R · C). R1/R2 bestimmt die "
        "Dreieck-Amplitude, R · C die Geschwindigkeit. Das ist das Prinzip einfacher Funktionsgeneratoren.")

    def sk_rechnen(self, w, v):
        return om.funktions_kurven(w["r1"], w["r2"], w["r"], w["c"], w["usat"])

    def sk_zeichnen(self, p, w, e, v):
        y_s, y_g = 5.0, 9.2
        k1 = p.opv(3.6, y_s, "1", plus_oben=True)
        k2 = p.opv(9.4, y_s + 0.5, "2", plus_oben=False)
        x_a1, x_n = 5.2, 2.0
        p.leitung(k1["aus"], (x_a1, y_s))
        p.knoten(x_a1, y_s)
        p.leitung(k1["plus"], (x_n, k1["plus"][1]))
        p.knoten(x_n, k1["plus"][1])
        p.leitung((x_a1, y_s), (x_a1, 2.6))
        p.widerstand(x_n, 2.6, x_a1, 2.6, "R2", _r(w["r2"]))
        p.leitung((x_n, 2.6), (x_n, k1["plus"][1]))
        p.leitung(k1["minus"], (2.2, k1["minus"][1]), (2.2, 6.4))
        p.masse(2.2, 6.4)
        p.widerstand(x_a1, y_s, 7.6, y_s, "R", _r(w["r"]))
        p.leitung((7.6, y_s), k2["minus"])
        p.knoten(7.6, y_s)
        p.leitung((7.6, y_s), (7.6, 3.4))
        x_a2 = 11.0
        p.kondensator_waagrecht(7.6, x_a2, 3.4, "C", _c(w["c"]))
        p.leitung(k2["aus"], (11.8, k2["aus"][1]))
        p.leitung((x_a2, 3.4), (x_a2, k2["aus"][1]))
        p.knoten(x_a2, k2["aus"][1])
        p.leitung(k2["plus"], (7.8, k2["plus"][1]), (7.8, 7.0))
        p.masse(7.8, 7.0)
        p.leitung((11.8, k2["aus"][1]), (11.8, 8.2), (1.0, 8.2), (1.0, 6.6))
        p.widerstand(1.0, 6.6, 1.0, k1["plus"][1], "R1", _r(w["r1"]), seite="rechts")
        p.leitung((1.0, k1["plus"][1]), (x_n, k1["plus"][1]))
        p.text(x_a1 + 0.2, y_s + 0.45, "Rechteck", "nw", klein=True, farbe=STROM)
        p.text(11.9, k2["aus"][1] - 0.35, "Dreieck", "sw", klein=True, farbe=SPANNUNG)
        p.messpunkt(x_a1, 2.6, "M1", seite="rechts")
        p.messpunkt(11.8, 6.6, "M2", seite="rechts")
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.6, 22.8
        u = w["usat"]
        p.diagramm(gx0, 1.0, gx1, 4.4, [(e["rechteck"], STROM, None, False)], -u * 1.15, u * 1.15,
                   "Rechteck am Ausgang OPV1 (M1)", zeit_text="", einheit="spannung")
        p.diagramm(gx0, 5.8, gx1, 9.4, [(e["dreieck"], SPANNUNG, None, False)], -u * 1.15, u * 1.15,
                   "Dreieck am Ausgang OPV2 (M2)", [(e["u_d"], f"+{_u(e['u_d'])}"), (-e["u_d"], f"−{_u(e['u_d'])}")],
                   einheit="spannung", t_ende=e["dauer"])

    def sk_info(self, w, e, v):
        return [f"Dreieck-Amplitude û = U_sat · R1 / R2 = {_u(w['usat'])} · {_r(w['r1'])} / {_r(w['r2'])} = {_u(e['u_d'])}",
                f"f = R2 / (4 · R1 · R · C) = {_f(e['f'])}   ·   Steigung des Dreiecks U_sat / (R·C) = "
                f"{fmt(e['steigung'], 'spannung')}/s",
                "Frequenz einstellen über R (Poti), Amplitude über R1/R2 – beide unabhängig voneinander"], OK


# =============================================================================
# WATCHDOG
# =============================================================================
class WatchdogSchaltung(_MitDiagramm):
    TITEL = "🔌 Watchdog: Der Aufpasser für den Mikrocontroller (interaktiv)"
    UNTERTITEL = "Das Programm muss regelmässig „Ich lebe“ melden – sonst gibt es einen Reset"
    VARIANTEN = ["Watchdog", "Fenster-Watchdog"]
    REGLER = [("ttr", "Trigger-Abstand im Programm", "zeit", 0.01, 2.0, 0.25, LOG_S),
              ("twd", "Timeout des Watchdogs (typisch)", "zeit", 0.05, 5.0, 1.0, LOG_S),
              ("tol", "Toleranz des Timeouts in %", "zahl", 0.0, 50.0, 30.0, {"grenzen": (0, 90)}),
              ("th", "Programm hängt ab", "zeit", 0.1, 10.0, 2.0, LOG_S),
              ("tst", "Bootzeit nach dem Reset", "zeit", 0.01, 2.0, 0.2, LOG_S),
              ("tf", "Fenster: frühester Trigger", "zeit", 0.01, 2.0, 0.1, LOG_S)]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.2, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der Watchdog-Baustein zählt die Zeit seit dem letzten Trigger (Puls an WDI). Das "
        "Programm sendet im normalen Ablauf regelmässig einen Trigger und setzt den Zähler damit zurück. Hängt das "
        "Programm (Endlosschleife, Absturz), bleibt der Trigger aus: Der Zähler erreicht den Timeout und der "
        "Watchdog zieht RESET – der µC startet neu. Wichtig: Der Timeout streut laut Datenblatt (z.B. ±30 %), also "
        "muss das Programm vor dem KÜRZESTEN Timeout triggern – und auch die Bootzeit nach dem Reset muss "
        "hineinpassen, sonst entsteht eine Reset-Schleife. Der FENSTER-Watchdog meldet zusätzlich zu FRÜHE "
        "Trigger: So fällt auch ein Programm auf, das in einer Schleife hängt, die ständig triggert.")

    def sk_rechnen(self, w, v):
        return om.watchdog_zeitachse(w["ttr"], w["twd"], w["th"], 0.05 * w["twd"], w["tst"], w["tol"] / 100,
                                     fenster=v == "Fenster-Watchdog", t_fenster=w["tf"])

    def sk_zeichnen(self, p, w, e, v):
        p.kasten(0.8, 2.4, 4.6, 7.6, "µC")
        p.kasten(7.4, 3.0, 11.4, 7.0, "Watchdog")
        p.versorgung(6.0, 1.0, "U_B")
        p.leitung((2.7, 1.0), (9.4, 1.0))
        p.leitung((2.7, 1.0), (2.7, 2.4))
        p.leitung((9.4, 1.0), (9.4, 3.0))
        p.knoten(6.0, 1.0)
        p.leitung((4.6, 4.0), (7.4, 4.0))
        p.text(6.0, 3.65, "WDI (Trigger)", "s", klein=True, farbe=SPANNUNG)
        reset_aktiv = any(r for _t, r in e["reset"])
        p.leitung((7.4, 6.0), (4.6, 6.0), farbe=FEHLER[1] if reset_aktiv else None)
        p.text(6.0, 6.35, "RESET", "n", klein=True, farbe=FEHLER[1] if reset_aktiv else p.leise)
        p.text(2.7, 4.4, "Programm", "center", klein=True, farbe=p.leise)
        p.text(2.7, 5.0, f"alle {_t(w['ttr'])}", "center", klein=True)
        p.text(2.7, 5.6, f"hängt ab {_t(w['th'])}", "center", klein=True, farbe=FEHLER[1])
        p.text(9.4, 4.4, f"Timeout {_t(w['twd'])}", "center", klein=True)
        p.text(9.4, 5.0, f"±{w['tol']:.0f} %", "center", klein=True, farbe=p.leise)
        if v == "Fenster-Watchdog":
            p.text(9.4, 5.6, f"Fenster ab {_t(w['tf'])}", "center", klein=True, farbe=p.leise)
        p.leitung((2.7, 7.6), (2.7, 8.8), (9.4, 8.8), (9.4, 7.0))
        p.masse(6.0, 8.8)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.0, 22.8
        p.diagramm(gx0, 0.9, gx1, 2.6, [(e["trigger"], SPANNUNG, None, False)], -0.1, 1.2, "Trigger vom Programm",
                   zeit_text="")
        p.diagramm(gx0, 3.6, gx1, 6.6, [(e["zaehler"], STROM, None, False)], 0.0, 1.15,
                   "Zähler des Watchdogs (oben = kürzester Timeout)", [(1.0, _t(e["t_wd_min"]))], zeit_text="")
        p.diagramm(gx0, 7.6, gx1, 9.3, [(e["reset"], FEHLER[1], None, False)], -0.1, 1.2, "RESET",
                   t_ende=e["dauer"])

    def sk_info(self, w, e, v):
        zeilen = [f"Kürzester Timeout = {_t(w['twd'])} · (1 − {w['tol']:.0f} %) = {_t(e['t_wd_min'])}   ·   "
                  f"Trigger alle {_t(w['ttr'])}"]
        for t, grund in e["ereignisse"][:4]:
            zeilen.append(f"  t = {_t(t)}: {grund}")
        if len(e["ereignisse"]) > 4:
            zeilen.append(f"  … insgesamt {len(e['ereignisse'])} Resets")
        if e["bootschleife"]:
            zeilen.append("⚠ Bootzeit + Trigger-Abstand länger als der Timeout: Der µC kommt nach dem Reset nie zum "
                          "Triggern – endlose Reset-Schleife")
            return zeilen, WARN
        if not e["sicher"]:
            zeilen.append("⚠ Auch ohne Hänger gibt es Resets – Trigger-Abstand muss kleiner als der kürzeste Timeout "
                          "(und beim Fenster grösser als das Fenster) sein")
            return zeilen, WARN
        zeilen.append("✓ Im Normalbetrieb kein Reset – nur der Hänger wird erkannt")
        return zeilen, OK


# =============================================================================
# VCO (spannungsgesteuerter Oszillator)
# =============================================================================
class VcoSchaltung(_MitDiagramm):
    TITEL = "🔌 VCO: Frequenz per Spannung einstellen (interaktiv)"
    UNTERTITEL = "Steuerspannung hochdrehen – das Dreieck wird steiler, die Frequenz steigt proportional"
    VARIANTEN = []
    U_ST_MAX = 12.0
    REGLER = [("ust", "Steuerspannung U_st", "spannung", 0.0, 12.0, 6.0, {"einheit": "V", "grenzen": (0.0, 12.0)}),
              ("usat", "Ausgangsspannung ±U_sat", "spannung", 3.0, 15.0, 12.0, {"einheit": "V", "grenzen": (0.5, 50)}),
              ("r1", "R1", "widerstand", 1e3, 100e3, 10e3, LOG_R),
              ("r2", "R2", "widerstand", 1e3, 1e6, 20e3, LOG_R),
              ("r", "R (Integrator)", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("c", "C (Integrator)", "kapazitaet", 1e-9, 10e-6, 100e-9, LOG_C)]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.6, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Ein VCO (Voltage Controlled Oscillator) erzeugt eine Frequenz, die von einer Spannung "
        "abhängt. Prinzip wie beim Rechteck-/Dreieckgenerator, aber der Integrator integriert nicht ±U_sat, sondern "
        "die STEUERSPANNUNG ±U_st – ein Umschalter (z.B. Analogschalter oder invertierender Verstärker) wählt das "
        "Vorzeichen nach dem Schmitt-Trigger. Doppelte Steuerspannung = doppelt steiles Dreieck = doppelte Frequenz: "
        "f = K · U_st mit der Steilheit K = R2 / (4 · R1 · R · C · U_sat) in Hz/V. Die Schaltschwellen (also die "
        "Dreieck-Amplitude) bleiben gleich. VCOs stecken in PLLs (Taktvervielfachung im µC, Funkempfänger), in "
        "Synthesizern und in Spannungs-Frequenz-Wandlern. Oben: Signale über eine feste Zeitspanne, unten: f über U_st.")

    def sk_rechnen(self, w, v):
        k = om.vco(w["r1"], w["r2"], w["r"], w["c"], w["usat"], 1.0)["k"]
        dauer = 4 / (k * self.U_ST_MAX)                          # feste Zeitachse: 4 Perioden bei U_st,max
        e = om.vco_kurven(w["r1"], w["r2"], w["r"], w["c"], w["usat"], w["ust"], dauer)
        e["dauer"] = dauer
        e["kennlinie"] = [(x / 20, k * self.U_ST_MAX * x / 20) for x in range(21)]
        return e

    def _pfeil(self, p, xa, ya, xb, yb):
        (a, b), (c, d) = p.p(xa, ya), p.p(xb, yb)
        p.c.create_line(a, b, c, d, fill=p.linie, width=p.dick, arrow="last",
                        arrowshape=(p.u * 0.25, p.u * 0.3, p.u * 0.1))

    def sk_zeichnen(self, p, w, e, v):
        bloecke = [(0.4, 2.4, "U_st", SPANNUNG), (3.2, 5.6, "± Umschalter", None), (6.4, 8.8, "Integrator", None),
                   (9.6, 12.2, "Schmitt-Trigger", None)]
        y0, y1 = 3.2, 5.2
        for x0, x1, titel, farbe in bloecke:
            p.kasten(x0, y0, x1, y1, "")
            p.text((x0 + x1) / 2, (y0 + y1) / 2, titel, "center", fett=True, farbe=farbe)
        p.text(1.4, y1 + 0.4, _u(w["ust"]), "n", klein=True, farbe=SPANNUNG)
        for xa, xb in ((2.4, 3.2), (5.6, 6.4), (8.8, 9.6)):
            self._pfeil(p, xa, 4.2, xb, 4.2)
        p.leitung((12.2, 4.2), (12.6, 4.2), (12.6, 6.6), (4.4, 6.6))       # Rückführung: Vorzeichen umschalten
        self._pfeil(p, 4.4, 6.6, 4.4, y1)
        p.text(8.4, 6.95, "Rechteck schaltet das Vorzeichen um", "n", klein=True, farbe=p.leise)
        p.text(7.6, 2.9, "Dreieck", "s", klein=True, farbe=SPANNUNG)
        p.text(10.9, 2.9, "Rechteck", "s", klein=True, farbe=STROM)
        p.text(0.4, 8.6, f"f = K · U_st = {_f(e['k'])}/V · {_u(w['ust'])} = {_f(e['f'])}", "w", fett=True,
               farbe=SPANNUNG)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.6, 22.8
        u = w["usat"]
        p.diagramm(gx0, 1.0, gx1, 4.6, [(e["rechteck"], STROM, 1, True), (e["dreieck"], SPANNUNG, None, False)],
                   -u * 1.15, u * 1.15, "Rechteck (rot) und Dreieck (blau) – feste Zeitspanne",
                   einheit="spannung", t_ende=e["dauer"])
        f_max = e["k"] * self.U_ST_MAX
        p.diagramm(gx0, 6.0, gx1, 9.4, [(e["kennlinie"], STROM, None, False)], 0.0, f_max * 1.1,
                   "Kennlinie f über U_st", einheit="frequenz", zeit_text=f"U_st (0 … {_u(self.U_ST_MAX)})")
        _punkt(p, gx0, 6.0, gx1, 9.4, w["ust"] / self.U_ST_MAX, e["f"], 0.0, f_max * 1.1)

    def sk_info(self, w, e, v):
        return [f"Steilheit K = R2 / (4 · R1 · R · C · U_sat) = {_f(e['k'])}/V",
                f"f = K · U_st = {_f(e['f'])}   ·   Dreieck-Amplitude bleibt ±{_u(e['u_d'])} (Schwellen fest)",
                "Linear, solange Umschalter und Integrator ideal arbeiten – bei U_st = 0 bleibt die Schwingung "
                "stehen"], OK
