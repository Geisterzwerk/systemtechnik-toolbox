# =============================================================================
# schaltungen/grafiken_netzteil.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE: Netzteile und Quellen.
# Spannung = blau, Strom = rot, Messpunkte = orange.
#
#   QuelleSchaltung          reale Spannungs-/Stromquelle an einer Last, Kennlinie über R_L
#   LinearreglerSchaltung    78xx / LDO / LM317 hinter dem Ladeelko: Dropout, Verlust, Temperatur
#   StrombegrenzungSchaltung Längsregler (Z-Diode + Transistor) mit/ohne Strombegrenzung, U-I-Kennlinie
#   StromquelleOpvSchaltung  geregelte Stromsenke OPV + MOSFET + Shunt, Kennlinie über R_L
#   VirtuelleMasseSchaltung  ±U aus einer Versorgung: Teiler mit/ohne OPV-Puffer bei ungleicher Last
#   SchaltreglerSchaltung    Buck / Boost: Spulenstrom und Schaltknoten über zwei Perioden
#
# Trafo + Gleichrichter + Elko gibt es schon: "schaltung_gleichrichter" (schaltungen/grafiken_dioden.py).
# Rechnung: schaltungen/netzteil_mathe.py
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_linearregler")
# =============================================================================

from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN       # -> bauteile/grafiken/schaltplan.py
from bauteile.grafiken.schaltplan import SchaltungsKarte                 # -> bauteile/grafiken/schaltplan.py
from schaltungen import netzteil_mathe as ntm                            # -> schaltungen/netzteil_mathe.py
from schaltungen.grafiken import _i, _r, _u                              # -> schaltungen/grafiken.py
from schaltungen.grafiken_dioden import FEHLER, _MitDiagramm, _p         # -> schaltungen/grafiken_dioden.py
from schaltungen.grafiken_rc import _punkt                               # -> schaltungen/grafiken_rc.py

LOG_R = {"einheit": "Ω", "log": True, "grenzen": (1e-3, 100e6)}
V = {"einheit": "V", "grenzen": (0.0, 200)}


def _f(wert):
    return fmt(wert, "frequenz", 3)


def _gestrichelt(p, x0, y0, x1, y1, text):
    """Gestrichelter Rahmen (z.B. „reale Quelle“), Text oben links."""
    (a, b), (c, d) = p.p(x0, y0), p.p(x1, y1)
    p.c.create_rectangle(a, b, c, d, outline=p.leise, width=1, dash=(4, 3))
    p.text(x0 + 0.1, y0 - 0.25, text, "w", klein=True, farbe=p.leise)


