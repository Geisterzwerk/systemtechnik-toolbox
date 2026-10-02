# =============================================================================
# schaltungen/grafiken_transistor.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE der Transistor- und MOSFET-Grundschaltungen.
# Spannung = blau, Strom = rot, Messpunkte = orange.
#
#   LastTreiberSchaltung     LED / Relais / Motor an einem µC-Pin, mit NPN oder N-MOSFET (Low-Side)
#   EmitterSchaltung         Spannungsverstärker: Arbeitspunkt, Verstärkung, Übersteuerung (+ Zeitdiagramm)
#   EmitterfolgerSchaltung   Impedanzwandler Ua = Ue − 0.7 V (+ Zeitdiagramm)
#   KonstantstromSchaltung   Transistor + Z-Diode oder JFET + R_S, Kennlinie I über R_Last
#
# Die Schalter-Simulatoren (NPN/PNP, N-/P-MOSFET) gibt es schon:
#   bauteile/grafiken/schalter_simulator.py  -> werden auf den Seiten per ID wiederverwendet.
#
# Rechnung: schaltungen/verstaerker_mathe.py, bauteile/rechner/transistor_mathe.py, mosfet_mathe.py
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_emitter")
# =============================================================================

import config                                                            # -> config.py
from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN       # -> bauteile/grafiken/schaltplan.py
from bauteile.rechner import mosfet_mathe as mm                          # -> bauteile/rechner/mosfet_mathe.py
from bauteile.rechner import normreihen                                  # -> bauteile/rechner/normreihen.py
from bauteile.rechner import transistor_mathe as tm                      # -> bauteile/rechner/transistor_mathe.py
from schaltungen import verstaerker_mathe as vm                          # -> schaltungen/verstaerker_mathe.py
from schaltungen.grafiken import _i, _r, _u                              # -> schaltungen/grafiken.py
from schaltungen.grafiken_dioden import FEHLER, _MitDiagramm, _p         # -> schaltungen/grafiken_dioden.py
from bauteile.grafiken.schaltplan import SchaltungsKarte                 # -> bauteile/grafiken/schaltplan.py

BETA = 200.0                 # Stromverstärkung für die Verstärkerschaltungen (typ. BC547B)
LOG_R = {"einheit": "kΩ", "log": True, "grenzen": (1.0, 100e6)}


