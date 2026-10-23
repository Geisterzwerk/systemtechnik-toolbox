# =============================================================================
# bauteile/grafiken/schaltung_karte.py
# -----------------------------------------------------------------------------
# FENSTER-KARTE um ein SchaltungsModell (customtkinter):
#   [Variante] [Schalter] [Pfeile]                                    [❓]
#   Auswahlfelder / Textfelder (optional mit Logik-Tastenleiste)
#   Schaltplan mit Werten (tk.Canvas) - Klickbereiche (z.B. KV-Felder) anklickbar
#   Regler (Slider + Zahlenfeld + Einheit)
#   [Knöpfe des Modells, z.B. 1τ … 5τ]                      [↺ Zurücksetzen]
#   Ergebnis als Tabelle (core/widgets.py WerteAnzeige) + Erklärung
#
# Rechnen und Zeichnen macht das Modell (bauteile/grafiken/schaltplan.py -> SchaltungsModell,
# Unterklassen in schaltungen/grafiken*.py). Diese Datei kümmert sich NUR um das Fenster.
#
#   karte = SchaltungsKarte(master, SpannungsteilerSchaltung())
#   karte.sk_modell          das Modell
#   karte.sk_regler          {"ue": WertRegler, ...}
#   karte.sk_variante        Umschalter oder None
#   karte.sk_schalter        {"taster": CTkSwitch, ...}
#   karte.sk_auswahl         {"sender": Auswahl, ...}      (Modell.AUSWAHL, Dropdown)
#   karte.sk_texte           {"zahl": CTkEntry, ...}       (Modell.TEXTFELDER, Enter oder Verlassen = übernehmen)
#   karte.sk_neu()           neu rechnen + zeichnen (nach jeder Änderung)
#   karte.sk_zuruecksetzen() alles wie beim Öffnen
#
# UNGÜLTIGE EINGABE: Die Grafik bleibt beim letzten gültigen Stand stehen (verschwindet nicht),
# das geänderte Textfeld wird rot umrandet und die Meldung steht im Ergebnis.
#
# WER RUFT DAS AUF?  SchaltungsModell.karte_bauen() (bauteile/grafiken/schaltplan.py),
#                    das wiederum GrafikVerweis aus bauteile/rechner/kern.py beim Öffnen aufruft
# =============================================================================

import customtkinter as ctk

import config                                                            # -> config.py
from bauteile.grafiken.schaltplan import Schaltplan, text_eingabe        # -> grafiken/schaltplan.py
from bauteile.rechner.basis import Auswahl, WertRegler                   # -> rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel               # -> core/layout.py
from core.widgets import LogikTastatur, Tooltip, WerteAnzeige            # -> core/widgets.py

ROT = ("#DC2626", "#F87171")

ALLGEMEINE_HILFE = """## Bedienung
- **Regler ziehen** oder rechts eine **Zahl eintippen** (Enter oder Feld verlassen übernimmt)
- **Einheit** rechts wählen – der Regler gilt dann in dieser Einheit (z.B. 0 … 1000 mV)
- Oben: **Varianten** und **Schalter** der Schaltung umschalten
- **↺ Zurücksetzen** stellt alles wieder wie beim Öffnen ein
- Unter der Grafik stehen die berechneten Werte und was die Grafik zeigt"""


