# =============================================================================
# gui/programmieren_gui.py
# -----------------------------------------------------------------------------
# Die PROGRAMMIER-SEITE (Programmier-Wiki).
#
#   ┌──────────────────────────────────────────────────────────────────────┐
#   │ ⬅  🏠  ◀   🔍 [ Suche ........ wächst mit ........ ]  [Py|C++|C#|Alle]│  <- Kopfleiste
#   ├───────────────────┬──────────────────────────────────────────────────┤
#   │ Navigation        │  Inhalt (ScrollSeite -> wächst mit, zentriert    │
#   │ (feste Breite)    │  ab config.INHALT_MAX_BREITE)                    │
#   └───────────────────┴──────────────────────────────────────────────────┘
#
# WER RUFT DAS AUF?  main.py -> programmieren_gui.create(tab, app)
# BENUTZT:
#   programmieren/engine/lader.py   -> alle Themen laden
#   programmieren/engine/suche.py   -> Suchfunktion
#   programmieren/engine/seite.py   -> eine Seite zeichnen
#   core/layout.py                  -> ScrollSeite (Inhalt, responsive)
# =============================================================================

import customtkinter as ctk

import config                                                            # -> config.py
from core.layout import ScrollSeite                                      # -> core/layout.py
from core.widgets import Tooltip                                         # -> core/widgets.py
from programmieren.engine import lader                                   # -> engine/lader.py
from programmieren.engine.seite import ThemenSeite, uebersicht_zeichnen  # -> engine/seite.py
from programmieren.engine.suche import Suchmaschine                      # -> engine/suche.py


def create(parent, app):
    """Wird von main.py aufgerufen (parent = Tab "Programmieren")."""
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    seite = ProgrammierSeite(parent, app)          # -> Klasse unten
    seite.grid(row=0, column=0, sticky="nsew")
    return seite


