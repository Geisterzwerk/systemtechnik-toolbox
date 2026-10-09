# =============================================================================
# bauteile/grafiken/svg_canvas.py
# -----------------------------------------------------------------------------
# SVG STATT FENSTER: dieselben Zeichenbefehle wie tk.Canvas (create_line, create_oval ...),
# aber das Ergebnis ist ein SVG-Text, den jeder Browser anzeigen kann.
# KEIN tkinter - läuft auch auf einem Webserver.
#
#   c = SvgCanvas(820, 490, dunkel=False)
#   c.create_line(10, 10, 200, 10, fill="#3B82F6", width=2, arrow="last")
#   c.create_text(100, 40, text="U = 5 V", font=("Segoe UI", 11, "bold"))
#   c.svg()                    -> '<svg xmlns=... >...</svg>'
#
#   schaltung_svg(SpannungsteilerSchaltung, {"ue": 12.0}, breite=820)
#       -> {"svg": "...", "zeilen": [...], "farbe": "#...", "fehler": None}
#   Eine interaktive Schaltung (SchaltungsModell) rechnen und als SVG zeichnen -
#   genau wie im Fenster, nur ohne Fenster.
#
# Farben dürfen auch Paare ('hell', 'dunkel') sein - gewählt wird nach "dunkel".
# Schriftgrösse: tk rechnet in Punkt, SVG in Pixel -> Pixel = Punkt · 4/3 (96 dpi).
#
# WER RUFT DAS AUF?  später die Webversion (web/), heute: python svg_test.py (siehe pruefen_svg.py)
# =============================================================================

import math
from xml.sax.saxutils import escape

import config                                                            # -> config.py
from bauteile.grafiken.schaltplan import Schaltplan, farbe_waehlen       # -> grafiken/schaltplan.py

PT_ZU_PX = 4 / 3

# tk-Anker -> (text-anchor, dominant-baseline) in SVG
ANKER = {"center": ("middle", "central"), "w": ("start", "central"), "e": ("end", "central"),
         "n": ("middle", "text-before-edge"), "s": ("middle", "text-after-edge"),
         "nw": ("start", "text-before-edge"), "ne": ("end", "text-before-edge"),
         "sw": ("start", "text-after-edge"), "se": ("end", "text-after-edge")}


def _zahl(x):
    """Kurze Zahlen im SVG: 12.0 -> '12', 3.14159 -> '3.14'"""
    return f"{x:.2f}".rstrip("0").rstrip(".")


