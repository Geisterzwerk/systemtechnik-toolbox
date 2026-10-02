# =============================================================================
# bauteile/grafiken/transistor_simulator.py
# -----------------------------------------------------------------------------
# SIMULATOR: Ein NPN-Transistor schaltet eine Lampe (Low-Side-Schalter).
#
#   ┌───────────────────────────────────────────────────────┐
#   │ U_B [12][V]  R Last [120][Ω]  R_B [2.2][kΩ]  B [100]  │
#   │   +U_B ───────────┬──────────                          │
#   │                  (💡) Last        Zustand: GESÄTTIGT   │
#   │                   │               I_B = 1.95 mA        │
#   │  U_St ──[R_B]──→ (╲ NPN)          I_C = 98.3 mA ...    │
#   │                   │                                    │
#   │   GND ────────────┴──────────                          │
#   │  U Steuer: ──────●──────────  (Schieberegler 0 … 5 V)  │
#   └───────────────────────────────────────────────────────┘
#
# WAS MAN SIEHT:
#   - Kreis um den Transistor: grau = gesperrt, orange = aktiv, grün = gesättigt
#   - Lampe leuchtet je nach Kollektorstrom
#   - Violetter Pfeil = Basisstrom (dicker = mehr Übersteuerung)
#   - Im aktiven Bereich ("halb offen") wird der Transistor heiss -> Warnung
#
# Die Rechnung macht bauteile/rechner/transistor_mathe.py arbeitspunkt().
# Alle eigenen Namen beginnen mit ts_ (keine Kollision mit tkinter!).
#
# WER RUFT DAS AUF?  bauteile/rechner/transistor_rechner.py (RECHNER "transistor_simulator")
#                    -> eingebunden in bauteile/inhalte/03_transistoren/transistor.py
# =============================================================================

import customtkinter as ctk

import config                                                   # -> config.py
from bauteile.einheiten import formatieren as fmt               # -> bauteile/einheiten.py
from bauteile.rechner import transistor_mathe as tm             # -> rechner/transistor_mathe.py
from bauteile.rechner.basis import EinheitenEingabe             # -> rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel      # -> core/layout.py

U_MAX = 5.0             # Schieberegler geht bis 5 V (typische Logikpegel 3.3 V / 5 V)

# Farben als (Light, Dark) - wie in config.py
ZUSTAND_FARBE = {"gesperrt": ("#667085", "#9AA1AD"), "aktiv": ("#D97706", "#F59E0B"),
                 "gesättigt": ("#16A34A", "#22C55E")}
ROT = ("#DC2626", "#EF4444")          # +U_B
BLAU = ("#1F6FEB", "#60A5FA")         # GND
VIOLETT = ("#7C3AED", "#A78BFA")      # Basisstrom / Steuerspannung
GELB = "#FACC15"                      # Lampe


def _farbe(paar):
    return paar[1] if ctk.get_appearance_mode() == "Dark" else paar[0]


