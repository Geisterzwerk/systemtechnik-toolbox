# =============================================================================
# schaltungen/grafiken_schnittstellen.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE für Schnittstellen und Leistung.
# Spannung = blau, Strom = rot, Messpunkte = orange.
#
#   PegelwandlerSchaltung  5 V -> 3.3 V mit Teiler, bidirektional mit N-MOSFET (BSS138-Prinzip)
#   OptokopplerSchaltung   LED-Strom, CTR, Pull-up: sättigt der Ausgang sicher?
#   HBrueckeSchaltung      vier Schalter, Strompfad je Zustand, Brückenkurzschluss
#   GateTreiberSchaltung   MOSFET einschalten: u_GS mit Miller-Plateau, u_DS, Schaltzeiten
#   AdcEingangSchaltung    Abtastkondensator laden: Restfehler in LSB, ohne / mit externem C
#   BusabschlussSchaltung  RS-485/CAN: Reflexionen je nach Abschluss, Fail-safe-Vorspannung
#
# Rechnung: schaltungen/schnittstellen_mathe.py
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_pegelwandler")
# =============================================================================

from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN       # -> bauteile/grafiken/schaltplan.py
from schaltungen import schnittstellen_mathe as sm                       # -> schaltungen/schnittstellen_mathe.py
from schaltungen.grafiken import _i, _r, _u                              # -> schaltungen/grafiken.py
from schaltungen.grafiken_dioden import FEHLER, _MitDiagramm             # -> schaltungen/grafiken_dioden.py
from schaltungen.grafiken_rc import LOG_C, LOG_R, _punkt, _t             # -> schaltungen/grafiken_rc.py

GRUEN_AN = OK[1]                      # Schalter EIN

LOG_RK = {"einheit": "Ω", "log": True, "grenzen": (0.1, 10e6)}
LADUNG = {"einheit": "nC", "grenzen": (0.1e-9, 10e-6)}


def _c(wert):
    return fmt(wert, "kapazitaet", 3)


def _zustand_text(p, x, y, an):
    p.text(x, y, "EIN" if an else "aus", "e", fett=an, klein=not an, farbe=GRUEN_AN if an else p.leise)


