# =============================================================================
# digitaltechnik/grafiken_busse.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE für serielle Busse und Speicher (mit Zeitdiagrammen):
#
#   UartKarte      Zeichen/Byte eingeben -> UART-Rahmen (Start, Daten LSB zuerst, Parität, Stopp), TTL und RS-232
#   SpiKarte       Modus 0 … 3, MOSI- und MISO-Byte -> CS, SCLK, MOSI, MISO mit Abtastflanken
#   I2cKarte       Adresse, schreiben/lesen, Daten -> START, Adresse, R/W, ACK, Daten, STOP auf SDA/SCL
#   SpeicherKarte  kleiner Speicherbaustein: Adresse wählen, lesen und schreiben, Steuersignale CS/OE/WE
#
# Rechnung: digitaltechnik/busse_mathe.py
# Zeitdiagramm: zeitdiagramm() aus digitaltechnik/grafiken_schaltwerke.py (wiederverwendet)
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_uart")
# Eigene Namen beginnen mit dg_ (keine Kollision mit tkinter).
# =============================================================================

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile.grafiken.schaltplan import OK                            # -> bauteile/grafiken/schaltplan.py
from bauteile.rechner.basis import Auswahl, WertRegler                 # -> bauteile/rechner/basis.py
from core.layout import Karte, ResponsiveCanvas                        # -> core/layout.py
from digitaltechnik import busse_mathe as bm                           # -> digitaltechnik/busse_mathe.py
from digitaltechnik.grafiken import FEHLER, _erklaerung, _ergebnis_label, _farbe   # -> digitaltechnik/grafiken.py
from digitaltechnik.grafiken_schaltwerke import (EINS, ORANGE, BLAU, ROT,   # -> digitaltechnik/grafiken_schaltwerke.py
                                                 SIGNAL_FARBEN, zeitdiagramm)

LILA, GRUEN = "#A855F7", "#22C55E"
TEIL_FARBEN = {"Start": ORANGE, "P": LILA, "Stop": GRUEN}             # UART-Rahmen
SENDER_FARBEN = {"Master": BLAU, "Slave": ORANGE}                     # I²C: wer treibt SDA?


def _feld(master, start, breite, bei_enter):
    """Eingabefeld: Enter oder Verlassen übernimmt."""
    feld = ctk.CTkEntry(master, width=breite, font=(config.SCHRIFT_CODE, 14))
    feld.insert(0, start)
    feld.bind("<Return>", lambda _e: bei_enter())
    feld.bind("<FocusOut>", lambda _e: bei_enter())
    return feld


