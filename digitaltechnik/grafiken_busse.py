# =============================================================================
# digitaltechnik/grafiken_busse.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE für serielle Busse und Speicher (mit Zeitdiagrammen) - MODELLE OHNE FENSTER:
#
#   UartKarte      Zeichen/Byte eingeben -> UART-Rahmen (Start, Daten LSB zuerst, Parität, Stopp), TTL und RS-232
#   SpiKarte       Modus 0 … 3, MOSI- und MISO-Byte -> CS, SCLK, MOSI, MISO mit Abtastflanken
#   I2cKarte       Adresse, schreiben/lesen, Daten -> START, Adresse, R/W, ACK, Daten, STOP auf SDA/SCL
#   SpeicherKarte  kleiner Speicherbaustein: Adresse wählen, lesen oder schreiben, Steuersignale CS/OE/WE
#
# Rechnung: digitaltechnik/busse_mathe.py
# Zeitdiagramm: zeitdiagramm() aus digitaltechnik/grafiken_schaltwerke.py (wiederverwendet)
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_uart")
# =============================================================================

import config                                                            # -> config.py
from bauteile.grafiken.schaltplan import OK, SchaltungsModell            # -> bauteile/grafiken/schaltplan.py
from digitaltechnik import busse_mathe as bm                             # -> digitaltechnik/busse_mathe.py
from digitaltechnik.grafiken import FEHLER, farben                       # -> digitaltechnik/grafiken.py
from digitaltechnik.grafiken_schaltwerke import (BLAU, EINS, ORANGE, ROT,  # -> digitaltechnik/grafiken_schaltwerke.py
                                                 SIGNAL_FARBEN, zeitdiagramm)

LILA, GRUEN = "#A855F7", "#22C55E"
TEIL_FARBEN = {"Start": ORANGE, "P": LILA, "Stop": GRUEN}             # UART-Rahmen
SENDER_FARBEN = {"Master": BLAU, "Slave": ORANGE}                     # I²C: wer treibt SDA?


def _hex(wert, bits=8):
    return f"0x{wert:0{max(1, (bits + 3) // 4)}X}"


def _zeichen(wert):
    return f"'{chr(wert)}'" if 32 <= wert < 127 else "(nicht druckbar)"