# =============================================================================
# PEGELWANDLER
# =============================================================================
class PegelwandlerSchaltung(_MitDiagramm):
    TITEL = "🔌 Pegelwandler 5 V ↔ 3.3 V (interaktiv)"
    UNTERTITEL = "Teiler für eine Richtung, N-MOSFET für bidirektionale Open-Drain-Leitungen (I²C)"
    VARIANTEN = ["Teiler 5 V → 3.3 V", "MOSFET: beide frei", "MOSFET: A zieht LOW", "MOSFET: B zieht LOW"]
    REGLER = [("ua", "Spannung Seite A (niedrig)", "spannung", 1.2, 5.0, 3.3, {"einheit": "V", "grenzen": (0.5, 30)}),
              ("ub", "Spannung Seite B (hoch)", "spannung", 1.8, 12.0, 5.0, {"einheit": "V", "grenzen": (0.5, 30)}),
              ("r1", "R1 (Teiler oben / Pull-up A)", "widerstand", 470.0, 100e3, 10e3, LOG_R),
              ("r2", "R2 (Teiler unten / Pull-up B)", "widerstand", 470.0, 100e3, 20e3, LOG_R),
              ("c", "Leitungskapazität C", "kapazitaet", 5e-12, 1e-9, 100e-12, LOG_C),
              ("uth", "U_GS(th) des MOSFET", "spannung", 0.5, 3.0, 1.5, {"einheit": "V", "grenzen": (0.1, 10)})]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.6, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  TEILER: Ein 5-V-Ausgang darf nicht direkt an einen 3.3-V-Eingang (Schutzdioden "
        "leiten). Zwei Widerstände teilen herunter: U = U_B · R2/(R1 + R2). Nachteil: nur eine Richtung, und mit der "
        "Eingangskapazität entsteht ein Tiefpass (t_r = 2.2 · (R1∥R2) · C). MOSFET: Gate fest an der niedrigen "
        "Spannung, beide Seiten mit Pull-up. Ruhe: U_GS = 0, der MOSFET sperrt, jede Seite hat ihren Pegel. Zieht "
        "A nach LOW, wird U_GS = U_A, der Kanal leitet und B folgt. Zieht B nach LOW, zieht zuerst die Body-Diode A "
        "auf ≈ 0.6 V, dann leitet der Kanal. So funktioniert es in BEIDE Richtungen – ideal für I²C. Die Pull-ups "
        "bestimmen, wie schnell die Leitungen wieder hochkommen (Diagramm).")

    def sk_rechnen(self, w, v):
        if v.startswith("Teiler"):
            e = sm.pegel_teiler(w["ub"], w["r1"], w["r2"], w["c"])
            tau = e["r_par"] * w["c"]
            e["dauer"] = 5 * tau
            e["kurve"] = [(k / 100, e["u_aus"] * (1 - pow(2.718281828, -5 * k / 100))) for k in range(101)]
            return e
        zustand = v.split(": ")[1]
        e = sm.pegel_mosfet(zustand, w["ua"], w["ub"], w["r1"], w["r2"], w["c"], w["uth"])
        tau = max(w["r1"], w["r2"]) * w["c"]
        e["dauer"] = 5 * tau
        e["kurve_a"] = [(k / 100, w["ua"] * (1 - pow(2.718281828, -5 * k / 100 * max(w["r1"], w["r2"]) / w["r1"])))
                        for k in range(101)]
        e["kurve_b"] = [(k / 100, w["ub"] * (1 - pow(2.718281828, -5 * k / 100 * max(w["r1"], w["r2"]) / w["r2"])))
                        for k in range(101)]
        return e

    def sk_zeichnen(self, p, w, e, v):
        if v.startswith("Teiler"):
            self._teiler(p, w, e)
        else:
            self._mosfet(p, w, e, v)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.6, 22.8
        if v.startswith("Teiler"):
            p.diagramm(gx0, 1.6, gx1, 8.6, [(e["kurve"], SPANNUNG, None, False)], 0.0, w["ub"] * 1.05,
                       "Eingang nach einer steigenden Flanke (5 τ)", [(e["u_aus"], _u(e["u_aus"]))],
                       einheit="spannung", t_ende=e["dauer"])
        else:
            p.diagramm(gx0, 1.6, gx1, 8.6, [(e["kurve_a"], SPANNUNG, None, False), (e["kurve_b"], STROM, None, False)],
                       0.0, w["ub"] * 1.05, "Loslassen: A (blau) und B (rot) steigen über die Pull-ups",
                       [(w["ua"], f"U_A = {_u(w['ua'])}"), (w["ub"], f"U_B = {_u(w['ub'])}")], einheit="spannung",
                       t_ende=e["dauer"])

    def _teiler(self, p, w, e):
        y, y_u = 4.0, 8.6
        p.kasten(0.6, 2.8, 3.2, 5.2, "5-V-Logik")
        p.text(1.9, 4.4, f"HIGH = {_u(w['ub'])}", "center", klein=True, farbe=p.leise)
        p.widerstand(3.2, y, 6.6, y, "R1", _r(w["r1"]))
        p.knoten(6.6, y)
        p.widerstand(6.6, y, 6.6, y_u, "R2", _r(w["r2"]), seite="links")
        p.masse(6.6, y_u)
        p.leitung((6.6, y), (8.6, y))
        p.kasten(8.6, 2.8, 11.6, 5.2, "3.3-V-Eingang")
        p.text(10.1, 4.4, f"C_ein = {_c(w['c'])}", "center", klein=True, farbe=p.leise)
        p.spannung(7.8, y + 0.4, y_u - 0.4, f"U = {_u(e['u_aus'])}")
        p.messpunkt(6.6, y, "M1", seite="rechts")

    def _mosfet(self, p, w, e, v):
        x_m, y_m, y_a, y_b, y_r, y_u = 6.4, 5.0, 7.0, 3.2, 1.0, 9.2
        p.versorgung(3.0, y_r, f"U_A = {_u(w['ua'])}")
        p.versorgung(9.6, y_r, f"U_B = {_u(w['ub'])}")
        p.leitung((3.0, y_r), (5.0, y_r))
        p.nmosfet(x_m, y_m, "Q1")
        p.leitung((x_m - 0.9, y_m), (5.0, y_m), (5.0, y_r))                     # Gate an U_A
        p.knoten(5.0, y_r)
        p.leitung((x_m, y_m + 1), (x_m, y_a), (1.0, y_a))                         # Source -> Seite A
        p.leitung((x_m, y_m - 1), (x_m, y_b), (11.6, y_b))                        # Drain -> Seite B
        p.widerstand(3.0, y_r, 3.0, y_a, "R1", _r(w["r1"]), seite="links")
        p.widerstand(9.6, y_r, 9.6, y_b, "R2", _r(w["r2"]), seite="rechts")
        p.knoten(3.0, y_a)
        p.knoten(9.6, y_b)
        p.anschluss(1.0, y_a, "A", seite="links")
        p.anschluss(11.6, y_b, "B")
        a_low, b_low = v.endswith("A zieht LOW"), v.endswith("B zieht LOW")
        p.leitung((1.8, y_a), (1.8, 7.6))
        p.schalter(1.8, 7.6, 1.8, 8.6, a_low, "")
        p.leitung((1.8, 8.6), (1.8, y_u))
        p.leitung((10.8, y_b), (10.8, 7.6))
        p.schalter(10.8, 7.6, 10.8, 8.6, b_low, "")
        p.leitung((10.8, 8.6), (10.8, y_u), (1.8, y_u))
        p.masse(6.4, y_u)
        p.knoten(1.8, y_a)
        p.knoten(10.8, y_b)
        p.text(2.2, 8.1, "Teilnehmer A", "w", klein=True, farbe=p.leise)
        p.text(10.4, 8.1, "Teilnehmer B", "e", klein=True, farbe=p.leise)
        p.text(4.0, y_a + 0.45, f"A = {_u(e['a'])}", "w", fett=True, farbe=SPANNUNG)
        p.text(7.0, y_b - 0.45, f"B = {_u(e['b'])}", "w", fett=True, farbe=SPANNUNG)
        _zustand_text(p, x_m - 0.2, y_m + 1.35, e["leitet"])

    def sk_info(self, w, e, v):
        if v.startswith("Teiler"):
            zeilen = [f"U = U_B · R2 / (R1 + R2) = {_u(e['u_aus'])}   ·   Querstrom {_i(e['i'])}",
                      f"t_r = 2.2 · (R1 ∥ R2) · C = 2.2 · {_r(e['r_par'])} · {_c(w['c'])} = {_t(e['t_r'])}   ·   "
                      f"bis ca. {fmt(e['f_max'], 'frequenz')}"]
            if e["u_aus"] > w["ua"] + 0.3:
                zeilen.append(f"⚠ {_u(e['u_aus'])} liegt über U_A + 0.3 V – die Schutzdioden des Eingangs leiten")
                return zeilen, WARN
            if e["u_aus"] < 0.7 * w["ua"]:
                zeilen.append(f"⚠ {_u(e['u_aus'])} liegt unter 0.7 · U_A – wird evtl. nicht als HIGH erkannt")
                return zeilen, WARN
            zeilen.append("Nur von 5 V nach 3.3 V – in Gegenrichtung ist 3.3 V für 5-V-CMOS (V_IH = 3.5 V) zu wenig")
            return zeilen, OK
        zeilen = [f"A = {_u(e['a'])}   ·   B = {_u(e['b'])}   ·   MOSFET {'leitet' if e['leitet'] else 'sperrt'}"
                  f"   ·   U_GS-Reserve = U_A − U_th = {_u(e['reserve'])}",
                  f"Anstieg: t_r(A) = 2.2 · R1 · C = {_t(e['t_r_a'])}   ·   t_r(B) = {_t(e['t_r_b'])}   ·   "
                  f"bis ca. {fmt(e['f_max'], 'frequenz')}"]
        if e["reserve"] < 0.5:
            zeilen.append("⚠ U_A liegt kaum über der Schwellspannung – der MOSFET leitet nicht sicher (Logic-Level-Typ "
                          "mit kleinem U_GS(th) wählen)")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# OPTOKOPPLER
