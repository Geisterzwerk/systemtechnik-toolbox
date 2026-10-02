# =============================================================================
# schaltungen/grafiken_mess.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE der Sensor-Messschaltungen.
# Spannung = blau, Strom = rot, Messpunkte = orange.
#
#   PtLeitungSchaltung   Pt100/Pt1000 mit Konstantstrom in 2-, 3- und 4-Leiter-Schaltung:
#                        Leitungsfehler über R_L und Eigenerwärmung über dem Messstrom
#   NtcTeilerSchaltung   NTC im Spannungsteiler vor dem ADC: U_aus und Empfindlichkeit über der Temperatur
#   DmsKetteSchaltung    DMS-Brücke -> Instrumentenverstärker -> ADC: U_aus über der Dehnung, Aussteuergrenzen
#
# Rechnung: schaltungen/mess_mathe.py (Pt-Kennlinie aus messtechnik/rechner.py)
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_pt_leitung")
# =============================================================================

from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN       # -> bauteile/grafiken/schaltplan.py
from schaltungen import mess_mathe as mm                                 # -> schaltungen/mess_mathe.py
from schaltungen.grafiken import _i, _r, _u                              # -> schaltungen/grafiken.py
from schaltungen.grafiken_dioden import FEHLER, _MitDiagramm             # -> schaltungen/grafiken_dioden.py
from schaltungen.grafiken_rc import LOG_R, _punkt                        # -> schaltungen/grafiken_rc.py

AKTIV = "#F59E0B"                     # aktive Sensoren (DMS, NTC) orange hervorheben
T_BEREICH = (-20.0, 120.0)            # Temperaturachse des NTC-Diagramms


def _k(wert):
    return f"{wert:+.2f} K".replace("-", "−")


