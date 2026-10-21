# =============================================================================
# bauteile/grafiken/halbleiter_modell.py
# -----------------------------------------------------------------------------
# INTERAKTIVE HALBLEITER-GRAFIKEN als MODELLE OHNE FENSTER (Desktop-App UND Web):
#
#   DiodenKennlinie    Kennlinie I(U) + Arbeitsgerade von Ub und R -> Arbeitspunkt (Schnittpunkt),
#                      Si-, Schottky-, Ge-Diode, LEDs ("Arbeiten mit Kennlinien", vgl. Zastrow Kap. 2)
#   ZDiodenKennlinie   VOLLE Z-Dioden-Kennlinie: Durchlass (+0.7 V) und Z-Durchbruch bei −Uz,
#                      Arbeitsgerade der Stabilisierung im 3. Quadranten
#   BjtSchalter        Bipolartransistor als Schalter: NPN (Low-Side) | PNP (High-Side)  -> stromgesteuert
#   MosfetSchalter     MOSFET als Schalter: N-Kanal (Low-Side) | P-Kanal (High-Side)     -> spannungsgesteuert
#
#   Low-Side (NPN / N-Kanal)          High-Side (PNP / P-Kanal)
#      +U_B ────┬────                    +U_B ────┬────
#              (💡) Last                       [T]  E / S
#               │                               │
#   U_St ─[R]─ [T]  C / D             U_St ─[R]─┘   C / D
#               │                              (💡) Last
#      GND ─────┴────                    GND ─────┴────
#
# Rechnung: Diode hier (vereinfachtes Exponentialmodell), Schalter in
#   bauteile/rechner/transistor_mathe.py  schalter()   (NPN/PNP)
#   bauteile/rechner/mosfet_mathe.py      schalter(), gate_umladen()
#
# WER RUFT DAS AUF?  bauteile/rechner/halbleiter_rechner.py (diode_kennlinie, zdiode_kennlinie,
#                    transistor_simulator, mosfet_simulator) über GrafikVerweis
# =============================================================================

import math

import config                                                            # -> config.py
from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import (BLAU, GRAU, GRUEN, ORANGE, ROT,  # -> grafiken/schaltplan.py
                                          SchaltungsModell, farbe_waehlen)
from bauteile.grafiken.skala import schoene_grenze                       # -> grafiken/skala.py
from bauteile.rechner import mosfet_mathe as mm                          # -> rechner/mosfet_mathe.py
from bauteile.rechner import transistor_mathe as tm                      # -> rechner/transistor_mathe.py

WARN = ("#B45309", ORANGE)
FEHLER = ("#B91C1C", ROT)


def _mischen(a, b, anteil):
    """Mischt zwei Farben #RRGGBB / #RGB (anteil 0 = a, 1 = b)."""
    def rgb(f):
        f = f.lstrip("#")
        if len(f) == 3:
            f = "".join(z * 2 for z in f)
        return [int(f[i:i + 2], 16) for i in (0, 2, 4)] if len(f) == 6 else [35, 38, 45]
    x, y = rgb(a), rgb(b)
    anteil = max(0.0, min(1.0, anteil))
    return "#" + "".join(f"{round(p + (q - p) * anteil):02x}" for p, q in zip(x, y))


def _farben(p):
    """Text-, leise, Linien- und Hintergrundfarbe passend zu hell/dunkel."""
    return (farbe_waehlen(config.FARBEN["text"], p.dunkel), farbe_waehlen(config.FARBEN["text_leise"], p.dunkel),
            farbe_waehlen(config.FARBEN["rahmen"], p.dunkel), farbe_waehlen(config.FARBEN["flaeche"], p.dunkel))


# =============================================================================
# 1) DIODEN-KENNLINIE MIT ARBEITSGERADE
# =============================================================================
# Vereinfachtes Modell: I(U) = I_ref · e^((U − U_ref) / m)
#   U_ref = Spannung bei I_ref = 10 mA, m = Steilheit (kleiner = steiler)
DIODEN = {
    "Si-Diode (1N4148)":        {"u": 0.70, "m": 0.045, "farbe": BLAU},
    "Schottky (BAT46)":         {"u": 0.35, "m": 0.040, "farbe": "#8B5CF6"},
    "Germanium":                {"u": 0.30, "m": 0.050, "farbe": "#A16207"},
    "LED rot":                  {"u": 1.90, "m": 0.060, "farbe": ROT},
    "LED blau / weiss":         {"u": 3.00, "m": 0.080, "farbe": "#60A5FA"},
    # Z-Dioden: "u" = Z-Spannung Uz (Durchbruch in SPERRRICHTUNG bei U_AK = −Uz)
    "Z-Diode 3.3 V":            {"u": 3.30, "m": 0.090, "farbe": ORANGE, "z": True},
    "Z-Diode 5.1 V":            {"u": 5.10, "m": 0.040, "farbe": ORANGE, "z": True},
    "Z-Diode 6.8 V":            {"u": 6.80, "m": 0.030, "farbe": ORANGE, "z": True},
}
SI_VORWAERTS = {"u": 0.70, "m": 0.045}      # Durchlassbereich der Z-Diode (wie eine Si-Diode)
I_REF = 0.010


def ist_z(typ):
    return DIODEN[typ].get("z", False)


def _strom(u, typ):
    d = DIODEN[typ]
    return I_REF * math.exp(min((u - d["u"]) / d["m"], 50))


