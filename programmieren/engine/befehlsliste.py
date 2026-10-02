# =============================================================================
# programmieren/engine/befehlsliste.py
# -----------------------------------------------------------------------------
# GUI-Baustein: Liste von Konsolenbefehlen, JEDER mit eigenem Kopier-Knopf.
#
#   ┌ Navigation ─────────────────────────────────────────────────┐
#   │ [📋]  pwd                 Wo bin ich gerade?                 │
#   │ [📋]  cd /etc             In den Ordner /etc wechseln        │
#   │ [📋]  ⚠ rm -rf ordner/    Löscht OHNE Rückfrage ... (rot)    │
#   └─────────────────────────────────────────────────────────────┘
#
# Breites Fenster: Befehl und Erklärung nebeneinander.
# Schmales Fenster: Erklärung rutscht unter den Befehl (core/layout.py Responsive).
# Gefährliche Befehle erkennt engine/syntax.py ist_gefaehrlich() -> rot + ⚠.
#
# Daten (im THEMA einer Seite):
#   "befehle": [
#       {"titel": "Navigation", "zeilen": [("pwd", "Wo bin ich?"), ("cd /etc", "...")]},
#   ]
#
# WER BENUTZT DAS?  engine/seite.py ThemenSeite._befehle()
# =============================================================================

import customtkinter as ctk

import config                                   # -> config.py
from core.layout import Karte, Responsive, WrapLabel   # -> core/layout.py
from programmieren.engine import syntax         # -> engine/syntax.py

UMBRUCH_AB = 620            # schmaler als das (Pixel) -> Erklärung unter den Befehl


class BefehlsListe(Karte, Responsive):

    def __init__(self, master, titel, zeilen):
        super().__init__(master, titel=titel)
        self.bl_zeilen = []                     # (knopf, befehl_label, erklaerung_label)
        self.bl_schmal = None                   # noch kein Layout gewählt
        code = config.CODE_FARBEN[ctk.get_appearance_mode()]
        b = self.body
        b.grid_columnconfigure(0, weight=0)
        b.grid_columnconfigure(1, weight=0)
        b.grid_columnconfigure(2, weight=1)

        for befehl, erklaerung in zeilen:
            gefahr = syntax.ist_gefaehrlich(befehl)
            knopf = ctk.CTkButton(b, text="📋", width=34, height=26, font=config.FONT_KLEIN,
                                  fg_color="transparent", border_width=1, border_color=config.FARBEN["rahmen"],
                                  text_color=config.FARBEN["text_leise"], hover_color=config.FARBEN["rahmen"])
            knopf.configure(command=lambda k=knopf, t=befehl: self._kopieren(k, t))
            befehl_label = ctk.CTkLabel(
                b, text=("⚠ " if gefahr else "") + befehl, anchor="w", justify="left",
                font=(config.SCHRIFT_CODE, 13, "bold"), corner_radius=6,
                fg_color=code["gefahr_bg"] if gefahr else code["hintergrund"],
                text_color=code["gefahr"] if gefahr else code["text"])
            erklaerung_label = WrapLabel(b, text=erklaerung, font=config.FONT_TEXT,
                                         text_color=config.FARBEN["text"])
            self.bl_zeilen.append((knopf, befehl_label, erklaerung_label))

        self._anordnen(schmal=False)
        self.responsive_starten()               # -> core/layout.py

    # -------------------------------------------------------------------------
    def _anordnen(self, schmal):
        """Breit: [📋][Befehl][Erklärung]   Schmal: [📋][Befehl] / darunter Erklärung."""
        if schmal == self.bl_schmal:
            return
        self.bl_schmal = schmal
        for i, (knopf, befehl, erklaerung) in enumerate(self.bl_zeilen):
            zeile = i * 2 if schmal else i
            knopf.grid(row=zeile, column=0, sticky="nw", padx=(0, 8), pady=(4, 0))
            befehl.grid(row=zeile, column=1, columnspan=2 if schmal else 1, sticky="w", pady=(4, 0), ipadx=6)
            if schmal:
                erklaerung.grid(row=zeile + 1, column=1, columnspan=2, sticky="ew", pady=(0, 4))
            else:
                erklaerung.grid(row=zeile, column=2, sticky="ew", padx=(14, 0), pady=(4, 0))

    def anpassen(self, breite):
        self._anordnen(schmal=breite / self._skalierung() < UMBRUCH_AB)

    def _kopieren(self, knopf, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        knopf.configure(text="✅")
        self.after(1200, lambda: knopf.winfo_exists() and knopf.configure(text="📋"))