# =============================================================================
# PT100 IN 2-, 3- UND 4-LEITER-SCHALTUNG
# =============================================================================
class PtLeitungSchaltung(_MitDiagramm):
    TITEL = "🔌 Pt100 / Pt1000: 2-, 3- und 4-Leiter-Schaltung (interaktiv)"
    UNTERTITEL = "Leitungswiderstand und Messstrom verfälschen die Temperatur – welche Schaltung hilft wogegen?"
    VARIANTEN = mm.PT_ARTEN
    SCHALTER = [("pt1000", "Pt1000 statt Pt100")]
    REGLER = [("t", "Temperatur T", "temperatur", -50.0, 400.0, 25.0, {"einheit": "°C", "grenzen": (-200, 850)}),
              ("rl", "Leitungswiderstand je Ader", "widerstand", 0.0, 10.0, 1.0, {"einheit": "Ω", "grenzen": (0, 1000)}),
              ("un", "Unterschied der Adern (3-Leiter)", "zahl", 0.0, 20.0, 5.0, {"grenzen": (0, 100)}),
              ("i", "Messstrom I", "strom", 0.1e-3, 5e-3, 1e-3, {"einheit": "mA", "grenzen": (1e-6, 0.1)}),
              ("k", "Eigenerwärmung (Datenblatt)", "zahl", 0.05, 1.0, 0.4, {"grenzen": (0.0, 10.0)})]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.2, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Eine Konstantstromquelle treibt I durch den Sensor, gemessen wird die Spannung. "
        "2-LEITER: Das Voltmeter misst auch den Spannungsabfall an beiden Adern mit – beim Pt100 (0.385 Ω/K) ergibt "
        "schon 1 Ω je Ader +5 K. 3-LEITER: Eine dritte Ader führt keinen Strom; aus zwei Messungen (U1 über Ader A + "
        "Sensor, U2 über Ader B) wird der Leitungswiderstand abgezogen – fehlerfrei, solange die Adern gleich sind "
        "(Regler „Unterschied“ in %). 4-LEITER: Eigene stromlose Messadern – der Leitungswiderstand fällt ganz weg. "
        "Unabhängig davon heizt der Messstrom den Sensor auf: P = I²·R, ΔT = P · k (k in K/mW aus dem Datenblatt). "
        "Oben: Leitungsfehler über R_L (alle drei Schaltungen), unten: Eigenerwärmung über dem Messstrom.")

    def sk_rechnen(self, w, v):
        r0 = 1000.0 if w["pt1000"] else 100.0
        e = mm.pt_leitung(v, w["t"], r0, w["rl"], w["un"] / 100, w["i"], w["k"])
        e["r0"] = r0
        e["rl_max"] = max(2.0 * w["rl"], 2.0)
        e["kurven"] = {art: mm.pt_fehlerkurve(art, w["t"], r0, e["rl_max"], w["un"] / 100) for art in mm.PT_ARTEN}
        i_max = max(2.0 * w["i"], 2e-3)
        e["i_max"] = i_max
        e["kurve_eigen"] = [(k / 40, (i_max * k / 40) ** 2 * mm.pt_widerstand(w["t"], r0) * 1e3 * w["k"])
                            for k in range(41)]
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_m, x_s, y_o, y_u = 1.4, 3.6, 10.2, 2.6, 8.4
        p.stromquelle(x_q, y_o + 1.6, y_u - 1.6, "I", _i(w["i"]), seite="rechts")
        p.leitung((x_q, y_o + 1.6), (x_q, y_o), (4.6, y_o), farbe=STROM)
        p.leitung((x_q, y_u - 1.6), (x_q, y_u), (4.6, y_u), farbe=STROM)
        rl_text = _r(w["rl"])
        p.widerstand(4.6, y_o, 7.2, y_o, "R_L", rl_text, farbe=STROM)
        rl_b = w["rl"] * (1 + w["un"] / 100) if v == "3-Leiter" else w["rl"]
        p.widerstand(4.6, y_u, 7.2, y_u, "R_L", _r(rl_b), seite="unten", farbe=STROM)
        p.leitung((7.2, y_o), (x_s, y_o), farbe=STROM)
        p.leitung((7.2, y_u), (x_s, y_u), farbe=STROM)
        sensor = "Pt1000" if w["pt1000"] else "Pt100"
        p.widerstand(x_s, y_o, x_s, y_u, sensor, f"{_r(e['r_t'])} bei {w['t']:g} °C", seite="links", farbe=AKTIV)
        if v == "2-Leiter":
            p.knoten(x_m, y_o)
            p.knoten(x_m, y_u)
            p.leitung((x_m, y_o), (x_m, 4.8))
            p.leitung((x_m, 6.2), (x_m, y_u))
            p.messgeraet(x_m, 5.5, "V", _u(e["u_mess"]))
        else:
            y_c = 7.4                                                 # stromlose Messader C (am unteren Anschluss)
            p.knoten(x_s, y_c)
            p.leitung((x_s, y_c), (8.4, y_c))
            p.widerstand(5.2, y_c, 8.4, y_c, "", rl_text, seite="oben")
            if v == "4-Leiter":
                y_d = 3.6                                             # stromlose Messader D (am oberen Anschluss)
                p.knoten(x_s, y_d)
                p.leitung((x_s, y_d), (8.4, y_d))
                p.widerstand(5.2, y_d, 8.4, y_d, "", rl_text, seite="unten")
                p.leitung((5.2, y_d), (x_m, y_d), (x_m, 4.8))
                p.leitung((5.2, y_c), (x_m, y_c), (x_m, 6.2))
                p.messgeraet(x_m, 5.5, "V", _u(e["u_mess"]))
            else:
                p.knoten(x_m, y_o)
                p.leitung((x_m, y_o), (x_m, 4.3))
                p.leitung((5.2, y_c), (x_m, y_c), (x_m, 5.7))
                p.messgeraet(x_m, 5.0, "V", "U1")
                p.knoten(x_m, y_c)
                p.knoten(2.4, y_u)
                p.leitung((x_m, y_c), (2.4, y_c), (2.4, 7.6))
                p.leitung((2.4, y_u), (2.4, 8.2))
                p.text(2.0, 7.9, "U2", "e", klein=True, farbe=SPANNUNG)
                p.c.create_oval(*p.p(2.1, 7.6), *p.p(2.7, 8.2), outline=p.linie, width=p.dick, fill=p.bg)
                p.text(2.4, 7.9, "V", "center", klein=True, fett=False)
        p.text(0.6, 0.6, f"{v}: angezeigt {e['t_anzeige']:.2f} °C  ·  Fehler {_k(e['fehler'])}", "w", fett=True,
               farbe=FEHLER[1] if abs(e["fehler"]) > 0.5 else SPANNUNG)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.6, 22.8
        werte = [y for kurve in e["kurven"].values() for _t, y in kurve]
        lo, hi = min(min(werte), 0.0), max(max(werte), 0.1)
        kurven = [(kurve, SPANNUNG if art == v else p.leise, None if art == v else 1, art != v)
                  for art, kurve in e["kurven"].items()]
        p.diagramm(gx0, 1.0, gx1, 4.6, kurven, lo, hi * 1.1, "Leitungsfehler über R_L je Ader (blau = gewählt)",
                   [(hi, f"{hi:+.2g} K".replace("-", "−")), (0.0, "0 K")], zeit_text=f"R_L (0 … {_r(e['rl_max'])})")
        _punkt(p, gx0, 1.0, gx1, 4.6, w["rl"] / e["rl_max"], e["fehler_leitung"], lo, hi * 1.1)
        top = max(y for _t, y in e["kurve_eigen"])
        p.diagramm(gx0, 6.0, gx1, 9.0, [(e["kurve_eigen"], STROM, None, False)], 0.0, top * 1.1 or 1.0,
                   "Eigenerwärmung ΔT über dem Messstrom", [(top, f"{top:.2g} K")],
                   zeit_text=f"I (0 … {_i(e['i_max'])})")
        _punkt(p, gx0, 6.0, gx1, 9.0, w["i"] / e["i_max"], e["fehler_eigen"], 0.0, top * 1.1 or 1.0, farbe=SPANNUNG)

    def sk_info(self, w, e, v):
        zeilen = [f"R_T = {_r(e['r_t'])}   ·   gemessen {_r(e['r_gem'])}   ·   U = I · R = {_u(e['u_mess'])}",
                  f"Leitungsfehler {_k(e['fehler_leitung'])}   ·   Eigenerwärmung P = I²·R = {fmt(e['p'], 'leistung')} → "
                  f"{_k(e['fehler_eigen'])}   ·   gesamt {_k(e['fehler'])}"]
        if v == "2-Leiter":
            zeilen.append(f"2 · R_L = {_r(2 * w['rl'])} werden als Sensorwiderstand gemessen "
                          f"({2 * w['rl'] / (e['r0'] * 0.00385):.1f} K) – nur für kurze Leitungen oder Pt1000")
        elif v == "3-Leiter":
            zeilen.append("R_L wird abgezogen – es bleibt nur der Unterschied zwischen den Adern als Fehler")
        else:
            zeilen.append("Messadern führen keinen Strom → kein Spannungsabfall, der Leitungsfehler ist null")
        return zeilen, WARN if abs(e["fehler"]) > 0.5 else OK