# =============================================================================
# LASTEN AM µC ANSTEUERN
# =============================================================================
class LastTreiberSchaltung(SchaltungsKarte):
    TITEL = "🔌 Last am Mikrocontroller schalten (interaktiv)"
    UNTERTITEL = "LED, Relais oder Motor – mit NPN-Transistor oder N-MOSFET auf der Low-Side"
    VARIANTEN = ["LED", "Relais", "Motor"]
    SCHALTER = [("mosfet", "N-MOSFET statt NPN")]
    REGLER = [("ub", "Versorgung U_B", "spannung", 3.0, 30.0, 12.0, {"einheit": "V", "grenzen": (1.0, 100)}),
              ("i", "Laststrom (Nenn)", "strom", 1e-3, 3.0, 0.1, {"einheit": "mA", "log": True, "grenzen": (1e-5, 50)}),
              ("ust", "Pin-Spannung (HIGH)", "spannung", 1.8, 5.0, 3.3, {"einheit": "V", "grenzen": (0.5, 15)})]
    RASTER = (15, 9.6)
    SEITENVERHAELTNIS = 0.62
    B_MIN, UE = 100.0, 3.0                 # NPN: B min aus dem Datenblatt, Übersteuerung
    U_F_LED = 2.0                          # rote LED
    ANLAUF = 5.0                           # Motor: Anlaufstrom ≈ 5 × Nennstrom
    MOS = {"u_th": 1.0, "rds": 0.045, "u_spec": 4.5}      # Logic-Level-MOSFET (z.B. IRLML2502)
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Ein µC-Pin liefert nur wenige mA – der Transistor schaltet den grossen Laststrom "
        "auf der Low-Side (zwischen Last und GND). Der NPN braucht Basisstrom: I_B = ü · I_C / B, mit "
        "Übersteuerung ü ≈ 3, damit er sicher sättigt. Der MOSFET braucht im Betrieb keinen Strom, aber eine "
        "ausreichende Gate-Spannung: Bei 3.3 V nur ein Logic-Level-Typ. Induktive Lasten (Relais, Motor) brauchen "
        "eine Freilaufdiode, Motoren ziehen beim Anlaufen ein Vielfaches des Nennstroms, LEDs einen Vorwiderstand.")

    def sk_rechnen(self, w, v):
        ub, i, ust = w["ub"], w["i"], w["ust"]
        e = {"v": v}
        if v == "LED":
            if ub <= self.U_F_LED + 0.3:
                raise ValueError(f"U_B muss über U_F der LED ({self.U_F_LED:g} V) + Schalter liegen")
            r_v = normreihen.naechste_werte((ub - self.U_F_LED - tm.U_CE_SAT) / i, "E12")[1]
            e["r_v"] = r_v
            r_last = r_v                                          # LED als Spannungsquelle U_F + R_V
            u_quelle = ub - self.U_F_LED
        else:
            r_last, u_quelle = ub / i, ub
        i_auslegung = i * (self.ANLAUF if v == "Motor" else 1.0)
        e.update(r_last=r_last, i_auslegung=i_auslegung)
        if w["mosfet"]:
            m = mm.schalter("N", u_quelle, r_last, ust, self.MOS["u_th"], self.MOS["rds"], self.MOS["u_spec"])
            e.update(art="MOSFET", i=m["i"], zustand=m["zustand"], p_t=m["p_t"], r_on=m["r_on"], u_t=m["u_ds"],
                     r_g=100.0, i_pin=0.0)
            if v == "Motor" and m["r_on"]:
                e["p_anlauf"] = i_auslegung ** 2 * m["r_on"]
        else:
            d = tm.schalter_dimensionieren(ub, ust, self.B_MIN, self.UE, i_last=i_auslegung)
            i_ist = (u_quelle - tm.U_CE_SAT) / r_last
            e.update(art="NPN", i=i_ist, zustand="voll", p_t=tm.U_CE_SAT * i_ist + tm.U_BE * d["i_b_echt"],
                     r_b=d["r_b_norm"], i_pin=d["i_b_echt"], u_t=tm.U_CE_SAT)
        return e

    def sk_zeichnen(self, p, w, e, v):
        x, y_o, y_k, y_t, x_f = 7.4, 1.2, 5.0, 6.5, 9.6
        p.versorgung(x, y_o, f"+U_B = {_u(w['ub'])}")
        if v == "LED":
            p.widerstand(x, y_o, x, 3.0, "R_V", _r(e["r_v"]))
            p.diode(x, 3.0, x, y_k, "LED", f"{self.U_F_LED:g} V")
        else:
            if v == "Relais":
                p.widerstand(x, y_o, x, y_k, "K1", _r(e["r_last"]), seite="links", laenge=1.8)
            else:
                p.motor(x, y_o, y_k, "Motor", _r(e["r_last"]), seite="links")
            ya = y_o + 0.5
            p.knoten(x, ya)
            p.knoten(x, y_k - 0.2)
            p.leitung((x, ya), (x_f, ya))
            p.leitung((x, y_k - 0.2), (x_f, y_k - 0.2))
            p.diode(x_f, y_k - 0.2, x_f, ya, "D", "Freilauf")
        p.leitung((x, y_k), (x, y_t - 1.0))
        if w["mosfet"]:
            p.nmosfet(x, y_t, "T1")
            r_text, r_wert = "R_G", _r(e["r_g"])
            p.knoten(4.2, y_t)
            p.widerstand(4.2, y_t, 4.2, 9.0, "100 kΩ", "", seite="rechts", laenge=1.0)
        else:
            p.npn(x, y_t, "T1")
            r_text, r_wert = "R_B", _r(e["r_b"])
        p.masse(x, y_t + 1.0)
        if w["mosfet"]:
            p.masse(4.2, 9.0)
        p.leitung((x - 0.9, y_t), (5.4, y_t))
        p.widerstand(5.4, y_t, 2.0, y_t, r_text, r_wert)
        p.anschluss(2.0, y_t, "")
        p.text(2.0, y_t + 0.45, "µC-Pin", "n", klein=True)
        p.text(x + 0.35, y_k + 0.1, f"I = {_i(e['i'])}", "w", fett=True, farbe=STROM)
        p.messpunkt(x, y_k, "M1", seite="links")

    def sk_info(self, w, e, v):
        zeilen = [f"Laststrom {_i(e['i'])}   ·   am Schalter {_u(e['u_t'])}   ·   Verlust im Transistor {_p(e['p_t'])}"]
        farbe = OK
        if e["art"] == "NPN":
            ausgelegt = "Anlaufstrom" if v == "Motor" else "Laststrom"
            zeilen.append(f"R_B = {_r(e['r_b'])} (E12, ü = 3 auf {ausgelegt} {_i(e['i_auslegung'])})   ·   "
                          f"Pin liefert {_i(e['i_pin'])}")
            if e["i_pin"] > 10e-3:
                zeilen.append("⚠ Mehr als 10 mA aus dem Pin – Darlington, ULN2003 oder Logic-Level-MOSFET verwenden")
                farbe = WARN
        else:
            zeilen.append(f"MOSFET bei U_GS = {_u(w['ust'])}: R_DS(on) ≈ {_r(e['r_on']) if e['r_on'] else '–'}   ·   "
                          "Gate: 100 Ω in Reihe, 100 kΩ nach GND (definiert AUS beim Reset)")
            if e["zustand"] != "voll":
                zeilen.append("❌ Gate-Spannung reicht nicht – MOSFET arbeitet im linearen Bereich und wird heiss "
                              "→ Logic-Level-Typ mit kleinerem U_th oder Gate-Treiber")
                farbe = FEHLER
            if v == "Motor" and e.get("p_anlauf"):
                zeilen.append(f"Beim Anlaufen ({_i(e['i_auslegung'])}): {_p(e['p_anlauf'])} im MOSFET")
        if v != "LED":
            zeilen.append("Freilaufdiode antiparallel zur Last: begrenzt die Abschaltspitze auf U_B + 0.7 V")
        return zeilen, farbe