# =============================================================================
# UART
# =============================================================================
class UartKarte(SchaltungsModell):
    TITEL = "📨 UART-Rahmen (interaktiv)"
    UNTERTITEL = "Zeichen oder Zahl eingeben (z.B. A, 0x41, 65), Format wählen"
    TEXTFELDER = [("daten", "Daten", "A", {"max": 12, "platzhalter": "A, 0x41 oder 65"})]
    AUSWAHL = [("baud", "Baudrate", [str(b) for b in bm.BAUDRATEN], "9600"),
               ("datenbits", "Datenbits", ["8 Bit", "7 Bit"], "8 Bit"),
               ("paritaet", "Parität", list(bm.PARITAETEN), "keine"),
               ("stopbits", "Stoppbits", ["1 Stopp", "2 Stopp"], "1 Stopp")]
    SEITENVERHAELTNIS = 0.42
    MAX_HOEHE = 320
    ERKLAERUNG = ("Was zeigt das Werkzeug?  UART überträgt ohne Taktleitung: Beide Seiten müssen dieselbe Baudrate und "
                  "dasselbe Format (z.B. 8N1) kennen. In Ruhe ist die Leitung HIGH. Das STARTBIT (0) kündigt ein Zeichen "
                  "an; der Empfänger startet mit dieser Flanke seine Uhr und tastet jedes Bit in der Mitte ab (Punkte). "
                  "Die Daten kommen mit dem NIEDRIGSTEN Bit zuerst, danach optional das Paritätsbit und das STOPPBIT (1). "
                  "RS-232 überträgt dasselbe mit umgekehrten Pegeln: logisch 1 ist −3 … −15 V, logisch 0 ist +3 … +15 V "
                  "(Pegelwandler z.B. MAX232).")

    def sk_rechnen(self, w, v):
        datenbits, stopbits = int(w["datenbits"].split()[0]), int(w["stopbits"].split()[0])
        baud, paritaet = int(w["baud"]), w["paritaet"]
        wert = bm.byte_einlesen(w["daten"], datenbits)                       # ValueError mit Erklärung
        return {"wert": wert, "datenbits": datenbits, "paritaet": paritaet, "stopbits": stopbits, "baud": baud,
                "bits": bm.uart_rahmen(wert, datenbits, paritaet, stopbits),
                "t": bm.uart_timing(baud, datenbits, paritaet, stopbits)}

    def sk_info(self, w, e, v):
        wert, t = e["wert"], e["t"]
        zeilen = [f"{wert} = {_hex(wert)} = 0b{wert:0{e['datenbits']}b}  {_zeichen(wert)}   ·   Format "
                  f"{bm.uart_format(e['datenbits'], e['paritaet'], e['stopbits'])}",
                  f"auf der Leitung (LSB zuerst): {' '.join(str(b) for _n, b in e['bits'])}"]
        p = bm.paritaetsbit(wert, e["paritaet"])
        if p is not None:
            zeilen.append(f"Parität {e['paritaet'].split()[0]}: {bin(wert).count('1')} Einsen in den Daten → P = {p}")
        zeilen.append(f"t_bit = 1 / {e['baud']} Bd = {t['t_bit'] * 1e6:.2f} µs   ·   Rahmen {t['rahmen_bits']} Bit = "
                      f"{t['t_rahmen'] * 1e3:.3f} ms   ·   max. {t['bytes_s']:.0f} Zeichen/s")
        return zeilen, config.FARBEN["akzent"]

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        text, leise, _, _ = farben(p)
        g = max(7, int(min(wb / 2.2, h) / 17))
        schrift, fett = (config.SCHRIFT, g), (config.SCHRIFT, g, "bold")
        bits = e["bits"]
        ruhe = 1.2                                                     # Ruhezeit vor und nach dem Rahmen (Bitzeiten)
        x0, x1 = wb * 0.15, wb * 0.98
        dx = (x1 - x0) / (len(bits) + 2 * ruhe)
        xs = x0 + ruhe * dx                                            # Beginn des Startbits
        kurz = dx < g * 3.2
        for i, (name, wert) in enumerate(bits):                        # Bitnamen und Werte oben
            farbe = TEIL_FARBEN.get(name, BLAU)
            xa = xs + i * dx
            c.create_rectangle(xa + 1, h * 0.04, xa + dx - 1, h * 0.22, outline=farbe)
            beschr = {"Start": "St", "Stop": "Sp"}.get(name, name.lstrip("D")) if kurz else name
            c.create_text(xa + dx / 2, h * 0.09, text=beschr, fill=farbe, font=schrift)
            c.create_text(xa + dx / 2, h * 0.17, text=str(wert), fill=text, font=fett)
        for name, oben, unten, invertiert, pegel_oben, pegel_unten in (
                ("TX (TTL)", h * 0.30, h * 0.50, False, "3.3 V", "0 V"), ("RS-232", h * 0.66, h * 0.86, True, "+12 V", "−12 V")):
            c.create_text(x0 - 6, (oben + unten) / 2, text=name, anchor="e", fill=text, font=schrift)
            c.create_text(x0 - 6, oben, text=pegel_oben, anchor="e", fill=leise, font=(config.SCHRIFT, max(6, g - 2)))
            c.create_text(x0 - 6, unten, text=pegel_unten, anchor="e", fill=leise, font=(config.SCHRIFT, max(6, g - 2)))
            werte = [1] + [b for _n, b in bits] + [1]
            grenzen = [x0, xs] + [xs + (i + 1) * dx for i in range(len(bits))] + [x1]
            punkte = []
            for k, wert in enumerate(werte):
                y = oben if (wert ^ invertiert) else unten
                punkte += [grenzen[k], y, grenzen[k + 1], y]
            c.create_line(*punkte, fill=EINS if not invertiert else ORANGE, width=2)
            if not invertiert:                                         # Abtastpunkte in der Bitmitte
                r = max(2.5, g * 0.3)
                for i, (_n, wert) in enumerate(bits):
                    xm, y = xs + (i + 0.5) * dx, oben if wert else unten
                    c.create_oval(xm - r, y - r, xm + r, y + r, fill=ROT, outline="")
        c.create_text(xs, h * 0.95, text="0", fill=leise, font=schrift)
        c.create_text(xs + len(bits) * dx, h * 0.95, text=f"{e['t']['t_rahmen'] * 1e3:.3f} ms", fill=leise, font=schrift,
                      anchor="e")
        c.create_line(xs, h * 0.04, xs, h * 0.90, fill=leise, dash=(2, 3))


