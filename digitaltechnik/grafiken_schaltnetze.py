# =============================================================================
# digitaltechnik/grafiken_schaltnetze.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE der Schaltnetze - MODELLE OHNE FENSTER (Desktop-App UND Web):
#
#   AddiererKarte   Ripple-Carry-Addierer (4 / 8 Bit) aus Volladdierern, Übertragskette sichtbar, Subtraktion
#   MuxKarte        4:1-Multiplexer und 1:4-Demultiplexer, Datenweg hervorgehoben
#   DecoderKarte    3:8-Decoder (74HC138), 8:3-Prioritäts-Encoder (74HC148), 7-Segment-Decoder
#   AusgangKarte    Push-Pull, Open Drain, Tri-State an einer gemeinsamen Leitung (Schaltplan + Anstieg)
#
# Rechnung: digitaltechnik/schaltnetze_mathe.py
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_addierer")
# =============================================================================

import math

import config                                                          # -> config.py
from bauteile.einheiten import formatieren as fmt                      # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN, SchaltungsModell, farbe_waehlen  # -> schaltplan.py
from digitaltechnik import schaltnetze_mathe as sm                     # -> digitaltechnik/schaltnetze_mathe.py
from digitaltechnik import zahlen_mathe as zm                          # -> digitaltechnik/zahlen_mathe.py
from digitaltechnik.grafiken import FEHLER, farben                     # -> digitaltechnik/grafiken.py

EINS, NULL_FARBE, ORANGE = "#22C55E", "#6B7280", "#F59E0B"


def _wert_farbe(bit):
    return EINS if bit else NULL_FARBE


def bitmuster(text, bits, name):
    """Bitmuster aus einem Textfeld: binär ('0110', '0b0110'), hex nur mit 0x. Muss in 'bits' Bit passen."""
    t = str(text or "").strip()
    wert = zm.einlesen(t, None if t.lower().startswith(("0x", "0o", "0b")) else 2)
    if not 0 <= wert < 2 ** bits:
        raise ValueError(f"{name} passt nicht in {bits} Bit (0 … {2 ** bits - 1})")
    return wert


class _Leinwand:
    """Kleine Hilfe: Schriften und Farben passend zur Zeichenfläche."""

    def __init__(self, p, teiler=22):
        self.c, self.w, self.h = p.c, p.breite, p.hoehe
        self.text, self.leise, _, _ = farben(p)
        self.dunkel = p.dunkel
        self.dick = max(2, int(min(self.w, self.h * 2) / 260))
        g = max(8, int(min(self.w / 2.2, self.h) / teiler))
        self.schrift = (config.SCHRIFT, g)
        self.fett = (config.SCHRIFT, g, "bold")
        self.klein = (config.SCHRIFT, max(7, g - 2))


