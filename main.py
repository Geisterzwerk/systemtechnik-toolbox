# =============================================================================
# main.py   <-  DIESE DATEI STARTEN  (F5 in VS Code  oder  "python main.py")
# -----------------------------------------------------------------------------
# Das Hauptfenster der Systemtechnik HF Toolbox.
#
# ORDNERSTRUKTUR:
#   main.py                  <- Hauptfenster + Umschalten der Bereiche
#   config.py                <- Farben, Pfade, Schriften, Layout-Werte
#   core/layout.py           <- ALLES zum Thema "mit der Fenstergrösse mitgehen"
#   core/widgets.py          <- Tooltip, SeitenBereich, FormatText, ...
#   core/bilder.py           <- Bilder finden und laden
#   gui/                     <- ein Bereich pro Datei (Startseite, Bauteile, ...)
#   bauteile/                <- die einzelnen Bauteil-Seiten
#   programmieren/engine/    <- Programmier-Wiki: laden, suchen, anzeigen
#   programmieren/inhalte/   <- die Wiki-Seiten (NUR Daten)
#   server/inhalte/          <- Server-/Linux-Wiki (NUR Daten, gleiche Engine wie Programmieren)
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
from gui import (bauteile_gui, messwerte_gui, messtechnik_gui, programmieren_gui,  # -> Ordner gui/
                 rechner_gui, schaltungen_gui, server_gui, startseite_gui)

ctk.set_appearance_mode("Dark")        # "Dark", "Light" oder "System"
ctk.set_default_color_theme("blue")

# (Name, Datei mit create(), Icon, Beschreibung) -> neue Zeile = neuer Bereich
BEREICHE = [
    ("Bauteile",      bauteile_gui,      "🔧", "Widerstand, Kondensator, Diode, Spule, ..."),
    ("Schaltungen",   schaltungen_gui,   "🔌", "Grundschaltungen und Filter"),
    ("Rechner",       rechner_gui,       "🧮", "Alle Rechner an einem Ort – Suche, nach Thema oder A–Z"),
    ("Messwerte",     messwerte_gui,     "📊", "Messwerte erfassen und auswerten"),
    ("Programmieren", programmieren_gui, "💻", "Python, C++ und C# nachschlagen - mit Suche"),
    ("Messtechnik",   messtechnik_gui,   "📏", "Messgeräte, Messfehler, Sensoren, AD-Wandler"),
    ("Server / Linux", server_gui,       "🐧", "Ubuntu Server per Konsole: Befehle, sudo, Dienste, Netzwerk, Sicherheit"),
]


class App(ctk.CTk):
    """Das Hauptfenster. Zeigt entweder die Startseite ODER die Tabs."""

    def __init__(self):
        super().__init__()
        self.title(config.APP_TITEL)
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
        startseite_gui.create(self.startseite, self)

        self.show_startseite()

    def _bereich_erstellen(self, name):
        """Bereich beim ersten Öffnen bauen -> gui/<bereich>_gui.py create(parent, app)."""
        if name not in self.seiten:
            self.seiten[name] = self.module[name].create(self.tabs.tab(name), self)

    def show_tab(self, tab_name):
        self.startseite.grid_forget()
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.tabs.set(tab_name)                  # set() ruft command NICHT auf ...
        self._bereich_erstellen(tab_name)        # ... deshalb hier selbst bauen

    def show_startseite(self):
        self.tabs.grid_forget()
        self.startseite.grid(row=0, column=0, sticky="nsew")

    def modus_wechseln(self, dunkel):
        """Dark/Light Mode (Schalter auf der Startseite)."""
        ctk.set_appearance_mode("Dark" if dunkel else "Light")
        # tk.Text / tk.Canvas passen sich nicht automatisch an -> Programmier-Seite neu zeichnen
        seite = self.seiten.get("Programmieren")
        if seite is not None and seite.aktuelles_thema:
            seite.thema_oeffnen(seite.aktuelles_thema, verlauf_merken=False)


# -----------------------------------------------------------------------------
# HÄNGER-WÄCHTER
# -----------------------------------------------------------------------------
# Die GUI setzt alle 500 ms einen "Herzschlag". Ein zweiter Thread prüft ihn.
# Kommt 5 Sekunden lang keiner (= Programm hängt), schreibt der Wächter auf,
# WO das Programm gerade feststeckt -> Datei  haenger_log.txt  im Projektordner.
# Diese Datei kannst du dann einfach an Copilot schicken.
# -----------------------------------------------------------------------------
HAENGER_LOG = os.path.join(config.BASIS_PFAD, "haenger_log.txt")


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
