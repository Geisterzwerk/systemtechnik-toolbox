# =============================================================================
# bauteile/grafiken/schalter_simulator.py
# -----------------------------------------------------------------------------
# ZWEI GETRENNTE SIMULATOREN "Transistor als Schalter":
#
#   BjtSchalter      Bipolartransistor   NPN (Low-Side)  |  PNP (High-Side)   -> stromgesteuert
#   MosfetSchalter   MOSFET              N-Kanal (Low)   |  P-Kanal (High)    -> spannungsgesteuert
#
#   Low-Side (NPN / N-Kanal)          High-Side (PNP / P-Kanal)
#      +U_B ────┬────                    +U_B ────┬────
#              (💡) Last                       [T]  E / S
#               │                               │
#   U_St ─[R]─ [T]  C / D             U_St ─[R]─┘   C / D
#               │                              (💡) Last
#      GND ─────┴────                    GND ─────┴────
#
# Gemeinsam ist nur der ZEICHEN-Unterbau (Schienen, Lampe, Wärmebalken, Regler).
# Die Rechnung steckt getrennt in:
#   bauteile/rechner/transistor_mathe.py  schalter()   (NPN/PNP)
#   bauteile/rechner/mosfet_mathe.py      schalter()   (N-/P-Kanal), gate_umladen()
#
# Die wichtigsten Werte stehen DIREKT in der Zeichnung (I, U_CE/U_DS, I_B/U_GS),
# darunter die Erklärung, was die Grafik physikalisch zeigt.
# Eigene Namen beginnen mit sb_ (keine Kollision mit tkinter).
#
# WER RUFT DAS AUF?  bauteile/rechner/halbleiter_rechner.py
#                    "transistor_simulator" -> BjtSchalter,  "mosfet_simulator" -> MosfetSchalter
# =============================================================================

import customtkinter as ctk

import config                                                            # -> config.py
from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.halbleiter_grafiken import (BLAU, GRAU, GRUEN,    # -> grafiken/halbleiter_grafiken.py
                                                   ORANGE, ROT, _farbe, _mischen)
from bauteile.rechner import mosfet_mathe as mm                          # -> rechner/mosfet_mathe.py
from bauteile.rechner import transistor_mathe as tm                      # -> rechner/transistor_mathe.py
from bauteile.rechner.basis import EinheitenEingabe, WertRegler          # -> rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel               # -> core/layout.py

WARN = ("#B45309", ORANGE)
FEHLER = ("#B91C1C", ROT)


