# =============================================================================
# bauteile/grafiken/farbcode_karten.py
# -----------------------------------------------------------------------------
# KARTEN MIT ZEICHNUNG für die Seite "Widerstand" (Fenster-Teil, customtkinter).
# Gerechnet wird in bauteile/rechner/widerstand_rechner.py (ohne Fenster, auch fürs Web).
#
#   widerstand_zeichnen()  Widerstand mit Farbringen auf ein Canvas zeichnen
#   FarbcodeZuWert         Ringe wählen -> Wert       (rechnet mit farben_zu_wert)
#   WertZuFarbcode         Wert eingeben -> Ringe     (rechnet mit farbcode_zeilen)
#   SmdCode                SMD-Aufdruck entschlüsseln (rechnet mit smd_zeilen)
#
# WER RUFT DAS AUF?  bauteile/rechner/widerstand_rechner.py (RECHNER, als GrafikVerweis)
# =============================================================================

import customtkinter as ctk

import config                                                       # -> config.py
from bauteile.rechner.basis import Auswahl, EinheitenEingabe        # -> rechner/basis.py
from bauteile.rechner.kern import RechnerFehler                     # -> rechner/kern.py
from bauteile.rechner.widerstand_rechner import (FARB_HEX, RINGE,   # -> rechner/widerstand_rechner.py
                                                 TOLERANZ, farbcode_zeilen, farben_zu_wert, smd_zeilen)
from core.layout import Karte, ResponsiveCanvas, WrapLabel          # -> core/layout.py

WARN_FARBE = ("#B45309", "#F59E0B")


def widerstand_zeichnen(c, w, h, farben):
    """Zeichnet einen Widerstand mit Farbringen. farben = Liste (None = noch nicht gewählt)."""
    mitte = h / 2
    c.create_line(0.03 * w, mitte, 0.97 * w, mitte, fill="#9AA1AD", width=max(2, h / 40))      # Anschlussdrähte
    x1, x2, y1, y2 = 0.2 * w, 0.8 * w, 0.22 * h, 0.78 * h
    koerper = "#E8D3A8"                                                                       # typische Farbe (beige)
    c.create_oval(x1 - 0.03 * w, y1 - 0.04 * h, x1 + 0.07 * w, y2 + 0.04 * h, fill=koerper, outline="")
    c.create_oval(x2 - 0.07 * w, y1 - 0.04 * h, x2 + 0.03 * w, y2 + 0.04 * h, fill=koerper, outline="")
    c.create_rectangle(x1 + 0.02 * w, y1, x2 - 0.02 * w, y2, fill=koerper, outline="")

    n = len(farben)
    breite = 0.035 * w
    # Ziffern + Multiplikator links gruppiert, Toleranz (und TK) rechts mit Abstand
    links = n - (2 if n == 6 else 1)
    positionen = [0.27 * w + i * 0.085 * w for i in range(links)]
    positionen += [0.70 * w] if n != 6 else [0.66 * w, 0.73 * w]
    for x, farbe in zip(positionen, farben):
        if farbe:
            c.create_rectangle(x - breite / 2, y1 - 0.02 * h, x + breite / 2, y2 + 0.02 * h,
                               fill=FARB_HEX[farbe], outline="#555555" if farbe in ("Weiss", "Gelb", "Silber") else "")
        else:
            c.create_rectangle(x - breite / 2, y1, x + breite / 2, y2, outline="#777777", dash=(3, 3))
    c.create_text(0.5 * w, 0.93 * h, text="Lesen von links nach rechts →   (Toleranzring rechts)",
                  fill="#9AA1AD", font=(config.SCHRIFT, max(8, int(h / 14))))


class _FarbCanvas(ResponsiveCanvas):
    """Canvas, der sich die aktuellen Farben merkt und neu zeichnen kann."""

    def __init__(self, master):
        self.fc_farben = [None] * 4
        super().__init__(master, lambda c, w, h: widerstand_zeichnen(c, w, h, self.fc_farben),
                         seitenverhaeltnis=0.3, max_hoehe=170)

    def farben_setzen(self, farben):
        self.fc_farben = list(farben)
        breite, hoehe = self.winfo_width(), self.winfo_height()
        if breite > 1:
            self.delete("all")
            widerstand_zeichnen(self, breite, hoehe, self.fc_farben)


