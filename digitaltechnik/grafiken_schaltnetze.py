# =============================================================================
# digitaltechnik/grafiken_schaltnetze.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE der Schaltnetze:
#
#   AddiererKarte   Ripple-Carry-Addierer (4 / 8 Bit) aus Volladdierern, Übertragskette sichtbar, Subtraktion
#   MuxKarte        4:1-Multiplexer und 1:4-Demultiplexer, Datenweg hervorgehoben
#   DecoderKarte    3:8-Decoder (74HC138), 8:3-Prioritäts-Encoder (74HC148), 7-Segment-Decoder
#   AusgangKarte    Push-Pull, Open Drain, Tri-State an einer gemeinsamen Leitung (Schaltplan + Anstieg)
#
# Rechnung: digitaltechnik/schaltnetze_mathe.py
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_addierer")
# Eigene Namen beginnen mit dg_ (keine Kollision mit tkinter).
# =============================================================================

import math

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile.einheiten import formatieren as fmt                      # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN, SchaltungsKarte   # -> bauteile/grafiken/schaltplan.py
from core.layout import Karte, ResponsiveCanvas                        # -> core/layout.py
from digitaltechnik import schaltnetze_mathe as sm                     # -> digitaltechnik/schaltnetze_mathe.py
from digitaltechnik.grafiken import FEHLER, BitLeiste, _erklaerung, _ergebnis_label, _farbe   # -> digitaltechnik/grafiken.py

EINS, NULL_FARBE, ORANGE = "#22C55E", "#6B7280", "#F59E0B"


def _wert_farbe(bit):
    return EINS if bit else NULL_FARBE


class _Leinwand:
    """Kleine Hilfe: Schriften und Farben passend zur Canvas-Grösse."""

    def __init__(self, c, w, h, teiler=22):
        self.c, self.w, self.h = c, w, h
        self.text = _farbe(config.FARBEN["text"])
        self.leise = _farbe(config.FARBEN["text_leise"])
        self.dick = max(2, int(min(w, h * 2) / 260))
        g = max(8, int(min(w / 2.2, h) / teiler))
        self.schrift = (config.SCHRIFT, g)
        self.fett = (config.SCHRIFT, g, "bold")
        self.klein = (config.SCHRIFT, max(7, g - 2))


