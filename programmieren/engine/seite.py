# =============================================================================
# programmieren/engine/seite.py
# -----------------------------------------------------------------------------
# Zeichnet EINE Wiki-Seite aus den Daten eines Themas (und die Übersicht).
#
# AUFBAU EINER SEITE (alles optional ausser Titel):
#   Pfad · Titel · Kurzbeschreibung · Erklärung · Bild(er) · Tabelle(n)
#   · Beispiele (Code) · Sprachunterschiede · Tipps · Häufige Fehler · Siehe auch
#
# RESPONSIVE: Alles läuft über core/layout.py -> Text bricht um, Bilder und
#             Tabellen skalieren, "Siehe auch" und Übersicht ordnen sich neu an.
#             Die Seite füllt die ganze Breite (max. config.INHALT_MAX_BREITE).
#
# WER RUFT DAS AUF?  gui/programmieren_gui.py -> thema_oeffnen() / _uebersicht_zeigen()
# =============================================================================

import os

import customtkinter as ctk

import config                                                   # -> config.py
from core.layout import (Karte, ResponsiveBild, ResponsiveGrid,  # -> core/layout.py
                         Stapel, Tabelle, WrapLabel, seiten_kopf)
from core.widgets import FormatText, info_box                   # -> core/widgets.py
from programmieren.engine.codeblock import CodeBlock            # -> engine/codeblock.py


class ThemenSeite:
    """
    master       leere, mitwachsende Seite (aus ScrollSeite.neue_seite())
    thema        Thema-Objekt aus engine/lader.py
    sprache      "Python", "C++", "C#" oder "Alle"
    alle_themen  dict id -> Thema (für "Siehe auch")
    oeffnen      Funktion, die ein anderes Thema öffnet
    """

    def __init__(self, master, thema, sprache, alle_themen, oeffnen):
        self.master = master
        self.thema = thema
        self.daten = thema.daten
        self.sprache = sprache
        self.alle_themen = alle_themen
        self.oeffnen = oeffnen
        self.s = Stapel(master)                  # -> core/layout.py: alles untereinander

        kat = thema.kategorie
        seiten_kopf(self.s, thema.titel, thema.kurz or None, pfad=f"{kat.icon} {kat.name}  ›  {thema.titel}")

        self._erklaerung()
        self._bilder()
        self._tabellen()
        self._beispiele()
        self._sprachunterschiede()
        self._tipps_und_fehler()
        self._siehe_auch()

    # -------------------------------------------------------------------------
    def _abschnitt(self, text):
        self.s.add(WrapLabel(self.master, text=text, font=config.FONT_SEKTION,
                             text_color=config.FARBEN["text"]), pady=(16, 6))

    def _text_karte(self, text):
        kasten = self.s.add(Karte(self.master))
        feld = FormatText(kasten.body)
        feld.setze_text(text)
        feld.grid(row=0, column=0, sticky="ew")

    # -------------------------------------------------------------------------
    def _erklaerung(self):
        if self.daten.get("erklaerung"):
            self._text_karte(self.daten["erklaerung"])

    def _bilder(self):
        bilder = list(self.daten.get("bilder") or [])
        if self.daten.get("bild"):
            bilder.insert(0, {"datei": self.daten["bild"], "text": self.daten.get("bild_text", "")})
        for eintrag in bilder:
            kasten = self.s.add(Karte(self.master))
            pfad = os.path.join(config.BILDER_PROGRAMMIEREN, eintrag["datei"])
            # -> core/layout.py: Bild skaliert mit der Kartenbreite
            ResponsiveBild(kasten.body, pfad, max_breite=config.MAX_BILD_BREITE).grid(row=0, column=0, sticky="ew")
            if eintrag.get("text"):
                WrapLabel(kasten.body, text=eintrag["text"], font=config.FONT_KLEIN, anchor="center",
                          justify="center", text_color=config.FARBEN["text_leise"]).grid(
                    row=1, column=0, sticky="ew", pady=(6, 0))

    def _tabellen(self):
        tabellen = list(self.daten.get("tabellen") or [])
        if self.daten.get("tabelle"):
            tabellen.insert(0, self.daten["tabelle"])
        for tab in tabellen:
            if tab.get("titel"):
                self._abschnitt(tab["titel"])
            kasten = self.s.add(Karte(self.master))
            # -> core/layout.py: Spalten wachsen mit, Text bricht um
            Tabelle(kasten.body, tab.get("kopf", []), tab.get("zeilen", [])).grid(row=0, column=0, sticky="ew")
            if tab.get("hinweis"):
                hinweis = FormatText(kasten.body)
                hinweis.setze_text(tab["hinweis"])
                hinweis.grid(row=1, column=0, sticky="ew", pady=(10, 0))

    def _beispiele(self):
        beispiele = self.daten.get("beispiele") or []
        if not beispiele:
            return
        self._abschnitt("💻 Beispiele" if self.sprache == "Alle" else f"💻 Beispiele in {self.sprache}")
        sprachen = config.SPRACHEN if self.sprache == "Alle" else [self.sprache]

        for beispiel in beispiele:
            if beispiel.get("titel"):
                self.s.add(WrapLabel(self.master, text=beispiel["titel"], font=(config.SCHRIFT, 14, "bold"),
                                     text_color=config.FARBEN["text"]), pady=(8, 2))
            if beispiel.get("text"):
                feld = FormatText(self.master, hintergrund="hintergrund")
                feld.setze_text(beispiel["text"])
                self.s.add(feld, pady=(0, 4))

            code_dict = beispiel.get("code", {})
            hinweise = beispiel.get("hinweis", {})
            for sprache in sprachen:
                if sprache in code_dict:
                    self.s.add(CodeBlock(self.master, code_dict[sprache], sprache), pady=(0, 6))
                else:
                    box = self.s.add(ctk.CTkFrame(self.master, corner_radius=8, fg_color=config.FARBEN["warnung"]),
                                     pady=(0, 6))
                    box.grid_columnconfigure(0, weight=1)
                    feld = FormatText(box, hintergrund="warnung")
                    feld.setze_text(f"**{sprache}:** " + hinweise.get(
                        sprache, f"Für {sprache} gibt es zu diesem Beispiel keinen Code."))
                    feld.grid(row=0, column=0, sticky="ew", padx=10, pady=8)

            if beispiel.get("ausgabe"):
                box = self.s.add(ctk.CTkFrame(self.master, corner_radius=8, fg_color=config.FARBEN["sidebar"]),
                                 pady=(0, 10))
                box.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(box, text="▶ Ausgabe", font=(config.SCHRIFT, 11, "bold"), anchor="w",
                             text_color=config.FARBEN["text_leise"]).grid(row=0, column=0, sticky="w", padx=12, pady=(6, 0))
                WrapLabel(box, text=beispiel["ausgabe"].strip("\n"), font=config.FONT_CODE,
                          text_color=config.FARBEN["text"]).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

    def _sprachunterschiede(self):
        if self.daten.get("unterschiede"):
            self._abschnitt("🔀 Unterschiede Python / C++ / C#")
            self._text_karte(self.daten["unterschiede"])

    def _tipps_und_fehler(self):
        if self.daten.get("tipps"):
            self.s.add(info_box(self.master, "💡 Tipps", self.daten["tipps"], art="tipp"), pady=(16, 0))
        if self.daten.get("fehler"):
            self.s.add(info_box(self.master, "⚠️ Häufige Fehler", self.daten["fehler"], art="warnung"), pady=(12, 0))

    def _siehe_auch(self):
        verweise = [self.alle_themen[i] for i in self.daten.get("siehe_auch", []) if i in self.alle_themen]
        if not verweise:
            return
        self._abschnitt("🔗 Siehe auch")
        # -> core/layout.py: Buttons ordnen sich je nach Breite in 1-4 Spalten an
        leiste = self.s.add(ResponsiveGrid(self.master, min_spaltenbreite=220, max_spalten=4, abstand=8))
        for ziel in verweise:
            # Klick -> zurück in gui/programmieren_gui.py thema_oeffnen(ziel.id)
            leiste.add(ctk.CTkButton(leiste, text=f"{ziel.kategorie.icon} {ziel.titel}", height=32,
                                     command=lambda z=ziel: self.oeffnen(z.id)))


