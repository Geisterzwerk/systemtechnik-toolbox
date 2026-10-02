# =============================================================================
# bauteile/engine/seite.py
# -----------------------------------------------------------------------------
# Zeichnet EINE Bauteil-Seite (und die Übersicht).
#
#   ┌──────────────────────────────────────────────────────┐
#   │ Passiv › Widerstand                                  │
#   │ Widerstand                                           │
#   │ Kurzbeschreibung                                     │
#   │ [ 📖 Wissen | 🧮 Rechner (10) ]   <- Umschalter      │
#   ├──────────────────────────────────────────────────────┤
#   │ WISSEN:  Steckbrief (Symbol + Eckdaten) · Grafik ·    │
#   │          Erklärung                                   │
#   │          · Bilder · Tabellen · 💡 Kniffe · ⚠ Fehler  │
#   │          · 🔗 Siehe auch                             │
#   │ RECHNER: Karten nebeneinander (bei schmalem Fenster  │
#   │          untereinander)                              │
#   └──────────────────────────────────────────────────────┘
#
# Die DATEN kommen aus bauteile/inhalte/<kategorie>/<bauteil>.py (THEMA = {...}).
#
# WER RUFT DAS AUF?  gui/bauteile_gui.py -> BauteilWiki.thema_oeffnen()
# =============================================================================

import os

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile import rechner                                           # -> bauteile/rechner/__init__.py
from bauteile.grafiken.symbole import SYMBOLE                          # -> bauteile/grafiken/symbole.py
from core.layout import (Karte, ResponsiveBild, ResponsiveCanvas,      # -> core/layout.py
                         ResponsiveGrid, Stapel, Tabelle, WrapLabel, seiten_kopf)
from core.widgets import FormatText, info_box                          # -> core/widgets.py

WISSEN = "📖 Wissen"


def rechner_text(anzahl):
    return f"🧮 Rechner ({anzahl})"


