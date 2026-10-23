# =============================================================================
# gui/gesamtsuche.py
# -----------------------------------------------------------------------------
# SUCHE ÜBER ALLES (Startseite): Wissensseiten aller Bereiche, Programmieren, Server und alle Rechner.
#
#   gesamtindex()        (aus core/inhalte_index.py) {schluessel: Eintrag} + Infos je Bereich
#   oeffnen(app, e)      springt in den richtigen Tab und öffnet Seite oder Rechner
#   eintrag_dict(e)      Eintrag als dict für core/benutzerdaten.py (Zuletzt / Favoriten)
#   SuchLeiste(master, app)   grosses Suchfeld mit Trefferliste darunter (Enter = erster Treffer)
#
# Die Suchlogik (Punkte, Tippfehler-Toleranz) ist dieselbe wie in den Bereichen:
#   programmieren/engine/suche.py -> Suchmaschine  (hier nur mit allen Einträgen zusammen)
# WER RUFT DAS AUF?  gui/startseite_gui.py
# =============================================================================

import customtkinter as ctk

import config                                                          # -> config.py
# Index und Suche ohne Fenster (auch für die Webversion) -> core/inhalte_index.py
from core.inhalte_index import (BEREICH_ICON, BEREICH_ORDNER, Eintrag,  # noqa: F401 (von startseite_gui benutzt)
                                eintrag_dict, gesamtindex, interaktiv)

def oeffnen(app, eintrag):
    """eintrag: Eintrag-Objekt oder dict (aus Zuletzt/Favoriten)."""
    art = eintrag["art"] if isinstance(eintrag, dict) else eintrag.art
    bereich = eintrag["bereich"] if isinstance(eintrag, dict) else eintrag.bereich
    eid = eintrag["id"] if isinstance(eintrag, dict) else eintrag.id
    app.show_tab(bereich)                                    # baut den Tab beim ersten Mal (main.py)
    seite = app.seiten.get(bereich)
    if seite is None:
        return
    if art == "rechner":
        seite.rechner_oeffnen(eid)
    else:
        if hasattr(seite, "ansicht"):
            seite.ansicht = "wissen"
        seite.thema_oeffnen(eid)


# =============================================================================
# SUCHLEISTE MIT TREFFERLISTE
# =============================================================================
class SuchLeiste(ctk.CTkFrame):
    MAX_TREFFER = 9

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.gs_feld = ctk.CTkEntry(self, height=46, font=(config.SCHRIFT, 16), corner_radius=23,
                                    border_width=2, border_color=config.FARBEN["akzent"],
                                    placeholder_text="🔍  In allen Bereichen suchen …  z.B. Tiefpass, chmod, "
                                                     "while-Schleife, Pt100, NE555   (Ctrl+K)")
        self.gs_feld.grid(row=0, column=0, sticky="ew")
        self.gs_feld.bind("<KeyRelease>", self._gs_tippen)
        self.gs_feld.bind("<Return>", self._gs_enter)
        self.gs_feld.bind("<Escape>", lambda _e: self.leeren())
        self.gs_liste = ctk.CTkFrame(self, fg_color=config.FARBEN["flaeche"], corner_radius=12, border_width=1,
                                     border_color=config.FARBEN["rahmen"])
        self.gs_liste.grid_columnconfigure(0, weight=1)
        self.gs_treffer = []

    def fokus(self):
        """Ins Suchfeld springen; vorhandener Text wird markiert (gleich lostippen = ersetzen)."""
        self.gs_feld.focus_set()
        if self.gs_feld.get():
            self.gs_feld.select_range(0, "end")
            self.gs_feld.icursor("end")

    def leeren(self):
        self.gs_feld.delete(0, "end")
        self._gs_zeigen([])

    def _gs_tippen(self, event=None):
        if event is not None and event.keysym in ("Return", "Escape", "Up", "Down", "Left", "Right"):
            return
        anfrage = self.gs_feld.get().strip()
        treffer = gesamtindex()["suche"].suchen(anfrage, max_treffer=self.MAX_TREFFER) if anfrage else []
        self._gs_zeigen(treffer, anfrage)

    def _gs_enter(self, _event=None):
        if self.gs_treffer:
            self._gs_oeffnen(self.gs_treffer[0])

    def _gs_oeffnen(self, eintrag):
        self.leeren()
        oeffnen(self.app, eintrag)

    def _gs_zeigen(self, treffer, anfrage=""):
        self.gs_treffer = treffer
        for kind in self.gs_liste.winfo_children():
            kind.destroy()
        if not anfrage:
            self.gs_liste.grid_forget()
            return
        self.gs_liste.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        if not treffer:
            ctk.CTkLabel(self.gs_liste, text=f"Nichts gefunden für „{anfrage}“ – anderes Wort oder kürzer versuchen.",
                         font=config.FONT_TEXT, text_color=config.FARBEN["text_leise"]).grid(
                row=0, column=0, sticky="w", padx=16, pady=10)
            return
        for zeile, e in enumerate(treffer):
            rahmen = ctk.CTkFrame(self.gs_liste, fg_color="transparent", corner_radius=0)
            rahmen.grid(row=zeile, column=0, sticky="ew", padx=6, pady=(6 if zeile == 0 else 0, 0))
            rahmen.grid_columnconfigure(0, weight=1)
            knopf = ctk.CTkButton(rahmen, text=f"{e.icon}  {e.titel}", anchor="w", height=32,
                                  font=(config.SCHRIFT, 14, "bold" if zeile == 0 else "normal"),
                                  fg_color=config.FARBEN["tipp"] if zeile == 0 else "transparent",
                                  text_color=config.FARBEN["text"], hover_color=config.FARBEN["rahmen"],
                                  command=lambda e=e: self._gs_oeffnen(e))
            knopf.grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(rahmen, text=f"{BEREICH_ICON.get(e.bereich, '')} {e.ort}", font=config.FONT_KLEIN,
                         text_color=config.FARBEN["text_leise"]).grid(row=0, column=1, sticky="e", padx=(8, 10))
        ctk.CTkLabel(self.gs_liste, text="Enter öffnet den ersten Treffer  ·  Esc leert die Suche",
                     font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"]).grid(
            row=len(treffer), column=0, sticky="w", padx=16, pady=(4, 8))