# =============================================================================
class OptokopplerSchaltung(_MitDiagramm):
    TITEL = "🔌 Optokoppler: Signal galvanisch getrennt übertragen (interaktiv)"
    UNTERTITEL = "Reicht der LED-Strom, damit der Fototransistor den Pull-up sicher nach LOW zieht?"
    VARIANTEN = ["Eingang EIN", "Eingang AUS"]
    REGLER = [("ue", "Eingangsspannung U_e", "spannung", 3.0, 30.0, 24.0, {"einheit": "V", "grenzen": (0.5, 300)}),
              ("rv", "Vorwiderstand R_V", "widerstand", 100.0, 47e3, 4.7e3, LOG_R),
              ("ctr", "CTR (Datenblatt, Minimum)", "zahl", 10.0, 300.0, 50.0, {"grenzen": (1, 2000)}),
              ("ub", "Versorgung Ausgang U_B", "spannung", 1.8, 12.0, 3.3, {"einheit": "V", "grenzen": (0.5, 50)}),
              ("rl", "Pull-up R_L", "widerstand", 470.0, 100e3, 4.7e3, LOG_R)]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.6, 10)
    SEITENVERHAELTNIS = 0.5
    U_F = 1.2
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Im Optokoppler leuchtet eine Infrarot-LED auf einen Fototransistor – Eingang und "
        "Ausgang haben keine elektrische Verbindung (getrennte Massen, Isolationsspannung mehrere kV). Der "
        "Fototransistor liefert höchstens I_C = CTR · I_F (Current Transfer Ratio aus dem Datenblatt, z.B. 50 % … "
        "600 %). Der Pull-up R_L verlangt zum sicheren LOW den Strom (U_B − 0.3 V) / R_L. Ist CTR · I_F kleiner, "
        "sättigt der Transistor nicht und der Ausgang bleibt irgendwo in der Mitte – ein undefinierter Pegel. Die "
        "CTR sinkt über die Lebensdauer (LED altert), darum mit Reserve (Faktor ≥ 2) auslegen. Diagramm: Ausgang "
        "über dem LED-Strom, der Knick ist der Übergang in die Sättigung.")

    def sk_rechnen(self, w, v):
        e = sm.optokoppler(w["ue"], self.U_F, w["rv"], w["ctr"] / 100, w["ub"], w["rl"], aktiv=v == "Eingang EIN")
        i_f_max = max(2 * (w["ue"] - self.U_F) / w["rv"], 1e-3)
        e["i_f_achse"] = i_f_max
        e["kurve"] = []
        for k in range(81):
            i_f = i_f_max * k / 80
            r = sm.optokoppler(self.U_F + i_f * w["rv"], self.U_F, w["rv"], w["ctr"] / 100, w["ub"], w["rl"])
            e["kurve"].append((k / 80, r["u_aus"]))
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_d, x_t, x_o, y_o, y_u = 1.2, 4.8, 7.6, 9.8, 2.4, 8.2
        an = v == "Eingang EIN"
        p.quelle(x_q, y_o + 1.6, y_u - 1.6, "U_e", _u(w["ue"]) if an else "0 V")
        p.leitung((x_q, y_o + 1.6), (x_q, y_o))
        p.widerstand(x_q, y_o, x_d, y_o, "R_V", _r(w["rv"]), farbe=STROM if an else None)
        p.leitung((x_d, y_o), (x_d, 4.2))
        p.diode(x_d, 4.2, x_d, 6.0, "LED", f"I_F = {_i(e['i_f'])}", seite="links",
                farbe="#EF4444" if e["i_f"] > 0 else None)
        p.leitung((x_d, 6.0), (x_d, y_u), (x_q, y_u), (x_q, y_u - 1.6))
        a, b = p.p(4.0, 3.3)
        c, d = p.p(8.6, 7.0)
        p.c.create_rectangle(a, b, c, d, outline=p.leise, dash=(4, 3))
        p.text(6.3, 6.75, "getrennt", "center", klein=True, farbe=p.leise)
        for dy in (-0.3, 0.3):                                               # Licht
            (a, b), (c, d) = p.p(5.4, 5.1 + dy), p.p(6.5, 5.1 + dy)
            p.c.create_line(a, b, c, d, fill="#EF4444" if e["i_f"] > 0 else p.leise, width=max(1, p.dick - 1),
                            arrow="last", arrowshape=(p.u * 0.16, p.u * 0.2, p.u * 0.07))
        p.npn(x_t, 5.1)
        p.versorgung(x_o, 1.2, f"U_B = {_u(w['ub'])}")
        p.widerstand(x_o, 1.2, x_o, 3.6, "R_L", _r(w["rl"]), seite="rechts")
        p.leitung((x_t, 4.1), (x_t, 3.6), (11.6, 3.6))
        p.knoten(x_o, 3.6)
        p.anschluss(11.6, 3.6, "U_aus")
        p.leitung((x_t, 6.1), (x_t, 8.8))
        p.masse(x_t, 8.8)
        p.text(x_o + 0.3, 4.2, _u(e["u_aus"]), "w", fett=True,
               farbe=SPANNUNG if (e["gesaettigt"] or not an) else FEHLER[1])
        p.messpunkt(x_o, 3.6, "M1", seite="rechts")
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.6, 22.8
        p.diagramm(gx0, 1.6, gx1, 8.6, [(e["kurve"], SPANNUNG, None, False)], 0.0, w["ub"] * 1.05,
                   "U_aus über dem LED-Strom I_F", [(w["ub"], "U_B"), (0.3, "U_CE,sat")],
                   zeit_text=f"I_F (0 … {_i(e['i_f_achse'])})", einheit="spannung")
        if an:
            _punkt(p, gx0, 1.6, gx1, 8.6, min(e["i_f"] / e["i_f_achse"], 1.0), e["u_aus"], 0.0, w["ub"] * 1.05)

    def sk_info(self, w, e, v):
        if v != "Eingang EIN":
            return [f"LED aus → Fototransistor sperrt → U_aus = U_B = {_u(w['ub'])} (Pull-up)"], OK
        zeilen = [f"I_F = (U_e − U_F) / R_V = ({_u(w['ue'])} − {self.U_F} V) / {_r(w['rv'])} = {_i(e['i_f'])}   ·   "
                  f"P(R_V) = {fmt(e['p_rv'], 'leistung')}",
                  f"I_C,max = CTR · I_F = {_i(e['i_c_max'])}   ·   nötig für LOW: (U_B − 0.3 V) / R_L = {_i(e['i_noetig'])}"
                  f"   ·   Reserve ×{e['reserve']:.2g}"]
        if not e["gesaettigt"]:
            zeilen.append(f"❌ Nicht gesättigt: U_aus = {_u(e['u_aus'])} – kein sauberes LOW. R_L vergrössern oder I_F erhöhen")
            return zeilen, WARN
        if e["reserve"] < 2:
            zeilen.append("⚠ Gesättigt, aber Reserve < 2 – nach einigen Jahren (CTR sinkt) reicht es evtl. nicht mehr")
            return zeilen, WARN
        zeilen.append(f"✓ Sicher gesättigt: U_aus ≈ {_u(e['u_aus'])}")
        return zeilen, OK