def arbeitspunkt(ub, r, typ):
    """Schnittpunkt Kennlinie / Arbeitsgerade I = (Ub − U)/R. Rückgabe (U, I)."""
    if ub <= 0 or r <= 0:
        return 0.0, 0.0
    lo, hi = 0.0, ub
    for _ in range(60):                         # Bisektion: g(U) = I_Diode − I_Gerade steigt monoton
        mitte = (lo + hi) / 2
        if _strom(mitte, typ) - (ub - mitte) / r > 0:
            hi = mitte
        else:
            lo = mitte
    u = (lo + hi) / 2
    return u, (ub - u) / r


class DiodenKennlinie(SchaltungsModell):
    TITEL = "📈 Kennlinie & Arbeitspunkt (interaktiv)"
    UNTERTITEL = "Die Diode stellt sich dort ein, wo Kennlinie und Arbeitsgerade sich schneiden"
    VARIANTEN = [t for t in DIODEN if not ist_z(t)]
    REGLER = [("ub", "Versorgung Ub", "spannung", 0.5, 12.0, 5.0, {"einheit": "V", "grenzen": (0.1, 50)}),
              ("r", "Vorwiderstand R", "widerstand", 10.0, 2000.0, 330.0, {"einheit": "Ω", "grenzen": (1, 1e6)})]
    SEITENVERHAELTNIS = 0.5
    MAX_HOEHE = 380
    ERKLAERUNG = ("Was zeigt die Grafik?  Die Kennlinie zeigt, welcher Strom bei welcher Spannung durch die Diode "
                  "fliesst. Die Arbeitsgerade zeigt, was der Vorwiderstand zulässt: I = (Ub − U_D) / R. Beides muss "
                  "gleichzeitig gelten – darum stellt sich der Arbeitspunkt im Schnittpunkt ein. Die Kennlinie ist ein "
                  "vereinfachtes Modell (typische Werte), kein bestimmtes Datenblatt.")

    def sk_rechnen(self, w, v):
        typ = v if v in DIODEN else self.VARIANTEN[0]
        u, i = arbeitspunkt(w["ub"], w["r"], typ)
        if ist_z(typ) and i < 1e-7:                    # praktisch kein Strom -> nicht "1e-14 A" anzeigen
            i, u = 0.0, w["ub"]
        return {"typ": typ, "u": u, "i": i}

    def sk_info(self, w, e, v):
        ub, u, i, typ = w["ub"], e["u"], e["i"], e["typ"]
        if ist_z(typ):
            uz = DIODEN[typ]["u"]
            minus = "−" if i > 0 else ""
            zeilen = [f"Arbeitspunkt (Kennlinie): U_AK = −{fmt(u, 'spannung')}   I_AK = {minus}{fmt(i, 'strom')}",
                      f"In der Schaltung (Kathode an +, gegen Masse gemessen): U_Z = +{fmt(u, 'spannung')}   "
                      f"I_Z = {fmt(i, 'strom')}   P_Z = {fmt(u * i, 'leistung')}",
                      f"Am Vorwiderstand: {fmt(ub - u, 'spannung')}"]
            zeilen.append(f"Ue liegt unter Uz = {fmt(uz, 'spannung')} → Z-Diode sperrt noch, sie stabilisiert NICHT"
                          if ub < uz * 0.97 else
                          "Die Spannung bleibt fast bei Uz, auch wenn Ue oder R sich ändern → Stabilisierung")
            return zeilen, config.FARBEN["akzent"]
        zeilen = [f"Arbeitspunkt: U_D = {fmt(u, 'spannung')}   I = {fmt(i, 'strom')}   P_D = {fmt(u * i, 'leistung')}",
                  f"Am Widerstand: {fmt(ub - u, 'spannung')}   P_R = {fmt((ub - u) * i, 'leistung')}"]
        if ub < DIODEN[typ]["u"] * 0.9:
            zeilen.append("Ub liegt unter der Schwellspannung → es fliesst fast kein Strom")
        return zeilen, config.FARBEN["akzent"]

    def sk_zeichnen(self, p, w, e, v):
        if ist_z(e["typ"]):
            self._z_zeichnen(p, w, e)
            return
        c, wb, h = p.c, p.breite, p.hoehe
        ub, r, typ = w["ub"], w["r"], e["typ"]
        u_ap, i_ap = arbeitspunkt(ub, r, typ)
        d = DIODEN[typ]
        _, text, linie, _bg = _farben(p)
        schrift = (config.SCHRIFT, max(8, int(h / 26)))
        links, rechts, oben, unten = 0.12 * wb, 0.96 * wb, 0.08 * h, 0.84 * h
        u_max = max(d["u"] * 1.5, min(ub, d["u"] * 3), 1.0)                 # bis etwas über die Schwelle bzw. Ub
        i_max = schoene_grenze(max(ub / r, i_ap * 1.3, 1e-7) * 1.1)         # Stromachse am Signal ausgerichtet

        def x(u):
            return links + (rechts - links) * u / u_max

        def y(i):
            return unten - (unten - oben) * i / i_max

        for k in range(1, 5):                                                # Raster
            c.create_line(x(u_max * k / 4), oben, x(u_max * k / 4), unten, fill=linie, dash=(2, 4))
            c.create_text(x(u_max * k / 4), unten + 0.06 * h, text=fmt(u_max * k / 4, "spannung", 2), fill=text,
                          font=schrift)
            c.create_line(links, y(i_max * k / 4), rechts, y(i_max * k / 4), fill=linie, dash=(2, 4))
            c.create_text(links - 4, y(i_max * k / 4), anchor="e", text=fmt(i_max * k / 4, "strom", 2), fill=text,
                          font=schrift)
        c.create_line(links, unten, rechts, unten, fill=text, width=2, arrow="last")
        c.create_line(links, unten, links, oben - 0.03 * h, fill=text, width=2, arrow="last")
        c.create_text(rechts, unten - 0.04 * h, anchor="e", text="U_D", fill=text, font=schrift)
        c.create_text(links + 6, oben, anchor="w", text="I", fill=text, font=schrift)

        punkte = []                                                          # Kennlinie, soweit sie im Bild bleibt
        for n in range(161):
            u = u_max * n / 160
            i = _strom(u, typ)
            if i > i_max:
                punkte += [x(u), y(i_max)]
                break
            punkte += [x(u), y(i)]
        if len(punkte) >= 4:
            c.create_line(*punkte, fill=d["farbe"], width=3)

        u_start, u_ende = max(0.0, ub - i_max * r), min(ub, u_max)          # Arbeitsgerade (0 | Ub/R) … (Ub | 0)
        if u_ende > u_start:
            c.create_line(x(u_start), y((ub - u_start) / r), x(u_ende), y((ub - u_ende) / r),
                          fill=ORANGE, width=2, dash=(6, 4))
            c.create_text(x(u_start) + 6, y((ub - u_start) / r) - 8, anchor="w", fill=ORANGE, font=schrift,
                          text=f"Arbeitsgerade  (Ub = {fmt(ub, 'spannung', 3)}, R = {fmt(r, 'widerstand', 3)})")
        if u_ap <= u_max and i_ap <= i_max:                                  # Arbeitspunkt
            px, py = x(u_ap), y(i_ap)
            c.create_line(px, py, px, unten, fill=GRUEN, dash=(2, 3))
            c.create_line(links, py, px, py, fill=GRUEN, dash=(2, 3))
            c.create_oval(px - 7, py - 7, px + 7, py + 7, fill=GRUEN, outline="white", width=2)
            c.create_text(px + 10, py + 14, anchor="w", text="Arbeitspunkt", fill=GRUEN, font=schrift)

    def _z_zeichnen(self, p, w, e):
        """Volle Z-Dioden-Kennlinie mit Achsenkreuz im Ursprung (1. Quadrant Durchlass, 3. Quadrant Durchbruch),
        Arbeitsgerade der Stabilisierung (Ue, Rv) im 3. Quadranten von (0 | −Ue/Rv) nach (−Ue | 0)."""
        c, wb, h = p.c, p.breite, p.hoehe
        ub, r, typ = w["ub"], w["r"], e["typ"]
        d = DIODEN[typ]
        uz = d["u"]
        _, text, linie, _bg = _farben(p)
        schrift = (config.SCHRIFT, max(8, int(h / 26)))
        klein = (config.SCHRIFT, max(7, int(h / 32)))
        links, rechts, oben, unten = 0.06 * wb, 0.96 * wb, 0.07 * h, 0.90 * h
        u_min, u_max = -max(uz * 1.3, ub * 1.08, 2.0), 1.2
        i_unten = -schoene_grenze(max(ub / r, 1e-7) * 1.15)                 # Sperrbereich, am Signal ausgerichtet
        i_oben = -i_unten * 0.55                                            # Durchlassbereich (kleiner dargestellt)

        def x(u):
            return links + (rechts - links) * (u - u_min) / (u_max - u_min)

        def y(i):
            return oben + (unten - oben) * (i_oben - i) / (i_oben - i_unten)

        schritt = 1.0 if -u_min <= 8 else 2.0
        k = -schritt
        while k > u_min:
            c.create_line(x(k), oben, x(k), unten, fill=linie, dash=(2, 4))
            c.create_text(x(k), y(0) + 0.045 * h, text=f"{k:g} V".replace("-", "−"), fill=text, font=klein)
            k -= schritt
        for anteil in (0.5, 1.0):
            iy = i_unten * anteil
            c.create_line(links, y(iy), rechts, y(iy), fill=linie, dash=(2, 4))
            c.create_text(x(0) + 4, y(iy), anchor="w", text=f"−{fmt(-iy, 'strom', 2)}", fill=text, font=klein)
        c.create_line(links, y(0), rechts, y(0), fill=text, width=2, arrow="last")
        c.create_line(x(0), unten, x(0), oben - 0.02 * h, fill=text, width=2, arrow="last")
        c.create_text(rechts, y(0) - 0.04 * h, anchor="e", text="U_AK", fill=text, font=schrift)
        c.create_text(x(0) + 6, oben, anchor="w", text="I_AK", fill=text, font=schrift)
        c.create_text(x(0.6), oben + 0.12 * h, text="Durchlass", fill=text, font=klein)
        c.create_text(x(-uz / 2), y(0) - 0.05 * h, text="Sperrbereich (fast kein Strom)", fill=text, font=klein)
        c.create_line(x(-uz), oben, x(-uz), unten, fill=d["farbe"], dash=(4, 3))
        c.create_text(x(-uz) - 4, oben + 0.03 * h, anchor="e", fill=d["farbe"], font=schrift,
                      text=f"−Uz = −{fmt(uz, 'spannung', 3)}")
        c.create_text(x(-uz) - 4, y(i_unten * 0.75), anchor="e", fill=d["farbe"], font=klein,
                      text="Z-Durchbruch\n(hier arbeitet sie)")
        punkte = []                                                          # Durchlassbereich (wie Si-Diode)
        for n in range(61):
            u = u_max * n / 60
            i = I_REF * math.exp(min((u - SI_VORWAERTS["u"]) / SI_VORWAERTS["m"], 50))
            if i > i_oben:
                punkte += [x(u), y(i_oben)]
                break
            punkte += [x(u), y(i)]
        if len(punkte) >= 4:
            c.create_line(*punkte, fill=d["farbe"], width=3)
        punkte = []                                                          # Sperr- und Durchbruchbereich
        for n in range(201):
            u = u_min * n / 200
            i = -_strom(-u, typ)
            if i < i_unten:
                punkte += [x(u), y(i_unten)]
                break
            punkte += [x(u), y(i)]
        if len(punkte) >= 4:
            c.create_line(*punkte, fill=d["farbe"], width=3)
        c.create_line(x(0), y(-ub / r), x(-ub), y(0), fill=ORANGE, width=2, dash=(6, 4))
        c.create_text(x(-ub) + 6, y(0) + 0.09 * h, anchor="w", fill=ORANGE, font=klein,
                      text=f"Arbeitsgerade (Ue = {fmt(ub, 'spannung', 3)}, Rv = {fmt(r, 'widerstand', 3)})")
        u_ap, i_ap = arbeitspunkt(ub, r, typ)
        px, py = x(-u_ap), y(-i_ap)
        c.create_line(px, py, px, y(0), fill=GRUEN, dash=(2, 3))
        c.create_line(x(0), py, px, py, fill=GRUEN, dash=(2, 3))
        c.create_oval(px - 7, py - 7, px + 7, py + 7, fill=GRUEN, outline="white", width=2)
        c.create_text(px + 10, max(py + 14, y(0) + 0.15 * h), anchor="w", text="Arbeitspunkt", fill=GRUEN, font=schrift)
        c.create_text(links, unten, anchor="sw", fill=text, font=klein,
                      text="In der Schaltung ist die Kathode an Plus → gemessen wird +Uz")