class SvgCanvas:
    """Sammelt Zeichenbefehle wie ein tk.Canvas und gibt sie mit svg() als SVG-Text aus."""

    def __init__(self, breite, hoehe, dunkel=False, hintergrund=None):
        self.breite, self.hoehe = breite, hoehe
        self.dunkel = dunkel                          # Schaltplan liest das (ist_dunkel)
        self.hintergrund = farbe_waehlen(hintergrund or config.FARBEN["flaeche"], dunkel)
        self.teile = []

    # ---- Hilfen -----------------------------------------------------------------
    def _farbe(self, farbe):
        """'' oder None -> 'none' (wie tk: leer = nicht füllen)"""
        farbe = farbe_waehlen(farbe, self.dunkel)
        return farbe if farbe else "none"

    def _strich(self, farbe, breite, dash=None):
        teile = [f'stroke="{self._farbe(farbe)}"', f'stroke-width="{_zahl(float(breite))}"']
        if dash:
            teile.append(f'stroke-dasharray="{" ".join(_zahl(float(d)) for d in dash)}"')
        return " ".join(teile)

    def _pfeil(self, x0, y0, x1, y1, farbe, form):
        """Pfeilspitze bei (x1, y1) wie tk: form = (Länge, Länge bis Flügel, Breite)."""
        laenge, _, halb = form
        winkel = math.atan2(y1 - y0, x1 - x0)
        c, s = math.cos(winkel), math.sin(winkel)
        punkte = [(x1, y1), (x1 - laenge * c + halb * s, y1 - laenge * s - halb * c),
                  (x1 - laenge * c - halb * s, y1 - laenge * s + halb * c)]
        self.teile.append(f'<polygon points="{" ".join(f"{_zahl(x)},{_zahl(y)}" for x, y in punkte)}" '
                          f'fill="{self._farbe(farbe)}"/>')

    # ---- wie tk.Canvas ----------------------------------------------------------
    def create_line(self, *koordinaten, fill="black", width=1, arrow=None, arrowshape=(8, 10, 3), dash=None,
                    smooth=False, capstyle="butt", joinstyle="round", **_rest):
        if len(koordinaten) == 1:                    # create_line([x0, y0, x1, y1]) ist bei tk auch erlaubt
            koordinaten = tuple(koordinaten[0])
        z = [float(k) for k in koordinaten]
        punkte = list(zip(z[::2], z[1::2]))
        if smooth and len(punkte) > 2:               # tk glättet mit Splines - hier: Kurve durch die Mitten
            d = f"M{_zahl(punkte[0][0])},{_zahl(punkte[0][1])}"
            for (xa, ya), (xb, yb) in zip(punkte[1:-1], punkte[2:]):
                d += f" Q{_zahl(xa)},{_zahl(ya)} {_zahl((xa + xb) / 2)},{_zahl((ya + yb) / 2)}"
            d += f" L{_zahl(punkte[-1][0])},{_zahl(punkte[-1][1])}"
            form = f'<path d="{d}"'
        else:
            form = f'<polyline points="{" ".join(f"{_zahl(x)},{_zahl(y)}" for x, y in punkte)}"'
        ende = {"round": "round", "projecting": "square"}.get(capstyle, "butt")
        self.teile.append(f'{form} fill="none" {self._strich(fill, width, dash)} '
                          f'stroke-linecap="{ende}" stroke-linejoin="{joinstyle}"/>')
        if arrow in ("last", "both"):
            self._pfeil(*punkte[-2], *punkte[-1], fill, arrowshape)
        if arrow in ("first", "both"):
            self._pfeil(*punkte[1], *punkte[0], fill, arrowshape)

    def create_polygon(self, *koordinaten, fill="black", outline="", width=1, **_rest):
        if len(koordinaten) == 1:
            koordinaten = tuple(koordinaten[0])
        z = [float(k) for k in koordinaten]
        punkte = " ".join(f"{_zahl(x)},{_zahl(y)}" for x, y in zip(z[::2], z[1::2]))
        self.teile.append(f'<polygon points="{punkte}" fill="{self._farbe(fill)}" {self._strich(outline, width)}/>')

    def create_rectangle(self, x0, y0, x1, y1, fill="", outline="black", width=1, dash=None, **_rest):
        x, y = min(x0, x1), min(y0, y1)
        self.teile.append(f'<rect x="{_zahl(x)}" y="{_zahl(y)}" width="{_zahl(abs(x1 - x0))}" '
                          f'height="{_zahl(abs(y1 - y0))}" fill="{self._farbe(fill)}" '
                          f'{self._strich(outline, width, dash)}/>')

    def create_oval(self, x0, y0, x1, y1, fill="", outline="black", width=1, dash=None, **_rest):
        self.teile.append(f'<ellipse cx="{_zahl((x0 + x1) / 2)}" cy="{_zahl((y0 + y1) / 2)}" '
                          f'rx="{_zahl(abs(x1 - x0) / 2)}" ry="{_zahl(abs(y1 - y0) / 2)}" '
                          f'fill="{self._farbe(fill)}" {self._strich(outline, width, dash)}/>')

    def create_arc(self, x0, y0, x1, y1, start=0, extent=90, outline="black", width=1, style="arc", fill="", **_rest):
        """Bogen wie tk: Winkel in Grad, 0° = rechts, positiv = gegen den Uhrzeigersinn."""
        cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, abs(x1 - x0) / 2, abs(y1 - y0) / 2
        a, b = math.radians(start), math.radians(start + extent)
        xa, ya = cx + rx * math.cos(a), cy - ry * math.sin(a)
        xb, yb = cx + rx * math.cos(b), cy - ry * math.sin(b)
        gross = 1 if abs(extent) > 180 else 0
        richtung = 0 if extent > 0 else 1
        d = f"M{_zahl(xa)},{_zahl(ya)} A{_zahl(rx)},{_zahl(ry)} 0 {gross} {richtung} {_zahl(xb)},{_zahl(yb)}"
        fuellung = "none"
        if style == "pieslice":
            d += f" L{_zahl(cx)},{_zahl(cy)} Z"
            fuellung = self._farbe(fill)
        self.teile.append(f'<path d="{d}" fill="{fuellung}" {self._strich(outline, width)}/>')

    def create_text(self, x, y, text="", fill="black", font=None, anchor="center", **_rest):
        familie, groesse, *art = font or (config.SCHRIFT, 10)
        h_anker, v_anker = ANKER.get(anchor, ANKER["center"])
        fett = ' font-weight="bold"' if "bold" in art else ""
        zeilen = str(text).split("\n")
        hoehe = abs(groesse) * PT_ZU_PX * 1.25
        # mehrzeiliger Text: Block wie bei tk um den Anker herum verteilen
        if v_anker == "central":
            start = y - hoehe * (len(zeilen) - 1) / 2
        elif v_anker == "text-after-edge":
            start = y - hoehe * (len(zeilen) - 1)
        else:
            start = y
        for i, zeile in enumerate(zeilen):
            self.teile.append(f'<text x="{_zahl(x)}" y="{_zahl(start + i * hoehe)}" fill="{self._farbe(fill)}" '
                              f'font-family="{escape(familie)}, sans-serif" font-size="{_zahl(abs(groesse) * PT_ZU_PX)}"'
                              f'{fett} text-anchor="{h_anker}" dominant-baseline="{v_anker}">{escape(zeile)}</text>')

    def delete(self, *_alles):
        self.teile = []

    # ---- Ausgabe ----------------------------------------------------------------
    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.breite} {self.hoehe}" '
                f'width="{self.breite}" height="{self.hoehe}" role="img">'
                f'<rect width="100%" height="100%" fill="{self.hintergrund}"/>'
                + "".join(self.teile) + "</svg>")


