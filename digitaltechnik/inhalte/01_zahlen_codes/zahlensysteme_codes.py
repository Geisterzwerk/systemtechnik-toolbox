# Seite "Zahlensysteme und Codes"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Zahlensysteme und Codes",
    "reihenfolge": 10,
    "kurz": "Dezimal, Binär, Hexadezimal, Oktal – und Codes wie BCD, Gray und ASCII: dieselbe Zahl, verschiedene Schreibweisen.",
    "stichworte": ["Zahlensystem", "Binär", "Dual", "Hexadezimal", "Hex", "Oktal", "Stellenwertsystem", "Basis",
                   "Bit", "Byte", "Nibble", "BCD", "Gray-Code", "ASCII", "MSB", "LSB", "Umrechnen"],

    "grafiken": ["werkzeug_zahlensystem"],

    "erklaerung": """
## Grundlagen
Alle üblichen Zahlensysteme sind **Stellenwertsysteme**: Jede Stelle hat die Wertigkeit `Basis^Stelle` (rechts Stelle 0).
- **Dezimal** (Basis 10): Ziffern 0 … 9
- **Binär / Dual** (Basis 2): Ziffern 0 und 1 – so speichert die Hardware. Bit 0 = **LSB** (niederwertigstes Bit), das linke Bit = **MSB**.
- **Hexadezimal** (Basis 16): Ziffern 0 … 9, A … F. Eine Hex-Ziffer = genau **4 Bit** (Nibble) → kompakte Schreibweise für Bitmuster: `0xC8 = 1100 1000`.
- **Oktal** (Basis 8): eine Ziffer = 3 Bit (Unix-Dateirechte `chmod 755`).
- Mit n Bit gibt es `2^n` Muster (8 Bit: 0 … 255).

**Codes** ordnen Bitmustern eine Bedeutung zu:
- **BCD** (8421): jede Dezimalziffer einzeln in 4 Bit – 59 = `0101 1001`. Einfach anzuzeigen (7-Segment, RTC-Uhren-ICs), verschenkt aber 6 von 16 Mustern.
- **Gray-Code**: benachbarte Zahlen unterscheiden sich in genau EINEM Bit (`g = n XOR (n >> 1)`). Bei Drehgebern kann so beim Übergang kein falscher Zwischenwert entstehen.
- **ASCII**: 7-Bit-Zeichencode, z.B. `'A' = 0x41 = 65`, `'0' = 0x30`.

## Vorgehen
- **Dezimal → Binär**: wiederholt durch 2 teilen, die Reste von unten nach oben lesen. Oder: grösste passende Zweierpotenz abziehen (128, 64, 32 …).
- **Binär → Dezimal**: gesetzte Bits mit ihren Wertigkeiten addieren.
- **Binär ↔ Hex**: von rechts in 4er-Gruppen teilen, jede Gruppe einzeln umwandeln (`1010 = A`, `1111 = F`).
- **Hex → Dezimal**: `0x2F = 2 · 16 + 15 = 47`.
- **Benötigte Bits**: `n = ⌈log2(Wert + 1)⌉` (unsigned).

## Beispiel
200 dezimal:
- 200 = 128 + 64 + 8 → Bits 7, 6 und 3 gesetzt → `1100 1000`
- Gruppen `1100 | 1000` → `C | 8` → `0xC8`
- Oktal: `11 001 000` → `0o310`
- BCD: `0010 0000 0000` (drei Ziffern = 12 Bit)
- Gray: `200 XOR 100 = 172` → `1010 1100`

## Praxis
- Datenblätter und Register: fast immer hexadezimal (`0x3F`), Bitnummern ab 0 von rechts.
- In C/C++/Python: `0b1100`, `0xC8`; in VHDL `x"C8"`; in Datenblättern auch `C8h`.
- Speicher und Adressen: 1 KiB = 1024 Byte = 0x400, 64 KiB = 0x10000 (16 Adressbits).
- Programmier-Sicht (Datentypen, Bit-Operatoren im Code): Bereich Programmieren → „Zahlensysteme, Bits & Bytes“.
""",

    "tipps": [
        "Die Zweierpotenzen bis 2^10 = 1024 und die Hex-Ziffern A … F auswendig kennen spart viel Zeit.",
        "Ein Byte = zwei Hex-Ziffern: 0x00 … 0xFF – darum schreiben Debugger und Logikanalysatoren hex.",
    ],
    "fehler": [
        "Bitnummern ab 1 statt ab 0 gezählt – Bit 3 hat die Wertigkeit 8, nicht 4.",
        "BCD und binär verwechselt: 0x59 ist in BCD die Zahl 59, binär aber 89.",
        "Führende Nullen weggelassen und dadurch Bitpositionen verschoben (8 Bit immer vollständig schreiben).",
    ],
    "siehe_auch": ["zweierkomplement_ueberlauf", "bitmasken"],
    "rechner": ["zahlensystem"],
}
