# =============================================================================
# digitaltechnik/busse_mathe.py
# -----------------------------------------------------------------------------
# REINE FUNKTIONEN für serielle Busse und Speicher - KEIN tkinter. Einzeln testbar, z.B.:
#
#   python -c "from digitaltechnik.busse_mathe import *; print(baud_teiler(16e6, 9600))"
#
#   byte_einlesen()        "65", "0x41", "0b1000001" oder ein Zeichen "A" -> Zahl
#   uart_rahmen()          Bits eines UART-Rahmens (Start, Daten LSB zuerst, Parität, Stopp)
#   uart_timing()          Bitzeit, Rahmenzeit, Bytes pro Sekunde, Nutzanteil
#   baud_teiler()          Baudraten-Teiler eines µC, tatsächliche Baudrate und Fehler in %
#   spi_modus()            CPOL / CPHA, Ruhepegel, Abtastflanke
#   spi_signale()          Zeitdiagramm einer SPI-Übertragung (CS, SCLK, MOSI, MISO)
#   i2c_rahmen()           Abschnitte einer I²C-Übertragung (START, Adresse, R/W, ACK, Daten, STOP)
#   i2c_signale()          Zeitdiagramm SDA / SCL dazu
#   i2c_dauer()            Taktanzahl und Dauer einer I²C-Übertragung
#   speicher_organisation() Kapazität aus Adress- und Datenbits
#   worte_einlesen()       "32K", "2^15" -> 32768
#   speicher_erweitern()   Wie viele Chips für eine grössere Tiefe / Wortbreite?
#
# WER RUFT DAS AUF?  digitaltechnik/grafiken_busse.py, digitaltechnik/rechner.py
# =============================================================================

import math

from digitaltechnik import zahlen_mathe as zm                          # -> digitaltechnik/zahlen_mathe.py


def byte_einlesen(text, bits=8):
    """Zahl (dez, 0x…, 0b…) oder EIN Zeichen (ASCII) -> ganze Zahl 0 … 2^bits − 1."""
    t = str(text or "").strip()
    if len(t) == 3 and t[0] == t[2] and t[0] in "'\"":             # 'A' oder "A"
        t = t[1]
    if len(t) == 1 and not t.isdigit():
        wert = ord(t)
    else:
        wert = zm.einlesen(t)
    if not 0 <= wert < 2 ** bits:
        raise ValueError(f"Wert {wert} passt nicht in {bits} Bit (0 … {2 ** bits - 1})")
    return wert


# =============================================================================
# UART
# =============================================================================
PARITAETEN = ["keine", "gerade (even)", "ungerade (odd)"]
BAUDRATEN = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]


def paritaetsbit(wert, paritaet):
    """Gerade (even): Anzahl Einsen inkl. Paritätsbit ist gerade. Ungerade (odd): ungerade. keine -> None."""
    einsen = bin(wert).count("1")
    if paritaet.startswith("gerade"):
        return einsen % 2
    if paritaet.startswith("ungerade"):
        return 1 - einsen % 2
    return None


def uart_rahmen(wert, datenbits=8, paritaet="keine", stopbits=1):
    """
    Bits in Sende-Reihenfolge: [(name, bit), …]
    Ruhepegel 1, Startbit 0, Daten mit dem NIEDRIGSTEN Bit zuerst (LSB first), optional Parität, Stoppbit(s) 1.
    """
    if not 5 <= datenbits <= 9:
        raise ValueError("Datenbits: 5 … 9")
    if stopbits not in (1, 1.5, 2):
        raise ValueError("Stoppbits: 1, 1.5 oder 2")
    if not 0 <= wert < 2 ** datenbits:
        raise ValueError(f"Wert {wert} passt nicht in {datenbits} Datenbits")
    bits = [("Start", 0)] + [(f"D{i}", (wert >> i) & 1) for i in range(datenbits)]
    p = paritaetsbit(wert, paritaet)
    if p is not None:
        bits.append(("P", p))
    bits += [("Stop", 1)] * math.ceil(stopbits)
    return bits


def uart_format(datenbits, paritaet, stopbits):
    """Kurzschreibweise, z.B. 8N1, 7E1, 8O2."""
    p = "N" if paritaet == "keine" else ("E" if paritaet.startswith("gerade") else "O")
    return f"{datenbits}{p}{stopbits:g}"