# =============================================================================
# SPI
# =============================================================================
class SpiKarte(SchaltungsModell):
    TITEL = "🔁 SPI-Übertragung (interaktiv)"
    UNTERTITEL = "Modus wählen, MOSI- und MISO-Byte eingeben – Master und Slave tauschen ihre Bytes"
    VARIANTEN = ["Modus 0", "Modus 1", "Modus 2", "Modus 3"]
    TEXTFELDER = [("mosi", "MOSI (Master → Slave)", "0xA5", {"max": 12, "platzhalter": "z.B. 0xA5"}),
                  ("miso", "MISO (Slave → Master)", "0x3C", {"max": 12, "platzhalter": "z.B. 0x3C"})]
    AUSWAHL = [("reihenfolge", "Bitreihenfolge", ["MSB zuerst", "LSB zuerst"], "MSB zuerst")]
    SEITENVERHAELTNIS = 0.46
    MAX_HOEHE = 340
    ERKLAERUNG = ("Was zeigt das Werkzeug?  SPI hat eine Taktleitung (SCLK) vom Master und zwei Datenleitungen: MOSI "
                  "(Master → Slave) und MISO (Slave → Master). Mit CS = 0 wählt der Master EINEN Slave aus; nicht "
                  "gewählte Slaves schalten MISO hochohmig (Mittellinie). Bei jedem Takt wandert ein Bit in beide "
                  "Richtungen – Master und Slave tauschen den Inhalt ihrer Schieberegister. CPOL legt den Ruhepegel von "
                  "SCLK fest, CPHA, ob an der ersten (0) oder zweiten (1) Flanke abgetastet wird (orange Linien). Beide "
                  "Seiten müssen denselben Modus verwenden – sonst ist jedes Bit um eine halbe Periode verschoben.")

    def sk_rechnen(self, w, v):
        modus = self.VARIANTEN.index(v) if v in self.VARIANTEN else 0
        msb = w["reihenfolge"].startswith("MSB")
        mosi, miso = bm.byte_einlesen(w["mosi"]), bm.byte_einlesen(w["miso"])
        return {"modus": modus, "msb": msb, "mosi": mosi, "miso": miso, **bm.spi_signale(mosi, miso, modus, msb_zuerst=msb)}

    def sk_info(self, w, e, v):
        return ([f"Modus {e['modus']}: CPOL = {e['cpol']}, CPHA = {e['cpha']}  →  SCLK in Ruhe "
                 f"{'HIGH' if e['ruhe'] else 'LOW'}, abtasten an der {e['abtast']}en Flanke, Daten wechseln an der "
                 f"{e['schiebe']}en",
                 f"Master sendet {_hex(e['mosi'])} = 0b{e['mosi']:08b} und empfängt {_hex(e['miso'])} = 0b{e['miso']:08b}  "
                 f"({'MSB' if e['msb'] else 'LSB'} zuerst)",
                 "8 Takte = 1 Byte in jede Richtung (Vollduplex) – kein Adressbyte, kein ACK"], config.FARBEN["akzent"])

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        text, leise, _, _ = farben(p)
        g = max(7, int(min(wb / 2.2, h) / 17))
        schrift = (config.SCHRIFT, g)
        signale = [("CS", e["CS"], ROT), ("SCLK", e["SCLK"], SIGNAL_FARBEN["CLK"]), ("MOSI", e["MOSI"], BLAU),
                   ("MISO", e["MISO"], ORANGE)]
        x0, x1, y0, y1 = wb * 0.11, wb * 0.98, h * 0.12, h * 0.98
        zeitdiagramm(c, x0, x1, y0, y1, signale, schrift, leise, [(s, ORANGE) for s in e["flanken"]])
        dx = (x1 - x0) / len(e["CS"])
        for schritt, name in e["bits"]:                                 # Bitnummer über jedem Bit
            c.create_text(x0 + (schritt + 1) * dx, y0 - 3, text=name if dx > g * 1.6 else name[1:], anchor="s",
                          fill=text, font=schrift)


