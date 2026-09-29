# =============================================================================
# bauteile/rechner/basis.py
# -----------------------------------------------------------------------------
# BAUSTEINE für alle Rechner.
#
#   EinheitenEingabe   Eingabefeld + Einheiten-Dropdown dahinter  [ 4.7 ][kΩ ▾]
#                      versteht auch "4k7", "2.2M", "470m", "4R7" direkt im Feld
#   Auswahl            Dropdown für Optionen (z.B. "E12" / "E24", Material)
#   FormelRechner      Kompletter Rechner als Karte: Felder + Berechnen + Ergebnis.
#                      Man beschreibt nur die Felder und schreibt eine Funktion,
#                      die rechnet - die Oberfläche entsteht automatisch.
#   RechnerFehler      Für verständliche Fehlermeldungen: raise RechnerFehler("...")
#
# BEISPIEL (so entsteht ein neuer Rechner):
#
#   def _rechnen(w):                       # w = {"U": 12.0, "R": None, ...} in Basiseinheiten
#       if w["U"] is None or w["R"] is None:
#           raise RechnerFehler("U und R eingeben")
#       return [f"I = {fmt(w['U'] / w['R'], 'strom')}"]      # Liste von Ergebniszeilen
#
#   FormelRechner(master, "Strom", "aus U und R",
#                 felder=[("U", "Spannung U", "spannung"),
#                         ("R", "Widerstand R", "widerstand", {"einheit": "kΩ"})],
#                 berechnen=_rechnen, formel="I = U / R")
#
# NAMEN: Alle eigenen Attribute beginnen mit ee_ / fr_ / aw_, damit sie nie mit
#        internen Namen von tkinter/CustomTkinter kollidieren (siehe _configure-Fehler!).
# =============================================================================

import customtkinter as ctk

import config                                            # -> config.py
from bauteile import einheiten                           # -> bauteile/einheiten.py
from core.layout import Karte, WrapLabel                 # -> core/layout.py

fmt = einheiten.formatieren                              # Kurzname für Ergebnisse


class RechnerFehler(Exception):
    """Verständliche Meldung an den Benutzer (wird im Ergebnisfeld angezeigt)."""


# =============================================================================
# EINGABEFELD MIT EINHEIT
# =============================================================================
class EinheitenEingabe(ctk.CTkFrame):
    """
    [ Eingabe ][ kΩ ▾ ]
    wert()  -> Wert in Basiseinheit (Ω, V, A, F ...) oder None, wenn leer
    liste=True -> mehrere Werte "1k 2k2 470" -> wert() gibt eine Liste zurück
    """

    def __init__(self, master, typ, platzhalter="", einheit=None, breite=140, liste=False):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.ee_typ = typ
        self.ee_liste = liste
        info = einheiten.EINHEITEN[typ]
        self.ee_faktoren = dict(info["stufen"])

        self.ee_feld = ctk.CTkEntry(self, placeholder_text=platzhalter, width=breite * (2 if liste else 1))
        self.ee_feld.grid(row=0, column=0, sticky="w")

        namen = [n for n, _ in info["stufen"]]
        if len(namen) > 1:
            # Dropdown mit den Einheiten (mΩ, Ω, kΩ, MΩ ...)
            self.ee_menue = ctk.CTkOptionMenu(self, values=namen, width=74, dynamic_resizing=False)
            self.ee_menue.set(einheit or info["standard"])
            self.ee_menue.grid(row=0, column=1, sticky="w", padx=(6, 0))
        else:
            self.ee_menue = None
            ctk.CTkLabel(self, text=namen[0], width=74, anchor="w").grid(row=0, column=1, sticky="w", padx=(6, 0))

    def _faktor(self):
        if self.ee_menue is None:
            return next(iter(self.ee_faktoren.values()))
        return self.ee_faktoren[self.ee_menue.get()]

    def wert(self):
        text = self.ee_feld.get()
        if self.ee_liste:
            return einheiten.text_zu_liste(text, self.ee_typ, self._faktor())
        return einheiten.text_zu_zahl(text, self.ee_typ, self._faktor())

    def setzen(self, wert):
        """Wert (Basiseinheit) eintragen, passende Einheit wird gewählt."""
        self.leeren()
        if wert is None:
            return
        name, zahl = einheiten.stufe_waehlen(wert, self.ee_typ)
        if self.ee_menue is not None:
            self.ee_menue.set(name)
        self.ee_feld.insert(0, f"{zahl:.6g}")

    def leeren(self):
        self.ee_feld.delete(0, "end")

    def bei_enter(self, funktion):
        self.ee_feld.bind("<Return>", lambda e: funktion())


class TextEingabe(ctk.CTkEntry):
    """Freitext-Feld (z.B. für Codes wie '104K'). wert() -> Text oder None."""

    def __init__(self, master, platzhalter="", breite=220):
        super().__init__(master, placeholder_text=platzhalter, width=breite)

    def wert(self):
        return self.get().strip() or None

    def leeren(self):
        self.delete(0, "end")

    def bei_enter(self, funktion):
        self.bind("<Return>", lambda e: funktion())