def uart_timing(baud, datenbits=8, paritaet="keine", stopbits=1):
    """t_bit = 1 / Baudrate;  Rahmen = 1 Start + Daten + Parität + Stopp;  Bytes/s = Baudrate / Rahmenbits."""
    if baud <= 0:
        raise ValueError("Baudrate muss grösser als 0 sein")
    rahmen = 1 + datenbits + (0 if paritaet == "keine" else 1) + stopbits
    return {"t_bit": 1 / baud, "rahmen_bits": rahmen, "t_rahmen": rahmen / baud, "bytes_s": baud / rahmen,
            "nutz_bit_s": baud * datenbits / rahmen, "nutzanteil": datenbits / rahmen,
            # Der Empfänger synchronisiert nur auf die Startflanke und tastet dann in der Bitmitte ab.
            # Beim letzten Abtastpunkt (Mitte Stoppbit) darf der Versatz höchstens eine halbe Bitzeit sein:
            "toleranz_gesamt": 0.5 / (rahmen - 0.5)}


def baud_teiler(f_takt, baud, ueberabtastung=16):
    """
    Typischer µC-UART: Baudrate = f_Takt / (Überabtastung · N), N ganzzahlig.
    (Beim AVR steht im Register UBRR = N − 1.)
    Rückgabe: Teiler N, tatsächliche Baudrate, Fehler (Anteil, z.B. 0.0016 = 0.16 %).
    """
    if f_takt <= 0 or baud <= 0:
        raise ValueError("Takt und Baudrate müssen grösser als 0 sein")
    ideal = f_takt / (ueberabtastung * baud)
    n = max(1, round(ideal))
    ist = f_takt / (ueberabtastung * n)
    if ideal < 0.5:
        raise ValueError(f"Takt zu klein: Für {baud:g} Baud bräuchte es mindestens {ueberabtastung * baud:g} Hz")
    return {"ideal": ideal, "teiler": n, "register": n - 1, "ist": ist, "fehler": ist / baud - 1}


# =============================================================================
# SPI
# =============================================================================
def spi_modus(modus):
    """Modus 0 … 3 = (CPOL, CPHA). CPOL = Ruhepegel von SCLK, CPHA = 0: Abtasten an der ersten Flanke."""
    if modus not in (0, 1, 2, 3):
        raise ValueError("SPI-Modus 0 … 3")
    cpol, cpha = modus >> 1, modus & 1
    abtast = "steigend" if cpol == cpha else "fallend"
    return {"cpol": cpol, "cpha": cpha, "ruhe": cpol, "abtast": abtast,
            "schiebe": "fallend" if abtast == "steigend" else "steigend"}


def spi_signale(mosi, miso, modus=0, bits=8, msb_zuerst=True):
    """
    Zeitschritte (je Bit 2 Halbperioden) für CS, SCLK, MOSI, MISO.
      CPHA = 0: Bit liegt schon an, bevor die erste Flanke kommt -> SCLK je Bit [Ruhe, aktiv]
      CPHA = 1: Bit wird mit der ersten Flanke ausgegeben         -> SCLK je Bit [aktiv, Ruhe]
    Abgetastet wird immer in der Bitmitte (an der zweiten Halbperiode). "Z" = hochohmig (Leitung frei).
    """
    m = spi_modus(modus)
    ruhe, aktiv = m["ruhe"], 1 - m["ruhe"]
    reihenfolge = list(range(bits - 1, -1, -1)) if msb_zuerst else list(range(bits))
    cs, sclk, d_mosi, d_miso, flanken, bitnamen = [], [], [], [], [], []

    def schritt(c, s, mo, mi):
        cs.append(c), sclk.append(s), d_mosi.append(mo), d_miso.append(mi)

    schritt(1, ruhe, "Z", "Z")                                         # Ruhe, CS inaktiv
    schritt(0, ruhe, "Z" if m["cpha"] else (mosi >> reihenfolge[0]) & 1,  # CS fällt, bei CPHA 0 liegt Bit schon an
            "Z" if m["cpha"] else (miso >> reihenfolge[0]) & 1)
    for k, i in enumerate(reihenfolge):
        mo, mi = (mosi >> i) & 1, (miso >> i) & 1
        takt = (ruhe, aktiv) if m["cpha"] == 0 else (aktiv, ruhe)
        schritt(0, takt[0], mo, mi)
        flanken.append(len(cs))                                        # Flanke zwischen den Halbperioden
        bitnamen.append((len(cs) - 1, f"D{i}"))
        schritt(0, takt[1], mo, mi)
    schritt(0, ruhe, d_mosi[-1], d_miso[-1])                          # letzte Halbperiode, Bit bleibt
    schritt(1, ruhe, "Z", "Z")
    return {"CS": cs, "SCLK": sclk, "MOSI": d_mosi, "MISO": d_miso, "flanken": flanken, "bits": bitnamen, **m}


