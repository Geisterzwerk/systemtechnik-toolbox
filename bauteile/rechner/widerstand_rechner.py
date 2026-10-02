# =============================================================================
# bauteile/rechner/widerstand_rechner.py
# -----------------------------------------------------------------------------
# Alle RECHNER für die Seite "Widerstand".
#
# Unten im Dictionary RECHNER steht: ID -> Funktion, die die Rechner-Karte baut.
# Die ID wird in bauteile/inhalte/01_passiv/widerstand.py unter "rechner" benutzt.
#
#   ohm_leistung        U, I, R, P - zwei eingeben, Rest wird berechnet
#   farbcode_wert       Farbringe -> Widerstandswert (4/5/6 Ringe, mit Zeichnung)
#   wert_farbcode       Widerstandswert -> Farbringe
#   smd_code            SMD-Aufdruck entschlüsseln (103, 4R7, 4701, 01C)
#   e_reihe             Nächster Normwert (E6 ... E96)
#   reihe_parallel      Reihen- und Parallelschaltung beliebig vieler Widerstände
#   spannungsteiler     inkl. Last am Ausgang und Normwert-Vorschlag
#   led_vorwiderstand   inkl. Normwert, echter Strom und Leistung
#   leitung             Leitungswiderstand und Spannungsfall
#   temperatur          Widerstand bei anderer Temperatur (Kupfer, Pt100 ...)
# =============================================================================

import math

import customtkinter as ctk

import config                                                       # -> config.py
from bauteile.rechner.basis import (Auswahl, EinheitenEingabe,      # -> rechner/basis.py
                                    FormelRechner, RechnerFehler, anzahl_gegeben, fmt)
from bauteile.rechner import normreihen                             # -> rechner/normreihen.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel          # -> core/layout.py


# =============================================================================
# 1) OHM & LEISTUNG
# =============================================================================
def _ohm_leistung(w):
    U, I, R, P = w["U"], w["I"], w["R"], w["P"]
    if anzahl_gegeben(w, "U", "I", "R", "P") != 2:
        raise RechnerFehler("Genau ZWEI Werte eingeben, die anderen zwei leer lassen.")
    if U is not None and I is not None:
        R, P = U / I, U * I
    elif U is not None and R is not None:
        I, P = U / R, U * U / R
    elif U is not None and P is not None:
        I, R = P / U, U * U / P
    elif I is not None and R is not None:
        U, P = I * R, I * I * R
    elif I is not None and P is not None:
        U, R = P / I, P / (I * I)
    else:                                   # R und P gegeben
        if P / R < 0:
            raise RechnerFehler("R und P müssen dasselbe Vorzeichen haben")
        I, U = math.sqrt(P / R), math.sqrt(P * R)
    return [f"U = {fmt(U, 'spannung')}", f"I = {fmt(I, 'strom')}",
            f"R = {fmt(R, 'widerstand')}", f"P = {fmt(P, 'leistung')}"]


def ohm_leistung(master):
    return FormelRechner(
        master, "Ohm'sches Gesetz & Leistung", "Zwei beliebige Werte eingeben, der Rest wird berechnet",
        felder=[("U", "Spannung U", "spannung"), ("I", "Strom I", "strom", {"einheit": "mA"}),
                ("R", "Widerstand R", "widerstand"), ("P", "Leistung P", "leistung")],
        berechnen=_ohm_leistung, formel="U = R · I     P = U · I = I² · R = U² / R")


# =============================================================================
# FARBCODE - Daten + Zeichnung
# =============================================================================
FARB_HEX = {"Schwarz": "#111111", "Braun": "#8B4513", "Rot": "#E02424", "Orange": "#FF8C00",
            "Gelb": "#FFD500", "Grün": "#1E9E3A", "Blau": "#1F5FD6", "Violett": "#8A2BE2",
            "Grau": "#8C8C8C", "Weiss": "#FFFFFF", "Gold": "#D4AF37", "Silber": "#C0C0C0"}
ZIFFER = {"Schwarz": 0, "Braun": 1, "Rot": 2, "Orange": 3, "Gelb": 4,
          "Grün": 5, "Blau": 6, "Violett": 7, "Grau": 8, "Weiss": 9}