# =============================================================================
# NTC IM SPANNUNGSTEILER
# =============================================================================
class NtcTeilerSchaltung(_MitDiagramm):
    TITEL = "🔌 NTC im Spannungsteiler vor dem ADC (interaktiv)"
    UNTERTITEL = "Der Festwiderstand bestimmt, wo der Teiler am empfindlichsten und am linearsten ist"
    VARIANTEN = ["NTC unten", "NTC oben"]
    REGLER = [("t", "Temperatur T", "temperatur", -20.0, 120.0, 25.0, {"einheit": "°C", "grenzen": (-55, 200)}),
              ("r25", "NTC R25", "widerstand", 1e3, 100e3, 10e3, LOG_R),
              ("b", "B-Wert", "zahl", 3000.0, 4500.0, 3950.0, {"grenzen": (1000, 6000)}),
              ("rf", "Festwiderstand R_fix", "widerstand", 1e3, 100e3, 10e3, LOG_R),
              ("ub", "Versorgung = U_ref des ADC", "spannung", 1.8, 5.0, 3.3, {"einheit": "V", "grenzen": (0.5, 30)})]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.2, 10)
    SEITENVERHAELTNIS = 0.5
    BITS = 12
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der NTC (Heissleiter) wird mit steigender Temperatur stark niederohmiger – "
        "R(T) = R25 · e^(B·(1/T − 1/298 K)). Im Spannungsteiler mit einem Festwiderstand wird daraus eine Spannung "
        "für den ADC. Die Kurve ist ein S: In der Mitte (dort, wo R_NTC ≈ R_fix) ist sie am steilsten und fast "
        "gerade, an den Rändern flach – dort bringt jedes Kelvin nur noch wenige ADC-Stufen. Darum R_fix so wählen, "
        "dass die Mitte im wichtigsten Temperaturbereich liegt. Speist man den Teiler aus derselben Spannung wie die "
        "ADC-Referenz (ratiometrisch), kürzen sich Schwankungen der Versorgung heraus. Unten: Empfindlichkeit in "
        "ADC-Stufen pro Kelvin (12 Bit).")

    def sk_rechnen(self, w, v):
        unten = v == "NTC unten"
        e = mm.ntc_teiler(w["t"], w["r25"], w["b"], w["rf"], w["ub"], unten, self.BITS)
        e["kurve"] = mm.ntc_kurve(w["r25"], w["b"], w["rf"], w["ub"], unten, *T_BEREICH)
        e["kurve_stufen"] = []
        for k in range(71):
            t = T_BEREICH[0] + (T_BEREICH[1] - T_BEREICH[0]) * k / 70
            e["kurve_stufen"].append((k / 70, mm.ntc_teiler(t, w["r25"], w["b"], w["rf"], w["ub"], unten,
                                                            self.BITS)["stufen_pro_k"]))
        e["r_lin"] = mm.ntc_linear_r(w["r25"], w["b"], 0.0, 100.0)
        return e

    def sk_zeichnen(self, p, w, e, v):
        x, x_a, y_o, y_m, y_u = 4.6, 8.0, 1.6, 5.2, 8.8
        p.versorgung(x, y_o, f"U_B = {_u(w['ub'])}")
        oben_ntc = v == "NTC oben"
        for y1, y2, ist_ntc, seite in ((y_o, y_m, oben_ntc, "links"), (y_m, y_u, not oben_ntc, "links")):
            if ist_ntc:
                p.widerstand(x, y1, x, y2, "NTC ϑ", f"{_r(e['r_ntc'])} bei {w['t']:g} °C", seite=seite, farbe=AKTIV)
            else:
                p.widerstand(x, y1, x, y2, "R_fix", _r(w["rf"]), seite=seite)
        p.knoten(x, y_m)
        p.leitung((x, y_m), (x_a, y_m))
        p.masse(x, y_u)
        p.kasten(x_a, y_m - 1.3, x_a + 2.8, y_m + 1.3, "ADC")
        p.text(x_a + 1.4, y_m + 0.4, f"{self.BITS} Bit", "center", klein=True, farbe=p.leise)
        p.spannung(x_a - 0.6, y_m + 0.4, y_u - 0.4, f"U = {_u(e['u_aus'])}")
        p.messpunkt(x, y_m, "M1", seite="rechts")
        p.strom(x - 1.4, y_o + 0.3, x - 1.4, y_o + 1.4, f"{_i(e['i'])}", seite="links")
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.0, 22.8
        t_pos = (w["t"] - T_BEREICH[0]) / (T_BEREICH[1] - T_BEREICH[0])
        zeit = f"T ({T_BEREICH[0]:g} … {T_BEREICH[1]:g} °C)".replace("-", "−")
        p.diagramm(gx0, 1.0, gx1, 4.6, [(e["kurve"], SPANNUNG, None, False)], 0.0, w["ub"],
                   "U am ADC über der Temperatur", zeit_text=zeit, einheit="spannung")
        if 0 <= t_pos <= 1:
            _punkt(p, gx0, 1.0, gx1, 4.6, t_pos, e["u_aus"], 0.0, w["ub"])
        top = max(y for _t, y in e["kurve_stufen"])
        p.diagramm(gx0, 6.0, gx1, 9.0, [(e["kurve_stufen"], STROM, None, False)], 0.0, top * 1.1,
                   "Empfindlichkeit: ADC-Stufen pro Kelvin", [(top, f"{top:.0f}/K")], zeit_text=zeit)
        if 0 <= t_pos <= 1:
            _punkt(p, gx0, 6.0, gx1, 9.0, t_pos, e["stufen_pro_k"], 0.0, top * 1.1, farbe=SPANNUNG)

    def sk_info(self, w, e, v):
        zeilen = [f"R_NTC({w['t']:g} °C) = {_r(e['r_ntc'])}   ·   U = {_u(e['u_aus'])}   ·   "
                  f"{e['steigung'] * 1e3:+.1f} mV/K".replace("-", "−"),
                  f"{e['stufen_pro_k']:.1f} ADC-Stufen pro K → Auflösung {e['aufloesung_k']:.3f} K   ·   "
                  f"Querstrom {_i(e['i'])}, Eigenerwärmung NTC {fmt(e['p_ntc'], 'leistung')}",
                  f"Am linearsten zwischen 0 und 100 °C mit R_fix = {_r(e['r_lin'])} (Rechner „NTC-Spannungsteiler“)"]
        farbe = OK if e["stufen_pro_k"] >= 5 else WARN
        if e["stufen_pro_k"] < 5:
            zeilen.append("⚠ Weniger als 5 Stufen pro Kelvin – hier ist der Teiler flach, R_fix anpassen")
        return zeilen, farbe


