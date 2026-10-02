# =============================================================================
# bauteile/grafiken/halbleiter_grafiken.py
# -----------------------------------------------------------------------------
# INTERAKTIVE GRAFIKEN + SCHALTZEICHEN für Dioden und Transistoren (Etappe 3).
#
#   DiodenKennlinie      Kennlinie I(U) + Arbeitsgerade von Ub und R.
#                        Z-Dioden: VOLLE Kennlinie mit Durchlass (+0.7 V) und
#                        Z-Durchbruch bei −Uz; Arbeitsgerade im 3. Quadranten.
#                        Der Schnittpunkt ist der Arbeitspunkt ("Arbeiten mit
#                        Kennlinien", vgl. Zastrow Kap. 2).
#   TransistorSchalter   Transistor als Schalter: Ansteuerspannung am Regler,
#                        Lampe leuchtet, Zustand (sperrt / aktiv / gesättigt)
#                        wird farbig angezeigt. Umschaltbar NPN <-> N-MOSFET.
#
#   Schaltzeichen: werden am Ende in bauteile/grafiken/symbole.py -> SYMBOLE
#   eingetragen (symbole.py selbst muss dafür NICHT geändert werden).
#
# REGEL gegen Hänger: Es wird nur gezeichnet, wenn sich die Grösse ändert
# (core/layout.py ResponsiveCanvas) oder ein Regler bewegt wird. Keine
# Endlosschleifen, keine Animation mit after().
# Alle eigenen Namen beginnen mit dk_ / ts_ (keine Kollision mit tkinter).
# =============================================================================

import math

import customtkinter as ctk

import config                                                    # -> config.py
from bauteile.einheiten import formatieren as fmt                # -> bauteile/einheiten.py
from bauteile.grafiken.symbole import SYMBOLE, _beschriftung     # -> bauteile/grafiken/symbole.py
from bauteile.rechner.basis import EinheitenEingabe, WertRegler  # -> bauteile/rechner/basis.py
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