MULTI = {"Silber": -2, "Gold": -1, "Schwarz": 0, "Braun": 1, "Rot": 2, "Orange": 3,
         "Gelb": 4, "Grün": 5, "Blau": 6, "Violett": 7, "Grau": 8, "Weiss": 9}      # Exponent: 10^x
TOLERANZ = {"Braun": 1, "Rot": 2, "Grün": 0.5, "Blau": 0.25, "Violett": 0.1,
            "Grau": 0.05, "Gold": 5, "Silber": 10}                                  # in %
TK = {"Braun": 100, "Rot": 50, "Orange": 15, "Gelb": 25, "Blau": 10, "Violett": 5}  # ppm/K (typ. nach IEC 60062)

# Aufbau je nach Anzahl Ringe: (Beschriftung, Tabelle)
RINGE = {
    4: [("1. Ziffer", ZIFFER), ("2. Ziffer", ZIFFER), ("Multiplikator", MULTI), ("Toleranz", TOLERANZ)],
    5: [("1. Ziffer", ZIFFER), ("2. Ziffer", ZIFFER), ("3. Ziffer", ZIFFER), ("Multiplikator", MULTI),
        ("Toleranz", TOLERANZ)],
    6: [("1. Ziffer", ZIFFER), ("2. Ziffer", ZIFFER), ("3. Ziffer", ZIFFER), ("Multiplikator", MULTI),
        ("Toleranz", TOLERANZ), ("Temperaturkoeffizient", TK)],
}


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


def _wert_text(ohm):
    return fmt(ohm, "widerstand", 5)


# =============================================================================
# 2) FARBCODE -> WERT
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
        if None in farben:
            self.fz_ergebnis.configure(text="Alle Ringe wählen …", text_color=config.FARBEN["text_leise"])
            return
        n = len(farben)
        ziffern = 2 if n == 4 else 3
        zahl = int("".join(str(ZIFFER[f]) for f in farben[:ziffern]))
        wert = zahl * 10 ** MULTI[farben[ziffern]]
        tol = TOLERANZ[farben[ziffern + 1]]
        zeilen = [f"R = {_wert_text(wert)}  ±{tol:g} %",
                  f"Bereich: {_wert_text(wert * (1 - tol / 100))} … {_wert_text(wert * (1 + tol / 100))}"]
        if n == 6:
            zeilen.append(f"TK = {TK[farben[5]]} ppm/K")
        self.fz_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])


# =============================================================================
# 3) WERT -> FARBCODE
# =============================================================================
def wert_zu_farben(wert, ringe, toleranz_farbe):
    """Gibt (farben, gerundeter_wert) zurück. ringe = 4 oder 5."""
    if wert <= 0:
        raise RechnerFehler("Wert muss grösser als 0 sein")
    ziffern = 2 if ringe == 4 else 3
    exponent = math.floor(math.log10(wert)) - (ziffern - 1)
    zahl = math.floor(wert / 10 ** exponent + 0.5)       # kaufmännisch runden (4.65 -> 4.7)
    if zahl >= 10 ** ziffern:                    # z.B. 999.6 -> 1000 -> eine Stelle weiter
        exponent += 1
        zahl = math.floor(wert / 10 ** exponent + 0.5)
    if not -2 <= exponent <= 9:
        raise RechnerFehler("Wert ausserhalb des Farbcodes (ca. 0.1 Ω … 99 GΩ)")
    multi = next(f for f, e in MULTI.items() if e == exponent)
    ziffern_farben = [next(f for f, z in ZIFFER.items() if z == int(c)) for c in str(zahl).zfill(ziffern)]
    return ziffern_farben + [multi, toleranz_farbe], zahl * 10 ** exponent


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
            farben, gerundet = wert_zu_farben(wert, ringe, tol_farbe)
            self.wf_bild.farben_setzen(farben)
            zeilen = [" – ".join(farben)]
            if not math.isclose(gerundet, wert, rel_tol=1e-9):
                zeilen.append(f"⚠ {_wert_text(wert)} ist so nicht darstellbar → {_wert_text(gerundet)}")
            reihe = "E24" if ringe == 4 else "E96"
            if not normreihen.ist_normwert(gerundet, reihe):
                zeilen.append(f"Hinweis: kein {reihe}-Normwert (nächster: "
                              f"{_wert_text(normreihen.naechste_werte(gerundet, reihe)[2])})")
            self.wf_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
        except (RechnerFehler, ValueError) as fehler:
            self.wf_ergebnis.configure(text=f"⚠ {fehler}", text_color=("#B45309", "#F59E0B"))


