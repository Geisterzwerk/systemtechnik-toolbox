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
#   WertRegler         Slider + Zahlenfeld + Einheit, immer synchron (für interaktive Grafiken)
#                      [U1      ═══════●═══════  [ 230 ][V ▾]]
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


# =============================================================================
# WERT-REGLER: Slider + Zahlenfeld + Einheit (für interaktive Grafiken)
# =============================================================================
class WertRegler(ctk.CTkFrame):
    """
    [Beschriftung]  ═══════●═══════  [ 230 ][V ▾]
                                     ⚠ Meldung (nur bei ungültiger Eingabe)

    - Slider bewegen  -> Zahlenfeld zeigt den Wert sofort an
    - Zahl eintippen  -> Enter oder Feld verlassen übernimmt, Slider springt mit
    - Einheit wählen  -> derselbe Wert wird in der neuen Einheit angezeigt
    - Ungültig        -> Feld rot + Erklärung, der alte Wert bleibt (nie still korrigieren)

    text           Beschriftung links
    typ            Einheiten-Typ aus bauteile/einheiten.py ("spannung", "widerstand", "zahl" ...)
    von, bis       Bereich des Sliders (in Basiseinheit: V, Ω, A, s ...)
    start          Startwert
    einheit        Startauswahl im Dropdown (z.B. "kΩ"), None = Standard des Typs
    grenzen        (min, max) für das Zahlenfeld. Liegt ein Wert ausserhalb des Sliders,
                   aber innerhalb der Grenzen, wird er angenommen und der Slider wächst mit.
                   Standard: (von, bis)
    ganzzahl       True -> nur ganze Zahlen (z.B. Windungen)
    schritte       Raststufen des Sliders (None = stufenlos, bei ganzzahl automatisch)
    bei_aenderung  Funktion ohne Argumente, wird nach jeder GÜLTIGEN Änderung aufgerufen

    wert()                       -> aktueller Wert (Basiseinheit)
    setzen(wert)                 -> Wert von aussen setzen (ruft bei_aenderung NICHT auf)
    bereich_setzen(von, bis, w)  -> neuer Slider-Bereich (z.B. Zeitachse 0 … 5τ)

    NAMEN: eigene Attribute beginnen mit wr_ (keine Kollision mit tkinter).
    """

    ROT = ("#DC2626", "#F87171")

    def __init__(self, master, text, typ, von, bis, start, einheit=None, grenzen=None, ganzzahl=False,
                 schritte=None, bei_aenderung=None, text_breite=150):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.wr_typ = typ
        self.wr_von, self.wr_bis = von, bis
        self.wr_grenzen = grenzen or (von, bis)
        self.wr_ganzzahl = ganzzahl
        self.wr_schritte = schritte
        self.wr_funktion = bei_aenderung
        self.wr_wert = start
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text=text, anchor="w", width=text_breite).grid(row=0, column=0, sticky="w")
        self.wr_slider = ctk.CTkSlider(self, from_=von, to=bis, number_of_steps=self._wr_stufen(),
                                       command=self._wr_slider_bewegt)
        self.wr_slider.grid(row=0, column=1, sticky="ew", padx=8, pady=3)

        self.wr_feld = EinheitenEingabe(self, typ, "", einheit, breite=72)      # -> Klasse oben
        self.wr_feld.grid(row=0, column=2, sticky="e")
        self.wr_feld.bei_enter(self._wr_feld_uebernehmen)
        self.wr_feld.ee_feld.bind("<FocusOut>", lambda _e: self._wr_feld_uebernehmen(), add="+")
        if self.wr_feld.ee_menue is not None:
            self.wr_feld.ee_menue.configure(command=lambda _v: self._wr_feld_schreiben())
        self.wr_rand = self.wr_feld.ee_feld.cget("border_color")

        self.wr_meldung = WrapLabel(self, text="", font=config.FONT_KLEIN, text_color=self.ROT)

        self.wr_slider.set(self._wr_im_slider(start))
        self._wr_feld_schreiben()

    # ---- von aussen ---------------------------------------------------------
    def wert(self):
        return self.wr_wert

    def setzen(self, wert):
        self._wr_bereich_erweitern(wert)
        self.wr_wert = wert
        self.wr_slider.set(wert)
        self._wr_feld_schreiben()
        self._wr_ok()

    def bereich_setzen(self, von, bis, wert=None):
        """Slider-Bereich und Grenzen neu setzen, z.B. wenn sich τ ändert."""
        self.wr_von, self.wr_bis = von, bis
        self.wr_grenzen = (von, bis)
        self.wr_slider.configure(from_=von, to=bis, number_of_steps=self._wr_stufen())
        if self.wr_feld.ee_menue is not None and bis > 0:      # Einheit passend zum Bereich (5 s statt 5000 ms)
            self.wr_feld.ee_menue.set(einheiten.stufe_waehlen(bis, self.wr_typ)[0])
        self.setzen(min(max(self.wr_wert if wert is None else wert, von), bis))

    # ---- intern -------------------------------------------------------------
    def _wr_stufen(self):
        if self.wr_ganzzahl:
            return max(1, int(round(self.wr_bis - self.wr_von)))
        return self.wr_schritte

    def _wr_im_slider(self, wert):
        return min(max(wert, self.wr_von), self.wr_bis)

    def _wr_bereich_erweitern(self, wert):
        """Wert ausserhalb des Sliders (aber erlaubt) -> Slider-Bereich wächst mit."""
        if wert < self.wr_von or wert > self.wr_bis:
            self.wr_von, self.wr_bis = min(self.wr_von, wert), max(self.wr_bis, wert)
            self.wr_slider.configure(from_=self.wr_von, to=self.wr_bis, number_of_steps=self._wr_stufen())

    def _wr_slider_bewegt(self, wert):
        wert = float(wert)
        if self.wr_ganzzahl:
            wert = float(round(wert))
        self.wr_wert = wert
        self._wr_feld_schreiben()
        self._wr_ok()
        if self.wr_funktion:
            self.wr_funktion()

    def _wr_feld_schreiben(self):
        """Aktuellen Wert in der gerade gewählten Einheit ins Feld schreiben."""
        zahl = self.wr_wert / self.wr_feld._faktor()
        text = f"{zahl:.0f}" if self.wr_ganzzahl else f"{zahl:.4g}"
        self.wr_feld.leeren()
        self.wr_feld.ee_feld.insert(0, text)
        self.wr_text = text                      # merken: unverändert -> nichts übernehmen

    def _wr_feld_uebernehmen(self):
        if self.wr_feld.ee_feld.get() == self.wr_text:      # nur angeklickt, nichts geändert
            self._wr_ok()
            return
        try:
            wert = self.wr_feld.wert()
        except ValueError as fehler:
            self._wr_fehler(str(fehler))
            return
        if wert is None:
            self._wr_fehler("Bitte einen Wert eingeben")
            return
        unten, oben = self.wr_grenzen
        if not unten <= wert <= oben:
            self._wr_fehler(f"Erlaubt: {fmt(unten, self.wr_typ)} … {fmt(oben, self.wr_typ)}")
            return
        if self.wr_ganzzahl and abs(wert - round(wert)) > 1e-9:
            self._wr_fehler("Nur ganze Zahlen erlaubt")
            return
        geaendert = abs(wert - self.wr_wert) > 1e-12 * max(1.0, abs(wert))
        self.setzen(wert)
        if geaendert and self.wr_funktion:
            self.wr_funktion()

    def _wr_fehler(self, text):
        self.wr_feld.ee_feld.configure(border_color=self.ROT)
        self.wr_meldung.configure(text=f"⚠ {text}")
        self.wr_meldung.grid(row=1, column=1, columnspan=2, sticky="ew", padx=8)

    def _wr_ok(self):
        self.wr_feld.ee_feld.configure(border_color=self.wr_rand)
        self.wr_meldung.grid_remove()
