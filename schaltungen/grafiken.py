# =============================================================================
# schaltungen/grafiken.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE der Widerstandsnetzwerke. Werte stehen direkt im Plan,
# Spannung = blau, Strom = rot, Messpunkte = orange (M1, M2 ...).
#
#   SpannungsteilerSchaltung   unbelastet / mit Last, Querstromverhältnis
#   StromteilerSchaltung       zwei Zweige an einer Stromquelle
#   PullSchaltung              Pull-up / Pull-down mit Taster, Leckstrom, Flanke
#   PotiSchaltung              Potentiometer mit Last + Kennlinie daneben
#   BrueckeSchaltung           Wheatstone-Brücke mit Diagonalspannung
#
# Jede Klasse beschreibt nur Regler, Rechnung (-> netzwerk_mathe.py) und Zeichnung.
# Das Grundgerüst (Regler, Neuzeichnen, Meldungen) kommt aus
#   bauteile/grafiken/schaltplan.py -> SchaltungsKarte
#
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_spannungsteiler")
# =============================================================================

import config                                                            # -> config.py
from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import (OK, SPANNUNG, STROM, WARN,     # -> bauteile/grafiken/schaltplan.py
                                          SchaltungsKarte)
from schaltungen import netzwerk_mathe as nm                             # -> schaltungen/netzwerk_mathe.py

R_BEREICH = (100.0, 1e6)                       # Slider-Bereich für Widerstände (log)
R_GRENZEN = (1.0, 100e6)                       # im Zahlenfeld erlaubt
LOG_R = {"einheit": "kΩ", "log": True, "grenzen": R_GRENZEN}


def _u(wert):
    return fmt(wert, "spannung", 3)


def _i(wert):
    return fmt(wert, "strom", 3)


def _r(wert):
    return fmt(wert, "widerstand", 3)