# =============================================================================
# GEMEINSAMER UNTERBAU
# =============================================================================
class _SchalterBasis(Karte):
    """
    Unterklassen liefern:
      TYPEN                 Werte des Umschalters, z.B. ["NPN (Low-Side)", "PNP (High-Side)"]
      PARAMETER             [(name, text, einheiten_typ, einheit, startwert), ...]
      STEUER_TEXT           Beschriftung des Reglers
      STEUER_MAX            Regelbereich mindestens 0 … STEUER_MAX (bzw. bis U_B, falls grösser)
      ERKLAERUNG            Text unter der Grafik: was zeigt sie physikalisch?
      _sb_rechnen(p, u_st)  -> dict mit Ergebnis (zustand "aus" | "teil" | "voll", i, u_t, p_t, ...)
      _sb_info(e)           -> (zeilen, farbe)
      _sb_bauteil(c, ...)   -> zeichnet Transistor und Ansteuerung
    """

    def __init__(self, master, titel, untertitel):
        super().__init__(master, titel=titel, untertitel=untertitel)
        b = self.body
        self.sb_groesse = (0, 0)
        self.sb_e = None                  # letztes Rechenergebnis
        self.sb_p = None                  # letzte gültige Parameter

        self.sb_typ = ctk.CTkSegmentedButton(b, values=self.TYPEN, command=lambda _v: self._sb_typ_geaendert())
        self.sb_typ.set(self.TYPEN[0])
        self.sb_typ.grid(row=0, column=0, sticky="w")

        # ---- Parameter (Enter = übernehmen) ----
        rahmen = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        rahmen.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.sb_felder = {}
        for i, (name, text, typ, einheit, start) in enumerate(self.PARAMETER):
            zeile, spalte = divmod(i, 2)
            ctk.CTkLabel(rahmen, text=text, anchor="w").grid(row=zeile, column=spalte * 2, sticky="w",
                                                             padx=(0 if spalte == 0 else 18, 6), pady=2)
            feld = EinheitenEingabe(rahmen, typ, "", einheit, breite=70)
            feld.ee_feld.insert(0, start)
            feld.grid(row=zeile, column=spalte * 2 + 1, sticky="w", pady=2)
            feld.bei_enter(self.sb_neu)
            self.sb_felder[name] = feld

        # ---- Zeichnung ----
        self.sb_canvas = ResponsiveCanvas(b, self._sb_zeichnen, seitenverhaeltnis=0.58, max_hoehe=430)
        self.sb_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        # ---- Regler Ansteuerspannung (Slider + Zahlenfeld) ----
        self.sb_regler = WertRegler(b, self.STEUER_TEXT, "spannung", 0, 12, 0, einheit="V", grenzen=(0, 60),
                                    schritte=240, bei_aenderung=self.sb_neu, text_breite=170)
        self.sb_regler.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        self.sb_info = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"),
                                 text_color=config.FARBEN["akzent"])
        self.sb_info.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        WrapLabel(b, text=self.ERKLAERUNG, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"]).grid(
            row=5, column=0, sticky="ew", pady=(8, 0))
        self._sb_typ_geaendert()

    # ---- Bedienung -----------------------------------------------------------
    def _sb_high_side(self):
        return self.sb_typ.get() == self.TYPEN[1]

    def _sb_parameter(self):
        werte = {}
        for name, feld in self.sb_felder.items():
            wert = feld.wert()                       # ValueError bei Unsinn -> wird in sb_neu gemeldet
            if wert is None or wert <= 0:
                raise ValueError(f"{dict((n, t) for n, t, *_ in self.PARAMETER)[name]} muss grösser als 0 sein")
            werte[name] = wert
        return werte

    def _sb_typ_geaendert(self):
        """Neuer Typ -> Regler auf AUS stellen (Low-Side: 0 V, High-Side: U_B)."""
        try:
            p = self._sb_parameter()
        except ValueError:
            p = None
        ub = p["ub"] if p else 12.0
        self.sb_regler.bereich_setzen(0, max(ub, self.STEUER_MAX), ub if self._sb_high_side() else 0.0)
        self.sb_neu()

    def sb_neu(self):
        try:
            self.sb_p = self._sb_parameter()
            ub = self.sb_p["ub"]
            if self.sb_regler.wr_bis < ub:                       # High-Side braucht den Bereich bis U_B
                self.sb_regler.bereich_setzen(0, max(ub, self.STEUER_MAX))
            self.sb_e = self._sb_rechnen(self.sb_p, self.sb_regler.wert())
        except ValueError as fehler:
            self.sb_e = None
            self.sb_info.configure(text=f"⚠ {fehler}", text_color=WARN)
            self.sb_canvas.delete("all")
            return
        zeilen, farbe = self._sb_info(self.sb_e)
        self.sb_info.configure(text="\n".join(zeilen), text_color=farbe)
        w, h = self.sb_groesse
        if w > 1:
            self.sb_canvas.delete("all")
            self._sb_zeichnen(self.sb_canvas, w, h)

    # ---- Zeichnen ------------------------------------------------------------
    def _sb_zeichnen(self, c, w, h):
        self.sb_groesse = (w, h)
        e = self.sb_e
        if e is None:
            return
        text = _farbe(config.FARBEN["text"])
        leise = _farbe(config.FARBEN["text_leise"])
        bg = _farbe(config.FARBEN["flaeche"])
        schrift = (config.SCHRIFT, max(8, int(h / 28)))
        fett = (config.SCHRIFT, max(9, int(h / 24)), "bold")
        dick = max(2, int(h / 120))
        zustand_farbe = {"aus": GRAU, "teil": ORANGE, "voll": GRUEN}[e["zustand"]]
        anteil_strom = min(1.0, e["i"] / e["i_max"]) if e["i_max"] > 0 else 0.0
        strom_farbe = _mischen(leise, GRUEN, anteil_strom)

        xs = 0.56 * w                                   # senkrechte Hauptleitung
        y_ub, y_gnd = 0.08 * h, 0.92 * h
        high = self._sb_high_side()
        y_t, y_l = (0.36 * h, 0.70 * h) if high else (0.66 * h, 0.32 * h)
        r_t = 0.10 * h                                  # Grösse Transistor
        r_l = min(0.075 * h, 0.06 * w)                  # Radius Lampe

        # ---- Schienen ----
        c.create_line(xs - 0.10 * w, y_ub, xs + 0.10 * w, y_ub, fill=ROT, width=dick + 1)
        c.create_text(xs + 0.11 * w, y_ub, anchor="w", text=f"+U_B = {fmt(e['ub'], 'spannung', 3)}", fill=ROT, font=schrift)
        c.create_line(xs - 0.07 * w, y_gnd, xs + 0.07 * w, y_gnd, fill=text, width=dick + 1)
        c.create_line(xs - 0.04 * w, y_gnd + 0.025 * h, xs + 0.04 * w, y_gnd + 0.025 * h, fill=text, width=dick)
        c.create_text(xs + 0.08 * w, y_gnd, anchor="w", text="GND", fill=leise, font=schrift)

        # ---- Leitungen (Farbe = Stromstärke) ----
        punkte = sorted([y_ub, y_gnd, y_t - r_t, y_t + r_t, y_l - r_l, y_l + r_l])
        for y0, y1 in zip(punkte[0::2], punkte[1::2]):
            c.create_line(xs, y0, xs, y1, fill=strom_farbe, width=dick)

        # ---- Lampe: Helligkeit ~ Leistung ----
        hell = (e["u_last"] * e["i"]) / (e["ub"] * e["i_max"]) if e["i_max"] > 0 else 0.0
        if hell > 0.03:
            glanz = r_l * (1.2 + 0.6 * hell)
            c.create_oval(xs - glanz, y_l - glanz, xs + glanz, y_l + glanz, outline="",
                          fill=_mischen(bg, "#FFD54A", 0.35 * hell))
        c.create_oval(xs - r_l, y_l - r_l, xs + r_l, y_l + r_l, width=dick, outline=text,
                      fill=_mischen(bg, "#FFE066", hell))
        k = r_l * 0.6
        c.create_line(xs - k, y_l - k, xs + k, y_l + k, fill=text, width=dick)
        c.create_line(xs - k, y_l + k, xs + k, y_l - k, fill=text, width=dick)
        x_text = xs + 1.9 * r_l                         # ausserhalb des grössten Scheins
        c.create_text(x_text, y_l - 0.035 * h, anchor="w", fill=leise, font=schrift,
                      text=f"Last {fmt(e['rl'], 'widerstand', 3)}")
        c.create_text(x_text, y_l + 0.035 * h, anchor="w", fill=text, font=schrift,
                      text=f"I = {fmt(e['i'], 'strom', 3)}")

        # ---- Transistor + Ansteuerung (Unterklasse) ----
        self._sb_bauteil(c, w, h, e, xs, y_t, r_t, high, zustand_farbe, text, leise, bg, schrift, fett, dick)

        # ---- Zustand oben links ----
        c.create_text(0.03 * w, 0.06 * h, anchor="w", fill=zustand_farbe, font=fett,
                      text={"aus": "AUS – sperrt", "teil": "HALB OFFEN – heizt!", "voll": "EIN – voll durchgeschaltet"}[e["zustand"]])
        c.create_text(0.03 * w, 0.12 * h, anchor="w", fill=leise, font=schrift,
                      text="High-Side (Schalter an +U_B)" if high else "Low-Side (Schalter an GND)")

        # ---- Balken: Verlustleistung im Transistor ----
        # Low-Side: unten rechts frei · High-Side: unten links frei (Ansteuerung sitzt oben)
        bx0, bx1, by = (0.04 * w, 0.30 * w, 0.84 * h) if high else (0.72 * w, 0.96 * w, 0.84 * h)
        p_ref = max(e["ub"] * e["i_max"] / 4, 1e-9)    # grösster möglicher Verlust: bei halbem Strom
        anteil = min(1.0, e["p_t"] / p_ref)
        c.create_text(bx0 if high else bx1, by - 0.05 * h, anchor="w" if high else "e",
                      text=f"Wärme im Transistor: {fmt(e['p_t'], 'leistung', 3)}",
                      fill=leise, font=schrift)
        c.create_rectangle(bx0, by - 0.02 * h, bx1, by + 0.02 * h, outline=leise)
        if anteil > 0.005:
            c.create_rectangle(bx0, by - 0.02 * h, bx0 + (bx1 - bx0) * anteil, by + 0.02 * h, outline="",
                               fill=_mischen(GRUEN, ROT, anteil))

    @staticmethod
    def _sb_steuerleitung(c, w, h, y, x_ende, u_st, r_text, schrift, fett, dick, bg, mit_widerstand=True):
        """Ansteuerung links: Punkt U_St, Widerstand, Leitung bis x_ende."""
        x_ein = 0.06 * w
        c.create_line(x_ein, y, x_ende, y, fill=BLAU, width=dick)
        c.create_oval(x_ein - 5, y - 5, x_ein + 5, y + 5, fill=BLAU, outline="")
        c.create_text(x_ein, y - 0.06 * h, anchor="w", text=f"U_St = {fmt(u_st, 'spannung', 3)}", fill=BLAU, font=fett)
        if mit_widerstand:
            rx0, rx1 = 0.17 * w, 0.27 * w
            c.create_rectangle(rx0, y - 0.03 * h, rx1, y + 0.03 * h, fill=bg, outline=BLAU, width=dick)
            c.create_text((rx0 + rx1) / 2, y + 0.065 * h, text=r_text, fill=BLAU, font=schrift)


