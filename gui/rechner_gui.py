# =============================================================================
# gui/rechner_gui.py
# -----------------------------------------------------------------------------
# Der Bereich RECHNER: alle Rechner an einem Ort - suchen, nach Thema oder A–Z.
#
#   ┌──────────────────────────────────────────────────────────────────────┐
#   │ ⬅  🏠  ◀   🔍 [ Suche ... z.B. Tiefpass, Pt100, LED ]  [Thema | A–Z] │
#   ├───────────────────────┬──────────────────────────────────────────────┤
#   │ 📘 Grundlagen       ▾ │  📘 Grundlagen › Gleichstrom                 │
#   │   GLEICHSTROM         │  Ohm'sches Gesetz & Leistung                 │
#   │     Ohm'sches Gesetz  │  [📖 Erklärung: Widerstand]                  │
#   │     ...               │  ┌ Rechner-Karte (dieselbe wie auf der Seite)┐│
#   └───────────────────────┴──────────────────────────────────────────────┘
#
# WICHTIG: Hier wird KEIN Rechner kopiert. Jede Karte entsteht über dieselbe
# Registry wie auf den Wissensseiten:  bauteile/rechner/__init__.py -> erstellen()
#
# WER RUFT DAS AUF?  main.py -> rechner_gui.create(tab, app)
# BENUTZT:
#   bauteile/rechner/rechner_info.py -> Titel, Kategorie, Stichworte, Wissensseite
#   bauteile/rechner/__init__.py     -> baut die Rechner-Karte
#   programmieren/engine/suche.py    -> Suche mit Tippfehler-Toleranz (wie in den Wikis)
#
# NEUER RECHNER? Nur in bauteile/rechner/rechner_info.py eintragen - erscheint hier automatisch.
# =============================================================================

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile import rechner                                           # -> bauteile/rechner/__init__.py
from bauteile.rechner.rechner_info import (KATEGORIEN, RECHNER_INFO,   # -> bauteile/rechner/rechner_info.py
                                           seiten_mit_rechner, wissensseiten_laden)
from core.benutzerdaten import FavoritKnopf                            # -> core/benutzerdaten.py
from core.layout import Karte, ResponsiveGrid, ScrollSeite, Stapel, WrapLabel, seiten_kopf   # -> core/layout.py
from core.widgets import Tooltip, info_box                             # -> core/widgets.py
from programmieren.engine.suche import Suchmaschine                    # -> programmieren/engine/suche.py

THEMATISCH, ALPHABETISCH = "Nach Thema", "A–Z"


def create(parent, app):
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    bereich = RechnerBereich(parent, app)
    bereich.grid(row=0, column=0, sticky="nsew")
    return bereich


class RechnerEintrag:
    """
    Ein Rechner, so aufbereitet, dass die Suchmaschine der Wikis ihn versteht
    (sie erwartet: id, titel, kurz, stichworte, reihenfolge, daten).
    """

    def __init__(self, rechner_id, info, nummer):
        self.id = rechner_id
        self.info = info
        self.titel = info["titel"]
        self.kurz = info["beschreibung"]
        self.stichworte = info["stichworte"] + [info["unterkategorie"], info["kategorie"]]
        self.reihenfolge = nummer
        self.daten = {}


def sortier_text(titel):
    """'Ohm'sches Gesetz' und 'Ä…' richtig einsortieren (Umlaute wie ae, Gross/klein egal)."""
    t = titel.lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue")):
        t = t.replace(alt, neu)
    return t


