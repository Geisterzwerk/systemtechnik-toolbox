# =============================================================================
# gui/messtechnik_gui.py
# -----------------------------------------------------------------------------
# Der Bereich MESSTECHNIK - gleiches Wiki-System wie Bauteile und Programmieren.
#
#   ┌──────────────────────────────────────────────────────────────┐
#   │ ⬅  🏠  ◀   🔍 [ Suche .... z.B. Pt100, Oszilloskop, Aliasing ]│
#   ├───────────────────┬──────────────────────────────────────────┤
#   │ 📐 Grundlagen   ▾ │  Seite  [ 📖 Wissen | 🧮 Rechner ]        │
#   │ 🔬 Messgeräte   ▾ │                                           │
#   └───────────────────┴──────────────────────────────────────────┘
#
# WER RUFT DAS AUF?  main.py -> messtechnik_gui.create(tab, app)
# BENUTZT:
#   programmieren/engine/lader.py  -> lädt die Seiten aus messtechnik/inhalte/
#   programmieren/engine/suche.py  -> Suche
#   bauteile/engine/seite.py       -> zeichnet eine Seite (Wissen / Rechner)
#
# NEUE SEITE: Datei in messtechnik/inhalte/<kategorie>/ anlegen (Vorlage:
#             bauteile/inhalte/_vorlage.py) -> erscheint automatisch.
# =============================================================================

import os

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile.engine.seite import BauteilSeite                         # -> bauteile/engine/seite.py
from core.layout import Karte, ResponsiveGrid, ScrollSeite, Stapel, seiten_kopf   # -> core/layout.py
from core.widgets import Tooltip, info_box                             # -> core/widgets.py
from programmieren.engine import lader                                 # -> programmieren/engine/lader.py
from programmieren.engine.suche import Suchmaschine                    # -> programmieren/engine/suche.py

INHALTE_PFAD = os.path.join(config.BASIS_PFAD, "messtechnik", "inhalte")


def create(parent, app):
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    wiki = MesstechnikWiki(parent, app)
    wiki.grid(row=0, column=0, sticky="nsew")
    return wiki


def uebersicht_zeichnen(master, kategorien, oeffnen, ladefehler=None):
    """Startansicht: alle Kategorien als Karten."""
    s = Stapel(master)
    anzahl = sum(len(k.themen) for k in kategorien)
    seiten_kopf(s, "📏 Messtechnik",
                f"{anzahl} Themen in {len(kategorien)} Kategorien  ·  Messgeräte, Messfehler, Sensoren, AD-Wandler")
    if ladefehler:
        s.add(info_box(master, "⚠️ Einige Seiten konnten nicht geladen werden", ladefehler, art="warnung"))
    grid = s.add(ResponsiveGrid(master, min_spaltenbreite=340, max_spalten=2))
    for kat in kategorien:
        kasten = grid.add(Karte(grid, titel=f"{kat.icon}  {kat.name}", untertitel=kat.beschreibung or None))
        for zeile, thema in enumerate(kat.themen):
            anzahl_r = len(thema.daten.get("rechner", []))
            ctk.CTkButton(kasten.body, text=f"  {thema.titel}" + (f"   ·  🧮 {anzahl_r}" if anzahl_r else ""),
                          anchor="w", height=28, fg_color="transparent", hover_color=config.FARBEN["rahmen"],
                          text_color=config.FARBEN["akzent"],
                          command=lambda t=thema: oeffnen(t.id)).grid(row=zeile, column=0, sticky="ew", pady=1)