# =============================================================================
# I²C
# =============================================================================
class I2cKarte(SchaltungsModell):
    TITEL = "🔗 I²C-Übertragung (interaktiv)"
    UNTERTITEL = "Adresse, Richtung und Daten wählen – blau sendet der Master, orange der Slave"
    KURZ = {"START": "S", "STOP": "P", "ACK": "A", "NACK": "N", "R/W": "R/W", "Sr": "Sr"}
    VARIANTEN = list(bm.I2C_ARTEN)
    AUSWAHL = [("da", "Slave", ["Slave antwortet", "kein Slave"], "Slave antwortet")]
    TEXTFELDER = [("adresse", "Adresse (7 Bit)", "0x48", {"max": 10, "platzhalter": "z.B. 0x48"}),
                  ("register", "Register (nur „Register lesen“)", "0x00", {"max": 10, "platzhalter": "z.B. 0x00"}),
                  ("daten", "Daten (1 … 3 Bytes)", "0x12", {"max": 30, "platzhalter": "z.B. 0x12 0x34"})]
    SEITENVERHAELTNIS = 0.36
    MAX_HOEHE = 280
    ERKLAERUNG = ("Was zeigt das Werkzeug?  I²C braucht nur zwei Leitungen (SDA Daten, SCL Takt), beide Open Drain mit "
                  "Pull-up: Jeder darf nur nach LOW ziehen. Normalerweise ändert sich SDA nur, wenn SCL = 0 ist. Zwei "
                  "Ausnahmen markieren Anfang und Ende: START (SDA fällt bei SCL = 1) und STOP (SDA steigt bei SCL = 1). "
                  "Nach dem START sendet der Master die 7-Bit-Adresse und das R/W-Bit (0 = schreiben, 1 = lesen). Nach "
                  "jedem Byte bestätigt der Empfänger im 9. Takt mit ACK (SDA = 0). Meldet sich niemand, bleibt SDA durch "
                  "den Pull-up HIGH = NACK. „Register lesen“: erst die Registernummer schreiben, dann mit wiederholtem "
                  "START (Sr) lesen.")

    def sk_rechnen(self, w, v):
        art = v if v in bm.I2C_ARTEN else bm.I2C_ARTEN[0]
        slave_da = w["da"] == "Slave antwortet"
        adresse = bm.byte_einlesen(w["adresse"], 7)
        daten = [bm.byte_einlesen(t) for t in w["daten"].replace(",", " ").split()]
        if not 1 <= len(daten) <= 3:
            raise ValueError("1 bis 3 Datenbytes eingeben, getrennt mit Leerzeichen (z.B. 0x12 0x34)")
        register = bm.byte_einlesen(w["register"]) if art == "Register lesen" else None
        teile = bm.i2c_rahmen(adresse, art == "lesen", daten, slave_da, register)
        return {"art": art, "adresse": adresse, "register": register, "slave_da": slave_da, "teile": teile,
                **bm.i2c_signale(teile)}

    def sk_info(self, w, e, v):
        art, adresse, register = e["art"], e["adresse"], e["register"]
        adressbyte = (adresse << 1) | (1 if art == "lesen" else 0)
        zeilen = [f"Adresse 0x{adresse:02X} = 0b{adresse:07b}  →  erstes Byte 0b{adressbyte:08b} = {_hex(adressbyte)} "
                  f"({'lesen' if art == 'lesen' else 'schreiben'})" +
                  (f", nach Sr: {_hex(adressbyte | 1)} (lesen)" if register is not None else "")]
        kette = "  ".join(self.KURZ.get(n, n.replace("Daten ", "D").replace("Adresse", f"0x{adresse:02X}")
                                         .replace("Register", _hex(register or 0)))
                          + ("" if n != "R/W" else f"={bits[0]}") for n, bits, _s in e["teile"])
        zeilen.append("Ablauf: " + kette)
        if not e["slave_da"]:
            zeilen.append("⚠ Kein Slave mit dieser Adresse: SDA bleibt im 9. Takt HIGH (NACK) → der Master bricht mit "
                          "STOP ab (Adresse, Verdrahtung, Pull-ups prüfen)")
            return zeilen, FEHLER
        zeilen.append("Master liest: Er bestätigt jedes Byte mit ACK, das letzte mit NACK (= „genug“), dann STOP"
                      if art != "schreiben" else "Master schreibt: Der Slave bestätigt jedes Byte mit ACK")
        return zeilen, OK

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        _, leise, _, _ = farben(p)
        g = max(7, int(min(wb / 2.2, h) / 15))
        schrift, klein = (config.SCHRIFT, g), (config.SCHRIFT, max(6, g - 2))
        x0, x1 = wb * 0.08, wb * 0.99
        dx = (x1 - x0) / len(e["SCL"])
        for (anfang, ende, name, sender), (_n, bits, _s) in zip(e["abschnitte"], e["teile"]):   # wer sendet was?
            farbe = LILA if name in ("START", "STOP", "Sr") else SENDER_FARBEN[sender]
            xa, xb = x0 + anfang * dx, x0 + ende * dx
            c.create_rectangle(xa + 0.5, h * 0.03, xb - 0.5, h * 0.20, fill=farbe, outline="")
            kurz = ("R" if bits[0] else "W") if name == "R/W" else self.KURZ.get(
                name, name.replace("Daten ", "D").replace("Adresse", "Adr").replace("Register", "Reg"))
            for beschr in (name, kurz):
                if len(beschr) * g * 0.75 + 4 < xb - xa:
                    c.create_text((xa + xb) / 2, h * 0.115, text=beschr, fill="#FFFFFF", font=klein)
                    break
        markierungen = [(anfang + (1 if name == "START" else 3 if name == "Sr" else 2), LILA)
                        for anfang, _e, name, _s in e["abschnitte"] if name in ("START", "STOP", "Sr")]
        zeitdiagramm(c, x0, x1, h * 0.26, h * 0.98, [("SCL", e["SCL"], SIGNAL_FARBEN["CLK"]), ("SDA", e["SDA"], EINS)],
                     schrift, leise, markierungen)