# =============================================================================
# H-BRÜCKE
# =============================================================================
class HBrueckeSchaltung(_MitDiagramm):
    TITEL = "🔌 H-Brücke: Motor vorwärts, rückwärts, bremsen (interaktiv)"
    UNTERTITEL = "Vier Schalter – welcher Strompfad entsteht, und warum dürfen nie zwei Schalter einer Seite leiten?"
    VARIANTEN = sm.H_ZUSTAENDE
    REGLER = [("ub", "Versorgung U_B", "spannung", 5.0, 48.0, 12.0, {"einheit": "V", "grenzen": (0.5, 1000)}),
              ("rm", "Motorwiderstand R_M", "widerstand", 0.2, 20.0, 2.0, LOG_RK),
              ("rds", "R_DS(on) je Schalter", "widerstand", 0.002, 0.5, 0.02, {"einheit": "mΩ", "log": True,
                                                                              "grenzen": (1e-4, 100)}),
              ("d", "Tastgrad PWM", "zahl", 0.0, 1.0, 1.0, {"grenzen": (0, 1)}),
              ("emk", "Gegenspannung des drehenden Motors", "spannung", 0.0, 48.0, 0.0, {"einheit": "V",
                                                                                         "grenzen": (0, 1000)})]
    RASTER = (12.6, 10)
    RASTER_SCHMAL = (12.6, 10)
    SEITENVERHAELTNIS = 0.62
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Vier Schalter (MOSFETs) bilden ein H, der Motor ist der Querbalken. VORWÄRTS: S1 und "
        "S4 leiten, der Strom fliesst von links nach rechts durch den Motor. RÜCKWÄRTS: S3 und S2 – umgekehrte "
        "Richtung. BREMSEN: beide unteren Schalter – der Motor ist kurzgeschlossen, seine Gegenspannung treibt einen "
        "Strom, der ihn abbremst. FREILAUF: alle aus – der Motor läuft aus. Der verbotene Zustand: S1 und S2 (oder "
        "S3 und S4) gleichzeitig – ein Kurzschluss direkt über die Versorgung (Shoot-through). Darum lässt jeder "
        "H-Brücken-Treiber beim Umschalten eine kurze Totzeit, in der beide Schalter einer Seite aus sind. Mit PWM "
        "(Tastgrad D) stellt man die mittlere Motorspannung D · U_B ein.")

    PFADE = {"vorwärts": [(1.2, 2.4), (1.2, 1.2), (3.8, 1.2), (3.8, 5.1), (9.0, 5.1), (9.0, 9.0), (1.2, 9.0),
                          (1.2, 7.6)],
             "rückwärts": [(1.2, 2.4), (1.2, 1.2), (9.0, 1.2), (9.0, 5.1), (3.8, 5.1), (3.8, 9.0), (1.2, 9.0),
                           (1.2, 7.6)],
             "bremsen": [(3.8, 5.1), (9.0, 5.1), (9.0, 9.0), (3.8, 9.0), (3.8, 5.1)],
             "⚠ Kurzschluss": [(1.2, 2.4), (1.2, 1.2), (3.8, 1.2), (3.8, 9.0), (1.2, 9.0), (1.2, 7.6)]}

    def sk_rechnen(self, w, v):
        return sm.h_bruecke(v, w["ub"], w["rm"], w["rds"], w["d"], w["emk"])

    def sk_zeichnen(self, p, w, e, v):
        pfad = self.PFADE.get(v)
        if pfad and (abs(e["i_motor"]) > 1e-9 or v == "⚠ Kurzschluss"):
            p.leitung(*pfad, farbe=FEHLER[1] if v == "⚠ Kurzschluss" else STROM, dick=p.dick + 4)
        p.quelle(1.2, 2.4, 7.6, "U_B", _u(w["ub"]))
        p.leitung((1.2, 2.4), (1.2, 1.2), (9.0, 1.2))
        p.leitung((1.2, 7.6), (1.2, 9.0), (9.0, 9.0))
        for name, x, y in (("S1", 3.8, 3.2), ("S2", 3.8, 7.0), ("S3", 9.0, 3.2), ("S4", 9.0, 7.0)):
            p.nmosfet(x, y)
            p.leitung((x, y - 1), (x, 1.2 if y < 5 else 6.0))
            p.leitung((x, y + 1), (x, 4.2 if y < 5 else 9.0))
            p.text(x - 1.0, y - 0.55, name, "e", fett=True)
            _zustand_text(p, x - 1.0, y + 0.4, name in e["an"])
        for x in (3.8, 9.0):
            p.leitung((x, 4.2), (x, 6.0))
            p.knoten(x, 5.1)
            p.knoten(x, 1.2)
            p.knoten(x, 9.0)
        p.leitung((3.8, 5.1), (5.8, 5.1))
        p.leitung((7.0, 5.1), (9.0, 5.1))
        a, b = p.p(5.8, 4.5)
        c, d = p.p(7.0, 5.7)
        p.c.create_oval(a, b, c, d, outline=p.linie, width=p.dick, fill=p.bg)
        p.text(6.4, 5.1, "M", "center", fett=True)
        p.masse(6.4, 9.0)
        richtung = "→" if e["i_motor"] > 1e-9 else ("←" if e["i_motor"] < -1e-9 else "")
        p.text(6.4, 4.0, f"{richtung} {_i(abs(e['i_motor']))}" if richtung else "I = 0", "center", fett=True,
               farbe=STROM)
        p.text(6.4, 6.3, f"U_M = {_u(e['u_motor'])}", "center", klein=True, farbe=SPANNUNG)
        if v == "⚠ Kurzschluss":
            p.text(6.4, 2.2, f"Kurzschluss {_i(e['i_kurzschluss'])}!", "center", fett=True, farbe=FEHLER[1])

    def sk_info(self, w, e, v):
        an = ", ".join(sorted(e["an"])) or "keiner"
        zeilen = [f"Eingeschaltet: {an}   ·   Motorstrom {_i(e['i_motor'])}   ·   Motorspannung {_u(e['u_motor'])}"]
        if v in ("vorwärts", "rückwärts"):
            zeilen.append(f"I = (D · U_B − U_EMK) / (R_M + 2 · R_DS) = ({w['d']:.2f} · {_u(w['ub'])} − {_u(w['emk'])}) / "
                          f"{_r(w['rm'] + 2 * w['rds'])}   ·   Verlust in den Schaltern {fmt(e['p_schalter'], 'leistung')}")
        elif v == "bremsen":
            zeilen.append("Motor kurzgeschlossen: Die Gegenspannung treibt den Strom rückwärts → Bremsmoment "
                          "(ohne Gegenspannung, also im Stillstand, fliesst nichts)")
        elif v == "Freilauf":
            zeilen.append("Alle Schalter aus: Ein laufender Motorstrom fliesst kurz über die Body-Dioden zurück zur "
                          "Versorgung und klingt ab – der Motor läuft frei aus")
        else:
            zeilen.append(f"❌ S1 und S2 leiten gleichzeitig: I = U_B / (2 · R_DS) = {_i(e['i_kurzschluss'])} → "
                          f"{fmt(e['p_schalter'], 'leistung')} in den Schaltern. Totzeit im Treiber vorsehen!")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# MOSFET-GATE-TREIBER
