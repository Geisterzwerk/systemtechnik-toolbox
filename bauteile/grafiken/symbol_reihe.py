# =============================================================================
# bauteile/grafiken/symbol_reihe.py
# -----------------------------------------------------------------------------
# SYMBOL-REIHE: zeigt die Varianten eines Schaltzeichens nebeneinander,
# jede in einer EIGENEN Zelle mit der Beschriftung darunter.
#
#   breit:   ┌────────┐ ┌────────┐ ┌────────┐
#            │ Symbol │ │ Symbol │ │ Symbol │
#            └────────┘ └────────┘ └────────┘
#             Text 1     Text 2     Text 3
#
#   schmal:  ┌────────┐
#            │ Symbol │      <- Zellen rutschen untereinander,
#            └────────┘         nichts überlappt
#             Text 1
#            ┌────────┐ ...
#
# Die Beschriftung ist ein echtes Label (WrapLabel) und bricht um - sie kann
# deshalb nie in das Symbol hineinragen oder abgeschnitten werden.
#
# WER BENUTZT DAS?  bauteile/engine/seite.py BauteilSeite._steckbrief()
# DATEN:            bauteile/grafiken/symbole.py SYMBOLE (Listen von Variante)
# =============================================================================

import customtkinter as ctk

import config                                                            # -> config.py
from core.layout import ResponsiveCanvas, ResponsiveGrid, WrapLabel      # -> core/layout.py

MAX_HOEHE = 140          # Zellen werden nie höher (bei sehr breitem Fenster)


def _symbolfarbe():
    hell, dunkel = config.FARBEN["text"]
    return dunkel if ctk.get_appearance_mode() == "Dark" else hell


class SymbolReihe(ResponsiveGrid):
    """
    varianten   Liste von symbole.Variante(zeichnen, text, seitenverhaeltnis, min_breite)
    """

    def __init__(self, master, varianten):
        breiteste = max(v.min_breite for v in varianten)
        super().__init__(master, min_spaltenbreite=breiteste, max_spalten=len(varianten), abstand=16)
        farbe = _symbolfarbe()
        for variante in varianten:
            zelle = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
            zelle.grid_columnconfigure(0, weight=1)
            ResponsiveCanvas(zelle, lambda c, w, h, f=variante.zeichnen: f(c, w, h, farbe),
                             seitenverhaeltnis=variante.seitenverhaeltnis, max_hoehe=MAX_HOEHE).grid(
                row=0, column=0, sticky="ew")
            WrapLabel(zelle, text=variante.text, font=config.FONT_KLEIN, anchor="center", justify="center",
                      text_color=config.FARBEN["text_leise"]).grid(row=1, column=0, sticky="ew", pady=(2, 0))
            self.add(zelle)

    def _anordnen(self):
        """
        Wie ResponsiveGrid, aber JEDE Zelle bekommt links und rechts gleich viel Rand.
        (ResponsiveGrid gibt den äusseren Spalten weniger Rand -> Zellen wären ein paar
        Pixel unterschiedlich breit und die Symbole unterschiedlich gross.)
        """
        n = self._spalten
        for s in range(self.max_spalten):
            self.grid_columnconfigure(s, weight=1 if s < n else 0, uniform="spalte" if s < n else "")
        halb = self.abstand // 2
        for i, widget in enumerate(self._elemente):
            zeile, spalte = divmod(i, n)
            widget.grid(row=zeile, column=spalte, sticky="nsew", padx=(halb, halb), pady=(0, self.abstand))