# =============================================================================
# 4) SMD-CODE
# =============================================================================
EIA96_MULTI = {"Z": 0.001, "Y": 0.01, "R": 0.01, "X": 0.1, "S": 0.1, "A": 1, "B": 10, "H": 10,
               "C": 100, "D": 1e3, "E": 1e4, "F": 1e5}


def smd_entschluesseln(code):
    """'103' -> (10000, 'Erklärung')"""
    c = code.strip().upper().replace(" ", "")
    if not c:
        raise RechnerFehler("Code eingeben (z.B. 103, 4R7, 4701, 01C)")
    if c in ("0", "00", "000", "0000"):
        return 0.0, "0-Ω-Brücke (Drahtbrücke als Bauteil)"
    if "R" in c and len(c) <= 4 and c.replace("R", "", 1).isdigit():
        return float(c.replace("R", ".")), "R steht für das Komma"
    if c.isdigit() and len(c) == 3:
        return int(c[:2]) * 10 ** int(c[2]), f"{c[:2]} × 10^{c[2]}  (3-stellig, meist ±5 %)"
    if c.isdigit() and len(c) == 4:
        return int(c[:3]) * 10 ** int(c[3]), f"{c[:3]} × 10^{c[3]}  (4-stellig, meist ±1 %)"
    if len(c) == 3 and c[:2].isdigit() and c[2] in EIA96_MULTI:
        index = int(c[:2])
        if not 1 <= index <= 96:
            raise RechnerFehler("EIA-96-Code muss zwischen 01 und 96 liegen")
        basis = round(normreihen.E96[index - 1] * 100)
        return basis * EIA96_MULTI[c[2]], f"EIA-96: Code {c[:2]} = {basis}, {c[2]} = ×{EIA96_MULTI[c[2]]:g}  (±1 %)"
    raise RechnerFehler(f"„{code}“ ist kein bekanntes SMD-Format")


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
            wert, erklaerung = smd_entschluesseln(self.sc_feld.get())
            self.sc_ergebnis.configure(text=f"R = {_wert_text(wert)}\n{erklaerung}",
                                       text_color=config.FARBEN["akzent"])
        except RechnerFehler as fehler:
            if not still:
                self.sc_ergebnis.configure(text=f"⚠ {fehler}", text_color=("#B45309", "#F59E0B"))
            else:
                self.sc_ergebnis.configure(text="")


# =============================================================================
# 5) E-REIHE
# =============================================================================
def _e_reihe(w):
    if w["R"] is None:
        raise RechnerFehler("Wert eingeben")
    reihe = w["reihe"].split()[0]
    unten, oben, naechster = normreihen.naechste_werte(w["R"], reihe)
    abw = (naechster - w["R"]) / w["R"] * 100
    zeilen = [f"Nächster {reihe}-Wert: {_wert_text(naechster)}  ({abw:+.2f} %)"]
    if not math.isclose(unten, oben):
        zeilen.append(f"Kleiner: {_wert_text(unten)}   Grösser: {_wert_text(oben)}")
    zeilen.append(f"Typische Toleranz {reihe}: {normreihen.TOLERANZ[reihe]}")
    return zeilen


def e_reihe(master):
    return FormelRechner(
        master, "Nächster Normwert (E-Reihe)", "Gerechneten Wert eingeben → käuflichen Wert finden",
        felder=[("R", "Wert", "widerstand", {"einheit": "kΩ"}),
                ("reihe", "Reihe", "auswahl", {"werte": ["E6 (±20 %)", "E12 (±10 %)", "E24 (±5 %)",
                                                          "E48 (±2 %)", "E96 (±1 %)"], "standard": "E24 (±5 %)"})],
        berechnen=_e_reihe, formel="Normwerte sind logarithmisch verteilt: gleicher Abstand in %")


