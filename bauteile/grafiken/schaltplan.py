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

import customtkinter as ctk

import config                                                            # -> config.py
from bauteile.grafiken.halbleiter_grafiken import (BLAU, GRUEN, ORANGE,  # -> grafiken/halbleiter_grafiken.py
                                                   ROT, _farbe)
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
            self.text(x, y - 0.2, name, anker, fett=True, farbe=farbe)
            if wert:
                self.text(x, y + 0.2, wert, anker, farbe=farbe or self.leise)
        else:
            dy = -1 if seite == "oben" else 1
            self.text(x, y + dy * 0.62, name, "center", fett=True, farbe=farbe)
            if wert:
                self.text(x, y + dy * 0.28 if seite == "oben" else y + 0.95, wert, "center",
                          farbe=farbe or self.leise)

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

    def quelle(self, x, y1, y2, name="", wert="", seite="links"):
        """Gleichspannungsquelle senkrecht von (x,y1) [+] nach (x,y2) [−] (Kreis mit Linie, IEC)."""
        ym, r = (y1 + y2) / 2, 0.45
        self.leitung((x, y1), (x, ym - r))
        self.leitung((x, ym + r), (x, y2))
        (ax, ay), (bx, by) = self.p(x - r, ym - r), self.p(x + r, ym + r)
        self.c.create_oval(ax, ay, bx, by, outline=self.linie, width=self.dick, fill=self.bg)
        self.leitung((x, ym - r), (x, ym + r))
        self.text(x + 0.3, ym - r - 0.05, "+", "sw", fett=True)
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
