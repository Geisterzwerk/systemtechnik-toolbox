# =============================================================================
# schaltungen/grafiken_rc.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE der RC-Schaltungen.
# Spannung = blau, Strom = rot, Messpunkte = orange.
#
#   RcFilterSchaltung       Tief-/Hochpass: Betragsgang (Bode) + Sinus am Ein- und Ausgang
#   EntprellSchaltung       Taster mit Pull-up, RC und Schmitt-Trigger, Prellen im Zeitdiagramm
#   AntiAliasingSchaltung   RC-Tiefpass vor dem ADC: Abtastpunkte und Alias-Signal
#
# Laden/Entladen und RL ein/aus gibt es schon als Lernansicht:
#   bauteile/grafiken/kurven.py ("rc_ladekurve", "rl_kurve") -> werden auf den Seiten per ID wiederverwendet.
#
# Rechnung: schaltungen/rc_mathe.py
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_rc_filter")
# =============================================================================

import math

from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN       # -> bauteile/grafiken/schaltplan.py
from schaltungen import rc_mathe as rm                                   # -> schaltungen/rc_mathe.py
from schaltungen.grafiken import _i, _r, _u                              # -> schaltungen/grafiken.py
from schaltungen.grafiken_dioden import FEHLER, _MitDiagramm             # -> schaltungen/grafiken_dioden.py

LOG_R = {"einheit": "kΩ", "log": True, "grenzen": (1.0, 100e6)}
LOG_C = {"einheit": "nF", "log": True, "grenzen": (1e-12, 1.0)}
LOG_F = {"einheit": "Hz", "log": True, "grenzen": (1e-3, 1e9)}


def _f(wert):
    return fmt(wert, "frequenz", 3)


def _t(wert):
    return fmt(wert, "zeit", 3)


def _punkt(p, x0, y0, x1, y1, t, wert, y_min, y_max, farbe=STROM):
    """Ausgefüllter Punkt in einem Diagramm (t 0 … 1, wert wie die Kurven)."""
    anteil = min(max((wert - y_min) / (y_max - y_min), 0.0), 1.0)
    px, py = p.p(x0 + t * (x1 - x0), y1 - anteil * (y1 - y0))
    r = max(3, p.u * 0.12)
    p.c.create_oval(px - r, py - r, px + r, py + r, fill=farbe, outline="")