# =============================================================================
# ADDIERER
# =============================================================================
class AddiererKarte(SchaltungsModell):
    TITEL = "➕ Ripple-Carry-Addierer aus Volladdierern (interaktiv)"
    UNTERTITEL = "A und B als Bitmuster eintippen – der Übertrag läuft von rechts (LSB) nach links"
    VARIANTEN = ["4 Bit", "8 Bit"]
    AUSWAHL = [("art", "Rechnung", ["A + B", "A − B"], "A + B")]
    TEXTFELDER = [("a", "A (binär)", "0110", {"max": 20, "platzhalter": "z.B. 0110 oder 0x6"}),
                  ("b", "B (binär)", "0011", {"max": 20, "platzhalter": "z.B. 0011"})]
    STARTWERTE = {"4 Bit": {"a": "0110", "b": "0011"}, "8 Bit": {"a": "0110 0100", "b": "0011 0010"}}
    SEITENVERHAELTNIS = 0.36
    MAX_HOEHE = 320
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Jeder Volladdierer (VA) rechnet eine Stelle: S = A ⊕ B ⊕ C_ein, "
                  "C_aus = A·B + C_ein·(A ⊕ B). Sein Übertrag geht an die nächste Stelle – deshalb muss das Ergebnis "
                  "warten, bis der Übertrag durch ALLE Stufen gelaufen ist (Ripple Carry, grün = 1). Subtraktion: B wird "
                  "mit XOR invertiert und C_ein = 1 gesetzt, also A + ¬B + 1 = A − B im Zweierkomplement – dasselbe "
                  "Addierwerk rechnet beides. C = Übertrag aus der höchsten Stelle (unsigned; bei Subtraktion heisst "
                  "C = 0 „geborgt“), V = Overflow für signed.")

    def sk_rechnen(self, w, v):
        bits = int((v or "4 Bit").split()[0])
        a, b = bitmuster(w["a"], bits, "A"), bitmuster(w["b"], bits, "B")
        sub = w["art"] == "A − B"
        return {"bits": bits, "a": a, "b": b, "sub": sub, **sm.ripple(a, b, bits, sub)}

    def sk_info(self, w, e, v):
        bits, a, b, sub = e["bits"], e["a"], e["b"], e["sub"]
        sa = a - 2 ** bits if a >> (bits - 1) else a
        sb = b - 2 ** bits if b >> (bits - 1) else b
        op = "−" if sub else "+"
        richtig_u = a - b if sub else a + b
        zeilen = [f"{format(a, f'0{bits}b')} {op} {format(b, f'0{bits}b')} = {format(e['summe'], f'0{bits}b')}"
                  f"   (C = {e['carry']}, V = {e['overflow']})",
                  f"unsigned: {a} {op} {b} = {e['summe']}" +
                  ("" if 0 <= richtig_u < 2 ** bits else f"   ✗ (richtig {richtig_u} – passt nicht)"),
                  f"signed:   {sa} {op} {sb} = {e['signed']}" +
                  (f"   ✗ Overflow (richtig {sa - sb if sub else sa + sb})" if e["overflow"] else "   ✓")]
        if sub:
            zeilen.append(f"gerechnet als A + ¬B + 1 = {format(a, f'0{bits}b')} + {format(~b & (2 ** bits - 1), f'0{bits}b')} + 1")
        lauf = sm.laufzeit(bits, 10e-9)
        zeilen.append(f"Laufzeit bei 10 ns pro Stufe: bis {fmt(lauf['t_ges'], 'zeit', 3)} (Übertrag durch {bits} Stufen)")
        return zeilen, (WARN if e["overflow"] else config.FARBEN["akzent"])

    def sk_zeichnen(self, p, w, e, v):
        L = _Leinwand(p, teiler=16 if e["bits"] == 4 else 20)
        c, wb, h, bits = L.c, L.w, L.h, e["bits"]
        breite = wb * 0.8 / bits
        kb, kh = breite * 0.62, h * 0.3
        y0 = h * 0.4
        for i, (a, b, c_ein, s, c_aus) in enumerate(e["stufen"]):
            x = wb * 0.13 + (bits - 1 - i) * breite                 # LSB rechts
            c.create_rectangle(x, y0, x + kb, y0 + kh, outline=L.text, width=L.dick)
            c.create_text(x + kb / 2, y0 + kh / 2, text="VA", fill=L.leise, font=L.fett)
            for dx, name, wert, hoch in ((0.3, "A", a, 0.24), (0.7, "B", b, 0.12)):   # A höher als B: keine Überlappung
                xx = x + kb * dx
                c.create_line(xx, y0 - h * hoch, xx, y0, fill=_wert_farbe(wert), width=L.dick)
                c.create_text(xx, y0 - h * hoch - 1, text=f"{name}{i}={wert}", anchor="s", fill=_wert_farbe(wert), font=L.klein)
            c.create_line(x + kb / 2, y0 + kh, x + kb / 2, y0 + kh + h * 0.12, fill=_wert_farbe(s), width=L.dick)
            c.create_text(x + kb / 2, y0 + kh + h * 0.13, text=f"S{i}={s}", anchor="n", fill=_wert_farbe(s), font=L.fett)
            ym = y0 + kh / 2                                        # Übertrag nach links
            c.create_line(x, ym, x - (breite - kb), ym, fill=_wert_farbe(c_aus), width=L.dick + 1, arrow="last",
                          arrowshape=(8, 10, 4))
            if i == bits - 1:
                c.create_text(x - (breite - kb) / 2, ym - 5, text=f"C={c_aus}", anchor="s", fill=_wert_farbe(c_aus), font=L.fett)
            if i == 0:
                c.create_line(x + kb + (breite - kb) * 0.8, ym, x + kb, ym, fill=_wert_farbe(c_ein), width=L.dick + 1,
                              arrow="last", arrowshape=(8, 10, 4))
                c.create_text(x + kb + 2, ym - 4, text=f"C_ein={c_ein}", anchor="sw", fill=_wert_farbe(c_ein), font=L.klein)