# =============================================================================
# FARBCODE -> WERT
# =============================================================================
class FarbcodeZuWert(Karte):
    def __init__(self, master):
        super().__init__(master, titel="Farbcode → Wert", untertitel="Ringe von links nach rechts wählen")
        b = self.body
        self.fz_anzahl = ctk.CTkSegmentedButton(b, values=["4 Ringe", "5 Ringe", "6 Ringe"],
                                                command=lambda _v: self._fz_aufbauen())
        self.fz_anzahl.set("4 Ringe")
        self.fz_anzahl.grid(row=0, column=0, sticky="w")
        self.fz_bild = _FarbCanvas(b)
        self.fz_bild.grid(row=1, column=0, sticky="ew", pady=8)
        self.fz_rahmen = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        self.fz_rahmen.grid(row=2, column=0, sticky="ew")
        self.fz_ergebnis = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"),
                                     text_color=config.FARBEN["akzent"])
        self.fz_ergebnis.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        self.fz_menues = []
        self._fz_aufbauen()

    def _fz_aufbauen(self):
        for kind in self.fz_rahmen.winfo_children():
            kind.destroy()
        n = int(self.fz_anzahl.get()[0])
        self.fz_menues = []
        for zeile, (name, tabelle) in enumerate(RINGE[n]):
            ctk.CTkLabel(self.fz_rahmen, text=f"Ring {zeile + 1}: {name}", anchor="w").grid(
                row=zeile, column=0, sticky="w", padx=(0, 12), pady=2)
            menue = ctk.CTkOptionMenu(self.fz_rahmen, values=list(tabelle.keys()), width=140,
                                      dynamic_resizing=False, command=lambda _v: self._fz_rechnen())
            menue.set("wählen")
            menue.grid(row=zeile, column=1, sticky="w", pady=2)
            self.fz_menues.append((menue, tabelle))
        self._fz_rechnen()

    def _fz_rechnen(self):
        farben = [m.get() if m.get() in t else None for m, t in self.fz_menues]
        self.fz_bild.farben_setzen(farben)
        try:
            zeilen = farben_zu_wert(farben)                  # -> widerstand_rechner.py
        except RechnerFehler as fehler:                      # z.B. "Alle Ringe wählen …"
            self.fz_ergebnis.configure(text=str(fehler), text_color=config.FARBEN["text_leise"])
            return
        self.fz_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])


# =============================================================================
# WERT -> FARBCODE
# =============================================================================
class WertZuFarbcode(Karte):
    def __init__(self, master):
        super().__init__(master, titel="Wert → Farbcode", untertitel="Welche Ringe hat mein Widerstand?")
        b = self.body
        zeile = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        zeile.grid(row=0, column=0, sticky="w")
        self.wf_wert = EinheitenEingabe(zeile, "widerstand", "z.B. 4k7", "kΩ")
        self.wf_wert.grid(row=0, column=0, sticky="w")
        self.wf_wert.bei_enter(self._wf_rechnen)
        self.wf_ringe = ctk.CTkSegmentedButton(b, values=["4 Ringe", "5 Ringe"], command=lambda _v: self._wf_rechnen())
        self.wf_ringe.set("4 Ringe")
        self.wf_ringe.grid(row=1, column=0, sticky="w", pady=(6, 0))
        tol_zeile = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        tol_zeile.grid(row=2, column=0, sticky="w", pady=(6, 0))
        ctk.CTkLabel(tol_zeile, text="Toleranz", anchor="w").grid(row=0, column=0, padx=(0, 12))
        self.wf_tol = Auswahl(tol_zeile, [f"±{v:g} % ({f})" for f, v in TOLERANZ.items()],
                              standard="±5 % (Gold)", breite=150, bei_aenderung=self._wf_rechnen)
        self.wf_tol.grid(row=0, column=1)
        ctk.CTkButton(b, text="Farben anzeigen", width=140, command=self._wf_rechnen).grid(
            row=3, column=0, sticky="w", pady=(10, 0))
        self.wf_bild = _FarbCanvas(b)
        self.wf_bild.grid(row=4, column=0, sticky="ew", pady=8)
        self.wf_ergebnis = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"),
                                     text_color=config.FARBEN["akzent"])
        self.wf_ergebnis.grid(row=5, column=0, sticky="ew")

    def _wf_rechnen(self):
        try:
            wert = self.wf_wert.wert()
            if wert is None:
                return
            ringe = int(self.wf_ringe.get()[0])
            tol_farbe = self.wf_tol.wert().split("(")[1].rstrip(")")
            farben, zeilen = farbcode_zeilen(wert, ringe, tol_farbe)      # -> widerstand_rechner.py
            self.wf_bild.farben_setzen(farben)
            self.wf_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
        except (RechnerFehler, ValueError) as fehler:
            self.wf_ergebnis.configure(text=f"⚠ {fehler}", text_color=WARN_FARBE)


# =============================================================================
# SMD-CODE
# =============================================================================
class SmdCode(Karte):
    def __init__(self, master):
        super().__init__(master, titel="SMD-Code entschlüsseln", untertitel="Aufdruck auf dem Bauteil eingeben")
        b = self.body
        self.sc_feld = ctk.CTkEntry(b, placeholder_text="z.B. 103, 4R7, 4701, 01C", width=220)
        self.sc_feld.grid(row=0, column=0, sticky="w")
        self.sc_feld.bind("<Return>", lambda e: self._sc_rechnen())
        self.sc_feld.bind("<KeyRelease>", lambda e: self._sc_rechnen(still=True))
        ctk.CTkButton(b, text="Entschlüsseln", width=120, command=self._sc_rechnen).grid(
            row=1, column=0, sticky="w", pady=(10, 6))
        self.sc_ergebnis = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"),
                                     text_color=config.FARBEN["akzent"])
        self.sc_ergebnis.grid(row=2, column=0, sticky="ew")

    def _sc_rechnen(self, still=False):
        try:
            zeilen = smd_zeilen(self.sc_feld.get())                     # -> widerstand_rechner.py
            self.sc_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
        except RechnerFehler as fehler:
            if not still:
                self.sc_ergebnis.configure(text=f"⚠ {fehler}", text_color=WARN_FARBE)
            else:
                self.sc_ergebnis.configure(text="")