class ZDiodenKennlinie(DiodenKennlinie):
    TITEL = "📈 Z-Diode: Kennlinie & Arbeitspunkt (interaktiv)"
    UNTERTITEL = "Stabilisierung mit Vorwiderstand: Arbeitspunkt im Z-Durchbruch"
    VARIANTEN = ["Z-Diode 5.1 V", "Z-Diode 3.3 V", "Z-Diode 6.8 V"]
    REGLER = [("ub", "Eingang Ue", "spannung", 0.5, 15.0, 9.0, {"einheit": "V", "grenzen": (0.1, 50)}),
              ("r", "Vorwiderstand Rv", "widerstand", 10.0, 2000.0, 330.0, {"einheit": "Ω", "grenzen": (1, 1e6)})]
    MAX_HOEHE = 420
    ERKLAERUNG = ("Was zeigt die Grafik?  In Sperrrichtung leitet die Z-Diode fast nicht – bis zur Z-Spannung. Dort "
                  "steigt der Strom steil an, die Spannung bleibt fast konstant: Das nutzt man zum Stabilisieren. "
                  "Die Arbeitsgerade (Ue, Rv) liegt im 3. Quadranten; ihr Schnittpunkt mit dem Durchbruch ist der "
                  "Arbeitspunkt. Vereinfachtes Modell mit typischen Werten.")


