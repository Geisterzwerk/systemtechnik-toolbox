# =============================================================================
# gui/gesamtsuche.py
# -----------------------------------------------------------------------------
# SUCHE ÜBER ALLES (Startseite): Wissensseiten aller Bereiche, Programmieren, Server und alle Rechner.
#
#   gesamtindex()        einmal aufgebaut, dann gemerkt: {schluessel: Eintrag} + Infos je Bereich
#   oeffnen(app, e)      springt in den richtigen Tab und öffnet Seite oder Rechner
#   eintrag_dict(e)      Eintrag als dict für core/benutzerdaten.py (Zuletzt / Favoriten)
#   SuchLeiste(master, app)   grosses Suchfeld mit Trefferliste darunter (Enter = erster Treffer)
#
# Die Suchlogik (Punkte, Tippfehler-Toleranz) ist dieselbe wie in den Bereichen:
#   programmieren/engine/suche.py -> Suchmaschine  (hier nur mit allen Einträgen zusammen)
# WER RUFT DAS AUF?  gui/startseite_gui.py
# =============================================================================

import os

import customtkinter as ctk

import config                                                          # -> config.py
import bauteile.rechner as rechner_registry                            # -> bauteile/rechner/__init__.py
from bauteile.rechner.rechner_info import KATEGORIEN, RECHNER_INFO     # -> bauteile/rechner/rechner_info.py
from programmieren.engine import lader                                 # -> programmieren/engine/lader.py
from programmieren.engine.suche import Suchmaschine                    # -> programmieren/engine/suche.py

# Bereich (Tab-Name in main.py) -> Inhalts-Ordner
BEREICH_ORDNER = {"Bauteile": "bauteile/inhalte", "Schaltungen": "schaltungen/inhalte",
                  "Digitaltechnik": "digitaltechnik/inhalte", "Messtechnik": "messtechnik/inhalte",
                  "Programmieren": "programmieren/inhalte", "Server / Linux": "server/inhalte"}
BEREICH_ICON = {"Bauteile": "🔧", "Schaltungen": "🔌", "Digitaltechnik": "💾", "Messtechnik": "📏",
                "Programmieren": "💻", "Server / Linux": "🐧", "Rechner": "🧮"}

_index = None


class Eintrag:
    """Ein Suchtreffer: Wissensseite oder Rechner (Felder so, wie die Suchmaschine sie erwartet)."""

    def __init__(self, art, bereich, eintrag_id, titel, kurz, stichworte, reihenfolge, daten, icon, ort):
        self.art, self.bereich, self.id = art, bereich, eintrag_id
        self.titel, self.kurz, self.stichworte = titel, kurz, stichworte
        self.reihenfolge, self.daten, self.icon, self.ort = reihenfolge, daten, icon, ort


def interaktiv(rechner_id):
    """Interaktive Grafik/Simulation (Titel endet bei uns immer mit „(interaktiv)“)."""
    info = RECHNER_INFO.get(rechner_id, {})
    return "interaktiv" in info.get("titel", "").lower()


def gesamtindex():
    """
    Rückgabe: {"eintraege": {schluessel: Eintrag}, "bereiche": {bereich: {"kategorien", "seiten", "rechner",
               "simulationen", "befehle"}}, "suche": Suchmaschine}
    """
    global _index
    if _index is not None:
        return _index
    eintraege, bereiche = {}, {}
    for bereich, ordner in BEREICH_ORDNER.items():
        kategorien, themen, _fehler = lader.alle_laden(os.path.join(config.BASIS_PFAD, ordner))
        rechner_ids, befehle = set(), 0
        for thema in themen.values():
            daten = thema.daten
            ids = set(daten.get("rechner", [])) | set(daten.get("grafiken", []))
            rechner_ids |= ids
            befehle += sum(len(g.get("zeilen", [])) for g in daten.get("befehle", []))
            eintraege[f"{bereich}:{thema.id}"] = Eintrag(
                "seite", bereich, thema.id, thema.titel, thema.kurz, thema.stichworte, thema.reihenfolge, daten,
                thema.kategorie.icon, f"{bereich} › {thema.kategorie.name}")
        bereiche[bereich] = {"kategorien": kategorien, "seiten": len(themen), "befehle": befehle,
                             "rechner": len([r for r in rechner_ids if not interaktiv(r)]),
                             "simulationen": len([r for r in rechner_ids if interaktiv(r)])}
    vorhanden = rechner_registry.registry()
    anzahl = 0
    for nummer, (rid, info) in enumerate(RECHNER_INFO.items()):
        if rid not in vorhanden:
            continue
        anzahl += 1
        icon = KATEGORIEN.get(info["kategorie"], ("🧮",))[0]
        eintraege[f"Rechner:{rid}"] = Eintrag(
            "rechner", "Rechner", rid, info["titel"], info["beschreibung"],
            info["stichworte"] + [info["unterkategorie"], info["kategorie"]], 500 + nummer, {}, icon,
            f"Rechner › {info['kategorie']} › {info['unterkategorie']}")
    bereiche["Rechner"] = {"kategorien": list(KATEGORIEN.items()), "seiten": 0, "befehle": 0,
                           "rechner": len([r for r in vorhanden if r in RECHNER_INFO and not interaktiv(r)]),
                           "simulationen": len([r for r in vorhanden if r in RECHNER_INFO and interaktiv(r)])}
    _index = {"eintraege": eintraege, "bereiche": bereiche, "suche": Suchmaschine(eintraege)}
    _index["anzahl_rechner"] = anzahl
    return _index