# =============================================================================
# SPANNUNGSTEILER
# =============================================================================
class SpannungsteilerSchaltung(SchaltungsKarte):
    TITEL = "🔌 Spannungsteiler (interaktiv)"
    UNTERTITEL = "Widerstände verändern, Last zuschalten – wie stark bricht Ua ein?"
    VARIANTEN = ["unbelastet", "mit Last R_L"]
    REGLER = [("ue", "Eingang Ue", "spannung", 0.0, 30.0, 12.0, {"einheit": "V", "grenzen": (0, 1000)}),
              ("r1", "R1 (oben)", "widerstand", *R_BEREICH, 10e3, LOG_R),
              ("r2", "R2 (unten)", "widerstand", *R_BEREICH, 10e3, LOG_R),
              ("rl", "Last R_L", "widerstand", *R_BEREICH, 10e3, LOG_R)]
    RASTER = (14, 8.6)
    SEITENVERHAELTNIS = 0.62
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Durch R1 und R2 fliesst derselbe Strom, deshalb teilt sich Ue im Verhältnis der "
        "Widerstände auf: Ua = Ue · R2 / (R1 + R2). Eine Last R_L liegt PARALLEL zu R2 – der untere Widerstand wird "
        "kleiner und Ua sinkt. Wie stark, hängt vom Querstromverhältnis q = I2 / I_L ab: Ist der Strom durch den Teiler "
        "mindestens 10-mal grösser als der Laststrom, bleibt Ua fast stabil. Darum ist ein Spannungsteiler keine "
        "Spannungsversorgung, sondern liefert eine Bezugs- oder Messspannung.")

    def sk_rechnen(self, w, v):
        return nm.spannungsteiler(w["ue"], w["r1"], w["r2"], w["rl"] if v == self.VARIANTEN[1] else None)

    def sk_zeichnen(self, p, w, e, v):
        last = v == self.VARIANTEN[1]
        x_q, x_r, x_a, y_o, y_m, y_u = 1.6, 6.0, 9.6, 1.0, 4.3, 7.6
        p.quelle(x_q, y_o + 0.6, y_u - 0.6, "Ue", _u(w["ue"]))
        p.leitung((x_q, y_o + 0.6), (x_q, y_o), (x_r, y_o))
        p.leitung((x_q, y_u - 0.6), (x_q, y_u), (x_a if last else x_r, y_u))
        p.widerstand(x_r, y_o, x_r, y_m, "R1", _r(w["r1"]))
        p.widerstand(x_r, y_m, x_r, y_u, "R2", _r(w["r2"]))
        p.leitung((x_r, y_m), (x_a, y_m))
        p.knoten(x_r, y_m)
        p.masse(3.6, y_u)
        p.knoten(3.6, y_u)
        p.strom(2.7, y_o, 4.3, y_o, f"I1 = {_i(e['i1'])}")
        p.strom(x_r, y_m + 0.15, x_r, y_m + 0.95, f"I2 = {_i(e['i2'])}", seite="links")
        if last:
            p.knoten(x_r, y_u)
            p.widerstand(x_a, y_m, x_a, y_u, "R_L", _r(w["rl"]))
            p.strom(7.0, y_m, 8.4, y_m, f"I_L = {_i(e['il'])}")
            p.spannung(x_a + 1.9, y_m, y_u, f"Ua = {_u(e['ua'])}")
            p.leitung((x_a, y_m), (x_a + 1.9, y_m), farbe=p.leise, dick=1)
            p.leitung((x_a, y_u), (x_a + 1.9, y_u), farbe=p.leise, dick=1)
        else:
            p.anschluss(x_a, y_m)
            p.anschluss(x_a, y_u)
            p.leitung((x_r, y_u), (x_a, y_u))
            p.spannung(x_a + 0.5, y_m, y_u, f"Ua = {_u(e['ua'])}")
        p.messpunkt(x_r, y_m, "M1", seite="links")

    def sk_info(self, w, e, v):
        zeilen = [f"Ua = {_u(e['ua'])}   (unbelastet {_u(e['ua0'])})",
                  f"Querstrom I2 = {_i(e['i2'])}   ·   P(R1) = {fmt(e['p1'], 'leistung', 3)}   P(R2) = {fmt(e['p2'], 'leistung', 3)}"]
        if e["q"] is None:
            return zeilen, config.FARBEN["akzent"]
        zeilen.append(f"Last zieht {_i(e['il'])} → Ua {e['abweichung'] * 100:+.1f} %   ·   "
                      f"Querstromverhältnis q = I2 / I_L = {e['q']:.2g}")
        if e["q"] < 10:
            zeilen.append("⚠ q < 10: Teiler zu hochohmig für diese Last → R1, R2 kleiner oder Puffer (OPV)")
            return zeilen, WARN
        zeilen.append("✅ q ≥ 10: Last verändert Ua nur wenig")
        return zeilen, OK


