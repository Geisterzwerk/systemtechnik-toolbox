# =============================================================================
# core/navigation.py
# -----------------------------------------------------------------------------
# NAVIGATION, die alle Bereiche gleich benutzen (Bauteile, Schaltungen, Digitaltechnik, Messtechnik,
# Programmieren, Server, Rechner):
#
#   ┌───────────────────────────────────────────────────────────────────┐
#   │ [☰] [🏠] [💡] [◀]   🔍 [ Suche …                     ]  [⭐]          │   KopfNavigation
#   ├─────────────────────┬┬────────────────────────────────────────────┤
#   │ Seitenliste        ││  Inhalt                                    │   Seitenleiste + Griff
#   └─────────────────────┴┴────────────────────────────────────────────┘
#
#   ☰   Seitenliste links ein-/ausblenden (mehr Platz für die Seite)
#   🏠  zur Startseite
#   💡  Übersicht: zeigt das Icon der KATEGORIE der offenen Seite (Dioden = 💡, Leistung & Schalten = ⚡)
#       -> Klick öffnet die Übersicht dieser Kategorie. In der Kategorie-Übersicht zeigt er das Icon des
#       BEREICHS (🔧) -> Klick öffnet die Übersicht des ganzen Bereichs.
#   ◀   eine Seite zurück
#   Griff zwischen Liste und Inhalt: mit der Maus ziehen = Liste breiter/schmaler (wird gemerkt).
#
# WER RUFT DAS AUF?  bauteile/engine/wiki_bereich.py, gui/programmieren_gui.py, gui/rechner_gui.py
# =============================================================================

import customtkinter as ctk

import config                                                          # -> config.py
from core import benutzerdaten                                         # -> core/benutzerdaten.py (Breite merken)
from core.layout import Scrollbereich                                  # -> core/layout.py
from core.widgets import Tooltip                                       # -> core/widgets.py

BREITE_STANDARD = 250
BREITE_MIN, BREITE_MAX = 170, 560
LANGER_TITEL = 26          # längere Titel bekommen in der Liste einen Tooltip mit dem ganzen Namen


class Seitenleiste(ctk.CTkFrame):
    """
    Die Liste links mit Griff zum Breiterziehen.
        leiste = Seitenleiste(master)
        leiste.liste      -> hier kommen die Knöpfe hinein (scrollbar, Spalte 0 wächst)
        leiste.umschalten()   ein-/ausblenden
    Alle Seitenleisten teilen sich EINE Breite (Einstellung "seitenliste_breite").
    """

    _alle = []

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=config.FARBEN["sidebar"], corner_radius=0, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.sl_breite = int(benutzerdaten.einstellung("seitenliste_breite", BREITE_STANDARD))
        self.sl_breite = max(BREITE_MIN, min(BREITE_MAX, self.sl_breite))
        self.liste = Scrollbereich(self, width=self.sl_breite, corner_radius=0, fg_color=config.FARBEN["sidebar"])
        self.liste.grid(row=0, column=0, sticky="nsw")
        self.liste.grid_columnconfigure(0, weight=1)
        # Griff: schmaler Streifen, Mauszeiger ↔
        self.sl_griff = ctk.CTkFrame(self, width=6, corner_radius=0, fg_color=config.FARBEN["rahmen"],
                                     cursor="sb_h_double_arrow")
        self.sl_griff.grid(row=0, column=1, sticky="ns")
        self.sl_griff.bind("<B1-Motion>", self._sl_ziehen)
        self.sl_griff.bind("<ButtonRelease-1>", self._sl_loslassen)
        self.sl_griff.bind("<Double-Button-1>", lambda _e: self.breite_setzen(BREITE_STANDARD, merken=True))
        Tooltip(self.sl_griff, "Ziehen: Liste breiter oder schmaler  ·  Doppelklick: Standardbreite")
        self.sl_sichtbar = True
        self.sl_timer = None
        Seitenleiste._alle.append(self)

    # ---- ein-/ausblenden ----------------------------------------------------
    def umschalten(self):
        if self.sl_sichtbar:
            self.grid_remove()                     # merkt sich die grid-Optionen, grid() stellt sie wieder her
        else:
            self.grid()
        self.sl_sichtbar = not self.sl_sichtbar

    # ---- Breite ziehen ------------------------------------------------------
    def _sl_ziehen(self, event):
        skalierung = self.liste._get_widget_scaling()
        neu = (event.x_root - self.winfo_rootx()) / skalierung
        self.sl_wunsch = int(max(BREITE_MIN, min(BREITE_MAX, neu)))
        if self.sl_timer is None:                  # höchstens alle 30 ms neu anordnen (sonst ruckelt es)
            self.sl_timer = self.after(30, self._sl_anwenden)

    def _sl_anwenden(self):
        self.sl_timer = None
        self.breite_setzen(self.sl_wunsch)

    def _sl_loslassen(self, _event):
        if hasattr(self, "sl_wunsch"):
            self.breite_setzen(self.sl_wunsch, merken=True)

    def breite_setzen(self, breite, merken=False):
        """Neue Breite für ALLE Seitenleisten (in jedem Bereich gleich)."""
        for leiste in list(Seitenleiste._alle):
            try:
                if leiste.winfo_exists() and leiste.sl_breite != breite:
                    leiste.sl_breite = breite
                    leiste.liste.configure(width=breite)
            except Exception:
                Seitenleiste._alle.remove(leiste)
        if merken:
            benutzerdaten.einstellung_setzen("seitenliste_breite", int(breite))


