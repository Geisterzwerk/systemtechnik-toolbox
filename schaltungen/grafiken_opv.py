# =============================================================================
# schaltungen/grafiken_opv.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE der OPV-Grundschaltungen.
# Spannung = blau, Strom = rot, Messpunkte = orange.
#
#   OpvVerstaerkerSchaltung  Spannungsfolger, nichtinvertierend, invertierend (+ Zeitdiagramm, Begrenzung)
#   AddiererSchaltung        invertierender Summierer mit drei Eingängen
#   DifferenzSchaltung       Differenzverstärker (4 R) und Instrumentenverstärker (3 OPV)
#   SchmittSchaltung         Komparator und Schmitt-Trigger mit verrauschtem Eingang (+ Zeitdiagramm)
#   IntegratorSchaltung      Integrator und Differenzierer, ideal oder praxisgerecht (+ Zeitdiagramm)
#
# OPV-Symbol: bauteile/grafiken/schaltplan.py -> Schaltplan.opv()
# Rechnung:   schaltungen/opv_mathe.py
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_opv_verstaerker")
# =============================================================================

from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN       # -> bauteile/grafiken/schaltplan.py
from bauteile.grafiken.schaltplan import SchaltungsKarte                 # -> bauteile/grafiken/schaltplan.py
from schaltungen import opv_mathe as om                                  # -> schaltungen/opv_mathe.py
from schaltungen.grafiken import _i, _r, _u                              # -> schaltungen/grafiken.py
from schaltungen.grafiken_dioden import FEHLER, _MitDiagramm             # -> schaltungen/grafiken_dioden.py

LOG_R = {"einheit": "kΩ", "log": True, "grenzen": (1.0, 100e6)}
U_SIGNAL = {"einheit": "V", "grenzen": (-100, 100)}
U_B = ("ub", "Versorgung ±U_B", "spannung", 3.0, 18.0, 12.0, {"einheit": "V", "grenzen": (1.0, 50)})


def _marken(e, g):
    """Aussteuergrenzen als Hilfslinien – nur wenn sie im Diagramm liegen."""
    return [(m, t) for m, t in ((e["u_max"], "+U_max"), (e["u_min"], "−U_max")) if abs(m) <= g]