# =============================================================================
# TIEF- UND HOCHPASS
# =============================================================================
class RcFilterSchaltung(_MitDiagramm):
    TITEL = "🔌 RC-Tiefpass und -Hochpass (interaktiv)"
    UNTERTITEL = "Frequenz verschieben: Wie viel kommt am Ausgang an, und wie stark verschiebt sich die Phase?"
    VARIANTEN = rm.FILTER_ARTEN
    REGLER = [("r", "Widerstand R", "widerstand", 100.0, 1e6, 10e3, LOG_R),
              ("c", "Kapazität C", "kapazitaet", 1e-9, 100e-6, 100e-9, LOG_C),
              ("f", "Signalfrequenz f", "frequenz", 1.0, 1e6, 1e3, LOG_F),
              ("ue", "Eingang û_e", "spannung", 0.1, 20.0, 1.0, {"einheit": "V", "grenzen": (1e-3, 1000)})]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (11.2, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  R und C bilden einen frequenzabhängigen Spannungsteiler: Der Blindwiderstand "
        "Xc = 1 / (2π · f · C) wird mit steigender Frequenz kleiner. Beim TIEFPASS liegt der Ausgang am C – tiefe "
        "Frequenzen kommen durch, hohe werden mit −20 dB pro Dekade gedämpft. Beim HOCHPASS liegt der Ausgang am R – "
        "umgekehrt. Bei der Grenzfrequenz fg = 1 / (2π · R · C) ist Xc = R: Der Ausgang hat 70.7 % (−3 dB) und ist "
        "um 45° verschoben. Oben der Betragsgang über der Frequenz (roter Punkt = eingestellte Frequenz), unten "
        "Eingang (gestrichelt) und Ausgang (blau) über der Zeit. Modell: Quelle ideal, Ausgang unbelastet.")

    def sk_rechnen(self, w, v):
        e = rm.rc_glied(v, w["r"], w["c"], w["f"])
        e["u_a"] = e["betrag"] * w["ue"]
        phi = math.radians(e["phase"])
        e["kurve_ein"] = [(k / 160, w["ue"] * math.sin(4 * math.pi * k / 160)) for k in range(161)]
        e["kurve_aus"] = [(k / 160, e["u_a"] * math.sin(4 * math.pi * k / 160 + phi)) for k in range(161)]
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_k, x_a, y_o, y_u = 2.6, 6.4, 9.4, 2.0, 8.4
        p.wechselquelle(x_q, y_o + 1.6, y_u - 1.6, "u_e", f"û = {_u(w['ue'])}")
        p.leitung((x_q, y_o + 1.6), (x_q, y_o))
        p.leitung((x_q, y_u - 1.6), (x_q, y_u), (x_a, y_u))
        if v == "Tiefpass":
            p.widerstand(x_q, y_o, x_k, y_o, "R", _r(w["r"]))
            p.kondensator(x_k, y_o, y_u, "C", f"Xc = {_r(e['x_c'])}", seite="links")
        else:
            p.kondensator_waagrecht(x_q, x_k, y_o, "C", f"Xc = {_r(e['x_c'])}")
            p.widerstand(x_k, y_o, x_k, y_u, "R", _r(w["r"]), seite="links")
        p.knoten(x_k, y_o)
        p.knoten(x_k, y_u)
        p.leitung((x_k, y_o), (x_a, y_o))
        p.anschluss(x_a, y_o)
        p.anschluss(x_a, y_u)
        p.spannung(x_a, y_o + 0.5, y_u - 0.5, f"û_a = {_u(e['u_a'])}")
        p.messpunkt(x_k, y_o, "M1", seite="rechts")
        p.text(x_q - 0.4, y_u + 0.9, f"fg = {_f(e['fg'])}   ·   f = {_f(w['f'])}", "w", fett=True)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 13.6, 22.8
        # ---- Betragsgang: x = fg / 100 … fg · 100 (logarithmisch) ----
        p.diagramm(gx0, 1.0, gx1, 4.4, [(rm.bode_kurve(v), SPANNUNG, None, False)], -45.0, 5.0,
                   "|H| in dB über f (log)", [(0.0, "0 dB"), (-3.0, "−3 dB"), (-20.0, "−20 dB"), (-40.0, "−40 dB")],
                   zeit_text="")
        p.text((gx0 + gx1) / 2, 4.65, "fg/100   ·   fg/10   ·   fg   ·   10·fg   ·   100·fg", "n", klein=True, farbe=p.leise)
        _punkt(p, gx0, 1.0, gx1, 4.4, rm.bode_position(w["f"], e["fg"]), max(e["db"], -45.0), -45.0, 5.0)
        # ---- Zeitbereich: zwei Perioden bei f ----
        g = w["ue"] * 1.15
        p.diagramm(gx0, 5.8, gx1, 9.4, [(e["kurve_ein"], p.leise, 1, True), (e["kurve_aus"], SPANNUNG, None, False)],
                   -g, g, "u_e (gestrichelt)  ·  u_a (blau)  ·  2 Perioden", zeit_text="t")

    def sk_info(self, w, e, v):
        zeilen = [f"fg = 1 / (2π · R · C) = {_f(e['fg'])}   ·   τ = R · C = {_t(e['tau'])}",
                  f"Bei f = {_f(w['f'])}:  Xc = {_r(e['x_c'])}   ·   |H| = {e['betrag']:.3f} ({e['db']:.1f} dB)   ·   "
                  f"û_a = {_u(e['u_a'])}   ·   φ = {e['phase']:+.1f}°"]
        if v == "Tiefpass":
            zeilen.append("Ausgang eilt dem Eingang NACH (φ < 0) – über fg sinkt der Ausgang auf 1/10 pro Dekade")
        else:
            zeilen.append("Ausgang eilt dem Eingang VOR (φ > 0) – Gleichspannung wird ganz gesperrt (Koppelkondensator)")
        return zeilen, OK


