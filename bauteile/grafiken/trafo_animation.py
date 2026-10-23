# =============================================================================
# bauteile/grafiken/trafo_animation.py
# -----------------------------------------------------------------------------
# TRAFO-ANIMATION IM FENSTER: Regler, AC/DC-Umschalter, Pause und die Zeitschleife.
# Rechnen und Zeichnen macht das Modell OHNE Fenster -> bauteile/grafiken/trafo_modell.py
# (dasselbe Modell zeichnet die Animation in der Webversion als SVG).
#
# TECHNIK:
#   - Statische Teile (Kern, Spulen, Leitungen) werden nur bei Grössenänderung
#     oder neuer Einstellung gezeichnet.
#   - Bewegte Teile (Tag "dyn") werden alle 40 ms gelöscht und neu gezeichnet.
#   - Die Animation stoppt von selbst, wenn die Seite verlassen wird, und
#     pausiert, solange sie nicht sichtbar ist (spart Rechenzeit).
#   - Alle eigenen Namen beginnen mit ta_ (keine Kollision mit tkinter!).
#
# WER RUFT DAS AUF?  bauteile/rechner/trafo_rechner.py (RECHNER "trafo_animation", als GrafikVerweis)
# =============================================================================

import time

import customtkinter as ctk

import config                                                   # -> config.py
from bauteile.grafiken.trafo_modell import TrafoModell          # -> bauteile/grafiken/trafo_modell.py
from bauteile.rechner.basis import WertRegler                   # -> bauteile/rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel      # -> core/layout.py
from core.widgets import Tooltip, WerteAnzeige                  # -> core/widgets.py

FRAME_MS = 40           # 25 Bilder pro Sekunde
HILFE = """## Bedienung
- **Regler ziehen** oder rechts eine Zahl eintippen (Enter übernimmt), **Einheit** rechts wählen
- **AC / DC** umschalten: Bei Gleichspannung ändert sich das Magnetfeld nicht – es wird nichts übertragen
- **⏸ Pause** hält die Animation an, **↺ Zurücksetzen** stellt alle Werte wie beim Öffnen ein
- Die Punkte zeigen den Strom, die drei kleinen Oszilloskope U1, das Magnetfeld Φ und U2"""