# =============================================================================
# MULTIPLEXER / DEMULTIPLEXER
# =============================================================================
class MuxKarte(SchaltungsModell):
    TITEL = "🔀 Multiplexer und Demultiplexer (interaktiv)"
    UNTERTITEL = "Eingänge und Auswahl S1 S0 schalten – der aktive Datenweg ist grün"
    VARIANTEN = ["MUX 4:1", "DEMUX 1:4"]
    SCHALTER = [("d0", "D0 = 1"), ("d1", "D1 = 1"), ("d2", "D2 = 1"), ("d3", "D3 = 1"), ("x", "X = 1 (DEMUX)"),
                ("s1", "S1 = 1"), ("s0", "S0 = 1")]
    STARTWERTE = {"MUX 4:1": {"d1": True, "d2": True, "s1": True}, "DEMUX 1:4": {"x": True, "s1": True}}
    SEITENVERHAELTNIS = 0.42
    MAX_HOEHE = 340
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Der Multiplexer ist ein digital gesteuerter Umschalter: Die Auswahleingänge "
                  "(Binärzahl S1 S0) bestimmen, welcher Dateneingang zum Ausgang durchgeschaltet wird – "
                  "Y = ¬S1·¬S0·D0 + ¬S1·S0·D1 + S1·¬S0·D2 + S1·S0·D3. Der Demultiplexer macht das Umgekehrte: ein "
                  "Eingang wird auf einen von vier Ausgängen verteilt. Anwendungen: mehrere Sensoren an einen ADC "
                  "(Analog-MUX), Bus-Auswahl, Zeitmultiplex. Ein 2^n:1-MUX kann ausserdem JEDE Logikfunktion mit n + 1 "
                  "Variablen bilden.")

    def sk_rechnen(self, w, v):
        d = [int(bool(w[f"d{k}"])) for k in range(4)]
        s1, s0, x = int(bool(w["s1"])), int(bool(w["s0"])), int(bool(w["x"]))
        s = s1 * 2 + s0
        mux = v != "DEMUX 1:4"
        return {"mux": mux, "d": d, "s1": s1, "s0": s0, "s": s, "x": x,
                "y": sm.mux(d, s) if mux else None, "ys": None if mux else sm.demux(x, s, 4)}

    def sk_info(self, w, e, v):
        if e["mux"]:
            return [f"S1 S0 = {e['s1']}{e['s0']} = {e['s']}  →  Y = D{e['s']} = {e['y']}",
                    "Y = ¬S1·¬S0·D0 + ¬S1·S0·D1 + S1·¬S0·D2 + S1·S0·D3"], config.FARBEN["akzent"]
        return [f"S1 S0 = {e['s1']}{e['s0']} = {e['s']}  →  Y{e['s']} = X = {e['x']}, alle anderen 0",
                "Y0 Y1 Y2 Y3 = " + " ".join(map(str, e["ys"]))], config.FARBEN["akzent"]

    def sk_zeichnen(self, p, w, e, v):
        L = _Leinwand(p, teiler=15)
        c, wb, h = L.c, L.w, L.h
        mux, s = e["mux"], e["s"]
        x0, x1 = wb * 0.38, wb * 0.58
        y0, y1 = h * 0.08, h * 0.78
        schraeg = (y1 - y0) * 0.16
        if mux:                                                     # Trapez: links hoch, rechts niedrig
            punkte = (x0, y0, x1, y0 + schraeg, x1, y1 - schraeg, x0, y1)
        else:
            punkte = (x0, y0 + schraeg, x1, y0, x1, y1, x0, y1 - schraeg)
        c.create_polygon(*punkte, outline=L.text, fill="", width=L.dick)
        c.create_text((x0 + x1) / 2, y0 + h * 0.2, text="MUX" if mux else "DEMUX", fill=L.leise, font=L.fett)
        ys = [y0 + (y1 - y0) * (k + 0.9) / 4.6 + h * 0.05 for k in range(4)]
        ym = (y0 + y1) / 2
        for k, yy in enumerate(ys):
            if mux:
                farbe = _wert_farbe(e["d"][k])
                c.create_line(wb * 0.18, yy, x0, yy, fill=farbe, width=L.dick)
                c.create_text(wb * 0.17, yy, text=f"D{k}={e['d'][k]}", anchor="e", fill=farbe, font=L.schrift)
            else:
                wert = e["x"] if k == s else 0
                c.create_line(x1, yy, wb * 0.78, yy, fill=_wert_farbe(wert), width=L.dick)
                c.create_text(wb * 0.79, yy, text=f"Y{k}={wert}", anchor="w", fill=_wert_farbe(wert), font=L.schrift)
        if mux:                                                     # Datenweg im Inneren
            y = e["y"]
            c.create_line(x0, ys[s], x1, ym, fill=EINS if y else ORANGE, width=L.dick + 1, dash=(6, 3))
            c.create_line(x1, ym, wb * 0.78, ym, fill=_wert_farbe(y), width=L.dick)
            c.create_text(wb * 0.79, ym, text=f"Y={y}", anchor="w", fill=_wert_farbe(y), font=L.fett)
        else:
            c.create_line(wb * 0.18, ym, x0, ym, fill=_wert_farbe(e["x"]), width=L.dick)
            c.create_text(wb * 0.17, ym, text=f"X={e['x']}", anchor="e", fill=_wert_farbe(e["x"]), font=L.fett)
            c.create_line(x0, ym, x1, ys[s], fill=EINS if e["x"] else ORANGE, width=L.dick + 1, dash=(6, 3))
        for i, (name, wert) in enumerate((("S1", e["s1"]), ("S0", e["s0"]))):           # Auswahlleitungen unten
            xx = x0 + (x1 - x0) * (0.35 + 0.35 * i)
            unten = y1 - schraeg * (0.35 + 0.35 * i) * (1 if mux else 0) - (0 if mux else schraeg * (0.65 - 0.35 * i))
            c.create_line(xx, h * 0.95, xx, unten, fill=_wert_farbe(wert), width=L.dick)
            c.create_text(xx + (-4 if i == 0 else 4), h * 0.93, text=f"{name}={wert}", anchor="e" if i == 0 else "w",
                          fill=_wert_farbe(wert), font=L.klein)