class BauteilSeite:
    """
    master           leere, mitwachsende Seite (ScrollSeite.neue_seite())
    thema            Thema-Objekt (programmieren/engine/lader.py - gleiche Maschine)
    ansicht          "wissen" oder "rechner"
    alle_themen      dict id -> Thema (für "Siehe auch")
    oeffnen          Funktion: anderes Thema öffnen
    ansicht_setzen   Funktion: Umschalter Wissen/Rechner wurde geklickt
    """

    def __init__(self, master, thema, ansicht, alle_themen, oeffnen, ansicht_setzen):
        self.master = master
        self.thema = thema
        self.daten = thema.daten
        self.alle_themen = alle_themen
        self.oeffnen = oeffnen

        self.s = Stapel(master)                     # -> core/layout.py: alles untereinander
        kat = thema.kategorie
        seiten_kopf(self.s, thema.titel, thema.kurz or None, pfad=f"{kat.icon} {kat.name}  ›  {thema.titel}")

        rechner_ids = self.daten.get("rechner", [])
        if rechner_ids:
            # ---- Umschalter Wissen | Rechner ----
            werte = [WISSEN, rechner_text(len(rechner_ids))]
            schalter = ctk.CTkSegmentedButton(master, values=werte, height=34, font=(config.SCHRIFT, 13, "bold"),
                                              command=lambda v: ansicht_setzen("wissen" if v == WISSEN else "rechner"))
            schalter.set(werte[0] if ansicht == "wissen" else werte[1])
            self.s.add(schalter, sticky="w", pady=(0, 14))
        else:
            ansicht = "wissen"

        if ansicht == "rechner":
            self._rechner(rechner_ids)
        else:
            self._steckbrief()
            # Interaktive Grafiken (z.B. Trafo-Animation, Ladekurve) direkt im Wissen-Teil
            for grafik_id in self.daten.get("grafiken", []):
                self.s.add(rechner.erstellen(master, grafik_id))      # -> bauteile/rechner/__init__.py
            self._text_karte(self.daten.get("erklaerung"))
            self._bilder()
            self._tabellen()
            if self.daten.get("tipps"):
                self.s.add(info_box(master, "💡 Kniffe & Praxis", self.daten["tipps"], art="tipp"), pady=(16, 0))
            if self.daten.get("fehler"):
                self.s.add(info_box(master, "⚠️ Häufige Fehler", self.daten["fehler"], art="warnung"), pady=(12, 0))
            self._siehe_auch()

    # -------------------------------------------------------------------------
    def _abschnitt(self, text):
        self.s.add(WrapLabel(self.master, text=text, font=config.FONT_SEKTION,
                             text_color=config.FARBEN["text"]), pady=(16, 6))

    def _text_karte(self, text):
        if not text:
            return
        kasten = self.s.add(Karte(self.master))
        feld = FormatText(kasten.body)
        feld.setze_text(text)
        feld.grid(row=0, column=0, sticky="ew")

    def _steckbrief(self):
        """Schaltzeichen (links) + Eckdaten (rechts), bei schmalem Fenster untereinander."""
        brief = self.daten.get("steckbrief")
        if not brief:
            return
        grid = self.s.add(ResponsiveGrid(self.master, min_spaltenbreite=320, max_spalten=2))
        symbol = SYMBOLE.get(brief.get("symbol", ""))
        if symbol:
            karte = grid.add(Karte(grid, titel="Schaltzeichen"))
            hell, dunkel = config.FARBEN["text"]
            farbe = dunkel if ctk.get_appearance_mode() == "Dark" else hell
            ResponsiveCanvas(karte.body, lambda c, w, h: symbol(c, w, h, farbe),
                             seitenverhaeltnis=0.32, max_hoehe=170).grid(row=0, column=0, sticky="ew")
        daten = grid.add(Karte(grid, titel="Steckbrief"))
        feld = FormatText(daten.body)
        feld.setze_text("\n".join(f"- **{k}:** {v}" for k, v in brief.get("zeilen", [])))
        feld.grid(row=0, column=0, sticky="ew")

    def _bilder(self):
        for eintrag in self.daten.get("bilder", []):
            if eintrag.get("titel"):
                self._abschnitt(eintrag["titel"])
            kasten = self.s.add(Karte(self.master))
            pfad = os.path.join(config.BILDER_PFAD, eintrag["datei"])
            ResponsiveBild(kasten.body, pfad, max_breite=eintrag.get("max_breite", config.MAX_BILD_BREITE)).grid(
                row=0, column=0, sticky="ew")
            if eintrag.get("text"):
                WrapLabel(kasten.body, text=eintrag["text"], font=config.FONT_KLEIN, anchor="center",
                          justify="center", text_color=config.FARBEN["text_leise"]).grid(
                    row=1, column=0, sticky="ew", pady=(6, 0))

    def _tabellen(self):
        for tab in self.daten.get("tabellen", []):
            if tab.get("titel"):
                self._abschnitt(tab["titel"])
            kasten = self.s.add(Karte(self.master))
            Tabelle(kasten.body, tab.get("kopf", []), tab.get("zeilen", [])).grid(row=0, column=0, sticky="ew")
            if tab.get("hinweis"):
                hinweis = FormatText(kasten.body)
                hinweis.setze_text(tab["hinweis"])
                hinweis.grid(row=1, column=0, sticky="ew", pady=(10, 0))

    def _siehe_auch(self):
        verweise = [self.alle_themen[i] for i in self.daten.get("siehe_auch", []) if i in self.alle_themen]
        if not verweise:
            return
        self._abschnitt("🔗 Siehe auch")
        leiste = self.s.add(ResponsiveGrid(self.master, min_spaltenbreite=220, max_spalten=4, abstand=8))
        for ziel in verweise:
            leiste.add(ctk.CTkButton(leiste, text=f"{ziel.kategorie.icon} {ziel.titel}", height=32,
                                     command=lambda z=ziel: self.oeffnen(z.id)))

    def _rechner(self, rechner_ids):
        self.s.add(info_box(self.master, "⌨️ Eingabe-Tipps", [
            "Einheit rechts neben dem Feld wählen – oder direkt tippen: `4k7`, `2.2M`, `470m`, `4R7`, `100n`",
            "Komma oder Punkt als Dezimalzeichen, **Enter** rechnet sofort",
            "Ergebnisse werden automatisch in der passenden Einheit angezeigt (mV, kΩ, µF …)",
        ], art="tipp"), pady=(0, 12))
        grid = self.s.add(ResponsiveGrid(self.master, min_spaltenbreite=400, max_spalten=2))
        for rechner_id in rechner_ids:
            grid.add(rechner.erstellen(grid, rechner_id))       # -> bauteile/rechner/__init__.py


# =============================================================================
# ÜBERSICHT
# =============================================================================
def uebersicht_zeichnen(master, kategorien, oeffnen, ladefehler=None):
    s = Stapel(master)
    anzahl = sum(len(k.themen) for k in kategorien)
    seiten_kopf(s, "🔧 Bauteile",
                f"{anzahl} Bauteile in {len(kategorien)} Kategorien  ·  Wissen, Kniffe und Rechner  ·  "
                f"Suche oben oder links wählen")
    if ladefehler:
        s.add(info_box(master, "⚠️ Einige Bauteile konnten nicht geladen werden", ladefehler, art="warnung"))
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