# =============================================================================
# INTERAKTIVE SCHALTUNG ALS SVG
# =============================================================================
def schaltung_svg(modell_klasse, werte=None, variante=None, breite=820, dunkel=False):
    """
    modell_klasse  eine SchaltungsModell-Unterklasse (z.B. SpannungsteilerSchaltung)
    werte          {"ue": 12.0, ...} - fehlende Regler bekommen ihren Startwert
    variante       Text aus VARIANTEN (None = erste)
    Rückgabe: {"svg": Text, "zeilen": [...], "farbe": "#…", "fehler": None oder Meldung}
    """
    modell = modell_klasse()
    if variante is None and modell.VARIANTEN:
        variante = modell.VARIANTEN[0]
    if modell.VARIANTEN and variante not in modell.VARIANTEN:
        raise ValueError(f"Variante „{variante}“ gibt es nicht ({', '.join(modell.VARIANTEN)})")
    w = modell.startwerte(variante)
    w.update(werte or {})
    hoehe = min(int(breite * modell.SEITENVERHAELTNIS), modell.MAX_HOEHE)
    c = SvgCanvas(breite, hoehe, dunkel)
    try:
        e = modell.sk_rechnen(w, variante)
    except ValueError as fehler:                     # verständliche Meldung statt Ergebnis
        return {"svg": c.svg(), "zeilen": [], "farbe": None, "fehler": str(fehler)}
    zeilen, farbe = modell.sk_info(w, e, variante)
    modell.sk_zeichnen(Schaltplan(c, breite, hoehe, *modell.sk_raster(breite)), w, e, variante)
    return {"svg": c.svg(), "zeilen": list(zeilen), "farbe": farbe_waehlen(farbe, dunkel), "fehler": None}
