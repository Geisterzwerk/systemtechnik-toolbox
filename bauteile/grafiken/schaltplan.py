# =============================================================================
# bauteile/grafiken/schaltplan.py
# -----------------------------------------------------------------------------
# SCHALTPLÄNE ZEICHNEN - auf einem Raster, damit alles sauber ausgerichtet ist.
#
#   Schaltplan      Zeichenwerkzeug: Leitung, Widerstand, Quelle, Masse, Messpunkt,
#                   Spannungs- und Strompfeil ... in RASTER-Einheiten (nicht Pixel)
#   SchaltungsKarte Grundgerüst einer interaktiven Schaltung:
#                   [Variante] + Schaltplan mit Werten + Regler + Ergebnis + Erklärung
#
# RASTER: Ein Plan ist z.B. 12 × 8 Einheiten gross. Er wird so skaliert, dass er
# in die Zeichenfläche passt (zentriert). Koordinaten sind (spalte, zeile),
# 0/0 = oben links. So bleibt der Plan bei jeder Fenstergrösse gleich proportioniert.
#
# FARBEN (wie im Unterricht üblich):
#   Spannung = BLAU (Pfeil von + nach −)     Strom = ROT (Pfeil in Stromrichtung)
#   Messpunkt = ORANGE (M1, M2 ...)         Leitungen/Bauteile = Textfarbe
#
# BEISPIEL:
#   p = Schaltplan(c, w, h, spalten=10, zeilen=8)
#   p.leitung((1, 1), (6, 1), (6, 2))
#   p.widerstand(6, 2, 6, 5, "R1", "10 kΩ")       # senkrecht von (6,2) nach (6,5)
#   p.masse(6, 7)
#
# WER RUFT DAS AUF?  schaltungen/grafiken.py (alle interaktiven Schaltungen)
# =============================================================================

import math

import customtkinter as ctk

import config                                                            # -> config.py
from bauteile.grafiken.halbleiter_grafiken import (BLAU, GRUEN, ORANGE,  # -> grafiken/halbleiter_grafiken.py
                                                   ROT, _farbe)
from bauteile.grafiken.skala import wert_text                             # -> grafiken/skala.py
from bauteile.rechner.basis import WertRegler                            # -> rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel               # -> core/layout.py

SPANNUNG, STROM, MESSPUNKT = BLAU, ROT, ORANGE
WARN = ("#B45309", ORANGE)
OK = ("#15803D", GRUEN)