# =============================================================================
# STROMTEILER
# =============================================================================
class StromteilerSchaltung(SchaltungsKarte):
    TITEL = "🔌 Stromteiler (interaktiv)"
    UNTERTITEL = "Ein Strom teilt sich auf zwei Zweige – der kleinere Widerstand bekommt mehr"
    REGLER = [("i", "Gesamtstrom I", "strom", 1e-3, 1.0, 0.1, {"einheit": "mA", "log": True, "grenzen": (1e-6, 100)}),
              ("r1", "R1", "widerstand", 1.0, 100e3, 100.0, {"einheit": "Ω", "log": True, "grenzen": R_GRENZEN}),
              ("r2", "R2", "widerstand", 1.0, 100e3, 300.0, {"einheit": "Ω", "log": True, "grenzen": R_GRENZEN})]
    RASTER = (13, 8.4)
    SEITENVERHAELTNIS = 0.6
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Parallele Zweige haben dieselbe Spannung U. Darum fliesst durch jeden Zweig "
        "I_k = U / R_k: Der Strom teilt sich UMGEKEHRT zu den Widerständen auf, I1 / I2 = R2 / R1. Zusammen ergeben "
        "die Zweigströme wieder den Gesamtstrom (Knotenregel). Bei zwei Zweigen gilt I1 = I · R2 / (R1 + R2). "
        "Praxis: Shunt am Messwerk, parallel geschaltete LEDs (nur mit eigenem Vorwiderstand!), Stromaufteilung "
        "auf Leiterbahnen.")

    def sk_rechnen(self, w, v):
        return nm.stromteiler(w["i"], w["r1"], w["r2"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x1, x2, y_o, y_u = 1.6, 5.6, 9.4, 1.0, 7.4
        i1, i2 = e["stroeme"]
        p.stromquelle(x_q, y_o + 0.6, y_u - 0.6, "I", _i(w["i"]))
        p.leitung((x_q, y_o + 0.6), (x_q, y_o), (x2, y_o))
        p.leitung((x_q, y_u - 0.6), (x_q, y_u), (x2, y_u))
        p.knoten(x1, y_o)
        p.knoten(x1, y_u)
        p.widerstand(x1, y_o, x1, y_u, "R1", _r(w["r1"]))
        p.widerstand(x2, y_o, x2, y_u, "R2", _r(w["r2"]))
        p.strom(2.5, y_o, 4.0, y_o, f"I = {_i(w['i'])}")
        p.strom(x1, y_o + 0.2, x1, y_o + 1.4, f"I1 = {_i(i1)}", seite="links")
        p.strom(x2, y_o + 0.2, x2, y_o + 1.4, f"I2 = {_i(i2)}", seite="links")
        p.spannung(x2 + 1.6, y_o, y_u, f"U = {_u(e['u'])}")
        p.leitung((x2, y_o), (x2 + 1.6, y_o), farbe=p.leise, dick=1)
        p.leitung((x2, y_u), (x2 + 1.6, y_u), farbe=p.leise, dick=1)

    def sk_info(self, w, e, v):
        i1, i2 = e["stroeme"]
        p1, p2 = e["leistungen"]
        return [f"R_ges = R1 || R2 = {_r(e['r_ges'])}   ·   U = I · R_ges = {_u(e['u'])}",
                f"I1 = {_i(i1)} ({i1 / w['i'] * 100:.1f} %)   ·   I2 = {_i(i2)} ({i2 / w['i'] * 100:.1f} %)",
                f"P(R1) = {fmt(p1, 'leistung', 3)}   ·   P(R2) = {fmt(p2, 'leistung', 3)}   ·   "
                f"Probe: I1 + I2 = {_i(i1 + i2)}"], config.FARBEN["akzent"]


# =============================================================================
# PULL-UP / PULL-DOWN
# =============================================================================
class PullSchaltung(SchaltungsKarte):
    TITEL = "🔌 Pull-up / Pull-down (interaktiv)"
    UNTERTITEL = "Taster am Mikrocontroller: definierter Pegel, Strom, Flanke"
    VARIANTEN = ["Pull-up", "Pull-down"]
    SCHALTER = [("taster", "Taster gedrückt")]
    REGLER = [("ub", "Versorgung U_B", "spannung", 1.8, 12.0, 5.0, {"einheit": "V", "grenzen": (0.5, 60)}),
              ("r", "Widerstand R", "widerstand", *R_BEREICH, 10e3, LOG_R),
              ("leck", "Leckstrom Eingang", "strom", 1e-9, 100e-6, 1e-6, {"einheit": "µA", "log": True,
                                                                          "grenzen": (1e-12, 10e-3)}),
              ("c", "Kapazität Pin + Leitung", "kapazitaet", 1e-12, 10e-9, 100e-12, {"einheit": "pF", "log": True,
                                                                                   "grenzen": (1e-13, 1e-6)})]
    RASTER = (14, 8.6)
    SEITENVERHAELTNIS = 0.6
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Ein offener CMOS-Eingang ist sehr hochohmig und „schwebt“ – er fängt Störungen ein "
        "und liest zufällig 0 oder 1. Der Pull-Widerstand zieht ihn auf einen festen Pegel, solange der Taster offen "
        "ist. Wird gedrückt, überbrückt der Taster den Eingang hart auf den anderen Pegel; jetzt fliesst U_B / R "
        "durch den Widerstand. Kleines R: sicherer Pegel und schnelle Flanke, aber mehr Strom. Grosses R: wenig Strom, "
        "aber der Leckstrom des Eingangs verschiebt den Pegel und die Pin-Kapazität macht die Flanke langsam (τ = R·C).")

    def sk_rechnen(self, w, v):
        art = "pullup" if v == self.VARIANTEN[0] else "pulldown"
        return nm.pull_widerstand(art, w["ub"], w["r"], w["taster"], w["leck"], w["c"])

    def sk_zeichnen(self, p, w, e, v):
        pullup = v == self.VARIANTEN[0]
        x, y_o, y_k, y_u, x_pin = 4.2, 1.2, 4.3, 7.4, 9.6
        p.versorgung(x, y_o, f"+U_B = {_u(w['ub'])}")
        p.masse(x, y_u)
        if pullup:
            p.widerstand(x, y_o, x, y_k, "R", _r(w["r"]), seite="links")
            p.leitung((x, y_k), (x, y_k + 0.6))
            p.schalter(x, y_k + 0.6, x, y_u - 0.6, w["taster"], "Taster")
            p.leitung((x, y_u - 0.6), (x, y_u))
            if e["i_r"] > 0:
                p.strom(x, y_k - 0.85, x, y_k - 0.15, f"I = {_i(e['i_r'])}", seite="links")
        else:
            p.leitung((x, y_o), (x, y_o + 0.6))
            p.schalter(x, y_o + 0.6, x, y_k - 0.6, w["taster"], "Taster")
            p.leitung((x, y_k - 0.6), (x, y_k))
            p.widerstand(x, y_k, x, y_u, "R", _r(w["r"]), seite="links")
            if e["i_r"] > 0:
                p.strom(x, y_k + 0.15, x, y_k + 0.85, f"I = {_i(e['i_r'])}", seite="links")
        p.knoten(x, y_k)
        p.leitung((x, y_k), (x_pin, y_k))
        # Pin-Kapazität (parasitär: Eingang + Leitung)
        p.kondensator(7.2, y_k, y_u, "C", fmt(w["c"], "kapazitaet", 3), seite="rechts")
        p.knoten(7.2, y_k)
        p.masse(7.2, y_u)
        # Mikrocontroller als Kasten
        (ax, ay), (bx, by) = p.p(x_pin, y_k - 2.0), p.p(13.6, y_k + 2.0)
        farbe = {"HIGH": OK[1], "LOW": SPANNUNG, "unsicher": WARN[1]}[e["pegel"]]
        p.c.create_rectangle(ax, ay, bx, by, outline=p.linie, width=p.dick, fill=p.bg)
        p.text(11.6, y_k - 1.5, "µC", "center", fett=True)
        p.text(x_pin + 0.25, y_k, "Eingang", "w", klein=True)
        p.text(11.6, y_k + 0.75, _u(e["u_pin"]), "center", fett=True, farbe=SPANNUNG)
        p.text(11.6, y_k + 1.35, e["pegel"], "center", fett=True, farbe=farbe)
        p.messpunkt(x, y_k, "M1", seite="rechts")

    def sk_info(self, w, e, v):
        zeilen = [f"U_Pin = {_u(e['u_pin'])} → {e['pegel']}   (HIGH ab {_u(e['u_high'])}, LOW bis {_u(e['u_low'])})",
                  f"Strom durch R = {_i(e['i_r'])}   ·   P = {fmt(e['p_r'], 'leistung', 3)}   ·   "
                  f"Flanke über R (10→90 %) = {fmt(e['t_flanke'], 'zeit', 3)}"]
        if e["pegel"] == "unsicher":
            zeilen.append("⚠ Pegel liegt im verbotenen Bereich: R zu gross für diesen Leckstrom → R verkleinern")
            return zeilen, WARN
        if w["taster"] and e["i_r"] > 5e-3:
            zeilen.append("⚠ Mehr als 5 mA nur für einen Tastendruck – R ist unnötig klein (Batterie!)")
            return zeilen, WARN
        if e["t_flanke"] > 10e-6:
            zeilen.append("Hinweis: Flanke langsamer als 10 µs – für Taster egal, für Busse (I²C) zu langsam")
        return zeilen, OK


# =============================================================================
# POTENTIOMETER
# =============================================================================
class PotiSchaltung(SchaltungsKarte):
    TITEL = "🔌 Potentiometer als Spannungsteiler (interaktiv)"
    UNTERTITEL = "Schleifer drehen, Last zuschalten – die Kennlinie hängt durch"
    VARIANTEN = ["unbelastet", "mit Last R_L"]
    REGLER = [("ue", "Eingang Ue", "spannung", 0.0, 30.0, 10.0, {"einheit": "V", "grenzen": (0, 1000)}),
              ("rp", "Poti R_P", "widerstand", *R_BEREICH, 10e3, LOG_R),
              ("a", "Schleiferstellung", "prozent", 0.0, 1.0, 0.5, {"einheit": "%"}),
              ("rl", "Last R_L", "widerstand", *R_BEREICH, 10e3, LOG_R)]
    RASTER = (19, 8.6)
    RASTER_SCHMAL = (11.4, 8.6)                # unter MIN_BREITE_KENNLINIE: nur der Schaltplan
    MIN_BREITE_KENNLINIE = 600
    SEITENVERHAELTNIS = 0.6
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der Schleifer teilt das Potentiometer in einen oberen und einen unteren Teil – ohne "
        "Last ist Ua genau proportional zur Stellung (gestrichelte Gerade). Mit Last liegt R_L parallel zum UNTEREN "
        "Teil. Bei ca. 2/3 Stellung ist der Fehler am grössten, an den Enden verschwindet er. Faustregel: "
        "R_L ≥ 10 · R_P hält den Fehler unter ca. 1.5 % von Ue (≈ 0.15 · R_P / R_L). Sonst: kleineres Poti oder Puffer (Spannungsfolger).")

    def sk_raster(self, breite):
        self.poti_kennlinie = breite >= self.MIN_BREITE_KENNLINIE
        return self.RASTER if self.poti_kennlinie else self.RASTER_SCHMAL

    def sk_rechnen(self, w, v):
        last = w["rl"] if v == self.VARIANTEN[1] else None
        e = nm.poti_teiler(w["ue"], w["rp"], w["a"], last)
        e["kurve"] = nm.poti_kennlinie(w["rp"], last) if last else None
        return e

    def sk_zeichnen(self, p, w, e, v):
        last = v == self.VARIANTEN[1]
        x_q, x_p, x_a, y_o, y_u = 1.6, 5.0, 8.4, 1.0, 7.6
        p.quelle(x_q, y_o + 0.6, y_u - 0.6, "Ue", _u(w["ue"]))
        p.leitung((x_q, y_o + 0.6), (x_q, y_o), (x_p, y_o))
        p.leitung((x_q, y_u - 0.6), (x_q, y_u), (x_a, y_u))
        xs, ys = p.poti(x_p, y_o, y_u, w["a"], "R_P", _r(w["rp"]), schleifer_x=x_p + 1.2)
        p.leitung((xs, ys), (xs, 4.3), (x_a, 4.3))
        p.knoten(x_p, y_u)
        if last:
            p.widerstand(x_a, 4.3, x_a, y_u, "R_L", _r(w["rl"]))
            p.knoten(x_a, 4.3)
        else:
            p.anschluss(x_a, 4.3)
            p.anschluss(x_a, y_u)
        p.spannung(x_a + (1.7 if last else 0.5), 4.3, y_u, f"Ua = {_u(e['ua'])}")
        if last:
            p.leitung((x_a, 4.3), (x_a + 1.7, 4.3), farbe=p.leise, dick=1)
            p.leitung((x_a, y_u), (x_a + 1.7, y_u), farbe=p.leise, dick=1)
        p.text(x_p + 1.3, ys - 0.35, f"{w['a'] * 100:.0f} %", "w", klein=True, farbe=p.leise)
        if getattr(self, "poti_kennlinie", True):          # bei schmalem Fenster nur der Schaltplan
            self._kennlinie(p, e, w)

    def _kennlinie(self, p, e, w):
        """Rechts: Ua/Ue über der Schleiferstellung (Gerade = ohne Last, Kurve = mit Last)."""
        gx0, gx1, gy0, gy1 = 12.6, 18.4, 7.2, 1.4
        (a, b), (c, d) = p.p(gx0, gy0), p.p(gx1, gy1)
        p.c.create_line(a, b, c, b, fill=p.leise, width=1)
        p.c.create_line(a, b, a, d, fill=p.leise, width=1)
        p.text(gx0 - 0.15, gy1, "Ue", "e", klein=True, farbe=p.leise)
        p.text(gx0 - 0.15, gy0, "0", "e", klein=True, farbe=p.leise)
        p.text(gx1, gy0 + 0.4, "100 %", "e", klein=True, farbe=p.leise)
        p.text(gx0, gy0 + 0.4, "0 %", "w", klein=True, farbe=p.leise)
        p.text((gx0 + gx1) / 2, gy1 - 0.45, "Ua über Schleiferstellung", "center", klein=True, farbe=p.leise)
        p.c.create_line(a, b, c, d, fill=p.leise, width=max(1, p.dick - 1), dash=(4, 3))

        def punkt(anteil, verhaeltnis):
            return p.p(gx0 + anteil * (gx1 - gx0), gy0 + verhaeltnis * (gy1 - gy0))
        if e["kurve"]:
            pixel = [k for anteil, verhaeltnis in e["kurve"] for k in punkt(anteil, verhaeltnis)]
            p.c.create_line(*pixel, fill=SPANNUNG, width=p.dick, smooth=True)
        verhaeltnis = e["ua"] / w["ue"] if w["ue"] else w["a"]
        px, py = punkt(w["a"], verhaeltnis)
        r = max(4, p.u * 0.13)
        p.c.create_oval(px - r, py - r, px + r, py + r, fill=STROM, outline="")

    def sk_info(self, w, e, v):
        zeilen = [f"Ua = {_u(e['ua'])}   ·   ohne Last wären es {_u(e['ua0'])}",
                  f"R oben = {_r(e['r_oben'])}   ·   R unten = {_r(e['r_unten'])}"]
        if v == self.VARIANTEN[0]:
            return zeilen, config.FARBEN["akzent"]
        fehler = e["fehler"] / w["ue"] * 100 if w["ue"] else 0.0
        zeilen.append(f"Fehler durch die Last: {_u(e['fehler'])} ({fehler:+.1f} % von Ue)   ·   "
                      f"R_L / R_P = {w['rl'] / w['rp']:.2g}")
        if w["rl"] < 10 * w["rp"]:
            zeilen.append("⚠ R_L < 10 · R_P: Kennlinie deutlich gekrümmt → kleineres Poti oder Spannungsfolger")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# WHEATSTONE-BRÜCKE
