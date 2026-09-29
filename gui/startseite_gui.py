# =============================================================================
# gui/startseite_gui.py
# -----------------------------------------------------------------------------
# STARTSEITE: Titel, Kacheln für alle Bereiche, Dark-Mode-Schalter, Tipp.
# WER RUFT DAS AUF?  main.py -> startseite_gui.create(self.startseite, self)
#
# Die Kacheln entstehen automatisch aus app.bereiche (Liste BEREICHE in main.py).
# Responsive: 3 Kacheln pro Zeile, bei schmalem Fenster 2 oder 1.
# =============================================================================

import random

import customtkinter as ctk

import config                                                          # -> config.py
from core.layout import Karte, ResponsiveGrid, ScrollSeite, Stapel, WrapLabel   # -> core/layout.py

TIPPS = [
    "P = U · I   (Leistung = Spannung × Strom)",
    "τ = R · C   - nach 5τ ist ein Kondensator praktisch voll geladen",
    "Python: Einrückung ist Teil der Syntax - 4 Leerzeichen pro Ebene",
    "C++: int hat meist 32 Bit, long unter Windows aber auch nur 32 Bit!",
    "In der Toolbox: Ctrl+F springt auf der Programmier-Seite ins Suchfeld",
    "C#: decimal statt double verwenden, wenn es um Geld geht",
    "1 Byte = 8 Bit  →  Wertebereich 0 … 255 (unsigned)",
]


def create(master, app):
    master.grid_rowconfigure(0, weight=1)
    master.grid_columnconfigure(0, weight=1)

    scroll = ScrollSeite(master, max_breite=1000)          # -> core/layout.py
    scroll.grid(row=0, column=0, sticky="nsew")
    body = scroll.body
    s = Stapel(body)

    # ---- Titel (zentriert) ----
    s.add(WrapLabel(body, text=config.APP_TITEL, font=(config.SCHRIFT, 34, "bold"),
                    anchor="center", justify="center", text_color=config.FARBEN["text"]), pady=(40, 2))
    s.add(WrapLabel(body, text=config.APP_UNTERTITEL, font=config.FONT_UNTERTITEL,
                    anchor="center", justify="center", text_color=config.FARBEN["text_leise"]), pady=(0, 28))

    # ---- Kacheln ----
    kacheln = s.add(ResponsiveGrid(body, min_spaltenbreite=260, max_spalten=3))
    for name, _modul, icon, beschreibung in app.bereiche:
        kachel = kacheln.add(Karte(kacheln, titel=f"{icon}  {name}", untertitel=beschreibung))
        # Button -> main.py App.show_tab(name)
        ctk.CTkButton(kachel.body, text="Öffnen  →", height=30,
                      command=lambda n=name: app.show_tab(n)).grid(row=0, column=0, sticky="w")

    # ---- Dark Mode + Tipp ----
    unten = s.add(ctk.CTkFrame(body, fg_color="transparent"), pady=(16, 0))
    unten.grid_columnconfigure(0, weight=1)
    schalter = ctk.CTkSwitch(unten, text="Dark Mode", font=config.FONT_TEXT,
                             command=lambda: app.modus_wechseln(schalter.get() == 1))
    if ctk.get_appearance_mode() == "Dark":
        schalter.select()
    schalter.grid(row=0, column=0, pady=(0, 12))
    WrapLabel(unten, text=f"💡 Tipp: {random.choice(TIPPS)}", font=config.FONT_TEXT, anchor="center",
              justify="center", text_color=config.FARBEN["text_leise"]).grid(row=1, column=0, sticky="ew")