# =============================================================================
# ADDIERER
# =============================================================================
class AddiererKarte(Karte):
    BREITEN = ["4 Bit", "8 Bit"]

    def __init__(self, master):
        super().__init__(master, titel="➕ Ripple-Carry-Addierer aus Volladdierern (interaktiv)",
                         untertitel="Bits von A und B anklicken – der Übertrag läuft von rechts (LSB) nach links")
        b = self.body
        self.dg_a, self.dg_b, self.dg_e = 0b0110, 0b0011, None
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        self.dg_breite = ctk.CTkSegmentedButton(oben, values=self.BREITEN, command=lambda _v: self._dg_breite_neu())
        self.dg_breite.set(self.BREITEN[0])
        self.dg_breite.grid(row=0, column=0, padx=(0, 12))
        self.dg_art = ctk.CTkSegmentedButton(oben, values=["A + B", "A − B"], command=lambda _v: self._dg_neu())
        self.dg_art.set("A + B")
        self.dg_art.grid(row=0, column=1)
        self.dg_leisten = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        self.dg_leisten.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.36, max_hoehe=320)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(6, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Jeder Volladdierer (VA) rechnet eine Stelle: S = A ⊕ B ⊕ C_ein, "
                       "C_aus = A·B + C_ein·(A ⊕ B). Sein Übertrag geht an die nächste Stelle – deshalb muss das "
                       "Ergebnis warten, bis der Übertrag durch ALLE Stufen gelaufen ist (Ripple Carry, grün = 1). "
                       "Subtraktion: B wird mit XOR invertiert und C_ein = 1 gesetzt, also A + ¬B + 1 = A − B im "
                       "Zweierkomplement – dasselbe Addierwerk rechnet beides. C = Übertrag aus der höchsten Stelle "
                       "(unsigned; bei Subtraktion heisst C = 0 „geborgt“), V = Overflow für signed.").grid(
            row=4, column=0, sticky="ew", pady=(8, 0))
        self._dg_breite_neu()

    def _dg_bits(self):
        return int(self.dg_breite.get().split()[0])

    def _dg_breite_neu(self):
        for kind in self.dg_leisten.winfo_children():
            kind.destroy()
        bits = self._dg_bits()
        self.dg_a &= 2 ** bits - 1
        self.dg_b &= 2 ** bits - 1
        self.dg_la = BitLeiste(self.dg_leisten, bits, lambda n: self._dg_klick("a", n), titel="A")
        self.dg_la.grid(row=0, column=0, sticky="w")
        self.dg_lb = BitLeiste(self.dg_leisten, bits, lambda n: self._dg_klick("b", n), titel="B")
        self.dg_lb.grid(row=1, column=0, sticky="w")
        self._dg_neu()

    def _dg_klick(self, wer, n):
        if wer == "a":
            self.dg_a ^= 1 << n
        else:
            self.dg_b ^= 1 << n
        self._dg_neu()

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis") or not hasattr(self, "dg_la"):
            return
        bits, sub = self._dg_bits(), self.dg_art.get() == "A − B"
        self.dg_la.zeigen(self.dg_a)
        self.dg_lb.zeigen(self.dg_b)
        self.dg_e = e = sm.ripple(self.dg_a, self.dg_b, bits, sub)
        sa = self.dg_a - 2 ** bits if self.dg_a >> (bits - 1) else self.dg_a
        sb = self.dg_b - 2 ** bits if self.dg_b >> (bits - 1) else self.dg_b
        op = "−" if sub else "+"
        richtig_u = self.dg_a - self.dg_b if sub else self.dg_a + self.dg_b
        zeilen = [f"{format(self.dg_a, f'0{bits}b')} {op} {format(self.dg_b, f'0{bits}b')} = "
                  f"{format(e['summe'], f'0{bits}b')}   (C = {e['carry']}, V = {e['overflow']})",
                  f"unsigned: {self.dg_a} {op} {self.dg_b} = {e['summe']}" +
                  ("" if 0 <= richtig_u < 2 ** bits else f"   ✗ (richtig {richtig_u} – passt nicht)"),
                  f"signed:   {sa} {op} {sb} = {e['signed']}" +
                  (f"   ✗ Overflow (richtig {sa - sb if sub else sa + sb})" if e["overflow"] else "   ✓")]
        if sub:
            zeilen.append(f"gerechnet als A + ¬B + 1 = {format(self.dg_a, f'0{bits}b')} + "
                          f"{format(~self.dg_b & (2 ** bits - 1), f'0{bits}b')} + 1")
        lauf = sm.laufzeit(bits, 10e-9)
        zeilen.append(f"Laufzeit bei 10 ns pro Stufe: bis {fmt(lauf['t_ges'], 'zeit', 3)} (Übertrag durch {bits} Stufen)")
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=WARN if e["overflow"] else config.FARBEN["akzent"])
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    def _dg_zeichnen(self, c, w, h):
        if self.dg_e is None:
            return
        L = _Leinwand(c, w, h, teiler=16 if self._dg_bits() == 4 else 20)
        stufen, bits = self.dg_e["stufen"], self._dg_bits()
        breite = w * 0.8 / bits
        kb, kh = breite * 0.62, h * 0.3
        y0 = h * 0.4
        for i, (a, b, c_ein, s, c_aus) in enumerate(stufen):
            x = w * 0.13 + (bits - 1 - i) * breite                 # LSB rechts
            c.create_rectangle(x, y0, x + kb, y0 + kh, outline=L.text, width=L.dick)
            c.create_text(x + kb / 2, y0 + kh / 2, text="VA", fill=L.leise, font=L.fett)
            for dx, name, wert, hoch in ((0.3, "A", a, 0.24), (0.7, "B", b, 0.12)):   # A höher als B: Texte überlappen nicht
                xx = x + kb * dx
                c.create_line(xx, y0 - h * hoch, xx, y0, fill=_wert_farbe(wert), width=L.dick)
                c.create_text(xx, y0 - h * hoch - 1, text=f"{name}{i}={wert}", anchor="s", fill=_wert_farbe(wert),
                              font=L.klein)
            c.create_line(x + kb / 2, y0 + kh, x + kb / 2, y0 + kh + h * 0.12, fill=_wert_farbe(s), width=L.dick)
            c.create_text(x + kb / 2, y0 + kh + h * 0.13, text=f"S{i}={s}", anchor="n", fill=_wert_farbe(s), font=L.fett)
            # Übertrag nach links (zur nächsten Stufe bzw. C-Ausgang)
            ym = y0 + kh / 2
            c.create_line(x, ym, x - (breite - kb), ym, fill=_wert_farbe(c_aus), width=L.dick + 1, arrow="last",
                          arrowshape=(8, 10, 4))
            if i == bits - 1:
                c.create_text(x - (breite - kb) / 2, ym - 5, text=f"C={c_aus}", anchor="s", fill=_wert_farbe(c_aus),
                              font=L.fett)
            if i == 0:
                c.create_line(x + kb + (breite - kb) * 0.8, ym, x + kb, ym, fill=_wert_farbe(c_ein), width=L.dick + 1,
                              arrow="last", arrowshape=(8, 10, 4))
                c.create_text(x + kb + 2, ym - 4, text=f"C_ein={c_ein}", anchor="sw", fill=_wert_farbe(c_ein),
                              font=L.klein)


