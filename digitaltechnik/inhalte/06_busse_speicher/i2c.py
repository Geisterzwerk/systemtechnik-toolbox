# Seite "I²C"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py
# Pull-up-Berechnung: Rechner "open_drain_pullup" aus Schritt 8c (digitaltechnik/rechner.py) wird wiederverwendet.

THEMA = {
    "titel": "I²C (Inter-Integrated Circuit)",
    "reihenfolge": 30,
    "kurz": "Zwei Leitungen, viele Teilnehmer: Open Drain mit Pull-ups, START/STOP, 7-Bit-Adresse, ACK/NACK, Register lesen.",
    "stichworte": ["I2C", "I²C", "IIC", "TWI", "SMBus", "SDA", "SCL", "ACK", "NACK", "START", "STOP",
                   "Repeated Start", "Adresse", "7-Bit-Adresse", "R/W", "Pull-up", "Open Drain", "Clock Stretching",
                   "Fast-mode", "Standard-mode", "Bus-Scan"],

    "grafiken": ["werkzeug_i2c"],

    "erklaerung": """
## Grundlagen
I²C verbindet viele Bausteine über **zwei Leitungen**: **SDA** (Daten) und **SCL** (Takt), dazu GND.
- Beide Leitungen sind **Open Drain** mit je einem **Pull-up**: Jeder Teilnehmer darf nur nach LOW ziehen, HIGH macht der Widerstand. So gibt es keinen Kurzschluss, wenn zwei gleichzeitig senden.
- Jeder Slave hat eine **7-Bit-Adresse** (z.B. 0x48). Reserviert sind 0x00 … 0x07 und 0x78 … 0x7F.

Regeln auf dem Bus:
- SDA darf sich nur ändern, wenn **SCL = 0** ist; bei SCL = 1 wird gelesen.
- **START**: SDA fällt, während SCL = 1 ist. **STOP**: SDA steigt, während SCL = 1 ist.
- Erstes Byte: 7-Bit-Adresse + **R/¬W** (0 = schreiben, 1 = lesen).
- Nach jedem Byte gibt der **Empfänger** im 9. Takt **ACK** (SDA = 0). Bleibt SDA HIGH, ist das **NACK** (niemand da, oder „keine Daten mehr“).
- Beim Lesen bestätigt der Master das letzte Byte mit NACK und sendet dann STOP.
- **Repeated Start (Sr)**: neuer START ohne STOP davor, z.B. nach dem Schreiben der Registernummer.

**Geschwindigkeiten:**
- Standard-mode 100 kHz, t_r ≤ 1000 ns
- Fast-mode 400 kHz, t_r ≤ 300 ns
- Fast-mode Plus 1 MHz, t_r ≤ 120 ns

Buskapazität bis 400 pF. Die Pull-ups müssen klein genug für die Anstiegszeit sein und gross genug für den LOW-Strom (Rechner „Pull-up für Open Drain / I²C“).

## Vorgehen
1. Adressen aller Slaves aus den Datenblättern sammeln (oft mit Adress-Pins wählbar), Konflikte vermeiden.
2. Pull-ups dimensionieren: `R_min = (U_B − 0.4 V) / 3 mA`, `R_max = t_r / (0.847 · C_Bus)`; typisch 2.2 … 10 kΩ, nur EIN Paar pro Bus.
3. Register schreiben: `S | Adr+W | A | Reg | A | Daten | A | P`
4. Register lesen: `S | Adr+W | A | Reg | A | Sr | Adr+R | A | Daten | A … Daten | N | P`
5. Dauer abschätzen: etwa `9 Takte je Byte + START/STOP`; bei 100 kHz also ≈ 90 µs pro Byte.

## Beispiel
Temperatursensor an Adresse 0x48, Register 0x00, 2 Byte lesen (100 kHz):
- Adresse 0x48 = 100 1000 → erstes Byte schreiben `1001 0000` = 0x90, lesen `1001 0001` = 0x91
- Ablauf: `S, 0x90, A, 0x00, A, Sr, 0x91, A, MSB, A, LSB, N, P`
- Takte ≈ 1 + 9 + 9 + 1 + 9 + 2 · 9 + 1 = 48 → `t ≈ 48 / 100 kHz = 480 µs`

Pull-up bei 3.3 V, 200 pF, Fast-mode:
- `R_min = (3.3 − 0.4) V / 3 mA = 967 Ω`
- `R_max = 300 ns / (0.847 · 200 pF) = 1.77 kΩ`
- → z.B. 1.5 kΩ

## Praxis
- Bibliotheken schreiben die Adresse oft schon verschoben (8 Bit: 0x90/0x91) – Datenblatt genau lesen, 7 oder 8 Bit?
- Ein **Bus-Scan** (jede Adresse ansprechen, auf ACK warten) zeigt, wer am Bus hängt.
- Hängt SDA dauerhaft LOW (Slave mitten im Byte zurückgesetzt): 9 Takte auf SCL senden, dann STOP.
- **Clock Stretching**: Ein langsamer Slave hält SCL LOW, bis er bereit ist – der Master muss das unterstützen.
- Für lange Leitungen oder viele Teilnehmer: Bus-Puffer (z.B. P82B715, PCA9600); 3.3 V ↔ 5 V mit Pegelwandler (z.B. MOSFET BSS138).
""",

    "tipps": [
        "Fehlen die Pull-ups, bleiben SDA und SCL LOW oder schweben – dann antwortet niemand.",
        "Viele Breakout-Boards haben schon Pull-ups eingebaut. Bei mehreren Boards liegen sie parallel und der Widerstand wird zu klein.",
        "Mit Oszilloskop prüfen: Die Flanken dürfen nicht „haifischflossenartig“ langsam ansteigen.",
    ],
    "fehler": [
        "7-Bit-Adresse mit dem 8-Bit-Adressbyte verwechselt (0x48 statt 0x90 oder umgekehrt).",
        "Pull-ups vergessen oder viel zu gross gewählt (z.B. 100 kΩ) – die Flanken werden zu langsam.",
        "Zwei Bausteine mit derselben Adresse am selben Bus.",
        "Beim Lesen das letzte Byte mit ACK statt NACK bestätigt – der Slave sendet weiter und blockiert SDA.",
        "Leitungen zu lang (mehrere Meter) – I²C ist für die Platine gedacht.",
    ],
    "siehe_auch": ["ausgangstypen", "uart", "spi", "logikpegel_stoerabstand"],
    "rechner": ["i2c_uebertragung", "open_drain_pullup"],
}