def listen_knopf(liste, text, befehl, titel=None, **kwargs):
    """Knopf in der Seitenliste. Lange Titel bekommen einen Tooltip mit dem ganzen Namen."""
    knopf = ctk.CTkButton(liste, text=text, anchor="w", command=befehl, **kwargs)
    if titel and len(titel) > LANGER_TITEL:
        Tooltip(knopf, titel)
    return knopf


class KopfNavigation:
    """
    Die vier Knöpfe links in der Kopfleiste. Danach geht es ab Spalte  kopf.naechste_spalte  weiter.
        kopf = KopfNavigation(leiste, app, seitenleiste, "🔧", "Bauteile", uebersicht=..., zurueck=...)
        kopf.uebersicht_zeigen("💡", "Übersicht Dioden")      # wenn eine Seite der Kategorie offen ist
        kopf.uebersicht_zeigen()                              # Bereichs-Icon (Übersicht des Bereichs)
    """

    def __init__(self, leiste, app, seitenleiste, bereich_icon, bereich_name, uebersicht, zurueck):
        self.bereich_icon, self.bereich_name = bereich_icon, bereich_name
        self.tipp = f"Übersicht {bereich_name}"
        rahmen = dict(fg_color="transparent", border_width=1, border_color=config.FARBEN["rahmen"],
                      text_color=config.FARBEN["text"], hover_color=config.FARBEN["rahmen"])
        knoepfe = [
            ("☰", seitenleiste.umschalten, "Seitenliste links ein-/ausblenden", rahmen),
            ("🏠", app.show_startseite, "Zur Startseite", {}),
            (bereich_icon, uebersicht, lambda: self.tipp, rahmen),
            ("◀", zurueck, "Eine Seite zurück", rahmen),
        ]
        self.knoepfe = []
        for spalte, (text, befehl, tipp, stil) in enumerate(knoepfe):
            knopf = ctk.CTkButton(leiste, text=text, width=40, height=36, font=(config.SCHRIFT, 16),
                                  command=befehl, **stil)
            knopf.grid(row=0, column=spalte, padx=(10 if spalte == 0 else 4, 4), pady=10)
            Tooltip(knopf, tipp)
            self.knoepfe.append(knopf)
        self.uebersicht_knopf = self.knoepfe[2]
        self.naechste_spalte = len(knoepfe)

    def uebersicht_zeigen(self, icon=None, tipp=None):
        """Icon + Tooltip des Übersicht-Knopfs setzen (ohne Angabe: Bereich)."""
        self.uebersicht_knopf.configure(text=icon or self.bereich_icon)
        self.tipp = tipp or f"Übersicht {self.bereich_name}"