# =============================================================================
# MULTIPLEXER / DEMULTIPLEXER
# =============================================================================
class MuxKarte(Karte):
    ARTEN = ["MUX 4:1", "DEMUX 1:4"]

    def __init__(self, master):
        super().__init__(master, titel="🔀 Multiplexer und Demultiplexer (interaktiv)",
                         untertitel="Eingänge und Auswahl S1 S0 anklicken – der aktive Datenweg ist grün")
        b = self.body
        self.dg_d, self.dg_s, self.dg_x = [0, 1, 1, 0], [1, 0], 1
        self.dg_art = ctk.CTkSegmentedButton(b, values=self.ARTEN, command=lambda _v: self._dg_neu())
        self.dg_art.set(self.ARTEN[0])
        self.dg_art.grid(row=0, column=0, sticky="w")
        knoepfe = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        knoepfe.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.dg_knoepfe = {}
        for spalte, name in enumerate(["D0", "D1", "D2", "D3", "X", "S1", "S0"]):
            k = ctk.CTkButton(knoepfe, text=name, width=62, height=30, font=(config.SCHRIFT_CODE, 13, "bold"),
                              command=lambda name=name: self._dg_klick(name))
            k.grid(row=0, column=spalte, padx=(0 if spalte == 0 else (14 if name in ("X", "S1") else 4), 0))
            self.dg_knoepfe[name] = k
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.42, max_hoehe=340)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Der Multiplexer ist ein digital gesteuerter Umschalter: Die "
                       "Auswahleingänge (Binärzahl S1 S0) bestimmen, welcher Dateneingang zum Ausgang durchgeschaltet "
                       "wird – Y = ¬S1·¬S0·D0 + ¬S1·S0·D1 + S1·¬S0·D2 + S1·S0·D3. Der Demultiplexer macht das "
                       "Umgekehrte: ein Eingang wird auf einen von vier Ausgängen verteilt. Anwendungen: mehrere "
                       "Sensoren an einen ADC (Analog-MUX), Bus-Auswahl, Zeitmultiplex. Ein 2^n:1-MUX kann ausserdem "
                       "JEDE Logikfunktion mit n + 1 Variablen bilden.").grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self._dg_neu()

    def _dg_klick(self, name):
        if name.startswith("D"):
            self.dg_d[int(name[1])] ^= 1
        elif name == "X":
            self.dg_x ^= 1
        else:
            i = 0 if name == "S1" else 1
            self.dg_s[i] ^= 1
        self._dg_neu()

    def _dg_auswahl(self):
        return self.dg_s[0] * 2 + self.dg_s[1]

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        mux_art = self.dg_art.get() == self.ARTEN[0]
        werte = {f"D{k}": self.dg_d[k] for k in range(4)}
        werte.update({"X": self.dg_x, "S1": self.dg_s[0], "S0": self.dg_s[1]})
        for name, k in self.dg_knoepfe.items():
            sichtbar = (name != "X") if mux_art else (not name.startswith("D"))
            if sichtbar:
                k.grid()
                k.configure(text=f"{name}={werte[name]}",
                            fg_color=config.FARBEN["akzent"] if werte[name] else config.FARBEN["rahmen"],
                            text_color=("#FFFFFF", "#FFFFFF") if werte[name] else config.FARBEN["text"])
            else:
                k.grid_remove()
        s = self._dg_auswahl()
        if mux_art:
            y = sm.mux(self.dg_d, s)
            text = [f"S1 S0 = {self.dg_s[0]}{self.dg_s[1]} = {s}  →  Y = D{s} = {y}",
                    "Y = ¬S1·¬S0·D0 + ¬S1·S0·D1 + S1·¬S0·D2 + S1·S0·D3"]
        else:
            ys = sm.demux(self.dg_x, s, 4)
            text = [f"S1 S0 = {self.dg_s[0]}{self.dg_s[1]} = {s}  →  Y{s} = X = {self.dg_x}, alle anderen 0",
                    "Y0 Y1 Y2 Y3 = " + " ".join(map(str, ys))]
        self.dg_ergebnis.configure(text="\n".join(text), text_color=config.FARBEN["akzent"])
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    def _dg_zeichnen(self, c, w, h):
        if not hasattr(self, "dg_ergebnis"):
            return
        L = _Leinwand(c, w, h, teiler=15)
        mux_art = self.dg_art.get() == self.ARTEN[0]
        s = self._dg_auswahl()
        x0, x1 = w * 0.38, w * 0.58
        y0, y1 = h * 0.08, h * 0.78
        schraeg = (y1 - y0) * 0.16
        if mux_art:                                           # Trapez: links hoch, rechts niedrig
            punkte = (x0, y0, x1, y0 + schraeg, x1, y1 - schraeg, x0, y1)
        else:
            punkte = (x0, y0 + schraeg, x1, y0, x1, y1, x0, y1 - schraeg)
        c.create_polygon(*punkte, outline=L.text, fill="", width=L.dick)
        c.create_text((x0 + x1) / 2, y0 + h * 0.2, text="MUX" if mux_art else "DEMUX", fill=L.leise, font=L.fett)
        ys = [y0 + (y1 - y0) * (k + 0.9) / 4.6 + h * 0.05 for k in range(4)]
        ym = (y0 + y1) / 2
        for k, yy in enumerate(ys):
            if mux_art:
                farbe = _wert_farbe(self.dg_d[k])
                c.create_line(w * 0.18, yy, x0, yy, fill=farbe, width=L.dick)
                c.create_text(w * 0.17, yy, text=f"D{k}={self.dg_d[k]}", anchor="e", fill=farbe, font=L.schrift)
            else:
                wert = self.dg_x if k == s else 0
                farbe = _wert_farbe(wert)
                c.create_line(x1, yy, w * 0.78, yy, fill=farbe, width=L.dick)
                c.create_text(w * 0.79, yy, text=f"Y{k}={wert}", anchor="w", fill=farbe, font=L.schrift)
        # Datenweg im Inneren
        if mux_art:
            y = self.dg_d[s]
            c.create_line(x0, ys[s], x1, ym, fill=EINS if y else ORANGE, width=L.dick + 1, dash=(6, 3))
            c.create_line(x1, ym, w * 0.78, ym, fill=_wert_farbe(y), width=L.dick)
            c.create_text(w * 0.79, ym, text=f"Y={y}", anchor="w", fill=_wert_farbe(y), font=L.fett)
        else:
            c.create_line(w * 0.18, ym, x0, ym, fill=_wert_farbe(self.dg_x), width=L.dick)
            c.create_text(w * 0.17, ym, text=f"X={self.dg_x}", anchor="e", fill=_wert_farbe(self.dg_x), font=L.fett)
            c.create_line(x0, ym, x1, ys[s], fill=EINS if self.dg_x else ORANGE, width=L.dick + 1, dash=(6, 3))
        # Auswahlleitungen unten
        for i, (name, wert) in enumerate((("S1", self.dg_s[0]), ("S0", self.dg_s[1]))):
            xx = x0 + (x1 - x0) * (0.35 + 0.35 * i)
            unten = y1 - schraeg * (0.35 + 0.35 * i) * (1 if mux_art else 0) - (0 if mux_art else schraeg * (0.65 - 0.35 * i))
            c.create_line(xx, h * 0.95, xx, unten, fill=_wert_farbe(wert), width=L.dick)
            c.create_text(xx + (-4 if i == 0 else 4), h * 0.93, text=f"{name}={wert}", anchor="e" if i == 0 else "w",
                          fill=_wert_farbe(wert), font=L.klein)                   # S1 links, S0 rechts der Leitung