# =============================================================================
# 2) TRANSISTOR- UND MOSFET-SCHALTER
# =============================================================================
class _SchalterModell(SchaltungsModell):
    """
    Unterklassen liefern: VARIANTEN (Low-Side, High-Side), REGLER, STARTWERTE, ERKLAERUNG,
      _rechnen(w, high) -> dict (zustand "aus" | "teil" | "voll", i, i_max, ub, rl, p_t, u_st, ...)
      _info(e)          -> (zeilen, farbe)
      _bauteil(c, …)    -> zeichnet Transistor und Ansteuerung
    """
    SEITENVERHAELTNIS = 0.58
    MAX_HOEHE = 430

    def sk_rechnen(self, w, v):
        return self._rechnen(w, v == self.VARIANTEN[1])

    def sk_info(self, w, e, v):
        return self._info(e)

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        text, leise, _linie, bg = _farben(p)
        schrift = (config.SCHRIFT, max(8, int(h / 28)))
        fett = (config.SCHRIFT, max(9, int(h / 24)), "bold")
        dick = max(2, int(h / 120))
        zustand_farbe = {"aus": GRAU, "teil": ORANGE, "voll": GRUEN}[e["zustand"]]
        anteil_strom = min(1.0, e["i"] / e["i_max"]) if e["i_max"] > 0 else 0.0
        strom_farbe = _mischen(leise, GRUEN, anteil_strom)
        high = v == self.VARIANTEN[1]
        xs = 0.56 * wb                                   # senkrechte Hauptleitung
        y_ub, y_gnd = 0.08 * h, 0.92 * h
        y_t, y_l = (0.36 * h, 0.70 * h) if high else (0.66 * h, 0.32 * h)
        r_t = 0.10 * h
        r_l = min(0.075 * h, 0.06 * wb)

        c.create_line(xs - 0.10 * wb, y_ub, xs + 0.10 * wb, y_ub, fill=ROT, width=dick + 1)        # Schienen
        c.create_text(xs + 0.11 * wb, y_ub, anchor="w", text=f"+U_B = {fmt(e['ub'], 'spannung', 3)}", fill=ROT,
                      font=schrift)
        c.create_line(xs - 0.07 * wb, y_gnd, xs + 0.07 * wb, y_gnd, fill=text, width=dick + 1)
        c.create_line(xs - 0.04 * wb, y_gnd + 0.025 * h, xs + 0.04 * wb, y_gnd + 0.025 * h, fill=text, width=dick)
        c.create_text(xs + 0.08 * wb, y_gnd, anchor="w", text="GND", fill=leise, font=schrift)
        punkte = sorted([y_ub, y_gnd, y_t - r_t, y_t + r_t, y_l - r_l, y_l + r_l])            # Leitungen
        for y0, y1 in zip(punkte[0::2], punkte[1::2]):
            c.create_line(xs, y0, xs, y1, fill=strom_farbe, width=dick)

        hell = (e["u_last"] * e["i"]) / (e["ub"] * e["i_max"]) if e["i_max"] > 0 else 0.0     # Lampe ~ Leistung
        if hell > 0.03:
            glanz = r_l * (1.2 + 0.6 * hell)
            c.create_oval(xs - glanz, y_l - glanz, xs + glanz, y_l + glanz, outline="",
                          fill=_mischen(bg, "#FFD54A", 0.35 * hell))
        c.create_oval(xs - r_l, y_l - r_l, xs + r_l, y_l + r_l, width=dick, outline=text, fill=_mischen(bg, "#FFE066", hell))
        k = r_l * 0.6
        c.create_line(xs - k, y_l - k, xs + k, y_l + k, fill=text, width=dick)
        c.create_line(xs - k, y_l + k, xs + k, y_l - k, fill=text, width=dick)
        x_text = xs + 1.9 * r_l
        c.create_text(x_text, y_l - 0.035 * h, anchor="w", fill=leise, font=schrift, text=f"Last {fmt(e['rl'], 'widerstand', 3)}")
        c.create_text(x_text, y_l + 0.035 * h, anchor="w", fill=text, font=schrift, text=f"I = {fmt(e['i'], 'strom', 3)}")

        self._bauteil(c, wb, h, w, e, xs, y_t, r_t, high, zustand_farbe, text, leise, bg, schrift, fett, dick)

        c.create_text(0.03 * wb, 0.06 * h, anchor="w", fill=zustand_farbe, font=fett,
                      text={"aus": "AUS – sperrt", "teil": "HALB OFFEN – heizt!", "voll": "EIN – voll durchgeschaltet"}[e["zustand"]])
        c.create_text(0.03 * wb, 0.12 * h, anchor="w", fill=leise, font=schrift,
                      text="High-Side (Schalter an +U_B)" if high else "Low-Side (Schalter an GND)")
        bx0, bx1, by = (0.04 * wb, 0.30 * wb, 0.84 * h) if high else (0.72 * wb, 0.96 * wb, 0.84 * h)   # Wärme-Balken
        p_ref = max(e["ub"] * e["i_max"] / 4, 1e-9)          # grösster möglicher Verlust: bei halbem Strom
        anteil = min(1.0, e["p_t"] / p_ref)
        c.create_text(bx0 if high else bx1, by - 0.05 * h, anchor="w" if high else "e",
                      text=f"Wärme im Transistor: {fmt(e['p_t'], 'leistung', 3)}", fill=leise, font=schrift)
        c.create_rectangle(bx0, by - 0.02 * h, bx1, by + 0.02 * h, outline=leise)
        if anteil > 0.005:
            c.create_rectangle(bx0, by - 0.02 * h, bx0 + (bx1 - bx0) * anteil, by + 0.02 * h, outline="",
                               fill=_mischen(GRUEN, ROT, anteil))

    @staticmethod
    def _steuerleitung(c, wb, h, y, x_ende, u_st, r_text, schrift, fett, dick, bg):
        """Ansteuerung links: Punkt U_St, Widerstand, Leitung bis x_ende."""
        x_ein = 0.06 * wb
        c.create_line(x_ein, y, x_ende, y, fill=BLAU, width=dick)
        c.create_oval(x_ein - 5, y - 5, x_ein + 5, y + 5, fill=BLAU, outline="")
        c.create_text(x_ein, y - 0.06 * h, anchor="w", text=f"U_St = {fmt(u_st, 'spannung', 3)}", fill=BLAU, font=fett)
        rx0, rx1 = 0.17 * wb, 0.27 * wb
        c.create_rectangle(rx0, y - 0.03 * h, rx1, y + 0.03 * h, fill=bg, outline=BLAU, width=dick)
        c.create_text((rx0 + rx1) / 2, y + 0.065 * h, text=r_text, fill=BLAU, font=schrift)