# =============================================================================
# QUELLENMODELL
# =============================================================================
class QuelleSchaltung(_MitDiagramm):
    TITEL = "🔌 Reale Quelle mit Innenwiderstand (interaktiv)"
    UNTERTITEL = "Je mehr Strom die Last zieht, desto mehr Spannung bleibt im Innenwiderstand hängen"
    VARIANTEN = ntm.QUELLEN_ARTEN
    REGLER = [("u0", "Leerlaufspannung U0", "spannung", 1.0, 30.0, 12.0, V),
              ("i0", "Kurzschlussstrom I0 (Stromquelle)", "strom", 1e-3, 10.0, 1.0,
               {"einheit": "A", "log": True, "grenzen": (1e-6, 1000)}),
              ("ri", "Innenwiderstand R_i", "widerstand", 0.01, 1e3, 2.0, LOG_R),
              ("rl", "Last R_L", "widerstand", 0.01, 10e3, 10.0, LOG_R)]
    RASTER = (23.4, 9.6)
    RASTER_SCHMAL = (13.0, 9.6)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Jede reale Quelle (Batterie, Netzteil, Signalgenerator, Sensor) lässt sich als ideale "
        "Quelle plus Innenwiderstand R_i darstellen. Spannungsquellen-Modell: U0 in Reihe mit R_i – unter Last fällt "
        "I · R_i innen ab, die Klemmenspannung sinkt. Stromquellen-Modell: I0 parallel zu R_i – beide Modelle sind "
        "gleichwertig (U0 = I0 · R_i). Rechts: Klemmenspannung (blau) und Leistung an der Last (rot) über R_L. Die "
        "grösste Leistung kommt bei R_L = R_i an (Leistungsanpassung) – dann gehen aber 50 % im Innenwiderstand "
        "verloren. Netzteile werden deshalb mit R_L ≫ R_i betrieben (Spannungsanpassung).")

    def _q(self, w, v):
        return w["u0"] if v == "Spannungsquelle" else w["i0"]

    def sk_rechnen(self, w, v):
        return ntm.quelle(v, self._q(w, v), w["ri"], w["rl"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_k, x_l, y_o, y_u = 2.0, 6.4, 11.0, 2.2, 8.4
        _gestrichelt(p, 0.6, 1.4, 5.4, 9.0, "reale Quelle")
        if v == "Spannungsquelle":
            p.quelle(x_q, y_o + 1.6, y_u - 1.6, "U0", _u(w["u0"]), seite="rechts")
            p.leitung((x_q, y_o + 1.6), (x_q, y_o))
            p.leitung((x_q, y_u - 1.6), (x_q, y_u))
            p.widerstand(x_q, y_o, 4.8, y_o, "R_i", _r(w["ri"]))
            p.leitung((4.8, y_o), (x_k, y_o))
        else:
            p.stromquelle(x_q, y_o + 1.6, y_u - 1.6, "I0", _i(w["i0"]))
            p.leitung((x_q, y_o + 1.6), (x_q, y_o), (x_k, y_o))
            p.leitung((x_q, y_u - 1.6), (x_q, y_u))
            p.widerstand(4.0, y_o, 4.0, y_u, "R_i", _r(w["ri"]))
            p.knoten(4.0, y_o)
            p.knoten(4.0, y_u)
        p.leitung((x_q, y_u), (x_l, y_u))
        p.leitung((x_k, y_o), (x_l, y_o))
        p.anschluss(x_k, y_o)
        p.anschluss(x_k, y_u)
        p.widerstand(x_l, y_o, x_l, y_u, "R_L", _r(w["rl"]))
        p.spannung(x_k + 0.5, y_o + 1.2, y_u - 1.2, f"U_K = {_u(e['u_k'])}")
        p.strom(x_k + 0.4, y_o - 0.0, x_l - 0.6, y_o, "", farbe=STROM)
        p.text((x_k + x_l) / 2, y_o - 0.45, f"I = {_i(e['i'])}", "s", klein=True, farbe=STROM)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gy0, gx1, gy1 = 15.0, 1.2, 22.8, 8.2
        p.diagramm(gx0, gy0, gx1, gy1, [(e["kurve_u"], SPANNUNG, None, False), (e["kurve_p"], STROM, None, False)],
                   0.0, 1.1, "U_K / U_leer (blau)  ·  P_L / P_max (rot)  über R_L (log)", [(0.5, "50 %"), (1.0, "100 %")],
                   zeit_text="")
        p.text((gx0 + gx1) / 2, gy1 + 0.35, "R_i/100   ·   R_i/10   ·   R_L = R_i   ·   10·R_i   ·   100·R_i",
               "n", klein=True, farbe=p.leise)
        t = e["position"]
        _punkt(p, gx0, gy0, gx1, gy1, t, e["u_k"] / e["u_leer"], 0.0, 1.1, farbe=SPANNUNG)
        _punkt(p, gx0, gy0, gx1, gy1, t, e["p_l"] / e["p_max"], 0.0, 1.1)

    def sk_info(self, w, e, v):
        zeilen = [f"U_K = {_u(e['u_k'])}   ·   I = {_i(e['i'])}   ·   Leerlauf {_u(e['u_leer'])}, "
                  f"Kurzschluss {_i(e['i_kurz'])}",
                  f"P_Last = {_p(e['p_l'])}  (max. {_p(e['p_max'])} bei R_L = R_i)   ·   Verlust in R_i {_p(e['p_ri'])}"
                  f"   ·   Wirkungsgrad {e['eta'] * 100:.0f} %"]
        if v == "Stromquelle":
            zeilen.append(f"Gleichwertige Spannungsquelle: U0 = I0 · R_i = {_u(e['u_leer'])} mit demselben R_i")
        if w["rl"] < w["ri"]:
            zeilen.append("⚠ R_L < R_i: Mehr als die Hälfte der Leistung geht in der Quelle verloren")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# LINEARREGLER
# =============================================================================
class LinearreglerSchaltung(_MitDiagramm):
    TITEL = "🔌 Linearregler hinter dem Ladeelko (interaktiv)"
    UNTERTITEL = "Reicht die Spannung auch im Wellental? Und wie heiss wird der Regler?"
    VARIANTEN = ["78xx", "LDO", "LM317"]
    DROPOUT = {"78xx": 2.0, "LDO": 0.3, "LM317": 1.7}
    REGLER = [("ue", "Eingang: Spitze am Elko", "spannung", 3.0, 35.0, 11.5, V),
              ("du", "Welligkeit ΔU", "spannung", 0.0, 6.0, 1.0, V),
              ("ua", "Ausgang U_aus", "spannung", 1.25, 24.0, 5.0, V),
              ("i", "Laststrom", "strom", 1e-3, 3.0, 0.5, {"einheit": "mA", "log": True, "grenzen": (1e-6, 10)}),
              ("rth", "R_th Sperrschicht → Luft (K/W)", "zahl", 2.0, 80.0, 50.0, {"grenzen": (0.1, 500)})]
    RASTER = (23.4, 9.4)
    RASTER_SCHMAL = (13.8, 9.4)
    SEITENVERHAELTNIS = 0.5
    T_A, T_J_MAX = 25.0, 125.0
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Ein Linearregler ist ein geregelter Widerstand: Er „verheizt“ die Differenz "
        "zwischen Ein- und Ausgang, P = (U_ein − U_aus) · I. Damit er regeln kann, braucht er mindestens die "
        "Dropout-Spannung Abstand – und zwar auch im WELLENTAL der Elko-Spannung (gestrichelt). Wird es dort zu "
        "knapp, kommt die Welligkeit am Ausgang durch (blau). 78xx: ≈ 2 V Dropout, LDO: 0.1 … 0.5 V, LM317: "
        "einstellbar mit zwei Widerständen. R_th = 50 K/W entspricht TO-220 ohne Kühlkörper; die Sperrschicht darf "
        "höchstens 125 °C erreichen.")

    def sk_rechnen(self, w, v):
        e = ntm.linearregler(w["ue"], w["du"], w["ua"], w["i"], self.DROPOUT[v], w["rth"], self.T_A)
        if v == "LM317":
            e["r2"] = ntm.lm317_r2(w["ua"], 240.0)
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_e, x_c1, x0, x1, x_c2, x_l, y_o, y_u = 1.4, 2.8, 4.4, 7.0, 10.0, 11.6, 2.4, 8.6
        p.anschluss(x_e, y_o, "", seite="links")
        p.text(x_e, y_o - 0.45, "vom Elko", "s", klein=True, farbe=p.leise)
        p.leitung((x_e, y_o), (x0, y_o))
        p.kondensator(x_c1, y_o, y_u, "C1", "100 nF", seite="rechts")
        p.knoten(x_c1, y_o)
        p.kasten(x0, y_o - 0.9, x1, y_o + 1.6, v)
        p.text(x0 + 0.15, y_o, "IN", "w", klein=True)
        p.text(x1 - 0.15, y_o, "OUT", "e", klein=True)
        p.leitung((x1, y_o), (x_l, y_o))
        p.kondensator(x_c2, y_o, y_u, "C2", "", seite="rechts")
        p.knoten(x_c2, y_o)
        p.widerstand(x_l, y_o, x_l, y_u, "Last", _i(w["i"]))
        x_m = (x0 + x1) / 2
        if v == "LM317":
            p.text(x_m, y_o + 1.35, "ADJ", "s", klein=True)
            x_r = 8.0
            p.leitung((x_m, y_o + 1.6), (x_m, 5.0), (x_r, 5.0))
            p.widerstand(x_r, y_o, x_r, 5.0, "R1", "240 Ω", seite="rechts")
            p.knoten(x_r, y_o)
            p.knoten(x_r, 5.0)
            p.widerstand(x_r, 5.0, x_r, y_u, "R2", _r(e["r2"]), seite="rechts")
            p.knoten(x_r, y_u)
        else:
            p.text(x_m, y_o + 1.35, "GND", "s", klein=True)
            p.leitung((x_m, y_o + 1.6), (x_m, y_u))
            p.knoten(x_m, y_u)
        p.leitung((x_e, y_u), (x_l, y_u))
        p.anschluss(x_e, y_u, "", seite="links")
        p.masse(5.0 if v == "LM317" else 4.6, y_u)
        p.messpunkt(x_c1, y_o, "M1", seite="rechts")
        p.messpunkt(x_l, y_o, "M2", seite="rechts")
        farbe = FEHLER[1] if e.get("t_j", 0) > self.T_J_MAX else STROM
        p.text(x_m, y_o - 1.25, f"P = {_p(e['p'])}", "s", fett=True, farbe=farbe)
        if not getattr(self, "mit_diagramm", True):
            return
        g = max(w["ue"], w["ua"]) * 1.15
        marken = [(w["ua"] + self.DROPOUT[v], "+U_D"), (w["ua"], "U_aus")]
        p.diagramm(15.2, 1.2, 22.8, 8.2, [(e["kurve_ein"], p.leise, 1, True), (e["kurve_aus"], SPANNUNG, None, False)],
                   0.0, g, "U_ein (gestrichelt)  ·  U_aus (blau)  ·  U_D = Dropout", marken, einheit="spannung")

    def sk_info(self, w, e, v):
        zeilen = [f"U_ein: Spitze {_u(w['ue'])}, Wellental {_u(e['u_tal'])}, Mittel {_u(e['u_mittel'])}   ·   "
                  f"Reserve im Tal {_u(e['reserve'])}",
                  f"P = (U_ein − U_aus) · I = {_p(e['p'])}   ·   η = {e['eta'] * 100:.0f} %   ·   "
                  f"T_j = 25 °C + P · R_th = {e['t_j']:.0f} °C"]
        if v == "LM317":
            zeilen.append(f"LM317: U_aus = 1.25 V · (1 + R2 / R1) + 50 µA · R2  →  R2 = {_r(e['r2'])} bei R1 = 240 Ω")
        if not e["regelt"]:
            zeilen.append(f"❌ Dropout: Im Wellental fehlen {_u(-e['reserve'])} – die Welligkeit kommt am Ausgang "
                          "durch → grösserer Elko, höhere Trafospannung oder LDO")
            return zeilen, FEHLER
        if e["t_j"] > self.T_J_MAX:
            zeilen.append(f"❌ Zu heiss: Kühlkörper nötig mit R_th ≤ {(self.T_J_MAX - self.T_A) / e['p']:.1f} K/W "
                          "(gesamt) – oder Spannung vor dem Regler senken / Schaltregler")
            return zeilen, FEHLER
        return zeilen, OK


# =============================================================================
# LÄNGSREGLER MIT STROMBEGRENZUNG
# =============================================================================
class StrombegrenzungSchaltung(_MitDiagramm):
    TITEL = "🔌 Längsregler mit Strombegrenzung (interaktiv)"
    UNTERTITEL = "Z-Diode + Transistor als einfaches Netzteil – und ein zweiter Transistor, der bei Kurzschluss bremst"
    VARIANTEN = ["ohne Begrenzung", "mit Strombegrenzung"]
    REGLER = [("ue", "Eingang U_e", "spannung", 5.0, 30.0, 15.0, V),
              ("uz", "Z-Spannung U_Z", "spannung", 2.0, 20.0, 10.0, V),
              ("rl", "Last R_L", "widerstand", 0.1, 1e3, 22.0, LOG_R),
              ("rs", "Shunt R_S", "widerstand", 0.1, 10.0, 1.0, LOG_R)]
    RASTER = (23.4, 9.8)
    RASTER_SCHMAL = (12.2, 9.8)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Die Z-Diode hält die Basis von T1 fest, der Emitter folgt mit 0.7 V Abstand: "
        "U_a ≈ U_Z − 0.7 V, der Transistor liefert den Laststrom (Emitterfolger). Ohne Begrenzung zerstört ein "
        "Kurzschluss T1. Mit Begrenzung fliesst der Laststrom durch den Shunt R_S; erreicht die Spannung daran "
        "≈ 0.6 V, leitet T2 und zieht den Basisstrom von T1 ab – der Strom bleibt bei I_max = 0.6 V / R_S. "
        "Rechts die U-I-Kennlinie: waagrecht (Spannung konstant) bis I_max, dann senkrecht (Strom konstant). "
        "Achtung: Bei Kurzschluss liegt fast die ganze Eingangsspannung an T1 → Verlust U_e · I_max.")

    def _rs(self, w, v):
        return w["rs"] if v == self.VARIANTEN[1] else None

    def sk_rechnen(self, w, v):
        return ntm.laengsregler(w["ue"], w["uz"], w["rl"], self._rs(w, v))

    def sk_zeichnen(self, p, w, e, v):
        x_z, x_t1, x_l, y_o, y_b, y_u = 2.6, 7.0, 10.2, 1.2, 3.4, 9.0
        p.versorgung(4.0, y_o, f"+U_e = {_u(w['ue'])}")
        p.leitung((x_z, y_o), (x_t1, y_o), (x_t1, y_b - 1.0))
        p.widerstand(x_z, y_o, x_z, y_b, "R_V", "", seite="links")
        p.diode(x_z, y_u, x_z, y_b, "Z", _u(w["uz"]), art="z", seite="links")
        p.knoten(x_z, y_b)
        p.npn(x_t1, y_b, "T1")
        p.leitung((x_z, y_b), (x_t1 - 0.9, y_b))
        y_a = 7.0
        if v == self.VARIANTEN[1]:
            p.widerstand(x_t1, y_b + 1.0, x_t1, y_a, "R_S", _r(w["rs"]))
            # T2: B-E über R_S, Kollektor an die Basis von T1
            x_t2, y_t2 = 4.6, 5.9
            p.npn(x_t2, y_t2, "T2")
            p.leitung((x_t2, y_t2 - 1.0), (x_t2, y_b))
            p.knoten(x_t2, y_b)
            p.leitung((x_t1, 4.6), (x_t2 - 0.9 - 0.4, 4.6), (x_t2 - 0.9 - 0.4, y_t2), (x_t2 - 0.9, y_t2))
            p.knoten(x_t1, 4.6)
            p.leitung((x_t2, y_t2 + 1.0), (x_t2, y_a), (x_t1, y_a))
        else:
            p.leitung((x_t1, y_b + 1.0), (x_t1, y_a))
        p.knoten(x_t1, y_a)
        p.leitung((x_t1, y_a), (x_l, y_a))
        p.widerstand(x_l, y_a, x_l, y_u, "R_L", _r(w["rl"]))
        p.leitung((x_z, y_u), (x_l, y_u))
        p.masse(5.6, y_u)
        farbe = FEHLER[1] if e["begrenzt"] else SPANNUNG
        p.text(x_t1 + 0.3, y_a + 0.45, f"U_a = {_u(e['u_a'])}", "w", fett=True, farbe=farbe)
        p.text(x_t1 + 0.3, y_a + 0.95, f"I = {_i(e['i'])}", "w", fett=True, farbe=STROM)
        p.messpunkt(x_t1, y_a, "M1", seite="links")
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gy0, gx1, gy1 = 14.2, 1.4, 22.8, 8.4
        g = e["u_a0"] * 1.2
        p.diagramm(gx0, gy0, gx1, gy1, [(e["kurve"], SPANNUNG, None, False)], 0.0, g,
                   "U_a über dem Laststrom  ·  roter Punkt = jetzt", [(e["u_a0"], _u(e["u_a0"]))], einheit="spannung",
                   zeit_text=f"I (0 … {_i(e['i_achse'])})")
        _punkt(p, gx0, gy0, gx1, gy1, min(e["i"] / e["i_achse"], 1.0), e["u_a"], 0.0, g)

    def sk_info(self, w, e, v):
        zeilen = [f"U_a ≈ U_Z − 0.7 V = {_u(e['u_a0'])} (Leerlauf)   ·   jetzt {_u(e['u_a'])} bei {_i(e['i'])}   ·   "
                  f"Verlust in T1 {_p(e['p_t1'])}"]
        if v == self.VARIANTEN[0]:
            zeilen.append(f"Bei Kurzschluss: Strom nur durch β und den Basisstrom begrenzt → T1 wird zerstört")
            return zeilen, (WARN if w["rl"] > 1 else FEHLER)
        zeilen.append(f"I_max = 0.6 V / R_S = {_i(e['i_max'])}   ·   Verlust in T1 bei Kurzschluss ≈ "
                      f"{_p(e['p_t1_kurz'])}   ·   in R_S {_p(e['p_rs'])}")
        if e["begrenzt"]:
            zeilen.append("Strombegrenzung aktiv: Die Spannung bricht ein, der Strom bleibt bei I_max")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# GEREGELTE STROMQUELLE