def _beschriftung(master, text):
    return ctk.CTkLabel(master, text=text, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"])


def _neu_zeichnen(karte):
    w, h = karte.dg_canvas.winfo_width(), karte.dg_canvas.winfo_height()
    if w > 1:
        karte.dg_canvas.delete("all")
        karte._dg_zeichnen(karte.dg_canvas, w, h)


def _hex(wert, bits=8):
    return f"0x{wert:0{max(1, (bits + 3) // 4)}X}"


def _zeichen(wert):
    return f"'{chr(wert)}'" if 32 <= wert < 127 else "(nicht druckbar)"


# =============================================================================
# UART
# =============================================================================
class UartKarte(Karte):
    def __init__(self, master):
        super().__init__(master, titel="📨 UART-Rahmen (interaktiv)",
                         untertitel="Zeichen oder Zahl eingeben (z.B. A, 0x41, 65) + Enter, Format wählen")
        b = self.body
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        _beschriftung(oben, "Daten").grid(row=0, column=0, padx=(0, 6))
        self.dg_feld = _feld(oben, "A", 110, self._dg_neu)
        self.dg_feld.grid(row=0, column=1, padx=(0, 12), pady=2)
        _beschriftung(oben, "Baudrate").grid(row=0, column=2, padx=(0, 6))
        self.dg_baud = Auswahl(oben, [str(b_) for b_ in bm.BAUDRATEN], "9600", breite=110, bei_aenderung=self._dg_neu)
        self.dg_baud.grid(row=0, column=3, pady=2)
        format_zeile = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        format_zeile.grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.dg_datenbits = ctk.CTkSegmentedButton(format_zeile, values=["7 Bit", "8 Bit"], command=lambda _v: self._dg_neu())
        self.dg_datenbits.set("8 Bit")
        self.dg_datenbits.grid(row=0, column=0, padx=(0, 10), pady=2)
        self.dg_paritaet = ctk.CTkSegmentedButton(format_zeile, values=bm.PARITAETEN, command=lambda _v: self._dg_neu())
        self.dg_paritaet.set("keine")
        self.dg_paritaet.grid(row=0, column=1, padx=(0, 10), pady=2)
        self.dg_stopbits = ctk.CTkSegmentedButton(format_zeile, values=["1 Stopp", "2 Stopp"], command=lambda _v: self._dg_neu())
        self.dg_stopbits.set("1 Stopp")
        self.dg_stopbits.grid(row=0, column=2, pady=2)
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.42, max_hoehe=320)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  UART überträgt ohne Taktleitung: Beide Seiten müssen dieselbe "
                       "Baudrate und dasselbe Format (z.B. 8N1) kennen. In Ruhe ist die Leitung HIGH. Das STARTBIT (0) "
                       "kündigt ein Zeichen an; der Empfänger startet mit dieser Flanke seine Uhr und tastet jedes Bit "
                       "in der Mitte ab (Punkte). Die Daten kommen mit dem NIEDRIGSTEN Bit zuerst, danach optional das "
                       "Paritätsbit und das STOPPBIT (1). RS-232 überträgt dasselbe mit umgekehrten Pegeln: logisch 1 "
                       "ist −3 … −15 V, logisch 0 ist +3 … +15 V (Pegelwandler z.B. MAX232).").grid(
            row=4, column=0, sticky="ew", pady=(8, 0))
        self.dg_d = None
        self._dg_neu()

    def _dg_format(self):
        return (int(self.dg_datenbits.get().split()[0]), self.dg_paritaet.get(),
                int(self.dg_stopbits.get().split()[0]))

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        datenbits, paritaet, stopbits = self._dg_format()
        baud = int(self.dg_baud.get())
        try:
            wert = bm.byte_einlesen(self.dg_feld.get(), datenbits)
        except ValueError as fehler:
            self.dg_ergebnis.configure(text=f"⚠ {fehler}", text_color=FEHLER)
            self.dg_d = None
            _neu_zeichnen(self)
            return
        bits = bm.uart_rahmen(wert, datenbits, paritaet, stopbits)
        t = bm.uart_timing(baud, datenbits, paritaet, stopbits)
        self.dg_d = {"bits": bits, "t": t, "baud": baud}
        gesendet = " ".join(str(b) for _n, b in bits)
        zeilen = [f"{wert} = {_hex(wert)} = 0b{wert:0{datenbits}b}  {_zeichen(wert)}   ·   Format "
                  f"{bm.uart_format(datenbits, paritaet, stopbits)}",
                  f"auf der Leitung (LSB zuerst): {gesendet}"]
        p = bm.paritaetsbit(wert, paritaet)
        if p is not None:
            zeilen.append(f"Parität {paritaet.split()[0]}: {bin(wert).count('1')} Einsen in den Daten → P = {p}")
        zeilen.append(f"t_bit = 1 / {baud} Bd = {t['t_bit'] * 1e6:.2f} µs   ·   Rahmen {t['rahmen_bits']} Bit = "
                      f"{t['t_rahmen'] * 1e3:.3f} ms   ·   max. {t['bytes_s']:.0f} Zeichen/s")
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
        _neu_zeichnen(self)

    def _dg_zeichnen(self, c, w, h):
        d = self.dg_d
        if d is None:
            return
        text, leise = _farbe(config.FARBEN["text"]), _farbe(config.FARBEN["text_leise"])
        g = max(7, int(min(w / 2.2, h) / 17))
        schrift, fett = (config.SCHRIFT, g), (config.SCHRIFT, g, "bold")
        bits = d["bits"]
        ruhe = 1.2                                                     # Ruhezeit vor und nach dem Rahmen (in Bitzeiten)
        x0, x1 = w * 0.15, w * 0.98
        dx = (x1 - x0) / (len(bits) + 2 * ruhe)
        xs = x0 + ruhe * dx                                            # Beginn des Startbits
        kurz = dx < g * 3.2                                            # schmale Zellen: kurze Namen
        zeilen = [("TX (TTL)", h * 0.30, h * 0.50, False, "3.3 V", "0 V"),
                  ("RS-232", h * 0.66, h * 0.86, True, "+12 V", "−12 V")]
        # ---- Bitnamen und Werte oben ----
        for i, (name, wert) in enumerate(bits):
            farbe = TEIL_FARBEN.get(name, BLAU)
            xa = xs + i * dx
            c.create_rectangle(xa + 1, h * 0.04, xa + dx - 1, h * 0.22, outline=farbe)
            beschr = name
            if kurz:
                beschr = {"Start": "St", "Stop": "Sp"}.get(name, name.lstrip("D"))
            c.create_text(xa + dx / 2, h * 0.09, text=beschr, fill=farbe, font=schrift)
            c.create_text(xa + dx / 2, h * 0.17, text=str(wert), fill=text, font=fett)
        # ---- Leitungen ----
        for name, oben, unten, invertiert, pegel_oben, pegel_unten in zeilen:
            c.create_text(x0 - 6, (oben + unten) / 2, text=name, anchor="e", fill=text, font=schrift)
            c.create_text(x0 - 6, oben, text=pegel_oben, anchor="e", fill=leise, font=(config.SCHRIFT, max(6, g - 2)))
            c.create_text(x0 - 6, unten, text=pegel_unten, anchor="e", fill=leise, font=(config.SCHRIFT, max(6, g - 2)))
            werte = [1] + [b for _n, b in bits] + [1]
            grenzen = [x0, xs] + [xs + (i + 1) * dx for i in range(len(bits))] + [x1]
            punkte = []
            for k, wert in enumerate(werte):
                pegel = wert ^ invertiert
                y = oben if pegel else unten
                punkte += [grenzen[k], y, grenzen[k + 1], y]
            c.create_line(*punkte, fill=EINS if not invertiert else ORANGE, width=2)
            if not invertiert:                                         # Abtastpunkte in der Bitmitte
                r = max(2.5, g * 0.3)
                for i, (_n, wert) in enumerate(bits):
                    xm, y = xs + (i + 0.5) * dx, oben if wert else unten
                    c.create_oval(xm - r, y - r, xm + r, y + r, fill=ROT, outline="")
        # ---- Zeitachse ----
        y = h * 0.95
        c.create_text(xs, y, text="0", fill=leise, font=schrift)
        c.create_text(xs + len(bits) * dx, y, text=f"{d['t']['t_rahmen'] * 1e3:.3f} ms", fill=leise, font=schrift,
                      anchor="e")
        c.create_line(xs, h * 0.04, xs, h * 0.90, fill=leise, dash=(2, 3))