def eintrag_dict(e):
    return {"art": e.art, "bereich": e.bereich, "id": e.id, "titel": e.titel, "icon": e.icon}


def oeffnen(app, eintrag):
    """eintrag: Eintrag-Objekt oder dict (aus Zuletzt/Favoriten)."""
    art = eintrag["art"] if isinstance(eintrag, dict) else eintrag.art
    bereich = eintrag["bereich"] if isinstance(eintrag, dict) else eintrag.bereich
    eid = eintrag["id"] if isinstance(eintrag, dict) else eintrag.id
    app.show_tab(bereich)                                    # baut den Tab beim ersten Mal (main.py)
    seite = app.seiten.get(bereich)
    if seite is None:
        return
    if art == "rechner":
        seite.rechner_oeffnen(eid)
    else:
        if hasattr(seite, "ansicht"):
            seite.ansicht = "wissen"
        seite.thema_oeffnen(eid)


# =============================================================================
# SUCHLEISTE MIT TREFFERLISTE
# =============================================================================
class SuchLeiste(ctk.CTkFrame):
    MAX_TREFFER = 9

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.gs_feld = ctk.CTkEntry(self, height=46, font=(config.SCHRIFT, 16), corner_radius=23,
                                    border_width=2, border_color=config.FARBEN["akzent"],
                                    placeholder_text="🔍  In allen Bereichen suchen …  z.B. Tiefpass, chmod, "
                                                     "while-Schleife, Pt100, NE555   (Ctrl+K)")
        self.gs_feld.grid(row=0, column=0, sticky="ew")
        self.gs_feld.bind("<KeyRelease>", self._gs_tippen)
        self.gs_feld.bind("<Return>", self._gs_enter)
        self.gs_feld.bind("<Escape>", lambda _e: self.leeren())
        self.gs_liste = ctk.CTkFrame(self, fg_color=config.FARBEN["flaeche"], corner_radius=12, border_width=1,
                                     border_color=config.FARBEN["rahmen"])
        self.gs_liste.grid_columnconfigure(0, weight=1)
        self.gs_treffer = []

    def fokus(self):
        self.gs_feld.focus_set()

    def leeren(self):
        self.gs_feld.delete(0, "end")
        self._gs_zeigen([])

    def _gs_tippen(self, event=None):
        if event is not None and event.keysym in ("Return", "Escape", "Up", "Down", "Left", "Right"):
            return
        anfrage = self.gs_feld.get().strip()
        treffer = gesamtindex()["suche"].suchen(anfrage, max_treffer=self.MAX_TREFFER) if anfrage else []
        self._gs_zeigen(treffer, anfrage)

    def _gs_enter(self, _event=None):
        if self.gs_treffer:
            self._gs_oeffnen(self.gs_treffer[0])

    def _gs_oeffnen(self, eintrag):
        self.leeren()
        oeffnen(self.app, eintrag)

    def _gs_zeigen(self, treffer, anfrage=""):
        self.gs_treffer = treffer
        for kind in self.gs_liste.winfo_children():
            kind.destroy()
        if not anfrage:
            self.gs_liste.grid_forget()
            return
        self.gs_liste.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        if not treffer:
            ctk.CTkLabel(self.gs_liste, text=f"Nichts gefunden für „{anfrage}“ – anderes Wort oder kürzer versuchen.",
                         font=config.FONT_TEXT, text_color=config.FARBEN["text_leise"]).grid(
                row=0, column=0, sticky="w", padx=16, pady=10)
            return
        for zeile, e in enumerate(treffer):
            rahmen = ctk.CTkFrame(self.gs_liste, fg_color="transparent", corner_radius=0)
            rahmen.grid(row=zeile, column=0, sticky="ew", padx=6, pady=(6 if zeile == 0 else 0, 0))
            rahmen.grid_columnconfigure(0, weight=1)
            knopf = ctk.CTkButton(rahmen, text=f"{e.icon}  {e.titel}", anchor="w", height=32,
                                  font=(config.SCHRIFT, 14, "bold" if zeile == 0 else "normal"),
                                  fg_color=config.FARBEN["tipp"] if zeile == 0 else "transparent",
                                  text_color=config.FARBEN["text"], hover_color=config.FARBEN["rahmen"],
                                  command=lambda e=e: self._gs_oeffnen(e))
            knopf.grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(rahmen, text=f"{BEREICH_ICON.get(e.bereich, '')} {e.ort}", font=config.FONT_KLEIN,
                         text_color=config.FARBEN["text_leise"]).grid(row=0, column=1, sticky="e", padx=(8, 10))
        ctk.CTkLabel(self.gs_liste, text="Enter öffnet den ersten Treffer  ·  Esc leert die Suche",
                     font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"]).grid(
            row=len(treffer), column=0, sticky="w", padx=16, pady=(4, 8))