# =============================================================================
class GateTreiberSchaltung(_MitDiagramm):
    TITEL = "🔌 MOSFET schnell schalten: Gate-Treiber und Miller-Plateau (interaktiv)"
    UNTERTITEL = "Das Gate ist ein Kondensator – je mehr Strom der Treiber liefert, desto kürzer die verlustreiche Umschaltzeit"
    VARIANTEN = ["Gate-Treiber-IC", "µC-Pin direkt"]
    STARTWERTE = {"Gate-Treiber-IC": {"udr": 12.0, "rg": 10.0}, "µC-Pin direkt": {"udr": 3.3, "rg": 150.0}}
    REGLER = [("udr", "Treiberspannung U_Tr", "spannung", 2.5, 15.0, 12.0, {"einheit": "V", "grenzen": (0.5, 30)}),
              ("rg", "Gate-Widerstand (inkl. Treiber)", "widerstand", 1.0, 1000.0, 10.0, LOG_RK),
              ("qg", "Gate-Ladung Q_g (bei 10 V)", "ladung", 5e-9, 200e-9, 70e-9, LADUNG),
              ("qgs", "Q_gs", "ladung", 1e-9, 50e-9, 15e-9, LADUNG),
              ("qgd", "Q_gd (Miller)", "ladung", 1e-9, 80e-9, 25e-9, LADUNG),
              ("upl", "Plateauspannung U_pl", "spannung", 1.5, 7.0, 4.5, {"einheit": "V", "grenzen": (0.5, 15)}),
              ("uds", "Drain-Spannung im AUS", "spannung", 5.0, 100.0, 24.0, {"einheit": "V", "grenzen": (0.5, 1000)})]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.0, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Zum Einschalten muss der Treiber die Gate-Ladung Q_g über R_G hineinschieben. "
        "Zuerst steigt u_GS bis zum MILLER-PLATEAU – hier fliesst noch fast kein Drainstrom. Dann bleibt u_GS stehen: "
        "Die Ladung Q_gd wird gebraucht, um die Gate-Drain-Kapazität umzuladen, während u_DS von der vollen Spannung "
        "auf fast null fällt. Genau in dieser Zeit liegen Spannung UND Strom am MOSFET – das ist der Schaltverlust. "
        "Ihre Dauer t = Q_gd · R_G / (U_Tr − U_pl) wird kurz mit kleinem R_G und hoher Treiberspannung. Ein µC-Pin "
        "(3.3 V, ca. 20 mA) ist dafür viel zu schwach – und liegt bei Standard-MOSFETs sogar unter dem Plateau: Der "
        "MOSFET schaltet nie richtig durch. Lösung: Logic-Level-MOSFET (Plateau ≈ 2.5 V) oder Gate-Treiber.")

    def sk_rechnen(self, w, v):
        return sm.gate_ladung(w["udr"], w["rg"], w["qgs"], w["qgd"], w["qg"], w["upl"], w["uds"])

    def sk_zeichnen(self, p, w, e, v):
        x_m, y_m, y_r, y_u = 8.4, 5.4, 1.2, 8.8
        titel = "Treiber" if v == "Gate-Treiber-IC" else "µC"
        p.kasten(0.6, 4.2, 3.0, 6.6, titel)
        p.text(1.8, 5.8, _u(w["udr"]), "center", klein=True, farbe=SPANNUNG)
        p.widerstand(3.0, y_m, x_m - 0.9, y_m, "R_G", _r(w["rg"]))
        p.nmosfet(x_m, y_m, "Q1")
        p.versorgung(x_m, y_r, f"U_DS = {_u(w['uds'])}")
        p.widerstand(x_m, y_r, x_m, 3.6, "Last", "", seite="rechts")
        p.leitung((x_m, 3.6), (x_m, y_m - 1))
        p.leitung((x_m, y_m + 1), (x_m, y_u))
        p.masse(x_m, y_u)
        p.messpunkt(x_m - 1.3, y_m, "u_GS", seite="links")
        p.messpunkt(x_m, 4.0, "u_DS", seite="links")
        p.strom(3.6, y_m + 0.6, 5.4, y_m + 0.6, "", farbe=STROM)
        p.text(4.5, y_m + 1.0, f"î = {_i(e['i_spitze'])}", "n", klein=True, farbe=STROM)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 13.6, 22.8
        p.diagramm(gx0, 1.0, gx1, 4.6, [(e["u_gs"], SPANNUNG, None, False)], 0.0, w["udr"] * 1.1,
                   "u_GS (Gate) – das flache Stück ist das Miller-Plateau", [(w["upl"], "U_pl")],
                   zeit_text="", einheit="spannung")
        p.diagramm(gx0, 6.0, gx1, 9.4, [(e["u_ds"], STROM, None, False)], 0.0, w["uds"] * 1.1,
                   f"u_DS (Drain) fällt während des Plateaus ({_t(e['t2'])})", einheit="spannung",
                   t_ende=e["dauer"])

    def sk_info(self, w, e, v):
        zeilen = [f"Phase 1 bis Plateau: {_t(e['t1'])}   ·   Plateau (Schaltverlust!): t = Q_gd · R_G / (U_Tr − U_pl) = "
                  f"{_t(e['t2'])}   ·   bis voll durchgesteuert ≈ {_t(e['gesamt'])}",
                  f"Gate-Spitzenstrom U_Tr / R_G = {_i(e['i_spitze'])}   ·   während des Plateaus {_i(e['i_plateau'])}"]
        if e["i_spitze"] < 0.05:
            zeilen.append("⚠ Weniger als 50 mA Gate-Strom – die Umschaltung dauert lange, der MOSFET wird warm "
                          "(bei PWM mit hoher Frequenz besonders)")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# ADC-EINGANG: ABTASTKONDENSATOR
