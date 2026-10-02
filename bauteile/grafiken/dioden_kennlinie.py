# =============================================================================
# bauteile/grafiken/dioden_kennlinie.py
# -----------------------------------------------------------------------------
# INTERAKTIVE KENNLINIE: Durchlassbereich verschiedener Dioden + Z-Durchbruch.
#
#   ┌───────────────────────────────────────────────┐
#   │                         I │      Si  LED rot   │
#   │                           │      │   │         │
#   │   Sperrbereich            │      │   │         │
#   │ ──────────────────────────┼─────╱───╱──── U    │
#   │        ╱ Z-Durchbruch     │  Durchlassbereich   │
#   │       │ (−U_Z)            │                    │
#   │  U_Z:        ────●──────   (Schieberegler)      │
#   │  Temperatur: ──●────────   (Schieberegler)      │
#   └───────────────────────────────────────────────┘
#
# Die Kurven sind VEREINFACHT (Exponentialfunktion ab der Schwellspannung) -
# sie zeigen das Prinzip, nicht die Werte eines bestimmten Typs.
# Achtung: Die Spannungsachse ist links (Sperr) und rechts (Durchlass) verschieden skaliert.
#
# Alle eigenen Namen beginnen mit dk_ (keine Kollision mit tkinter!).
#
# WER RUFT DAS AUF?  bauteile/rechner/dioden_rechner.py (RECHNER "dioden_kennlinie")
#                    -> eingebunden in bauteile/inhalte/02_dioden/diode.py
# =============================================================================

import math

import customtkinter as ctk

import config                                                   # -> config.py
from bauteile.rechner import dioden_mathe as dm                 # -> rechner/dioden_mathe.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel      # -> core/layout.py

U_RECHTS = 3.5          # V, Durchlassbereich bis 3.5 V
U_LINKS = 12.0          # V, Sperrbereich bis −12 V

# Name -> (Schwellspannung bei 25 °C, Farbe Light, Farbe Dark)
TYPEN = {
    "Schottky (0.3 V)": (0.3, "#7C3AED", "#A78BFA"),
    "Si (0.7 V)": (0.7, "#1F6FEB", "#60A5FA"),
    "LED rot (1.8 V)": (1.8, "#DC2626", "#EF4444"),
    "LED blau (3.0 V)": (3.0, "#0E7490", "#22D3EE"),
}
Z_FARBE = ("#D97706", "#F59E0B")


def _farbe(paar):
    return paar[1] if ctk.get_appearance_mode() == "Dark" else paar[0]