class BjtSchalter(_SchalterModell):
    TITEL = "🔌 Bipolartransistor als Schalter (interaktiv)"
    UNTERTITEL = "NPN oder PNP wählen, Steuerspannung verändern – wann ist er wirklich gesättigt?"
    VARIANTEN = ["NPN (Low-Side)", "PNP (High-Side)"]
    REGLER = [("ub", "U_B", "spannung", 3.0, 24.0, 12.0, {"einheit": "V", "grenzen": (0.5, 60)}),
              ("rl", "Last R_L", "widerstand", 10.0, 1000.0, 120.0, {"einheit": "Ω", "log": True, "grenzen": (1, 1e6)}),
              ("rb", "R_B", "widerstand", 100.0, 100e3, 1e3, {"einheit": "kΩ", "log": True, "grenzen": (1, 10e6)}),
              ("b", "B min (β)", "zahl", 20.0, 500.0, 100.0, {"grenzen": (1, 2000)}),
              ("ust", "Steuerspannung U_St", "spannung", 0.0, 24.0, 0.0, {"einheit": "V", "grenzen": (0, 60), "schritte": 240})]
    STARTWERTE = {"NPN (Low-Side)": {"ust": 0.0}, "PNP (High-Side)": {"ust": 12.0}}     # jeweils AUS
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der Bipolartransistor ist STROMGESTEUERT: Der Basisstrom I_B bestimmt, wie viel "
        "Kollektorstrom höchstens fliessen darf (I_C = B · I_B). Erst wenn I_B grösser ist als I_C,max / B "
        "(Übersteuerungsfaktor ü ≥ 1, als Schalter ü = 2 … 5), ist der Transistor gesättigt: U_CE ≈ 0.2 V, wenig "
        "Wärme, die Lampe leuchtet voll. Dazwischen arbeitet er als Verstärker und setzt viel Leistung in Wärme um. "
        "NPN schaltet auf der Low-Side (Emitter an GND, einschalten mit HIGH). PNP schaltet auf der High-Side "
        "(Emitter an +U_B): eingeschaltet wird mit LOW, und zum Ausschalten muss die Basis fast auf +U_B.")

    def _rechnen(self, w, high):
        a = tm.schalter("PNP" if high else "NPN", w["ub"], w["rl"], w["ust"], w["rb"], w["b"])   # transistor_mathe.py
        zustand = {"gesperrt": "aus", "aktiv": "teil", "gesättigt": "voll"}[a["zustand"]]
        return dict(a, zustand=zustand, i=a["i_c"], u_t=a["u_ce"], i_max=a["i_c_max"], ub=w["ub"], rl=w["rl"],
                    u_st=w["ust"], b=w["b"])

    def _info(self, e):
        high = e["typ"] == "PNP"
        zeilen = []
        if e["zustand"] == "aus":
            zeilen.append("AUS: " + ("Basis liegt höher als U_B − 0.7 V → kein Basisstrom" if high
                                     else "U_St < 0.7 V → Basis-Emitter-Diode sperrt, kein Basisstrom"))
        else:
            zeilen.append(f"I_B = {fmt(e['i_b'], 'strom')}   ·   nötig für Sättigung: I_C,max / B = "
                          f"{fmt(e['i_b_noetig'], 'strom')}   →   Übersteuerung ü = {e['ue']:.2f}")
            zeilen.append(f"I_C = {fmt(e['i_c'], 'strom')}   ·   U_CE = {fmt(e['u_ce'], 'spannung')}   ·   "
                          f"P_T = {fmt(e['p_t'], 'leistung')}")
            if e["ue"] < 1:
                zeilen.append("⚠ Basisstrom reicht NICHT für Sättigung → Transistor nur halb offen und wird heiss. "
                              + ("U_St weiter senken oder R_B verkleinern" if high else "U_St erhöhen oder R_B verkleinern"))
            elif e["ue"] < 2:
                zeilen.append("⚠ Knapp gesättigt (ü < 2): B streut und sinkt bei Kälte/grossem Strom → als Schalter "
                              "mit ü = 2 … 5 auslegen")
            elif e["ue"] > 10:
                zeilen.append("Stark übersteuert (ü > 10): sicher ein, aber lange Ausschaltverzögerung (Speicherzeit) "
                              "und unnötig viel Steuerstrom")
            else:
                zeilen.append("✅ Sicher gesättigt (ü = 2 … 10) – so soll ein Schalter arbeiten")
        if high and e["ub"] > 5.7:
            zeilen.append(f"PNP an {fmt(e['ub'], 'spannung')}: Zum AUSschalten muss U_St ≥ "
                          f"{fmt(e['ub'] - 0.7, 'spannung')} sein – ein µC mit 3.3/5 V schafft das nicht "
                          "→ NPN als Pegelwandler davor")
        farbe = WARN if e["zustand"] == "teil" or (e["zustand"] == "voll" and e["ue"] < 2) else config.FARBEN["akzent"]
        return zeilen, farbe

    def _bauteil(self, c, wb, h, w, e, xs, y, r, high, zfarbe, text, leise, bg, schrift, fett, dick):
        xb = xs - 0.45 * r                                       # Basis-Balken
        c.create_oval(xs - 1.1 * r, y - r, xs + 0.9 * r, y + r, outline=zfarbe, width=dick + 1)
        c.create_line(xb, y - 0.55 * r, xb, y + 0.55 * r, fill=zfarbe, width=dick + 2)
        pfeil = dict(fill=text, width=dick, arrow="last", arrowshape=(max(8, r * 0.3), max(10, r * 0.36), max(4, r * 0.14)))
        if high:                                                 # PNP: Emitter OBEN, Pfeil zeigt zum Balken
            c.create_line(xs, y - r, xb, y - 0.25 * r, **pfeil)
            c.create_line(xb, y + 0.25 * r, xs, y + r, fill=text, width=dick)
            oben, unten = "E", "C"
        else:                                                    # NPN: Emitter UNTEN, Pfeil zeigt raus
            c.create_line(xb, y - 0.25 * r, xs, y - r, fill=text, width=dick)
            c.create_line(xb, y + 0.25 * r, xs, y + r, **pfeil)
            oben, unten = "C", "E"
        c.create_text(xs + 8, y - r - 0.02 * h, anchor="w", text=oben, fill=leise, font=schrift)
        c.create_text(xs + 8, y + r + 0.02 * h, anchor="w", text=unten, fill=leise, font=schrift)
        c.create_text(xs + 1.1 * r, y, anchor="w", fill=zfarbe, font=fett, text=f"U_CE = {fmt(e['u_ce'], 'spannung', 3)}")
        c.create_text(xs - 1.1 * r - 6, y - 0.04 * h, anchor="e", text="B", fill=leise, font=schrift)
        self._steuerleitung(c, wb, h, y, xb, e["u_st"], f"R_B {fmt(w['rb'], 'widerstand', 3)}", schrift, fett, dick, bg)
        if e["i_b"] > 0:                                         # Basisstrom-Pfeil: dicker = mehr Übersteuerung
            richtung = (0.29 * wb, xb - 10) if not high else (xb - 10, 0.29 * wb)   # PNP: Strom fliesst aus der Basis
            c.create_line(richtung[0], y + 0.06 * h, richtung[1], y + 0.06 * h, fill=BLAU,
                          width=max(1, min(7, 1 + 2 * e["ue"])), arrow="last")
            c.create_text((0.27 * wb + xs - 1.1 * r) / 2, y + 0.11 * h, text=f"I_B = {fmt(e['i_b'], 'strom', 3)}",
                          fill=BLAU, font=schrift)