# =============================================================================
# ÜBERSICHT (Startansicht des Wikis)
# =============================================================================
def uebersicht_zeichnen(master, kategorien, oeffnen, ladefehler=None):
    s = Stapel(master)
    anzahl = sum(len(k.themen) for k in kategorien)
    seiten_kopf(s, "💻 Programmieren",
                f"{anzahl} Themen in {len(kategorien)} Kategorien  ·  Suche oben benutzen oder links ein Thema wählen")

    if ladefehler:
        s.add(info_box(master, "⚠️ Einige Themen konnten nicht geladen werden", ladefehler, art="warnung"))

    # Kategorien als Karten: 2 nebeneinander, bei schmalem Fenster untereinander
    grid = s.add(ResponsiveGrid(master, min_spaltenbreite=380, max_spalten=2))
    for kat in kategorien:
        kasten = grid.add(Karte(grid, titel=f"{kat.icon}  {kat.name}", untertitel=kat.beschreibung or None))
        for zeile, thema in enumerate(kat.themen):
            ctk.CTkButton(kasten.body, text=f"  {thema.titel}", anchor="w", height=28,
                          fg_color="transparent", hover_color=config.FARBEN["rahmen"],
                          text_color=config.FARBEN["akzent"],
                          command=lambda t=thema: oeffnen(t.id)).grid(row=zeile, column=0, sticky="ew", pady=1)