# =============================================================================
# BIPOLARTRANSISTOR (NPN / PNP)
# =============================================================================
class BjtSchalter(_SchalterBasis):

    TYPEN = ["NPN (Low-Side)", "PNP (High-Side)"]
    PARAMETER = [("ub", "U_B", "spannung", "V", "12"), ("rl", "Last R_L", "widerstand", "Ω", "120"),
                 ("rb", "R_B", "widerstand", "kΩ", "1"), ("b", "B min (β)", "zahl", None, "100")]
    STEUER_TEXT = "Steuerspannung U_St"
    STEUER_MAX = 12.0
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der Bipolartransistor ist STROMGESTEUERT: Der Basisstrom I_B bestimmt, wie viel "
        "Kollektorstrom höchstens fliessen darf (I_C = B · I_B). Erst wenn I_B grösser ist als I_C,max / B "
        "(Übersteuerungsfaktor ü ≥ 1, als Schalter ü = 2 … 5), ist der Transistor gesättigt: U_CE ≈ 0.2 V, wenig "
        "Wärme, die Lampe leuchtet voll. Dazwischen arbeitet er als Verstärker und setzt viel Leistung in Wärme um. "
        "NPN schaltet auf der Low-Side (Emitter an GND, einschalten mit HIGH). PNP schaltet auf der High-Side "
        "(Emitter an +U_B): eingeschaltet wird mit LOW, und zum Ausschalten muss die Basis fast auf +U_B.")

    def __init__(self, master):
        super().__init__(master, "🔌 Bipolartransistor als Schalter (interaktiv)",
                         "NPN oder PNP wählen, Steuerspannung verändern – wann ist er wirklich gesättigt?")

    def _sb_rechnen(self, p, u_st):
        typ = "PNP" if self._sb_high_side() else "NPN"
        a = tm.schalter(typ, p["ub"], p["rl"], u_st, p["rb"], p["b"])          # -> transistor_mathe.py
        zustand = {"gesperrt": "aus", "aktiv": "teil", "gesättigt": "voll"}[a["zustand"]]
        return dict(a, zustand=zustand, i=a["i_c"], u_t=a["u_ce"], i_max=a["i_c_max"], ub=p["ub"], rl=p["rl"],
                    u_st=u_st, b=p["b"])

    def _sb_info(self, e):
        high = e["typ"] == "PNP"
        zeilen = []
        if e["zustand"] == "aus":
            zeilen.append("AUS: " + ("Basis liegt höher als U_B − 0.7 V → kein Basisstrom" if high
                                     else "U_St < 0.7 V → Basis-Emitter-Diode sperrt, kein Basisstrom"))
        else:
            zeilen.append(f"I_B = {fmt(e['i_b'], 'strom')}   ·   nötig für Sättigung: I_C,max / B = "
                          f"{fmt(e['i_b_noetig'], 'strom')}   →   Übersteuerung ü = {e['ue']:.2f}")
            zeilen.append(f"I_C = {fmt(e['i_c'], 'strom')}   ·   U_CE = {fmt(e['u_ce'], 'spannung')}   ·   "
                          f"P_T = {fmt(e['p_t'], 'leistung')}")
            if e["ue"] < 1:
                zeilen.append("⚠ Basisstrom reicht NICHT für Sättigung → Transistor nur halb offen und wird heiss. "
                              + ("U_St weiter senken oder R_B verkleinern" if high else "U_St erhöhen oder R_B verkleinern"))
            elif e["ue"] < 2:
                zeilen.append("⚠ Knapp gesättigt (ü < 2): B streut und sinkt bei Kälte/grossem Strom → als Schalter "
                              "mit ü = 2 … 5 auslegen")
            elif e["ue"] > 10:
                zeilen.append("Stark übersteuert (ü > 10): sicher ein, aber lange Ausschaltverzögerung (Speicherzeit) "
                              "und unnötig viel Steuerstrom")
            else:
                zeilen.append("✅ Sicher gesättigt (ü = 2 … 10) – so soll ein Schalter arbeiten")
        if high and e["ub"] > 5.7:
            zeilen.append(f"PNP an {fmt(e['ub'], 'spannung')}: Zum AUSschalten muss U_St ≥ "
                          f"{fmt(e['ub'] - 0.7, 'spannung')} sein – ein µC mit 3.3/5 V schafft das nicht "
                          "→ NPN als Pegelwandler davor")
        farbe = config.FARBEN["akzent"]
        if e["zustand"] == "teil" or (e["zustand"] == "voll" and e["ue"] < 2):
            farbe = WARN
        return zeilen, farbe

    def _sb_bauteil(self, c, w, h, e, xs, y, r, high, zfarbe, text, leise, bg, schrift, fett, dick):
        xb = xs - 0.45 * r                                       # Basis-Balken
        c.create_oval(xs - 1.1 * r, y - r, xs + 0.9 * r, y + r, outline=zfarbe, width=dick + 1)
        c.create_line(xb, y - 0.55 * r, xb, y + 0.55 * r, fill=zfarbe, width=dick + 2)
        pfeil = dict(fill=text, width=dick, arrow="last", arrowshape=(max(8, r * 0.3), max(10, r * 0.36), max(4, r * 0.14)))
        if high:                                                 # PNP: Emitter OBEN, Pfeil zeigt zum Balken
            c.create_line(xs, y - r, xb, y - 0.25 * r, **pfeil)
            c.create_line(xb, y + 0.25 * r, xs, y + r, fill=text, width=dick)
            oben, unten = "E", "C"
        else:                                                    # NPN: Emitter UNTEN, Pfeil zeigt raus
            c.create_line(xb, y - 0.25 * r, xs, y - r, fill=text, width=dick)
            c.create_line(xb, y + 0.25 * r, xs, y + r, **pfeil)
            oben, unten = "C", "E"
        c.create_text(xs + 8, y - r - 0.02 * h, anchor="w", text=oben, fill=leise, font=schrift)
        c.create_text(xs + 8, y + r + 0.02 * h, anchor="w", text=unten, fill=leise, font=schrift)
        c.create_text(xs + 1.1 * r, y, anchor="w", fill=zfarbe, font=fett, text=f"U_CE = {fmt(e['u_ce'], 'spannung', 3)}")
        c.create_text(xs - 1.1 * r - 6, y - 0.04 * h, anchor="e", text="B", fill=leise, font=schrift)
        self._sb_steuerleitung(c, w, h, y, xb, e["u_st"], f"R_B {fmt(self.sb_p['rb'], 'widerstand', 3)}",
                               schrift, fett, dick, bg)
        if e["i_b"] > 0:                                         # Basisstrom-Pfeil: dicker = mehr Übersteuerung
            richtung = (0.29 * w, xb - 10) if not high else (xb - 10, 0.29 * w)      # PNP: Strom fliesst aus der Basis
            c.create_line(richtung[0], y + 0.06 * h, richtung[1], y + 0.06 * h, fill=BLAU,
                          width=max(1, min(7, 1 + 2 * e["ue"])), arrow="last")
            c.create_text((0.27 * w + xs - 1.1 * r) / 2, y + 0.11 * h, text=f"I_B = {fmt(e['i_b'], 'strom', 3)}",
                          fill=BLAU, font=schrift)