class MosfetSchalter(_SchalterModell):
    TITEL = "🔌 MOSFET als Schalter (interaktiv)"
    UNTERTITEL = "N- oder P-Kanal wählen, Gate-Spannung verändern – wann ist er wirklich voll eingeschaltet?"
    VARIANTEN = ["N-Kanal (Low-Side)", "P-Kanal (High-Side)"]
    REGLER = [("ub", "U_B", "spannung", 3.0, 24.0, 12.0, {"einheit": "V", "grenzen": (0.5, 60)}),
              ("rl", "Last R_L", "widerstand", 1.0, 1000.0, 24.0, {"einheit": "Ω", "log": True, "grenzen": (0.1, 1e6)}),
              ("uth", "|U_GS(th)|", "spannung", 0.5, 5.0, 2.0, {"einheit": "V", "grenzen": (0.2, 10)}),
              ("rds", "R_DS(on)", "widerstand", 1e-3, 1.0, 0.05, {"einheit": "mΩ", "log": True, "grenzen": (1e-4, 100)}),
              ("uspec", "… gemessen bei |U_GS|", "spannung", 2.5, 10.0, 10.0, {"einheit": "V", "grenzen": (1, 20)}),
              ("qg", "Gate-Ladung Q_g", "ladung", 1e-9, 200e-9, 30e-9, {"einheit": "nC", "grenzen": (1e-10, 1e-5)}),
              ("rg", "Gate-Widerstand R_G", "widerstand", 1.0, 1000.0, 10.0, {"einheit": "Ω", "log": True, "grenzen": (0.1, 1e6)}),
              ("ug", "Gate-Spannung U_G (gegen GND)", "spannung", 0.0, 25.0, 0.0,
               {"einheit": "V", "grenzen": (0, 60), "schritte": 250})]
    STARTWERTE = {"N-Kanal (Low-Side)": {"ug": 0.0}, "P-Kanal (High-Side)": {"ug": 12.0}}   # jeweils AUS
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der MOSFET ist SPANNUNGSGESTEUERT: Die Spannung zwischen Gate und Source öffnet den "
        "Kanal. Im eingeschalteten Zustand fliesst kein Gate-Strom – beim UMSCHALTEN muss aber die Gate-Ladung Q_g "
        "bewegt werden, deshalb braucht es bei schneller PWM einen Treiber. Entscheidend ist nicht U_GS(th) (dort "
        "beginnt er erst zu leiten), sondern R_DS(on) bei der tatsächlichen Gate-Spannung: Nur bei der im Datenblatt "
        "angegebenen U_GS ist der kleine Widerstand garantiert. N-Kanal schaltet auf der Low-Side (Source an GND). "
        "P-Kanal schaltet auf der High-Side (Source an +U_B): eingeschaltet wird, indem man das Gate nach unten zieht.")

    def _rechnen(self, w, high):
        m = mm.schalter("P" if high else "N", w["ub"], w["rl"], w["ug"], w["uth"], w["rds"], w["uspec"])  # mosfet_mathe.py
        zustand = {"sperrt": "aus", "linear": "teil", "voll": "voll"}[m["zustand"]]
        u_treiber = abs(m["u_gs"]) if abs(m["u_gs"]) > w["uth"] else w["uspec"]    # Umladen mit der Einschaltspannung
        gate = dict(mm.gate_umladen(w["qg"], u_treiber, w["rg"]), u_treiber=u_treiber)
        return dict(m, zustand=zustand, u_t=m["u_ds"], ub=w["ub"], rl=w["rl"], u_st=w["ug"], gate=gate,
                    uth=w["uth"], uspec=w["uspec"], rds=w["rds"])

    def _info(self, e):
        high = e["kanal"] == "P"
        name = "U_SG" if high else "U_GS"
        zeilen = []
        if e["zustand"] == "aus":
            zeilen.append(f"AUS: {name} = {fmt(e['u_gs'], 'spannung')} liegt unter U_th = {fmt(e['uth'], 'spannung')}"
                          + (" → Gate liegt nahe +U_B" if high else ""))
        else:
            zeilen.append(f"{name} = {fmt(e['u_gs'], 'spannung')}   ·   R_on ≈ {fmt(e['r_on'], 'widerstand')}   ·   "
                          f"I = {fmt(e['i'], 'strom')}   ·   U_DS = {fmt(e['u_ds'], 'spannung')}   ·   "
                          f"P = {fmt(e['p_t'], 'leistung')}")
            if e["zustand"] == "teil":
                zeilen.append("⚠ Nur knapp über U_th: Kanal begrenzt den Strom, U_DS ist gross → MOSFET wird heiss")
            elif e["unter_spec"]:
                zeilen.append(f"⚠ R_DS(on) = {fmt(e['rds'], 'widerstand')} gilt nur bei {name} = "
                              f"{fmt(e['uspec'], 'spannung')}. Bei {fmt(e['u_gs'], 'spannung')} ist er ca. "
                              f"{e['r_on'] / e['rds']:.1f}× grösser → Logic-Level-Typ mit R_DS(on)-Angabe bei dieser "
                              "Spannung wählen")
            elif not e["zu_hoch"]:
                zeilen.append("✅ Voll eingeschaltet bei der Datenblatt-Spannung – R_DS(on) wie spezifiziert")
        if e["zu_hoch"]:
            zeilen.append(f"❌ |{name}| = {fmt(abs(e['u_gs']), 'spannung')} > {mm.U_GS_MAX:g} V: Gate-Oxid wird zerstört "
                          "→ Z-Diode (z.B. 12 V) zwischen Gate und Source oder Spannungsteiler")
        if high and e["ub"] > 5.7:
            zeilen.append(f"P-Kanal an {fmt(e['ub'], 'spannung')}: Zum AUSschalten muss das Gate auf ≈ U_B – "
                          "ein µC mit 3.3/5 V schafft das nicht → NPN/N-MOSFET als Pegelwandler davor")
        g = e["gate"]
        zeilen.append(f"Umschalten mit {fmt(g['u_treiber'], 'spannung')} über R_G: Gate-Strom bis ≈ "
                      f"{fmt(g['i_g'], 'strom')}, Q_g umladen dauert ≈ {fmt(g['t_schalt'], 'zeit')} "
                      "(statisch fliesst kein Gate-Strom)")
        farbe = FEHLER if e["zu_hoch"] else (WARN if e["zustand"] == "teil" or
                                             (e["zustand"] == "voll" and e["unter_spec"]) else config.FARBEN["akzent"])
        return zeilen, farbe

    def _bauteil(self, c, wb, h, w, e, xs, y, r, high, zfarbe, text, leise, bg, schrift, fett, dick):
        xk = xs - 0.45 * r                                       # Kanal (3 Striche = Anreicherungstyp)
        xg = xk - 0.28 * r                                       # Gate-Platte
        c.create_oval(xs - 1.1 * r, y - r, xs + 0.9 * r, y + r, outline=zfarbe, width=dick + 1)
        c.create_line(xg, y - 0.55 * r, xg, y + 0.55 * r, fill=text, width=dick)
        for dy in (-0.45, 0, 0.45):
            c.create_line(xk, y + (dy - 0.15) * r, xk, y + (dy + 0.15) * r, fill=zfarbe, width=dick + 2)
        c.create_line(xk, y - 0.45 * r, xs, y - 0.45 * r, xs, y - r, fill=text, width=dick)
        c.create_line(xk, y + 0.45 * r, xs, y + 0.45 * r, xs, y + r, fill=text, width=dick)
        pfeil = dict(fill=text, width=dick, arrow="last", arrowshape=(max(8, r * 0.3), max(10, r * 0.36), max(4, r * 0.14)))
        if high:                                                 # P-Kanal: Source OBEN, Pfeil zeigt vom Kanal weg
            c.create_line(xk, y, xs, y, **pfeil)
            c.create_line(xs, y, xs, y - 0.45 * r, fill=text, width=dick)
            oben, unten = "S", "D"
        else:                                                    # N-Kanal: Source UNTEN, Pfeil zeigt zum Kanal
            c.create_line(xs, y, xk, y, **pfeil)
            c.create_line(xs, y, xs, y + 0.45 * r, fill=text, width=dick)
            oben, unten = "D", "S"
        c.create_text(xs + 8, y - r - 0.02 * h, anchor="w", text=oben, fill=leise, font=schrift)
        c.create_text(xs + 8, y + r + 0.02 * h, anchor="w", text=unten, fill=leise, font=schrift)
        c.create_text(xs + 1.1 * r, y, anchor="w", fill=zfarbe, font=fett, text=f"U_DS = {fmt(e['u_ds'], 'spannung', 3)}")
        c.create_text(xs - 1.1 * r - 6, y - 0.04 * h, anchor="e", text="G", fill=leise, font=schrift)
        self._steuerleitung(c, wb, h, y, xg, e["u_st"], f"R_G {fmt(w['rg'], 'widerstand', 3)}", schrift, fett, dick, bg)
        c.create_text((0.27 * wb + xs - 1.1 * r) / 2, y + 0.07 * h, fill=BLAU, font=schrift,
                      text=f"{'U_SG' if high else 'U_GS'} = {fmt(e['u_gs'], 'spannung', 3)}")