# =============================================================================
# 6) REIHE / PARALLEL
# =============================================================================
def _reihe_parallel(w):
    werte = w["liste"]
    if not werte:
        raise RechnerFehler("Widerstände eingeben, z.B.  1k 2k2 470")
    if any(r <= 0 for r in werte):
        raise RechnerFehler("Alle Widerstände müssen grösser als 0 sein")
    r_reihe = sum(werte)
    r_parallel = 1 / sum(1 / r for r in werte)
    zeilen = [f"{len(werte)} Widerstände",
              f"Reihe:    R = {_wert_text(r_reihe)}",
              f"Parallel: R = {_wert_text(r_parallel)}"]
    ziel = w["ziel"]
    if ziel is not None:
        if ziel < r_parallel:
            zusatz = 1 / (1 / ziel - 1 / r_parallel)
            zeilen.append(f"Für {_wert_text(ziel)}: {_wert_text(zusatz)} PARALLEL dazu "
                          f"(E24: {_wert_text(normreihen.naechste_werte(zusatz, 'E24')[2])})")
        elif ziel > r_reihe:
            zusatz = ziel - r_reihe
            zeilen.append(f"Für {_wert_text(ziel)}: {_wert_text(zusatz)} in REIHE dazu "
                          f"(E24: {_wert_text(normreihen.naechste_werte(zusatz, 'E24')[2])})")
        else:
            zeilen.append("Zielwert liegt zwischen Parallel- und Reihenwert → Kombination nötig")
    return zeilen


def reihe_parallel(master):
    return FormelRechner(
        master, "Reihen- & Parallelschaltung", "Beliebig viele Werte mit Leerzeichen trennen: 1k 2k2 470",
        felder=[("liste", "Widerstände", "widerstand", {"liste": True, "platzhalter": "1k 2k2 470"}),
                ("ziel", "Zielwert (optional)", "widerstand", {"einheit": "kΩ", "platzhalter": "optional"})],
        berechnen=_reihe_parallel, formel="Reihe: R = R1 + R2 + …     Parallel: 1/R = 1/R1 + 1/R2 + …")


# =============================================================================
# 7) SPANNUNGSTEILER
# =============================================================================
def _parallel(a, b):
    return a * b / (a + b)


def _spannungsteiler(w):
    Ue, R1, R2, Ua, RL = w["Ue"], w["R1"], w["R2"], w["Ua"], w["RL"]
    if anzahl_gegeben(w, "Ue", "R1", "R2", "Ua") != 3:
        raise RechnerFehler("Genau DREI von Ue, R1, R2, Ua eingeben – eines leer lassen.")
    zeilen, berechnet = [], None
    if Ua is None:
        Ua = Ue * R2 / (R1 + R2)
        zeilen.append(f"Ua = {fmt(Ua, 'spannung')}  (unbelastet)")
    else:
        if Ue is not None and not 0 < Ua < Ue:
            raise RechnerFehler("Ua muss zwischen 0 und Ue liegen")
        if Ua <= 0:
            raise RechnerFehler("Ua muss grösser als 0 sein")
        if R1 is None:
            R1 = R2 * (Ue - Ua) / Ua
            berechnet = ("R1", R1)
        elif R2 is None:
            R2 = R1 * Ua / (Ue - Ua)
            berechnet = ("R2", R2)
        else:
            Ue = Ua * (R1 + R2) / R2
            zeilen.append(f"Ue = {fmt(Ue, 'spannung')}")
    if berechnet:
        name, wert = berechnet
        norm = normreihen.naechste_werte(wert, "E24")[2]
        r1n, r2n = (norm, R2) if name == "R1" else (R1, norm)
        zeilen.append(f"{name} = {_wert_text(wert)}")
        zeilen.append(f"  E24-Wert {_wert_text(norm)} → Ua = {fmt(Ue * r2n / (r1n + r2n), 'spannung')}")
    Iq = Ue / (R1 + R2)
    zeilen.append(f"Querstrom = {fmt(Iq, 'strom')}")
    zeilen.append(f"P(R1) = {fmt(Iq * Iq * R1, 'leistung')}   P(R2) = {fmt(Iq * Iq * R2, 'leistung')}")
    if RL is not None:
        ua_last = Ue * _parallel(R2, RL) / (R1 + _parallel(R2, RL))
        abw = (ua_last - Ue * R2 / (R1 + R2)) / (Ue * R2 / (R1 + R2)) * 100
        zeilen.append(f"Mit Last {_wert_text(RL)}: Ua = {fmt(ua_last, 'spannung')}  ({abw:+.1f} %)")
        if abs(abw) > 5:
            zeilen.append("⚠ Last zu klein: Teiler niederohmiger machen oder Puffer (OPV) verwenden")
    return zeilen