class Schaltplan:
    """Zeichnet auf einen tk.Canvas in Raster-Einheiten. Siehe Beispiel oben."""

    def __init__(self, c, w, h, spalten, zeilen, rand=0.7):
        self.c = c
        # rand: zusätzlicher Platz links UND rechts (für Beschriftungen, die über den Plan hinausgehen)
        self.u = min(w / (spalten + 2 * rand), h / zeilen)    # Pixel pro Raster-Einheit
        self.x0 = (w - spalten * self.u) / 2                  # zentrieren
        self.y0 = (h - zeilen * self.u) / 2
        self.linie = _farbe(config.FARBEN["text"])
        self.leise = _farbe(config.FARBEN["text_leise"])
        self.bg = _farbe(config.FARBEN["flaeche"])
        self.dick = max(2, round(self.u / 22))
        groesse = max(8, round(self.u * 0.24))                # Schrift wächst mit dem Plan
        self.schrift = (config.SCHRIFT, groesse)
        self.fett = (config.SCHRIFT, groesse, "bold")
        self.klein = (config.SCHRIFT, max(7, groesse - 2))

    # ---- Umrechnung ----------------------------------------------------------
    def p(self, x, y):
        """Raster -> Pixel."""
        return self.x0 + x * self.u, self.y0 + y * self.u

    # ---- Grundelemente -------------------------------------------------------
    def leitung(self, *punkte, farbe=None, dick=None):
        pixel = [k for x, y in punkte for k in self.p(x, y)]
        self.c.create_line(*pixel, fill=farbe or self.linie, width=dick or self.dick, capstyle="round",
                           joinstyle="round")

    def knoten(self, x, y):
        px, py = self.p(x, y)
        r = max(3, self.u * 0.08)
        self.c.create_oval(px - r, py - r, px + r, py + r, fill=self.linie, outline="")

    def text(self, x, y, text, anker="w", farbe=None, fett=False, klein=False):
        px, py = self.p(x, y)
        schrift = self.fett if fett else (self.klein if klein else self.schrift)
        self.c.create_text(px, py, text=text, anchor=anker, fill=farbe or self.linie, font=schrift)

    def _beschriftung(self, x, y, name, wert, seite, farbe=None):
        """Name (fett) + Wert neben einem Bauteil. seite: 'rechts', 'links', 'oben', 'unten'."""
        if seite in ("rechts", "links"):
            anker = "w" if seite == "rechts" else "e"
            # halber Zeilenabstand: mind. 0.2 Raster, bei kleinem Plan nach der Schriftgrösse (Pixel ≈ pt · 1.33)
            halb = max(0.2, 0.62 * self.schrift[1] * 1.33 / self.u)
            self.text(x, y - halb, name, anker, fett=True, farbe=farbe)
            if wert:
                self.text(x, y + halb, wert, anker, farbe=farbe or self.leise)
        else:
            zeile = max(0.36, 1.2 * self.schrift[1] * 1.33 / self.u)     # Zeilenhöhe in Raster-Einheiten
            if seite == "oben":                               # Name über dem Wert, beides über dem Bauteil
                self.text(x, y - 0.4, wert or name, "s", fett=not wert, farbe=farbe or (self.leise if wert else None))
                if wert:
                    self.text(x, y - 0.4 - zeile, name, "s", fett=True, farbe=farbe)
            else:                                             # unten: Name, darunter der Wert
                self.text(x, y + 0.4, name, "n", fett=True, farbe=farbe)
                if wert:
                    self.text(x, y + 0.4 + zeile, wert, "n", farbe=farbe or self.leise)

    # ---- Bauteile ------------------------------------------------------------
    def widerstand(self, x1, y1, x2, y2, name="", wert="", seite=None, farbe=None, laenge=1.4):
        """Widerstand (IEC-Rechteck) zwischen zwei Rasterpunkten - waagrecht oder senkrecht."""
        senkrecht = abs(x2 - x1) < abs(y2 - y1)
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        l2, b2 = laenge / 2, 0.24
        if senkrecht:
            self.leitung((x1, y1), (x1, ym - l2), farbe=farbe)
            self.leitung((x1, ym + l2), (x2, y2), farbe=farbe)
            ecken = (xm - b2, ym - l2, xm + b2, ym + l2)
        else:
            self.leitung((x1, y1), (xm - l2, y1), farbe=farbe)
            self.leitung((xm + l2, y1), (x2, y2), farbe=farbe)
            ecken = (xm - l2, ym - b2, xm + l2, ym + b2)
        a, b = self.p(ecken[0], ecken[1]), self.p(ecken[2], ecken[3])
        self.c.create_rectangle(*a, *b, outline=farbe or self.linie, fill=self.bg, width=self.dick)
        if name or wert:
            seite = seite or ("rechts" if senkrecht else "oben")
            if senkrecht:
                self._beschriftung(xm + (0.42 if seite == "rechts" else -0.42), ym, name, wert, seite)
            else:
                self._beschriftung(xm, ym, name, wert, seite)
        return ecken

    def poti(self, x, y1, y2, anteil, name="", wert="", schleifer_x=None):
        """Senkrechtes Potentiometer von (x,y1) nach (x,y2); Schleifer zeigt von rechts auf die Stelle 'anteil'
        (0 = unten, 1 = oben). Gibt die Rasterposition des Schleiferanschlusses zurück."""
        ecken = self.widerstand(x, y1, x, y2, name, wert, seite="links", laenge=min(2.4, abs(y2 - y1) - 0.6))
        y_s = ecken[3] - anteil * (ecken[3] - ecken[1])
        xs = schleifer_x if schleifer_x is not None else x + 1.0
        x_spitze = ecken[2] + 0.02
        px0, py = self.p(xs, y_s)
        px1, _ = self.p(x_spitze, y_s)
        self.c.create_line(px0, py, px1, py, fill=self.linie, width=self.dick, arrow="last",
                           arrowshape=(self.u * 0.28, self.u * 0.32, self.u * 0.12))
        return xs, y_s

    def quelle(self, x, y1, y2, name="", wert="", seite="links", plus_oben=True):
        """Gleichspannungsquelle senkrecht von (x,y1) [+] nach (x,y2) [−] (Kreis mit Linie, IEC).
        plus_oben=False: Pluspol unten (z.B. verpolte Batterie)."""
        ym, r = (y1 + y2) / 2, 0.45
        self.leitung((x, y1), (x, ym - r))
        self.leitung((x, ym + r), (x, y2))
        (ax, ay), (bx, by) = self.p(x - r, ym - r), self.p(x + r, ym + r)
        self.c.create_oval(ax, ay, bx, by, outline=self.linie, width=self.dick, fill=self.bg)
        self.leitung((x, ym - r), (x, ym + r))
        if plus_oben:
            self.text(x + 0.3, ym - r - 0.05, "+", "sw", fett=True)
        else:
            self.text(x + 0.3, ym + r + 0.05, "+", "nw", fett=True)
        if name or wert:
            self._beschriftung(x - r - 0.25 if seite == "links" else x + r + 0.25, ym, name, wert, seite)

    def stromquelle(self, x, y1, y2, name="", wert="", seite="links"):
        """Ideale Stromquelle senkrecht, Strom fliesst oben heraus (Kreis mit Querstrich, IEC)."""
        ym, r = (y1 + y2) / 2, 0.45
        self.leitung((x, y1), (x, ym - r))
        self.leitung((x, ym + r), (x, y2))
        (ax, ay), (bx, by) = self.p(x - r, ym - r), self.p(x + r, ym + r)
        self.c.create_oval(ax, ay, bx, by, outline=self.linie, width=self.dick, fill=self.bg)
        self.leitung((x - r, ym), (x + r, ym))
        if name or wert:
            self._beschriftung(x - r - 0.25 if seite == "links" else x + r + 0.25, ym, name, wert, seite)

    def kondensator(self, x, y1, y2, name="", wert="", seite="rechts"):
        """Kondensator senkrecht zwischen (x,y1) und (x,y2): zwei Platten in der Mitte."""
        ym, abstand, halb = (y1 + y2) / 2, 0.14, 0.38
        self.leitung((x, y1), (x, ym - abstand))
        self.leitung((x, ym + abstand), (x, y2))
        for dy in (-abstand, abstand):
            self.leitung((x - halb, ym + dy), (x + halb, ym + dy), dick=self.dick + 1)
        if name or wert:
            self._beschriftung(x + (halb + 0.2 if seite == "rechts" else -halb - 0.2), ym, name, wert, seite)

    def masse(self, x, y):
        """Masse-Symbol, Anschluss oben bei (x, y)."""
        self.leitung((x, y), (x, y + 0.25))
        for i, halb in enumerate((0.38, 0.24, 0.10)):
            yy = y + 0.25 + i * 0.13
            self.leitung((x - halb, yy), (x + halb, yy))

    def versorgung(self, x, y, text):
        """Versorgungsanschluss: kurzer Balken mit Text darüber, Anschluss unten bei (x, y)."""
        self.leitung((x, y), (x, y - 0.3))
        self.leitung((x - 0.35, y - 0.3), (x + 0.35, y - 0.3), dick=self.dick + 1)
        self.text(x, y - 0.55, text, "s", fett=True)

    def anschluss(self, x, y, text="", seite="rechts", farbe=None):
        """Offener Anschluss (Klemme) mit Beschriftung."""
        px, py = self.p(x, y)
        r = max(4, self.u * 0.11)
        self.c.create_oval(px - r, py - r, px + r, py + r, outline=farbe or self.linie, width=self.dick, fill=self.bg)
        if text:
            dx = 0.25 if seite == "rechts" else -0.25
            self.text(x + dx, y, text, "w" if seite == "rechts" else "e", fett=True, farbe=farbe)

    def schalter(self, x1, y1, x2, y2, geschlossen, name=""):
        """Schliesser (Taster) zwischen zwei Punkten, waagrecht oder senkrecht."""
        senkrecht = abs(x2 - x1) < abs(y2 - y1)
        for x, y in ((x1, y1), (x2, y2)):
            px, py = self.p(x, y)
            r = max(3, self.u * 0.07)
            self.c.create_oval(px - r, py - r, px + r, py + r, outline=self.linie, width=self.dick, fill=self.bg)
        if geschlossen:
            self.leitung((x1, y1), (x2, y2))
        elif senkrecht:
            self.leitung((x2, y2), (x1 + 0.45, y1 + 0.15))
        else:
            self.leitung((x1, y1), (x2 - 0.15, y2 - 0.45))
        if name:
            if senkrecht:
                self.text(x1 + 0.6, (y1 + y2) / 2, name, "w", fett=True)
            else:
                self.text((x1 + x2) / 2, y1 - 0.7, name, "center", fett=True)

    # ---- Halbleiter -----------------------------------------------------------
    def diode(self, x1, y1, x2, y2, name="", wert="", art="normal", seite=None, farbe=None, groesse=0.34):
        """
        Diode von ANODE (x1,y1) nach KATHODE (x2,y2) - Strom fliesst in Richtung der Dreieckspitze.
        art: "normal", "schottky", "z" (Z-Diode), "tvs" (bidirektional: zwei Dreiecke gegeneinander)
        Waagrecht oder senkrecht. Gibt die Mitte zurück.
        """
        farbe = farbe or self.linie
        dx, dy = x2 - x1, y2 - y1
        laenge = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / laenge, dy / laenge                 # Richtung Anode -> Kathode
        nx, ny = -uy, ux                                  # quer dazu
        xm, ym, g = (x1 + x2) / 2, (y1 + y2) / 2, groesse
        halb = g * (2 if art == "tvs" else 1)             # halbe Baulänge des Symbols
        self.leitung((x1, y1), (xm - ux * halb, ym - uy * halb), farbe=farbe)
        self.leitung((xm + ux * halb, ym + uy * halb), (x2, y2), farbe=farbe)
        if art == "tvs":                                  # zwei Dreiecke, Spitzen zur Mitte
            dreiecke = [(xm - ux * g, ym - uy * g, 1), (xm + ux * g, ym + uy * g, -1)]
        else:
            dreiecke = [(xm, ym, 1)]
        for cx, cy, r in dreiecke:
            basis = (cx - ux * g * r, cy - uy * g * r)
            spitze = (cx + ux * g * r, cy + uy * g * r)
            ecken = [self.p(basis[0] + nx * g, basis[1] + ny * g), self.p(basis[0] - nx * g, basis[1] - ny * g),
                     self.p(*spitze)]
            self.c.create_polygon(*[k for e in ecken for k in e], outline=farbe, fill=self.bg, width=self.dick)
        # Kathodenstrich (bei TVS in der Mitte, gemeinsam für beide Dreiecke)
        kx, ky = (xm, ym) if art == "tvs" else (xm + ux * g, ym + uy * g)
        a, b = (kx + nx * g, ky + ny * g), (kx - nx * g, ky - ny * g)
        self.leitung(a, b, farbe=farbe)
        haken = 0.13
        if art in ("z", "tvs"):                           # Z: abgeknickte Enden
            self.leitung(a, (a[0] - ux * haken, a[1] - uy * haken), farbe=farbe)
            self.leitung(b, (b[0] + ux * haken, b[1] + uy * haken), farbe=farbe)
        elif art == "schottky":                           # Schottky: S-förmige Enden
            self.leitung(a, (a[0] + ux * haken, a[1] + uy * haken),
                         (a[0] + ux * haken - nx * haken, a[1] + uy * haken - ny * haken), farbe=farbe)
            self.leitung(b, (b[0] - ux * haken, b[1] - uy * haken),
                         (b[0] - ux * haken + nx * haken, b[1] - uy * haken + ny * haken), farbe=farbe)
        if name or wert:
            senkrecht = abs(dy) > abs(dx)
            seite = seite or ("rechts" if senkrecht else "oben")
            if senkrecht:
                self._beschriftung(xm + (g + 0.25 if seite == "rechts" else -g - 0.25), ym, name, wert, seite)
            else:
                self._beschriftung(xm, ym, name, wert, seite)
        return xm, ym

    def npn(self, x, y, name="", seite="rechts", basis_rechts=False):
        """
        NPN-Transistor: Basis links bei (x - 0.9, y), Kollektor oben (x, y - 1), Emitter unten (x, y + 1).
        basis_rechts=True: gespiegelt, Basis rechts bei (x + 0.9, y) (z.B. Multivibrator, Basis zur Mitte).
        """
        m = -1 if basis_rechts else 1                                                     # Spiegelung
        self.leitung((x - 0.9 * m, y), (x - 0.3 * m, y))
        self.leitung((x - 0.3 * m, y - 0.45), (x - 0.3 * m, y + 0.45), dick=self.dick + 2)  # Basis-Balken
        self.leitung((x - 0.3 * m, y - 0.2), (x, y - 0.55), (x, y - 1))                   # Kollektor
        (a, b), (c, d) = self.p(x - 0.3 * m, y + 0.2), self.p(x, y + 0.55)
        self.c.create_line(a, b, c, d, fill=self.linie, width=self.dick, arrow="last",
                           arrowshape=(self.u * 0.22, self.u * 0.26, self.u * 0.1))        # Emitter-Pfeil nach aussen
        self.leitung((x, y + 0.55), (x, y + 1))
        if name:
            self.text(x + (0.3 if seite == "rechts" else -1.2), y, name, "w" if seite == "rechts" else "e", fett=True)

    def pnp(self, x, y, name="", seite="rechts"):
        """
        PNP-Transistor: Basis links bei (x - 0.9, y), EMITTER oben (x, y - 1), Kollektor unten (x, y + 1)
        (so wie er in einer Gegentakt-Endstufe unten sitzt). Emitter-Pfeil zeigt zur Basis hin.
        """
        self.leitung((x - 0.9, y), (x - 0.3, y))
        self.leitung((x - 0.3, y - 0.45), (x - 0.3, y + 0.45), dick=self.dick + 2)      # Basis-Balken
        self.leitung((x, y - 1), (x, y - 0.55))
        (a, b), (c, d) = self.p(x, y - 0.55), self.p(x - 0.3, y - 0.2)
        self.c.create_line(a, b, c, d, fill=self.linie, width=self.dick, arrow="last",
                           arrowshape=(self.u * 0.22, self.u * 0.26, self.u * 0.1))        # Emitter-Pfeil hinein
        self.leitung((x - 0.3, y + 0.2), (x, y + 0.55), (x, y + 1))                       # Kollektor
        if name:
            self.text(x + (0.3 if seite == "rechts" else -1.2), y, name, "w" if seite == "rechts" else "e", fett=True)

    def nmosfet(self, x, y, name="", seite="rechts"):
        """N-MOSFET senkrecht: Gate links bei (x - 0.9, y), Drain oben (x, y - 1), Source unten (x, y + 1)."""
        xk = x - 0.3                                      # Kanal
        self.leitung((x - 0.9, y), (x - 0.48, y))
        self.leitung((x - 0.48, y - 0.45), (x - 0.48, y + 0.45), dick=self.dick + 1)     # Gate-Platte
        for y0, y1 in ((-0.55, -0.22), (-0.12, 0.12), (0.22, 0.55)):                      # Anreicherung: unterbrochen
            self.leitung((xk, y + y0), (xk, y + y1), dick=self.dick + 1)
        self.leitung((xk, y - 0.38), (x, y - 0.38), (x, y - 1))                          # Drain
        self.leitung((xk, y + 0.38), (x, y + 0.38), (x, y + 1))                          # Source
        self.leitung((x, y), (x, y + 0.38))                                              # Bulk an Source
        (a, b), (c, d) = self.p(x, y), self.p(xk + 0.02, y)
        self.c.create_line(a, b, c, d, fill=self.linie, width=self.dick, arrow="last",       # N-Kanal: Pfeil hinein
                           arrowshape=(self.u * 0.18, self.u * 0.22, self.u * 0.08))
        if name:
            self.text(x + (0.3 if seite == "rechts" else -1.2), y, name, "w" if seite == "rechts" else "e", fett=True)

    def njfet(self, x, y, name="", seite="rechts"):
        """N-Kanal-JFET senkrecht: Gate links bei (x - 0.9, y), Drain oben (x, y - 1), Source unten (x, y + 1)."""
        xk = x - 0.3
        self.leitung((xk, y - 0.5), (xk, y + 0.5), dick=self.dick + 1)                  # durchgehender Kanal
        self.leitung((xk, y - 0.35), (x, y - 0.35), (x, y - 1))                          # Drain
        self.leitung((xk, y + 0.35), (x, y + 0.35), (x, y + 1))                          # Source
        (a, b), (c, d) = self.p(x - 0.9, y), self.p(xk - 0.02, y)
        self.c.create_line(a, b, c, d, fill=self.linie, width=self.dick, arrow="last",       # N-Kanal: Pfeil zum Kanal
                           arrowshape=(self.u * 0.2, self.u * 0.24, self.u * 0.09))
        if name:
            self.text(x + (0.3 if seite == "rechts" else -1.2), y, name, "w" if seite == "rechts" else "e", fett=True)

    def kondensator_waagrecht(self, x1, x2, y, name="", wert=""):
        """Kondensator waagrecht zwischen (x1,y) und (x2,y), z.B. Koppelkondensator."""
        xm, abstand, halb = (x1 + x2) / 2, 0.14, 0.38
        self.leitung((x1, y), (xm - abstand, y))
        self.leitung((xm + abstand, y), (x2, y))
        for dx in (-abstand, abstand):
            self.leitung((xm + dx, y - halb), (xm + dx, y + halb), dick=self.dick + 1)
        if name or wert:
            self._beschriftung(xm, y - 0.05, name, wert, "oben")

    def motor(self, x, y1, y2, name="M", wert="", seite="rechts"):
        """Gleichstrommotor senkrecht zwischen (x,y1) und (x,y2): Kreis mit M."""
        ym, r = (y1 + y2) / 2, 0.5
        self.leitung((x, y1), (x, ym - r))
        self.leitung((x, ym + r), (x, y2))
        (ax, ay), (bx, by) = self.p(x - r, ym - r), self.p(x + r, ym + r)
        self.c.create_oval(ax, ay, bx, by, outline=self.linie, width=self.dick, fill=self.bg)
        self.text(x, ym, "M", "center", fett=True)
        if wert:
            self._beschriftung(x + (r + 0.25 if seite == "rechts" else -r - 0.25), ym, name if name != "M" else "Motor",
                               wert, seite)

    def pmosfet(self, x, y, name="", gate_unten=1.4):
        """
        P-MOSFET waagrecht in einer Leitung: DRAIN links (x - 1, y), SOURCE rechts (x + 1, y),
        Gate unten bei (x, y + gate_unten). Die Body-Diode (Anode = Drain, Kathode = Source) ist darüber
        eingezeichnet - über sie fliesst beim Einschalten zuerst der Strom.
        """
        yk = y + 0.45                                     # Kanal liegt unter der Leitung
        self.leitung((x - 1, y), (x - 0.5, y), (x - 0.5, yk))
        self.leitung((x + 1, y), (x + 0.5, y), (x + 0.5, yk))
        for x0, x1 in ((-0.55, -0.2), (-0.12, 0.12), (0.2, 0.55)):                      # Anreicherung: unterbrochen
            self.leitung((x + x0, yk), (x + x1, yk), dick=self.dick + 1)
        (a, b), (c, d) = self.p(x, yk), self.p(x, yk + 0.3)
        self.c.create_line(a, b, c, d, fill=self.linie, width=self.dick, arrow="last",       # P-Kanal: Pfeil nach aussen
                           arrowshape=(self.u * 0.16, self.u * 0.2, self.u * 0.08))
        self.leitung((x - 0.5, yk + 0.32), (x + 0.5, yk + 0.32), dick=self.dick + 1)    # Gate-Platte
        self.leitung((x, yk + 0.32), (x, y + gate_unten))
        self.leitung((x - 0.5, y), (x - 0.5, y - 0.55))
        self.leitung((x + 0.5, y), (x + 0.5, y - 0.55))
        self.diode(x - 0.5, y - 0.55, x + 0.5, y - 0.55, groesse=0.17)                   # Body-Diode
        self.text(x - 0.95, y + 0.25, "D", "nw", klein=True, farbe=self.leise)
        self.text(x + 0.95, y + 0.25, "S", "ne", klein=True, farbe=self.leise)
        self.text(x + 0.15, y + gate_unten - 0.3, "G", "w", klein=True, farbe=self.leise)
        if name:
            self.text(x, y - 0.95, name, "s", fett=True)

    def wechselquelle(self, x, y1, y2, name="", wert="", seite="links"):
        """Wechselspannungsquelle senkrecht (Kreis mit Sinus)."""
        ym, r = (y1 + y2) / 2, 0.45
        self.leitung((x, y1), (x, ym - r))
        self.leitung((x, ym + r), (x, y2))
        (ax, ay), (bx, by) = self.p(x - r, ym - r), self.p(x + r, ym + r)
        self.c.create_oval(ax, ay, bx, by, outline=self.linie, width=self.dick, fill=self.bg)
        punkte = [self.p(x - 0.28 + 0.56 * k / 16, ym - 0.18 * math.sin(2 * math.pi * k / 16)) for k in range(17)]
        self.c.create_line(*[k for pk in punkte for k in pk], fill=self.linie, width=max(1, self.dick - 1))
        if name or wert:
            self._beschriftung(x - r - 0.25 if seite == "links" else x + r + 0.25, ym, name, wert, seite)

    def trafo(self, x, y1, y2, mittelanzapfung=False, name=""):
        """
        Transformator senkrecht, Wicklungen von y1 bis y2:
          primär links bei x - 0.55, sekundär rechts bei x + 0.55
          (Mittelanzapfung sekundär bei (x + 0.55, (y1 + y2) / 2))
        """
        for versatz, richtung in ((-0.55, -1), (0.55, 1)):
            xs = x + versatz
            n = 4
            hoehe = (y2 - y1) / n
            for k in range(n):
                ya = y1 + k * hoehe
                punkte = [self.p(xs + richtung * 0.22 * math.sin(math.pi * t / 10), ya + hoehe * t / 10)
                          for t in range(11)]
                self.c.create_line(*[q for pk in punkte for q in pk], fill=self.linie, width=self.dick)
        for xk in (x - 0.08, x + 0.08):                   # Eisenkern
            self.leitung((xk, y1), (xk, y2), dick=max(1, self.dick - 1))
        if name:
            self.text(x, y1 - 0.3, name, "s", fett=True)

    def kasten(self, x0, y0, x1, y1, titel="", farbe=None):
        """Gerät/IC als Rechteck mit Titel oben (z.B. µC, Last, geschütztes Gerät)."""
        (a, b), (c, d) = self.p(x0, y0), self.p(x1, y1)
        self.c.create_rectangle(a, b, c, d, outline=farbe or self.linie, width=self.dick, fill=self.bg)
        if titel:
            self.text((x0 + x1) / 2, y0 + 0.4, titel, "center", fett=True)

    def spule(self, x1, y1, x2, y2, name="", wert="", seite=None, laenge=1.6):
        """Spule (Induktivität) mit 4 Bögen zwischen zwei Rasterpunkten - waagrecht oder senkrecht."""
        senkrecht = abs(x2 - x1) < abs(y2 - y1)
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        l2, bogen = laenge / 2, laenge / 4
        if senkrecht:
            self.leitung((x1, y1), (x1, ym - l2))
            self.leitung((x1, ym + l2), (x2, y2))
        else:
            self.leitung((x1, y1), (xm - l2, y1))
            self.leitung((xm + l2, y1), (x2, y2))
        for k in range(4):
            start = -l2 + k * bogen
            punkte = []
            for n in range(13):
                winkel = math.pi * n / 12
                a, b = start + bogen / 2 * (1 - math.cos(winkel)), -0.3 * math.sin(winkel)   # Halbkreis
                punkte.append(self.p(xm - b, ym + a) if senkrecht else self.p(xm + a, ym + b))
            self.c.create_line(*[q for pk in punkte for q in pk], fill=self.linie, width=self.dick)
        if name or wert:
            seite = seite or ("rechts" if senkrecht else "oben")
            if senkrecht:
                self._beschriftung(xm + (0.5 if seite == "rechts" else -0.5), ym, name, wert, seite)
            else:
                self._beschriftung(xm, ym - 0.15, name, wert, seite)

    def opv(self, x, y, name="", plus_oben=False, versorgung=True):
        """
        Operationsverstärker als Dreieck (Spitze rechts), Mitte bei (x, y):
          Eingänge links bei (x − 1.2, y − 0.5) und (x − 1.2, y + 0.5), Ausgang rechts bei (x + 1.2, y)
          plus_oben=False: − oben, + unten (üblich bei invertierenden Schaltungen)
          versorgung:      kurze Striche oben/unten mit +U_B / −U_B (nur Hinweis, keine Leitung)
        Rückgabe: {"plus": (x, y), "minus": (x, y), "aus": (x, y)} - dort die Leitungen anschliessen.
        """
        a, b, c = self.p(x - 0.8, y - 1.0), self.p(x - 0.8, y + 1.0), self.p(x + 1.0, y)
        self.c.create_polygon(*a, *b, *c, outline=self.linie, fill=self.bg, width=self.dick)
        y_plus, y_minus = (y - 0.5, y + 0.5) if plus_oben else (y + 0.5, y - 0.5)
        for ye, zeichen in ((y_plus, "+"), (y_minus, "−")):
            self.leitung((x - 1.2, ye), (x - 0.8, ye))
            self.text(x - 0.52, ye, zeichen, "center", fett=True)
        self.leitung((x + 1.0, y), (x + 1.2, y))
        if versorgung:
            # Dreieckskante bei x: y ± (1.0 − (x + 0.8) / 1.8 · 1.0)  -> Strich bei x − 0.1
            kante = 1.0 - 0.7 / 1.8
            self.leitung((x - 0.1, y - kante), (x - 0.1, y - kante - 0.3))
            self.leitung((x - 0.1, y + kante), (x - 0.1, y + kante + 0.3))
            self.text(x + 0.05, y - kante - 0.3, "+U_B", "sw", klein=True, farbe=self.leise)
            self.text(x + 0.05, y + kante + 0.3, "−U_B", "nw", klein=True, farbe=self.leise)
        if name:
            self.text(x + 0.05, y, name, "center", klein=True, farbe=self.leise)
        return {"plus": (x - 1.2, y_plus), "minus": (x - 1.2, y_minus), "aus": (x + 1.2, y)}

    # ---- Zeitdiagramm ---------------------------------------------------------
    def diagramm(self, x0, y0, x1, y1, kurven, y_min, y_max, titel="", marken=(), zeit_text="t", einheit=None,
                 t_ende=None):
        """
        Kleines Zeitdiagramm im Rechteck (x0,y0)-(x1,y1), Raster-Einheiten.
          kurven  [(punkte, farbe, dick, gestrichelt), ...]   punkte = [(t 0…1, wert), ...]
          marken  [(wert, text), ...] waagrechte Hilfslinien mit Text links (z.B. Begrenzungspegel)
          einheit Einheiten-Typ der y-Achse ("spannung", "strom" …) -> Skalenwerte mit Einheit an der Achse
                  (nur dort, wo keine Marke steht). -> bauteile/grafiken/skala.py
          t_ende  Dauer der Zeitachse in s -> "t (0 … 40 ms)"
        Die Skala (y_min, y_max) wählt der Aufrufer aus dem Signal - so füllen auch mV- oder µA-Kurven das Bild.
        """
        if t_ende is not None and zeit_text == "t":
            zeit_text = f"t (0 … {wert_text(t_ende, 'zeit')})"
        def pixel(t, wert):
            anteil = (wert - y_min) / (y_max - y_min) if y_max > y_min else 0.5
            return self.p(x0 + t * (x1 - x0), y1 - min(max(anteil, -0.02), 1.02) * (y1 - y0))
        (a, b), (c, d) = self.p(x0, y0), self.p(x1, y1)
        self.c.create_line(a, b, a, d, fill=self.leise, width=1)
        null = pixel(0, 0)[1] if y_min < 0 < y_max else d
        self.c.create_line(a, null, c, null, fill=self.leise, width=1)
        self.text(x1, (null - self.y0) / self.u + 0.3, zeit_text, "e", klein=True, farbe=self.leise)
        belegt = []                                       # Texthöhen der Marken (nicht übereinander schreiben)
        for wert, text in marken:
            _, py = pixel(0, wert)
            self.c.create_line(a, py, c, py, fill=self.leise, width=1, dash=(3, 3))
            zeile = (py - self.y0) / self.u
            if all(abs(zeile - z) > 0.4 for z in belegt):
                self.text(x0 - 0.12, zeile, text, "e", klein=True, farbe=self.leise)
                belegt.append(zeile)
        if einheit:                                       # Skala: Endwerte (und 0) mit Einheit
            skala = [y_max, y_min] + ([0.0] if y_min < 0 < y_max else [])
            for wert in skala:
                zeile = (pixel(0, wert)[1] - self.y0) / self.u
                if all(abs(zeile - z) > 0.4 for z in belegt):
                    self.text(x0 - 0.12, zeile, wert_text(wert, einheit), "e", klein=True, farbe=self.leise)
                    belegt.append(zeile)
        for punkte, farbe, dick, gestrichelt in kurven:
            koordinaten = [k for t, wert in punkte for k in pixel(t, wert)]
            if len(koordinaten) >= 4:
                if gestrichelt:
                    self.c.create_line(*koordinaten, fill=farbe, width=dick or self.dick, dash=(5, 4))
                else:
                    self.c.create_line(*koordinaten, fill=farbe, width=dick or self.dick)
        if titel:
            self.text((x0 + x1) / 2, y0 - 0.35, titel, "center", klein=True, farbe=self.leise)

    # ---- Messgrössen ---------------------------------------------------------
    def messpunkt(self, x, y, name, seite="rechts"):
        """Messpunkt (z.B. M1): oranger Ring + Name."""
        px, py = self.p(x, y)
        r = max(5, self.u * 0.15)
        self.c.create_oval(px - r, py - r, px + r, py + r, outline=MESSPUNKT, width=self.dick + 1)
        dx = 0.28 if seite == "rechts" else -0.28
        self.text(x + dx, y - 0.28, name, "sw" if seite == "rechts" else "se", farbe=MESSPUNKT, fett=True)

    def spannung(self, x, y1, y2, text, seite="rechts", farbe=SPANNUNG):
        """Spannungspfeil senkrecht von y1 (+) nach y2 (−), Text daneben."""
        (px, a), (_, b) = self.p(x, y1), self.p(x, y2)
        self.c.create_line(px, a, px, b, fill=farbe, width=self.dick, arrow="last",
                           arrowshape=(self.u * 0.3, self.u * 0.34, self.u * 0.12))
        self.text(x + (0.2 if seite == "rechts" else -0.2), (y1 + y2) / 2, text,
                  "w" if seite == "rechts" else "e", farbe=farbe, fett=True)

    def strom(self, x1, y1, x2, y2, text, seite=None, farbe=STROM):
        """Strompfeil auf einer Leitung von (x1,y1) Richtung (x2,y2), Text daneben."""
        (a, b), (c, d) = self.p(x1, y1), self.p(x2, y2)
        self.c.create_line(a, b, c, d, fill=farbe, width=self.dick + 1, arrow="last",
                           arrowshape=(self.u * 0.3, self.u * 0.34, self.u * 0.13))
        senkrecht = abs(x2 - x1) < abs(y2 - y1)
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        if senkrecht:
            links = seite == "links"
            self.text(xm + (-0.25 if links else 0.25), ym, text, "e" if links else "w", farbe=farbe, fett=True)
        else:
            unten = seite == "unten"
            self.text(xm, ym + (0.4 if unten else -0.4), text, "center", farbe=farbe, fett=True)

    def messgeraet(self, x, y, zeichen, text="", seite="rechts"):
        """Messgerät als Kreis mit V / A / Ω, Wert daneben."""
        px, py = self.p(x, y)
        r = self.u * 0.42
        self.c.create_oval(px - r, py - r, px + r, py + r, outline=self.linie, width=self.dick, fill=self.bg)
        self.text(x, y, zeichen, "center", fett=True)
        if text:
            self.text(x + (0.6 if seite == "rechts" else -0.6), y, text, "w" if seite == "rechts" else "e",
                      farbe=SPANNUNG if zeichen == "V" else STROM, fett=True)