# =============================================================================
class AdcEingangSchaltung(_MitDiagramm):
    TITEL = "🔌 ADC-Eingang: Wie hochohmig darf die Quelle sein? (interaktiv)"
    UNTERTITEL = "Der Abtastkondensator muss in der Abtastzeit auf ½ LSB genau geladen werden"
    VARIANTEN = ["ohne C_ext", "mit C_ext"]
    REGLER = [("u", "Eingangsspannung U", "spannung", 0.1, 3.3, 3.0, {"einheit": "V", "grenzen": (0, 30)}),
              ("rext", "Quellwiderstand + R_ext", "widerstand", 100.0, 1e6, 10e3, LOG_R),
              ("cext", "C_ext am Pin", "kapazitaet", 1e-9, 10e-6, 100e-9, LOG_C),
              ("ts", "Abtastzeit t_s", "zeit", 0.1e-6, 20e-6, 1e-6, {"einheit": "µs", "log": True, "grenzen": (1e-9, 1)}),
              ("cs", "Abtastkondensator C_S", "kapazitaet", 2e-12, 30e-12, 10e-12, {"einheit": "pF",
                                                                                    "grenzen": (1e-13, 1e-9)})]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.4, 10)
    SEITENVERHAELTNIS = 0.5
    R_SW, BITS, U_REF = 1e3, 12, 3.3
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Ein SAR-ADC (wie im µC) verbindet beim Abtasten für kurze Zeit t_s einen kleinen "
        "Kondensator C_S über den Schalterwiderstand R_sw mit dem Pin. C_S hat noch die Spannung der letzten Messung "
        "(hier worst case 0 V) und muss in t_s bis auf ½ LSB an U herankommen. OHNE C_EXT lädt er über Quelle + "
        "R_sw: Ist die Quelle zu hochohmig, bleibt ein Fehler (rot über ½ LSB). MIT C_EXT direkt am Pin liefert "
        "dieser die Ladung sofort (Ladungsteilung) – er muss aber gross genug sein (≥ 2^(N+1) · C_S), sonst sackt die "
        "Spannung um mehr als ½ LSB ab und R_ext lädt nicht schnell genug nach. Werte für einen typischen 12-Bit-ADC "
        "(R_sw = 1 kΩ, U_ref = 3.3 V).")

    def sk_rechnen(self, w, v):
        c_ext = w["cext"] if v == "mit C_ext" else 0.0
        e = sm.adc_abtastung(w["u"], w["rext"], c_ext, self.R_SW, w["cs"], w["ts"], self.BITS, self.U_REF)
        e["fehler_anzeige"] = [(t, min(f, 8.0)) for t, f in e["fehler_kurve"]]
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_p, y_o, y_u = 1.2, 6.8, 3.6, 8.8
        p.kasten(7.4, 1.8, 12.2, 8.0, "")
        p.text(9.8, 1.7, "ADC im µC", "s", fett=True)
        p.quelle(x_q, y_o + 1.4, y_u - 1.4, "U", _u(w["u"]))
        p.leitung((x_q, y_o + 1.4), (x_q, y_o))
        p.leitung((x_q, y_u - 1.4), (x_q, y_u), (10.8, y_u))
        p.widerstand(x_q, y_o, 5.0, y_o, "R_ext", _r(w["rext"]))
        p.leitung((5.0, y_o), (7.6, y_o))
        if v == "mit C_ext":
            p.kondensator(6.0, y_o, y_u, "C_ext", _c(w["cext"]), seite="links")
            p.knoten(6.0, y_o)
            p.knoten(6.0, y_u)
        p.anschluss(x_p, y_o)
        p.text(x_p, y_o - 0.45, "Pin", "s", fett=True)
        p.widerstand(7.6, y_o, 9.4, y_o, "R_sw", _r(self.R_SW), laenge=1.0)
        p.schalter(9.4, y_o, 10.4, y_o, True, "")
        p.leitung((10.4, y_o), (10.8, y_o))
        p.kondensator(10.8, y_o, 7.6, "C_S", _c(w["cs"]), seite="links")
        p.leitung((10.8, 7.6), (10.8, y_u))
        p.masse(4.0, y_u)
        fehler = e["fehler_lsb"]
        p.text(9.8, 7.3, f"Rest: {fehler:.2f} LSB", "center", fett=True,
               farbe=SPANNUNG if fehler <= 0.5 else FEHLER[1])
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.0, 22.8
        kurven = [(e["kurve_pin"], p.leise, 1, True), (e["kurve_s"], SPANNUNG, None, False)]
        p.diagramm(gx0, 1.0, gx1, 4.6, kurven, 0.0, max(w["u"], 0.01) * 1.1,
                   "u am Pin (gestrichelt) und an C_S (blau)", zeit_text="", einheit="spannung")
        top = max(f for _t, f in e["fehler_anzeige"])
        p.diagramm(gx0, 6.0, gx1, 9.4, [(e["fehler_anzeige"], STROM, None, False)], 0.0, max(top, 1.0) * 1.05,
                   "Restfehler in LSB (abgeschnitten bei 8)", [(0.5, "½ LSB")], t_ende=w["ts"])

    def sk_info(self, w, e, v):
        zeilen = [f"1 LSB = U_ref / 2^{self.BITS} = {fmt(e['lsb'], 'spannung')}   ·   Restfehler nach t_s: "
                  f"{e['fehler_lsb']:.2f} LSB",
                  f"Ohne C_ext höchstens R = t_s / (C_S · ln 2^(N+1)) − R_sw = {_r(e['r_max'])}   ·   "
                  f"C_ext ≥ (2^(N+1) − 1) · C_S = {_c(e['c_ext_min'])}"]
        if v == "mit C_ext":
            zeilen.append(f"Ladungsteilung: U · C_S / (C_S + C_ext) = {e['teilung_lsb']:.2f} LSB   ·   Tiefpass "
                          f"R_ext · C_ext: fg = {fmt(e['f_g'], 'frequenz')} (begrenzt die Signalfrequenz)")
        if e["fehler_lsb"] > 0.5:
            zeilen.append("⚠ Mehr als ½ LSB Fehler – Quelle niederohmiger, t_s länger oder (genügend grosses) C_ext")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# BUSABSCHLUSS RS-485 / CAN