def spi_dauer(f_sclk, anzahl_bytes, bits=8):
    if f_sclk <= 0 or anzahl_bytes <= 0:
        raise ValueError("Takt und Anzahl Bytes müssen grösser als 0 sein")
    t = anzahl_bytes * bits / f_sclk
    return {"takte": anzahl_bytes * bits, "dauer": t, "bytes_s": f_sclk / bits}


# =============================================================================
# I²C
# =============================================================================
I2C_MODI = {"Standard-mode (100 kHz)": 100e3, "Fast-mode (400 kHz)": 400e3, "Fast-mode Plus (1 MHz)": 1e6}
I2C_ARTEN = ["schreiben", "lesen", "Register lesen"]


def i2c_rahmen(adresse, lesen=False, daten=(), slave_da=True, register=None):
    """
    Abschnitte: [(name, bits, sender), …]  sender = "Master" oder "Slave"; bits als Liste (MSB zuerst).
      START, 7-Bit-Adresse + R/W (1 = lesen), ACK vom Slave (0 = ACK, 1 = NACK),
      je Datenbyte 8 Bit + ACK vom Empfänger. Beim Lesen bestätigt der Master das LETZTE Byte mit NACK.
      register: zuerst schreiben (Registernummer), dann wiederholter START (Sr) und lesen.
    Antwortet kein Slave (slave_da=False), folgt nach dem NACK sofort STOP.
    """
    if not 0 <= adresse <= 0x7F:
        raise ValueError("I²C-Adresse 7 Bit: 0x00 … 0x7F")
    if adresse <= 0x07 or adresse >= 0x78:
        raise ValueError(f"Adresse 0x{adresse:02X} ist reserviert (0x00 … 0x07 und 0x78 … 0x7F)")

    def byte_bits(b):
        return [(b >> i) & 1 for i in range(7, -1, -1)]

    def adress_teil(rw):
        return [("Adresse", byte_bits(adresse << 1)[:7], "Master"), ("R/W", [rw], "Master"),
                ("ACK" if slave_da else "NACK", [0 if slave_da else 1], "Slave")]

    teile = [("START", [], "Master")]
    if register is not None:
        teile += adress_teil(0)
        if not slave_da:
            return teile + [("STOP", [], "Master")]
        teile += [("Register", byte_bits(register), "Master"), ("ACK", [0], "Slave"), ("Sr", [], "Master")]
        lesen = True
    teile += adress_teil(1 if lesen else 0)
    if not slave_da:
        return teile + [("STOP", [], "Master")]
    for k, b in enumerate(daten):
        if lesen:
            letztes = k == len(daten) - 1
            teile += [(f"Daten {k + 1}", byte_bits(b), "Slave"), ("NACK" if letztes else "ACK", [int(letztes)], "Master")]
        else:
            teile += [(f"Daten {k + 1}", byte_bits(b), "Master"), ("ACK", [0], "Slave")]
    return teile + [("STOP", [], "Master")]


def i2c_signale(teile):
    """
    SCL / SDA je Viertel-Bitzeit. Datenbit: SCL [0, 1, 1, 0], SDA ändert sich nur, wenn SCL = 0.
    START: SDA fällt, während SCL = 1.   STOP: SDA steigt, während SCL = 1.   Sr = START ohne STOP davor.
    Rückgabe: SCL, SDA, Abschnitte [(start, ende, name, sender)], Abtastpunkte (SCL-Mitte HIGH).
    """
    scl, sda, abschnitte, abtast = [1, 1], [1, 1], [], []
    for name, bits, sender in teile:
        anfang = len(scl)
        if name == "START":
            scl += [1, 1, 0]
            sda += [1, 0, 0]
        elif name == "Sr":                                             # wiederholter START
            scl += [0, 1, 1, 1, 0]
            sda += [1, 1, 1, 0, 0]
        elif name == "STOP":
            scl += [0, 1, 1, 1]
            sda += [0, 0, 1, 1]
        else:
            for b in bits:
                scl += [0, 1, 1, 0]
                sda += [b] * 4
                abtast.append(len(scl) - 3)
        abschnitte.append((anfang, len(scl), name, sender))
    scl += [1]
    sda += [1]
    return {"SCL": scl, "SDA": sda, "abschnitte": abschnitte, "abtast": abtast}


