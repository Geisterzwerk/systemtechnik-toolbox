# Seite "Schieberegister"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Schieberegister, Ring- und Johnson-Zähler",
    "reihenfolge": 30,
    "kurz": "D-Flipflops in einer Kette: seriell ↔ parallel wandeln, Bits schieben, Zustände im Kreis laufen lassen.",
    "stichworte": ["Schieberegister", "Shift Register", "SIPO", "PISO", "SISO", "PIPO", "74HC595", "74HC165",
                   "Ringzähler", "Johnson-Zähler", "Seriell-Parallel-Wandler", "Porterweiterung", "SPI", "LFSR"],

    "grafiken": ["werkzeug_schieberegister"],

    "erklaerung": """
## Stell dir vor …
Eine **Eimerkette** beim Löschen eines Brandes: Bei jedem Kommando reicht jede Person ihren Eimer an die nächste weiter. Nach acht Kommandos ist der erste Eimer bei der achten Person. Das Schieberegister ist diese Kette – der Takt ist das Kommando, die Bits sind die Eimer.
## Grundlagen
Ein Schieberegister besteht aus n D-Flipflops am selben Takt; jede Stufe übernimmt bei der Flanke den Wert der vorigen.
- **SIPO** (seriell rein, parallel raus, 74HC595): aus einer Datenleitung werden n Ausgänge.
- **PISO** (parallel rein, seriell raus, 74HC165): viele Eingänge (Taster) über eine Leitung einlesen.
- **SISO**: Verzögerung um n Takte.
- **Ringzähler**: Ausgang zurück zum Eingang, genau eine 1 läuft im Kreis → n Zustände, 1-aus-n ohne Decoder.
- **Johnson-Zähler**: INVERTIERTER Ausgang zurück → 2n Zustände, pro Takt ändert sich nur ein Bit (störarm dekodierbar).

## Vorgehen
SIPO mit dem 74HC595 an einem µC:
1. Datenbit an SER anlegen, Taktflanke an SRCLK – 8-mal (MSB oder LSB zuerst, wie gewünscht).
2. Danach eine Flanke an RCLK: Das Ausgangsregister übernimmt alle 8 Bit gleichzeitig (kein Flackern während des Schiebens).
3. Mehrere 595 kaskadieren: QH′ an SER des nächsten.

Ringzähler: beim Start genau EINE 1 setzen (Reset auf 0001), sonst läuft er falsch oder bleibt bei 0000 stehen.

## Beispiel
4-Bit-SIPO, eingegeben werden 1, 0, 1, 1 (Q0 bekommt das neue Bit):
- `0000 → 0001 → 0010 → 0101 → 1011`

4-Bit-Johnson-Zähler ab 0000:
- `0000 → 0001 → 0011 → 0111 → 1111 → 1110 → 1100 → 1000 → 0000` (8 Zustände)
- Teilt durch 8 mit 50 % Tastgrad.

## Praxis
- 74HC595 ist der Klassiker für LED-Ketten, 7-Segment-Anzeigen und Relaisplatinen am µC (nur 3 Pins).
- SPI ist im Kern ein Schieberegister in Master und Slave, die ihre Inhalte austauschen.
- Mit XOR-Rückkopplung (LFSR) entstehen Pseudozufallsfolgen und CRC-Prüfsummen.
- Schieben um eine Stelle nach links = × 2 (wie `x << 1` im Code).
## 🔬 Genauer hingeschaut
- **Schieben und Übernehmen getrennt:** Der 74HC595 hat hinter dem Schieberegister ein zweites Register (Latch). Die Bits werden zuerst in Ruhe hineingeschoben, und erst ein Puls am Übernahme-Eingang zeigt alle gleichzeitig an. So flackern die Ausgänge beim Schieben nicht.
- **Kaskadieren:** Der serielle Ausgang eines Registers geht an den Eingang des nächsten. Mit drei Leitungen lassen sich so beliebig viele Ausgänge steuern – nur dauert das Schieben entsprechend länger.
- **LFSR:** Ein Schieberegister, dessen Eingang aus einer XOR-Verknüpfung einzelner Stufen kommt, erzeugt lange, scheinbar zufällige Bitfolgen. Das nutzt man für Pseudozufallszahlen, Verschlüsselung und Prüfsummen.
## 💡 Wusstest du?
- Die Prüfsumme (CRC), mit der Ethernet und viele andere Protokolle Übertragungsfehler erkennen, lässt sich mit genau so einem rückgekoppelten Schieberegister berechnen.
""",

    "tipps": [
        "Beim 74HC595 OE (Output Enable) mit Pull-up versehen – sonst leuchten beim Einschalten zufällige Ausgänge.",
    ],
    "fehler": [
        "Ringzähler ohne definierten Startzustand – nach dem Einschalten kreisen mehrere oder keine Einsen.",
        "Beim 74HC595 RCLK vergessen – die Ausgänge bleiben auf dem alten Stand.",
        "MSB/LSB-Reihenfolge zwischen Sender und Empfänger vertauscht.",
    ],
    "siehe_auch": ["flipflops", "zaehler", "bitmasken"],
    "rechner": ["frequenzteiler", "bitmaske"],
}