# =============================================================================
# TASTER ENTPRELLEN
# =============================================================================
class EntprellSchaltung(_MitDiagramm):
    TITEL = "🔌 Taster entprellen mit RC und Schmitt-Trigger (interaktiv)"
    UNTERTITEL = "Ein mechanischer Kontakt prellt – wie viele Tastendrücke erkennt der Eingang?"
    VARIANTEN = ["ohne Entprellung", "RC + Schmitt-Trigger"]
    REGLER = [("ub", "Versorgung U_B", "spannung", 3.3, 5.0, 5.0, {"einheit": "V", "grenzen": (1.0, 30)}),
              ("r1", "Pull-up R1", "widerstand", 1e3, 100e3, 10e3, LOG_R),
              ("r2", "R2 (zum C)", "widerstand", 100.0, 100e3, 4.7e3, LOG_R),
              ("c", "Kapazität C", "kapazitaet", 1e-9, 10e-6, 1e-6, {**LOG_C, "einheit": "µF"}),
              ("tp", "Prellzeit des Tasters", "zeit", 0.1e-3, 20e-3, 5e-3,
               {"einheit": "ms", "log": True, "grenzen": (1e-6, 1)})]
    RASTER = (23.4, 10.4)
    RASTER_SCHMAL = (11.8, 10.4)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Beim Drücken und Loslassen springt der Kontakt einige Millisekunden lang hin und her "
        "(Prellen). Ohne Entprellung sieht der Eingang jede Berührung als eigenen Tastendruck. Mit RC wird C beim "
        "Drücken über R2 entladen (τ = R2 · C) und beim Loslassen über R1 + R2 geladen – die kurzen Prell-Pausen "
        "ändern die Spannung kaum. Der Schmitt-Trigger (z.B. 74HC14) hat zwei Schwellen (Hysterese, hier "
        "0.55 · U_B und 0.33 · U_B): Eine langsame oder leicht wackelnde Spannung schaltet ihn nur EINMAL. R2 "
        "begrenzt ausserdem den Entladestrom des Kondensators über den Kontakt. Oben Kontakt, in der Mitte die "
        "Spannung am Eingang, unten der erkannte Zustand (1 = gedrückt).")

    def sk_rechnen(self, w, v):
        return rm.entprellung(w["ub"], w["r1"], w["r2"], w["c"], w["tp"], mit_rc=v != self.VARIANTEN[0])

    def sk_zeichnen(self, p, w, e, v):
        mit_rc = v != self.VARIANTEN[0]
        x_a, x_c, y_o, y_a, y_u = 3.2, 6.6, 1.2, 4.4, 9.0
        p.versorgung(x_a, y_o, f"+U_B = {_u(w['ub'])}")
        p.widerstand(x_a, y_o, x_a, y_a, "R1", _r(w["r1"]), seite="links")
        p.knoten(x_a, y_a)
        p.schalter(x_a, y_a + 1.2, x_a, y_a + 2.8, False, "")
        p.text(x_a - 0.35, y_a + 2.0, "S1", "e", fett=True)
        p.leitung((x_a, y_a), (x_a, y_a + 1.2))
        p.leitung((x_a, y_a + 2.8), (x_a, y_u))
        x_ic0, x_ic1, y_ic0, y_ic1 = 8.4, 10.6, y_a - 0.9, y_a + 0.9
        if mit_rc:
            p.widerstand(x_a, y_a, x_c, y_a, "R2", _r(w["r2"]))
            p.knoten(x_c, y_a)
            p.kondensator(x_c, y_a, y_u, "C", fmt(w["c"], "kapazitaet", 3))
            p.knoten(x_c, y_u)
            p.leitung((x_c, y_a), (x_ic0, y_a))
            p.kasten(x_ic0, y_ic0, x_ic1, y_ic1, "74HC14")
            p.text((x_ic0 + x_ic1) / 2, y_a + 0.35, "⎍ ¬", "center")
            p.messpunkt(x_c, y_a, "M1", seite="rechts")
        else:
            p.leitung((x_a, y_a), (x_ic0, y_a))
            p.kasten(x_ic0, y_ic0, x_ic1, y_ic1, "µC-Pin")
            p.messpunkt(x_a + 1.6, y_a, "M1", seite="rechts")
        p.leitung((x_ic1, y_a), (x_ic1 + 0.5, y_a))
        p.anschluss(x_ic1 + 0.5, y_a)
        p.leitung((x_a, y_u), (x_c if mit_rc else x_a, y_u))
        p.masse(x_a, y_u)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 13.8, 22.8
        p.diagramm(gx0, 1.0, gx1, 2.4, [(e["kontakt"], p.leise, None, False)], -0.15, 1.15,
                   "Kontakt S1 (oben = geschlossen)", zeit_text="")
        marken = [(e["u_tp"], "U_T+"), (e["u_tm"], "U_T−")] if mit_rc else [(e["u_tp"], "U_B/2")]
        p.diagramm(gx0, 3.6, gx1, 6.8, [(e["u_c"], SPANNUNG, None, False)], 0.0, w["ub"] * 1.1,
                   "Spannung am Eingang (M1)", marken, zeit_text="")
        farbe = STROM if e["sauber"] else FEHLER[1]
        p.diagramm(gx0, 8.0, gx1, 9.4, [(e["ausgang"], farbe, None, False)], -0.15, 1.15,
                   f"erkannt: {e['druecke']}× gedrückt, {e['loslassen']}× losgelassen",
                   zeit_text=f"0 … {_t(e['t_ende'])}")

    def sk_info(self, w, e, v):
        if v == self.VARIANTEN[0]:
            return [f"Der Eingang erkennt {e['druecke']} Tastendrücke statt 1 – jede Prell-Berührung zählt",
                    f"Strom über den Kontakt nur U_B / R1 = {_i(w['ub'] / w['r1'])}   ·   "
                    "→ RC + Schmitt-Trigger oder Software-Entprellung (≈ 10 … 20 ms warten)"], FEHLER
        zeilen = [f"Drücken: τ = R2 · C = {_t(e['tau_ab'])}, bis U_T−: t = R2 · C · ln(U_B / U_T−) = {_t(e['t_ab'])}",
                  f"Loslassen: τ = (R1 + R2) · C = {_t(e['tau_auf'])}, bis U_T+: "
                  f"t = (R1 + R2) · C · ln(U_B / (U_B − U_T+)) = {_t(e['t_auf'])}"]
        if not e["sauber"]:
            zeilen.append(f"⚠ {e['druecke']}× gedrückt / {e['loslassen']}× losgelassen erkannt – τ zu klein "
                          f"gegenüber der Prellzeit → C grösser")
            return zeilen, FEHLER
        verz = f"Reaktion nach {_t(e['verzoegerung'])}" if e["verzoegerung"] is not None else ""
        if min(e["t_ab"], e["t_auf"]) < w["tp"]:
            zeilen.append(f"Sauber erkannt ({verz}) – dank Hysterese, obwohl t < Prellzeit. "
                          "Mit Reserve: t ≥ Prellzeit wählen")
            return zeilen, WARN
        zeilen.append(f"✓ Sauber: genau 1 Tastendruck erkannt ({verz})")
        return zeilen, OK