# =============================================================================
# 2) TRANSISTOR ALS SCHALTER (NPN / N-MOSFET)
# =============================================================================
class TransistorSchalter(Karte):
    """
    Schaltung:    +Ub ── Lampe (RL) ── C/D ── Transistor ── E/S ── GND
                  Ue ── Rb ── B/G   (beim MOSFET direkt ans Gate)
    """

    def __init__(self, master, modus="NPN"):
        super().__init__(master, titel="🔌 Transistor als Schalter (interaktiv)",
                         untertitel="Ansteuerspannung am Regler erhöhen und beobachten, wann die Lampe voll leuchtet")
        b = self.body
        self.ts_groesse = (0, 0)
        self.ts_canvas = None
        self.ts_ue = None                  # Regler existiert erst weiter unten
        self.ts_felder = {}

        self.ts_modus = ctk.CTkSegmentedButton(b, values=["NPN-Transistor", "N-MOSFET"],
                                               command=lambda _v: self._ts_modus_geaendert())
        self.ts_modus.set("N-MOSFET" if modus == "MOSFET" else "NPN-Transistor")
        self.ts_modus.grid(row=0, column=0, sticky="w")

        # ---- Parameter (Enter = übernehmen) ----
        self.ts_param_rahmen = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        self.ts_param_rahmen.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.ts_felder = {}

        # ---- Zeichnung ----
        self.ts_canvas = ResponsiveCanvas(b, self._ts_zeichnen, seitenverhaeltnis=0.55, max_hoehe=400)
        self.ts_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        # ---- Regler für die Ansteuerspannung ----
        regler = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        regler.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        regler.grid_columnconfigure(0, weight=1)
        # Slider + Zahlenfeld + Einheit -> bauteile/rechner/basis.py WertRegler
        self.ts_ue = WertRegler(regler, "Ansteuerspannung Ue", "spannung", 0, 12, 0, einheit="V", grenzen=(0, 30),
                                schritte=240, bei_aenderung=self.ts_neu)
        self.ts_ue.grid(row=0, column=0, sticky="ew")

        self.ts_info = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"), text_color=config.FARBEN["akzent"])
        self.ts_info.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self._ts_modus_geaendert()

    # -------------------------------------------------------------------------
    def _ts_ist_mosfet(self):
        return self.ts_modus.get() == "N-MOSFET"

    def _ts_modus_geaendert(self):
        for kind in self.ts_param_rahmen.winfo_children():
            kind.destroy()
        if self._ts_ist_mosfet():
            felder = [("Ub", "Ub", "spannung", "V", "12"), ("RL", "Lampe RL", "widerstand", "Ω", "24"),
                      ("Uth", "Ugs(th)", "spannung", "V", "2"), ("Rds", "Rds(on)", "widerstand", "mΩ", "50")]
        else:
            felder = [("Ub", "Ub", "spannung", "V", "12"), ("RL", "Lampe RL", "widerstand", "Ω", "24"),
                      ("Rb", "Rb", "widerstand", "kΩ", "1"), ("beta", "β", "zahl", "", "100")]
        self.ts_felder = {}
        for spalte, (name, text, typ, einheit, start) in enumerate(felder):
            ctk.CTkLabel(self.ts_param_rahmen, text=text, anchor="w").grid(
                row=spalte // 2, column=(spalte % 2) * 2, sticky="w", padx=(0 if spalte % 2 == 0 else 14, 6), pady=2)
            feld = EinheitenEingabe(self.ts_param_rahmen, typ, "", einheit or None, breite=70)
            feld.ee_feld.insert(0, start)
            feld.grid(row=spalte // 2, column=(spalte % 2) * 2 + 1, sticky="w", pady=2)
            feld.bei_enter(self.ts_neu)
            self.ts_felder[name] = feld
        self.ts_neu()

    def _ts_param(self, name, standard):
        try:
            wert = self.ts_felder[name].wert()
        except (ValueError, KeyError):
            return standard
        return standard if wert is None or wert <= 0 else wert

    # -------------------------------------------------------------------------
    def ts_berechnen(self):
        """Gibt ein Dictionary mit allen Werten des aktuellen Zustands zurück."""
        ue = self.ts_ue.wert()
        ub = self._ts_param("Ub", 12.0)
        rl = self._ts_param("RL", 24.0)
        i_max = ub / rl                                          # Strom bei ideal geschlossenem Schalter
        if self._ts_ist_mosfet():
            uth = self._ts_param("Uth", 2.0)
            rds = self._ts_param("Rds", 0.05)
            k = 0.5                                              # Steilheit in A/V² (vereinfacht)
            if ue <= uth:
                i, zustand = 0.0, "sperrt"
            else:
                i_kanal = k * (ue - uth) ** 2                    # was der Kanal bei dieser Ugs zulässt
                i_voll = ub / (rl + rds)                         # was die Last zulässt
                if i_kanal < i_voll * 0.97:
                    i, zustand = i_kanal, "linear"
                else:
                    i, zustand = i_voll, "voll"
            u_t = ub - i * rl
            i_steuer = 0.0
        else:
            rb = self._ts_param("Rb", 1000.0)
            beta = self._ts_param("beta", 100.0)
            ib = max(0.0, (ue - 0.7) / rb)
            ic_aktiv = beta * ib
            ic_sat = max(0.0, (ub - 0.2) / rl)
            if ib <= 0:
                i, zustand = 0.0, "sperrt"
            elif ic_aktiv < ic_sat:
                i, zustand = ic_aktiv, "linear"
            else:
                i, zustand = ic_sat, "voll"
            u_t = ub - i * rl
            i_steuer = ib
        return {"ue": ue, "ub": ub, "rl": rl, "i": i, "u_t": u_t, "zustand": zustand,
                "p_t": u_t * i, "p_last": i * i * rl, "p_max": i_max * i_max * rl, "i_steuer": i_steuer}

    def ts_neu(self):
        if self.ts_ue is None:
            return
        z = self.ts_berechnen()
        mosfet = self._ts_ist_mosfet()
        texte = {
            "sperrt": ("SPERRT – Schalter offen", "Ugs unter der Schwellspannung" if mosfet else "Ube < 0.7 V → kein Basisstrom"),
            "linear": ("TEILWEISE LEITEND – Verstärkerbereich",
                       "⚠ Transistor wird heiss! Als Schalter immer voll ein- oder ausschalten"),
            "voll": ("VOLL DURCHGESCHALTET – Schalter zu",
                     "Rds(on) klein → kaum Verlust" if mosfet else "Gesättigt: Uce ≈ 0.2 V, Ib reicht aus"),
        }
        titel, hinweis = texte[z["zustand"]]
        zeilen = [f"{titel}",
                  f"Strom {fmt(z['i'], 'strom')}   ·   Spannung am Transistor {fmt(z['u_t'], 'spannung')}   ·   "
                  f"Verlust im Transistor {fmt(z['p_t'], 'leistung')}",
                  hinweis]
        if not mosfet and z["i_steuer"] > 0:
            zeilen.append(f"Basisstrom Ib = {fmt(z['i_steuer'], 'strom')}  (muss die Ansteuerung liefern)")
        if mosfet:
            zeilen.append("Gate braucht (statisch) keinen Strom – nur beim Umladen der Gate-Kapazität")
        self.ts_info.configure(text="\n".join(zeilen),
                               text_color=("#B45309", ORANGE) if z["zustand"] == "linear" else config.FARBEN["akzent"])
        w, h = self.ts_groesse
        if self.ts_canvas is not None and w > 1:
            self.ts_canvas.delete("all")
            self._ts_zeichnen(self.ts_canvas, w, h)

    # -------------------------------------------------------------------------
    def _ts_zeichnen(self, c, w, h):
        self.ts_groesse = (w, h)
        if self.ts_ue is None:             # Canvas zeichnet evtl. schon beim Erstellen -> später nochmal
            return
        z = self.ts_berechnen()
        text = _farbe(config.FARBEN["text"])
        leise = _farbe(config.FARBEN["text_leise"])
        bg = _farbe(config.FARBEN["flaeche"])
        schrift = (config.SCHRIFT, max(8, int(h / 26)))
        dick = max(2, int(h / 120))
        farbe_zustand = {"sperrt": GRAU, "linear": ORANGE, "voll": GRUEN}[z["zustand"]]
        strom_farbe = _mischen(leise, GRUEN, min(1.0, z["i"] / (z["ub"] / z["rl"])) if z["rl"] else 0)

        xs = 0.55 * w                                 # senkrechte Hauptleitung
        y_ub, y_gnd = 0.08 * h, 0.92 * h
        y_lampe, y_t = 0.28 * h, 0.63 * h
        r_lampe = min(0.09 * h, 0.06 * w)

        # Versorgung und Masse
        c.create_line(xs - 0.1 * w, y_ub, xs + 0.1 * w, y_ub, fill=ROT, width=dick + 1)
        c.create_text(xs + 0.11 * w, y_ub, anchor="w", text=f"+Ub = {fmt(z['ub'], 'spannung', 3)}", fill=ROT, font=schrift)
        c.create_line(xs - 0.06 * w, y_gnd, xs + 0.06 * w, y_gnd, fill=text, width=dick + 1)
        c.create_line(xs - 0.035 * w, y_gnd + 0.025 * h, xs + 0.035 * w, y_gnd + 0.025 * h, fill=text, width=dick)
        c.create_text(xs + 0.07 * w, y_gnd, anchor="w", text="GND", fill=leise, font=schrift)

        # Leitungen (Farbe = Stromstärke)
        c.create_line(xs, y_ub, xs, y_lampe - r_lampe, fill=strom_farbe, width=dick)
        c.create_line(xs, y_lampe + r_lampe, xs, y_t - 0.1 * h, fill=strom_farbe, width=dick)
        c.create_line(xs, y_t + 0.1 * h, xs, y_gnd, fill=strom_farbe, width=dick)

        # Lampe: Helligkeit ~ Leistung
        hell = z["p_last"] / z["p_max"] if z["p_max"] > 0 else 0
        if hell > 0.03:
            glow = r_lampe * (1.3 + 1.0 * hell)
            c.create_oval(xs - glow, y_lampe - glow, xs + glow, y_lampe + glow, outline="",
                          fill=_mischen(bg, "#FFD54A", 0.35 * hell))
        c.create_oval(xs - r_lampe, y_lampe - r_lampe, xs + r_lampe, y_lampe + r_lampe, width=dick,
                      outline=text, fill=_mischen(bg, "#FFE066", hell))
        k = r_lampe * 0.6
        c.create_line(xs - k, y_lampe - k, xs + k, y_lampe + k, fill=text, width=dick)
        c.create_line(xs - k, y_lampe + k, xs + k, y_lampe - k, fill=text, width=dick)
        c.create_text(xs + r_lampe + 8, y_lampe, anchor="w", fill=leise, font=schrift,
                      text=f"Lampe {fmt(z['rl'], 'widerstand', 3)}  ·  {fmt(z['p_last'], 'leistung', 3)}")

        # Transistor (Kreis in Zustandsfarbe)
        rt = 0.1 * h
        c.create_oval(xs - rt * 1.1, y_t - rt, xs + rt * 0.9, y_t + rt, outline=farbe_zustand, width=dick + 1)
        mosfet = self._ts_ist_mosfet()
        xb = xs - 0.45 * rt                           # Basis-/Gate-Linie
        if mosfet:
            c.create_line(xb - 0.25 * rt, y_t - 0.55 * rt, xb - 0.25 * rt, y_t + 0.55 * rt, fill=text, width=dick)
            for dy in (-0.45, 0, 0.45):                # Kanal in drei Stücken (Anreicherungstyp)
                c.create_line(xb, y_t + (dy - 0.15) * rt, xb, y_t + (dy + 0.15) * rt, fill=farbe_zustand, width=dick + 1)
            c.create_line(xb, y_t - 0.45 * rt, xs, y_t - 0.45 * rt, xs, y_t - rt, fill=text, width=dick)
            c.create_line(xb, y_t + 0.45 * rt, xs, y_t + 0.45 * rt, xs, y_t + rt, fill=text, width=dick)
            c.create_line(xs, y_t, xb, y_t, fill=text, width=dick, arrow="last")
            beschr_oben, beschr_unten, beschr_steuer = "D", "S", "G"
        else:
            c.create_line(xb, y_t - 0.55 * rt, xb, y_t + 0.55 * rt, fill=farbe_zustand, width=dick + 2)
            c.create_line(xb, y_t - 0.25 * rt, xs, y_t - rt, fill=text, width=dick)
            c.create_line(xb, y_t + 0.25 * rt, xs, y_t + rt, fill=text, width=dick, arrow="last")
            beschr_oben, beschr_unten, beschr_steuer = "C", "E", "B"
        c.create_text(xs + 6, y_t - rt - 6, anchor="w", text=beschr_oben, fill=leise, font=schrift)
        c.create_text(xs + 6, y_t + rt + 8, anchor="w", text=beschr_unten, fill=leise, font=schrift)
        c.create_text(xs + rt * 1.1, y_t, anchor="w", fill=farbe_zustand, font=(config.SCHRIFT, max(9, int(h / 22)), "bold"),
                      text=f"{'U_DS' if mosfet else 'U_CE'} = {fmt(z['u_t'], 'spannung', 3)}")

        # Ansteuerung links
        x_ein = 0.08 * w
        steuer_x = xb - (0.25 * rt if mosfet else 0)
        c.create_line(x_ein, y_t, steuer_x, y_t, fill=BLAU, width=dick)
        c.create_oval(x_ein - 5, y_t - 5, x_ein + 5, y_t + 5, fill=BLAU, outline="")
        c.create_text(x_ein, y_t - 0.07 * h, text=f"Ue = {fmt(z['ue'], 'spannung', 3)}", fill=BLAU, font=schrift)
        if not mosfet:
            rx0, rx1 = 0.2 * w, 0.32 * w
            c.create_rectangle(rx0, y_t - 0.035 * h, rx1, y_t + 0.035 * h, fill=bg, outline=BLAU, width=dick)
            c.create_text((rx0 + rx1) / 2, y_t + 0.07 * h, text="Rb", fill=BLAU, font=schrift)
        c.create_text(steuer_x - 8, y_t - 0.05 * h, anchor="e", text=beschr_steuer, fill=leise, font=schrift)

        # Balken: Verlustleistung im Transistor
        bx0, bx1, by = 0.72 * w, 0.95 * w, 0.84 * h
        p_ref = max(z["p_max"] / 4, 1e-9)            # max. Verlust tritt bei halbem Strom auf (P_max/4)
        anteil = min(1.0, z["p_t"] / p_ref)
        c.create_text(bx0, by - 0.05 * h, anchor="w", text="Wärme im Transistor", fill=leise, font=schrift)
        c.create_rectangle(bx0, by - 0.02 * h, bx1, by + 0.02 * h, outline=leise)
        if anteil > 0.005:
            c.create_rectangle(bx0, by - 0.02 * h, bx0 + (bx1 - bx0) * anteil, by + 0.02 * h, outline="",
                               fill=_mischen(GRUEN, ROT, anteil))


# =============================================================================
# SCHALTZEICHEN (werden in SYMBOLE aus symbole.py eingetragen)
# =============================================================================
def _diodenkoerper(c, xm, m, groesse, farbe, s, strich="normal"):
    """Dreieck (Anode links) + Kathodenstrich rechts. Gibt x der Kathode zurück."""
    a, k = xm - groesse, xm + groesse * 0.6
    c.create_polygon(a, m - groesse, a, m + groesse, k, m, outline=farbe, fill="", width=s)
    c.create_line(k, m - groesse, k, m + groesse, fill=farbe, width=s)
    if strich == "z":                                   # Z-Diode: Knick am Kathodenstrich
        c.create_line(k, m - groesse, k - groesse * 0.35, m - groesse * 1.15, fill=farbe, width=s)
        c.create_line(k, m + groesse, k + groesse * 0.35, m + groesse * 1.15, fill=farbe, width=s)
    if strich == "schottky":
        c.create_line(k, m - groesse, k + groesse * 0.3, m - groesse, k + groesse * 0.3, m - groesse * 0.7,
                      fill=farbe, width=s)
        c.create_line(k, m + groesse, k - groesse * 0.3, m + groesse, k - groesse * 0.3, m + groesse * 0.7,
                      fill=farbe, width=s)
    return a, k


def symbol_diode(c, w, h, farbe):
    s = max(2, int(h / 40))
    m, g = h * 0.42, min(0.13 * h, 0.05 * w)
    for xm, art, text in ((0.2 * w, "normal", "Diode (Si)"), (0.5 * w, "schottky", "Schottky"),
                          (0.8 * w, "z", "Z-Diode")):
        a, k = _diodenkoerper(c, xm, m, g, farbe, s, art)
        c.create_line(xm - 0.13 * w, m, a, m, fill=farbe, width=s)
        c.create_line(k, m, xm + 0.13 * w, m, fill=farbe, width=s)
        _beschriftung(c, xm, 0.86 * h, text, farbe, h)
    c.create_text(0.05 * w, m - g - 0.06 * h, anchor="w", text="A (Anode)", fill=farbe,
                  font=(config.SCHRIFT, max(7, int(h / 13))))
    c.create_text(0.35 * w, m - g - 0.06 * h, anchor="e", text="K (Kathode, Ring)", fill=farbe,
                  font=(config.SCHRIFT, max(7, int(h / 13))))


def symbol_led(c, w, h, farbe):
    s = max(2, int(h / 40))
    m, g = h * 0.48, min(0.14 * h, 0.06 * w)
    xm = 0.42 * w
    a, k = _diodenkoerper(c, xm, m, g, farbe, s)
    c.create_line(0.1 * w, m, a, m, fill=farbe, width=s)
    c.create_line(k, m, 0.74 * w, m, fill=farbe, width=s)
    for dx in (0, 0.05 * w):                            # zwei Pfeile nach aussen = Licht
        x0, y0 = xm + dx, m - g * 1.1
        c.create_line(x0, y0, x0 + 0.06 * w, y0 - 0.14 * h, fill=farbe, width=s, arrow="last")
    _beschriftung(c, 0.12 * w, m - 0.12 * h, "+ Anode (langes Bein)", farbe, h)
    _beschriftung(c, 0.78 * w, m + 0.14 * h, "− Kathode (kurz, abgeflacht)", farbe, h)


def _bjt(c, xm, m, g, farbe, s, npn=True):
    xb = xm - 0.3 * g
    c.create_oval(xm - g, m - g, xm + g, m + g, outline=farbe, width=s)
    c.create_line(xb, m - 0.55 * g, xb, m + 0.55 * g, fill=farbe, width=s + 1)
    c.create_line(xm - 1.7 * g, m, xb, m, fill=farbe, width=s)                      # Basis
    c.create_line(xb, m - 0.25 * g, xm + 0.45 * g, m - 0.8 * g, xm + 0.45 * g, m - 1.5 * g, fill=farbe, width=s)
    if npn:
        c.create_line(xb, m + 0.25 * g, xm + 0.45 * g, m + 0.8 * g, fill=farbe, width=s, arrow="last")
    else:
        c.create_line(xm + 0.45 * g, m + 0.8 * g, xb, m + 0.25 * g, fill=farbe, width=s, arrow="last")
    c.create_line(xm + 0.45 * g, m + 0.8 * g, xm + 0.45 * g, m + 1.5 * g, fill=farbe, width=s)


def symbol_bipolar(c, w, h, farbe):
    s = max(2, int(h / 45))
    g = min(0.25 * h, 0.1 * w)
    m = 0.45 * h
    for xm, npn, text in ((0.28 * w, True, "NPN (Pfeil zeigt raus)"), (0.72 * w, False, "PNP (Pfeil zeigt rein)")):
        _bjt(c, xm, m, g, farbe, s, npn)
        klein = (config.SCHRIFT, max(7, int(h / 14)))
        c.create_text(xm - 1.7 * g, m - 0.12 * h, text="B", fill=farbe, font=klein)
        c.create_text(xm + 0.45 * g + 12, m - 1.4 * g, text="C", fill=farbe, font=klein)
        c.create_text(xm + 0.45 * g + 12, m + 1.4 * g, text="E", fill=farbe, font=klein)
        _beschriftung(c, xm, 0.95 * h, text, farbe, h)


def _mos(c, xm, m, g, farbe, s, n_kanal=True):
    xk = xm - 0.2 * g                                   # Kanal
    xg = xk - 0.3 * g                                   # Gate-Platte
    c.create_oval(xm - g, m - g, xm + g, m + g, outline=farbe, width=s)
    c.create_line(xm - 1.7 * g, m + 0.45 * g, xg, m + 0.45 * g, fill=farbe, width=s)            # Gate-Anschluss
    c.create_line(xg, m - 0.55 * g, xg, m + 0.55 * g, fill=farbe, width=s)
    for dy in (-0.45, 0, 0.45):
        c.create_line(xk, m + (dy - 0.17) * g, xk, m + (dy + 0.17) * g, fill=farbe, width=s + 1)
    xr = xm + 0.4 * g
    c.create_line(xk, m - 0.45 * g, xr, m - 0.45 * g, xr, m - 1.5 * g, fill=farbe, width=s)     # Drain
    c.create_line(xk, m + 0.45 * g, xr, m + 0.45 * g, xr, m + 1.5 * g, fill=farbe, width=s)     # Source
    c.create_line(xr, m, xr, m + 0.45 * g, fill=farbe, width=s)                                 # Bulk an Source
    if n_kanal:
        c.create_line(xr, m, xk, m, fill=farbe, width=s, arrow="last")
    else:
        c.create_line(xk, m, xr, m, fill=farbe, width=s, arrow="last")


def symbol_mosfet(c, w, h, farbe):
    s = max(2, int(h / 45))
    g = min(0.25 * h, 0.1 * w)
    m = 0.45 * h
    for xm, n_kanal, text in ((0.28 * w, True, "N-Kanal (Pfeil zeigt rein)"), (0.72 * w, False, "P-Kanal (Pfeil zeigt raus)")):
        _mos(c, xm, m, g, farbe, s, n_kanal)
        klein = (config.SCHRIFT, max(7, int(h / 14)))
        c.create_text(xm - 1.7 * g, m + 0.2 * g, text="G", fill=farbe, font=klein)
        c.create_text(xm + 0.4 * g + 12, m - 1.4 * g, text="D", fill=farbe, font=klein)
        c.create_text(xm + 0.4 * g + 12, m + 1.4 * g, text="S", fill=farbe, font=klein)
        _beschriftung(c, xm, 0.95 * h, text, farbe, h)


SYMBOLE.update({
    "diode": symbol_diode,
    "led": symbol_led,
    "bipolartransistor": symbol_bipolar,
    "mosfet": symbol_mosfet,
})
