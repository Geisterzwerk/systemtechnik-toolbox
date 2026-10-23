# =============================================================================
# gui/programmieren_gui.py
# -----------------------------------------------------------------------------
# Die PROGRAMMIER-SEITE (Programmier-Wiki).
#
#   ┌──────────────────────────────────────────────────────────────────────┐
#   │ ☰ 🏠 💡 ◀  🔍 [ Suche ........ wächst mit ........ ]  [Py|C++|C#|Alle]│  <- Kopfleiste
#   ├───────────────────┬──────────────────────────────────────────────────┤
#   │ Navigation        │  Inhalt (ScrollSeite -> wächst mit, zentriert    │
#   │ (feste Breite)    │  ab config.INHALT_MAX_BREITE)                    │
#   └───────────────────┴──────────────────────────────────────────────────┘
#
# WER RUFT DAS AUF?  main.py -> programmieren_gui.create(tab, app)
#                    gui/server_gui.py benutzt dieselbe Klasse ProgrammierSeite
#                    mit eigenem Inhalts-Ordner und nur EINER Sprache (Bash)
#                    -> dann gibt es keinen Sprachumschalter oben rechts.
# BENUTZT:
#   programmieren/engine/lader.py   -> alle Themen laden
#   programmieren/engine/suche.py   -> Suchfunktion
#   programmieren/engine/seite.py   -> eine Seite zeichnen
#   core/layout.py                  -> ScrollSeite (Inhalt, responsive)
# =============================================================================

import customtkinter as ctk