class Auswahl(ctk.CTkOptionMenu):
    """Dropdown für Optionen. wert() -> gewählter Text."""

    def __init__(self, master, werte, standard=None, breite=220, bei_aenderung=None):
        super().__init__(master, values=list(werte), width=breite, dynamic_resizing=False,
                         command=(lambda _w: bei_aenderung()) if bei_aenderung else None)
        self.set(standard or werte[0])

    def wert(self):
        return self.get()

    def leeren(self):
        pass

    def bei_enter(self, funktion):
        pass


# =============================================================================
# FORMEL-RECHNER (Karte)
# =============================================================================
class FormelRechner(Karte):
    """
    felder: Liste von (schluessel, beschriftung, typ, optionen)
        typ       Einheiten-Typ aus bauteile/einheiten.py  ODER  "auswahl"  ODER  "text"
        optionen  dict (optional):
                    "einheit": "kΩ"          Startwert im Dropdown
                    "platzhalter": "z.B. 12"
                    "liste": True            mehrere Werte in einem Feld
                    "werte": [...]           nur bei typ "auswahl"
    berechnen(werte) -> Liste von Textzeilen (oder raise RechnerFehler)
    formel    kleiner grauer Text unter dem Ergebnis, z.B. "R = U / I"
    """

    def __init__(self, master, titel, untertitel, felder, berechnen, formel=None):
        super().__init__(master, titel=titel, untertitel=untertitel)
        self.fr_funktion = berechnen
        self.fr_felder = {}

        b = self.body
        b.grid_columnconfigure(0, weight=0)
        b.grid_columnconfigure(1, weight=1)

        # ---- Eingabefelder ----
        for zeile, eintrag in enumerate(felder):
            schluessel, beschriftung, typ = eintrag[:3]
            opt = eintrag[3] if len(eintrag) > 3 else {}
            ctk.CTkLabel(b, text=beschriftung, anchor="w").grid(row=zeile, column=0, sticky="w", padx=(0, 12), pady=3)
            if typ == "auswahl":
                feld = Auswahl(b, opt["werte"], opt.get("standard"))
            elif typ == "text":
                feld = TextEingabe(b, opt.get("platzhalter", ""))
            else:
                feld = EinheitenEingabe(b, typ, opt.get("platzhalter", ""), opt.get("einheit"),
                                        liste=opt.get("liste", False))
            feld.grid(row=zeile, column=1, sticky="w", pady=3)
            feld.bei_enter(self.fr_rechnen)               # Enter im Feld = Berechnen
            self.fr_felder[schluessel] = feld

        n = len(felder)
        # ---- Knöpfe ----
        knoepfe = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        knoepfe.grid(row=n, column=0, columnspan=2, sticky="w", pady=(10, 6))
        ctk.CTkButton(knoepfe, text="Berechnen", width=110, command=self.fr_rechnen).grid(row=0, column=0)
        ctk.CTkButton(knoepfe, text="Leeren", width=80, fg_color="transparent", border_width=1,
                      border_color=config.FARBEN["rahmen"], text_color=config.FARBEN["text"],
                      command=self.fr_leeren).grid(row=0, column=1, padx=(8, 0))

        # ---- Ergebnis + Formel ----
        self.fr_ergebnis = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"),
                                     text_color=config.FARBEN["akzent"])
        self.fr_ergebnis.grid(row=n + 1, column=0, columnspan=2, sticky="ew")
        if formel:
            WrapLabel(b, text=f"Formel: {formel}", font=config.FONT_KLEIN,
                      text_color=config.FARBEN["text_leise"]).grid(row=n + 2, column=0, columnspan=2,
                                                                   sticky="ew", pady=(6, 0))

    def fr_rechnen(self):
        try:
            werte = {k: f.wert() for k, f in self.fr_felder.items()}
            zeilen = self.fr_funktion(werte)
            self.fr_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
        except RechnerFehler as fehler:
            self._fr_fehler(str(fehler))
        except ValueError as fehler:
            self._fr_fehler(f"Ungültige Eingabe: {fehler}")
        except ZeroDivisionError:
            self._fr_fehler("Division durch 0 - ein Wert darf nicht 0 sein")
        except OverflowError:
            self._fr_fehler("Ergebnis ist zu gross")

    def _fr_fehler(self, text):
        self.fr_ergebnis.configure(text=f"⚠ {text}", text_color=("#B45309", "#F59E0B"))

    def fr_leeren(self):
        for feld in self.fr_felder.values():
            feld.leeren()
        self.fr_ergebnis.configure(text="")


def anzahl_gegeben(werte, *schluessel):
    """Wie viele der genannten Felder sind ausgefüllt?"""
    return sum(werte[s] is not None for s in schluessel)
