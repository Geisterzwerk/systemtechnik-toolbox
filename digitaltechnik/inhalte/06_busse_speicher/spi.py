# Seite "SPI"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "SPI (Serial Peripheral Interface)",
    "reihenfolge": 20,
    "kurz": "Synchron, schnell, vollduplex: SCLK, MOSI, MISO und Chip-Select – die vier Modi über CPOL und CPHA.",
    "stichworte": ["SPI", "Serial Peripheral Interface", "SCLK", "SCK", "MOSI", "MISO", "COPI", "CIPO", "SDO", "SDI",
                   "CS", "SS", "Chip Select", "CPOL", "CPHA", "SPI-Modus", "Daisy Chain", "74HC595", "SD-Karte",
                   "Vollduplex", "synchron"],

    "grafiken": ["werkzeug_spi"],

    "erklaerung": """
## Grundlagen
SPI verbindet einen **Master** (meist der µC) mit einem oder mehreren **Slaves** (Sensoren, ADC, Displays, Flash, SD-Karte):
- **SCLK**: Takt, immer vom Master
- **MOSI** (Master Out Slave In, neu auch COPI/SDO): Daten zum Slave
- **MISO** (Master In Slave Out, CIPO/SDI): Daten zum Master
- **¬CS** (Chip Select, auch ¬SS): aktiv LOW, je Slave eine eigene Leitung

Intern sind Master und Slave **zwei Schieberegister, die zu einem Ring verbunden sind**: Mit jedem Takt wandert ein Bit vom Master zum Slave und gleichzeitig eins zurück. Nach 8 Takten haben beide ihre Bytes getauscht (**vollduplex**). Wer nur lesen will, sendet Dummy-Bytes (z.B. 0x00 oder 0xFF).

Es gibt kein Protokoll im Bus selbst – keine Adresse, kein ACK, keine feste Geschwindigkeit. Die Ausgänge sind Push-Pull, darum sind Takte von 10 … 50 MHz üblich.

**Modi** – Modus = 2 · CPOL + CPHA:
- **CPOL** = Ruhepegel von SCLK (0 = LOW, 1 = HIGH)
- **CPHA** = 0: Abtasten an der ersten Flanke (Daten liegen schon vorher an); CPHA = 1: Abtasten an der zweiten Flanke
- Modus 0 und 3: abtasten bei steigender Flanke, Modus 1 und 2: bei fallender

## Vorgehen
1. Im Datenblatt des Slaves nachsehen: SPI-Modus, max. Taktfrequenz, MSB oder LSB zuerst, Wortlänge.
2. Den Master genau so konfigurieren (Modus falsch = Bits um eine halbe Periode verschoben, oft „fast richtig“).
3. Ablauf: ¬CS = 0 → n Bytes takten (gleichzeitig senden und empfangen) → ¬CS = 1.
4. Mehrere Slaves: je eine ¬CS-Leitung (oder Daisy Chain, wenn die Bausteine das können); nicht gewählte Slaves schalten MISO hochohmig.
5. Dauer: `t = 8 · n / f_SCLK` (plus Pausen zwischen den Bytes).

## Beispiel
Ein 12-Bit-ADC (Modus 0, laut Datenblatt max. 2 MHz) wird abgefragt: Der Master schickt 3 Bytes (Startbit, Kanal, Dummy) und liest gleichzeitig 3 Bytes zurück.
- Mit `f_SCLK = 1 MHz`: `t = 3 · 8 / 1 MHz = 24 µs` je Messung, also höchstens etwa 41 000 Messungen/s.

Das Werkzeug unten im Modus 0 mit MOSI = 0xA5, MISO = 0x3C:
- SCLK ist in Ruhe LOW, das erste Bit (D7 = 1) liegt schon an, wenn ¬CS fällt.
- Abgetastet wird bei jeder steigenden Flanke (orange), gewechselt bei der fallenden.
- Nach 8 Takten hat der Master 0x3C, der Slave 0xA5.

## Praxis
- Das Schieberegister 74HC595 ist ein SPI-Slave ohne MISO: 8 Ausgänge mit 3 Pins (Daten, Takt, Übernahme).
- SD-Karten, TFT-Displays und SPI-Flash brauchen hohe Takte → kurze Leitungen, gemeinsame Masse, ggf. Serienwiderstände (22 … 47 Ω) gegen Überschwinger.
- SPI ist für Leitungen auf der Platine gedacht (einige cm bis wenige dm), nicht für lange Kabel.
- Quad-SPI (QSPI) nutzt 4 Datenleitungen für schnelle Flash-Speicher.
""",

    "tipps": [
        "Modus 0 ist am häufigsten. Viele Bausteine können Modus 0 und 3, weil beide an der steigenden Flanke abtasten.",
        "Beim Lesen trotzdem senden: Ohne Takt vom Master kommt kein Bit zurück.",
        "Bei mehreren Slaves auf Pull-ups an den ¬CS-Leitungen achten, damit beim Start kein Slave versehentlich aktiv ist.",
    ],
    "fehler": [
        "Falscher SPI-Modus – die Werte sind um ein Bit verschoben oder springen.",
        "¬CS zwischen den Bytes eines Befehls losgelassen – der Slave bricht den Befehl ab.",
        "Takt höher als im Datenblatt des Slaves erlaubt.",
        "MISO eines Slaves treibt die Leitung, obwohl er nicht gewählt ist (Baustein ohne Tri-State am Ausgang).",
    ],
    "siehe_auch": ["uart", "i2c", "schieberegister", "ausgangstypen"],
    "rechner": ["spi_uebertragung"],
}
