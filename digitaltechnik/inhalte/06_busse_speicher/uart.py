# Seite "UART"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "UART, RS-232 und RS-485",
    "reihenfolge": 10,
    "kurz": "Asynchron seriell ohne Taktleitung: Startbit, Daten (LSB zuerst), Parität, Stoppbit – Baudrate, Toleranz und Pegel.",
    "stichworte": ["UART", "USART", "seriell", "serielle Schnittstelle", "RS-232", "RS-485", "RS-422", "Baudrate",
                   "8N1", "Startbit", "Stoppbit", "Parität", "Parity", "TX", "RX", "COM-Port", "MAX232",
                   "USB-Seriell", "Modbus RTU", "asynchron"],

    "grafiken": ["werkzeug_uart"],

    "erklaerung": """
## Grundlagen
UART (Universal Asynchronous Receiver Transmitter) überträgt Zeichen Bit für Bit über **eine Leitung je Richtung** (TX → RX, gekreuzt) und GND. Es gibt **keine Taktleitung** – beide Seiten vereinbaren vorher:
- **Baudrate** (Symbole pro Sekunde, bei UART = Bit/s): 9600, 115200 …  `t_bit = 1 / Baudrate`
- **Format**, z.B. **8N1** = 8 Datenbits, keine Parität (N, E = gerade, O = ungerade), 1 Stoppbit

Ein Rahmen:
- Ruhe = **HIGH**
- **Startbit 0**: Die fallende Flanke startet die Uhr des Empfängers.
- **Daten mit dem niedrigsten Bit zuerst** (LSB first)
- optional **Paritätsbit**: gerade = Anzahl Einsen inkl. P gerade
- **Stoppbit(s) 1**

Der Empfänger tastet jedes Bit in der Mitte ab (meist 16-fach überabgetastet). Weil er sich nur am Startbit synchronisiert, darf der Takt bis zum letzten Bit höchstens eine halbe Bitzeit weglaufen: `Δf_gesamt < 0.5 / (Rahmenbits − 0.5)`, bei 8N1 ≈ 5 % für beide Seiten zusammen.

**Pegel** – dasselbe Protokoll, verschiedene Leitungen:
- **TTL/CMOS** (µC-Pins, 3.3 V oder 5 V): 1 = HIGH
- **RS-232**: invertiert und bipolar, 1 („Mark“) = −3 … −15 V, 0 („Space“) = +3 … +15 V; Pegelwandler z.B. MAX232/MAX3232; nur Punkt zu Punkt, einige Meter
- **RS-485**: differenziell (A/B), Empfänger erkennt schon ±200 mV; bis ca. 1200 m, bis 32 Teilnehmer (Unit Loads) an einem Bus, halbduplex; Abschluss 120 Ω an beiden Enden

## Vorgehen
1. Baudrate und Format auf beiden Seiten gleich einstellen (z.B. 115200 8N1).
2. TX des einen an RX des anderen, GND verbinden; Pegel prüfen (3.3 V ↔ 5 V? RS-232? → Wandler).
3. Baudraten-Teiler des µC berechnen: `N = f / (16 · Baudrate)`, gerundet; Fehler `f / (16 · N · Baudrate) − 1` sollte je Seite ≤ 2 % sein.
4. Datenrate abschätzen: `Zeichen/s = Baudrate / Rahmenbits` (8N1: Baudrate / 10).
5. Bei Bussen (RS-485): Richtungsumschaltung (DE/RE), Abschlusswiderstände, Protokoll mit Adressen (z.B. Modbus RTU).

## Beispiel
Zeichen „A“ = 0x41 = 0100 0001 mit 9600 Baud, 8N1:
- Auf der Leitung: Start 0, dann D0 … D7 = `1 0 0 0 0 0 1 0`, Stopp 1
- `t_bit = 1 / 9600 = 104.2 µs`, Rahmen = 10 Bit = 1.042 ms → max. 960 Zeichen/s
- Mit gerader Parität (8E1): zwei Einsen → P = 0, Rahmen 11 Bit

Baudraten-Teiler, µC mit 16 MHz:
- 9600 Bd: `N = 16 MHz / (16 · 9600) = 104.17` → 104, tatsächlich 9615 Bd, Fehler +0.16 % ✓
- 115200 Bd: `N = 8.68` → 9, tatsächlich 111 111 Bd, Fehler −3.5 % ⚠ – mit einem 14.7456-MHz-Quarz wäre der Fehler 0 %.

## Praxis
- „Kauderwelsch“ im Terminal = fast immer falsche Baudrate (oder vertauschte Pegel: RS-232 direkt an einen µC-Pin zerstört ihn).
- USB-Seriell-Wandler (CH340, FT232, CP2102) erscheinen als COM-Port bzw. /dev/ttyUSB0.
- TX und RX kreuzen; RTS/CTS (Hardware-Handshake) nur, wenn beide Seiten es nutzen.
- Industrie: RS-485 mit Modbus RTU; zwischen den Telegrammen mindestens 3.5 Zeichen Pause.
- Der Werkzeug-Rahmen unten zeigt TTL und RS-232 untereinander; die roten Punkte sind die Abtastzeitpunkte.
""",

    "tipps": [
        "8N1 heisst: 10 Bit pro Byte – Baudrate / 10 = Bytes pro Sekunde.",
        "Baudratenquarze (1.8432, 3.6864, 7.3728, 11.0592, 14.7456 MHz) teilen alle Standard-Baudraten ohne Fehler.",
        "Logic-Analyzer oder Oszilloskop mit UART-Decoder zeigen sofort, ob Baudrate und Format stimmen.",
    ],
    "fehler": [
        "TX an TX angeschlossen – es muss gekreuzt werden (TX → RX).",
        "GND nicht verbunden – ohne gemeinsame Masse gibt es keinen gemeinsamen Pegel.",
        "RS-232 (±12 V) direkt an einen 3.3-V-µC angeschlossen.",
        "Baudrate mit Bits pro Sekunde Nutzdaten verwechselt (Start- und Stoppbits kosten 20 %).",
        "RS-485 ohne Abschlusswiderstände oder mit Abzweigleitungen (Sternverdrahtung) aufgebaut.",
    ],
    "siehe_auch": ["spi", "i2c", "logikpegel_stoerabstand", "schieberegister"],
    "rechner": ["uart_timing", "uart_baudrate"],
}
