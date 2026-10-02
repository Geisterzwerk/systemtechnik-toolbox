# =============================================================================
# bauteile/engine/wiki_bereich.py
# -----------------------------------------------------------------------------
# EIN Wiki-Bereich mit Suche, Kategorie-Baum links und Seite rechts.
# Benutzt von den Tabs Bauteile, Messtechnik und Schaltungen - vorher war das
# dreimal fast gleich kopiert, jetzt steht es nur noch hier.
#
#   ┌──────────────────────────────────────────────────────────────┐
#   │ ⬅  🏠  ◀   🔍 [ Suche .... ]                                  │
#   ├───────────────────┬──────────────────────────────────────────┤
#   │ 🔌 Kategorie    ▾ │  Seite  [ 📖 Wissen | 🧮 Rechner ]        │
#   │    Thema          │                                           │
#   └───────────────────┴──────────────────────────────────────────┘
#
# BENUTZUNG (in gui/<bereich>_gui.py):
#   WikiBereich(parent, app, inhalte_pfad, titel="🔧 Bauteile",
#               beschreibung="Wissen, Kniffe und Rechner", suchtext="z.B. Farbcode, LED")
#
# WER RUFT DAS AUF?  gui/bauteile_gui.py, gui/messtechnik_gui.py, gui/schaltungen_gui.py,
#                    gui/digitaltechnik_gui.py
# BENUTZT:
#   programmieren/engine/lader.py  -> lädt die Seiten (Ordner mit THEMA-Dateien)
#   programmieren/engine/suche.py  -> Suche mit Tippfehler-Toleranz
#   bauteile/engine/seite.py       -> zeichnet eine Seite (Wissen / Rechner)
# =============================================================================

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile.engine.seite import BauteilSeite                         # -> bauteile/engine/seite.py
from core.layout import Karte, ResponsiveGrid, ScrollSeite, Stapel, seiten_kopf   # -> core/layout.py
from core.widgets import Tooltip, info_box                             # -> core/widgets.py
from programmieren.engine import lader                                 # -> programmieren/engine/lader.py
from programmieren.engine.suche import Suchmaschine                    # -> programmieren/engine/suche.py


def uebersicht_zeichnen(master, kategorien, oeffnen, titel, beschreibung, ladefehler=None):
    """Startansicht eines Bereichs: alle Kategorien als Karten mit ihren Themen."""
    s = Stapel(master)
    anzahl = sum(len(k.themen) for k in kategorien)
    seiten_kopf(s, titel, f"{anzahl} Themen in {len(kategorien)} Kategorien  ·  {beschreibung}")
    if ladefehler:
        s.add(info_box(master, "⚠️ Einige Seiten konnten nicht geladen werden", ladefehler, art="warnung"))
    grid = s.add(ResponsiveGrid(master, min_spaltenbreite=340, max_spalten=2))
    for kat in kategorien:
        kasten = grid.add(Karte(grid, titel=f"{kat.icon}  {kat.name}", untertitel=kat.beschreibung or None))
        for zeile, thema in enumerate(kat.themen):
            anzahl_r = len(thema.daten.get("rechner", []))
            zusatz = f"   ·  🧮 {anzahl_r}" if anzahl_r else ""
            ctk.CTkButton(kasten.body, text=f"  {thema.titel}{zusatz}", anchor="w", height=28,
                          fg_color="transparent", hover_color=config.FARBEN["rahmen"],
                          text_color=config.FARBEN["akzent"],
                          command=lambda t=thema: oeffnen(t.id)).grid(row=zeile, column=0, sticky="ew", pady=1)