# =============================================================================
class StromquelleOpvSchaltung(_MitDiagramm):
    TITEL = "🔌 Geregelte Stromquelle mit OPV + MOSFET (interaktiv)"
    UNTERTITEL = "Der OPV regelt die Spannung am Shunt – und damit den Strom, egal wie gross die Last ist"
    REGLER = [("us", "Sollspannung U_soll", "spannung", 0.01, 2.5, 0.1, {"einheit": "mV", "grenzen": (1e-4, 10)}),
              ("rsh", "Shunt R_S", "widerstand", 0.1, 100.0, 1.0, LOG_R),
              ("ub", "Versorgung U_B", "spannung", 3.0, 30.0, 12.0, V),
              ("rl", "Last R_L", "widerstand", 1.0, 10e3, 47.0, LOG_R)]
    RASTER = (23.4, 9.6)
    RASTER_SCHMAL = (11.8, 9.6)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der OPV vergleicht die Sollspannung am + Eingang mit der Spannung am Shunt "
        "(− Eingang) und stellt das Gate so ein, dass beide gleich sind: U_Shunt = U_soll, also I = U_soll / R_S. "
        "Die Last liegt im Drain-Zweig und hat keinen Einfluss – bis die Versorgung nicht mehr reicht: "
        "I · (R_L + R_S) ≤ U_B. Danach ist der MOSFET voll durchgesteuert und der Strom sinkt (Knick in der "
        "Kennlinie). Der MOSFET verheizt den Rest: P = (U_B − I · (R_L + R_S)) · I – am meisten bei kleiner Last. "
        "Anwendungen: LED-Treiber, elektronische Last, Akku-Entladetester, Sensorspeisung 4 … 20 mA.")

    def sk_rechnen(self, w, v):
        return ntm.stromquelle_opv(w["us"], w["rsh"], w["ub"], w["rl"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_o, x_m, y_o, y_u = 1.6, 4.4, 8.4, 1.2, 9.0
        p.versorgung(x_m, y_o, f"+U_B = {_u(w['ub'])}")
        p.widerstand(x_m, y_o, x_m, 4.4, "R_L", _r(w["rl"]))
        p.nmosfet(x_m, 5.4, "Q1")
        pins = p.opv(x_o, 5.4, plus_oben=True)
        p.leitung(pins["aus"], (x_m - 0.9, 5.4))
        p.quelle(x_q, 7.3, y_u - 0.3, "U_soll", _u(w["us"]), seite="rechts")      # unter der Rückführung
        p.leitung((x_q, 7.3), (x_q, pins["plus"][1]), pins["plus"])
        p.leitung((x_q, y_u - 0.3), (x_q, y_u), (x_m, y_u))
        y_s = 6.9
        p.leitung((x_m, 6.4), (x_m, y_s))
        p.knoten(x_m, y_s)
        p.leitung(pins["minus"], (2.8, pins["minus"][1]), (2.8, y_s), (x_m, y_s))
        p.widerstand(x_m, y_s, x_m, y_u, "R_S", _r(w["rsh"]))
        p.masse(5.4, y_u)
        p.messpunkt(x_m, y_s, "M1", seite="links")
        farbe = STROM if e["regelt"] else FEHLER[1]
        p.text(x_m - 0.35, 3.0, f"I = {_i(e['i'])}", "e", fett=True, farbe=farbe)
        if not getattr(self, "mit_diagramm", True):
            return
        i_max = e["i_soll"] * 1.2
        gx0, gy0, gx1, gy1 = 14.2, 1.4, 22.8, 8.2
        p.diagramm(gx0, gy0, gx1, gy1, [(e["kurve"], STROM, None, False)], 0.0, i_max,
                   "Strom über R_Last  ·  Punkt = jetzt", [(e["i_soll"], _i(e["i_soll"]))], einheit="strom",
                   zeit_text=f"R_L (0 … {_r(e['r_achse'])})")
        _punkt(p, gx0, gy0, gx1, gy1, w["rl"] / e["r_achse"], e["i"], 0.0, i_max, farbe=SPANNUNG)

    def sk_info(self, w, e, v):
        zeilen = [f"I = U_soll / R_S = {_i(e['i_soll'])}   ·   jetzt {_i(e['i'])}   ·   Spannung an der Last {_u(e['u_last'])}",
                  f"Regelt bis R_L ≈ {_r(e['r_last_max'])}   ·   Verlust MOSFET {_p(e['p_mos'])} "
                  f"(max. {_p(e['p_mos_max'])} bei R_L = 0)   ·   Shunt {_p(e['p_shunt'])}"]
        if not e["regelt"]:
            zeilen.append("⚠ Last zu gross: MOSFET voll durchgesteuert, der Strom erreicht den Sollwert nicht")
            return zeilen, WARN
        if e["p_mos"] > 1.0:
            zeilen.append("⚠ Über 1 W im MOSFET – Kühlkörper vorsehen")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# VIRTUELLE MASSE / BIPOLARE VERSORGUNG
# =============================================================================
class VirtuelleMasseSchaltung(SchaltungsKarte):
    TITEL = "🔌 ±U aus einer Versorgung: virtuelle Masse (interaktiv)"
    UNTERTITEL = "Ein Spannungsteiler als neue Mitte – hält er, wenn die Lasten ungleich sind?"
    SCHALTER = [("opv", "OPV-Puffer (Rail-Splitter)")]
    REGLER = [("ub", "Versorgung U_B", "spannung", 5.0, 30.0, 12.0, V),
              ("r", "Teiler-Widerstände R", "widerstand", 1e3, 1e6, 10e3, {**LOG_R, "einheit": "kΩ"}),
              ("rl1", "Last an +U (R_L1)", "widerstand", 10.0, 1e6, 1e3, {**LOG_R, "einheit": "kΩ"}),
              ("rl2", "Last an −U (R_L2)", "widerstand", 10.0, 1e6, 100e3, {**LOG_R, "einheit": "kΩ"})]
    RASTER = (14.6, 9.6)
    SEITENVERHAELTNIS = 0.62
    ERKLAERUNG = (
        "Was zeigt die Grafik?  OPV-Schaltungen brauchen oft ±U. Aus einer einzelnen Versorgung (Batterie, "
        "USB) macht ein Spannungsteiler eine neue Mitte M – die „virtuelle Masse“: oben +U_B/2, unten −U_B/2. "
        "Das funktioniert nur, solange beide Seiten gleich belastet werden: Zieht die positive Seite mehr Strom, "
        "fliesst er durch den Teiler und verschiebt die Mitte. Ein OPV als Spannungsfolger (Rail-Splitter, z.B. "
        "TLE2426) hält M fest auf U_B/2 und liefert bzw. schluckt die Differenz der Lastströme – bis zu seinem "
        "Ausgangsstrom (hier 20 mA). Echte ±U: Trafo mit Mittelanzapfung oder eine Ladungspumpe.")

    def sk_rechnen(self, w, v):
        return ntm.virtuelle_masse(w["ub"], w["r"], w["rl1"], w["rl2"], w["opv"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_t, x_l, y_o, y_u = 1.6, 4.2, 12.0, 1.2, 8.8
        y_m = 5.0
        p.quelle(x_q, y_o + 2.0, y_u - 2.0, "U_B", _u(w["ub"]), seite="rechts")
        p.leitung((x_q, y_o + 2.0), (x_q, y_o), (x_l, y_o))
        p.leitung((x_q, y_u - 2.0), (x_q, y_u), (x_l, y_u))
        p.widerstand(x_t, y_o, x_t, y_m, "R", _r(w["r"]), seite="rechts")
        p.widerstand(x_t, y_m, x_t, y_u, "R", _r(w["r"]), seite="rechts")
        p.knoten(x_t, y_o)
        p.knoten(x_t, y_u)
        p.knoten(x_t, y_m)
        if w["opv"]:
            pins = p.opv(7.6, y_m + 0.5, plus_oben=True, versorgung=False)
            p.leitung((x_t, y_m), pins["plus"])
            p.leitung(pins["minus"], (6.0, pins["minus"][1]), (6.0, 7.0), (9.2, 7.0), (9.2, y_m + 0.5))
            p.leitung(pins["aus"], (x_l, y_m + 0.5))
            p.knoten(9.2, y_m + 0.5)
            y_mid = y_m + 0.5
            p.text(7.6, 7.4, f"I_OPV = {_i(e['i_opv'])}", "n", klein=True, farbe=STROM)
        else:
            p.leitung((x_t, y_m), (x_l, y_m))
            y_mid = y_m
        p.widerstand(x_l, y_o, x_l, y_mid, "R_L1", _r(w["rl1"]), seite="links")
        p.widerstand(x_l, y_mid, x_l, y_u, "R_L2", _r(w["rl2"]), seite="links")
        p.knoten(x_l, y_mid)
        p.messpunkt(x_l, y_mid, "M", seite="rechts")
        p.masse(10.4, y_mid)
        p.text(x_l + 0.4, (y_o + y_mid) / 2, f"+{_u(e['u_plus'])}", "w", fett=True, farbe=SPANNUNG)
        p.text(x_l + 0.4, (y_mid + y_u) / 2, _u(e["u_minus"]), "w", fett=True, farbe=SPANNUNG)

    def sk_info(self, w, e, v):
        zeilen = [f"Mitte M = {_u(e['u_m'])} (soll {_u(w['ub'] / 2)})   →   +U = {_u(e['u_plus'])},  −U = {_u(e['u_minus'])}",
                  f"Lastströme: oben {_i(e['i_l1'])}, unten {_i(e['i_l2'])}   ·   Querstrom im Teiler {_i(e['i_teiler'])}"]
        if e["opv_am_limit"]:
            zeilen.append("⚠ OPV am Stromlimit (20 mA) – die Mitte verschiebt sich trotzdem → stärkerer Puffer "
                          "(z.B. Push-Pull-Endstufe) oder echte ±U")
            return zeilen, WARN
        if abs(e["abweichung"]) > 0.05 * w["ub"]:
            zeilen.append("⚠ Mitte um mehr als 5 % von U_B verschoben – die Lasten sind zu ungleich für einen "
                          "einfachen Teiler → OPV-Puffer einschalten")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# SCHALTREGLER BUCK / BOOST
# =============================================================================
class SchaltreglerSchaltung(_MitDiagramm):
    TITEL = "🔌 Schaltregler: Buck und Boost (interaktiv)"
    UNTERTITEL = "Ein schneller Schalter und eine Spule – Spannung wandeln fast ohne Verluste"
    VARIANTEN = ntm.SCHALTREGLER_ARTEN
    REGLER = [("ue", "Eingang U_e", "spannung", 2.0, 36.0, 12.0, V),
              ("ua", "Ausgang U_a", "spannung", 1.0, 48.0, 5.0, V),
              ("ia", "Ausgangsstrom I_a", "strom", 0.01, 5.0, 1.0, {"einheit": "A", "log": True, "grenzen": (1e-5, 100)}),
              ("f", "Schaltfrequenz f", "frequenz", 10e3, 2e6, 100e3, {"einheit": "kHz", "log": True, "grenzen": (1.0, 1e8)}),
              ("l", "Spule L", "induktivitaet", 1e-6, 1e-3, 47e-6, {"einheit": "µH", "log": True, "grenzen": (1e-9, 1)}),
              ("c", "Ausgangskondensator C", "kapazitaet", 1e-6, 1e-3, 22e-6,
               {"einheit": "µF", "log": True, "grenzen": (1e-9, 1)})]
    RASTER = (23.4, 10)
    RASTER_SCHMAL = (11.8, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Statt Spannung zu verheizen, schaltet ein MOSFET mit z.B. 100 kHz ein und aus; "
        "die Spule speichert Energie und glättet den Strom, der Kondensator die Spannung. BUCK (abwärts): "
        "Schalter EIN – Strom steigt in der Spule; AUS – die Spule treibt den Strom über die Diode weiter. "
        "U_a = D · U_e (D = Einschaltanteil). BOOST (aufwärts): Schalter EIN – Spule lädt sich gegen GND auf; "
        "AUS – ihre Spannung addiert sich zu U_e: U_a = U_e / (1 − D). Oben der Spulenstrom (Dreieck um den "
        "Mittelwert, ΔI = Rippelstrom), unten die Spannung am Schaltknoten. Wird der Strom 0 (Lückbetrieb, DCM), "
        "gelten die einfachen Formeln nicht mehr. Ideal gerechnet (ohne Verluste).")

    # Beim Umschalten typische Werte setzen (Buck braucht U_a < U_e, Boost U_a > U_e) - sichtbar in den Reglern
    STARTWERTE = {ntm.SCHALTREGLER_ARTEN[0]: {"ue": 12.0, "ua": 5.0, "ia": 1.0},
                  ntm.SCHALTREGLER_ARTEN[1]: {"ue": 5.0, "ua": 12.0, "ia": 0.5}}

    def sk_neu(self):
        v = self.sk_v()
        if v != getattr(self, "_sr_variante", v) and getattr(self, "sk_regler", None):
            for schluessel, wert in self.STARTWERTE[v].items():
                self.sk_regler[schluessel].setzen(wert)
        self._sr_variante = v
        super().sk_neu()

    def sk_rechnen(self, w, v):
        return ntm.schaltregler(v, w["ue"], w["ua"], w["ia"], w["f"], w["l"], w["c"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_out, x_l, y_o, y_u = 1.4, 8.4, 10.4, 2.6, 8.6
        p.quelle(x_q, y_o + 1.6, y_u - 1.6, "U_e", _u(w["ue"]))
        p.leitung((x_q, y_o + 1.6), (x_q, y_o))
        p.leitung((x_q, y_u - 1.6), (x_q, y_u), (x_l, y_u))
        if v == ntm.SCHALTREGLER_ARTEN[0]:
            x_sw = 4.8
            p.schalter(x_q + 0.8, y_o, x_sw - 0.8, y_o, False, "S (MOSFET)")
            p.leitung((x_q, y_o), (x_q + 0.8, y_o))
            p.leitung((x_sw - 0.8, y_o), (x_sw, y_o))
            p.diode(x_sw, y_u, x_sw, y_o, "D", "Schottky", art="schottky", seite="links")
            p.spule(x_sw, y_o, x_out, y_o, "L", fmt(w["l"], "induktivitaet", 3))
            p.knoten(x_sw, y_u)
        else:
            x_sw = 5.0
            p.spule(x_q, y_o, x_sw, y_o, "L", fmt(w["l"], "induktivitaet", 3))
            p.leitung((x_sw, y_o), (x_sw, 4.4))
            p.schalter(x_sw, 4.4, x_sw, 6.4, False, "S")
            p.leitung((x_sw, 6.4), (x_sw, y_u))
            p.knoten(x_sw, y_u)
            p.diode(x_sw, y_o, x_out, y_o, "D", "Schottky", art="schottky")
        p.knoten(x_sw, y_o)
        p.messpunkt(x_sw, y_o, "SW", seite="rechts")
        p.leitung((x_out, y_o), (x_l, y_o))
        p.knoten(x_out, y_o)
        p.kondensator(x_out, y_o, y_u, "C", fmt(w["c"], "kapazitaet", 3), seite="rechts")
        p.knoten(x_out, y_u)
        p.widerstand(x_l, y_o, x_l, y_u, "Last", _i(w["ia"]))
        p.masse(3.2, y_u)
        p.text(x_out + 0.3, y_o - 0.5, f"U_a = {_u(w['ua'])}", "w", fett=True, farbe=SPANNUNG)
        p.text(x_q - 0.4, y_u + 1.0, f"D = {e['d'] * 100:.0f} %   ·   f = {_f(w['f'])}", "w", fett=True)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.0, 22.8
        i_top = max(i for _, i in e["kurve_i"]) * 1.15 or 1e-3
        farbe = STROM if e["ccm"] else FEHLER[1]
        p.diagramm(gx0, 1.2, gx1, 4.8, [(e["kurve_i"], farbe, None, False)], 0.0, i_top,
                   f"Spulenstrom i_L  ·  ΔI = {_i(e['delta_i'])}", [(e["i_l"], f"Ø {_i(e['i_l'])}")], zeit_text="",
                   einheit="strom")
        u_top = e["u_sw_max"] * 1.15
        p.diagramm(gx0, 6.2, gx1, 9.4, [(e["kurve_u"], SPANNUNG, None, False)], -0.1 * u_top, u_top,
                   "Spannung am Schaltknoten SW", [], zeit_text=f"2 Perioden = {fmt(2 / w['f'], 'zeit', 3)}",
                   einheit="spannung")

    def sk_info(self, w, e, v):
        formel = "D = U_a / U_e" if v == ntm.SCHALTREGLER_ARTEN[0] else "D = 1 − U_e / U_a"
        zeilen = [f"{formel} = {e['d'] * 100:.1f} %   ·   Spulenstrom Ø {_i(e['i_l'])}, ΔI = {_i(e['delta_i'])} "
                  f"({e['delta_i'] / e['i_l'] * 100:.0f} %), Spitze {_i(e['i_spitze'])}",
                  f"Ausgangswelligkeit ≈ {_u(e['delta_u'])}   ·   für ΔI = 30 %: L ≈ {fmt(e['l_30'], 'induktivitaet', 3)}"]
        if not e["ccm"]:
            zeilen.append("⚠ Lückbetrieb (DCM): Der Spulenstrom erreicht 0 – U_a würde mit diesem D steigen, der "
                          "Regler verkleinert D. Grössere Spule oder höhere Frequenz für Dauerbetrieb")
            return zeilen, WARN
        if e["delta_i"] > 0.6 * e["i_l"]:
            zeilen.append("⚠ Rippelstrom über 60 % – hohe Spitzenströme und Verluste → L grösser")
            return zeilen, WARN
        return zeilen, OK