# =============================================================================
# SPI
# =============================================================================
class SpiKarte(Karte):
    MODI = ["Modus 0", "Modus 1", "Modus 2", "Modus 3"]

    def __init__(self, master):
        super().__init__(master, titel="🔁 SPI-Übertragung (interaktiv)",
                         untertitel="Modus wählen, MOSI- und MISO-Byte eingeben – Master und Slave tauschen ihre Bytes")
        b = self.body
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        self.dg_modus = ctk.CTkSegmentedButton(oben, values=self.MODI, command=lambda _v: self._dg_neu())
        self.dg_modus.set(self.MODI[0])
        self.dg_modus.grid(row=0, column=0, columnspan=4, sticky="w", pady=2)
        _beschriftung(oben, "MOSI").grid(row=1, column=0, padx=(0, 6), pady=(6, 0))
        self.dg_mosi = _feld(oben, "0xA5", 90, self._dg_neu)
        self.dg_mosi.grid(row=1, column=1, padx=(0, 12), pady=(6, 0))
        _beschriftung(oben, "MISO").grid(row=1, column=2, padx=(0, 6), pady=(6, 0))
        self.dg_miso = _feld(oben, "0x3C", 90, self._dg_neu)
        self.dg_miso.grid(row=1, column=3, padx=(0, 12), pady=(6, 0))
        self.dg_reihenfolge = ctk.CTkSegmentedButton(oben, values=["MSB zuerst", "LSB zuerst"],
                                                     command=lambda _v: self._dg_neu())
        self.dg_reihenfolge.set("MSB zuerst")
        self.dg_reihenfolge.grid(row=1, column=4, pady=(6, 0))
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.46, max_hoehe=340)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  SPI hat eine Taktleitung (SCLK) vom Master und zwei Datenleitungen: "
                       "MOSI (Master → Slave) und MISO (Slave → Master). Mit CS = 0 wählt der Master EINEN Slave aus; "
                       "nicht gewählte Slaves schalten MISO hochohmig (Mittellinie). Bei jedem Takt wandert ein Bit in "
                       "beide Richtungen – Master und Slave tauschen den Inhalt ihrer Schieberegister. CPOL legt den "
                       "Ruhepegel von SCLK fest, CPHA, ob an der ersten (0) oder zweiten (1) Flanke abgetastet wird "
                       "(orange Linien). Beide Seiten müssen denselben Modus verwenden – sonst ist jedes Bit um eine "
                       "halbe Periode verschoben.").grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self.dg_d = None
        self._dg_neu()

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        modus = self.MODI.index(self.dg_modus.get())
        msb = self.dg_reihenfolge.get().startswith("MSB")
        try:
            mosi = bm.byte_einlesen(self.dg_mosi.get())
            miso = bm.byte_einlesen(self.dg_miso.get())
        except ValueError as fehler:
            self.dg_ergebnis.configure(text=f"⚠ {fehler}", text_color=FEHLER)
            self.dg_d = None
            _neu_zeichnen(self)
            return
        self.dg_d = d = bm.spi_signale(mosi, miso, modus, msb_zuerst=msb)
        zeilen = [f"Modus {modus}: CPOL = {d['cpol']}, CPHA = {d['cpha']}  →  SCLK in Ruhe "
                  f"{'HIGH' if d['ruhe'] else 'LOW'}, abtasten an der {d['abtast']}en Flanke, "
                  f"Daten wechseln an der {d['schiebe']}en",
                  f"Master sendet {_hex(mosi)} = 0b{mosi:08b} und empfängt {_hex(miso)} = 0b{miso:08b}  "
                  f"({'MSB' if msb else 'LSB'} zuerst)",
                  "8 Takte = 1 Byte in jede Richtung (Vollduplex) – kein Adressbyte, kein ACK"]
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
        _neu_zeichnen(self)

    def _dg_zeichnen(self, c, w, h):
        d = self.dg_d
        if d is None:
            return
        text, leise = _farbe(config.FARBEN["text"]), _farbe(config.FARBEN["text_leise"])
        g = max(7, int(min(w / 2.2, h) / 17))
        schrift = (config.SCHRIFT, g)
        signale = [("CS", d["CS"], ROT), ("SCLK", d["SCLK"], SIGNAL_FARBEN["CLK"]),
                   ("MOSI", d["MOSI"], BLAU), ("MISO", d["MISO"], ORANGE)]
        x0, x1, y0, y1 = w * 0.11, w * 0.98, h * 0.12, h * 0.98
        zeitdiagramm(c, x0, x1, y0, y1, signale, schrift, leise, [(s, ORANGE) for s in d["flanken"]])
        dx = (x1 - x0) / len(d["CS"])
        for schritt, name in d["bits"]:                                # Bitnummer über jedem Bit
            c.create_text(x0 + (schritt + 1) * dx, y0 - 3, text=name if dx > g * 1.6 else name[1:], anchor="s",
                          fill=text, font=schrift)


