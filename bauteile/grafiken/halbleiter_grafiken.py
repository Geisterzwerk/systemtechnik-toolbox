# =============================================================================
# bauteile/grafiken/halbleiter_grafiken.py
# -----------------------------------------------------------------------------
# INTERAKTIVE GRAFIK für Dioden (Etappe 3) + gemeinsame Farben/Hilfsfunktionen.
#
#   DiodenKennlinie      Kennlinie I(U) + Arbeitsgerade von Ub und R.
#                        Z-Dioden: VOLLE Kennlinie mit Durchlass (+0.7 V) und
#                        Z-Durchbruch bei −Uz; Arbeitsgerade im 3. Quadranten.
#                        Der Schnittpunkt ist der Arbeitspunkt ("Arbeiten mit
#                        Kennlinien", vgl. Zastrow Kap. 2).
#
#   Transistor-/MOSFET-Schalter (getrennt): bauteile/grafiken/schalter_simulator.py
#   Schaltzeichen (Diode, LED, Bipolartransistor, MOSFET): bauteile/grafiken/symbole.py
#
# REGEL gegen Hänger: Es wird nur gezeichnet, wenn sich die Grösse ändert
# (core/layout.py ResponsiveCanvas) oder ein Regler bewegt wird. Keine
# Endlosschleifen, keine Animation mit after().
# Alle eigenen Namen beginnen mit dk_ (keine Kollision mit tkinter).
# =============================================================================

import math

import customtkinter as ctk

import config                                                    # -> config.py
from bauteile.einheiten import formatieren as fmt                # -> bauteile/einheiten.py
from bauteile.rechner.basis import WertRegler                    # -> bauteile/rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel       # -> core/layout.py

BLAU = "#3B82F6"
ORANGE = "#F59E0B"
GRUEN = "#22C55E"
ROT = "#EF4444"
GRAU = "#6B7280"


def _farbe(paar):
    """('hell', 'dunkel') -> Farbe passend zum aktuellen Modus."""
    return paar[1] if ctk.get_appearance_mode() == "Dark" else paar[0]


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


def ist_z(typ):
    return DIODEN[typ].get("z", False)
I_REF = 0.010


def _strom(u, typ):
    d = DIODEN[typ]
    exponent = (u - d["u"]) / d["m"]
    return I_REF * math.exp(min(exponent, 50))


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