# =============================================================================
# MOSFET (N-Kanal / P-Kanal)
# =============================================================================
class MosfetSchalter(_SchalterBasis):

    TYPEN = ["N-Kanal (Low-Side)", "P-Kanal (High-Side)"]
    PARAMETER = [("ub", "U_B", "spannung", "V", "12"), ("rl", "Last R_L", "widerstand", "Ω", "24"),
                 ("uth", "|U_GS(th)|", "spannung", "V", "2"), ("rds", "R_DS(on)", "widerstand", "mΩ", "50"),
                 ("uspec", "… gemessen bei |U_GS|", "spannung", "V", "10"), ("qg", "Gate-Ladung Q_g", "ladung", "nC", "30"),
                 ("rg", "Gate-Widerstand R_G", "widerstand", "Ω", "10")]
    STEUER_TEXT = "Gate-Spannung U_G (gegen GND)"
    STEUER_MAX = 25.0                     # bis über U_GS,max = 20 V, damit die Warnung erreichbar ist
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der MOSFET ist SPANNUNGSGESTEUERT: Die Spannung zwischen Gate und Source öffnet den "
        "Kanal. Im eingeschalteten Zustand fliesst kein Gate-Strom – beim UMSCHALTEN muss aber die Gate-Ladung Q_g "
        "bewegt werden, deshalb braucht es bei schneller PWM einen Treiber. Entscheidend ist nicht U_GS(th) (dort "
        "beginnt er erst zu leiten), sondern R_DS(on) bei der tatsächlichen Gate-Spannung: Nur bei der im Datenblatt "
        "angegebenen U_GS ist der kleine Widerstand garantiert. N-Kanal schaltet auf der Low-Side (Source an GND). "
        "P-Kanal schaltet auf der High-Side (Source an +U_B): eingeschaltet wird, indem man das Gate nach unten zieht.")

    def __init__(self, master):
        super().__init__(master, "🔌 MOSFET als Schalter (interaktiv)",
                         "N- oder P-Kanal wählen, Gate-Spannung verändern – wann ist er wirklich voll eingeschaltet?")

    def _sb_rechnen(self, p, u_g):
        kanal = "P" if self._sb_high_side() else "N"
        m = mm.schalter(kanal, p["ub"], p["rl"], u_g, p["uth"], p["rds"], p["uspec"])   # -> mosfet_mathe.py
        zustand = {"sperrt": "aus", "linear": "teil", "voll": "voll"}[m["zustand"]]
        # Umladezeit mit der EINSCHALT-Spannung rechnen (ausgeschaltet: Datenblatt-Spannung als Ziel)
        u_treiber = abs(m["u_gs"]) if abs(m["u_gs"]) > p["uth"] else p["uspec"]
        gate = dict(mm.gate_umladen(p["qg"], u_treiber, p["rg"]), u_treiber=u_treiber)
        return dict(m, zustand=zustand, u_t=m["u_ds"], ub=p["ub"], rl=p["rl"], u_st=u_g, gate=gate,
                    uth=p["uth"], uspec=p["uspec"], rds=p["rds"])

    def _sb_info(self, e):
        high = e["kanal"] == "P"
        name = "U_SG" if high else "U_GS"
        zeilen = []
        if e["zustand"] == "aus":
            zeilen.append(f"AUS: {name} = {fmt(e['u_gs'], 'spannung')} liegt unter U_th = {fmt(e['uth'], 'spannung')}"
                          + (" → Gate liegt nahe +U_B" if high else ""))
        else:
            zeilen.append(f"{name} = {fmt(e['u_gs'], 'spannung')}   ·   R_on ≈ {fmt(e['r_on'], 'widerstand')}   ·   "
                          f"I = {fmt(e['i'], 'strom')}   ·   U_DS = {fmt(e['u_ds'], 'spannung')}   ·   "
                          f"P = {fmt(e['p_t'], 'leistung')}")
            if e["zustand"] == "teil":
                zeilen.append("⚠ Nur knapp über U_th: Kanal begrenzt den Strom, U_DS ist gross → MOSFET wird heiss")
            elif e["unter_spec"]:
                zeilen.append(f"⚠ R_DS(on) = {fmt(e['rds'], 'widerstand')} gilt nur bei {name} = "
                              f"{fmt(e['uspec'], 'spannung')}. Bei {fmt(e['u_gs'], 'spannung')} ist er ca. "
                              f"{e['r_on'] / e['rds']:.1f}× grösser → Logic-Level-Typ mit R_DS(on)-Angabe bei dieser "
                              "Spannung wählen")
            elif not e["zu_hoch"]:
                zeilen.append("✅ Voll eingeschaltet bei der Datenblatt-Spannung – R_DS(on) wie spezifiziert")
        if e["zu_hoch"]:
            zeilen.append(f"❌ |{name}| = {fmt(abs(e['u_gs']), 'spannung')} > {mm.U_GS_MAX:g} V: Gate-Oxid wird zerstört "
                          "→ Z-Diode (z.B. 12 V) zwischen Gate und Source oder Spannungsteiler")
        if high and e["ub"] > 5.7:
            zeilen.append(f"P-Kanal an {fmt(e['ub'], 'spannung')}: Zum AUSschalten muss das Gate auf ≈ U_B – "
                          "ein µC mit 3.3/5 V schafft das nicht → NPN/N-MOSFET als Pegelwandler davor")
        g = e["gate"]
        zeilen.append(f"Umschalten mit {fmt(g['u_treiber'], 'spannung')} über R_G: Gate-Strom bis ≈ "
                      f"{fmt(g['i_g'], 'strom')}, Q_g umladen dauert ≈ {fmt(g['t_schalt'], 'zeit')} "
                      "(statisch fliesst kein Gate-Strom)")
        farbe = FEHLER if e["zu_hoch"] else (WARN if e["zustand"] == "teil" or
                                             (e["zustand"] == "voll" and e["unter_spec"]) else config.FARBEN["akzent"])
        return zeilen, farbe

    def _sb_bauteil(self, c, w, h, e, xs, y, r, high, zfarbe, text, leise, bg, schrift, fett, dick):
        xk = xs - 0.45 * r                                       # Kanal (3 Striche = Anreicherungstyp)
        xg = xk - 0.28 * r                                       # Gate-Platte
        c.create_oval(xs - 1.1 * r, y - r, xs + 0.9 * r, y + r, outline=zfarbe, width=dick + 1)
        c.create_line(xg, y - 0.55 * r, xg, y + 0.55 * r, fill=text, width=dick)
        for dy in (-0.45, 0, 0.45):
            c.create_line(xk, y + (dy - 0.15) * r, xk, y + (dy + 0.15) * r, fill=zfarbe, width=dick + 2)
        c.create_line(xk, y - 0.45 * r, xs, y - 0.45 * r, xs, y - r, fill=text, width=dick)        # oberer Anschluss
        c.create_line(xk, y + 0.45 * r, xs, y + 0.45 * r, xs, y + r, fill=text, width=dick)        # unterer Anschluss
        pfeil = dict(fill=text, width=dick, arrow="last", arrowshape=(max(8, r * 0.3), max(10, r * 0.36), max(4, r * 0.14)))
        if high:                                                 # P-Kanal: Source OBEN, Pfeil zeigt vom Kanal weg
            c.create_line(xk, y, xs, y, **pfeil)
            c.create_line(xs, y, xs, y - 0.45 * r, fill=text, width=dick)                         # Bulk an Source
            oben, unten = "S", "D"
        else:                                                    # N-Kanal: Source UNTEN, Pfeil zeigt zum Kanal
            c.create_line(xs, y, xk, y, **pfeil)
            c.create_line(xs, y, xs, y + 0.45 * r, fill=text, width=dick)                         # Bulk an Source
            oben, unten = "D", "S"
        c.create_text(xs + 8, y - r - 0.02 * h, anchor="w", text=oben, fill=leise, font=schrift)
        c.create_text(xs + 8, y + r + 0.02 * h, anchor="w", text=unten, fill=leise, font=schrift)
        c.create_text(xs + 1.1 * r, y, anchor="w", fill=zfarbe, font=fett, text=f"U_DS = {fmt(e['u_ds'], 'spannung', 3)}")
        c.create_text(xs - 1.1 * r - 6, y - 0.04 * h, anchor="e", text="G", fill=leise, font=schrift)
        self._sb_steuerleitung(c, w, h, y, xg, e["u_st"], f"R_G {fmt(self.sb_p['rg'], 'widerstand', 3)}",
                               schrift, fett, dick, bg)
        c.create_text((0.27 * w + xs - 1.1 * r) / 2, y + 0.07 * h, fill=BLAU, font=schrift,
                      text=f"{'U_SG' if high else 'U_GS'} = {fmt(e['u_gs'], 'spannung', 3)}")