# =============================================================================
class BrueckeSchaltung(SchaltungsKarte):
    TITEL = "🔌 Wheatstone-Brücke (interaktiv)"
    UNTERTITEL = "Zwei Spannungsteiler nebeneinander – gemessen wird nur der Unterschied"
    REGLER = [("ue", "Speisung Ue", "spannung", 0.0, 24.0, 10.0, {"einheit": "V", "grenzen": (0, 1000)}),
              ("r1", "R1 (links oben)", "widerstand", *R_BEREICH, 1e3, LOG_R),
              ("r2", "R2 (links unten)", "widerstand", *R_BEREICH, 1e3, LOG_R),
              ("r3", "R3 (rechts oben)", "widerstand", *R_BEREICH, 1e3, LOG_R),
              ("r4", "R4 (rechts unten)", "widerstand", *R_BEREICH, 1.01e3, LOG_R)]
    RASTER = (15, 8.8)
    SEITENVERHAELTNIS = 0.58
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Die Brücke besteht aus zwei Spannungsteilern an derselben Speisespannung. Gemessen "
        "wird die Spannung U_d ZWISCHEN den beiden Mittelpunkten M1 und M2. Sind die Teilerverhältnisse gleich "
        "(R1 / R2 = R3 / R4), ist U_d = 0 – die Brücke ist abgeglichen. Ändert sich ein Widerstand nur wenig "
        "(Sensor: Pt100, DMS), entsteht eine kleine, gut messbare Spannung, ohne dass man die grosse Grundspannung "
        "mitmessen muss. Darum misst man kleine Widerstandsänderungen fast immer in einer Brücke.")

    def sk_rechnen(self, w, v):
        return nm.bruecke(w["ue"], w["r1"], w["r2"], w["r3"], w["r4"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_l, x_r, y_o, y_m, y_u = 1.4, 5.0, 11.0, 1.0, 4.4, 7.8
        p.quelle(x_q, y_o + 0.6, y_u - 0.6, "Ue", _u(w["ue"]))
        p.leitung((x_q, y_o + 0.6), (x_q, y_o), (x_r, y_o))
        p.leitung((x_q, y_u - 0.6), (x_q, y_u), (x_r, y_u))
        for x in (x_l,):
            p.knoten(x, y_o)
            p.knoten(x, y_u)
        p.widerstand(x_l, y_o, x_l, y_m, "R1", _r(w["r1"]), seite="links")
        p.widerstand(x_l, y_m, x_l, y_u, "R2", _r(w["r2"]), seite="links")
        p.widerstand(x_r, y_o, x_r, y_m, "R3", _r(w["r3"]), seite="rechts")
        p.widerstand(x_r, y_m, x_r, y_u, "R4", _r(w["r4"]), seite="rechts")
        p.knoten(x_l, y_m)
        p.knoten(x_r, y_m)
        p.leitung((x_l, y_m), (7.5, y_m))
        p.leitung((8.5, y_m), (x_r, y_m))
        p.messgeraet(8.0, y_m, "V")
        p.text(8.0, y_m - 0.75, f"U_d = {_u(e['u_d'])}", "center", fett=True, farbe=SPANNUNG)
        p.messpunkt(x_l, y_m, "M1", seite="rechts")
        p.messpunkt(x_r, y_m, "M2", seite="links")
        p.text(x_l + 0.3, y_m + 0.55, _u(e["u_links"]), "w", klein=True, farbe=SPANNUNG)
        p.text(x_r - 0.3, y_m + 0.55, _u(e["u_rechts"]), "e", klein=True, farbe=SPANNUNG)

    def sk_info(self, w, e, v):
        zeilen = [f"U(M1) = {_u(e['u_links'])}   ·   U(M2) = {_u(e['u_rechts'])}   ·   "
                  f"U_d = U(M1) − U(M2) = {_u(e['u_d'])}"]
        if w["ue"]:
            zeilen.append(f"Empfindlichkeit: {e['u_d'] / w['ue'] * 1000:.3g} mV/V   ·   "
                          f"Abgleich bei R4 = R3 · R2 / R1 = {_r(e['r4_abgleich'])}")
        if abs(e["u_d"]) <= 1e-6 * max(abs(w["ue"]), 1e-9):
            zeilen.append("✅ Brücke abgeglichen (U_d ≈ 0)")
            return zeilen, OK
        return zeilen, config.FARBEN["akzent"]