# =============================================================================
# VERSTÄRKER: FOLGER, NICHTINVERTIEREND, INVERTIEREND
# =============================================================================
class OpvVerstaerkerSchaltung(_MitDiagramm):
    TITEL = "🔌 OPV als Verstärker (interaktiv)"
    UNTERTITEL = "Folger, nichtinvertierend, invertierend – Verstärkung, Eingangswiderstand und Begrenzung"
    VARIANTEN = om.VERSTAERKER_ARTEN
    SCHALTER = [("rail", "Rail-to-Rail-Ausgang")]
    REGLER = [U_B,
              ("r1", "R1", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("r2", "R2 (Gegenkopplung)", "widerstand", 1e3, 1e6, 47e3, LOG_R),
              ("ue", "Eingang Gleichanteil", "spannung", -5.0, 5.0, 0.0, U_SIGNAL),
              ("uh", "Eingang û (Sinus)", "spannung", 0.0, 5.0, 1.0, {"einheit": "V", "grenzen": (0.0, 100)})]
    RASTER = (23.4, 9.6)
    RASTER_SCHMAL = (11.8, 9.6)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Ein OPV verstärkt die Differenz seiner Eingänge riesig (10⁵ … 10⁶). Mit "
        "Gegenkopplung (R2 vom Ausgang zurück an −) regelt er seinen Ausgang so, dass U+ = U− wird – „virtueller "
        "Kurzschluss“. Daraus folgt alles: Folger Vu = 1, nichtinvertierend Vu = 1 + R2/R1 (Eingang hochohmig am +), "
        "invertierend Vu = −R2/R1 (der − Eingang ist virtuelle Masse, der Eingang sieht nur R1). Der Ausgang kommt "
        "nicht über die Versorgung hinaus: Ein klassischer OPV bleibt ≈ 1.5 V darunter, Rail-to-Rail-Typen fast "
        "bis an die Schiene. Rechts: Eingang gestrichelt, Ausgang blau – oben/unten abgeschnitten = übersteuert.")

    def sk_rechnen(self, w, v):
        return om.verstaerker(v, w["r1"], w["r2"], w["ue"], w["ub"], rail=w["rail"], u_hat=w["uh"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_n, x_o, y_o, y_u = 3.0, 5.2, 7.4, 4.0, 8.6
        x_a, x_r = 9.4, 10.6
        invertierend = v == "invertierend"
        pins = p.opv(x_o, y_o, plus_oben=not invertierend)
        p.leitung(pins["aus"], (x_a, y_o), (x_r, y_o))
        p.knoten(x_a, y_o)
        p.anschluss(x_r, y_o, "u_a")
        p.wechselquelle(x_q, y_o - 0.5 + 1.4, y_u - 0.8, "u_e", f"{_u(w['ue'])} ± {_u(w['uh'])}")
        p.leitung((x_q, y_o - 0.5 + 1.4), (x_q, y_o - 0.5))
        p.leitung((x_q, y_u - 0.8), (x_q, y_u), (x_r, y_u))
        p.anschluss(x_r, y_u)
        p.masse(4.0, y_u)
        if invertierend:
            # Eingang über R1 an −, R2 oben herum zum Ausgang, + an Masse
            p.widerstand(x_q, y_o - 0.5, x_n, y_o - 0.5, "R1", _r(w["r1"]))
            p.leitung((x_n, y_o - 0.5), pins["minus"])
            p.knoten(x_n, y_o - 0.5)
            p.leitung((x_n, y_o - 0.5), (x_n, 1.9))
            p.widerstand(x_n, 1.9, x_a, 1.9, "R2", _r(w["r2"]))
            p.leitung((x_a, 1.9), (x_a, y_o))
            p.leitung(pins["plus"], (5.8, y_o + 0.5), (5.8, y_u))
            p.knoten(5.8, y_u)
            p.messpunkt(x_n, 2.7, "M1 = 0 V", seite="rechts")
            p.strom(3.5, y_o - 0.05, 4.7, y_o - 0.05, "", farbe=STROM)
            p.text(4.1, y_o + 0.3, f"î = {_i((abs(w['ue']) + w['uh']) / w['r1'])}", "n", klein=True, farbe=STROM)
        else:
            p.leitung((x_q, y_o - 0.5), pins["plus"])
            p.leitung(pins["minus"], (x_n, y_o + 0.5), (x_n, 6.0))
            if v == "Spannungsfolger":
                p.leitung((x_n, 6.0), (x_a, 6.0), (x_a, y_o))
            else:
                p.knoten(x_n, 6.0)
                p.widerstand(x_n, 6.0, x_a, 6.0, "R2", _r(w["r2"]), seite="unten")
                p.leitung((x_a, 6.0), (x_a, y_o))
                p.widerstand(x_n, 6.0, x_n, y_u, "R1", _r(w["r1"]), seite="links")
                p.knoten(x_n, y_u)
            p.messpunkt(x_q + 1.2, y_o - 0.5, "M1", seite="rechts")
        p.messpunkt(x_a, y_o, "M2", seite="rechts")
        farbe = FEHLER[1] if e["begrenzt"] else SPANNUNG
        p.text(x_a + 0.2, y_o + 0.55, f"Vu = {e['vu']:.3g}", "w", fett=True, farbe=farbe)
        if not getattr(self, "mit_diagramm", True):
            return
        g = max(max(abs(u) for _, u in e["kurve_ideal"]), max(abs(u) for _, u in e["kurve_ein"]), 1e-4) * 1.15
        p.diagramm(14.0, 1.4, 22.8, 8.6, [(e["kurve_ein"], p.leise, 1, True), (e["kurve_ideal"], p.leise, 1, True),
                                         (e["kurve_aus"], SPANNUNG, None, False)],
                   -g, g, "u_e und u_a ideal (gestrichelt)  ·  u_a tatsächlich (blau)", _marken(e, g),
                   einheit="spannung")

    def sk_info(self, w, e, v):
        r_ein = "≈ ∞ (nur der + Eingang, z.B. 10¹² Ω)" if e["r_ein"] == float("inf") else _r(e["r_ein"])
        formel = {"Spannungsfolger": "Vu = 1", "nichtinvertierend": "Vu = 1 + R2 / R1",
                  "invertierend": "Vu = −R2 / R1"}[v]
        zeilen = [f"{formel} = {e['vu']:.4g}  ({e['db']:.1f} dB)   ·   Ua (Gleichanteil) = {_u(e['u_a'])}   ·   "
                  f"r_ein = {r_ein}",
                  f"Bandbreite ≈ GBW / (1 + R2/R1) = 1 MHz / {e['rauschverstaerkung']:.3g} = "
                  f"{fmt(e['f_g'], 'frequenz', 3)}   ·   Aussteuerung {_u(e['u_min'])} … +{_u(e['u_max'])}"]
        if e["begrenzt"]:
            zeilen.append("⚠ Übersteuert: Der Ausgang wird an der Aussteuergrenze abgeschnitten → Eingang "
                          "kleiner, Verstärkung kleiner oder höhere Versorgung")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# ADDIERER
# =============================================================================
class AddiererSchaltung(SchaltungsKarte):
    TITEL = "🔌 Addierer / Summierverstärker (interaktiv)"
    UNTERTITEL = "Die Ströme aller Eingänge treffen sich an der virtuellen Masse und fliessen gemeinsam durch R_f"
    REGLER = [("u1", "U1", "spannung", -5.0, 5.0, 1.0, U_SIGNAL),
              ("u2", "U2", "spannung", -5.0, 5.0, 2.0, U_SIGNAL),
              ("u3", "U3", "spannung", -5.0, 5.0, -0.5, U_SIGNAL),
              ("r1", "R1", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("r2", "R2", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("r3", "R3", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("rf", "R_f (Gegenkopplung)", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              U_B]
    RASTER = (13.8, 9.2)
    SEITENVERHAELTNIS = 0.6
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der − Eingang liegt durch die Gegenkopplung auf 0 V (virtuelle Masse). Jeder "
        "Eingang treibt deshalb unabhängig von den anderen den Strom I = U / R in den Knoten – die Eingänge "
        "beeinflussen sich nicht. Weil in den OPV kein Strom fliesst, muss die Summe aller Ströme durch R_f: "
        "Ua = −R_f · (U1/R1 + U2/R2 + U3/R3). Mit gleichen Widerständen ist das die (negative) Summe, mit "
        "verschiedenen eine gewichtete Summe – Grundlage von Mischpulten und einfachen D/A-Wandlern.")

    def _werte(self, w):
        return [w["u1"], w["u2"], w["u3"]], [w["r1"], w["r2"], w["r3"]]

    def sk_rechnen(self, w, v):
        u, r = self._werte(w)
        return om.addierer(u, r, w["rf"], w["ub"])

    def sk_zeichnen(self, p, w, e, v):
        x_e, x_n, x_o, x_a, y_o = 2.8, 6.2, 8.6, 10.6, 6.7
        pins = p.opv(x_o, y_o)
        u, r = self._werte(w)
        for k, y in enumerate((3.0, 4.6, y_o - 0.5)):
            p.anschluss(x_e, y, f"U{k + 1} = {_u(u[k])}", seite="links")
            p.widerstand(x_e, y, x_n, y, f"R{k + 1}", _r(r[k]))
            p.text(x_e - 0.25, y + 0.42, f"I{k + 1} = {_i(e['stroeme'][k])}", "e", klein=True, farbe=STROM)
            if k < 2:
                p.knoten(x_n, y)
        p.leitung((x_n, 1.5), (x_n, pins["minus"][1]), pins["minus"])
        p.knoten(x_n, pins["minus"][1])
        p.widerstand(x_n, 1.5, x_a, 1.5, "R_f", _r(w["rf"]))
        p.leitung((x_a, 1.5), (x_a, y_o))
        p.leitung(pins["aus"], (x_a, y_o), (x_a + 1.0, y_o))
        p.knoten(x_a, y_o)
        p.anschluss(x_a + 1.0, y_o)
        p.leitung(pins["plus"], (7.0, pins["plus"][1]), (7.0, 8.2))
        p.masse(7.0, 8.2)
        farbe = FEHLER[1] if e["begrenzt"] else SPANNUNG
        p.text(x_a + 0.2, y_o + 0.55, f"U_a = {_u(e['u_a'])}", "w", fett=True, farbe=farbe)
        p.text(x_n + 0.2, 2.15, f"I_f = {_i(e['i_f'])}", "w", klein=True, farbe=STROM)
        p.messpunkt(x_n, pins["minus"][1], "M1", seite="links")

    def sk_info(self, w, e, v):
        teile = "  ".join(f"{g:+.3g}·U{k + 1}" for k, g in enumerate(e["gewichte"]))
        zeilen = [f"Ua = −R_f · (U1/R1 + U2/R2 + U3/R3) = {teile} = {_u(e['u_a_ideal'])}",
                  f"Strom durch R_f = Summe der Eingangsströme = {_i(e['i_f'])}   ·   Spannung an M1 = 0 V (virtuelle Masse)"]
        if e["begrenzt"]:
            zeilen.append(f"⚠ Ausgang begrenzt auf {_u(e['u_a'])} – die Summe ist zu gross für die Versorgung")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# DIFFERENZ- UND INSTRUMENTENVERSTÄRKER
# =============================================================================
class DifferenzSchaltung(SchaltungsKarte):
    TITEL = "🔌 Differenz- und Instrumentenverstärker (interaktiv)"
    UNTERTITEL = "Nur die Differenz verstärken, den Gleichtakt unterdrücken – und was Widerstandstoleranzen anrichten"
    VARIANTEN = ["Differenzverstärker", "Instrumentenverstärker"]
    REGLER = [("ucm", "Gleichtakt U_cm", "spannung", -5.0, 5.0, 2.5, U_SIGNAL),
              ("ud", "Differenz U_d = U2 − U1", "spannung", -1.0, 1.0, 0.05, {"einheit": "mV", "grenzen": (-100, 100)}),
              ("r1", "R1", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("r2", "R2", "widerstand", 1e3, 1e6, 100e3, LOG_R),
              ("rg", "R_G (nur Instrumentenv.)", "widerstand", 100.0, 1e6, 10e3, LOG_R),
              ("tol", "Toleranz der Widerstände", "prozent", 0.0, 0.05, 0.01, {"einheit": "%", "grenzen": (0.0, 0.45)}),
              U_B]
    RASTER = (17.6, 9.8)
    SEITENVERHAELTNIS = 0.6
    R_INA = 25e3                       # Widerstände der Eingangsstufe (wie INA128: G = 1 + 50 kΩ / R_G)
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Sensoren (Messbrücke, Shunt auf der High-Side) liefern eine kleine Differenz "
        "auf einer grossen Gleichtaktspannung. Der Differenzverstärker rechnet Ua = R2/R1 · (U2 − U1) – aber nur, "
        "wenn die vier Widerstände exakt passen: Schon 1 % Toleranz lässt einen Teil des Gleichtakts durch "
        "(Gleichtaktfehler, CMRR ≈ (1 + R2/R1) / (4 · Toleranz)). Ausserdem ist er niederohmig (R1 belastet die "
        "Quelle). Der Instrumentenverstärker setzt zwei nichtinvertierende OPV davor: beide Eingänge hochohmig, "
        "Verstärkung mit EINEM Widerstand R_G (G = 1 + 2R/R_G), und die Differenz ist schon vor der Ausgangsstufe "
        "gross – der gleiche Gleichtaktfehler fällt viel weniger ins Gewicht.")

    def _ina(self, v):
        return v == self.VARIANTEN[1]

    def sk_rechnen(self, w, v):
        u1, u2 = w["ucm"] - w["ud"] / 2, w["ucm"] + w["ud"] / 2
        if self._ina(v):
            e = om.instrumenten(u1, u2, self.R_INA, w["rg"], w["r1"], w["r2"], w["tol"], w["ub"])
        else:
            e = om.differenz(u1, u2, w["r1"], w["r2"], w["tol"], w["ub"])
            e["g"] = e["a_d"]
        e["u1"], e["u2"] = u1, u2
        return e

    def _stufe2(self, p, w, e, x_e, y_minus, y_plus, x_o):
        """Differenzverstärker: R1 von den Eingängen, R2 zum Ausgang bzw. nach GND."""
        pins = p.opv(x_o, (y_minus + y_plus) / 2)
        x_n, x_a = x_o - 2.0, x_o + 2.0
        p.widerstand(x_e, y_minus, x_n, y_minus, "R1", _r(w["r1"]))
        p.leitung((x_n, y_minus), (x_n + 0.4, y_minus), (x_n + 0.4, pins["minus"][1]), pins["minus"])
        p.knoten(x_n, y_minus)
        p.leitung((x_n, y_minus), (x_n, y_minus - 1.6))
        p.widerstand(x_n, y_minus - 1.6, x_a, y_minus - 1.6, "R2", _r(w["r2"]))
        p.leitung((x_a, y_minus - 1.6), (x_a, pins["aus"][1]))
        p.leitung(pins["aus"], (x_a + 0.8, pins["aus"][1]))
        p.knoten(x_a, pins["aus"][1])
        p.anschluss(x_a + 0.8, pins["aus"][1])
        p.widerstand(x_e, y_plus, x_n, y_plus, "R1", _r(w["r1"]), seite="unten")
        p.leitung((x_n, y_plus), (x_n + 0.4, y_plus), (x_n + 0.4, pins["plus"][1]), pins["plus"])
        p.knoten(x_n, y_plus)
        p.widerstand(x_n, y_plus, x_n, y_plus + 2.0, "R2", _r(w["r2"]), seite="rechts")
        p.masse(x_n, y_plus + 2.0)
        farbe = FEHLER[1] if e["begrenzt"] else SPANNUNG
        p.text(x_a + 0.2, pins["aus"][1] + 0.55, f"U_a = {_u(e['u_a'])}", "w", fett=True, farbe=farbe)
        p.messpunkt(x_a, pins["aus"][1], "M1", seite="rechts")

    def sk_zeichnen(self, p, w, e, v):
        if not self._ina(v):
            p.anschluss(3.2, 3.9, f"U1 = {_u(e['u1'])}", seite="links")
            p.anschluss(3.2, 6.1, f"U2 = {_u(e['u2'])}", seite="links")
            self._stufe2(p, w, e, 3.2, 3.9, 6.1, 9.4)
            return
        # ---- Eingangsstufe: zwei nichtinvertierende OPV, R_G verbindet die − Eingänge ----
        x_o, x_g, x_k = 4.6, 2.8, 6.2
        oben = p.opv(x_o, 2.2, plus_oben=True, versorgung=False)
        unten = p.opv(x_o, 7.2, plus_oben=False, versorgung=False)
        for pin, text, dy, anker in ((oben["plus"], f"U1 = {_u(e['u1'])}", -0.3, "sw"),
                                     (unten["plus"], f"U2 = {_u(e['u2'])}", 0.3, "nw")):
            p.anschluss(0.6, pin[1])
            p.leitung((0.6, pin[1]), pin)
            p.text(0.4, pin[1] + dy, text, anker, fett=True)
        p.leitung(oben["minus"], (x_g, oben["minus"][1]), (x_g, 3.6))
        p.leitung(unten["minus"], (x_g, unten["minus"][1]), (x_g, 5.8))
        p.widerstand(x_g, 3.6, x_g, 5.8, "R_G", _r(w["rg"]), seite="links")
        for y_k, y_aus in ((3.6, 2.2), (5.8, 7.2)):
            p.knoten(x_g, y_k)
            p.widerstand(x_g, y_k, x_k, y_k, "", "")
            p.leitung((x_k, y_k), (x_k, y_aus))
        p.text((x_g + x_k) / 2, 4.15, f"R = {_r(self.R_INA)}", "n", klein=True, farbe=p.leise)
        p.leitung(oben["aus"], (x_k, 2.2), (7.0, 2.2), (7.0, 3.9))
        p.leitung(unten["aus"], (x_k, 7.2), (7.0, 7.2), (7.0, 6.1))
        p.knoten(x_k, 2.2)
        p.knoten(x_k, 7.2)
        p.text(x_k + 0.15, 1.75, _u(e["u_innen"][0]), "w", klein=True, farbe=SPANNUNG)
        p.text(x_k + 0.15, 7.65, _u(e["u_innen"][1]), "w", klein=True, farbe=SPANNUNG)
        self._stufe2(p, w, e, 7.0, 3.9, 6.1, 12.4)

    def sk_info(self, w, e, v):
        cmrr = "∞ (ideale Widerstände)" if e["cmrr"] == float("inf") else f"{e['cmrr_db']:.0f} dB"
        if self._ina(v):
            zeilen = [f"G = (1 + 2R / R_G) · R2/R1 = {e['g1']:.3g} · {w['r2'] / w['r1']:.3g} = {e['g']:.4g}   ·   "
                      f"beide Eingänge hochohmig"]
        else:
            zeilen = [f"Ua = R2/R1 · (U2 − U1) = {e['g']:.4g} · {_u(e['u_d'])}   ·   "
                      f"Eingangswiderstand: − {_r(e['r_ein_minus'])}, + {_r(e['r_ein_plus'])}"]
        zeilen.append(f"Ua = {_u(e['u_a'])}   (davon Gleichtaktfehler {_u(e['fehler_cm'])} aus U_cm = {_u(e['u_cm'])})"
                      f"   ·   CMRR ≈ {cmrr}")
        if e["begrenzt"] or e.get("innen_begrenzt"):
            zeilen.append("⚠ Ein Ausgang erreicht die Aussteuergrenze → Verstärkung oder Gleichtakt kleiner")
            return zeilen, WARN
        if abs(e["fehler_cm"]) > 0.01 * max(abs(e["u_a"]), 1e-3):
            zeilen.append("⚠ Gleichtaktfehler über 1 % des Ergebnisses → genauere Widerstände (0.1 %), "
                          + ("integrierter INA (abgeglichene Widerstände)" if self._ina(v)
                             else "Widerstandsnetzwerk oder Instrumentenverstärker"))
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# KOMPARATOR UND SCHMITT-TRIGGER
# =============================================================================
class SchmittSchaltung(_MitDiagramm):
    TITEL = "🔌 Komparator und Schmitt-Trigger (interaktiv)"
    UNTERTITEL = "Störung auf dem Eingang aufdrehen: Wer schaltet einmal, wer flattert?"
    VARIANTEN = ["Komparator", "Schmitt invertierend", "Schmitt nichtinvertierend"]
    REGLER = [U_B,
              ("uh", "Eingang û (Sinus)", "spannung", 0.5, 10.0, 3.0, {"einheit": "V", "grenzen": (0.01, 100)}),
              ("rs", "Störung (Spitze)", "spannung", 0.0, 3.0, 0.4, {"einheit": "V", "grenzen": (0.0, 100)}),
              ("r1", "R1", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("rf", "R_f (Mitkopplung)", "widerstand", 1e3, 1e6, 100e3, LOG_R),
              ("uref", "U_ref (Offset)", "spannung", -5.0, 5.0, 0.0, U_SIGNAL)]
    RASTER = (23.4, 10.2)
    RASTER_SCHMAL = (11.8, 10.2)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Ein Komparator hat KEINE Gegenkopplung: Ist U+ > U−, geht der Ausgang an die obere "
        "Grenze, sonst an die untere. Wackelt das Eingangssignal in der Nähe der Schwelle (Störung, Rauschen), "
        "schaltet er jedes Mal mit – der Ausgang flattert. Der Schmitt-Trigger koppelt über R_f einen Teil des "
        "Ausgangs MIT-gekoppelt auf den + Eingang zurück: Die Schwelle springt nach dem Umschalten weg. Es gibt "
        "eine obere (U_T+) und eine untere Schwelle (U_T−) – solange die Störung kleiner als die Hysterese ist, "
        "schaltet er genau einmal. U_ref verschiebt beide Schwellen (Offset). Invertierend: Signal am −, Ausgang "
        "geht bei hohem Eingang nach unten.")

    def _art(self, v):
        return {"Komparator": "Komparator", "Schmitt invertierend": "invertierend",
                "Schmitt nichtinvertierend": "nichtinvertierend"}[v]

    def sk_rechnen(self, w, v):
        return om.komparator_sim(self._art(v), w["uh"], w["rs"], w["ub"], w["r1"], w["rf"], w["uref"])

    def sk_zeichnen(self, p, w, e, v):
        art = self._art(v)
        x_q, x_n, x_o, y_o, y_u = 2.2, 5.0, 7.6, 4.6, 9.6
        x_a = 9.8
        pins = p.opv(x_o, y_o, plus_oben=art != "invertierend")
        p.leitung(pins["aus"], (x_a, y_o), (x_a + 0.8, y_o))
        p.anschluss(x_a + 0.8, y_o, "u_a")
        p.wechselquelle(x_q, y_o + 0.9, y_u - 1.2, "u_e", f"û {_u(w['uh'])}")
        p.leitung((x_q, y_o + 0.9), (x_q, y_o - 0.5))
        p.leitung((x_q, y_u - 1.2), (x_q, y_u), (x_a + 0.8, y_u))
        p.anschluss(x_a + 0.8, y_u)
        p.masse(3.6, y_u)
        y_ref = 8.0                                           # U_ref-Quelle von y_ref bis y_u
        if art == "Komparator":
            p.leitung((x_q, y_o - 0.5), pins["plus"])
            p.leitung(pins["minus"], (x_n, y_o + 0.5), (x_n, y_ref))
        elif art == "invertierend":
            p.leitung((x_q, y_o - 0.5), pins["minus"])
            x_p = 6.0
            p.leitung(pins["plus"], (x_p, y_o + 0.5), (x_p, 6.4))
            p.knoten(x_p, 6.4)
            p.widerstand(x_p, 6.4, x_a, 6.4, "R_f", _r(w["rf"]), seite="unten")
            p.leitung((x_a, 6.4), (x_a, y_o))
            p.leitung((x_p, 6.4), (x_n, 6.4))
            p.widerstand(x_n, 6.4, x_n, y_ref, "R1", _r(w["r1"]), seite="links")
        else:
            p.widerstand(x_q, y_o - 0.5, x_n + 0.8, y_o - 0.5, "R1", _r(w["r1"]))
            p.leitung((x_n + 0.8, y_o - 0.5), pins["plus"])
            p.knoten(x_n + 0.8, y_o - 0.5)
            p.leitung((x_n + 0.8, y_o - 0.5), (x_n + 0.8, 1.8))
            p.widerstand(x_n + 0.8, 1.8, x_a, 1.8, "R_f", _r(w["rf"]))
            p.leitung((x_a, 1.8), (x_a, y_o))
            p.leitung(pins["minus"], (x_n, y_o + 0.5), (x_n, y_ref))
        p.quelle(x_n, y_ref, y_u, "U_ref", _u(w["uref"]), seite="rechts")
        p.knoten(x_n, y_u)
        if art != "Komparator":
            p.knoten(x_a, y_o)
        p.messpunkt(x_a, y_o, "M1", seite="rechts")
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.2, 22.8
        g = (w["uh"] + w["rs"]) * 1.15
        schwellen = [(e["u_tp"], "U_T+"), (e["u_tm"], "U_T−")] if art != "Komparator" else [(e["u_tp"], "U_ref")]
        p.diagramm(gx0, 1.0, gx1, 5.2, [(e["kurve_ein"], SPANNUNG, 1, False)], -g, g,
                   "Eingang mit Störung  ·  Schaltschwellen", [(m, t) for m, t in schwellen if abs(m) <= g],
                   zeit_text="", einheit="spannung")
        farbe = STROM if e["wechsel"] <= e["wechsel_soll"] else FEHLER[1]
        ga = max(e["u_max"], 1.0) * 1.15
        p.diagramm(gx0, 6.6, gx1, 9.6, [(e["kurve_aus"], farbe, None, False)], -ga, ga,
                   f"Ausgang: {e['wechsel']} Umschaltungen (ohne Störung {e['wechsel_soll']})", zeit_text="t",
                   einheit="spannung")

    def sk_info(self, w, e, v):
        if v == "Komparator":
            zeilen = [f"Schaltet bei U_e = U_ref = {_u(e['u_tp'])} (keine Hysterese)   ·   "
                      f"Ausgang {_u(e['u_min'])} / +{_u(e['u_max'])}"]
        else:
            formel = ("U_T± = (U_ref · R_f ± U_sat · R1) / (R1 + R_f)" if v == "Schmitt invertierend"
                      else "U_T± = U_ref · (1 + R1/R_f) ± U_sat · R1/R_f")
            zeilen = [f"{formel}:  U_T+ = {_u(e['u_tp'])},  U_T− = {_u(e['u_tm'])}",
                      f"Hysterese {_u(e['hysterese'])}   ·   Störung Spitze-Spitze ≈ {_u(2 * w['rs'])}"]
        if not e["erreicht"]:
            zeilen.append("⚠ Das Signal erreicht eine Schwelle nicht – der Ausgang schaltet nie um")
            return zeilen, WARN
        if e["wechsel"] > e["wechsel_soll"]:
            zeilen.append(f"❌ Flattern: {e['wechsel']} statt {e['wechsel_soll']} Umschaltungen – die Störung "
                          "ist grösser als die Hysterese")
            return zeilen, FEHLER
        zeilen.append(f"✓ Sauber: {e['wechsel']} Umschaltungen in 2 Perioden")
        return zeilen, OK


# =============================================================================
# INTEGRATOR UND DIFFERENZIERER
# =============================================================================
class IntegratorSchaltung(_MitDiagramm):
    TITEL = "🔌 Integrator und Differenzierer (interaktiv)"
    UNTERTITEL = "Rechteck wird zum Dreieck – und umgekehrt. Ideal oder mit Widerstand für die Praxis?"
    VARIANTEN = ["Integrator", "Differenzierer"]
    SCHALTER = [("praxis", "praxisgerecht (R_p ∥ C bzw. R_s vor C)")]
    # R_p (Integrator) und R_s (Differenzierer) haben eigene Regler: R_p ≫ R, aber R_s ≪ R
    REGLER = [("ue", "Eingang û", "spannung", 0.1, 5.0, 1.0, {"einheit": "V", "grenzen": (1e-3, 100)}),
              ("f", "Frequenz f", "frequenz", 10.0, 100e3, 1e3, {"einheit": "Hz", "log": True, "grenzen": (0.01, 1e8)}),
              ("r", "R", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("c", "C", "kapazitaet", 1e-9, 10e-6, 100e-9, {"einheit": "nF", "log": True, "grenzen": (1e-12, 1)}),
              ("rp", "R_p (Integrator)", "widerstand", 1e3, 10e6, 100e3, LOG_R),
              ("rs", "R_s (Differenzierer)", "widerstand", 10.0, 100e3, 1e3, LOG_R),
              ("off", "Offset am Eingang (Integrator)", "spannung", -0.2, 0.2, 0.0,
               {"einheit": "mV", "grenzen": (-10, 10)})]
    RASTER = (23.4, 10)
    RASTER_SCHMAL = (11.8, 10)
    SEITENVERHAELTNIS = 0.5
    U_B = 12.0
    ERKLAERUNG = (
        "Was zeigt die Grafik?  INTEGRATOR: Der Eingangsstrom Ue/R lädt C, weil der − Eingang virtuelle Masse ist: "
        "Ua = −1/(R·C) · ∫Ue dt – konstante Eingangsspannung ergibt eine Rampe, ein Rechteck ein Dreieck. Jeder "
        "kleine Offset wird aber ebenfalls integriert: Der ideale Integrator läuft langsam in die Begrenzung "
        "(Offset-Regler!). R_p parallel zu C begrenzt die Gleichspannungsverstärkung auf −R_p/R. "
        "DIFFERENZIERER: Ua = −R·C · dUe/dt – ein Dreieck wird zum Rechteck. Weil die Verstärkung mit der Frequenz "
        "steigt, verstärkt er Rauschen und neigt zum Schwingen; R_s vor C begrenzt sie auf −R/R_s und rundet die "
        "Flanken ab. Modell: ±12 V, klassischer OPV.")

    def sk_rechnen(self, w, v):
        if v == "Integrator":
            e = om.integrator_sim(w["r"], w["c"], w["ue"], w["f"], self.U_B, w["rp"] if w["praxis"] else None, w["off"])
            e["k"] = om.integrator_kennwerte(w["r"], w["c"], w["ue"], w["f"], w["rp"] if w["praxis"] else None)
        else:
            e = om.differenzierer_sim(w["r"], w["c"], w["ue"], w["f"], self.U_B, w["rs"] if w["praxis"] else None)
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_n, x_o, x_a, y_o, y_u = 2.0, 5.4, 7.6, 9.6, 5.6, 9.0
        y_c, y_p = 3.0, 1.7                                   # Höhe von C (bzw. R) und R_p
        pins = p.opv(x_o, y_o)
        y_m = pins["minus"][1]
        p.leitung(pins["aus"], (x_a, y_o), (x_a + 0.9, y_o))
        p.knoten(x_a, y_o)
        p.anschluss(x_a + 0.9, y_o, "u_a")
        p.wechselquelle(x_q, y_m + 1.2, y_u - 0.6, "u_e", "Rechteck" if v == "Integrator" else "Dreieck")
        p.leitung((x_q, y_m + 1.2), (x_q, y_m))
        p.leitung((x_q, y_u - 0.6), (x_q, y_u), (x_a + 0.9, y_u))
        p.anschluss(x_a + 0.9, y_u)
        p.leitung(pins["plus"], (6.0, pins["plus"][1]), (6.0, y_u))
        p.knoten(6.0, y_u)
        p.masse(4.0, y_u)
        p.leitung((x_n, y_m), pins["minus"])
        p.knoten(x_n, y_m)
        p.leitung((x_n, y_m), (x_n, y_c))
        p.leitung((x_a, y_c), (x_a, y_o))
        if v == "Integrator":
            p.widerstand(x_q, y_m, x_n, y_m, "R", _r(w["r"]))
            p.kondensator_waagrecht(x_n, x_a, y_c)
            p.text((x_n + x_a) / 2, y_c + 0.5, f"C  {fmt(w['c'], 'kapazitaet', 3)}", "n", klein=True)
            if w["praxis"]:
                p.leitung((x_n, y_c), (x_n, y_p))
                p.widerstand(x_n, y_p, x_a, y_p, "R_p", _r(w["rp"]))
                p.leitung((x_a, y_p), (x_a, y_c))
                p.knoten(x_n, y_c)
                p.knoten(x_a, y_c)
        else:
            if w["praxis"]:
                p.widerstand(x_q, y_m, 3.6, y_m, "R_s", _r(w["rs"]), laenge=1.0)
                p.kondensator_waagrecht(3.6, x_n, y_m, "C", fmt(w["c"], "kapazitaet", 3))
            else:
                p.kondensator_waagrecht(x_q, x_n, y_m, "C", fmt(w["c"], "kapazitaet", 3))
            p.widerstand(x_n, y_c, x_a, y_c, "R", _r(w["r"]))
        p.messpunkt(x_a, y_o, "M1", seite="rechts")
        if not getattr(self, "mit_diagramm", True):
            return
        werte = [abs(u) for _, u in e["kurve_aus"]] + [abs(u) for _, u in e["kurve_ein"]]
        g = max(max(werte), 1e-4) * 1.15
        p.diagramm(14.0, 1.4, 22.8, 8.6, [(e["kurve_ein"], p.leise, 1, True), (e["kurve_aus"], SPANNUNG, None, False)],
                   -g, g, "u_e (gestrichelt)  ·  u_a (blau)  ·  2 Perioden", _marken(e, g), einheit="spannung",
                   t_ende=2 / w["f"])

    def sk_info(self, w, e, v):
        if v == "Integrator":
            k = e["k"]
            zeilen = [f"Steigung dUa/dt = −Ue / (R·C) = {k['steigung']:.4g} V/s   ·   τ = R·C = {fmt(k['tau'], 'zeit', 3)}",
                      f"Dreieck Spitze-Spitze = Ue / (R·C) · T/2 = {_u(k['dreieck_ss'])}"]
            if w["praxis"]:
                zeilen.append(f"R_p: Gleichspannungsverstärkung {k['v_dc']:.3g}, integriert erst über "
                              f"f_u = 1/(2π·R_p·C) = {fmt(k['f_u'], 'frequenz', 3)}")
                if w["f"] < 3 * k["f_u"]:
                    zeilen.append("⚠ f liegt nicht deutlich über f_u – der Ausgang ist kein sauberes Dreieck mehr")
                    return zeilen, WARN
            if e["gesaettigt"]:
                zeilen.append("⚠ Ausgang in der Begrenzung – ohne R_p läuft schon ein kleiner Offset weg "
                              "(oder Dreieck grösser als die Versorgung)")
                return zeilen, WARN
            if not w["praxis"] and w["off"] != 0:
                zeilen.append("⚠ Offset wird mitintegriert: Das Dreieck wandert langsam weg → R_p einbauen")
                return zeilen, WARN
            return zeilen, OK
        zeilen = [f"Ua = −R·C · dUe/dt = ∓R·C · 4 · û · f = ∓{_u(e['u_a_ideal'])}   ·   "
                  f"|Vu| = 2π·f·R·C = 1 bei {fmt(1 / (6.283185307 * w['r'] * w['c']), 'frequenz', 3)}"]
        if e["f_s"] is not None:
            zeilen.append(f"R_s begrenzt die Verstärkung auf R/R_s = {w['r'] / w['rs']:.3g} oberhalb "
                          f"f = 1/(2π·R_s·C) = {fmt(e['f_s'], 'frequenz', 3)} – Flanken runden ab")
        else:
            zeilen.append("Ohne R_s steigt die Verstärkung mit der Frequenz unbegrenzt → Rauschen, Schwingneigung")
        if e["gesaettigt"]:
            zeilen.append("⚠ Ausgang wäre grösser als die Versorgung – wird begrenzt")
            return zeilen, WARN
        return zeilen, OK if e["f_s"] is not None else WARN