def spannungsteiler(master):
    return FormelRechner(
        master, "Spannungsteiler", "Drei Werte eingeben, einer wird berechnet. Last optional.",
        felder=[("Ue", "Eingang Ue", "spannung"), ("R1", "R1 (oben)", "widerstand", {"einheit": "kΩ"}),
                ("R2", "R2 (unten)", "widerstand", {"einheit": "kΩ"}), ("Ua", "Ausgang Ua", "spannung"),
                ("RL", "Last RL (optional)", "widerstand", {"einheit": "kΩ", "platzhalter": "optional"})],
        berechnen=_spannungsteiler, formel="Ua = Ue · R2 / (R1 + R2)")


# =============================================================================
# 8) LED-VORWIDERSTAND
# =============================================================================
def _led(w):
    Ub, Uf, If, n = w["Ub"], w["Uf"], w["If"], w["n"]
    if None in (Ub, Uf, If):
        raise RechnerFehler("Ub, Uf und If eingeben")
    n = 1 if n is None else n
    if n < 1 or n != int(n):
        raise RechnerFehler("LEDs in Reihe: ganze Zahl ab 1 eingeben")
    if Uf <= 0 or If <= 0:
        raise RechnerFehler("Uf und If müssen grösser als 0 sein")
    n = int(n)
    Ur = Ub - n * Uf
    if Ur <= 0:
        raise RechnerFehler(f"Versorgung zu klein: {n} LED(s) brauchen {fmt(n * Uf, 'spannung')}")
    R = Ur / If
    zeilen = [f"R = {_wert_text(R)}   (am Widerstand: {fmt(Ur, 'spannung')})"]
    for reihe in ("E12", "E24"):
        norm = normreihen.naechste_werte(R, reihe)[1]          # nächst GRÖSSERER Wert -> Strom sicher kleiner
        i_echt = Ur / norm
        zeilen.append(f"{reihe}: {_wert_text(norm)} → I = {fmt(i_echt, 'strom')}, P = {fmt(i_echt ** 2 * norm, 'leistung')}")
    p = If ** 2 * R
    zeilen.append(f"Belastbarkeit Widerstand: mind. {fmt(2 * p, 'leistung')} (2× Reserve)")
    if Ur / Ub < 0.2:
        zeilen.append("⚠ Wenig Spannung am Widerstand → Strom schwankt stark mit Ub und Uf")
    return zeilen


def led_vorwiderstand(master):
    return FormelRechner(
        master, "LED-Vorwiderstand", "Uf typisch: rot/gelb ≈ 2 V, grün ≈ 2–3 V, blau/weiss ≈ 3 V (Datenblatt!)",
        felder=[("Ub", "Versorgung Ub", "spannung"), ("Uf", "LED-Spannung Uf", "spannung", {"platzhalter": "z.B. 2"}),
                ("If", "LED-Strom If", "strom", {"einheit": "mA", "platzhalter": "z.B. 10"}),
                ("n", "LEDs in Reihe", "zahl", {"platzhalter": "1"})],
        berechnen=_led, formel="R = (Ub − n · Uf) / If")


# =============================================================================
# 9) LEITUNGSWIDERSTAND
# =============================================================================
# spezifischer Widerstand ρ in Ω·mm²/m bei 20 °C (typische Werte)
MATERIAL_RHO = {"Kupfer (κ = 56)": 1 / 56, "Aluminium (κ = 35)": 1 / 35,
                "Silber (κ = 62)": 1 / 62, "Messing (≈ 0.07)": 0.07, "Stahl (≈ 0.13)": 0.13}


