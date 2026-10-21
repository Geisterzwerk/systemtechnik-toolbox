# =============================================================================
# bauteile/grafiken/schaltung_karte.py
# -----------------------------------------------------------------------------
# FENSTER-KARTE um ein SchaltungsModell (customtkinter):
#   [Variante] [Schalter]
#   Schaltplan mit Werten (tk.Canvas)
#   Regler (Slider + Zahlenfeld + Einheit)
#   Ergebnis + Erklärung
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
#
# WER RUFT DAS AUF?  SchaltungsModell.karte_bauen() (bauteile/grafiken/schaltplan.py),
#                    das wiederum GrafikVerweis aus bauteile/rechner/kern.py beim Öffnen aufruft
# =============================================================================

import customtkinter as ctk

import config                                                            # -> config.py
from bauteile.grafiken.schaltplan import WARN, Schaltplan, text_eingabe  # -> grafiken/schaltplan.py
from bauteile.rechner.basis import Auswahl, WertRegler                   # -> rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel               # -> core/layout.py


class SchaltungsKarte(Karte):
    """Eigene Attribute beginnen mit sk_ (keine Kollision mit tkinter)."""

    def __init__(self, master, modell):
        self.sk_modell = m = modell
        super().__init__(master, titel=m.TITEL, untertitel=m.UNTERTITEL)
        b = self.body
        zeile = 0
        self.sk_variante = None
        self.sk_schalter = {}
        if m.VARIANTEN or m.SCHALTER:
            oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
            oben.grid(row=zeile, column=0, sticky="w", pady=(0, 6))
            zeile += 1
            spalte = 0
            if m.VARIANTEN:
                self.sk_variante = ctk.CTkSegmentedButton(oben, values=m.VARIANTEN,
                                                          command=lambda _v: self.sk_neu())
                self.sk_variante.set(m.VARIANTEN[0])
                self.sk_variante.grid(row=0, column=0, sticky="w", padx=(0, 16), pady=2)
                spalte = 1
            for schluessel, text in m.SCHALTER:
                schalter = ctk.CTkSwitch(oben, text=text, command=self.sk_neu)
                schalter.grid(row=0, column=spalte, sticky="w", padx=(0, 16), pady=2)
                self.sk_schalter[schluessel] = schalter
                spalte += 1
        self.sk_auswahl, self.sk_texte = {}, {}
        if m.AUSWAHL or m.TEXTFELDER:
            eingaben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
            eingaben.grid(row=zeile, column=0, sticky="w", pady=(0, 6))
            zeile += 1
            for i, (schluessel, text, optionen, start) in enumerate(m.AUSWAHL):
                ctk.CTkLabel(eingaben, text=text, anchor="w").grid(row=i, column=0, sticky="w", padx=(0, 8), pady=2)
                feld = Auswahl(eingaben, optionen, start, breite=240, bei_aenderung=self.sk_neu)
                feld.grid(row=i, column=1, sticky="w", pady=2)
                self.sk_auswahl[schluessel] = feld
            for i, (schluessel, text, start, opt) in enumerate(m.TEXTFELDER, start=len(m.AUSWAHL)):
                ctk.CTkLabel(eingaben, text=text, anchor="w").grid(row=i, column=0, sticky="w", padx=(0, 8), pady=2)
                feld = ctk.CTkEntry(eingaben, width=240, font=(config.SCHRIFT_CODE, 14),
                                    placeholder_text=opt.get("platzhalter", ""))
                feld.insert(0, start)
                feld.bind("<Return>", lambda _e: self.sk_neu())
                feld.bind("<FocusOut>", lambda _e: self.sk_neu(), add="+")
                feld.grid(row=i, column=1, sticky="w", pady=2)
                self.sk_texte[schluessel] = feld
        self.sk_canvas = ResponsiveCanvas(b, self._sk_zeichnen, seitenverhaeltnis=m.SEITENVERHAELTNIS,
                                          max_hoehe=m.MAX_HOEHE)
        self.sk_canvas.grid(row=zeile, column=0, sticky="ew")
        zeile += 1
        self.sk_regler = {}
        for schluessel, text, typ, von, bis, start, *opt in m.REGLER:
            regler = WertRegler(b, text, typ, von, bis, start, bei_aenderung=self.sk_neu, text_breite=150,
                                **(opt[0] if opt else {}))
            regler.grid(row=zeile, column=0, sticky="ew", pady=(4, 0))
            self.sk_regler[schluessel] = regler
            zeile += 1
        self.sk_ergebnis = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"), text_color=config.FARBEN["akzent"])
        self.sk_ergebnis.grid(row=zeile, column=0, sticky="ew", pady=(8, 0))
        WrapLabel(b, text=m.ERKLAERUNG, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"]).grid(
            row=zeile + 1, column=0, sticky="ew", pady=(8, 0))
        self.sk_groesse = (0, 0)
        self.sk_e = None
        self.sk_neu()

    def _sk_werte(self):
        """Alle Reglerwerte und Schalterstellungen: {"ue": 12.0, "taster": False, ...}"""
        werte = {k: r.wert() for k, r in self.sk_regler.items()}
        werte.update({k: bool(s.get()) for k, s in self.sk_schalter.items()})
        werte.update({k: a.wert() for k, a in self.sk_auswahl.items()})
        laenge = {f[0]: f[3].get("max", 40) for f in self.sk_modell.TEXTFELDER}
        werte.update({k: text_eingabe(f.get(), laenge[k]) for k, f in self.sk_texte.items()})
        return werte

    def sk_v(self):
        return self.sk_variante.get() if self.sk_variante else None

    def sk_neu(self):
        """Nach jeder Änderung: neu rechnen, Text setzen, Plan neu zeichnen."""
        v = self.sk_v()
        if v != getattr(self, "sk_letzte_variante", v):                   # Variante gewechselt -> Startwerte
            for schluessel, wert in self.sk_modell.STARTWERTE.get(v, {}).items():
                if schluessel in self.sk_regler:
                    self.sk_regler[schluessel].setzen(wert)
                elif schluessel in self.sk_auswahl:
                    self.sk_auswahl[schluessel].set(wert)
                elif schluessel in self.sk_texte:
                    self.sk_texte[schluessel].delete(0, "end")
                    self.sk_texte[schluessel].insert(0, wert)
        self.sk_letzte_variante = v
        w = self._sk_werte()
        try:
            self.sk_e = self.sk_modell.sk_rechnen(w, v)
            zeilen, farbe = self.sk_modell.sk_info(w, self.sk_e, v)
            self.sk_ergebnis.configure(text="\n".join(zeilen), text_color=farbe)
        except ValueError as fehler:
            self.sk_e = None
            self.sk_ergebnis.configure(text=f"⚠ {fehler}", text_color=WARN)
        breite, hoehe = self.sk_groesse
        if breite > 1:
            self.sk_canvas.delete("all")
            self._sk_zeichnen(self.sk_canvas, breite, hoehe)

    def _sk_zeichnen(self, c, w, h):
        self.sk_groesse = (w, h)
        if self.sk_e is None:
            return
        plan = Schaltplan(c, w, h, *self.sk_modell.sk_raster(w))
        self.sk_modell.sk_zeichnen(plan, self._sk_werte(), self.sk_e, self.sk_v())