# =============================================================================
# I²C
# =============================================================================
class I2cKarte(Karte):
    KURZ = {"START": "S", "STOP": "P", "ACK": "A", "NACK": "N", "R/W": "R/W", "Sr": "Sr"}

    def __init__(self, master):
        super().__init__(master, titel="🔗 I²C-Übertragung (interaktiv)",
                         untertitel="Adresse, Richtung und Daten wählen – blau sendet der Master, orange der Slave")
        b = self.body
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        self.dg_art = ctk.CTkSegmentedButton(oben, values=bm.I2C_ARTEN, command=lambda _v: self._dg_neu())
        self.dg_art.set(bm.I2C_ARTEN[0])
        self.dg_art.grid(row=0, column=0, columnspan=4, sticky="w", pady=2)
        self.dg_da = ctk.CTkSegmentedButton(oben, values=["Slave antwortet", "kein Slave"], command=lambda _v: self._dg_neu())
        self.dg_da.set("Slave antwortet")
        self.dg_da.grid(row=0, column=4, columnspan=2, sticky="w", padx=(12, 0), pady=2)
        _beschriftung(oben, "Adresse").grid(row=1, column=0, padx=(0, 6), pady=(6, 0))
        self.dg_adresse = _feld(oben, "0x48", 80, self._dg_neu)
        self.dg_adresse.grid(row=1, column=1, padx=(0, 12), pady=(6, 0))
        self.dg_reg_text = _beschriftung(oben, "Register")
        self.dg_reg_text.grid(row=1, column=2, padx=(0, 6), pady=(6, 0))
        self.dg_register = _feld(oben, "0x00", 70, self._dg_neu)
        self.dg_register.grid(row=1, column=3, padx=(0, 12), pady=(6, 0))
        _beschriftung(oben, "Daten").grid(row=1, column=4, padx=(0, 6), pady=(6, 0))
        self.dg_daten = _feld(oben, "0x12", 130, self._dg_neu)
        self.dg_daten.grid(row=1, column=5, pady=(6, 0))
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.36, max_hoehe=280)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  I²C braucht nur zwei Leitungen (SDA Daten, SCL Takt), beide Open "
                       "Drain mit Pull-up: Jeder darf nur nach LOW ziehen. Normalerweise ändert sich SDA nur, wenn "
                       "SCL = 0 ist. Zwei Ausnahmen markieren Anfang und Ende: START (SDA fällt bei SCL = 1) und STOP "
                       "(SDA steigt bei SCL = 1). Nach dem START sendet der Master die 7-Bit-Adresse und das R/W-Bit "
                       "(0 = schreiben, 1 = lesen). Nach jedem Byte bestätigt der Empfänger im 9. Takt mit ACK (SDA = "
                       "0). Meldet sich niemand, bleibt SDA durch den Pull-up HIGH = NACK. „Register lesen“: erst die "
                       "Registernummer schreiben, dann mit wiederholtem START (Sr) lesen.").grid(
            row=4, column=0, sticky="ew", pady=(8, 0))
        self.dg_d = None
        self._dg_neu()

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        art = self.dg_art.get()
        if art == "Register lesen":
            self.dg_reg_text.grid()
            self.dg_register.grid()
        else:
            self.dg_reg_text.grid_remove()
            self.dg_register.grid_remove()
        slave_da = self.dg_da.get() == "Slave antwortet"
        try:
            adresse = bm.byte_einlesen(self.dg_adresse.get(), 7)
            daten = [bm.byte_einlesen(t) for t in self.dg_daten.get().replace(",", " ").split()]
            if not 1 <= len(daten) <= 3:
                raise ValueError("1 bis 3 Datenbytes eingeben, getrennt mit Leerzeichen (z.B. 0x12 0x34)")
            register = bm.byte_einlesen(self.dg_register.get()) if art == "Register lesen" else None
            teile = bm.i2c_rahmen(adresse, art == "lesen", daten, slave_da, register)
        except ValueError as fehler:
            self.dg_ergebnis.configure(text=f"⚠ {fehler}", text_color=FEHLER)
            self.dg_d = None
            _neu_zeichnen(self)
            return
        self.dg_d = {"teile": teile, **bm.i2c_signale(teile)}
        lesen = art != "schreiben"
        adressbyte = (adresse << 1) | (1 if art == "lesen" else 0)
        zeilen = [f"Adresse 0x{adresse:02X} = 0b{adresse:07b}  →  erstes Byte 0b{adressbyte:08b} = {_hex(adressbyte)} "
                  f"({'lesen' if art == 'lesen' else 'schreiben'})"]
        if register is not None:
            zeilen[0] += f", nach Sr: {_hex(adressbyte | 1)} (lesen)"
        kette = "  ".join(self.KURZ.get(n, n.replace("Daten ", "D").replace("Adresse", f"0x{adresse:02X}")
                                         .replace("Register", _hex(register or 0)))
                          + ("" if n != "R/W" else f"={bits[0]}") for n, bits, _s in teile)
        zeilen.append("Ablauf: " + kette)
        if not slave_da:
            zeilen.append("⚠ Kein Slave mit dieser Adresse: SDA bleibt im 9. Takt HIGH (NACK) → der Master bricht mit "
                          "STOP ab (Adresse, Verdrahtung, Pull-ups prüfen)")
            farbe = FEHLER
        else:
            zeilen.append(("Master liest: Er bestätigt jedes Byte mit ACK, das letzte mit NACK (= „genug“), dann STOP"
                           if lesen else "Master schreibt: Der Slave bestätigt jedes Byte mit ACK"))
            farbe = OK
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=farbe)
        _neu_zeichnen(self)

    def _dg_zeichnen(self, c, w, h):
        d = self.dg_d
        if d is None:
            return
        leise = _farbe(config.FARBEN["text_leise"])
        g = max(7, int(min(w / 2.2, h) / 15))
        schrift = (config.SCHRIFT, g)
        klein = (config.SCHRIFT, max(6, g - 2))
        x0, x1 = w * 0.08, w * 0.99
        n = len(d["SCL"])
        dx = (x1 - x0) / n
        # ---- Abschnitte oben (wer sendet was?) ----
        for (anfang, ende, name, sender), (_n, bits, _s) in zip(d["abschnitte"], d["teile"]):
            farbe = LILA if name in ("START", "STOP", "Sr") else SENDER_FARBEN[sender]
            xa, xb = x0 + anfang * dx, x0 + ende * dx
            c.create_rectangle(xa + 0.5, h * 0.03, xb - 0.5, h * 0.20, fill=farbe, outline="")
            platz = xb - xa
            kurz = ("R" if bits[0] else "W") if name == "R/W" else self.KURZ.get(
                name, name.replace("Daten ", "D").replace("Adresse", "Adr").replace("Register", "Reg"))
            for beschr in (name, kurz):
                if len(beschr) * g * 0.75 + 4 < platz:
                    c.create_text((xa + xb) / 2, h * 0.115, text=beschr, fill="#FFFFFF", font=klein)
                    break
        # ---- SCL und SDA ----
        signale = [("SCL", d["SCL"], SIGNAL_FARBEN["CLK"]), ("SDA", d["SDA"], EINS)]
        markierungen = [(anfang + (1 if name == "START" else 3 if name == "Sr" else 2), LILA)
                        for anfang, _e, name, _s in d["abschnitte"] if name in ("START", "STOP", "Sr")]
        zeitdiagramm(c, x0, x1, h * 0.26, h * 0.98, signale, schrift, leise, markierungen)