def i2c_dauer(f_scl, art="schreiben", n_daten=1):
    """
    Takte: START + 9 (Adresse, R/W, ACK) + 9 je Datenbyte + STOP (START/STOP grob je 1 Takt).
    Register lesen: Adresse + Registernummer schreiben, Sr, Adresse + n Bytes lesen.
    Ohne Clock Stretching und Pausen zwischen den Bytes (echte Werte sind etwas grösser).
    """
    if f_scl <= 0 or n_daten < 0:
        raise ValueError("Takt > 0 und Anzahl Bytes ≥ 0")
    if art == "Register lesen":
        takte = 1 + 9 + 9 + 1 + 9 + 9 * n_daten + 1
    else:
        takte = 1 + 9 + 9 * n_daten + 1
    t = takte / f_scl
    return {"takte": takte, "dauer": t, "nutz_bit_s": 8 * n_daten / t if n_daten else 0.0,
            "anteil": 8 * n_daten / takte}


# =============================================================================
# SPEICHER
# =============================================================================
def speicher_organisation(adressbits, datenbits):
    """2^Adressbits Speicherplätze (Wörter) zu je Datenbits: Kapazität = 2^a · d Bit."""
    if not 0 < adressbits <= 40 or not 0 < datenbits <= 128:
        raise ValueError("Adressbits 1 … 40, Datenbits 1 … 128")
    worte = 2 ** adressbits
    return {"worte": worte, "bits": worte * datenbits, "bytes": worte * datenbits / 8,
            "hoechste": worte - 1, "hex_stellen": math.ceil(adressbits / 4)}


def groesse_text(anzahl, einheit="Bit"):
    """1024er-Vorsätze wie in Datenblättern: 32768 -> 32 Ki (32 K)."""
    for vorsatz, faktor in (("Gi", 2 ** 30), ("Mi", 2 ** 20), ("Ki", 2 ** 10)):
        if anzahl >= faktor and anzahl % faktor == 0:
            return f"{anzahl // faktor} {vorsatz}{einheit}"
    return f"{anzahl:g} {einheit}"


def worte_einlesen(text):
    """Speichergrösse wie im Datenblatt: "32K", "32 Ki", "1M", "2^15" oder "32768" (K = 1024, M = 1024²)."""
    t = str(text or "").strip().replace(" ", "").upper().replace("I", "")
    if not t:
        raise ValueError("Grösse eingeben, z.B. 32K oder 32768")
    try:
        if t.startswith("2^"):
            return 2 ** int(t[2:])
        faktor = {"K": 2 ** 10, "M": 2 ** 20, "G": 2 ** 30}.get(t[-1], 1)
        return int(float(t[:-1] if faktor > 1 else t) * faktor)
    except ValueError:
        raise ValueError(f"„{text}“ ist keine Speichergrösse (z.B. 32K, 2^15, 32768)") from None


def speicher_erweitern(ziel_worte, ziel_breite, chip_worte, chip_breite):
    """
    Wortbreite erweitern: Chips NEBENEINANDER (gleiche Adressen, gleiches CS, je ein Teil des Datenbusses).
    Tiefe erweitern:      Chips UNTEREINANDER (gemeinsamer Datenbus, ein Adressdecoder wählt per CS).
    """
    for name, w in (("Ziel-Wörter", ziel_worte), ("Chip-Wörter", chip_worte)):
        if w < 1 or w & (w - 1):
            raise ValueError(f"{name} muss eine Zweierpotenz sein (z.B. 32768 = 32 K)")
    if ziel_breite < 1 or chip_breite < 1:
        raise ValueError("Wortbreiten müssen mindestens 1 Bit sein")
    nebeneinander = math.ceil(ziel_breite / chip_breite)
    untereinander = max(1, ziel_worte // chip_worte)
    adress_ziel = ziel_worte.bit_length() - 1
    adress_chip = chip_worte.bit_length() - 1
    return {"nebeneinander": nebeneinander, "untereinander": untereinander,
            "chips": nebeneinander * untereinander, "adressbits": adress_ziel, "adressbits_chip": adress_chip,
            "decoder_bits": max(0, adress_ziel - adress_chip), "ungenutzt_bits": nebeneinander * chip_breite - ziel_breite}