# =============================================================================
# DECODER / ENCODER / 7-SEGMENT
# =============================================================================
class DecoderKarte(SchaltungsModell):
    TITEL = "🔢 Decoder, Encoder und 7-Segment-Anzeige (interaktiv)"
    UNTERTITEL = "Eingänge einstellen – welcher Ausgang wird aktiv?"
    VARIANTEN = ["Decoder 3:8 (74HC138)", "Prioritäts-Encoder 8:3", "7-Segment-Decoder"]
    REGLER = [("adr", "Adresse A2 A1 A0 (Decoder)", "zahl", 0.0, 7.0, 5.0, {"ganzzahl": True}),
              ("ziffer", "Ziffer (7-Segment)", "zahl", 0.0, 15.0, 7.0, {"ganzzahl": True})]
    SCHALTER = [("frei", "Freigabe E (Decoder)")]
    STARTWERTE = {"Decoder 3:8 (74HC138)": {"frei": True}}
    AUSWAHL = [("anode", "Anzeige (7-Segment)", ["gemeinsame Kathode", "gemeinsame Anode"], "gemeinsame Kathode")]
    TEXTFELDER = [("ein", "Eingänge I7 … I0 (Encoder)", "0010 0100", {"max": 20, "platzhalter": "8 Bit, z.B. 0010 0100"})]
    SEITENVERHAELTNIS = 0.36
    MAX_HOEHE = 320
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Ein DECODER macht aus einer Binärzahl mit n Bit genau EINEN aktiven von 2^n "
                  "Ausgängen (1-aus-n) – z.B. um einen von acht Speicherbausteinen auszuwählen. Der 74HC138 hat "
                  "Ausgänge, die bei Aktivität LOW werden (¬Y), und einen Freigabe-Eingang. Ein ENCODER macht das "
                  "Umgekehrte; der Prioritäts-Encoder meldet den HÖCHSTEN aktiven Eingang (Tastatur, "
                  "Interrupt-Prioritäten) und mit GS, ob überhaupt einer aktiv ist. Der 7-Segment-Decoder (z.B. "
                  "74HC4511) schaltet für jede Ziffer die passenden Segmente a … g.")

    def sk_rechnen(self, w, v):
        art = self.VARIANTEN.index(v) if v in self.VARIANTEN else 0
        e = {"art": art, "adr": round(w["adr"]), "frei": int(bool(w["frei"])), "ziffer": round(w["ziffer"])}
        if art == 0:
            e["pegel"] = sm.decoder(e["adr"], 3, bool(e["frei"]))
        elif art == 1:
            e["ein"] = bitmuster(w["ein"], 8, "Eingänge I7 … I0")
            e["code"], e["gs"] = sm.prioritaets_encoder([(e["ein"] >> k) & 1 for k in range(8)])
        else:
            e["anode"] = w["anode"] == "gemeinsame Anode"
            e["seg"] = sm.siebensegment(e["ziffer"], e["anode"])
        return e

    def sk_info(self, w, e, v):
        if e["art"] == 0:
            return [f"Adresse {format(e['adr'], '03b')} = {e['adr']}  →  " +
                    (f"¬Y{e['adr']} = 0 (aktiv), alle anderen 1" if e["frei"] else "gesperrt: alle ¬Y = 1"),
                    "¬Y7 … ¬Y0 = " + " ".join(str(x) for x in reversed(e["pegel"]))], config.FARBEN["akzent"]
        if e["art"] == 1:
            return [f"höchster aktiver Eingang: I{e['code']}  →  A2 A1 A0 = {format(e['code'], '03b')}   GS = {e['gs']}"
                    if e["gs"] else "kein Eingang aktiv  →  GS = 0 (Code ungültig)",
                    "niedrigere aktive Eingänge werden ignoriert (Priorität)"], config.FARBEN["akzent"]
        s = e["seg"]
        return [f"Ziffer {e['ziffer']:X}  →  Segmente an: {' '.join(s['segmente'])}",
                "Pegel a … g = " + " ".join(str(s["pegel"][x]) for x in "abcdefg") +
                ("   (LOW = Segment an)" if e["anode"] else "   (HIGH = Segment an)")], config.FARBEN["akzent"]

    def sk_zeichnen(self, p, w, e, v):
        L = _Leinwand(p, teiler=15)
        c, wb, h = L.c, L.w, L.h
        if e["art"] == 2:
            self._siebensegment(L, e)
            return
        x0, x1, y0, y1 = wb * 0.36, wb * 0.56, h * 0.06, h * 0.94
        c.create_rectangle(x0, y0, x1, y1, outline=L.text, width=L.dick)
        c.create_text((x0 + x1) / 2, y0 + h * 0.08, text="138" if e["art"] == 0 else "148", fill=L.leise, font=L.fett)
        r = max(4, h * 0.03)
        if e["art"] == 0:
            for i in range(3):
                bit = (e["adr"] >> (2 - i)) & 1
                y = y0 + (y1 - y0) * (i + 1.5) / 5
                c.create_line(wb * 0.2, y, x0, y, fill=_wert_farbe(bit), width=L.dick)
                c.create_text(wb * 0.19, y, text=f"A{2 - i}={bit}", anchor="e", fill=_wert_farbe(bit), font=L.schrift)
            y = y0 + (y1 - y0) * 4.3 / 5
            c.create_line(wb * 0.2, y, x0, y, fill=_wert_farbe(e["frei"]), width=L.dick)
            c.create_text(wb * 0.19, y, text=f"E={e['frei']}", anchor="e", fill=_wert_farbe(e["frei"]), font=L.schrift)
            for k in range(8):
                y = y0 + (y1 - y0) * (k + 0.8) / 8.6
                aktiv = e["pegel"][k] == 0
                c.create_oval(x1, y - r, x1 + 2 * r, y + r, outline=L.text, width=L.dick)   # Negation
                farbe = ORANGE if aktiv else NULL_FARBE
                c.create_line(x1 + 2 * r, y, wb * 0.74, y, fill=farbe, width=L.dick)
                c.create_text(wb * 0.75, y, text=f"¬Y{k}={e['pegel'][k]}" + ("  ◀ aktiv" if aktiv else ""), anchor="w",
                              fill=farbe, font=L.klein)
        else:
            code, gs = e["code"], e["gs"]
            for k in range(8):
                bit = (e["ein"] >> k) & 1
                y = y0 + (y1 - y0) * (k + 0.8) / 8.6
                farbe = EINS if (bit and k == code and gs) else _wert_farbe(bit)
                c.create_line(wb * 0.2, y, x0, y, fill=farbe, width=L.dick + (1 if k == code and gs else 0))
                c.create_text(wb * 0.19, y, text=f"I{k}={bit}", anchor="e", fill=farbe, font=L.klein)
            for i, (name, wert) in enumerate((("A2", code >> 2 & 1), ("A1", code >> 1 & 1), ("A0", code & 1), ("GS", gs))):
                y = y0 + (y1 - y0) * (i + 1.2) / 5
                c.create_line(x1, y, wb * 0.74, y, fill=_wert_farbe(wert), width=L.dick)
                c.create_text(wb * 0.75, y, text=f"{name}={wert}", anchor="w", fill=_wert_farbe(wert), font=L.schrift)

    @staticmethod
    def _siebensegment(L, e):
        c, wb, h, s = L.c, L.w, L.h, e["seg"]
        bx, by, bb, bh = wb * 0.42, h * 0.14, min(wb * 0.16, h * 0.4), h * 0.72
        d = max(4, bb * 0.14)
        an_farbe, aus_farbe = "#EF4444", farbe_waehlen(("#E5E7EB", "#2A2E36"), L.dunkel)
        lage = {"a": (bx, by, bx + bb, by), "g": (bx, by + bh / 2, bx + bb, by + bh / 2), "d": (bx, by + bh, bx + bb, by + bh),
                "f": (bx, by, bx, by + bh / 2), "b": (bx + bb, by, bx + bb, by + bh / 2),
                "e": (bx, by + bh / 2, bx, by + bh), "c": (bx + bb, by + bh / 2, bx + bb, by + bh)}
        for seg, (xa, ya, xe, ye) in lage.items():
            an = seg in s["segmente"]
            c.create_line(xa + (d if xa != xe else 0), ya + (d if ya != ye else 0),
                          xe - (d if xa != xe else 0), ye - (d if ya != ye else 0),
                          fill=an_farbe if an else aus_farbe, width=d * 1.4, capstyle="round")
            mx, my = (xa + xe) / 2, (ya + ye) / 2
            dx = -d * 1.6 if seg in "fe" else (d * 1.6 if seg in "bc" else 0)
            dy = -d * 1.6 if seg == "a" else (d * 1.6 if seg == "d" else (-d * 1.2 if seg == "g" else 0))
            c.create_text(mx + dx, my + dy, text=seg, fill=L.leise, font=L.klein)
        c.create_text(wb * 0.12, h * 0.5, text=f"{e['ziffer']:X}", fill=L.text, font=(config.SCHRIFT, int(h * 0.35), "bold"))
        for i, seg in enumerate("abcdefg"):
            an = seg in s["segmente"]
            c.create_text(wb * 0.7, h * 0.12 + i * h * 0.11, text=f"{seg} = {s['pegel'][seg]}" + ("  an" if an else ""),
                          anchor="w", fill=an_farbe if an else L.leise, font=L.schrift)


# =============================================================================
# AUSGANGSTYPEN
# =============================================================================
class AusgangKarte(SchaltungsModell):
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