class WikiBereich(ctk.CTkFrame):
    """
    Attribute, die andere Tabs benutzen (z.B. der Rechner-Tab für "📖 Erklärung"):
      ansicht            "wissen" oder "rechner" (bleibt beim Themenwechsel)
      thema_oeffnen(id)  öffnet eine Seite
      aktuelles_thema    ID der offenen Seite (oder None)
    """

    def __init__(self, master, app, inhalte_pfad, titel, beschreibung, suchtext):
        super().__init__(master, fg_color=config.FARBEN["hintergrund"], corner_radius=0)
        self.app = app
        self.titel = titel
        self.beschreibung = beschreibung
        self.ansicht = "wissen"
        self.aktuelles_thema = None
        self.verlauf = []
        self.themen_buttons = {}

        # ---- Daten laden + Suche ----
        self.kategorien, self.themen, self.ladefehler = lader.alle_laden(inhalte_pfad)
        for fehler in self.ladefehler:
            print(f"[{titel}] Ladefehler:", fehler)
        self.suchmaschine = Suchmaschine(self.themen)
        self.offene_kategorien = {k.ordner for k in self.kategorien}   # alle aufgeklappt

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._kopfleiste(suchtext)
        self.navigation = ctk.CTkScrollableFrame(self, width=230, corner_radius=0, fg_color=config.FARBEN["sidebar"])
        self.navigation.grid(row=1, column=0, sticky="nsw")
        self.navigation.grid_columnconfigure(0, weight=1)
        self.inhalt = ScrollSeite(self)                                # -> core/layout.py
        self.inhalt.grid(row=1, column=1, sticky="nsew")

        self._baum_zeichnen()
        self._uebersicht_zeigen()

    # =========================================================================
    # KOPFLEISTE
    # =========================================================================
    def _kopfleiste(self, suchtext):
        leiste = ctk.CTkFrame(self, fg_color=config.FARBEN["sidebar"], corner_radius=0)
        leiste.grid(row=0, column=0, columnspan=2, sticky="ew")
        leiste.grid_columnconfigure(3, weight=1)
        rahmen = dict(fg_color="transparent", border_width=1, border_color=config.FARBEN["rahmen"],
                      text_color=config.FARBEN["text"])
        for spalte, (text, befehl, tipp, stil) in enumerate([
                ("⬅", self.app.show_startseite, "Zur Startseite", {}),
                ("🏠", self._uebersicht_zeigen, "Übersicht", rahmen),
                ("◀", self._zurueck, "Vorherige Seite", rahmen)]):
            knopf = ctk.CTkButton(leiste, text=text, width=40, height=36, command=befehl, **stil)
            knopf.grid(row=0, column=spalte, padx=(10 if spalte == 0 else 4, 4), pady=10)
            Tooltip(knopf, tipp)
        self.suchfeld = ctk.CTkEntry(leiste, height=36, width=120, font=config.FONT_TEXT,
                                     placeholder_text=f"🔍  Suchen ... {suchtext}")
        self.suchfeld.grid(row=0, column=3, sticky="ew", padx=(10, 12))
        self.suchfeld.bind("<KeyRelease>", self._suche)
        self.suchfeld.bind("<Return>", self._suche_enter)
        self.suchfeld.bind("<Escape>", lambda e: self._suche_leeren())

    # =========================================================================
    # NAVIGATION
    # =========================================================================
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

    # =========================================================================
    # SUCHE
    # =========================================================================
    def _suche(self, event=None):
        if event is not None and event.keysym in ("Return", "Escape", "Up", "Down", "Left", "Right"):
            return
        anfrage = self.suchfeld.get().strip()
        if not anfrage:
            self._baum_zeichnen()
            return
        treffer = self.suchmaschine.suchen(anfrage)            # -> programmieren/engine/suche.py
        self._nav_leeren()
        ctk.CTkLabel(self.navigation, text=f"🔍 {len(treffer)} Treffer", anchor="w", font=(config.SCHRIFT, 12, "bold"),
                     text_color=config.FARBEN["text_leise"]).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        if not treffer:
            ctk.CTkLabel(self.navigation, text="Nichts gefunden.", anchor="w",
                         text_color=config.FARBEN["text_leise"]).grid(row=1, column=0, sticky="w", padx=8)
            return
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

    # =========================================================================
    # INHALT
    # =========================================================================
    def _uebersicht_zeigen(self):
        self.aktuelles_thema = None
        self._markieren()
        uebersicht_zeichnen(self.inhalt.neue_seite(), self.kategorien, self.thema_oeffnen,
                            self.titel, self.beschreibung, self.ladefehler)

    def thema_oeffnen(self, thema_id, verlauf_merken=True):
        thema = self.themen.get(thema_id)
        if thema is None:
            return
        if verlauf_merken and self.aktuelles_thema and self.aktuelles_thema != thema_id:
            self.verlauf = (self.verlauf + [self.aktuelles_thema])[-30:]
        self.aktuelles_thema = thema_id
        if thema.kategorie.ordner not in self.offene_kategorien and not self.suchfeld.get().strip():
            self.offene_kategorien.add(thema.kategorie.ordner)
            self._baum_zeichnen()
        self._markieren()
        # -> bauteile/engine/seite.py (dieselbe Seitendarstellung in allen Wiki-Bereichen)
        BauteilSeite(self.inhalt.neue_seite(), thema, self.ansicht, self.themen, self.thema_oeffnen,
                     self._ansicht_setzen)

    def _ansicht_setzen(self, ansicht):
        """Umschalter Wissen | Rechner wurde geklickt."""
        self.ansicht = ansicht
        if self.aktuelles_thema:
            self.thema_oeffnen(self.aktuelles_thema, verlauf_merken=False)

    def _zurueck(self):
        if self.verlauf:
            self.thema_oeffnen(self.verlauf.pop(), verlauf_merken=False)
        else:
            self._uebersicht_zeigen()
