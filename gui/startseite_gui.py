# =============================================================================
# gui/startseite_gui.py
# -----------------------------------------------------------------------------
# STARTSEITE:
#
#   ┌─────────────────────────────────────────────────────────────┐
#   │  animiertes Banner (Schaltplan, Oszilloskop, Terminal, Code)  │  -> gui/startseite_banner.py
#   │  [ 🔍  In allen Bereichen suchen …                    ]      │  -> gui/gesamtsuche.py
#   │  ⭐ Favoriten        🕘 Zuletzt geöffnet                       │  -> core/benutzerdaten.py
#   │  🎲 Schaltung des Tages                                        │
#   │  Bereiche: Kacheln mit Zahlen + Kategorie-Chips               │
#   │  Dark Mode · Tipp                                             │
#   └─────────────────────────────────────────────────────────────┘
#
# create() gibt ein Objekt mit aktualisieren() zurück: main.py ruft es bei jedem Zurückkehren auf
# (neue Favoriten / zuletzt geöffnete Seiten erscheinen sofort).
# WER RUFT DAS AUF?  main.py -> startseite_gui.create(self.startseite, self)
# =============================================================================

import datetime
import random

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile.rechner.rechner_info import RECHNER_INFO                 # -> bauteile/rechner/rechner_info.py
from core import benutzerdaten                                         # -> core/benutzerdaten.py
from core.layout import Karte, ResponsiveGrid, ScrollSeite, Stapel, WrapLabel   # -> core/layout.py
from gui import gesamtsuche                                            # -> gui/gesamtsuche.py
from gui.startseite_banner import Banner                               # -> gui/startseite_banner.py

TIPPS = [
    "P = U · I   (Leistung = Spannung × Strom)",
    "τ = R · C   – nach 5τ ist ein Kondensator praktisch voll geladen",
    "Python: Einrückung ist Teil der Syntax – 4 Leerzeichen pro Ebene",
    "Ctrl+K springt von überall in die Suche auf der Startseite",
    "Mit ⭐ in der Kopfleiste merkst du dir eine Seite als Favorit",
    "Pt1000 statt Pt100: derselbe Leitungswiderstand macht 10× weniger Fehler",
    "1 Byte = 8 Bit  →  Wertebereich 0 … 255 (unsigned)",
    "Butterworth: Q = 0.707 – maximal flach, 4.3 % Überschwingen",
]
MAX_CHIPS = 6


def create(master, app):
    master.grid_rowconfigure(0, weight=1)
    master.grid_columnconfigure(0, weight=1)
    return Startseite(master, app)