# =============================================================================
# EMITTERSCHALTUNG
# =============================================================================
class EmitterSchaltung(_MitDiagramm):
    TITEL = "🔌 Emitterschaltung als Verstärker (interaktiv)"
    UNTERTITEL = "Arbeitspunkt einstellen, C_E zuschalten, Eingang aufdrehen – bis das Signal abgeschnitten wird"
    SCHALTER = [("ce", "C_E überbrückt R_E")]
    REGLER = [("ub", "Versorgung U_B", "spannung", 5.0, 30.0, 12.0, {"einheit": "V", "grenzen": (1.0, 100)}),
              ("r1", "R1 (Basis oben)", "widerstand", 1e3, 1e6, 47e3, LOG_R),
              ("r2", "R2 (Basis unten)", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("rc", "R_C", "widerstand", 100.0, 100e3, 2.2e3, LOG_R),
              ("re", "R_E", "widerstand", 10.0, 10e3, 1e3, {"einheit": "Ω", "log": True, "grenzen": (1.0, 1e6)}),
              ("uh", "Eingang û_e", "spannung", 1e-3, 2.0, 20e-3, {"einheit": "mV", "log": True, "grenzen": (1e-6, 20)})]
    RASTER = (23.4, 10)
    RASTER_SCHMAL = (13.4, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der Basisteiler R1/R2 stellt einen Ruhestrom ein, R_C setzt ihn in eine Spannung um: "
        "Der Kollektor sollte in Ruhe etwa in der Mitte zwischen U_E und U_B liegen, damit das Signal nach oben und "
        "unten Platz hat. Eine kleine Eingangsspannung ändert I_C – am Kollektor entsteht eine grosse, UMGEKEHRTE "
        "Spannung (Phasendrehung 180°). Ohne C_E ist die Verstärkung ≈ R_C / R_E (klein, aber stabil). Mit C_E "
        "wird R_E für Wechselstrom überbrückt: Vu ≈ R_C / r_e mit r_e = 26 mV / I_E – viel grösser, aber abhängig "
        "von Temperatur und Strom. Ist der Ausgang zu gross, wird er oben (Transistor sperrt) oder unten "
        "(Transistor sättigt) abgeschnitten. Modell: β = 200, Koppelkondensatoren gross.")

    def sk_rechnen(self, w, v):
        return vm.emitterschaltung(w["ub"], w["r1"], w["r2"], w["rc"], w["re"], BETA, c_e=w["ce"], u_hat=w["uh"])

    def sk_zeichnen(self, p, w, e, v):
        x_t, x_b, y_o, y_b, y_u = 8.4, 4.4, 1.2, 5.0, 9.0
        p.versorgung(6.4, y_o, f"+U_B = {_u(w['ub'])}")
        p.leitung((x_b, y_o), (x_t, y_o))
        p.knoten(6.4, y_o)
        p.widerstand(x_b, y_o, x_b, y_b, "R1", _r(w["r1"]), seite="links")
        p.widerstand(x_b, y_b, x_b, y_u, "R2", _r(w["r2"]), seite="links")
        p.widerstand(x_t, y_o, x_t, y_b - 1.0, "R_C", _r(w["rc"]))
        p.npn(x_t, y_b)
        p.leitung((x_b, y_b), (x_t - 0.9, y_b))
        p.knoten(x_b, y_b)
        p.widerstand(x_t, y_b + 1.0, x_t, y_u, "R_E", _r(w["re"]), seite="links")
        if w["ce"]:
            p.knoten(x_t, y_b + 1.4)
            p.leitung((x_t, y_b + 1.4), (x_t + 1.6, y_b + 1.4))
            p.kondensator(x_t + 1.6, y_b + 1.4, y_u, "C_E", "")
            p.knoten(x_t, y_u)
        p.leitung((x_b, y_u), (x_t + (1.6 if w["ce"] else 0), y_u))
        p.knoten(x_b, y_u)
        p.masse(6.4, y_u)
        # Eingang
        p.wechselquelle(1.8, 6.2, y_u, "u_e", _u(w["uh"]))
        p.leitung((1.8, 6.2), (1.8, y_b), (2.0, y_b))
        p.kondensator_waagrecht(2.0, 3.4, y_b, "C_K", "")
        p.leitung((3.4, y_b), (x_b, y_b))
        p.leitung((1.8, y_u), (x_b, y_u))
        # Ausgang
        y_c = y_b - 1.0
        p.knoten(x_t, y_c)
        p.leitung((x_t, y_c), (x_t + 0.8, y_c))
        p.kondensator_waagrecht(x_t + 0.8, x_t + 2.2, y_c)                 # Koppelkondensator Ausgang
        p.anschluss(x_t + 2.7, y_c, "u_a")
        p.leitung((x_t + 2.2, y_c), (x_t + 2.7, y_c))
        p.messpunkt(x_t, y_c, "M1", seite="links")
        if e["zustand"] == "aktiv":
            p.text(x_t + 0.35, y_c + 0.55, f"U_C = {_u(e['u_c'])}", "w", klein=True, farbe=SPANNUNG)
            p.text(x_t + 0.35, y_b + 1.25, f"U_E = {_u(e['u_e'])}", "w", klein=True, farbe=SPANNUNG)
            p.text(x_t - 0.25, y_o + 0.55, f"I_C = {_i(e['i_c'])}", "e", klein=True, farbe=STROM)
            if getattr(self, "mit_diagramm", True):
                # auf das SIGNAL skalieren; die Aussteuergrenzen nur zeigen, wenn sie im Bild liegen
                g = max(abs(e["vu"]) * w["uh"] * 1.25, 1e-3)
                marken = [(m, t) for m, t in ((e["oben"], f"+{_u(e['oben'])}"), (e["unten"], _u(e["unten"])))
                          if abs(m) <= g]
                p.diagramm(14.8, 1.6, 22.8, 8.6, [(e["kurve_ideal"], p.leise, 1, True),
                                                   (e["kurve_aus"], SPANNUNG, None, False)],
                           -g, g, "u_a ideal (gestrichelt)  ·  tatsächlich (blau)", marken, einheit="spannung")

    def sk_info(self, w, e, v):
        if e["zustand"] == "sperrt":
            return [f"U_Basis = {_u(e['u_th'])} < 0.7 V → Transistor SPERRT, kein Arbeitspunkt (R2 grösser oder R1 kleiner)"], WARN
        if e["zustand"] == "gesättigt":
            return ["Transistor GESÄTTIGT: U_CE < 0.3 V – der Kollektor kann nicht weiter nach unten "
                    "→ R_C oder Basisspannung verkleinern"], WARN
        zeilen = [f"Arbeitspunkt: I_C = {_i(e['i_c'])}, U_CE = {_u(e['u_ce'])}, U_C = {_u(e['u_c'])}   "
                  f"(Platz nach oben {_u(e['oben'])}, nach unten {_u(-e['unten'])})",
                  f"Vu = {e['vu']:.1f}  (r_e = {_r(e['r_e_diff'])})   ·   û_a = {_u(e['u_a_hat'])}   ·   "
                  f"r_ein ≈ {_r(e['r_ein'])}   ·   r_aus ≈ R_C"]
        if e["uebersteuert"]:
            zeilen.append("⚠ Übersteuert: Der Ausgang wird abgeschnitten (Verzerrungen) → Eingang kleiner oder "
                          "Arbeitspunkt in die Mitte legen")
            return zeilen, WARN
        if e["i_quer"] < 10 * e["i_b"]:
            zeilen.append("⚠ Teilerstrom < 10 · I_B – der Arbeitspunkt hängt stark von β ab")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# EMITTERFOLGER
# =============================================================================
class EmitterfolgerSchaltung(_MitDiagramm):
    TITEL = "🔌 Emitterfolger / Kollektorschaltung (interaktiv)"
    UNTERTITEL = "Spannung bleibt (fast) gleich, der Strom wird verstärkt – ein Impedanzwandler"
    SCHALTER = [("last", "Last R_L angeschlossen")]
    REGLER = [("ub", "Versorgung U_B", "spannung", 5.0, 30.0, 12.0, {"einheit": "V", "grenzen": (1.0, 100)}),
              ("ue", "Eingang Gleichanteil", "spannung", 0.0, 20.0, 6.0, {"einheit": "V", "grenzen": (0.0, 100)}),
              ("uh", "Eingang û (Wechselanteil)", "spannung", 0.0, 10.0, 2.0, {"einheit": "V", "grenzen": (0.0, 100)}),
              ("re", "R_E", "widerstand", 100.0, 100e3, 1e3, LOG_R),
              ("rl", "Last R_L", "widerstand", 10.0, 1e6, 470.0, {"einheit": "Ω", "log": True, "grenzen": (1.0, 1e8)})]
    RASTER = (22.4, 9.6)
    RASTER_SCHMAL = (12.8, 9.6)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der Emitter „folgt“ der Basis mit 0.7 V Abstand: Ua = Ue − 0.7 V, die Verstärkung "
        "ist ≈ 1 und nicht invertierend. Dafür liefert der Ausgang (β + 1)-mal mehr Strom, als in die Basis hinein "
        "fliesst: Der Eingang ist hochohmig (≈ β · R_E), der Ausgang niederohmig (≈ r_e). So kann eine schwache "
        "Quelle (Spannungsteiler, Sensor) eine Last treiben. Der Ausgang kann nur Strom LIEFERN – fällt Ue unter "
        "0.7 V, sperrt der Transistor und der Ausgang bleibt bei 0 V stehen (abgeschnitten).")

    def sk_rechnen(self, w, v):
        return vm.emitterfolger(w["ub"], w["ue"], w["re"], w["rl"] if w["last"] else None, BETA, u_hat=w["uh"])

    def sk_zeichnen(self, p, w, e, v):
        x, y_o, y_b, y_u, x_l = 7.0, 1.2, 4.2, 8.6, 9.8
        p.versorgung(x, y_o, f"+U_B = {_u(w['ub'])}")
        p.leitung((x, y_o), (x, y_b - 1.0))
        p.npn(x, y_b)
        p.leitung((x - 0.9, y_b), (2.0, y_b), (2.0, 5.0))
        p.quelle(2.0, 5.0, y_u, "u_e", f"{_u(w['ue'])} ± {_u(w['uh'])}", seite="rechts")
        y_e = y_b + 1.0
        p.knoten(x, y_e)
        p.widerstand(x, y_e, x, y_u, "R_E", _r(w["re"]), seite="rechts")
        p.leitung((x, y_e), (x_l, y_e))
        if w["last"]:
            p.widerstand(x_l, y_e, x_l, y_u, "R_L", _r(w["rl"]))
            p.knoten(x, y_u)
        else:
            p.anschluss(x_l, y_e)
            p.anschluss(x_l, y_u)
        p.leitung((2.0, y_u), (x_l, y_u))
        p.masse(4.5, y_u)
        p.text(x + 0.35, y_e + 0.45, f"U_a = {_u(e['u_a'])}", "w", fett=True, farbe=SPANNUNG)
        p.text(x - 1.2, y_b - 0.45, f"I_B = {_i(e['i_b'])}", "e", klein=True, farbe=STROM)
        p.text(x + 0.3, y_o + 1.0, f"I_E = {_i(e['i_e'])}", "w", klein=True, farbe=STROM)
        p.messpunkt(x, y_e, "M1", seite="links")
        if getattr(self, "mit_diagramm", True):
            g = max(w["ue"] + w["uh"], w["ub"] * 0.3, 1.0) * 1.12
            p.diagramm(14.0, 1.6, 21.8, 8.2, [(e["kurve_ein"], p.leise, 1, True), (e["kurve_aus"], SPANNUNG, None, False)],
                       0.0, g, "u_e (gestrichelt)  ·  u_a (blau)", [(w["ub"] - 0.2, "U_B")] if g > w["ub"] else [],
                       einheit="spannung")

    def sk_info(self, w, e, v):
        if not e["leitet"]:
            return ["Ue < 0.7 V: Transistor sperrt, Ausgang 0 V"], WARN
        zeilen = [f"Ua = Ue − 0.7 V = {_u(e['u_a'])}   ·   I_E = {_i(e['i_e'])}, aus der Quelle nur I_B = {_i(e['i_b'])}",
                  f"Vu = {e['vu']:.3f}   ·   r_ein ≈ {_r(e['r_ein'])}   ·   r_aus ≈ {_r(e['r_aus'])}   ·   "
                  f"Verlust im Transistor {_p(e['p_t'])}"]
        if e["abgeschnitten"]:
            zeilen.append("⚠ Ausgang wird abgeschnitten: unten bei 0 V (Transistor sperrt) oder oben bei U_B "
                          "→ Gleichanteil in die Mitte legen oder û verkleinern")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# KONSTANTSTROMQUELLE