# =============================================================================
# SPEICHER
# =============================================================================
def beispielinhalt(adresse, datenbits):
    """Beispiel-Inhalt des Speichers (fest, damit man beim Lesen etwas sieht): Adresse · 37 + 5, abgeschnitten."""
    return (adresse * 37 + 5) & (2 ** datenbits - 1)


class SpeicherKarte(SchaltungsModell):
    TITEL = "🗄️ Speicherbaustein (interaktiv)"
    UNTERTITEL = "Adresse wählen, dann lesen oder einen Wert schreiben"
    VARIANTEN = ["lesen", "schreiben"]
    AUSWAHL = [("breite", "Datenbreite", ["8 Bit", "4 Bit"], "8 Bit")]
    REGLER = [("a", "Adressbits a", "zahl", 2.0, 8.0, 4.0, {"ganzzahl": True}),
              ("adr", "Adresse", "zahl", 0.0, 255.0, 5.0, {"ganzzahl": True})]
    TEXTFELDER = [("wert", "Wert (schreiben)", "0x2A", {"max": 12, "platzhalter": "z.B. 0x2A"})]
    SEITENVERHAELTNIS = 0.5
    MAX_HOEHE = 380
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Ein Speicher ist eine Tabelle: Die a Adressleitungen wählen eine von 2^a "
                  "Zeilen (intern ein Decoder), die d Datenleitungen tragen den Inhalt dieser Zeile. Die Steuerleitungen "
                  "sind aktiv LOW: CS (Chip Select) aktiviert den Baustein, OE (Output Enable) schaltet beim Lesen die "
                  "Datenausgänge auf den Bus, WE (Write Enable) übernimmt beim Schreiben die Daten vom Bus. Ist CS = 1, "
                  "sind die Datenleitungen hochohmig – so teilen sich mehrere Bausteine einen Bus. (Der Inhalt ist ein "
                  "Beispiel; geschrieben wird nur in dieser Ansicht.)")

    def sk_rechnen(self, w, v):
        a, d = int(round(w["a"])), int(w["breite"].split()[0])
        adr = int(round(w["adr"]))
        if not 0 <= adr < 2 ** a:
            raise ValueError(f"Adresse {adr} gibt es bei {a} Adressbits nicht (0 … {2 ** a - 1})")
        inhalt = {k: beispielinhalt(k, d) for k in range(2 ** a)}
        schreiben = v == "schreiben"
        if schreiben:
            inhalt[adr] = bm.byte_einlesen(w["wert"], d)                    # ValueError mit Erklärung
        return {"a": a, "d": d, "adr": adr, "schreiben": schreiben, "inhalt": inhalt,
                "o": bm.speicher_organisation(a, d)}

    def sk_info(self, w, e, v):
        a, d, adr, o = e["a"], e["d"], e["adr"], e["o"]
        wert = e["inhalt"][adr]
        meldung = (f"Schreiben: CS = 0, WE = 0, OE = 1  →  {_hex(wert, d)} an Adresse {adr} gespeichert" if e["schreiben"]
                   else f"Lesen: CS = 0, OE = 0, WE = 1  →  Adresse {adr} liefert {_hex(wert, d)}")
        return ([f"Organisation 2^{a} × {d} = {o['worte']} Wörter × {d} Bit = {o['bits']} Bit "
                 f"(Adressen 0 … {o['hoechste']} = 0x0 … {_hex(o['hoechste'], a)})",
                 f"Adresse {adr} = A{a - 1}…A0 = {adr:0{a}b}", meldung], config.FARBEN["akzent"])

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        text, leise, _, _ = farben(p)
        g = max(7, int(min(wb / 2.4, h) / 18))
        schrift, fett, code = (config.SCHRIFT, g), (config.SCHRIFT, g, "bold"), (config.SCHRIFT_CODE, g)
        a, d, adr, schreiben = e["a"], e["d"], e["adr"], e["schreiben"]
        bx0, bx1, by0, by1 = wb * 0.15, wb * 0.33, h * 0.10, h * 0.90
        c.create_rectangle(bx0, by0, bx1, by1, outline=text, width=2)
        c.create_text((bx0 + bx1) / 2, by0 - 3, text=f"{2 ** a} × {d}", anchor="s", fill=leise, font=schrift)
        c.create_text((bx0 + bx1) / 2 + wb * 0.03, by0 + (by1 - by0) * 0.32, text="RAM", fill=leise, font=fett)
        for name, wert, farbe, y in (("A", f"{adr:0{a}b}", BLAU, by0 + (by1 - by0) * 0.18),
                                     ("CS", "0", ROT, by0 + (by1 - by0) * 0.45),
                                     ("OE", "1" if schreiben else "0", ROT, by0 + (by1 - by0) * 0.65),
                                     ("WE", "0" if schreiben else "1", ROT, by0 + (by1 - by0) * 0.85)):
            c.create_line(bx0 - wb * 0.05, y, bx0, y, fill=farbe, width=4 if name == "A" else 2)
            c.create_text(bx0 + 4, y, text=name if name == "A" else f"¬{name}", anchor="w", fill=text, font=schrift)
            c.create_text(bx0 - wb * 0.05 - 3, y, text=wert, anchor="e", fill=farbe, font=code)
        yd = by0 + (by1 - by0) * 0.18
        c.create_line(bx1, yd, bx1 + wb * 0.15, yd, fill=ORANGE, width=4, arrow="first" if schreiben else "last")
        c.create_text(bx1 - 4, yd, text="D", anchor="e", fill=text, font=schrift)
        c.create_text(bx1 + 4, yd - 5, text=f"{e['inhalt'][adr]:0{d}b}", anchor="sw", fill=ORANGE, font=code)
        worte = 2 ** a                                                      # Inhalt als Tabelle
        zeile_h = max(g * 1.5, 12)
        anzahl = min(worte, int((h * 0.86) // zeile_h) - 1, 16)
        start = min(max(0, adr - anzahl // 2), worte - anzahl)
        tx0, tx1, ty = wb * 0.52, wb * 0.98, h * 0.07
        c.create_text(tx0 + 4, ty, text="Adresse", anchor="w", fill=leise, font=schrift)
        c.create_text(tx1 - 4, ty, text="Inhalt", anchor="e", fill=leise, font=schrift)
        for k in range(anzahl):
            z = start + k
            y = ty + (k + 1) * zeile_h
            if z == adr:
                c.create_rectangle(tx0, y - zeile_h / 2, tx1, y + zeile_h / 2, fill=ORANGE if schreiben else BLAU, outline="")
            farbe = "#FFFFFF" if z == adr else text
            c.create_text(tx0 + 4, y, text=f"{z:0{a}b}  ({z})", anchor="w", fill=farbe, font=code)
            c.create_text(tx1 - 4, y, text=f"{e['inhalt'][z]:0{d}b}", anchor="e", fill=farbe, font=code)
        if anzahl < worte:
            c.create_text((tx0 + tx1) / 2, ty + (anzahl + 1) * zeile_h, text=f"… {worte - anzahl} weitere Zeilen",
                          fill=leise, font=schrift)
