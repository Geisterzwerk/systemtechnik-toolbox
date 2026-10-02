# =============================================================================
# messtechnik/grafiken.py
# -----------------------------------------------------------------------------
# INTERAKTIVE GRAFIK: Abtasttheorem und Aliasing.
#
#   blau    = echtes Signal (Sinus mit Frequenz f)
#   Punkte  = Abtastwerte (alle 1/fs Sekunden)
#   orange  = was der AD-Wandler "sieht" (die Rekonstruktion aus den Punkten)
#
# Ist fs > 2·f, passt die orange Kurve zum echten Signal. Sonst entsteht eine
# FALSCHE, tiefere Frequenz (Alias) – genau das verhindert ein Anti-Aliasing-Filter.
#
# Gezeichnet wird nur bei Grössenänderung oder Reglerbewegung (keine Animation).
# Eigene Namen beginnen mit ag_ (keine Kollision mit tkinter).
# =============================================================================

import math

import customtkinter as ctk

import config                                               # -> config.py
from bauteile.rechner.basis import WertRegler               # -> bauteile/rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel  # -> core/layout.py

BLAU = "#3B82F6"
ORANGE = "#F59E0B"
GRUEN = "#22C55E"
ROT = "#EF4444"


def _farbe(paar):
    return paar[1] if ctk.get_appearance_mode() == "Dark" else paar[0]


def alias_frequenz(f, fs):
    """Frequenz, die nach dem Abtasten erscheint (mit Vorzeichen, damit die Kurve durch die Punkte geht)."""
    return f - fs * round(f / fs)


class AbtastGrafik(Karte):

    def __init__(self, master):
        super().__init__(master, titel="📉 Abtasttheorem & Aliasing (interaktiv)",
                         untertitel="Signalfrequenz erhöhen: ab fs/2 sieht der Wandler eine falsche Frequenz")
        b = self.body
        self.ag_groesse = (0, 0)
        self.ag_canvas = None
        self.ag_regler = {}

        regler = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        regler.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        regler.grid_columnconfigure(0, weight=1)
        # Slider + Zahlenfeld + Einheit -> bauteile/rechner/basis.py WertRegler
        self.ag_regler = {
            "f": WertRegler(regler, "Signalfrequenz f", "frequenz", 1, 45, 3, einheit="Hz", grenzen=(0.1, 200),
                            schritte=88, bei_aenderung=self.ag_neu, text_breite=130),
            "fs": WertRegler(regler, "Abtastrate fs", "frequenz", 4, 60, 20, einheit="Hz", grenzen=(1, 400),
                             schritte=112, bei_aenderung=self.ag_neu, text_breite=130),
        }
        for zeile, eintrag in enumerate(self.ag_regler.values()):
            eintrag.grid(row=zeile, column=0, sticky="ew")

        self.ag_canvas = ResponsiveCanvas(b, self._ag_zeichnen, seitenverhaeltnis=0.42, max_hoehe=340)
        self.ag_canvas.grid(row=0, column=0, sticky="ew")
        self.ag_info = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"), text_color=config.FARBEN["akzent"])
        self.ag_info.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.ag_neu()

    def _ag_werte(self):
        return self.ag_regler["f"].wert(), self.ag_regler["fs"].wert()

    def ag_neu(self):
        if len(self.ag_regler) < 2:
            return
        f, fs = self._ag_werte()
        fa = abs(alias_frequenz(f, fs))
        zeilen = [f"Nyquist-Frequenz fs/2 = {fs / 2:.1f} Hz   ·   Signal f = {f:.1f} Hz"]
        if f < fs / 2 - 1e-9:
            zeilen.append(f"✅ f < fs/2 → korrekt erfasst ({fs / f:.1f} Abtastwerte pro Periode)")
            farbe = config.FARBEN["akzent"]
        elif abs(f - fs / 2) < 1e-9:
            zeilen.append("⚠ Genau fs/2: je nach Phase sieht man die volle Amplitude – oder nur Nullen")
            farbe = ("#B45309", ORANGE)
        else:
            zeilen.append(f"❌ ALIASING: Der Wandler sieht {fa:.1f} Hz statt {f:.1f} Hz!")
            farbe = ("#B91C1C", ROT)
        self.ag_info.configure(text="\n".join(zeilen), text_color=farbe)
        w, h = self.ag_groesse
        if self.ag_canvas is not None and w > 1:
            self.ag_canvas.delete("all")
            self._ag_zeichnen(self.ag_canvas, w, h)

    def _ag_zeichnen(self, c, w, h):
        self.ag_groesse = (w, h)
        if len(self.ag_regler) < 2:
            return
        f, fs = self._ag_werte()
        fa = alias_frequenz(f, fs)
        text = _farbe(config.FARBEN["text_leise"])
        linie = _farbe(config.FARBEN["rahmen"])
        schrift = (config.SCHRIFT, max(8, int(h / 24)))
        links, rechts, oben, unten = 0.04 * w, 0.98 * w, 0.10 * h, 0.86 * h
        dauer = 1.0                                             # 1 Sekunde anzeigen

        def x(t):
            return links + (rechts - links) * t / dauer

        def y(v):
            return (oben + unten) / 2 - (unten - oben) / 2 * 0.9 * v

        c.create_line(links, y(0), rechts, y(0), fill=linie)
        for k in range(1, 10):
            c.create_line(x(k / 10), oben, x(k / 10), unten, fill=linie, dash=(2, 4))
        c.create_text(rechts, unten + 0.07 * h, anchor="e", text="Zeit: 1 s", fill=text, font=schrift)

        # echtes Signal (fein aufgelöst)
        punkte = []
        schritte = max(200, int(f * 40))
        for i in range(schritte + 1):
            t = dauer * i / schritte
            punkte += [x(t), y(math.sin(2 * math.pi * f * t))]
        c.create_line(*punkte, fill=BLAU, width=2)

        # Rekonstruktion (was der Wandler sieht)
        punkte = []
        for i in range(401):
            t = dauer * i / 400
            punkte += [x(t), y(math.sin(2 * math.pi * fa * t))]
        c.create_line(*punkte, fill=ORANGE, width=3, dash=(8, 4))

        # Abtastpunkte
        n = int(dauer * fs)
        for k in range(n + 1):
            t = k / fs
            px, py = x(t), y(math.sin(2 * math.pi * f * t))
            c.create_line(px, y(0), px, py, fill=GRUEN)
            c.create_oval(px - 4, py - 4, px + 4, py + 4, fill=GRUEN, outline="")

        c.create_text(links + 4, oben - 0.05 * h, anchor="w", fill=BLAU, font=schrift, text="— echtes Signal")
        c.create_text(links + 0.2 * w, oben - 0.05 * h, anchor="w", fill=GRUEN, font=schrift, text="● Abtastwerte")
        c.create_text(links + 0.4 * w, oben - 0.05 * h, anchor="w", fill=ORANGE, font=schrift,
                      text="- - was der Wandler sieht")