# =============================================================================
class KonstantstromSchaltung(_MitDiagramm):
    TITEL = "🔌 Konstantstromquelle (interaktiv)"
    UNTERTITEL = "Der Strom bleibt gleich, egal wie gross die Last ist – bis die Spannung nicht mehr reicht"
    VARIANTEN = ["Transistor + Z-Diode", "JFET + R_S"]
    REGLER = [("ub", "Versorgung U_B", "spannung", 5.0, 30.0, 12.0, {"einheit": "V", "grenzen": (1.0, 100)}),
              ("rl", "Last R_L", "widerstand", 1.0, 10e3, 100.0, {"einheit": "Ω", "log": True, "grenzen": (0.01, 1e7)}),
              ("re", "R_E bzw. R_S", "widerstand", 10.0, 10e3, 220.0, {"einheit": "Ω", "log": True, "grenzen": (1.0, 1e6)}),
              ("uz", "Z-Spannung U_Z", "spannung", 1.4, 10.0, 3.3, {"einheit": "V", "grenzen": (0.8, 50)})]
    RASTER = (22.4, 9.6)
    RASTER_SCHMAL = (12.4, 9.6)
    SEITENVERHAELTNIS = 0.5
    I_DSS, U_P = 10e-3, 2.5             # JFET-Kennwerte (typ. J113-Klasse, Datenblatt streut stark!)
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Transistor-Variante: Die Z-Diode hält die Basis fest, am Emitter-Widerstand liegt "
        "darum immer U_Z − 0.7 V – also fliesst I = (U_Z − 0.7 V) / R_E, egal was im Kollektorkreis hängt. "
        "JFET-Variante: Gate an GND, der Strom durch R_S macht das Gate negativ und schnürt den Kanal genau so weit "
        "ab, dass sich ein fester Strom einstellt (nur 2 Anschlüsse nötig). Rechts die Kennlinie: Bis zum "
        "Knick ist der Strom konstant; danach reicht U_B nicht mehr (Transistor sättigt) und der Strom fällt.")

    def _rechnen(self, w, v, r_last):
        if v == self.VARIANTEN[0]:
            return vm.konstantstrom_bjt(w["ub"], w["uz"], w["re"], r_last)
        return vm.konstantstrom_jfet(w["ub"], self.I_DSS, self.U_P, w["re"], r_last)

    def sk_rechnen(self, w, v):
        e = self._rechnen(w, v, w["rl"])
        r_achse = max(2.2 * e["r_last_max"], 1.3 * w["rl"], 1.0)
        e["kurve"] = [(k / 80, self._rechnen(w, v, r_achse * k / 80)["i"]) for k in range(81)]
        e["r_achse"] = r_achse
        return e

    def sk_zeichnen(self, p, w, e, v):
        x, y_o, y_t, y_u = 7.4, 1.2, 5.2, 8.8
        p.versorgung(x, y_o, f"+U_B = {_u(w['ub'])}")
        p.widerstand(x, y_o, x, y_t - 1.0, "R_L (Last)", _r(w["rl"]))
        if v == self.VARIANTEN[0]:
            p.npn(x, y_t, "T1")
            xb = 3.6
            p.leitung((x, y_o), (xb, y_o))
            p.knoten(x, y_o)
            p.widerstand(xb, y_o, xb, y_t, "R_Z", "4.7 kΩ", seite="links")
            p.diode(xb, y_u, xb, y_t, "Z", _u(w["uz"]), art="z", seite="links")
            p.leitung((xb, y_t), (x - 0.9, y_t))
            p.knoten(xb, y_t)
            p.widerstand(x, y_t + 1.0, x, y_u, "R_E", _r(w["re"]))
            p.leitung((xb, y_u), (x, y_u))
            p.knoten(x, y_u)
        else:
            p.njfet(x, y_t, "J1")
            p.leitung((x - 0.9, y_t), (5.0, y_t), (5.0, y_u))
            p.text(4.8, y_t + 0.9, f"I_DSS {_i(self.I_DSS)}", "e", klein=True, farbe=p.leise)
            p.text(4.8, y_t + 1.4, f"U_P −{self.U_P:g} V", "e", klein=True, farbe=p.leise)
            p.widerstand(x, y_t + 1.0, x, y_u, "R_S", _r(w["re"]))
            p.leitung((5.0, y_u), (x, y_u))
            p.knoten(5.0, y_u)
        p.masse(6.2, y_u)
        farbe = STROM if e["regelt"] else FEHLER[1]
        p.text(x + 0.35, y_t - 1.0 + 0.1, f"I = {_i(e['i'])}", "w", fett=True, farbe=farbe)
        p.messpunkt(x, y_t - 1.0, "M1", seite="links")
        if getattr(self, "mit_diagramm", True):
            i_max = max(i for _, i in e["kurve"]) * 1.15 or 1e-3
            gx0, gy0, gx1, gy1 = 14.2, 1.6, 21.8, 8.2
            p.diagramm(gx0, gy0, gx1, gy1, [(e["kurve"], SPANNUNG, None, False)],
                       0.0, i_max, "Strom über R_Last  ·  roter Punkt = jetzt",
                       [(e["i_soll"], _i(e["i_soll"]))], einheit="strom", zeit_text=f"R_L (0 … {_r(e['r_achse'])})")
            px, py = p.p(gx0 + w["rl"] / e["r_achse"] * (gx1 - gx0), gy1 - e["i"] / i_max * (gy1 - gy0))
            r = max(4, p.u * 0.14)
            p.c.create_oval(px - r, py - r, px + r, py + r, fill=STROM, outline="")

    def sk_info(self, w, e, v):
        zeilen = [f"I = {_i(e['i'])}   (Sollwert {_i(e['i_soll'])})   ·   Spannung an der Last {_u(e['u_last'])}",
                  f"Konstant bis R_L ≈ {_r(e['r_last_max'])}  (Lastspannung max. {_u(e['u_last_max'])})"]
        if v == self.VARIANTEN[0]:
            zeilen.append(f"I = (U_Z − 0.7 V) / R_E   ·   Verlust im Transistor {_p(e['p_t'])}")
        else:
            zeilen.append(f"U_GS stellt sich auf {_u(e['u_gs'])} ein   ·   R_S = 0 → I = I_DSS (grösster Strom)")
        if not e["regelt"]:
            zeilen.append("⚠ Last zu gross: Die Spannung reicht nicht mehr, der Strom ist nicht mehr konstant")
            return zeilen, WARN
        return zeilen, OK