# =============================================================================
# DECODER / ENCODER / 7-SEGMENT
# =============================================================================
class DecoderKarte(Karte):
    ARTEN = ["Decoder 3:8 (74HC138)", "Prioritäts-Encoder 8:3", "7-Segment-Decoder"]

    def __init__(self, master):
        super().__init__(master, titel="🔢 Decoder, Encoder und 7-Segment-Anzeige (interaktiv)",
                         untertitel="Eingänge anklicken – welcher Ausgang wird aktiv?")
        b = self.body
        self.dg_adr, self.dg_frei, self.dg_ein, self.dg_ziffer = 5, 1, 0b00100100, 7
        self.dg_art = ctk.CTkSegmentedButton(b, values=self.ARTEN, command=lambda _v: self._dg_art_neu())
        self.dg_art.set(self.ARTEN[0])
        self.dg_art.grid(row=0, column=0, sticky="w")
        self.dg_eingabe = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        self.dg_eingabe.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.dg_anode = None
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.36, max_hoehe=320)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Ein DECODER macht aus einer Binärzahl mit n Bit genau EINEN aktiven "
                       "von 2^n Ausgängen (1-aus-n) – z.B. um einen von acht Speicherbausteinen auszuwählen. Der "
                       "74HC138 hat Ausgänge, die bei Aktivität LOW werden (¬Y), und einen Freigabe-Eingang. Ein "
                       "ENCODER macht das Umgekehrte; der Prioritäts-Encoder meldet den HÖCHSTEN aktiven Eingang "
                       "(Tastatur, Interrupt-Prioritäten) und mit GS, ob überhaupt einer aktiv ist. Der "
                       "7-Segment-Decoder (z.B. 74HC4511) schaltet für jede Ziffer die passenden Segmente a … g."
                  ).grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self._dg_art_neu()

    def _dg_art_neu(self):
        for kind in self.dg_eingabe.winfo_children():
            kind.destroy()
        art = self.ARTEN.index(self.dg_art.get())
        if art == 0:
            self.dg_leiste = BitLeiste(self.dg_eingabe, 3, self._dg_klick_adr, titel="A2 A1 A0")
            self.dg_leiste.grid(row=0, column=0, sticky="w")
            self.dg_frei_knopf = ctk.CTkButton(self.dg_eingabe, text="", width=120, command=self._dg_klick_frei)
            self.dg_frei_knopf.grid(row=0, column=1, padx=(16, 0))
        elif art == 1:
            self.dg_leiste = BitLeiste(self.dg_eingabe, 8, self._dg_klick_ein, titel="I7 … I0")
            self.dg_leiste.grid(row=0, column=0, sticky="w")
        else:
            self.dg_leiste = BitLeiste(self.dg_eingabe, 4, self._dg_klick_ziffer, titel="D C B A")
            self.dg_leiste.grid(row=0, column=0, sticky="w")
            self.dg_anode = ctk.CTkSegmentedButton(self.dg_eingabe, values=["gemeinsame Kathode", "gemeinsame Anode"],
                                                   command=lambda _v: self._dg_neu())
            self.dg_anode.set("gemeinsame Kathode")
            self.dg_anode.grid(row=0, column=1, padx=(16, 0))
        self._dg_neu()

    def _dg_klick_adr(self, n):
        self.dg_adr ^= 1 << n
        self._dg_neu()

    def _dg_klick_frei(self):
        self.dg_frei ^= 1
        self._dg_neu()

    def _dg_klick_ein(self, n):
        self.dg_ein ^= 1 << n
        self._dg_neu()

    def _dg_klick_ziffer(self, n):
        self.dg_ziffer ^= 1 << n
        self._dg_neu()

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        art = self.ARTEN.index(self.dg_art.get())
        if art == 0:
            self.dg_leiste.zeigen(self.dg_adr)
            self.dg_frei_knopf.configure(text=f"Freigabe = {self.dg_frei}",
                                         fg_color=config.FARBEN["akzent"] if self.dg_frei else config.FARBEN["rahmen"])
            pegel = sm.decoder(self.dg_adr, 3, bool(self.dg_frei))
            text = [f"Adresse {format(self.dg_adr, '03b')} = {self.dg_adr}  →  " +
                    (f"¬Y{self.dg_adr} = 0 (aktiv), alle anderen 1" if self.dg_frei else "gesperrt: alle ¬Y = 1"),
                    "¬Y7 … ¬Y0 = " + " ".join(str(p) for p in reversed(pegel))]
        elif art == 1:
            self.dg_leiste.zeigen(self.dg_ein)
            eingaenge = [(self.dg_ein >> k) & 1 for k in range(8)]
            code, gs = sm.prioritaets_encoder(eingaenge)
            text = [f"höchster aktiver Eingang: I{code}  →  A2 A1 A0 = {format(code, '03b')}   GS = {gs}"
                    if gs else "kein Eingang aktiv  →  GS = 0 (Code ungültig)",
                    "niedrigere aktive Eingänge werden ignoriert (Priorität)"]
        else:
            self.dg_leiste.zeigen(self.dg_ziffer)
            anode = self.dg_anode.get() == "gemeinsame Anode"
            e = sm.siebensegment(self.dg_ziffer, anode)
            text = [f"Ziffer {self.dg_ziffer:X}  →  Segmente an: {' '.join(e['segmente'])}",
                    "Pegel a … g = " + " ".join(str(e["pegel"][s]) for s in "abcdefg") +
                    ("   (LOW = Segment an)" if anode else "   (HIGH = Segment an)")]
        self.dg_ergebnis.configure(text="\n".join(text), text_color=config.FARBEN["akzent"])
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    def _dg_zeichnen(self, c, w, h):
        if not hasattr(self, "dg_ergebnis"):
            return
        L = _Leinwand(c, w, h, teiler=15)
        art = self.ARTEN.index(self.dg_art.get())
        if art == 2:
            self._dg_siebensegment(c, L, w, h)
            return
        x0, x1, y0, y1 = w * 0.36, w * 0.56, h * 0.06, h * 0.94
        c.create_rectangle(x0, y0, x1, y1, outline=L.text, width=L.dick)
        c.create_text((x0 + x1) / 2, y0 + h * 0.08, text="138" if art == 0 else "148", fill=L.leise, font=L.fett)
        r = max(4, h * 0.03)
        if art == 0:
            pegel = sm.decoder(self.dg_adr, 3, bool(self.dg_frei))
            for i in range(3):
                bit = (self.dg_adr >> (2 - i)) & 1
                y = y0 + (y1 - y0) * (i + 1.5) / 5
                c.create_line(w * 0.2, y, x0, y, fill=_wert_farbe(bit), width=L.dick)
                c.create_text(w * 0.19, y, text=f"A{2 - i}={bit}", anchor="e", fill=_wert_farbe(bit), font=L.schrift)
            y = y0 + (y1 - y0) * 4.3 / 5
            c.create_line(w * 0.2, y, x0, y, fill=_wert_farbe(self.dg_frei), width=L.dick)
            c.create_text(w * 0.19, y, text=f"E={self.dg_frei}", anchor="e", fill=_wert_farbe(self.dg_frei), font=L.schrift)
            for k in range(8):
                y = y0 + (y1 - y0) * (k + 0.8) / 8.6
                aktiv = pegel[k] == 0
                c.create_oval(x1, y - r, x1 + 2 * r, y + r, outline=L.text, width=L.dick)   # Negation
                farbe = ORANGE if aktiv else NULL_FARBE
                c.create_line(x1 + 2 * r, y, w * 0.74, y, fill=farbe, width=L.dick)
                c.create_text(w * 0.75, y, text=f"¬Y{k}={pegel[k]}" + ("  ◀ aktiv" if aktiv else ""), anchor="w",
                              fill=farbe, font=L.klein)
        else:
            code, gs = sm.prioritaets_encoder([(self.dg_ein >> k) & 1 for k in range(8)])
            for k in range(8):
                bit = (self.dg_ein >> k) & 1
                y = y0 + (y1 - y0) * (k + 0.8) / 8.6
                farbe = EINS if (bit and k == code and gs) else _wert_farbe(bit)
                c.create_line(w * 0.2, y, x0, y, fill=farbe, width=L.dick + (1 if k == code and gs else 0))
                c.create_text(w * 0.19, y, text=f"I{k}={bit}", anchor="e", fill=farbe, font=L.klein)
            for i, (name, wert) in enumerate((("A2", code >> 2 & 1), ("A1", code >> 1 & 1), ("A0", code & 1),
                                              ("GS", gs))):
                y = y0 + (y1 - y0) * (i + 1.2) / 5
                c.create_line(x1, y, w * 0.74, y, fill=_wert_farbe(wert), width=L.dick)
                c.create_text(w * 0.75, y, text=f"{name}={wert}", anchor="w", fill=_wert_farbe(wert), font=L.schrift)

    def _dg_siebensegment(self, c, L, w, h):
        anode = self.dg_anode is not None and self.dg_anode.get() == "gemeinsame Anode"
        e = sm.siebensegment(self.dg_ziffer, anode)
        bx, by, bb, bh = w * 0.42, h * 0.14, min(w * 0.16, h * 0.4), h * 0.72
        d = max(4, bb * 0.14)
        an_farbe, aus_farbe = "#EF4444", _farbe(("#E5E7EB", "#2A2E36"))
        lage = {"a": (bx, by, bx + bb, by), "g": (bx, by + bh / 2, bx + bb, by + bh / 2), "d": (bx, by + bh, bx + bb, by + bh),
                "f": (bx, by, bx, by + bh / 2), "b": (bx + bb, by, bx + bb, by + bh / 2),
                "e": (bx, by + bh / 2, bx, by + bh), "c": (bx + bb, by + bh / 2, bx + bb, by + bh)}
        for seg, (xa, ya, xe, ye) in lage.items():
            an = seg in e["segmente"]
            c.create_line(xa + (d if xa != xe else 0), ya + (d if ya != ye else 0),
                          xe - (d if xa != xe else 0), ye - (d if ya != ye else 0),
                          fill=an_farbe if an else aus_farbe, width=d * 1.4, capstyle="round")
            mx, my = (xa + xe) / 2, (ya + ye) / 2
            dx = -d * 1.6 if seg in "fe" else (d * 1.6 if seg in "bc" else 0)
            dy = -d * 1.6 if seg == "a" else (d * 1.6 if seg == "d" else (-d * 1.2 if seg == "g" else 0))
            c.create_text(mx + dx, my + dy, text=seg, fill=L.leise, font=L.klein)
        c.create_text(w * 0.12, h * 0.5, text=f"{self.dg_ziffer:X}", fill=L.text, font=(config.SCHRIFT, int(h * 0.35), "bold"))
        tx = w * 0.7
        for i, seg in enumerate("abcdefg"):
            p = e["pegel"][seg]
            an = seg in e["segmente"]
            c.create_text(tx, h * 0.12 + i * h * 0.11, text=f"{seg} = {p}" + ("  an" if an else ""), anchor="w",
                          fill=an_farbe if an else L.leise, font=L.schrift)