def _mischen(farbe_a, farbe_b, anteil):
    """Mischt zwei Hex-Farben: anteil 0 = a, 1 = b (für die Lampen-Helligkeit)."""
    a = [int(farbe_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(farbe_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * anteil):02x}" for x, y in zip(a, b))


class TransistorSimulator(Karte):

    def __init__(self, master):
        super().__init__(master, titel="🎛 Simulator: Transistor schaltet eine Lampe",
                         untertitel="Steuerspannung am Regler verändern · Werte ändern und Enter drücken")
        b = self.body
        # Startwerte VOR dem Canvas setzen (der Canvas kann sofort zeichnen wollen)
        self.ts_werte = {"ub": 12.0, "rl": 120.0, "rb": 2200.0, "b": 100.0, "ust": 0.0}
        self.ts_groesse = (0, 0)
        self.ts_ap = tm.arbeitspunkt(12.0, 120.0, 0.0, 2200.0, 100.0)

        # ---- Parameter ----
        eingaben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        eingaben.grid(row=0, column=0, sticky="w")
        self.ts_felder = {
            "ub": self._feld(eingaben, 0, "U_B", "spannung", "V", "12"),
            "rl": self._feld(eingaben, 1, "R Last", "widerstand", "Ω", "120"),
            "rb": self._feld(eingaben, 2, "R_B", "widerstand", "kΩ", "2.2"),
            "b": self._feld(eingaben, 3, "B", "zahl", None, "100"),
        }

        # ---- Schaltung (wächst mit der Breite) ----
        self.ts_canvas = ResponsiveCanvas(b, self._zeichnen, seitenverhaeltnis=0.45, max_hoehe=380)
        self.ts_canvas.grid(row=1, column=0, sticky="ew", pady=(8, 4))

        # ---- Regler Steuerspannung ----
        regler = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        regler.grid(row=2, column=0, sticky="ew")
        regler.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(regler, text="U Steuer  ", anchor="w").grid(row=0, column=0)
        self.ts_regler = ctk.CTkSlider(regler, from_=0, to=U_MAX, number_of_steps=250,
                                       command=self._regler_bewegt)
        self.ts_regler.set(0)
        self.ts_regler.grid(row=0, column=1, sticky="ew")
        self.ts_regler_text = ctk.CTkLabel(regler, text="0.00 V", width=64, anchor="e")
        self.ts_regler_text.grid(row=0, column=2)

        self.ts_anzeige = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"),
                                    text_color=config.FARBEN["akzent"])
        self.ts_anzeige.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        self.ts_neu()

    def _feld(self, rahmen, spalte, text, typ, einheit, start):
        ctk.CTkLabel(rahmen, text=text, anchor="w").grid(row=0, column=spalte * 2, padx=(0 if spalte == 0 else 12, 4))
        feld = EinheitenEingabe(rahmen, typ, "", einheit, breite=64)
        feld.ee_feld.insert(0, start)
        feld.grid(row=0, column=spalte * 2 + 1)
        feld.bei_enter(self.ts_neu)
        return feld

    # -------------------------------------------------------------------------
    def _regler_bewegt(self, wert):
        self.ts_werte["ust"] = float(wert)
        self.ts_regler_text.configure(text=f"{float(wert):.2f} V")
        self.ts_neu()

    def ts_neu(self):
        """Werte lesen, Arbeitspunkt berechnen, Schaltung neu zeichnen."""
        try:
            for schluessel, feld in self.ts_felder.items():
                wert = feld.wert()
                if wert is None or wert <= 0:
                    raise ValueError("Alle Werte müssen grösser als 0 sein")
                self.ts_werte[schluessel] = wert
            v = self.ts_werte
            if v["ub"] <= tm.U_CE_SAT:
                raise ValueError("U_B muss grösser als 0.2 V sein")
            self.ts_ap = tm.arbeitspunkt(v["ub"], v["rl"], v["ust"], v["rb"], v["b"])
        except ValueError as fehler:
            self.ts_anzeige.configure(text=f"⚠ {fehler}", text_color=("#B45309", "#F59E0B"))
            return
        self._erklaeren()
        breite, hoehe = self.ts_groesse
        if breite > 1:
            self.ts_canvas.delete("all")
            self._zeichnen(self.ts_canvas, breite, hoehe)

    def _erklaeren(self):
        a = self.ts_ap
        if a["zustand"] == "gesperrt":
            text = f"U Steuer < {tm.U_BE} V → die Basis-Emitter-Diode sperrt, es fliesst kein Strom."
        elif a["zustand"] == "aktiv":
            text = (f"Nur {a['ue'] * 100:.0f} % des nötigen Basisstroms → I_C = B · I_B. "
                    f"Am Transistor bleiben {fmt(a['u_ce'], 'spannung')} hängen → {fmt(a['p_t'], 'leistung')} Wärme!")
        else:
            text = (f"ü = {a['ue']:.1f} → voll durchgeschaltet, U_CE ≈ {tm.U_CE_SAT} V. "
                    f"Mehr Basisstrom ändert I_C nicht mehr – die Last begrenzt ({fmt(a['i_c_max'], 'strom')}).")
        farbe = config.FARBEN["akzent"] if a["zustand"] != "aktiv" else ("#B45309", "#F59E0B")
        self.ts_anzeige.configure(text=text, text_color=farbe)

    # -------------------------------------------------------------------------
    def _zeichnen(self, c, w, h):
        self.ts_groesse = (w, h)
        a, v = self.ts_ap, self.ts_werte
        linie = _farbe(config.FARBEN["text_leise"])
        text = _farbe(config.FARBEN["text"])
        flaeche = _farbe(config.FARBEN["flaeche"])
        zustand = _farbe(ZUSTAND_FARBE[a["zustand"]])
        lw = max(2, int(h / 150))
        gross = (config.SCHRIFT, max(9, int(h / 26)))
        klein = (config.SCHRIFT, max(8, int(h / 32)))
        hell = a["i_c"] / a["i_c_max"] if a["i_c_max"] > 0 else 0.0     # 0 ... 1

        oben, unten = 0.10 * h, 0.90 * h                  # +U_B- und GND-Schiene
        tx, ty = 0.40 * w, 0.62 * h                        # Transistor-Mitte
        r = 0.13 * h                                       # Radius Transistor-Kreis
        lx = tx + 0.55 * r                                 # x von Kollektor/Emitter-Leitung
        bar = tx - 0.3 * r                                 # x vom Basis-Balken

        # ---- Schienen ----
        c.create_line(0.06 * w, oben, 0.60 * w, oben, fill=_farbe(ROT), width=lw)
        c.create_text(0.06 * w, oben - 0.05 * h, text=f"+U_B = {fmt(v['ub'], 'spannung', 3)}",
                      fill=_farbe(ROT), anchor="w", font=gross)
        c.create_line(0.06 * w, unten, 0.60 * w, unten, fill=_farbe(BLAU), width=lw)
        c.create_text(0.06 * w, unten + 0.05 * h, text="GND", fill=_farbe(BLAU), anchor="w", font=klein)

        # ---- Lampe (Last) ----
        ly, lr = 0.28 * h, 0.075 * h
        if hell > 0.02:
            glanz = lr * (1.3 + 0.9 * hell)
            c.create_oval(lx - glanz, ly - glanz, lx + glanz, ly + glanz, outline="",
                          fill=_mischen(flaeche, GELB, 0.35 * hell))
        c.create_line(lx, oben, lx, ly - lr, fill=linie, width=lw)
        c.create_oval(lx - lr, ly - lr, lx + lr, ly + lr, outline=linie, width=lw,
                      fill=_mischen(flaeche, GELB, hell))
        d = lr * 0.7
        c.create_line(lx - d, ly - d, lx + d, ly + d, fill=linie, width=lw)
        c.create_line(lx - d, ly + d, lx + d, ly - d, fill=linie, width=lw)
        c.create_text(lx + lr + 8, ly, text=f"Last {fmt(v['rl'], 'widerstand', 3)}", fill=text,
                      anchor="w", font=klein)

        # ---- Transistor (NPN) ----
        c.create_line(lx, ly + lr, lx, ty - 0.55 * r, fill=linie, width=lw)                    # Kollektor
        c.create_oval(tx - r, ty - r, tx + r, ty + r, outline=zustand, width=lw + 1)
        c.create_line(bar, ty - 0.5 * r, bar, ty + 0.5 * r, fill=text, width=lw * 2)           # Basis-Balken
        c.create_line(bar, ty - 0.2 * r, lx, ty - 0.55 * r, fill=text, width=lw)
        c.create_line(bar, ty + 0.2 * r, lx, ty + 0.55 * r, fill=text, width=lw,               # Emitter-Pfeil
                      arrow="last", arrowshape=(10, 12, 4))
        c.create_line(lx, ty + 0.55 * r, lx, unten, fill=linie, width=lw)
        for buchstabe, bx, by in (("C", lx + 8, ty - 0.75 * r), ("E", lx + 8, ty + 0.75 * r)):
            c.create_text(bx, by, text=buchstabe, fill=linie, anchor="w", font=klein)

        # ---- Basiskreis mit R_B ----
        start = 0.08 * w
        c.create_line(start, ty, bar, ty, fill=linie, width=lw)
        c.create_rectangle(0.16 * w, ty - 0.035 * h, 0.26 * w, ty + 0.035 * h, outline=linie, width=lw,
                           fill=flaeche)
        c.create_text(0.21 * w, ty - 0.08 * h, text=f"R_B {fmt(v['rb'], 'widerstand', 3)}", fill=text, font=klein)
        c.create_oval(start - 5, ty - 5, start + 5, ty + 5, fill=_farbe(VIOLETT), outline="")
        c.create_text(start, ty - 0.1 * h, text=f"U_St\n{v['ust']:.2f} V", fill=_farbe(VIOLETT),
                      font=(config.SCHRIFT, max(9, int(h / 28)), "bold"), justify="center")
        if a["i_b"] > 0:                                   # Basisstrom-Pfeil: dicker = mehr Übersteuerung
            c.create_line(0.27 * w, ty + 0.06 * h, bar - 0.2 * r, ty + 0.06 * h, fill=_farbe(VIOLETT),
                          width=min(7, 1 + 2 * a["ue"]), arrow="last")
            c.create_text((0.27 * w + bar) / 2, ty + 0.11 * h, text="I_B", fill=_farbe(VIOLETT), font=klein)

        # ---- Messwerte rechts ----
        mx = 0.66 * w
        zeilen = [(f"Zustand: {a['zustand'].upper()}", zustand, True),
                  (f"I_B  = {fmt(a['i_b'], 'strom', 3)}", text, False),
                  (f"I_C  = {fmt(a['i_c'], 'strom', 3)}", text, False),
                  (f"U_CE = {fmt(a['u_ce'], 'spannung', 3)}", text, False),
                  (f"P_T  = {fmt(a['p_t'], 'leistung', 3)}", _farbe(ROT) if a["p_t"] > 0.5 else text, False)]
        for k, (inhalt, farbe, fett) in enumerate(zeilen):
            c.create_text(mx, 0.20 * h + k * 0.11 * h, text=inhalt, fill=farbe, anchor="w",
                          font=(config.SCHRIFT, max(9, int(h / 24)), "bold" if fett else "normal"))
        if a["zustand"] == "aktiv":
            c.create_text(mx, 0.20 * h + 5 * 0.11 * h, text="⚠ Transistor heizt!\n(nur halb offen)",
                          fill=zustand, anchor="nw", font=klein)