class TrafoAnimation(Karte):

    def __init__(self, master):
        m = self.ta_modell = TrafoModell()
        super().__init__(master, titel=m.TITEL, untertitel=m.UNTERTITEL, hilfe=HILFE)     # ❓ (core/layout.py)
        b = self.body

        # ---- Zustand (VOR dem Canvas setzen - der Canvas kann sofort zeichnen) ----
        self.ta_laeuft = True
        self.ta_zeit = 0.0                 # Animationszeit in s
        self.ta_geo = None                 # Geometrie, gesetzt in _ta_statisch
        self.ta_c = None                   # Zeichenfläche, auf die zuletzt gezeichnet wurde
        self.ta_letzt = time.monotonic()

        # ---- Zeichenfläche ----
        self.ta_canvas = ResponsiveCanvas(b, self._ta_statisch, seitenverhaeltnis=m.SEITENVERHAELTNIS,
                                          max_hoehe=m.MAX_HOEHE)
        self.ta_canvas.grid(row=0, column=0, sticky="ew")

        # ---- Regler: Slider + Zahlenfeld + Einheit (Definition im Modell: TrafoModell.REGLER) ----
        regler = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        regler.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        regler.grid_columnconfigure(0, weight=1)
        self.ta_regler = {}
        for zeile, (schluessel, text, typ, von, bis, start, opt) in enumerate(m.REGLER):
            self.ta_regler[schluessel] = WertRegler(regler, text, typ, von, bis, start, bei_aenderung=self._ta_neu,
                                                    text_breite=170, **opt)
            self.ta_regler[schluessel].grid(row=zeile, column=0, sticky="ew")

        knoepfe = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        knoepfe.grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.ta_art = ctk.CTkSegmentedButton(knoepfe, values=m.VARIANTEN, command=lambda _v: self._ta_neu())
        self.ta_art.set(m.VARIANTEN[0])
        self.ta_art.grid(row=0, column=0)
        self.ta_pause = ctk.CTkButton(knoepfe, text="⏸ Pause", width=90, command=self._ta_pause_umschalten)
        self.ta_pause.grid(row=0, column=1, padx=(10, 0))
        zurueck = ctk.CTkButton(knoepfe, text=config.TEXT_ZURUECKSETZEN, width=120, fg_color="transparent",
                                border_width=1, border_color=config.FARBEN["rahmen"], text_color=config.FARBEN["text"],
                                hover_color=config.FARBEN["rahmen"], command=self.ta_zuruecksetzen)
        zurueck.grid(row=0, column=2, padx=(10, 0))
        Tooltip(zurueck, "Alle Regler und den Umschalter wieder auf die Startwerte")

        # ---- Ergebnis + Legende ----
        self.ta_info = WerteAnzeige(b)                                 # Ergebnis als Tabelle (core/widgets.py)
        self.ta_info.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        WrapLabel(b, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"], text=m.ERKLAERUNG).grid(
            row=4, column=0, sticky="ew", pady=(6, 0))

        self._ta_neu()
        self._ta_schleife()

    # =========================================================================
    # BEDIENUNG
    # =========================================================================
    def _ta_neu(self):
        """Regler oder AC/DC geändert: Modell setzen, Text und statische Teile neu."""
        werte = {k: r.wert() for k, r in self.ta_regler.items()}
        self.ta_modell.setzen(werte, self.ta_art.get(), self.ta_zeit)
        zeilen, warnung = self.ta_modell.info()
        self.ta_info.zeigen(zeilen, ("#B45309", "#F59E0B") if warnung else config.FARBEN["akzent"])
        if self.ta_geo:
            self.ta_canvas.delete("all")
            self._ta_statisch(self.ta_canvas, self.ta_geo["w"], self.ta_geo["h"])

    def ta_zuruecksetzen(self):
        """↺ Zurücksetzen: Regler (mit Einheit) und AC/DC wie beim Öffnen."""
        for regler in self.ta_regler.values():
            regler.zuruecksetzen()
        self.ta_art.set(self.ta_modell.VARIANTEN[0])
        self._ta_neu()

    def _ta_pause_umschalten(self):
        self.ta_laeuft = not self.ta_laeuft
        self.ta_pause.configure(text="⏸ Pause" if self.ta_laeuft else "▶ Weiter")

    # =========================================================================
    # ZEICHNEN (das Modell zeichnet, hier nur wann)
    # =========================================================================
    def _ta_statisch(self, c, w, h):
        """Aufruf bei Grössenänderung oder neuer Einstellung."""
        self.ta_c = c                      # Zeichenfläche merken (self.ta_canvas existiert evtl. noch nicht)
        self.ta_geo = self.ta_modell.statisch(c, w, h)
        self._ta_dynamisch()

    def _ta_dynamisch(self):
        if self.ta_geo is None:
            return
        self.ta_c.delete("dyn")
        self.ta_modell.dynamisch(self.ta_c, self.ta_geo, self.ta_zeit)

    # =========================================================================
    # ANIMATIONS-SCHLEIFE
    # =========================================================================
    def _ta_schleife(self):
        if not hasattr(self, "ta_canvas") or not self.ta_canvas.winfo_exists():
            return                                          # Seite verlassen -> Ende
        jetzt = time.monotonic()
        dt = min(0.1, jetzt - self.ta_letzt)                # nach Pausen keine grossen Sprünge
        self.ta_letzt = jetzt
        if not self.ta_canvas.winfo_ismapped():
            self.after(300, self._ta_schleife)              # unsichtbar -> nur selten nachsehen
            return
        if self.ta_laeuft:
            self.ta_zeit += dt
            self.ta_modell.weiter(self.ta_zeit, dt)
            self._ta_dynamisch()
        self.after(FRAME_MS, self._ta_schleife)