class Startseite:
    def __init__(self, master, app):
        self.app = app
        self.index = gesamtsuche.gesamtindex()
        scroll = ScrollSeite(master, max_breite=1100)                  # -> core/layout.py
        scroll.grid(row=0, column=0, sticky="nsew")
        body = scroll.body
        s = Stapel(body)

        s.add(Banner(body), pady=(14, 0))
        self.suche = s.add(gesamtsuche.SuchLeiste(body, app), pady=(16, 18))
        app.bind("<Control-k>", lambda _e: self._suche_fokus(), add="+")

        self.persoenlich = s.add(ctk.CTkFrame(body, fg_color="transparent", corner_radius=0), pady=(0, 6))
        self.persoenlich.grid_columnconfigure(0, weight=1)
        self.tages = s.add(ctk.CTkFrame(body, fg_color="transparent", corner_radius=0), pady=(0, 14))
        self.tages.grid_columnconfigure(0, weight=1)
        self.tages_versatz = 0

        s.add(self._ueberschrift(body, "🧭  Bereiche"), pady=(6, 8))
        kacheln = s.add(ResponsiveGrid(body, min_spaltenbreite=300, max_spalten=3))
        for name, _modul, icon, beschreibung in app.bereiche:
            kacheln.add(self._kachel(kacheln, name, icon, beschreibung))

        unten = s.add(ctk.CTkFrame(body, fg_color="transparent"), pady=(18, 20))
        unten.grid_columnconfigure(0, weight=1)
        schalter = ctk.CTkSwitch(unten, text="Dark Mode", font=config.FONT_TEXT,
                                 command=lambda: app.modus_wechseln(schalter.get() == 1))
        if ctk.get_appearance_mode() == "Dark":
            schalter.select()
        schalter.grid(row=0, column=0, pady=(0, 10))
        WrapLabel(unten, text=f"💡 Tipp: {random.choice(TIPPS)}", font=config.FONT_TEXT, anchor="center",
                  justify="center", text_color=config.FARBEN["text_leise"]).grid(row=1, column=0, sticky="ew")
        self.aktualisieren()

    # =========================================================================
    def _suche_fokus(self):
        self.app.show_startseite()
        self.suche.fokus()

    def aktualisieren(self):
        """Favoriten, Zuletzt geöffnet und Schaltung des Tages neu zeichnen (main.py -> show_startseite)."""
        self._persoenlich_zeichnen()
        self._tages_zeichnen()

    @staticmethod
    def _ueberschrift(master, text):
        return ctk.CTkLabel(master, text=text, font=config.FONT_SEKTION, anchor="w", text_color=config.FARBEN["text"])

    # =========================================================================
    # FAVORITEN + ZULETZT
    # =========================================================================
    def _persoenlich_zeichnen(self):
        for kind in self.persoenlich.winfo_children():
            kind.destroy()
        raster = ResponsiveGrid(self.persoenlich, min_spaltenbreite=380, max_spalten=2)
        raster.grid(row=0, column=0, sticky="ew")
        for titel, liste, leer in (
                ("⭐  Favoriten", benutzerdaten.favoriten(),
                 "Noch keine Favoriten – auf einer Seite oder bei einem Rechner oben auf ☆ klicken."),
                ("🕘  Zuletzt geöffnet", benutzerdaten.zuletzt(),
                 "Hier erscheinen die Seiten und Rechner, die du zuletzt geöffnet hast.")):
            karte = raster.add(Karte(raster, titel=titel))
            if not liste:
                WrapLabel(karte.body, text=leer, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"]).grid(
                    row=0, column=0, sticky="ew")
                continue
            for zeile, eintrag in enumerate(liste[:8]):
                self._chip(karte.body, eintrag, zeile)

    def _chip(self, master, eintrag, zeile):
        rahmen = ctk.CTkFrame(master, fg_color="transparent", corner_radius=0)
        rahmen.grid(row=zeile, column=0, sticky="ew", pady=1)
        rahmen.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(rahmen, text=f"{eintrag.get('icon', '📄')}  {eintrag['titel']}", anchor="w", height=28,
                      font=config.FONT_TEXT, fg_color="transparent", text_color=config.FARBEN["text"],
                      hover_color=config.FARBEN["rahmen"],
                      command=lambda e=eintrag: gesamtsuche.oeffnen(self.app, e)).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(rahmen, text=eintrag["bereich"], font=config.FONT_KLEIN,
                     text_color=config.FARBEN["text_leise"]).grid(row=0, column=1, padx=(6, 4))

    # =========================================================================
    # SCHALTUNG DES TAGES
    # =========================================================================
    def _tages_kandidaten(self):
        seiten = {e.id: e for e in self.index["eintraege"].values() if e.art == "seite"}
        kandidaten = []
        for rid, info in RECHNER_INFO.items():
            seite = seiten.get(info.get("wissensseite"))
            if gesamtsuche.interaktiv(rid) and seite is not None and f"Rechner:{rid}" in self.index["eintraege"]:
                kandidaten.append((rid, info, seite))
        return kandidaten

    def _tages_zeichnen(self):
        for kind in self.tages.winfo_children():
            kind.destroy()
        kandidaten = self._tages_kandidaten()
        if not kandidaten:
            return
        nummer = (datetime.date.today().toordinal() + self.tages_versatz) % len(kandidaten)
        rid, info, seite = kandidaten[nummer]
        karte = Karte(self.tages, titel=f"🎲  {'Schaltung des Tages' if self.tages_versatz == 0 else 'Noch eine'}: "
                                        f"{info['titel'].replace(' (interaktiv)', '')}",
                      untertitel=f"{info['beschreibung']}   ·   {seite.ort}",
                      fg_color=config.FARBEN["tipp"])
        karte.grid(row=0, column=0, sticky="ew")
        knoepfe = ctk.CTkFrame(karte.body, fg_color="transparent", corner_radius=0)
        knoepfe.grid(row=0, column=0, sticky="w")
        ctk.CTkButton(knoepfe, text="Ausprobieren  →", height=32,
                      command=lambda: gesamtsuche.oeffnen(self.app, seite)).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkButton(knoepfe, text="🔄 Andere zeigen", height=32, fg_color="transparent", border_width=1,
                      border_color=config.FARBEN["rahmen"], text_color=config.FARBEN["text"],
                      command=self._tages_weiter).grid(row=0, column=1)

    def _tages_weiter(self):
        self.tages_versatz += 1
        self._tages_zeichnen()

    # =========================================================================
    # BEREICHSKACHELN
    # =========================================================================
    def _kachel(self, master, name, icon, beschreibung):
        info = self.index["bereiche"].get(name, {})
        karte = Karte(master, titel=f"{icon}  {name}", untertitel=beschreibung)
        teile = []
        if info.get("seiten"):
            teile.append(f"📄 {info['seiten']} Seiten")
        if info.get("rechner"):
            teile.append(f"🧮 {info['rechner']} Rechner")
        if info.get("simulationen"):
            teile.append(f"🎛️ {info['simulationen']} Simulationen")
        if info.get("befehle"):
            teile.append(f"⌨️ {info['befehle']} Befehle")
        if teile:
            WrapLabel(karte.body, text="   ".join(teile), font=(config.SCHRIFT, 12, "bold"),
                      text_color=config.FARBEN["akzent"]).grid(row=0, column=0, sticky="ew", pady=(0, 8))
        chips = ctk.CTkFrame(karte.body, fg_color="transparent", corner_radius=0)
        chips.grid(row=1, column=0, sticky="ew")
        chips.grid_columnconfigure((0, 1), weight=1, uniform="chip")
        kategorien = info.get("kategorien", [])
        for k, kat in enumerate(kategorien[:MAX_CHIPS]):
            if name == "Rechner":
                text, befehl = f"{kat[1][0]} {kat[0]}", (lambda: self.app.show_tab("Rechner"))
            else:
                text = f"{kat.icon} {kat.name}"
                befehl = (lambda n=name, k=kat: self._kategorie_oeffnen(n, k))
            ctk.CTkButton(chips, text=text, anchor="w", height=26, font=config.FONT_KLEIN, corner_radius=13,
                          fg_color=config.FARBEN["hintergrund"], text_color=config.FARBEN["text"],
                          hover_color=config.FARBEN["rahmen"], command=befehl).grid(
                row=k // 2, column=k % 2, sticky="ew", padx=2, pady=2)
        mehr = len(kategorien) - MAX_CHIPS
        ctk.CTkButton(karte.body, text=f"Öffnen  →" + (f"   (+{mehr} weitere Kategorien)" if mehr > 0 else ""),
                      height=32, command=lambda n=name: self.app.show_tab(n)).grid(row=2, column=0, sticky="w",
                                                                                  pady=(10, 0))
        return karte

    def _kategorie_oeffnen(self, bereich, kategorie):
        """Ersten Eintrag der Kategorie öffnen - die Navigation links zeigt dann die ganze Kategorie."""
        if not kategorie.themen:
            self.app.show_tab(bereich)
            return
        gesamtsuche.oeffnen(self.app, {"art": "seite", "bereich": bereich, "id": kategorie.themen[0].id})