class SchaltungsKarte(Karte):
    """Eigene Attribute beginnen mit sk_ (keine Kollision mit tkinter)."""

    def __init__(self, master, modell):
        self.sk_modell = m = modell
        super().__init__(master, titel=m.TITEL, untertitel=m.UNTERTITEL, hilfe=self._sk_hilfetext)
        b = self.body
        zeile = 0
        self.sk_variante = None
        self.sk_schalter = {}
        self.sk_gut = None                     # letzter GÜLTIGER Stand: (werte, ergebnis, variante)
        self.sk_pfeile_an = True
        self.sk_klickbereiche = []

        # ---- oben: Varianten, Schalter, Pfeile ein/aus ----
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=zeile, column=0, sticky="w", pady=(0, 6))
        zeile += 1
        spalte = 0
        if m.VARIANTEN:
            self.sk_variante = ctk.CTkSegmentedButton(oben, values=m.VARIANTEN, command=lambda _v: self.sk_neu())
            self.sk_variante.set(m.VARIANTEN[0])
            self.sk_variante.grid(row=0, column=0, sticky="w", padx=(0, 16), pady=2)
            spalte = 1
        for schluessel, text in m.SCHALTER:
            schalter = ctk.CTkSwitch(oben, text=text, command=self.sk_neu)
            schalter.grid(row=0, column=spalte, sticky="w", padx=(0, 16), pady=2)
            self.sk_schalter[schluessel] = schalter
            spalte += 1
        # erscheint erst, wenn der Plan wirklich Strom-/Spannungspfeile zeichnet (siehe _sk_zeichnen)
        self.sk_pfeil_schalter = ctk.CTkSwitch(oben, text="Strom-/Spannungspfeile", command=self._sk_pfeile_umschalten)
        self.sk_pfeil_schalter.select()
        self.sk_pfeil_spalte = spalte

        # ---- Auswahl- und Textfelder ----
        self.sk_auswahl, self.sk_texte = {}, {}
        if m.AUSWAHL or m.TEXTFELDER:
            eingaben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
            eingaben.grid(row=zeile, column=0, sticky="w", pady=(0, 6))
            zeile += 1
            r = 0
            for schluessel, text, optionen, start in m.AUSWAHL:
                ctk.CTkLabel(eingaben, text=text, anchor="w").grid(row=r, column=0, sticky="w", padx=(0, 8), pady=2)
                feld = Auswahl(eingaben, optionen, start, breite=240, bei_aenderung=self.sk_neu)
                feld.grid(row=r, column=1, sticky="w", pady=2)
                self.sk_auswahl[schluessel] = feld
                r += 1
            for schluessel, text, start, opt in m.TEXTFELDER:
                ctk.CTkLabel(eingaben, text=text, anchor="w").grid(row=r, column=0, sticky="w", padx=(0, 8), pady=2)
                feld = ctk.CTkEntry(eingaben, width=240, font=(config.SCHRIFT_CODE, 14),
                                    placeholder_text=opt.get("platzhalter", ""))
                feld.insert(0, start)
                feld.bind("<Return>", lambda _e: self.sk_neu())
                feld.bind("<FocusOut>", lambda _e: self.sk_neu(), add="+")
                feld.grid(row=r, column=1, sticky="w", pady=2)
                self.sk_texte[schluessel] = feld
                r += 1
                if opt.get("tastatur") == "logik":                      # -> core/widgets.py LogikTastatur
                    LogikTastatur(eingaben, feld, self.sk_neu, variablen=opt.get("variablen", "ABCD")).grid(
                        row=r, column=1, sticky="w", pady=(0, 4))
                    r += 1
            self.sk_rand = next(iter(self.sk_texte.values())).cget("border_color") if self.sk_texte else None

        # ---- Zeichenfläche ----
        self.sk_canvas = ResponsiveCanvas(b, self._sk_zeichnen, seitenverhaeltnis=m.SEITENVERHAELTNIS,
                                          max_hoehe=m.MAX_HOEHE)
        self.sk_canvas.grid(row=zeile, column=0, sticky="ew")
        self.sk_canvas.bind("<Button-1>", self._sk_klick)
        self.sk_canvas.bind("<Motion>", self._sk_maus)
        zeile += 1

        # ---- Regler ----
        self.sk_regler = {}
        for schluessel, text, typ, von, bis, start, *opt in m.REGLER:
            regler = WertRegler(b, text, typ, von, bis, start, bei_aenderung=self.sk_neu, text_breite=150,
                                **(opt[0] if opt else {}))
            regler.grid(row=zeile, column=0, sticky="ew", pady=(4, 0))
            self.sk_regler[schluessel] = regler
            zeile += 1

        # ---- Knöpfe des Modells + Zurücksetzen ----
        knoepfe = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        knoepfe.grid(row=zeile, column=0, sticky="ew", pady=(8, 0))
        knoepfe.grid_columnconfigure(len(m.KNOEPFE), weight=1)
        for nummer, (text, aktion) in enumerate(m.KNOEPFE):
            ctk.CTkButton(knoepfe, text=text, width=52, height=28, fg_color="transparent", border_width=1,
                          border_color=config.FARBEN["akzent"], text_color=config.FARBEN["akzent"],
                          hover_color=config.FARBEN["rahmen"],
                          command=lambda a=aktion: self._sk_knopf(a)).grid(row=0, column=nummer, padx=(0, 6))
        zurueck = ctk.CTkButton(knoepfe, text=config.TEXT_ZURUECKSETZEN, width=120, height=28, fg_color="transparent",
                                border_width=1, border_color=config.FARBEN["rahmen"], text_color=config.FARBEN["text"],
                                hover_color=config.FARBEN["rahmen"], command=self.sk_zuruecksetzen)
        zurueck.grid(row=0, column=len(m.KNOEPFE) + 1, sticky="e")
        Tooltip(zurueck, "Alle Regler, Schalter und Felder wieder auf die Startwerte")
        zeile += 1

        # ---- Ergebnis + Erklärung ----
        self.sk_ergebnis = WerteAnzeige(b)
        self.sk_ergebnis.grid(row=zeile, column=0, sticky="ew", pady=(8, 0))
        WrapLabel(b, text=m.ERKLAERUNG, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"]).grid(
            row=zeile + 1, column=0, sticky="ew", pady=(8, 0))
        self.sk_groesse = (0, 0)
        self.sk_e = None
        self.sk_neu()

    # =========================================================================
    # WERTE LESEN / SETZEN
    # =========================================================================
    def _sk_werte(self):
        """Alle Reglerwerte und Schalterstellungen: {"ue": 12.0, "taster": False, ...}"""
        werte = {k: r.wert() for k, r in self.sk_regler.items()}
        werte.update({k: bool(s.get()) for k, s in self.sk_schalter.items()})
        werte.update({k: a.wert() for k, a in self.sk_auswahl.items()})
        laenge = {f[0]: f[3].get("max", 40) for f in self.sk_modell.TEXTFELDER}
        werte.update({k: text_eingabe(f.get(), laenge[k]) for k, f in self.sk_texte.items()})
        return werte

    def _sk_werte_setzen(self, neue):
        """{schluessel: wert} in die passenden Bedienelemente schreiben (ohne neu zu rechnen).
        "__variante__": wert  stellt den Umschalter um, OHNE die Startwerte der Variante zu laden."""
        for schluessel, wert in neue.items():
            if schluessel == "__variante__":
                if self.sk_variante is not None and wert in self.sk_modell.VARIANTEN:
                    self.sk_variante.set(wert)
                    self.sk_letzte_variante = wert
            elif schluessel in self.sk_regler:
                self.sk_regler[schluessel].setzen(wert)
            elif schluessel in self.sk_auswahl:
                self.sk_auswahl[schluessel].set(wert)
            elif schluessel in self.sk_texte:
                self.sk_texte[schluessel].delete(0, "end")
                self.sk_texte[schluessel].insert(0, wert)
            elif schluessel in self.sk_schalter:
                (self.sk_schalter[schluessel].select if wert else self.sk_schalter[schluessel].deselect)()

    def sk_v(self):
        return self.sk_variante.get() if self.sk_variante else None

    # =========================================================================
    # RECHNEN + ZEICHNEN
    # =========================================================================
    def sk_neu(self):
        """Nach jeder Änderung: neu rechnen, Text setzen, Plan neu zeichnen."""
        v = self.sk_v()
        if v != getattr(self, "sk_letzte_variante", v):                   # Variante gewechselt -> Startwerte
            self._sk_werte_setzen(self.sk_modell.STARTWERTE.get(v, {}))
        self.sk_letzte_variante = v
        w = self._sk_werte()
        try:
            e = self.sk_modell.sk_rechnen(w, v)
            zeilen, farbe = self.sk_modell.sk_info(w, e, v)
        except ValueError as fehler:
            # Grafik bleibt beim letzten gültigen Stand, nur die Meldung + das rote Feld zeigen den Fehler
            self._sk_felder_markieren(w)
            self.sk_ergebnis.fehler(str(fehler))
            return
        self.sk_e = e
        self.sk_gut = (w, e, v)
        self._sk_felder_markieren(None)
        self.sk_ergebnis.zeigen(zeilen, farbe)
        breite, hoehe = self.sk_groesse
        if breite > 1:
            self.sk_canvas.delete("all")
            self._sk_zeichnen(self.sk_canvas, breite, hoehe)

    def _sk_felder_markieren(self, werte):
        """Textfelder rot umranden, die sich seit dem letzten gültigen Stand geändert haben (werte=None: alle normal)."""
        if not self.sk_texte:
            return
        gut = self.sk_gut[0] if self.sk_gut else {}
        for schluessel, feld in self.sk_texte.items():
            falsch = werte is not None and werte.get(schluessel) != gut.get(schluessel)
            feld.configure(border_color=ROT if falsch else self.sk_rand)

    def _sk_zeichnen(self, c, w, h):
        self.sk_groesse = (w, h)
        self.sk_klickbereiche = []
        if self.sk_gut is None:
            return
        werte, e, v = self.sk_gut
        plan = Schaltplan(c, w, h, *self.sk_modell.sk_raster(w), pfeile=self.sk_pfeile_an)
        self.sk_modell.sk_zeichnen(plan, werte, e, v)
        self.sk_klickbereiche = plan.klickbereiche
        if plan.pfeil_anzahl and not self.sk_pfeil_schalter.winfo_ismapped():
            self.sk_pfeil_schalter.grid(row=0, column=self.sk_pfeil_spalte, sticky="w", padx=(0, 16), pady=2)

    def _sk_pfeile_umschalten(self):
        self.sk_pfeile_an = bool(self.sk_pfeil_schalter.get())
        self.sk_neu()

    # =========================================================================
    # KNÖPFE, KLICKS, ZURÜCKSETZEN
    # =========================================================================
    def _sk_anwenden(self, neue):
        if neue:
            self._sk_werte_setzen(neue)
            self.sk_neu()

    def _sk_knopf(self, aktion):
        if self.sk_gut is None:
            return
        werte, e, v = self.sk_gut
        self._sk_anwenden(self.sk_modell.sk_knopf(aktion, werte, e, v))

    def _sk_bereich(self, x, y):
        for x0, y0, x1, y1, aktion in self.sk_klickbereiche:
            if x0 <= x <= x1 and y0 <= y <= y1:
                return aktion
        return None

    def _sk_klick(self, event):
        aktion = self._sk_bereich(event.x, event.y)
        if aktion is None or self.sk_gut is None:
            return
        werte, e, v = self.sk_gut
        self._sk_anwenden(self.sk_modell.sk_klick(aktion, werte, e, v))

    def _sk_maus(self, event):
        """Hand-Zeiger über anklickbaren Bereichen."""
        hand = self._sk_bereich(event.x, event.y) is not None
        if hand != getattr(self, "sk_hand", False):
            self.sk_hand = hand
            self.sk_canvas.configure(cursor="hand2" if hand else "")

    def sk_zuruecksetzen(self):
        """↺ Zurücksetzen: Variante, Schalter, Regler (inkl. Einheit), Auswahl und Texte wie beim Öffnen."""
        m = self.sk_modell
        v = m.VARIANTEN[0] if m.VARIANTEN else None
        if self.sk_variante:
            self.sk_variante.set(v)
        for regler in self.sk_regler.values():
            regler.zuruecksetzen()
        self._sk_werte_setzen(m.startwerte(v))
        self.sk_letzte_variante = v
        self.sk_gut = None                    # Startwerte sind gültig - Markierungen entfernen
        self.sk_neu()

    def _sk_hilfetext(self):
        m = self.sk_modell
        teile = []
        if m.HILFE:
            teile.append("## So geht's\n" + m.HILFE)
        if m.KNOEPFE:
            teile.append("## Knöpfe\n- " + "  ·  ".join(t for t, _a in m.KNOEPFE) + " springen direkt zu diesem Wert")
        if any(o.get("tastatur") for *_x, o in m.TEXTFELDER):
            teile.append("## Eingabe\n- Die Tasten unter dem Feld fügen Variablen und Zeichen an der Cursor-Stelle ein")
        teile.append(ALLGEMEINE_HILFE)
        return "\n".join(teile)
