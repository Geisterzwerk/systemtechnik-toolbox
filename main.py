# =============================================================================
# main.py   <-  DIESE DATEI STARTEN  (F5 in VS Code  oder  "python main.py")
# -----------------------------------------------------------------------------
# Das Hauptfenster von SystemLab (Name und Version: config.APP_NAME / APP_VERSION).
#
# ORDNERSTRUKTUR:
#   main.py                  <- Hauptfenster + Umschalten der Bereiche
#   config.py                <- Farben, Pfade, Schriften, Layout-Werte
#   core/layout.py           <- ALLES zum Thema "mit der Fenstergrösse mitgehen"
#   core/widgets.py          <- Tooltip, FormatText, info_box, ...
#   core/bilder.py           <- Bilder finden und laden
#   gui/                     <- ein Bereich pro Datei (Startseite, Bauteile, ...)
#   bauteile/                <- die einzelnen Bauteil-Seiten
#   programmieren/engine/    <- Programmier-Wiki: laden, suchen, anzeigen
#   programmieren/inhalte/   <- die Wiki-Seiten (NUR Daten)
#   server/inhalte/          <- Server-/Linux-Wiki (NUR Daten, gleiche Engine wie Programmieren)
#   schaltungen/, messtechnik/, digitaltechnik/  <- Wiki-Bereiche: inhalte/ (Daten), Rechner, Grafiken
#   images/                  <- alle Bilder
#
# ABLAUF BEIM START:
#   1. App() wird erstellt
#   2. Startseite wird gebaut          -> gui/startseite_gui.py
#   3. Tabs werden nur ANGELEGT. Ein Bereich wird erst gebaut, wenn man ihn
#      das erste Mal öffnet (schneller Start, nichts wird versteckt gezeichnet)
#   4. app.mainloop() wartet auf Klicks
# =============================================================================

import faulthandler
import os
import sys
import threading
import time
from datetime import datetime

import customtkinter as ctk

import config                                   # -> config.py
from core import benutzerdaten                  # -> core/benutzerdaten.py (Zuletzt geöffnet, Favoriten, Einstellungen)
from core import layout                         # -> core/layout.py (modus_gewechselt: Grafiken neu einfärben)
from core.inhalte_index import BEREICH_ICON, BEREICH_TEXT    # -> core/inhalte_index.py
from gui import (bauteile_gui, digitaltechnik_gui, messtechnik_gui,               # -> Ordner gui/
                 programmieren_gui, rechner_gui, schaltungen_gui, server_gui, startseite_gui)

ctk.set_appearance_mode(benutzerdaten.einstellung("modus", "Dark"))   # zuletzt gewählter Modus (Standard: Dark)
ctk.set_default_color_theme("blue")

# (Name, Datei mit create(), Icon, Beschreibung) -> neue Zeile = neuer Bereich
# Icon und Beschreibung stehen in core/inhalte_index.py (die Webversion braucht sie auch)
# Die Reihenfolge hier = Reihenfolge der Tabs (und der Kacheln auf der Startseite). Rechner ganz rechts.
BEREICHE = [(name, modul, BEREICH_ICON[name], BEREICH_TEXT[name]) for name, modul in [
    ("Bauteile", bauteile_gui),
    ("Schaltungen", schaltungen_gui),
    ("Digitaltechnik", digitaltechnik_gui),
    ("Programmieren", programmieren_gui),
    ("Messtechnik", messtechnik_gui),
    ("Server / Linux", server_gui),
    ("Rechner", rechner_gui),
]]