# =============================================================================
# AUSGANGSTYPEN
# =============================================================================
class AusgangKarte(SchaltungsKarte):
    TITEL = "🔌 Ausgangstypen an einer gemeinsamen Leitung (interaktiv)"
    UNTERTITEL = "Zwei Bausteine treiben dieselbe Leitung – was passiert bei Push-Pull, Open Drain und Tri-State?"
    VARIANTEN = ["Push-Pull", "Open Drain + Pull-up", "Tri-State"]
    SCHALTER = [("a", "Ausgang 1 = 1"), ("b", "Ausgang 2 = 1"), ("en", "Tri-State: Treiber 2 freigegeben")]
    REGLER = [("ub", "Versorgung U_B", "spannung", 1.8, 5.0, 3.3, {"einheit": "V", "grenzen": (1.0, 15)}),
              ("rp", "Pull-up R_P", "widerstand", 470.0, 47e3, 4.7e3, {"einheit": "kΩ", "log": True, "grenzen": (10.0, 1e7)}),
              ("cb", "Leitungskapazität C_Bus", "kapazitaet", 10e-12, 1e-9, 200e-12,
               {"einheit": "pF", "log": True, "grenzen": (1e-13, 1e-6)})]
    RASTER = (23.4, 9.6)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  PUSH-PULL (Totem-Pole, normale CMOS-Ausgänge): ein Transistor nach U_B und einer nach "
        "GND – der Ausgang treibt aktiv HIGH und LOW, schnell und kräftig. Zwei solche Ausgänge an EINER Leitung "
        "kämpfen gegeneinander, sobald sie verschieden sind: Kurzschlussstrom (Buskonflikt). OPEN DRAIN (bzw. Open "
        "Collector): nur der Transistor nach GND – HIGH macht der Pull-up-Widerstand. Mehrere Ausgänge dürfen "
        "zusammengeschaltet werden: Sobald einer LOW zieht, ist die Leitung LOW (Wired-AND, I²C, Interrupt-Leitung). "
        "Dafür steigt die Spannung nur langsam mit τ = R_P · C_Bus. TRI-STATE: Push-Pull mit Freigabe – gesperrt "
        "ist der Ausgang hochohmig (Z) und gibt die Leitung frei; es darf immer nur EIN Treiber freigegeben sein.")

    def sk_rechnen(self, w, v):
        a, b = int(w["a"]), int(w["b"])
        e = {"a": a, "b": b, "konflikt": False}
        if v == "Push-Pull":
            if a != b:
                k = sm.buskonflikt(w["ub"])
                e.update(konflikt=True, i=k["i"], u=k["u_leitung"], p=k["p"])
            else:
                e["u"] = w["ub"] * a
        elif v == "Open Drain + Pull-up":
            od = sm.open_drain_pullup(w["ub"], w["cb"], r=w["rp"])
            e.update(od, u=w["ub"] if (a and b) else 0.0)
            tau = w["rp"] * w["cb"]
            e["kurve"] = [(k / 100, 1 - math.exp(-5 * k / 100)) for k in range(101)]   # 0 … 5τ
            e["tau"] = tau
        else:
            treiber2 = bool(w["en"])
            if treiber2 and a != b:
                k = sm.buskonflikt(w["ub"])
                e.update(konflikt=True, i=k["i"], u=k["u_leitung"], p=k["p"])
            else:
                e["u"] = w["ub"] * a
            e["en"] = treiber2
        return e

    def _treiber(self, p, x, y_o, y_u, y_l, wert, art, name, aktiv=True):
        """Ausgangsstufe als zwei Schalter: oben nach U_B, unten nach GND (Open Drain: nur unten)."""
        p.kasten(x - 1.6, y_o - 0.6, x + 1.4, y_u + 0.6)
        p.text(x - 0.1, y_o - 0.95, name, "center", fett=True)
        oben_zu = aktiv and art != "od" and wert == 1
        unten_zu = aktiv and wert == 0
        if art != "od":
            p.versorgung(x, y_o, "")
            p.schalter(x, y_o + 0.3, x, y_l - 0.3, oben_zu, "")
            p.leitung((x, y_l - 0.3), (x, y_l))
        p.schalter(x, y_l + 0.3, x, y_u - 0.3, unten_zu, "")
        p.leitung((x, y_l), (x, y_l + 0.3))
        p.leitung((x, y_u - 0.3), (x, y_u))
        p.masse(x, y_u)
        zustand = "Z (hochohmig)" if not aktiv else (("LOW" if wert == 0 else "aus") if art == "od" else
                                                     ("HIGH" if wert else "LOW"))
        p.text(x - 1.4, y_u + 1.15, f"{name}: {zustand}", "w", klein=True,
               farbe=SPANNUNG if aktiv else p.leise)

    def sk_zeichnen(self, p, w, e, v):
        y_o, y_l, y_u = 1.9, 4.7, 7.6
        art = {"Push-Pull": "pp", "Open Drain + Pull-up": "od", "Tri-State": "pp"}[v]
        self._treiber(p, 2.4, y_o, y_u, y_l, e["a"], art, "Treiber 1")
        self._treiber(p, 8.6, y_o, y_u, y_l, e["b"], art, "Treiber 2", aktiv=e.get("en", True))
        p.leitung((2.4, y_l), (11.4, y_l))
        p.knoten(2.4, y_l)
        p.knoten(8.6, y_l)
        p.anschluss(11.4, y_l, "Bus")
        p.messpunkt(5.5, y_l, "M1")
        if art == "od":
            p.versorgung(5.5, 0.8, "")
            p.widerstand(5.5, 1.0, 5.5, y_l, "R_P", fmt(w["rp"], "widerstand", 3))
            p.knoten(5.5, y_l)
        farbe = FEHLER[1] if e["konflikt"] else SPANNUNG
        if e["konflikt"]:
            p.text(10.2, y_l + 0.65, "Kurzschluss!", "w", fett=True, farbe=farbe)
            p.text(10.2, y_l + 1.25, f"I ≈ {fmt(e['i'], 'strom', 3)}", "w", fett=True, farbe=farbe)
        else:
            p.text(10.2, y_l + 0.65, f"U_Bus = {fmt(e['u'], 'spannung', 3)}", "w", fett=True, farbe=farbe)
        if art == "od" and getattr(self, "mit_diagramm", True):
            p.diagramm(14.2, 1.4, 22.8, 7.6, [(e["kurve"], SPANNUNG, None, False)], 0.0, 1.1,
                       f"Anstieg nach dem Loslassen  ·  τ = R_P · C = {fmt(e['tau'], 'zeit', 3)}",
                       [(0.3, "30 %"), (0.7, "70 %"), (1.0, "U_B")], zeit_text="0 … 5τ")

    def sk_raster(self, breite):
        self.mit_diagramm = breite >= 600
        return self.RASTER if self.mit_diagramm else (12.6, 9.6)

    def sk_info(self, w, e, v):
        if v == "Push-Pull":
            if e["konflikt"]:
                return [f"Ausgänge verschieden → beide treiben gegeneinander: I ≈ U_B / (2 · R_on) = "
                        f"{fmt(e['i'], 'strom', 3)}, Leitung ≈ {fmt(e['u'], 'spannung', 3)} (undefiniert!)",
                        "❌ Push-Pull-Ausgänge nie direkt verbinden – Tri-State oder Open Drain verwenden"], FEHLER
            return [f"Beide gleich → Leitung {fmt(e['u'], 'spannung', 3)} – geht nur gut, solange sie nie verschieden sind"], WARN
        if v == "Open Drain + Pull-up":
            zeilen = [f"Wired-AND: Leitung = Ausgang 1 · Ausgang 2 = {e['a'] & e['b']}  ({fmt(e['u'], 'spannung', 3)})",
                      f"Anstieg 30 → 70 %: t_r = 0.847 · R · C = {fmt(e['t_r'], 'zeit', 3)}   ·   "
                      f"LOW-Strom (U_B − 0.4 V) / R = {fmt(e['i_low'], 'strom', 3)}"]
            if e["t_r"] > 1e-6:
                zeilen.append("⚠ Langsamer als I²C Standard-Mode (1 µs) → kleineres R_P oder weniger Kapazität")
                return zeilen, WARN
            if e["i_low"] > 3e-3:
                zeilen.append("⚠ LOW-Strom über 3 mA (I²C-Grenze) → R_P grösser")
                return zeilen, WARN
            return zeilen, OK
        if e["konflikt"]:
            return [f"Beide Treiber freigegeben und verschieden → Buskonflikt, I ≈ {fmt(e['i'], 'strom', 3)}",
                    "❌ Immer nur EINEN Tri-State-Treiber freigeben (Bus-Arbitrierung)"], FEHLER
        if not e["en"]:
            return [f"Treiber 2 hochohmig (Z) → Treiber 1 bestimmt die Leitung: {fmt(e['u'], 'spannung', 3)}"], OK
        return [f"Beide freigegeben, aber gleich → kein Strom, Leitung {fmt(e['u'], 'spannung', 3)} (Glück gehabt)"], WARN