class ProgrammierSeite(ctk.CTkFrame):

    def __init__(self, master, app):
        super().__init__(master, fg_color=config.FARBEN["hintergrund"], corner_radius=0)
        self.app = app
        self.sprache = config.STANDARD_SPRACHE
        self.aktuelles_thema = None
        self.verlauf = []
        self.offene_kategorien = set()
        self.themen_buttons = {}

        # ---- Daten laden + Suche vorbereiten ----
        self.kategorien, self.themen, self.ladefehler = lader.alle_laden()
        for fehler in self.ladefehler:
            print("[Programmieren] Ladefehler:", fehler)
        self.suchmaschine = Suchmaschine(self.themen)

        # ---- Layout: Zeile 0 Kopfleiste, Zeile 1 = Navigation (fix) + Inhalt (wächst) ----
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._kopfleiste_erstellen()
        self._navigation_erstellen()
        # Inhalt -> core/layout.py ScrollSeite (EIN Objekt, Seiten werden darin getauscht)
        self.inhalt = ScrollSeite(self)
        self.inhalt.grid(row=1, column=1, sticky="nsew")

        if self.kategorien:
            self.offene_kategorien.add(self.kategorien[0].ordner)
        self._navigation_baum_zeichnen()
        self._uebersicht_zeigen()

    # =========================================================================
    # KOPFLEISTE
    # =========================================================================
    def _kopfleiste_erstellen(self):
        leiste = ctk.CTkFrame(self, fg_color=config.FARBEN["sidebar"], corner_radius=0)
        leiste.grid(row=0, column=0, columnspan=2, sticky="ew")
        leiste.grid_columnconfigure(3, weight=1)          # NUR das Suchfeld wächst mit

        rahmen = dict(fg_color="transparent", border_width=1, border_color=config.FARBEN["rahmen"],
                      text_color=config.FARBEN["text"])
        btn_start = ctk.CTkButton(leiste, text="⬅", width=40, height=36, command=self.app.show_startseite)
        btn_start.grid(row=0, column=0, padx=(10, 4), pady=10)
        Tooltip(btn_start, "Zur Startseite")
        btn_home = ctk.CTkButton(leiste, text="🏠", width=40, height=36, command=self._uebersicht_zeigen, **rahmen)
        btn_home.grid(row=0, column=1, padx=4)
        Tooltip(btn_home, "Übersicht aller Themen")
        btn_zurueck = ctk.CTkButton(leiste, text="◀", width=40, height=36, command=self._verlauf_zurueck, **rahmen)
        btn_zurueck.grid(row=0, column=2, padx=4)
        Tooltip(btn_zurueck, "Vorheriges Thema")

        # ---- Suchfeld (sticky="ew" + weight=1 -> füllt den freien Platz) ----
        self.suchfeld = ctk.CTkEntry(leiste, height=36, width=120, font=config.FONT_TEXT,
                                     placeholder_text="🔍  Suchen ... z.B. while, if else, int, klasse  (Ctrl+F)")
        self.suchfeld.grid(row=0, column=3, sticky="ew", padx=10)
        self.suchfeld.bind("<KeyRelease>", self._suche_geaendert)
        self.suchfeld.bind("<Return>", self._suche_enter)
        self.suchfeld.bind("<Escape>", lambda e: self._suche_leeren())
        self.winfo_toplevel().bind("<Control-f>", lambda e: self.suchfeld.focus_set(), add="+")

        # ---- Sprachwahl (behält ihre Grösse) ----
        self.sprachwahl = ctk.CTkSegmentedButton(leiste, values=config.SPRACHEN + ["Alle"],
                                                 command=self._sprache_geaendert, height=36,
                                                 font=(config.SCHRIFT, 13, "bold"))
        self.sprachwahl.set(self.sprache)
        self.sprachwahl.grid(row=0, column=4, padx=(4, 12))

    # =========================================================================
    # NAVIGATION LINKS
    # =========================================================================
    def _navigation_erstellen(self):
        self.navigation = ctk.CTkScrollableFrame(self, width=240, corner_radius=0,
                                                 fg_color=config.FARBEN["sidebar"])
        self.navigation.grid(row=1, column=0, sticky="nsw")
        self.navigation.grid_columnconfigure(0, weight=1)

    def _navigation_leeren(self):
        for kind in self.navigation.winfo_children():
            kind.destroy()
        self.themen_buttons = {}

    def _navigation_baum_zeichnen(self):
        self._navigation_leeren()
        zeile = 0
        for kat in self.kategorien:
            offen = kat.ordner in self.offene_kategorien
            ctk.CTkButton(self.navigation, text=f"{kat.icon}  {kat.name}   {'▾' if offen else '▸'}",
                          anchor="w", height=34, font=(config.SCHRIFT, 13, "bold"), fg_color="transparent",
                          text_color=config.FARBEN["text"], hover_color=config.FARBEN["rahmen"],
                          command=lambda k=kat: self._kategorie_umschalten(k)).grid(
                row=zeile, column=0, sticky="ew", padx=4, pady=(6, 0))
            zeile += 1
            if offen:
                for thema in kat.themen:
                    zeile = self._themen_button(thema, zeile)
        self._aktiv_markieren()

    def _themen_button(self, thema, zeile, mit_kategorie=False):
        text = f"{thema.kategorie.icon}  {thema.titel}" if mit_kategorie else f"      {thema.titel}"
        button = ctk.CTkButton(self.navigation, text=text, anchor="w", height=28, font=config.FONT_TEXT,
                               fg_color="transparent", text_color=config.FARBEN["text"],
                               hover_color=config.FARBEN["rahmen"],
                               command=lambda t=thema: self.thema_oeffnen(t.id))
        button.grid(row=zeile, column=0, sticky="ew", padx=4, pady=1)
        self.themen_buttons[thema.id] = button
        return zeile + 1

    def _kategorie_umschalten(self, kategorie):
        self.offene_kategorien ^= {kategorie.ordner}        # an/aus
        self._navigation_baum_zeichnen()

    def _aktiv_markieren(self):
        for thema_id, button in self.themen_buttons.items():
            aktiv = thema_id == self.aktuelles_thema
            button.configure(fg_color=config.FARBEN["akzent"] if aktiv else "transparent",
                             text_color="white" if aktiv else config.FARBEN["text"])

    # =========================================================================
    # SUCHE
    # =========================================================================
    def _suche_geaendert(self, event=None):
        if event is not None and event.keysym in ("Return", "Escape", "Up", "Down", "Left", "Right"):
            return
        anfrage = self.suchfeld.get().strip()
        if not anfrage:
            self._navigation_baum_zeichnen()
            return
        treffer = self.suchmaschine.suchen(anfrage)          # -> engine/suche.py
        self._navigation_leeren()
        ctk.CTkLabel(self.navigation, text=f"🔍 {len(treffer)} Treffer", anchor="w",
                     font=(config.SCHRIFT, 12, "bold"), text_color=config.FARBEN["text_leise"]).grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        if not treffer:
            ctk.CTkLabel(self.navigation, text="Nichts gefunden.\nAnderes Stichwort versuchen.",
                         justify="left", anchor="w", text_color=config.FARBEN["text_leise"]).grid(
                row=1, column=0, sticky="w", padx=8)
            return
        zeile = 1
        for thema in treffer:
            zeile = self._themen_button(thema, zeile, mit_kategorie=True)
        self._aktiv_markieren()

    def _suche_enter(self, event=None):
        treffer = self.suchmaschine.suchen(self.suchfeld.get())
        if treffer:
            self.thema_oeffnen(treffer[0].id)

    def _suche_leeren(self):
        self.suchfeld.delete(0, "end")
        self._navigation_baum_zeichnen()

    # =========================================================================
    # INHALT
    # =========================================================================
    def _uebersicht_zeigen(self):
        self.aktuelles_thema = None
        self._aktiv_markieren()
        body = self.inhalt.neue_seite()                      # -> core/layout.py
        uebersicht_zeichnen(body, self.kategorien, self.thema_oeffnen, self.ladefehler)   # -> engine/seite.py

    def thema_oeffnen(self, thema_id, verlauf_merken=True):
        thema = self.themen.get(thema_id)
        if thema is None:
            return
        if verlauf_merken and self.aktuelles_thema and self.aktuelles_thema != thema_id:
            self.verlauf = (self.verlauf + [self.aktuelles_thema])[-30:]
        self.aktuelles_thema = thema_id

        if thema.kategorie.ordner not in self.offene_kategorien and not self.suchfeld.get().strip():
            self.offene_kategorien.add(thema.kategorie.ordner)
            self._navigation_baum_zeichnen()
        self._aktiv_markieren()

        body = self.inhalt.neue_seite()                      # alte Seite weg, nach oben scrollen
        ThemenSeite(body, thema, self.sprache, self.themen, self.thema_oeffnen)   # -> engine/seite.py

    def _verlauf_zurueck(self):
        if self.verlauf:
            self.thema_oeffnen(self.verlauf.pop(), verlauf_merken=False)
        else:
            self._uebersicht_zeigen()

    def _sprache_geaendert(self, neue_sprache):
        self.sprache = neue_sprache
        if self.aktuelles_thema:
            self.thema_oeffnen(self.aktuelles_thema, verlauf_merken=False)