class App(ctk.CTk):
    """Das Hauptfenster. Zeigt entweder die Startseite ODER die Tabs."""

    def __init__(self):
        super().__init__()
        self.title(f"{config.APP_NAME} {config.APP_VERSION}")
        self._icon_setzen()
        self.geometry(config.FENSTER_GROESSE)
        self.minsize(*config.FENSTER_MIN)
        self.configure(fg_color=config.FARBEN["hintergrund"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.bereiche = BEREICHE
        self.module = {name: modul for name, modul, _, _ in BEREICHE}
        self.seiten = {}      # Name -> Objekt aus create() (erst nach dem 1. Öffnen)

        # ---- Tabs nur anlegen, Inhalt kommt beim ersten Öffnen ----
        self.tabs = ctk.CTkTabview(self, fg_color=config.FARBEN["hintergrund"],
                                   segmented_button_selected_color=config.FARBEN["akzent"],
                                   command=lambda: self._bereich_erstellen(self.tabs.get()))
        for name, _, _, _ in self.bereiche:
            self.tabs.add(name)

        # ---- Startseite -> gui/startseite_gui.py ----
        self.startseite = ctk.CTkFrame(self, fg_color=config.FARBEN["hintergrund"], corner_radius=0)
        self.startseite_inhalt = startseite_gui.create(self.startseite, self)

        self._tastenkuerzel()
        self.show_startseite()

    # =========================================================================
    # TASTENKÜRZEL (einmal zentral, gelten überall)
    # =========================================================================
    def _tastenkuerzel(self):
        """
        Ctrl+K   Suche auf der Startseite (von überall, auch mit Caps Lock / Shift = "K")
        bind_all  -> gilt in jedem Widget.
        bind_class Entry/Text -> ERSETZT die eingebaute Tk-Belegung (Ctrl+K löscht dort sonst bis Zeilenende)
                     und "break" verhindert, dass der Befehl doppelt läuft.
        """
        for taste in ("k", "K"):
            folge = f"<Control-{taste}>"
            self.bind_all(folge, self.suche_oeffnen)
            for klasse in ("Entry", "Text"):
                self.bind_class(klasse, folge, self.suche_oeffnen)

    def suche_oeffnen(self, _event=None):
        """Ctrl+K: Startseite zeigen, ins grosse Suchfeld springen, alten Suchtext markieren."""
        self.show_startseite()
        self.startseite_inhalt.suche.fokus()
        return "break"

    def _icon_setzen(self):
        """Fenster-Icon (Titelleiste + Taskleiste). Fehlt die Datei, bleibt das Standard-Icon - kein Absturz."""
        if os.path.exists(config.APP_ICON):
            try:
                self.iconbitmap(config.APP_ICON)       # customtkinter setzt danach kein eigenes Icon mehr
            except Exception as fehler:                # z.B. auf Linux (kein .ico) -> egal
                print("[Icon]", fehler)

    def _bereich_erstellen(self, name):
        """Bereich beim ersten Öffnen bauen -> gui/<bereich>_gui.py create(parent, app)."""
        if name not in self.seiten:
            self.seiten[name] = self.module[name].create(self.tabs.tab(name), self)
            self.seiten[name].bereich_name = name          # für Zuletzt geöffnet / Favoriten

    def show_tab(self, tab_name):
        self.startseite.grid_forget()
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.tabs.set(tab_name)                  # set() ruft command NICHT auf ...
        self._bereich_erstellen(tab_name)        # ... deshalb hier selbst bauen

    def show_startseite(self):
        self.tabs.grid_forget()
        self.startseite.grid(row=0, column=0, sticky="nsew")
        if getattr(self, "startseite_inhalt", None) is not None:
            self.startseite_inhalt.aktualisieren()          # neue Favoriten / zuletzt geöffnete Seiten

    def geoeffnet(self, seite, art, eintrag_id, titel, icon):
        """
        Ein Bereich meldet: Seite bzw. Rechner wurde geöffnet -> "Zuletzt geöffnet" (core/benutzerdaten.py).
        Gibt den Eintrag zurück (für den ⭐-Knopf der Kopfleiste).
        """
        eintrag = {"art": art, "bereich": getattr(seite, "bereich_name", ""), "id": eintrag_id, "titel": titel,
                   "icon": icon}
        if eintrag["bereich"]:
            benutzerdaten.zuletzt_merken(eintrag)
        return eintrag

    def modus_wechseln(self, dunkel):
        """Dark/Light Mode (Schalter auf der Startseite).
        customtkinter wechselt alle Farbpaare selbst. tk.Canvas (Grafiken, Schaltpläne, Banner, Symbole)
        und tk.Text (Fliesstext, Code) können das nicht -> core/layout.py modus_gewechselt() geht ALLE
        Widgets durch (offene Seite, versteckte Tabs, Startseite) und zeichnet sie neu.
        Bilder mit heller Variante (bild_hell.png) wechselt customtkinter ebenfalls selbst."""
        modus = "Dark" if dunkel else "Light"
        ctk.set_appearance_mode(modus)
        layout.modus_gewechselt(self)
        benutzerdaten.einstellung_setzen("modus", modus)


# -----------------------------------------------------------------------------
# HÄNGER-WÄCHTER
# -----------------------------------------------------------------------------
# Die GUI setzt alle 500 ms einen "Herzschlag". Ein zweiter Thread prüft ihn.
# Kommt 5 Sekunden lang keiner (= Programm hängt), schreibt der Wächter auf,
# WO das Programm gerade feststeckt -> Datei  haenger_log.txt  im Projektordner.
# Diese Datei kannst du dann einfach an Copilot schicken.
# -----------------------------------------------------------------------------
HAENGER_LOG = os.path.join(config.DATEN_PFAD, "haenger_log.txt")


def haenger_waechter_starten(app, grenze_s=5.0):
    herz = {"zeit": time.monotonic(), "gemeldet": False}

    def herzschlag():
        herz["zeit"] = time.monotonic()
        herz["gemeldet"] = False
        app.after(500, herzschlag)

    def waechter():
        while True:
            time.sleep(1)
            stille = time.monotonic() - herz["zeit"]
            if stille > grenze_s and not herz["gemeldet"]:
                herz["gemeldet"] = True
                with open(HAENGER_LOG, "a", encoding="utf-8") as f:
                    f.write(f"\n===== HÄNGER {datetime.now():%Y-%m-%d %H:%M:%S} "
                            f"(seit {stille:.0f} s keine Reaktion) =====\n")
                    f.flush()
                    faulthandler.dump_traceback(file=f, all_threads=True)
                print(f"\n[Wächter] Programm hängt! Details gespeichert in: {HAENGER_LOG}\n", file=sys.stderr)

    herzschlag()
    threading.Thread(target=waechter, daemon=True).start()


if __name__ == "__main__":
    app = App()
    haenger_waechter_starten(app)
    app.mainloop()