class DiodenKennlinie(Karte):

    def __init__(self, master):
        super().__init__(master, titel="📈 Dioden-Kennlinien (interaktiv)",
                         untertitel="Rechts Durchlassbereich, links Sperrbereich mit Z-Durchbruch")
        b = self.body
        # Startwerte VOR dem Canvas setzen (der Canvas kann sofort zeichnen wollen)
        self.dk_uz = 5.1
        self.dk_temp = 25.0
        self.dk_groesse = (0, 0)

        self.dk_canvas = ResponsiveCanvas(b, self._zeichnen, seitenverhaeltnis=0.5, max_hoehe=360)
        self.dk_canvas.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        regler = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        regler.grid(row=1, column=0, sticky="ew")
        regler.grid_columnconfigure(1, weight=1)
        self.dk_uz_text = self._regler(regler, 0, "Z-Spannung U_Z", 2.7, 11.0, self.dk_uz, self._uz_neu)
        self.dk_t_text = self._regler(regler, 1, "Temperatur", -20.0, 125.0, self.dk_temp, self._t_neu)

        self.dk_anzeige = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"),
                                    text_color=config.FARBEN["akzent"])
        self.dk_anzeige.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        self._anzeigen()

    def _regler(self, rahmen, zeile, text, von, bis, start, funktion):
        ctk.CTkLabel(rahmen, text=f"{text}  ", anchor="w").grid(row=zeile, column=0, sticky="w", pady=2)
        regler = ctk.CTkSlider(rahmen, from_=von, to=bis, number_of_steps=int((bis - von) * 10), command=funktion)
        regler.set(start)
        regler.grid(row=zeile, column=1, sticky="ew", pady=2)
        anzeige = ctk.CTkLabel(rahmen, text="", width=70, anchor="e")
        anzeige.grid(row=zeile, column=2, pady=2)
        return anzeige

    # -------------------------------------------------------------------------
    def _uz_neu(self, wert):
        self.dk_uz = float(wert)
        self._neu()

    def _t_neu(self, wert):
        self.dk_temp = float(wert)
        self._neu()

    def _neu(self):
        self._anzeigen()
        breite, hoehe = self.dk_groesse
        if breite > 1:
            self.dk_canvas.delete("all")
            self._zeichnen(self.dk_canvas, breite, hoehe)

    def _anzeigen(self):
        self.dk_uz_text.configure(text=f"{self.dk_uz:.1f} V")
        self.dk_t_text.configure(text=f"{self.dk_temp:.0f} °C")
        verschiebung = dm.TK_U_F * (self.dk_temp - 25) * 1000
        self.dk_anzeige.configure(text=(
            f"Bei {self.dk_temp:.0f} °C: U_F ändert sich um {verschiebung:+.0f} mV (−2 mV/K)  ·  "
            f"Si-Diode ≈ {dm.U_F_SI + verschiebung / 1000:.2f} V\n"
            f"Z-Diode mit {self.dk_uz:.1f} V: " + ("Z-Effekt, TK negativ" if self.dk_uz < 5
                                                    else "Lawinen-Effekt, TK positiv" if self.dk_uz > 6
                                                    else "beide Effekte heben sich auf → kleinster TK")))

    # -------------------------------------------------------------------------
    def _zeichnen(self, c, w, h):
        self.dk_groesse = (w, h)
        achse = _farbe(config.FARBEN["text_leise"])
        raster = _farbe(config.FARBEN["rahmen"])
        klein = (config.SCHRIFT, max(8, int(h / 30)))
        x0, y0 = 0.45 * w, 0.72 * h                          # Nullpunkt
        sx = (w - x0 - 0.04 * w) / U_RECHTS                  # Pixel pro Volt rechts
        sx_neg = (x0 - 0.04 * w) / U_LINKS                   # Pixel pro Volt links (anderer Massstab!)
        sy = y0 - 0.06 * h                                   # Pixel für "vollen" Strom

        # ---- Achsen + Beschriftung ----
        c.create_line(0.02 * w, y0, w - 0.01 * w, y0, fill=achse, width=2, arrow="last")
        c.create_line(x0, h - 0.02 * h, x0, 0.02 * h, fill=achse, width=2, arrow="last")
        c.create_text(w - 0.02 * w, y0 - 12, text="U", fill=achse, font=klein)
        c.create_text(x0 + 12, 0.04 * h, text="I", fill=achse, font=klein)
        for v in (1, 2, 3):
            c.create_line(x0 + v * sx, y0 - 4, x0 + v * sx, y0 + 4, fill=achse)
            c.create_text(x0 + v * sx, y0 + 14, text=f"{v} V", fill=achse, font=klein)
        for v in (4, 8, 12):
            c.create_line(x0 - v * sx_neg, y0 - 4, x0 - v * sx_neg, y0 + 4, fill=achse)
            c.create_text(x0 - v * sx_neg, y0 - 14, text=f"−{v} V", fill=achse, font=klein)
        c.create_text(x0 + 0.02 * w, y0 + 0.2 * h, anchor="w", fill=achse, font=klein,
                      text="Durchlassbereich")
        c.create_text(0.03 * w, y0 + 0.2 * h, anchor="w", fill=achse, font=klein,
                      text="Sperrbereich (anderer Massstab)")
        c.create_line(0.02 * w, y0 + 1, x0, y0 + 1, fill=raster)

        # ---- Durchlasskurven: vereinfacht als e-Funktion ab Schwellspannung ----
        verschiebung = dm.TK_U_F * (self.dk_temp - 25)
        for n, (name, (us, hell, dunkel)) in enumerate(TYPEN.items()):
            farbe = dunkel if ctk.get_appearance_mode() == "Dark" else hell
            us = us + verschiebung
            punkte = []
            for k in range(0, 161):
                u = k * U_RECHTS / 160
                i = min(1.0, math.exp((u - us) * 12) * 0.05) if u > us - 0.4 else 0.0
                punkte += [x0 + u * sx, y0 - i * sy]
                if i >= 1.0:                               # oben angekommen -> Kurve hier beenden
                    break
            c.create_line(*punkte, fill=farbe, width=2, smooth=True)
            c.create_text(0.03 * w, 0.06 * h + n * 0.075 * h, text="■ " + name, fill=farbe, anchor="w", font=klein)

        # ---- Z-Diode: Durchbruch bei −U_Z (Strom nach unten = negativ) ----
        z = _farbe(Z_FARBE)
        punkte = []
        for k in range(0, 161):
            u = -k * U_LINKS / 160
            i = -min(0.25, math.exp((-u - self.dk_uz) * 8) * 0.01) if -u > self.dk_uz - 0.6 else 0.0
            punkte += [x0 + u * sx_neg, y0 - i * sy]
            if i <= -0.25:                                 # unten angekommen -> Kurve hier beenden
                break
        c.create_line(*punkte, fill=z, width=3, smooth=True)
        c.create_text(x0 - self.dk_uz * sx_neg + 8, y0 + 0.12 * sy, text=f"−U_Z = −{self.dk_uz:.1f} V",
                      fill=z, font=klein, anchor="w")
        c.create_text(0.03 * w, 0.06 * h + len(TYPEN) * 0.075 * h, text="■ Z-Diode (Sperrrichtung)",
                      fill=z, anchor="w", font=klein)