# =============================================================================
# GRUNDGERÜST EINER INTERAKTIVEN SCHALTUNG
# =============================================================================
class SchaltungsKarte(Karte):
    """
    Unterklassen legen fest:
      TITEL, UNTERTITEL     Kopf der Karte
      VARIANTEN             Liste für den Umschalter oben (leer = kein Umschalter)
      SCHALTER              [(schluessel, text), ...] Ein/Aus-Schalter neben dem Umschalter,
                            z.B. ("taster", "Taster gedrückt") -> w["taster"] ist True/False
      REGLER                [(schluessel, text, typ, von, bis, start, {optionen}), ...]
                            optionen: einheit, log, grenzen, ganzzahl, schritte (siehe WertRegler)
      RASTER                (spalten, zeilen) des Schaltplans
      sk_raster(breite)     (optional) anderes Raster bei schmaler Zeichenfläche, z.B. ohne Diagramm
      STARTWERTE            (optional) {variante: {regler: wert}} - beim Umschalten der Variante gesetzt,
                            z.B. Buck U_a < U_e, Boost U_a > U_e
      SEITENVERHAELTNIS     Höhe / Breite der Zeichenfläche
      ERKLAERUNG            Text unter der Grafik: Was zeigt sie physikalisch?
      sk_rechnen(w, v)      -> dict mit Ergebnissen  (w = Reglerwerte, v = Variante)
                               ValueError("Text") = verständliche Meldung statt Ergebnis
      sk_zeichnen(p, w, e, v)  zeichnet den Plan mit Schaltplan p
      sk_info(w, e, v)      -> (zeilen, farbe) für das Ergebnis unter der Grafik

    Eigene Attribute beginnen mit sk_ (keine Kollision mit tkinter).
    """

    TITEL = UNTERTITEL = ERKLAERUNG = ""
    VARIANTEN = []
    STARTWERTE = {}
    SCHALTER = []
    REGLER = []
    RASTER = (12, 8)
    SEITENVERHAELTNIS = 0.6
    MAX_HOEHE = 440

    def __init__(self, master):
        super().__init__(master, titel=self.TITEL, untertitel=self.UNTERTITEL)
        b = self.body
        zeile = 0
        self.sk_variante = None
        self.sk_schalter = {}
        if self.VARIANTEN or self.SCHALTER:
            oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
            oben.grid(row=zeile, column=0, sticky="w", pady=(0, 6))
            zeile += 1
            spalte = 0
            if self.VARIANTEN:
                self.sk_variante = ctk.CTkSegmentedButton(oben, values=self.VARIANTEN,
                                                          command=lambda _v: self.sk_neu())
                self.sk_variante.set(self.VARIANTEN[0])
                self.sk_variante.grid(row=0, column=0, sticky="w", padx=(0, 16), pady=2)
                spalte = 1
            for schluessel, text in self.SCHALTER:
                schalter = ctk.CTkSwitch(oben, text=text, command=self.sk_neu)
                schalter.grid(row=0, column=spalte, sticky="w", padx=(0, 16), pady=2)
                self.sk_schalter[schluessel] = schalter
                spalte += 1
        self.sk_canvas = ResponsiveCanvas(b, self._sk_zeichnen, seitenverhaeltnis=self.SEITENVERHAELTNIS,
                                          max_hoehe=self.MAX_HOEHE)
        self.sk_canvas.grid(row=zeile, column=0, sticky="ew")
        zeile += 1
        self.sk_regler = {}
        for schluessel, text, typ, von, bis, start, *opt in self.REGLER:
            regler = WertRegler(b, text, typ, von, bis, start, bei_aenderung=self.sk_neu, text_breite=150,
                                **(opt[0] if opt else {}))
            regler.grid(row=zeile, column=0, sticky="ew", pady=(4, 0))
            self.sk_regler[schluessel] = regler
            zeile += 1
        self.sk_ergebnis = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"), text_color=config.FARBEN["akzent"])
        self.sk_ergebnis.grid(row=zeile, column=0, sticky="ew", pady=(8, 0))
        WrapLabel(b, text=self.ERKLAERUNG, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"]).grid(
            row=zeile + 1, column=0, sticky="ew", pady=(8, 0))
        self.sk_groesse = (0, 0)
        self.sk_e = None
        self.sk_neu()

    def _sk_werte(self):
        """Alle Reglerwerte und Schalterstellungen: {"ue": 12.0, "taster": False, ...}"""
        werte = {k: r.wert() for k, r in self.sk_regler.items()}
        werte.update({k: bool(s.get()) for k, s in self.sk_schalter.items()})
        return werte

    def sk_v(self):
        return self.sk_variante.get() if self.sk_variante else None

    def sk_neu(self):
        """Nach jeder Änderung: neu rechnen, Text setzen, Plan neu zeichnen."""
        v = self.sk_v()
        if v != getattr(self, "sk_letzte_variante", v):                   # Variante gewechselt -> Startwerte
            for schluessel, wert in self.STARTWERTE.get(v, {}).items():
                self.sk_regler[schluessel].setzen(wert)
        self.sk_letzte_variante = v
        w = self._sk_werte()
        try:
            self.sk_e = self.sk_rechnen(w, self.sk_v())
            zeilen, farbe = self.sk_info(w, self.sk_e, self.sk_v())
            self.sk_ergebnis.configure(text="\n".join(zeilen), text_color=farbe)
        except ValueError as fehler:
            self.sk_e = None
            self.sk_ergebnis.configure(text=f"⚠ {fehler}", text_color=WARN)
        breite, hoehe = self.sk_groesse
        if breite > 1:
            self.sk_canvas.delete("all")
            self._sk_zeichnen(self.sk_canvas, breite, hoehe)

    def _sk_zeichnen(self, c, w, h):
        self.sk_groesse = (w, h)
        if self.sk_e is None:
            return
        werte = self._sk_werte()
        plan = Schaltplan(c, w, h, *self.sk_raster(w))
        self.sk_zeichnen(plan, werte, self.sk_e, self.sk_v())

    # ---- von Unterklassen zu füllen ----
    def sk_raster(self, breite):
        return self.RASTER

    def sk_rechnen(self, w, v):
        raise NotImplementedError

    def sk_zeichnen(self, p, w, e, v):
        raise NotImplementedError

    def sk_info(self, w, e, v):
        return [], config.FARBEN["akzent"]