class MesstechnikWiki(ctk.CTkFrame):

    def __init__(self, master, app):
        super().__init__(master, fg_color=config.FARBEN["hintergrund"], corner_radius=0)
        self.app = app
        self.ansicht = "wissen"
        self.aktuelles_thema = None
        self.verlauf = []
        self.themen_buttons = {}

        # ---- Daten laden + Suche ----
        self.kategorien, self.themen, self.ladefehler = lader.alle_laden(INHALTE_PFAD)
        for fehler in self.ladefehler:
            print("[Messtechnik] Ladefehler:", fehler)
        self.suchmaschine = Suchmaschine(self.themen)
        self.offene_kategorien = {k.ordner for k in self.kategorien}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._kopfleiste()
        self.navigation = ctk.CTkScrollableFrame(self, width=230, corner_radius=0, fg_color=config.FARBEN["sidebar"])
        self.navigation.grid(row=1, column=0, sticky="nsw")
        self.navigation.grid_columnconfigure(0, weight=1)
        self.inhalt = ScrollSeite(self)
        self.inhalt.grid(row=1, column=1, sticky="nsew")

        self._baum_zeichnen()
        self._uebersicht_zeigen()

    # ---- Kopfleiste ----
    def _kopfleiste(self):
        leiste = ctk.CTkFrame(self, fg_color=config.FARBEN["sidebar"], corner_radius=0)
        leiste.grid(row=0, column=0, columnspan=2, sticky="ew")
        leiste.grid_columnconfigure(3, weight=1)
        rahmen = dict(fg_color="transparent", border_width=1, border_color=config.FARBEN["rahmen"],
                      text_color=config.FARBEN["text"])
        for spalte, (text, befehl, tipp, stil) in enumerate([
                ("⬅", self.app.show_startseite, "Zur Startseite", {}),
                ("🏠", self._uebersicht_zeigen, "Übersicht Messtechnik", rahmen),
                ("◀", self._zurueck, "Vorherige Seite", rahmen)]):
            knopf = ctk.CTkButton(leiste, text=text, width=40, height=36, command=befehl, **stil)
            knopf.grid(row=0, column=spalte, padx=(10 if spalte == 0 else 4, 4), pady=10)
            Tooltip(knopf, tipp)
        self.suchfeld = ctk.CTkEntry(leiste, height=36, width=120, font=config.FONT_TEXT,
                                     placeholder_text="🔍  Suchen ... z.B. Pt100, Oszilloskop, True RMS, Aliasing")
        self.suchfeld.grid(row=0, column=3, sticky="ew", padx=(10, 12))
        self.suchfeld.bind("<KeyRelease>", self._suche)
        self.suchfeld.bind("<Return>", self._suche_enter)
        self.suchfeld.bind("<Escape>", lambda e: self._suche_leeren())

    # ---- Navigation ----
    def _nav_leeren(self):
        for kind in self.navigation.winfo_children():
            kind.destroy()
        self.themen_buttons = {}

    def _baum_zeichnen(self):
        self._nav_leeren()
        zeile = 0
        for kat in self.kategorien:
            offen = kat.ordner in self.offene_kategorien
            ctk.CTkButton(self.navigation, text=f"{kat.icon}  {kat.name}   {'▾' if offen else '▸'}", anchor="w",
                          height=34, font=(config.SCHRIFT, 13, "bold"), fg_color="transparent",
                          text_color=config.FARBEN["text"], hover_color=config.FARBEN["rahmen"],
                          command=lambda k=kat: self._umschalten(k)).grid(row=zeile, column=0, sticky="ew",
                                                                         padx=4, pady=(6, 0))
            zeile += 1
            if offen:
                for thema in kat.themen:
                    zeile = self._themen_knopf(thema, zeile)
        self._markieren()

    def _themen_knopf(self, thema, zeile, mit_kategorie=False):
        text = f"{thema.kategorie.icon}  {thema.titel}" if mit_kategorie else f"      {thema.titel}"
        knopf = ctk.CTkButton(self.navigation, text=text, anchor="w", height=28, font=config.FONT_TEXT,
                              fg_color="transparent", text_color=config.FARBEN["text"],
                              hover_color=config.FARBEN["rahmen"], command=lambda t=thema: self.thema_oeffnen(t.id))
        knopf.grid(row=zeile, column=0, sticky="ew", padx=4, pady=1)
        self.themen_buttons[thema.id] = knopf
        return zeile + 1

    def _umschalten(self, kategorie):
        self.offene_kategorien ^= {kategorie.ordner}
        self._baum_zeichnen()

    def _markieren(self):
        for thema_id, knopf in self.themen_buttons.items():
            aktiv = thema_id == self.aktuelles_thema
            knopf.configure(fg_color=config.FARBEN["akzent"] if aktiv else "transparent",
                            text_color="white" if aktiv else config.FARBEN["text"])

    # ---- Suche ----
    def _suche(self, event=None):
        if event is not None and event.keysym in ("Return", "Escape", "Up", "Down", "Left", "Right"):
            return
        anfrage = self.suchfeld.get().strip()
        if not anfrage:
            self._baum_zeichnen()
            return
        treffer = self.suchmaschine.suchen(anfrage)
        self._nav_leeren()
        ctk.CTkLabel(self.navigation, text=f"🔍 {len(treffer)} Treffer", anchor="w", font=(config.SCHRIFT, 12, "bold"),
                     text_color=config.FARBEN["text_leise"]).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        zeile = 1
        for thema in treffer:
            zeile = self._themen_knopf(thema, zeile, mit_kategorie=True)
        self._markieren()

    def _suche_enter(self, event=None):
        treffer = self.suchmaschine.suchen(self.suchfeld.get())
        if treffer:
            self.thema_oeffnen(treffer[0].id)

    def _suche_leeren(self):
        self.suchfeld.delete(0, "end")
        self._baum_zeichnen()

    # ---- Inhalt ----
    def _uebersicht_zeigen(self):
        self.aktuelles_thema = None
        self._markieren()
        uebersicht_zeichnen(self.inhalt.neue_seite(), self.kategorien, self.thema_oeffnen, self.ladefehler)

    def thema_oeffnen(self, thema_id, verlauf_merken=True):
        thema = self.themen.get(thema_id)
        if thema is None:
            return
        if verlauf_merken and self.aktuelles_thema and self.aktuelles_thema != thema_id:
            self.verlauf = (self.verlauf + [self.aktuelles_thema])[-30:]
        self.aktuelles_thema = thema_id
        self._markieren()
        # -> bauteile/engine/seite.py (dieselbe Seitendarstellung wie bei den Bauteilen)
        BauteilSeite(self.inhalt.neue_seite(), thema, self.ansicht, self.themen, self.thema_oeffnen,
                     self._ansicht_setzen)

    def _ansicht_setzen(self, ansicht):
        self.ansicht = ansicht
        if self.aktuelles_thema:
            self.thema_oeffnen(self.aktuelles_thema, verlauf_merken=False)

    def _zurueck(self):
        if self.verlauf:
            self.thema_oeffnen(self.verlauf.pop(), verlauf_merken=False)
        else:
            self._uebersicht_zeigen()