# =============================================================================
# SPEICHER
# =============================================================================
class SpeicherKarte(Karte):
    def __init__(self, master):
        super().__init__(master, titel="🗄️ Speicherbaustein (interaktiv)",
                         untertitel="Adresse wählen, dann lesen oder einen Wert schreiben")
        b = self.body
        self.dg_inhalt, self.dg_aktion = {}, "lesen"
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        self.dg_breite = ctk.CTkSegmentedButton(oben, values=["4 Bit", "8 Bit"], command=lambda _v: self._dg_neu())
        self.dg_breite.set("8 Bit")
        self.dg_breite.grid(row=0, column=0, padx=(0, 12), pady=2)
        _beschriftung(oben, "Wert").grid(row=0, column=1, padx=(0, 6))
        self.dg_wert = _feld(oben, "0x2A", 80, lambda: None)
        self.dg_wert.grid(row=0, column=2, padx=(0, 8), pady=2)
        ctk.CTkButton(oben, text="Lesen", width=80, height=30, command=self._dg_lesen).grid(row=0, column=3, padx=(0, 8))
        ctk.CTkButton(oben, text="Schreiben", width=90, height=30, fg_color="#7C3AED", hover_color="#6D28D9",
                      command=self._dg_schreiben).grid(row=0, column=4)
        self.dg_adressbits = WertRegler(b, "Adressbits a", "zahl", 2, 8, 4, ganzzahl=True,
                                        bei_aenderung=self._dg_adressbits_neu, text_breite=150)
        self.dg_adressbits.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.dg_adresse = WertRegler(b, "Adresse", "zahl", 0, 15, 5, ganzzahl=True, bei_aenderung=self._dg_lesen,
                                     text_breite=150)
        self.dg_adresse.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.5, max_hoehe=380)
        self.dg_canvas.grid(row=3, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Ein Speicher ist eine Tabelle: Die a Adressleitungen wählen eine von "
                       "2^a Zeilen (intern ein Decoder), die d Datenleitungen tragen den Inhalt dieser Zeile. Die "
                       "Steuerleitungen sind aktiv LOW: CS (Chip Select) aktiviert den Baustein, OE (Output Enable) "
                       "schaltet beim Lesen die Datenausgänge auf den Bus, WE (Write Enable) übernimmt beim Schreiben "
                       "die Daten vom Bus. Ist CS = 1, sind die Datenleitungen hochohmig – so teilen sich mehrere "
                       "Bausteine einen Bus.").grid(row=5, column=0, sticky="ew", pady=(8, 0))
        self.dg_meldung = ""
        self._dg_lesen()

    def _dg_d(self):
        return int(self.dg_breite.get().split()[0])

    def _dg_a(self):
        return int(round(self.dg_adressbits.wert()))

    def _dg_adr(self):
        return min(int(round(self.dg_adresse.wert())), 2 ** self._dg_a() - 1)

    def _dg_adressbits_neu(self):
        worte = 2 ** self._dg_a()
        self.dg_adresse.bereich_setzen(0, worte - 1, min(self._dg_adr(), worte - 1))
        self._dg_lesen()

    def _dg_lesen(self):
        self.dg_aktion = "lesen"
        wert = self.dg_inhalt.get(self._dg_adr(), 0) & (2 ** self._dg_d() - 1)
        self.dg_meldung = f"Lesen: CS = 0, OE = 0, WE = 1  →  Adresse {self._dg_adr()} liefert {_hex(wert, self._dg_d())}"
        self._dg_neu()

    def _dg_schreiben(self):
        try:
            wert = bm.byte_einlesen(self.dg_wert.get(), self._dg_d())
        except ValueError as fehler:
            self.dg_meldung = f"⚠ {fehler}"
            self._dg_neu(FEHLER)
            return
        self.dg_aktion = "schreiben"
        self.dg_inhalt[self._dg_adr()] = wert
        self.dg_meldung = (f"Schreiben: CS = 0, WE = 0, OE = 1  →  {_hex(wert, self._dg_d())} an Adresse "
                           f"{self._dg_adr()} gespeichert")
        self._dg_neu()

    def _dg_neu(self, farbe=None):
        if not hasattr(self, "dg_ergebnis"):
            return
        a, d = self._dg_a(), self._dg_d()
        o = bm.speicher_organisation(a, d)
        zeilen = [f"Organisation 2^{a} × {d} = {o['worte']} Wörter × {d} Bit = {o['bits']} Bit "
                  f"(Adressen 0 … {o['hoechste']} = 0x0 … {_hex(o['hoechste'], a)})",
                  f"Adresse {self._dg_adr()} = A{a - 1}…A0 = {self._dg_adr():0{a}b}",
                  self.dg_meldung]
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=farbe or config.FARBEN["akzent"])
        _neu_zeichnen(self)

    def _dg_zeichnen(self, c, w, h):
        if not hasattr(self, "dg_ergebnis"):
            return
        text, leise = _farbe(config.FARBEN["text"]), _farbe(config.FARBEN["text_leise"])
        g = max(7, int(min(w / 2.4, h) / 18))
        schrift, fett = (config.SCHRIFT, g), (config.SCHRIFT, g, "bold")
        code = (config.SCHRIFT_CODE, g)
        a, d, adr = self._dg_a(), self._dg_d(), self._dg_adr()
        schreiben = self.dg_aktion == "schreiben"
        # ---- Baustein ----
        bx0, bx1, by0, by1 = w * 0.15, w * 0.33, h * 0.10, h * 0.90
        c.create_rectangle(bx0, by0, bx1, by1, outline=text, width=2)
        c.create_text((bx0 + bx1) / 2, by0 - 3, text=f"{2 ** a} × {d}", anchor="s", fill=leise, font=schrift)
        c.create_text((bx0 + bx1) / 2 + w * 0.03, by0 + (by1 - by0) * 0.32, text="RAM", fill=leise, font=fett)
        anschluesse = [("A", f"{adr:0{a}b}", BLAU, by0 + (by1 - by0) * 0.18),
                       ("CS", "0", ROT, by0 + (by1 - by0) * 0.45),
                       ("OE", "1" if schreiben else "0", ROT, by0 + (by1 - by0) * 0.65),
                       ("WE", "0" if schreiben else "1", ROT, by0 + (by1 - by0) * 0.85)]
        for name, wert, farbe, y in anschluesse:
            c.create_line(bx0 - w * 0.05, y, bx0, y, fill=farbe, width=4 if name == "A" else 2)
            c.create_text(bx0 + 4, y, text=name if name == "A" else f"¬{name}", anchor="w", fill=text, font=schrift)
            c.create_text(bx0 - w * 0.05 - 3, y, text=wert, anchor="e", fill=farbe, font=code)
        yd = by0 + (by1 - by0) * 0.18
        wert = self.dg_inhalt.get(adr, 0) & (2 ** d - 1)
        c.create_line(bx1, yd, bx1 + w * 0.15, yd, fill=ORANGE, width=4, arrow="first" if schreiben else "last")
        c.create_text(bx1 - 4, yd, text="D", anchor="e", fill=text, font=schrift)
        c.create_text(bx1 + 4, yd - 5, text=f"{wert:0{d}b}", anchor="sw", fill=ORANGE, font=code)
        # ---- Inhalt als Tabelle ----
        worte = 2 ** a
        zeile_h = max(g * 1.5, 12)
        platz = int((h * 0.86) // zeile_h) - 1
        anzahl = min(worte, platz, 16)
        start = min(max(0, adr - anzahl // 2), worte - anzahl)
        tx0, tx1 = w * 0.52, w * 0.98
        ty = h * 0.07
        c.create_text(tx0 + 4, ty, text="Adresse", anchor="w", fill=leise, font=schrift)
        c.create_text(tx1 - 4, ty, text="Inhalt", anchor="e", fill=leise, font=schrift)
        for k in range(anzahl):
            z = start + k
            y = ty + (k + 1) * zeile_h
            if z == adr:
                c.create_rectangle(tx0, y - zeile_h / 2, tx1, y + zeile_h / 2, fill=ORANGE if schreiben else BLAU,
                                   outline="")
            farbe = "#FFFFFF" if z == adr else text
            inhalt = self.dg_inhalt.get(z, 0) & (2 ** d - 1)
            c.create_text(tx0 + 4, y, text=f"{z:0{a}b}  ({z})", anchor="w", fill=farbe, font=code)
            c.create_text(tx1 - 4, y, text=f"{inhalt:0{d}b}", anchor="e", fill=farbe, font=code)
        if anzahl < worte:
            c.create_text((tx0 + tx1) / 2, ty + (anzahl + 1) * zeile_h, text=f"… {worte - anzahl} weitere Zeilen",
                          fill=leise, font=schrift)