# =============================================================================
# ANTI-ALIASING
# =============================================================================
class AntiAliasingSchaltung(_MitDiagramm):
    TITEL = "🔌 Anti-Aliasing-Tiefpass vor dem ADC (interaktiv)"
    UNTERTITEL = "Signal über f_s / 2: Die Abtastpunkte ergeben eine falsche, tiefere Frequenz"
    SCHALTER = [("filter", "RC-Tiefpass eingebaut")]
    REGLER = [("fs", "Abtastrate f_s", "frequenz", 100.0, 1e6, 1e3, LOG_F),
              ("f", "Signal-/Störfrequenz f", "frequenz", 1.0, 1e6, 900.0, LOG_F),
              ("r", "Widerstand R", "widerstand", 100.0, 1e6, 10e3, LOG_R),
              ("c", "Kapazität C", "kapazitaet", 1e-9, 10e-6, 330e-9, LOG_C)]
    RASTER = (23.4, 10)
    RASTER_SCHMAL = (12.4, 10)
    SEITENVERHAELTNIS = 0.5
    BITS = 12
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der ADC misst nur zu den Abtastzeitpunkten (rote Punkte). Liegt die Frequenz über "
        "der halben Abtastrate (Nyquist, f_s / 2), passen die Punkte genauso gut zu einer TIEFEREN Frequenz "
        "f_alias = |f − n · f_s| (blau) – das Signal ist nicht mehr vom echten zu unterscheiden und lässt sich "
        "nachträglich nicht herausfiltern. Deshalb kommt VOR den ADC ein Tiefpass, der alles über f_s / 2 dämpft. "
        "Ein RC-Glied (1. Ordnung) dämpft nur 20 dB pro Dekade: Für einen 12-Bit-ADC bräuchte man über 72 dB – "
        "in der Praxis: höher abtasten (Oversampling) und digital filtern, oder Filter höherer Ordnung (OPV).")

    def sk_rechnen(self, w, v):
        if w["filter"]:
            e = rm.anti_aliasing(w["fs"], w["f"], w["r"], w["c"], self.BITS)
        else:
            e = rm.anti_aliasing(w["fs"], w["f"], bits=self.BITS)
        f_a, f, fs = e["f_alias"], w["f"], w["fs"]
        # Fenster: mind. 8, höchstens 40 Abtastungen, möglichst 2 Perioden des Alias
        n_abtast = min(max(round(2 * fs / abs(f_a)) if f_a else 40, 8), 40)
        dauer = n_abtast / fs
        phi = -math.atan(f / e["fg"]) if e["fg"] else 0.0
        a = e["betrag"]
        punkte = int(min(max(400, 40 * f * dauer), 3000))
        e["kurve_echt"] = [(k / punkte, a * math.sin(2 * math.pi * f * dauer * k / punkte + phi))
                           for k in range(punkte + 1)]
        e["kurve_alias"] = [(k / 300, a * math.sin(2 * math.pi * f_a * dauer * k / 300 + phi)) for k in range(301)]
        e["abtastungen"] = [(k / n_abtast, a * math.sin(2 * math.pi * f * k / fs + phi)) for k in range(n_abtast + 1)]
        e["dauer"] = dauer
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_k, y_o, y_u = 2.4, 6.4, 2.4, 8.4
        x_i0, x_i1 = 8.4, 11.0
        p.wechselquelle(x_q, y_o + 1.4, y_u - 1.4, "u_e", _f(w["f"]))
        p.leitung((x_q, y_o + 1.4), (x_q, y_o))
        p.leitung((x_q, y_u - 1.4), (x_q, y_u), (x_i0 + 1.3, y_u), (x_i0 + 1.3, y_o + 2.4))
        if w["filter"]:
            p.widerstand(x_q, y_o, x_k, y_o, "R", _r(w["r"]))
            p.kondensator(x_k, y_o, y_u, "C", fmt(w["c"], "kapazitaet", 3))
            p.knoten(x_k, y_o)
            p.knoten(x_k, y_u)
            p.leitung((x_k, y_o), (x_i0, y_o))
            p.text(x_k + 0.6, y_u - 0.5, f"fg = {_f(e['fg'])}", "w", fett=True)
        else:
            p.leitung((x_q, y_o), (x_i0, y_o))
        p.kasten(x_i0, y_o - 1.0, x_i1, y_o + 2.4, "ADC")
        p.text((x_i0 + x_i1) / 2, y_o + 0.6, f"f_s = {_f(w['fs'])}", "center", klein=True)
        p.text((x_i0 + x_i1) / 2, y_o + 1.2, f"{self.BITS} Bit", "center", klein=True, farbe=p.leise)
        p.messpunkt(x_k if w["filter"] else x_k - 1.0, y_o, "M1", seite="rechts")
        p.masse(4.2, y_u)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gy0, gx1, gy1 = 14.0, 1.4, 22.8, 8.8
        titel = ("echtes Signal (gestrichelt)  ·  Abtastwerte (rot)  ·  erkannt (blau)"
                 if e["faltet"] else "Signal (gestrichelt)  ·  Abtastwerte (rot)  ·  erkannt (blau)")
        p.diagramm(gx0, gy0, gx1, gy1, [(e["kurve_echt"], p.leise, 1, True),
                                        (e["kurve_alias"], SPANNUNG, None, False)],
                   -1.15, 1.15, titel, [(1.0, "1"), (-1.0, "−1")], zeit_text=f"0 … {_t(e['dauer'])}")
        for t, wert in e["abtastungen"]:
            _punkt(p, gx0, gy0, gx1, gy1, t, wert, -1.15, 1.15)

    def sk_info(self, w, e, v):
        zeilen = [f"Nyquist f_s / 2 = {_f(e['nyquist'])}   ·   Signal f = {_f(w['f'])}   ·   "
                  f"ADC erkennt {_f(abs(e['f_alias']))}"]
        if w["filter"]:
            zeilen.append(f"RC-Tiefpass fg = {_f(e['fg'])}:  Dämpfung bei f {e['db']:.1f} dB, bei f_s / 2 "
                          f"{e['db_nyquist']:.1f} dB   (nötig für {self.BITS} Bit: −{e['noetig_db']:.0f} dB)")
        if not e["faltet"]:
            zeilen.append("✓ f liegt unter f_s / 2 – das Signal wird richtig erfasst")
            return zeilen, OK
        zeilen.append(f"⚠ Aliasing: {_f(w['f'])} erscheint als {_f(abs(e['f_alias']))} mit "
                      f"{e['betrag'] * 100:.1f} % der Amplitude – nachträglich nicht mehr zu trennen")
        return zeilen, (WARN if w["filter"] and e["betrag"] < 0.1 else FEHLER)