import config                                                            # -> config.py
from core.benutzerdaten import FavoritKnopf                              # -> core/benutzerdaten.py
from core.layout import ScrollSeite                                      # -> core/layout.py
from core.navigation import KopfNavigation, Seitenleiste, listen_knopf   # -> core/navigation.py
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
    """
    Wiki mit Navigation, Suche und Themenseiten.
      inhalte_pfad     Ordner mit den Kategorien (None = programmieren/inhalte)
      sprachen         Liste der Sprachen. Nur EINE -> kein Umschalter (Server-Wiki: ["Bash"])
      titel            Überschrift der Übersicht
      such_platzhalter grauer Text im Suchfeld
    """

    def __init__(self, master, app, inhalte_pfad=None, sprachen=None, titel="💻 Programmieren",
                 such_platzhalter="🔍  Suchen ... z.B. while, if else, int, klasse  (Ctrl+F)"):
        super().__init__(master, fg_color=config.FARBEN["hintergrund"], corner_radius=0)
        self.app = app
        self.sprachen = sprachen or config.SPRACHEN
        self.sprache = config.STANDARD_SPRACHE if self.sprache_waehlbar() else self.sprachen[0]
        self.titel = titel
        self.such_platzhalter = such_platzhalter
        self.aktuelles_thema = None
        self.verlauf = []
        self.offene_kategorien = set()
        self.themen_buttons = {}
        self.aktueller_eintrag = None            # für ⭐ (Favorit) - gesetzt von main.py App.geoeffnet

        # ---- Daten laden + Suche vorbereiten ----
        self.kategorien, self.themen, self.ladefehler = lader.alle_laden(inhalte_pfad)
        for fehler in self.ladefehler:
            print("[Programmieren] Ladefehler:", fehler)
        self.suchmaschine = Suchmaschine(self.themen)

        # ---- Layout: Zeile 0 Kopfleiste, Zeile 1 = Navigation (fix) + Inhalt (wächst) ----
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._navigation_erstellen()           # zuerst: der ☰-Knopf der Kopfleiste braucht die Seitenleiste
        self._kopfleiste_erstellen()
        # Inhalt -> core/layout.py ScrollSeite (EIN Objekt, Seiten werden darin getauscht)
        self.inhalt = ScrollSeite(self)
        self.inhalt.grid(row=1, column=1, sticky="nsew")

        if self.kategorien:
            self.offene_kategorien.add(self.kategorien[0].ordner)
        self._navigation_baum_zeichnen()
        self._uebersicht_zeigen()

    def sprache_waehlbar(self):
        """Umschalter nur, wenn es mehr als eine Sprache gibt."""
        return len(self.sprachen) > 1

    # =========================================================================
    # KOPFLEISTE
    # =========================================================================
    def _kopfleiste_erstellen(self):
        leiste = ctk.CTkFrame(self, fg_color=config.FARBEN["sidebar"], corner_radius=0)
        leiste.grid(row=0, column=0, columnspan=2, sticky="ew")
        # ☰ 🏠 [Kategorie-/Bereichs-Icon] ◀  -> core/navigation.py
        icon, _, name = self.titel.partition(" ")
        self.kopf = KopfNavigation(leiste, self.app, self.seitenleiste, icon, name.strip(),
                                   uebersicht=self._uebersicht_knopf, zurueck=self._verlauf_zurueck)
        spalte = self.kopf.naechste_spalte
        leiste.grid_columnconfigure(spalte, weight=1)          # NUR das Suchfeld wächst mit

        # ---- Suchfeld (sticky="ew" + weight=1 -> füllt den freien Platz) ----
        self.suchfeld = ctk.CTkEntry(leiste, height=36, width=120, font=config.FONT_TEXT,
                                     placeholder_text=self.such_platzhalter)
        self.suchfeld.grid(row=0, column=spalte, sticky="ew", padx=10)
        self.suchfeld.bind("<KeyRelease>", self._suche_geaendert)
        self.suchfeld.bind("<Return>", self._suche_enter)
        self.suchfeld.bind("<Escape>", lambda e: self._suche_leeren())
        for taste in ("f", "F"):                          # F = mit Caps Lock / Shift
            self.winfo_toplevel().bind(f"<Control-{taste}>", lambda e: self._suchfeld_fokus(), add="+")
        self.favorit_knopf = FavoritKnopf(leiste, lambda: self.aktueller_eintrag)
        self.favorit_knopf.grid(row=0, column=spalte + 2, padx=(0, 12))
        Tooltip(self.favorit_knopf, "Als Favorit merken (erscheint auf der Startseite)")

        # ---- Sprachwahl (behält ihre Grösse) - nur wenn es etwas zu wählen gibt ----
        if not self.sprache_waehlbar():
            return
        self.sprachwahl = ctk.CTkSegmentedButton(leiste, values=self.sprachen + ["Alle"],
                                                 command=self._sprache_geaendert, height=36,
                                                 font=(config.SCHRIFT, 13, "bold"))
        self.sprachwahl.set(self.sprache)
        self.sprachwahl.grid(row=0, column=spalte + 1, padx=(4, 12))

    # =========================================================================
    # NAVIGATION LINKS
    # =========================================================================
    def _navigation_erstellen(self):
        # Seitenliste links (einklappbar, Breite ziehbar) -> core/navigation.py
        self.seitenleiste = Seitenleiste(self)
        self.seitenleiste.grid(row=1, column=0, sticky="nsw")
        self.navigation = self.seitenleiste.liste

    def _navigation_leeren(self):
        for kind in self.navigation.winfo_children():
            kind.destroy()
        self.themen_buttons = {}

    def _navigation_baum_zeichnen(self):
        self._navigation_leeren()
        zeile = 0
        for kat in self.kategorien:
            offen = kat.ordner in self.offene_kategorien
            listen_knopf(self.navigation, f"{kat.icon}  {kat.name}   {'▾' if offen else '▸'}",
                         lambda k=kat: self._kategorie_umschalten(k), titel=kat.name, height=34,
                         font=(config.SCHRIFT, 13, "bold"), fg_color="transparent", text_color=config.FARBEN["text"],
                         hover_color=config.FARBEN["rahmen"]).grid(row=zeile, column=0, sticky="ew", padx=4, pady=(6, 0))
            zeile += 1
            if offen:
                for thema in kat.themen:
                    zeile = self._themen_button(thema, zeile)
        self._aktiv_markieren()

    def _themen_button(self, thema, zeile, mit_kategorie=False):
        text = f"{thema.kategorie.icon}  {thema.titel}" if mit_kategorie else f"      {thema.titel}"
        button = listen_knopf(self.navigation, text, lambda t=thema: self.thema_oeffnen(t.id), titel=thema.titel,
                              height=28, font=config.FONT_TEXT, fg_color="transparent", text_color=config.FARBEN["text"],
                              hover_color=config.FARBEN["rahmen"])
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

    def _suchfeld_fokus(self):
        """Ctrl+F: nur das Suchfeld des gerade sichtbaren Wikis anspringen."""
        if self.winfo_ismapped():
            self.suchfeld.focus_set()

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
    def _uebersicht_knopf(self):
        """Übersicht-Knopf: auf einer Seite -> Übersicht ihrer Kategorie, sonst -> Übersicht des Bereichs."""
        thema = self.themen.get(self.aktuelles_thema)
        if thema is not None:
            self.kategorie_zeigen(thema.kategorie)
        else:
            self._uebersicht_zeigen()

    def _uebersicht_zeigen(self):
        self.aktuelles_thema = None
        self.aktueller_eintrag = None
        self.favorit_knopf.aktualisieren()
        self.kopf.uebersicht_zeigen()
        self._aktiv_markieren()
        body = self.inhalt.neue_seite()                      # -> core/layout.py
        uebersicht_zeichnen(body, self.kategorien, self.thema_oeffnen, self.ladefehler,   # -> engine/seite.py
                            titel=self.titel)

    def kategorie_zeigen(self, kategorie):
        """Übersicht EINER Kategorie. ◀ führt zurück zur Seite davor."""
        if self.aktuelles_thema:
            self.verlauf = (self.verlauf + [self.aktuelles_thema])[-30:]
        self.aktuelles_thema = None
        self.aktueller_eintrag = None
        self.favorit_knopf.aktualisieren()
        self.kopf.uebersicht_zeigen()                          # nächster Klick -> ganzer Bereich
        self._aktiv_markieren()
        body = self.inhalt.neue_seite()
        uebersicht_zeichnen(body, [kategorie], self.thema_oeffnen, titel=f"{kategorie.icon} {kategorie.name}")
        ctk.CTkButton(body, text=f"{self.titel}  ·  alle Kategorien  →", height=32, fg_color="transparent",
                      border_width=1, border_color=config.FARBEN["rahmen"], text_color=config.FARBEN["akzent"],
                      hover_color=config.FARBEN["rahmen"], command=self._uebersicht_zeigen).grid(
            row=99, column=0, sticky="w", pady=(4, 0))

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
        self.kopf.uebersicht_zeigen(thema.kategorie.icon, f"Übersicht {thema.kategorie.name}")

        body = self.inhalt.neue_seite()                      # alte Seite weg, nach oben scrollen
        ThemenSeite(body, thema, self.sprache, self.themen, self.thema_oeffnen)   # -> engine/seite.py
        self.aktueller_eintrag = self.app.geoeffnet(self, "seite", thema.id, thema.titel, thema.kategorie.icon)
        self.favorit_knopf.aktualisieren()

    def _verlauf_zurueck(self):
        if self.verlauf:
            self.thema_oeffnen(self.verlauf.pop(), verlauf_merken=False)
        else:
            self._uebersicht_zeigen()

    def _sprache_geaendert(self, neue_sprache):
        self.sprache = neue_sprache
        if self.aktuelles_thema:
            self.thema_oeffnen(self.aktuelles_thema, verlauf_merken=False)
