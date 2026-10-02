# Seite "Bitmasken"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Bitmasken und Bitoperationen",
    "reihenfolge": 30,
    "kurz": "Einzelne Bits in einem Register setzen, löschen, umschalten und prüfen – ohne die anderen zu verändern.",
    "stichworte": ["Bitmaske", "Maske", "Bitoperation", "AND", "OR", "XOR", "NOT", "Schieben", "Shift",
                   "Register", "Bit setzen", "Bit löschen", "Toggle", "Flag", "Read-Modify-Write", "Port"],

    "grafiken": ["werkzeug_bitmaske"],

    "erklaerung": """
## Grundlagen
In Registern eines Mikrocontrollers hat jedes Bit eine eigene Aufgabe (Pin-Richtung, Ausgangspegel, Interrupt-Freigabe, Statusflag). Eine **Maske** enthält genau an den Stellen eine 1, die man bearbeiten will.
- **setzen** `x |= m` (OR: 1 setzt, 0 lässt)
- **löschen** `x &= ~m` (AND mit invertierter Maske)
- **umschalten** `x ^= m` (XOR: 1 kippt, 0 lässt)
- **prüfen** `x & m` (AND: Ergebnis ≠ 0 → Bit gesetzt)
- **schieben** `x << n` (× 2^n), `x >> n` (÷ 2^n, abgerundet); herausgeschobene Bits gehen verloren
- Maske für Bit n: `(1 << n)`

## Vorgehen
1. Bitnummer(n) aus dem Datenblatt suchen (Bit 0 = LSB).
2. Maske bilden: `(1 << 3) | (1 << 5)` = `0x28`.
3. Passende Operation wählen – NIE das ganze Register überschreiben, wenn nur ein Bit geändert werden soll.
4. Mehrbit-Felder (z.B. Bits 4 … 6 = Vorteiler): erst löschen, dann den neuen Wert hineinschieben: `x = (x & ~(0x7 << 4)) | (wert << 4)`.
5. Feld auslesen: `(x >> 4) & 0x7`.

## Beispiel
Register x = `1010 0101` (0xA5), Bit 3 setzen:
- Maske `(1 << 3)` = `0000 1000`
- `x |= 0x08` → `1010 1101` (0xAD)

Bit 0 löschen:
- `x &= ~0x01` → `1010 0100` (0xA4)

Prüfen, ob Bit 7 gesetzt ist:
- `0xA5 & 0x80` = `0x80` ≠ 0 → ja

## Praxis
- AVR: `PORTB |= (1 << PB5);` schaltet die LED am Arduino-Pin 13 ein, `PINB & (1 << PB0)` liest einen Taster.
- STM32/ESP32: oft eigene Set/Reset-Register (BSRR, W1TS/W1TC) – schreiben ohne vorheriges Lesen, damit kein Interrupt dazwischen funkt (atomar).
- Read-Modify-Write auf Ports kann bei Open-Drain- oder belasteten Pins den falschen Zustand zurücklesen → Ausgangsregister (PORT/LAT) statt Eingangsregister (PIN) verändern.
- Programmier-Sicht (Operatoren in Python/C++/C#): Bereich Programmieren → „Zahlensysteme, Bits & Bytes“.
""",

    "tipps": [
        "Masken als (1 << n) schreiben statt als Zahl – so sieht man sofort, welches Bit gemeint ist.",
        "Für Flags in eigenem Code: Konstanten definieren (#define LED_AN (1 << 5)) statt Zahlen verstreuen.",
    ],
    "fehler": [
        "Bit mit x = (1 << 3) gesetzt – damit werden alle anderen Bits gelöscht (|= vergessen).",
        "Bit mit x &= (1 << 3) gelöscht – das löscht alle ANDEREN Bits (~ vergessen).",
        "Logisches && / || statt bitweisem & / | verwendet.",
    ],
    "siehe_auch": ["zahlensysteme_codes", "zweierkomplement_ueberlauf"],
    "rechner": ["bitmaske", "zahlensystem"],
}