class RechnerBereich(ctk.CTkFrame):

    def __init__(self, master, app):
        super().__init__(master, fg_color=config.FARBEN["hintergrund"], corner_radius=0)
        self.app = app
        self.aktueller = None
        self.aktueller_eintrag = None            # für ⭐ (Favorit) - gesetzt von main.py App.geoeffnet
        self.verlauf = []
        self.knoepfe = {}
        self.sortierung = THEMATISCH

        # ---- Daten: nur Rechner, die es in der Registry wirklich gibt ----
        vorhanden = rechner.registry()
        self.eintraege = {rid: RechnerEintrag(rid, info, n) for n, (rid, info) in enumerate(RECHNER_INFO.items())
                          if rid in vorhanden}
        self.suchmaschine = Suchmaschine(self.eintraege)
        self.seiten, meldungen = wissensseiten_laden()
        for meldung in meldungen:
            print("[Rechner] ", meldung)
        self.offene_kategorien = set(KATEGORIEN)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._kopfleiste()
        self.navigation = ctk.CTkScrollableFrame(self, width=250, corner_radius=0, fg_color=config.FARBEN["sidebar"])
        self.navigation.grid(row=1, column=0, sticky="nsw")
        self.navigation.grid_columnconfigure(0, weight=1)
        self.inhalt = ScrollSeite(self)                    # -> core/layout.py
        self.inhalt.grid(row=1, column=1, sticky="nsew")

        self._liste_zeichnen()
        self._uebersicht_zeigen()

    # =========================================================================
    # KOPFLEISTE
    # =========================================================================
    def _kopfleiste(self):
        leiste = ctk.CTkFrame(self, fg_color=config.FARBEN["sidebar"], corner_radius=0)
        leiste.grid(row=0, column=0, columnspan=2, sticky="ew")
        leiste.grid_columnconfigure(3, weight=1)
        rahmen = dict(fg_color="transparent", border_width=1, border_color=config.FARBEN["rahmen"],
                      text_color=config.FARBEN["text"])
        for spalte, (text, befehl, tipp, stil) in enumerate([
                ("⬅", self.app.show_startseite, "Zur Startseite", {}),
                ("🏠", self._uebersicht_zeigen, "Übersicht aller Rechner", rahmen),
                ("◀", self._zurueck, "Vorheriger Rechner", rahmen)]):
            knopf = ctk.CTkButton(leiste, text=text, width=40, height=36, command=befehl, **stil)
            knopf.grid(row=0, column=spalte, padx=(10 if spalte == 0 else 4, 4), pady=10)
            Tooltip(knopf, tipp)
        self.suchfeld = ctk.CTkEntry(leiste, height=36, width=120, font=config.FONT_TEXT,
                                     placeholder_text="🔍  Rechner suchen ... z.B. Tiefpass, Pt100, LED, Kühlkörper")
        self.suchfeld.grid(row=0, column=3, sticky="ew", padx=(10, 8))
        self.suchfeld.bind("<KeyRelease>", self._suche)
        self.suchfeld.bind("<Return>", self._suche_enter)
        self.suchfeld.bind("<Escape>", lambda e: self._suche_leeren())
        self.sortierschalter = ctk.CTkSegmentedButton(leiste, values=[THEMATISCH, ALPHABETISCH], height=36,
                                                      command=self._sortierung_setzen)
        self.sortierschalter.set(THEMATISCH)
        self.sortierschalter.grid(row=0, column=4, padx=(0, 8))   # (kein Tooltip: CTkSegmentedButton kann kein bind)
        self.favorit_knopf = FavoritKnopf(leiste, lambda: self.aktueller_eintrag)
        self.favorit_knopf.grid(row=0, column=5, padx=(0, 12))
        Tooltip(self.favorit_knopf, "Rechner als Favorit merken (erscheint auf der Startseite)")

    # =========================================================================
    # NAVIGATION (links)
    # =========================================================================
    def _nav_leeren(self):
        for kind in self.navigation.winfo_children():
            kind.destroy()
        self.knoepfe = {}

    def _nav_text(self, zeile, text, fett=False, pady=(6, 0)):
        ctk.CTkLabel(self.navigation, text=text, anchor="w",
                     font=(config.SCHRIFT, 12 if fett else 11, "bold"),
                     text_color=config.FARBEN["text_leise"]).grid(row=zeile, column=0, sticky="w", padx=8, pady=pady)
        return zeile + 1

    def _rechner_knopf(self, eintrag, zeile, einzug="      "):
        knopf = ctk.CTkButton(self.navigation, text=f"{einzug}{eintrag.titel}", anchor="w", height=28,
                              font=config.FONT_TEXT, fg_color="transparent", text_color=config.FARBEN["text"],
                              hover_color=config.FARBEN["rahmen"],
                              command=lambda e=eintrag: self.rechner_oeffnen(e.id))
        knopf.grid(row=zeile, column=0, sticky="ew", padx=4, pady=1)
        self.knoepfe[eintrag.id] = knopf
        return zeile + 1

    def _liste_zeichnen(self):
        self._nav_leeren()
        if self.sortierung == ALPHABETISCH:
            self._liste_alphabetisch()
        else:
            self._liste_thematisch()
        self._markieren()

    def _liste_thematisch(self):
        zeile = 0
        for kategorie, (icon, _beschreibung) in KATEGORIEN.items():
            eintraege = [e for e in self.eintraege.values() if e.info["kategorie"] == kategorie]
            if not eintraege:
                continue
            offen = kategorie in self.offene_kategorien
            ctk.CTkButton(self.navigation, text=f"{icon}  {kategorie}  ({len(eintraege)})   {'▾' if offen else '▸'}",
                          anchor="w", height=34, font=(config.SCHRIFT, 13, "bold"), fg_color="transparent",
                          text_color=config.FARBEN["text"], hover_color=config.FARBEN["rahmen"],
                          command=lambda k=kategorie: self._umschalten(k)).grid(row=zeile, column=0, sticky="ew",
                                                                               padx=4, pady=(6, 0))
            zeile += 1
            if not offen:
                continue
            unterkategorie = None
            for eintrag in eintraege:
                if eintrag.info["unterkategorie"] != unterkategorie:
                    unterkategorie = eintrag.info["unterkategorie"]
                    zeile = self._nav_text(zeile, f"   {unterkategorie.upper()}", pady=(4, 0))
                zeile = self._rechner_knopf(eintrag, zeile)

    def _liste_alphabetisch(self):
        zeile, buchstabe = 0, None
        for eintrag in sorted(self.eintraege.values(), key=lambda e: sortier_text(e.titel)):
            erster = sortier_text(eintrag.titel)[:1].upper()
            if erster != buchstabe:
                buchstabe = erster
                zeile = self._nav_text(zeile, buchstabe, fett=True)
            icon = KATEGORIEN[eintrag.info["kategorie"]][0]
            zeile = self._rechner_knopf(eintrag, zeile, einzug=f"  {icon}  ")

    def _umschalten(self, kategorie):
        self.offene_kategorien ^= {kategorie}
        self._liste_zeichnen()

    def _sortierung_setzen(self, wert):
        self.sortierung = wert
        self._suche_leeren()

    def _markieren(self):
        for rechner_id, knopf in self.knoepfe.items():
            aktiv = rechner_id == self.aktueller
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
            self._liste_zeichnen()
            return
        treffer = self.suchmaschine.suchen(anfrage, max_treffer=20)     # -> programmieren/engine/suche.py
        self._nav_leeren()
        zeile = self._nav_text(0, f"🔍 {len(treffer)} Treffer", fett=True, pady=(8, 4))
        if not treffer:
            self._nav_text(zeile, "Nichts gefunden.", pady=0)
            return
        for eintrag in treffer:
            zeile = self._rechner_knopf(eintrag, zeile, einzug=f"{KATEGORIEN[eintrag.info['kategorie']][0]}  ")
        self._markieren()

    def _suche_enter(self, event=None):
        treffer = self.suchmaschine.suchen(self.suchfeld.get())
        if treffer:
            self.rechner_oeffnen(treffer[0].id)

    def _suche_leeren(self):
        self.suchfeld.delete(0, "end")
        self._liste_zeichnen()

    # =========================================================================
    # INHALT (rechts)
    # =========================================================================
    def _uebersicht_zeigen(self):
        self.aktueller = None
        self.aktueller_eintrag = None
        self.favorit_knopf.aktualisieren()
        self._markieren()
        body = self.inhalt.neue_seite()
        s = Stapel(body)
        seiten_kopf(s, "🧮 Rechner", f"{len(self.eintraege)} Rechner in {len(KATEGORIEN)} Kategorien  ·  "
                                     "dieselben Rechner wie auf den Wissensseiten – mit Link zur Erklärung")
        fehlend = sorted(set(rechner.registry()) - set(self.eintraege))
        if fehlend:
            s.add(info_box(body, "⚠️ Rechner ohne Eintrag in rechner_info.py (erscheinen hier nicht)",
                           [", ".join(fehlend)], art="warnung"))
        grid = s.add(ResponsiveGrid(body, min_spaltenbreite=340, max_spalten=2))
        for kategorie, (icon, beschreibung) in KATEGORIEN.items():
            eintraege = [e for e in self.eintraege.values() if e.info["kategorie"] == kategorie]
            if not eintraege:
                continue
            kasten = grid.add(Karte(grid, titel=f"{icon}  {kategorie}", untertitel=beschreibung))
            zeile, unterkategorie = 0, None
            for eintrag in eintraege:
                if eintrag.info["unterkategorie"] != unterkategorie:
                    unterkategorie = eintrag.info["unterkategorie"]
                    ctk.CTkLabel(kasten.body, text=unterkategorie.upper(), anchor="w", font=(config.SCHRIFT, 11, "bold"),
                                 text_color=config.FARBEN["text_leise"]).grid(row=zeile, column=0, sticky="w",
                                                                              pady=(6 if zeile else 0, 0))
                    zeile += 1
                ctk.CTkButton(kasten.body, text=f"  {eintrag.titel}", anchor="w", height=28, fg_color="transparent",
                              hover_color=config.FARBEN["rahmen"], text_color=config.FARBEN["akzent"],
                              command=lambda e=eintrag: self.rechner_oeffnen(e.id)).grid(row=zeile, column=0,
                                                                                         sticky="ew", pady=1)
                zeile += 1

    def rechner_oeffnen(self, rechner_id, verlauf_merken=True):
        eintrag = self.eintraege.get(rechner_id)
        if eintrag is None:
            return
        if verlauf_merken and self.aktueller and self.aktueller != rechner_id:
            self.verlauf = (self.verlauf + [self.aktueller])[-30:]
        self.aktueller = rechner_id
        info = eintrag.info
        if (self.sortierung == THEMATISCH and info["kategorie"] not in self.offene_kategorien
                and not self.suchfeld.get().strip()):
            self.offene_kategorien.add(info["kategorie"])
            self._liste_zeichnen()
        self._markieren()

        body = self.inhalt.neue_seite()
        s = Stapel(body)
        icon = KATEGORIEN[info["kategorie"]][0]
        seiten_kopf(s, info["titel"], info["beschreibung"],
                    pfad=f"{icon} {info['kategorie']}  ›  {info['unterkategorie']}")
        self._verweise(s, body, rechner_id, info)
        s.add(rechner.erstellen(body, rechner_id))           # -> bauteile/rechner/__init__.py (keine Kopie!)
        s.add(WrapLabel(body, text="Stichworte: " + ", ".join(info["stichworte"]), font=config.FONT_KLEIN,
                        text_color=config.FARBEN["text_leise"]), pady=(0, 0))
        self.aktueller_eintrag = self.app.geoeffnet(self, "rechner", rechner_id, info["titel"], icon)
        self.favorit_knopf.aktualisieren()

    def _verweise(self, s, body, rechner_id, info):
        """Knöpfe zur erklärenden Wissensseite und zu weiteren Seiten mit diesem Rechner."""
        haupt = info["wissensseite"]
        weitere = [sid for sid in seiten_mit_rechner(self.seiten, rechner_id) if sid != haupt]
        zeile = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        s.add(zeile, sticky="w", pady=(0, 12))
        if haupt in self.seiten:
            knopf = ctk.CTkButton(zeile, text=f"📖 Erklärung: {self.seiten[haupt]['titel']}", height=30,
                                  command=lambda: self.wissensseite_oeffnen(haupt))
            knopf.grid(row=0, column=0, columnspan=4, pady=2, sticky="w")
            Tooltip(knopf, f"Öffnet die Seite im Bereich {self.seiten[haupt]['bereich']}")
        if weitere:                                       # zweite Zeile, damit es auch schmal passt
            ctk.CTkLabel(zeile, text="auch auf:", font=config.FONT_KLEIN,
                         text_color=config.FARBEN["text_leise"]).grid(row=1, column=0, padx=(0, 6), pady=(4, 0))
            for nummer, seite_id in enumerate(weitere):
                ctk.CTkButton(zeile, text=self.seiten[seite_id]["titel"], height=26, width=60,
                              fg_color="transparent", border_width=1, border_color=config.FARBEN["rahmen"],
                              text_color=config.FARBEN["akzent"], hover_color=config.FARBEN["rahmen"],
                              command=lambda sid=seite_id: self.wissensseite_oeffnen(sid)).grid(
                    row=1, column=1 + nummer, padx=(0, 6), pady=(4, 0))

    def wissensseite_oeffnen(self, seite_id):
        """Wechselt in den passenden Tab (Bauteile / Messtechnik) und öffnet dort die Seite."""
        bereich = self.seiten[seite_id]["bereich"]
        self.app.show_tab(bereich)                       # baut den Tab, falls noch nicht offen (main.py)
        wiki = self.app.seiten.get(bereich)
        if wiki is not None:
            wiki.ansicht = "wissen"
            wiki.thema_oeffnen(seite_id)

    def _zurueck(self):
        if self.verlauf:
            self.rechner_oeffnen(self.verlauf.pop(), verlauf_merken=False)
        else:
            self._uebersicht_zeigen()