# =============================================================================
# DMS-BRÜCKE + INSTRUMENTENVERSTÄRKER + ADC
# =============================================================================
class DmsKetteSchaltung(_MitDiagramm):
    TITEL = "🔌 DMS-Brücke mit Instrumentenverstärker (interaktiv)"
    UNTERTITEL = "Ein paar Millivolt aus der Brücke werden auf den ADC-Bereich verstärkt – passt die Aussteuerung?"
    VARIANTEN = mm.DMS_ARTEN
    REGLER = [("eps", "Dehnung ε (µm/m)", "zahl", -2000.0, 2000.0, 1000.0, {"grenzen": (-50000, 50000)}),
              ("ue", "Brückenspeisung U_e", "spannung", 1.0, 10.0, 5.0, {"einheit": "V", "grenzen": (0.1, 30)}),
              ("k", "k-Faktor", "zahl", 1.5, 3.5, 2.0, {"grenzen": (0.5, 200)}),
              ("rg", "Verstärkungswiderstand R_G", "widerstand", 10.0, 10e3, 100.0, {"einheit": "Ω", "log": True,
                                                                                    "grenzen": (1.0, 1e6)}),
              ("uref", "Referenz REF", "spannung", 0.0, 5.0, 2.5, {"einheit": "V", "grenzen": (-15, 30)})]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.6, 10)
    SEITENVERHAELTNIS = 0.5
    R_INTERN = 50e3                  # INA128: G = 1 + 50 kΩ / R_G
    U_B = 5.0
    BITS = 16
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Ein Dehnungsmessstreifen ändert seinen Widerstand nur um ΔR/R = k·ε – bei 1000 µm/m "
        "und k = 2 sind das 0.2 %. Die Brücke macht daraus eine Differenzspannung von wenigen mV, die auf der halben "
        "Speisespannung „schwimmt“ (Gleichtakt U_e/2). Der Instrumentenverstärker (hier INA128: G = 1 + 50 kΩ/R_G) "
        "verstärkt nur die Differenz und legt das Ergebnis auf die Referenz REF – so können auch negative Dehnungen "
        "(Stauchung) gemessen werden. Orange = aktive DMS: Viertelbrücke 1, Halbbrücke 2 (mit +ε und −ε, z.B. oben "
        "und unten am Biegebalken), Vollbrücke 4 – mehr aktive DMS = mehr Signal und Temperaturkompensation. "
        "Diagramm: U_aus über der Dehnung mit den Aussteuergrenzen des Verstärkers (U_B = 5 V).")

    def sk_rechnen(self, w, v):
        g = mm.inamp_verstaerkung(r_g=w["rg"], r_intern=self.R_INTERN)
        e = mm.dms_kette(v, w["ue"], w["eps"] * 1e-6, w["k"], g, w["uref"], self.U_B, self.BITS)
        e["g"] = g
        e["eps_max"] = max(2000.0, abs(w["eps"]) * 1.25)
        e["kurve"] = []
        for k in range(81):
            eps = -e["eps_max"] + 2 * e["eps_max"] * k / 80
            e["kurve"].append((k / 80, mm.dms_kette(v, w["ue"], eps * 1e-6, w["k"], g, w["uref"], self.U_B,
                                                    self.BITS)["u_aus"]))
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_l, x_r, y_o, y_m, y_u = 3.2, 6.2, 2.0, 5.4, 8.8
        aktiv = {"Viertelbrücke": {"R2"}, "Halbbrücke": {"R1", "R2"}, "Vollbrücke": {"R1", "R2", "R3", "R4"}}[v]
        p.quelle(1.2, y_o + 1.4, y_u - 1.4, "U_e", _u(w["ue"]))
        p.leitung((1.2, y_o + 1.4), (1.2, y_o), (x_r, y_o))
        p.leitung((1.2, y_u - 1.4), (1.2, y_u), (11.6, y_u))
        for x, (oben, unten) in ((x_l, ("R1", "R2")), (x_r, ("R3", "R4"))):
            for name, (y1, y2) in ((oben, (y_o, y_m)), (unten, (y_m, y_u))):
                wert = "DMS +ε" if name in aktiv and name in ("R2", "R3") else ("DMS −ε" if name in aktiv else "")
                p.widerstand(x, y1, x, y2, name, wert, seite="links" if x == x_l else "rechts",
                             farbe=AKTIV if name in aktiv else None)
            p.knoten(x, y_o)
            p.knoten(x, y_m)
            p.knoten(x, y_u)
        pins = p.opv(9.6, y_m, "INA", plus_oben=True)
        p.leitung((x_l, y_m), (4.7, y_m), (4.7, 1.1), (8.0, 1.1), (8.0, pins["plus"][1]), pins["plus"])
        p.leitung((x_r, y_m), (7.4, y_m), (7.4, pins["minus"][1]), pins["minus"])
        p.leitung(pins["aus"], (11.6, y_m))
        p.anschluss(11.6, y_m, "U_aus")
        p.masse(2.4, y_u)
        p.text(5.4, y_m - 0.35, f"U_d = {fmt(e['u_d'] * 1e3, 'zahl', 3)} mV", "s", klein=True, farbe=SPANNUNG)
        p.text(9.4, 7.0, f"R_G = {_r(w['rg'])} → G = {e['g']:.4g}", "center", klein=True)
        p.text(9.4, 7.6, f"REF = {_u(w['uref'])}", "center", klein=True, farbe=p.leise)
        p.messpunkt(11.0, y_m, "M1", seite="rechts")
        p.text(10.2, 3.6, _u(e["u_aus"]), "w", fett=True, farbe=FEHLER[1] if e["begrenzt"] else SPANNUNG)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.6, 22.8
        p.diagramm(gx0, 1.4, gx1, 8.6, [(e["kurve"], SPANNUNG, None, False)], 0.0, self.U_B,
                   "U_aus über der Dehnung (roter Punkt = jetzt)",
                   [(self.U_B - 0.1, "U_B − 0.1 V"), (0.1, "0.1 V"), (w["uref"], "REF")],
                   zeit_text=f"ε (±{e['eps_max']:.0f} µm/m)", einheit="spannung")
        _punkt(p, gx0, 1.4, gx1, 8.6, (w["eps"] + e["eps_max"]) / (2 * e["eps_max"]), e["u_aus"], 0.0, self.U_B)

    def sk_info(self, w, e, v):
        zeilen = [f"ΔR/R = k · ε = {e['x'] * 100:.3f} %   ·   U_d = {fmt(e['u_d'] * 1e3, 'zahl', 4)} mV "
                  f"({e['mv_v']:.3f} mV/V)   ·   Gleichtakt U_e/2 = {_u(e['u_cm'])}",
                  f"G = 1 + 50 kΩ / R_G = {e['g']:.4g}   ·   U_aus = REF + G · U_d = {_u(e['u_aus_ideal'])}",
                  f"ADC {self.BITS} Bit an {_u(self.U_B)}: 1 LSB = {fmt(e['lsb'], 'spannung')} → am Eingang "
                  f"{fmt(e['lsb_eingang'], 'spannung')} ≈ {e['dehnung_pro_lsb'] * 1e6:.3g} µm/m"]
        if v == "Viertelbrücke" and abs(e["nichtlinear"]) > 0.01:
            zeilen.append(f"Viertelbrücke: {e['nichtlinear']:+.2f} % Nichtlinearität (U_d = U_e·x/(4 + 2x))")
        if e["begrenzt"]:
            zeilen.append("⚠ Ausgang in der Begrenzung – R_G vergrössern (weniger Verstärkung) oder REF anpassen")
            return zeilen, WARN
        return zeilen, OK