def _leitung(w):
    if w["l"] is None or w["A"] is None:
        raise RechnerFehler("Länge und Querschnitt eingeben")
    rho = MATERIAL_RHO[w["mat"]]
    faktor = 2 if w["weg"].startswith("Hin") else 1
    laenge_m = w["l"] * faktor
    a_mm2 = w["A"] * 1e6                                # Basiseinheit m² -> mm²
    R = rho * laenge_m / a_mm2
    zeilen = [f"R = {_wert_text(R)}   (Leitungslänge total {laenge_m:g} m)"]
    if w["I"] is not None:
        du = R * w["I"]
        zeilen.append(f"Spannungsfall ΔU = {fmt(du, 'spannung')}")
        zeilen.append(f"Verlustleistung = {fmt(w['I'] ** 2 * R, 'leistung')}")
        if w["U"] is not None:
            zeilen.append(f"ΔU = {du / w['U'] * 100:.2f} % der Nennspannung")
    return zeilen


def leitung(master):
    return FormelRechner(
        master, "Leitungswiderstand & Spannungsfall", "Werte bei 20 °C. Hin- und Rückleiter nicht vergessen!",
        felder=[("l", "Länge (einfach)", "laenge"), ("A", "Querschnitt", "flaeche", {"platzhalter": "z.B. 1.5"}),
                ("mat", "Material", "auswahl", {"werte": list(MATERIAL_RHO)}),
                ("weg", "Leiter", "auswahl", {"werte": ["Hin- und Rückleiter (× 2)", "nur einfache Länge"]}),
                ("I", "Strom (optional)", "strom", {"platzhalter": "optional"}),
                ("U", "Nennspannung (optional)", "spannung", {"platzhalter": "optional"})],
        berechnen=_leitung, formel="R = ρ · l / A     ΔU = R · I")


# =============================================================================
# 10) TEMPERATUR
# =============================================================================
MATERIAL_ALPHA = {"Kupfer (α ≈ 0.0039 /K)": 0.0039, "Aluminium (α ≈ 0.0040 /K)": 0.0040,
                  "Platin / Pt100 (α = 0.00385 /K)": 0.00385, "Nickel (α ≈ 0.0062 /K)": 0.0062,
                  "Konstantan (α ≈ 0)": 0.00001}


def _temperatur(w):
    if w["R"] is None or w["T"] is None:
        raise RechnerFehler("R bei Bezugstemperatur und neue Temperatur eingeben")
    t_ref = 20.0 if w["Tref"] is None else w["Tref"]
    alpha = MATERIAL_ALPHA[w["mat"]]
    R_T = w["R"] * (1 + alpha * (w["T"] - t_ref))
    return [f"R({w['T']:g} °C) = {_wert_text(R_T)}",
            f"Änderung: {(R_T / w['R'] - 1) * 100:+.2f} %  (ΔT = {w['T'] - t_ref:+g} K)"]


def temperatur(master):
    return FormelRechner(
        master, "Widerstand bei anderer Temperatur", "Linear genähert – gut für ca. −50 … +150 °C. Pt100: Bezug 0 °C!",
        felder=[("R", "R bei Bezugstemp.", "widerstand"), ("Tref", "Bezugstemperatur", "temperatur", {"platzhalter": "20"}),
                ("T", "Neue Temperatur", "temperatur"), ("mat", "Material", "auswahl", {"werte": list(MATERIAL_ALPHA)})],
        berechnen=_temperatur, formel="R(T) = R_ref · (1 + α · (T − T_ref))")


# =============================================================================
# REGISTRIERUNG: ID -> Funktion/Klasse, die die Karte baut
# =============================================================================
RECHNER = {
    "ohm_leistung": ohm_leistung,
    "farbcode_wert": FarbcodeZuWert,
    "wert_farbcode": WertZuFarbcode,
    "smd_code": SmdCode,
    "e_reihe": e_reihe,
    "reihe_parallel": reihe_parallel,
    "spannungsteiler": spannungsteiler,
    "led_vorwiderstand": led_vorwiderstand,
    "leitung": leitung,
    "temperatur": temperatur,
}