# =============================================================================
class BusabschlussSchaltung(_MitDiagramm):
    TITEL = "🔌 Busabschluss RS-485 / CAN: Reflexionen auf der Leitung (interaktiv)"
    UNTERTITEL = "Ein Sprung läuft über die Leitung – passt der Abschluss nicht zum Wellenwiderstand, kommt er zurück"
    VARIANTEN = sm.ABSCHLUSS_ARTEN
    REGLER = [("l", "Leitungslänge", "laenge", 1.0, 1200.0, 100.0, {"einheit": "m", "log": True, "grenzen": (0.1, 5000)}),
              ("z0", "Wellenwiderstand Z0 (Kabel)", "widerstand", 50.0, 150.0, 120.0, {"einheit": "Ω", "grenzen": (10, 1000)}),
              ("rq", "Innenwiderstand Sender", "widerstand", 1.0, 100.0, 10.0, {"einheit": "Ω", "grenzen": (0.1, 1e4)}),
              ("u", "Differenzspannung Sender", "spannung", 1.5, 5.0, 2.0, {"einheit": "V", "grenzen": (0.1, 20)}),
              ("rb", "Fail-safe Pull-up/-down (RS-485)", "widerstand", 100.0, 47e3, 560.0, LOG_R)]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.4, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Eine verdrillte Leitung hat einen Wellenwiderstand Z0 (RS-485/CAN: 120 Ω). Ein "
        "Spannungssprung braucht für 100 m etwa 0.5 µs. Am Ende wird er reflektiert, wenn der Abschluss nicht Z0 ist: "
        "Γ = (R − Z0) / (R + Z0) – offen +1, angepasst 0. Die reflektierte Welle läuft zurück, wird am Sender wieder "
        "reflektiert, und der Empfänger sieht eine Treppe, die um den Endwert schwingt (Klingeln). Dabei kann ein "
        "Bit falsch erkannt werden. Mit je 120 Ω an BEIDEN ENDEN des Busses (nicht an jedem Teilnehmer!) wird die "
        "Welle geschluckt. CAN verwendet oft den Split-Abschluss (2 × 60 Ω mit Kondensator zur Mitte) – für das "
        "Signal ist das ebenfalls 120 Ω, zusätzlich werden Gleichtaktstörungen abgeleitet.")

    def _widerstaende(self, v, w):
        rt = {"ohne Abschluss": float("inf"), "nur am Sender": float("inf"), "120 Ω an beiden Enden": 120.0,
              "falscher Wert (1 kΩ)": 1000.0, "CAN Split (2 × 60 Ω + C)": 120.0}[v]
        sender = w["rq"] if v == "ohne Abschluss" else w["rq"] * (rt if rt != float("inf") else 120.0) / \
            (w["rq"] + (rt if rt != float("inf") else 120.0))
        return sender, rt

    def sk_rechnen(self, w, v):
        r_sender, r_last = self._widerstaende(v, w)
        e = sm.leitung_sprung(w["u"], r_sender, w["z0"], r_last, w["l"])
        e["r_last"], e["r_sender"] = r_last, r_sender
        e["failsafe"] = sm.rs485_failsafe(5.0, w["rb"], 120.0, beide_enden=r_last != float("inf"))
        return e

    def sk_zeichnen(self, p, w, e, v):
        y_a, y_b, x_s, x_e = 3.6, 6.4, 3.0, 9.6
        p.kasten(0.4, 2.6, 2.6, 7.4, "Sender")
        p.text(1.5, 5.4, f"R = {_r(w['rq'])}", "center", klein=True, farbe=p.leise)
        p.kasten(10.8, 2.6, 12.0, 7.4, "")
        p.text(11.4, 5.0, "E", "center", fett=True)
        p.leitung((2.6, y_a), (10.8, y_a), farbe=SPANNUNG)
        p.leitung((2.6, y_b), (10.8, y_b), farbe=SPANNUNG)
        for k in range(4):                                                  # Verdrillung andeuten
            x = 4.8 + k * 0.8
            p.leitung((x, y_a + 0.15), (x + 0.5, y_b - 0.15), farbe=p.leise, dick=1)
        p.text(6.4, y_a - 0.35, f"A   ·   {w['l']:g} m, Z0 = {_r(w['z0'])}, t_d = {_t(e['t_d'])}", "s", klein=True)
        p.text(6.4, y_b + 0.35, "B", "n", klein=True)
        if v != "ohne Abschluss":
            p.widerstand(x_s, y_a, x_s, y_b, "R_T", "120 Ω", seite="rechts")
            p.knoten(x_s, y_a)
            p.knoten(x_s, y_b)
        if e["r_last"] != float("inf"):
            if v.startswith("CAN"):
                ym = (y_a + y_b) / 2
                p.widerstand(x_e, y_a, x_e, ym, "", "60 Ω", seite="rechts", laenge=0.9)
                p.widerstand(x_e, ym, x_e, y_b, "", "60 Ω", seite="rechts", laenge=0.9)
                p.leitung((x_e, ym), (x_e - 0.9, ym))                              # C zur Masse, zwischen A und B
                p.kondensator(x_e - 0.9, ym, ym + 0.75, "", "", seite="links")
                p.masse(x_e - 0.9, ym + 0.75)
                p.text(x_e - 0.9, y_a + 0.35, "4.7 nF", "n", klein=True, farbe=p.leise)
            else:
                p.widerstand(x_e, y_a, x_e, y_b, "R_T", _r(e["r_last"]), seite="links")
            p.knoten(x_e, y_a)
            p.knoten(x_e, y_b)
        p.messpunkt(10.8, y_a, "M1", seite="rechts")
        p.text(0.4, 9.2, f"Γ am Ende = {e['g_l']:+.2f}   ·   Γ am Sender = {e['g_q']:+.2f}", "w", fett=True,
               farbe=SPANNUNG if abs(e["g_l"]) < 0.1 else FEHLER[1])
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.6, 22.8
        werte = [y for _t, y in e["kurve"]]
        oben = max(max(werte), e["endwert"]) * 1.15
        unten = min(min(werte), 0.0) - 0.05 * oben
        p.diagramm(gx0, 1.4, gx1, 8.6, [(e["kurve"], SPANNUNG, None, False)], unten, oben,
                   "Spannung am Empfänger (M1) nach dem Sprung",
                   [(e["endwert"], f"Endwert {_u(e['endwert'])}"), (0.2, "+200 mV Schwelle")],
                   einheit="spannung", t_ende=e["dauer"])

    def sk_info(self, w, e, v):
        fs = e["failsafe"]
        zeilen = [f"Laufzeit t_d = l / (0.66 · c) = {_t(e['t_d'])}   ·   Γ = (R − Z0) / (R + Z0) = {e['g_l']:+.2f}   ·   "
                  f"Überschwingen {e['ueberschwingen']:.0f} %",
                  f"RS-485 Ruhepegel (Fail-safe, 5 V, Pull-up/-down {_r(w['rb'])}): U_AB = {_u(fs['u_ab'])} "
                  + ("✓ ≥ 200 mV" if fs["ok"] else f"⚠ < 200 mV – höchstens {_r(fs['r_bias_max'])} verwenden")]
        if abs(e["g_l"]) > 0.1:
            zeilen.append("⚠ Nicht angepasst: Die Reflexionen klingen erst nach mehreren Laufzeiten ab – bei hoher "
                          "Baudrate und langer Leitung werden Bits verfälscht")
            return zeilen, WARN
        return zeilen, OK