class DiodenKennlinie(Karte):

    def __init__(self, master, start_typ=None):
        super().__init__(master, titel="📈 Kennlinie & Arbeitspunkt (interaktiv)",
                         untertitel="Die Diode stellt sich dort ein, wo Kennlinie und Arbeitsgerade sich schneiden")
        b = self.body
        self.dk_groesse = (0, 0)
        self.dk_canvas = None
        self.dk_regler = {}

        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(oben, text="Bauteil", anchor="w").grid(row=0, column=0, padx=(0, 8))
        self.dk_typ = ctk.CTkOptionMenu(oben, values=list(DIODEN), width=240, dynamic_resizing=False,
                                        command=lambda _v: self.dk_neu())
        self.dk_typ.set(start_typ if start_typ in DIODEN else list(DIODEN)[0])
        self.dk_typ.grid(row=0, column=1)

        self.dk_regler = {}
        regler = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        regler.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        regler.grid_columnconfigure(0, weight=1)
        # Slider + Zahlenfeld + Einheit -> bauteile/rechner/basis.py WertRegler
        self.dk_regler = {
            "ub": WertRegler(regler, "Versorgung Ub", "spannung", 0.5, 12.0, 5.0, einheit="V", grenzen=(0.1, 50),
                             bei_aenderung=self.dk_neu, text_breite=130),
            "r": WertRegler(regler, "Vorwiderstand R", "widerstand", 10, 2000, 330, einheit="Ω",
                            grenzen=(1, 1e6), bei_aenderung=self.dk_neu, text_breite=130),
        }
        for zeile, eintrag in enumerate(self.dk_regler.values()):
            eintrag.grid(row=zeile, column=0, sticky="ew")

        self.dk_canvas = ResponsiveCanvas(b, self._dk_zeichnen, seitenverhaeltnis=0.5, max_hoehe=380)
        self.dk_canvas.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.dk_info = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"), text_color=config.FARBEN["akzent"])
        self.dk_info.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        self.dk_neu()

    def _dk_werte(self):
        ub = self.dk_regler["ub"].wert()
        r = self.dk_regler["r"].wert()
        return ub, r, self.dk_typ.get()

    def dk_neu(self):
        ub, r, typ = self._dk_werte()
        u, i = arbeitspunkt(ub, r, typ)
        if ist_z(typ):
            uz = DIODEN[typ]["u"]
            if i < 1e-7:                               # praktisch kein Strom -> nicht "1e-14 A" anzeigen
                i, u = 0.0, ub
            minus = "−" if i > 0 else ""
            zeilen = [f"Arbeitspunkt (Kennlinie): U_AK = −{fmt(u, 'spannung')}   I_AK = {minus}{fmt(i, 'strom')}",
                      f"In der Schaltung (Kathode an +, gegen Masse gemessen): U_Z = +{fmt(u, 'spannung')}   "
                      f"I_Z = {fmt(i, 'strom')}   P_Z = {fmt(u * i, 'leistung')}",
                      f"Am Vorwiderstand: {fmt(ub - u, 'spannung')}"]
            if ub < uz * 0.97:
                zeilen.append(f"Ue liegt unter Uz = {fmt(uz, 'spannung')} → Z-Diode sperrt noch, sie stabilisiert NICHT")
            else:
                zeilen.append("Die Spannung bleibt fast bei Uz, auch wenn Ue oder R sich ändern → Stabilisierung")
            self.dk_info.configure(text="\n".join(zeilen))
            self._dk_neu_zeichnen()
            return
        zeilen = [f"Arbeitspunkt: U_D = {fmt(u, 'spannung')}   I = {fmt(i, 'strom')}   "
                  f"P_D = {fmt(u * i, 'leistung')}",
                  f"Am Widerstand: {fmt(ub - u, 'spannung')}   P_R = {fmt((ub - u) * i, 'leistung')}"]
        if ub < DIODEN[typ]["u"] * 0.9:
            zeilen.append("Ub liegt unter der Schwellspannung → es fliesst fast kein Strom")
        self.dk_info.configure(text="\n".join(zeilen))
        self._dk_neu_zeichnen()

    def _dk_neu_zeichnen(self):
        w, h = self.dk_groesse
        if self.dk_canvas is not None and w > 1:
            self.dk_canvas.delete("all")
            self._dk_zeichnen(self.dk_canvas, w, h)

    def _dk_zeichnen(self, c, w, h):
        self.dk_groesse = (w, h)
        if len(self.dk_regler) < 2:
            return
        ub, r, typ = self._dk_werte()
        if ist_z(typ):
            self._dk_zeichnen_z(c, w, h, ub, r, typ)
            return
        u_ap, i_ap = arbeitspunkt(ub, r, typ)
        d = DIODEN[typ]
        text = _farbe(config.FARBEN["text_leise"])
        linie = _farbe(config.FARBEN["rahmen"])
        schrift = (config.SCHRIFT, max(8, int(h / 26)))
        links, rechts, oben, unten = 0.12 * w, 0.96 * w, 0.08 * h, 0.84 * h

        # Achsenbereich: bis etwas über die Schwellspannung bzw. Ub
        u_max = max(d["u"] * 1.5, min(ub, d["u"] * 3), 1.0)
        i_max = max(ub / r, i_ap * 1.3, 0.005) * 1.1

        def x(u):
            return links + (rechts - links) * u / u_max

        def y(i):
            return unten - (unten - oben) * i / i_max

        for k in range(1, 5):                                    # Raster
            c.create_line(x(u_max * k / 4), oben, x(u_max * k / 4), unten, fill=linie, dash=(2, 4))
            c.create_text(x(u_max * k / 4), unten + 0.06 * h, text=fmt(u_max * k / 4, "spannung", 2), fill=text, font=schrift)
            c.create_line(links, y(i_max * k / 4), rechts, y(i_max * k / 4), fill=linie, dash=(2, 4))
            c.create_text(links - 4, y(i_max * k / 4), anchor="e", text=fmt(i_max * k / 4, "strom", 2), fill=text, font=schrift)
        c.create_line(links, unten, rechts, unten, fill=text, width=2, arrow="last")
        c.create_line(links, unten, links, oben - 0.03 * h, fill=text, width=2, arrow="last")
        c.create_text(rechts, unten - 0.04 * h, anchor="e", text="U_D", fill=text, font=schrift)
        c.create_text(links + 6, oben, anchor="w", text="I", fill=text, font=schrift)

        # Kennlinie (nur so weit, wie sie im Bild bleibt)
        punkte = []
        for n in range(161):
            u = u_max * n / 160
            i = _strom(u, typ)
            if i > i_max:
                punkte += [x(u), y(i_max)]
                break
            punkte += [x(u), y(i)]
        if len(punkte) >= 4:
            c.create_line(*punkte, fill=d["farbe"], width=3)

        # Arbeitsgerade von (0 | Ub/R) nach (Ub | 0), auf den sichtbaren Bereich zugeschnitten
        u_start = max(0.0, ub - i_max * r)
        u_ende = min(ub, u_max)
        if u_ende > u_start:
            c.create_line(x(u_start), y((ub - u_start) / r), x(u_ende), y((ub - u_ende) / r),
                          fill=ORANGE, width=2, dash=(6, 4))
            c.create_text(x(u_start) + 6, y((ub - u_start) / r) - 8, anchor="w", fill=ORANGE, font=schrift,
                          text=f"Arbeitsgerade  (Ub = {fmt(ub, 'spannung', 3)}, R = {fmt(r, 'widerstand', 3)})")

        # Arbeitspunkt
        if u_ap <= u_max and i_ap <= i_max:
            px, py = x(u_ap), y(i_ap)
            c.create_line(px, py, px, unten, fill=GRUEN, dash=(2, 3))
            c.create_line(links, py, px, py, fill=GRUEN, dash=(2, 3))
            c.create_oval(px - 7, py - 7, px + 7, py + 7, fill=GRUEN, outline="white", width=2)
            c.create_text(px + 10, py - 12, anchor="w", text="Arbeitspunkt", fill=GRUEN, font=schrift)

    def _dk_zeichnen_z(self, c, w, h, ub, r, typ):
        """
        Volle Z-Dioden-Kennlinie mit Achsenkreuz im Ursprung:
          rechts oben (1. Quadrant): Durchlassbereich bei ca. +0.7 V
          links unten (3. Quadrant): Z-Durchbruch bei U_AK = −Uz
        Arbeitsgerade der Stabilisierungsschaltung (Ue, Rv) im 3. Quadranten:
          von (0 | −Ue/Rv) nach (−Ue | 0).
        """
        d = DIODEN[typ]
        uz = d["u"]
        text = _farbe(config.FARBEN["text_leise"])
        linie = _farbe(config.FARBEN["rahmen"])
        schrift = (config.SCHRIFT, max(8, int(h / 26)))
        klein = (config.SCHRIFT, max(7, int(h / 32)))
        links, rechts, oben, unten = 0.06 * w, 0.96 * w, 0.07 * h, 0.90 * h

        # Wertebereich: links bis über Uz bzw. Ue hinaus, rechts bis 1.2 V
        u_min = -max(uz * 1.3, ub * 1.08, 2.0)
        u_max = 1.2
        i_unten = -max(ub / r, 0.005) * 1.15            # Sperrbereich (negativ)
        i_oben = -i_unten * 0.55                        # Durchlassbereich (kleiner dargestellt)

        def x(u):
            return links + (rechts - links) * (u - u_min) / (u_max - u_min)

        def y(i):
            return oben + (unten - oben) * (i_oben - i) / (i_oben - i_unten)

        # ---- Raster + Beschriftung ----
        schritt = 1.0 if -u_min <= 8 else 2.0
        k = -schritt
        while k > u_min:
            c.create_line(x(k), oben, x(k), unten, fill=linie, dash=(2, 4))
            c.create_text(x(k), y(0) + 0.045 * h, text=f"{k:g} V", fill=text, font=klein)
            k -= schritt
        for anteil in (0.5, 1.0):
            iy = i_unten * anteil
            c.create_line(links, y(iy), rechts, y(iy), fill=linie, dash=(2, 4))
            c.create_text(x(0) + 4, y(iy), anchor="w", text=f"−{fmt(-iy, 'strom', 2)}", fill=text, font=klein)

        # ---- Achsenkreuz im Ursprung ----
        c.create_line(links, y(0), rechts, y(0), fill=text, width=2, arrow="last")
        c.create_line(x(0), unten, x(0), oben - 0.02 * h, fill=text, width=2, arrow="last")
        c.create_text(rechts, y(0) - 0.04 * h, anchor="e", text="U_AK", fill=text, font=schrift)
        c.create_text(x(0) + 6, oben, anchor="w", text="I_AK", fill=text, font=schrift)

        # ---- Bereichsbeschriftungen ----
        c.create_text(x(0.6), oben + 0.03 * h, text="Durchlass", fill=text, font=klein)
        c.create_text(x(-uz / 2), y(0) - 0.05 * h, text="Sperrbereich (fast kein Strom)", fill=text, font=klein)
        c.create_line(x(-uz), oben, x(-uz), unten, fill=d["farbe"], dash=(4, 3))
        c.create_text(x(-uz) - 4, oben + 0.03 * h, anchor="e", fill=d["farbe"], font=schrift,
                      text=f"−Uz = −{fmt(uz, 'spannung', 3)}")
        c.create_text(x(-uz) - 4, y(i_unten * 0.75), anchor="e", fill=d["farbe"], font=klein,
                      text="Z-Durchbruch\n(hier arbeitet sie)")

        # ---- Kennlinie: Durchlassbereich (wie Si-Diode) ----
        punkte = []
        for n in range(61):
            u = u_max * n / 60
            i = I_REF * math.exp(min((u - SI_VORWAERTS["u"]) / SI_VORWAERTS["m"], 50))
            if i > i_oben:
                punkte += [x(u), y(i_oben)]
                break
            punkte += [x(u), y(i)]
        if len(punkte) >= 4:
            c.create_line(*punkte, fill=d["farbe"], width=3)

        # ---- Kennlinie: Sperr- und Durchbruchbereich (gespiegelt) ----
        punkte = []
        for n in range(201):
            u = u_min * n / 200                         # 0 ... u_min (negativ)
            i = -_strom(-u, typ)                        # Durchbruch-Modell, gespiegelt
            if i < i_unten:
                punkte += [x(u), y(i_unten)]
                break
            punkte += [x(u), y(i)]
        if len(punkte) >= 4:
            c.create_line(*punkte, fill=d["farbe"], width=3)

        # ---- Arbeitsgerade im 3. Quadranten: (0 | −Ue/Rv) bis (−Ue | 0) ----
        c.create_line(x(0), y(-ub / r), x(-ub), y(0), fill=ORANGE, width=2, dash=(6, 4))
        c.create_text(x(-ub) + 6, y(0) + 0.09 * h, anchor="w", fill=ORANGE, font=klein,
                      text=f"Arbeitsgerade (Ue = {fmt(ub, 'spannung', 3)}, Rv = {fmt(r, 'widerstand', 3)})")

        # ---- Arbeitspunkt (gespiegelt) ----
        u_ap, i_ap = arbeitspunkt(ub, r, typ)
        px, py = x(-u_ap), y(-i_ap)
        c.create_line(px, py, px, y(0), fill=GRUEN, dash=(2, 3))
        c.create_line(x(0), py, px, py, fill=GRUEN, dash=(2, 3))
        c.create_oval(px - 7, py - 7, px + 7, py + 7, fill=GRUEN, outline="white", width=2)
        c.create_text(px + 10, py + 14, anchor="w", text="Arbeitspunkt", fill=GRUEN, font=schrift)

        # ---- Hinweis Schaltungssicht ----
        c.create_text(links, unten, anchor="sw", fill=text, font=klein,
                      text="In der Schaltung ist die Kathode an Plus → gemessen wird +Uz")
