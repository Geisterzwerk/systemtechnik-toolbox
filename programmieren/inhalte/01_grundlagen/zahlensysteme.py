# Thema: Zahlensysteme, Bits & Bytes  (Kategorie: Grundlagen)
THEMA = {
    "titel": "Zahlensysteme, Bits & Bytes",
    "reihenfolge": 4,
    "kurz": "Binär, Hexadezimal, Zweierkomplement und Bit-Operationen. Wichtig für Hardware und Embedded.",
    "stichworte": ["binaer", "binär", "hex", "hexadezimal", "dezimal", "bit", "byte", "nibble",
                   "zweierkomplement", "bitmaske", "maske", "bitoperation", "shift", "schieben",
                   "and", "or", "xor", "0x", "0b", "register", "msb", "lsb"],

    "erklaerung": """
## Die drei wichtigen Zahlensysteme
- **Dezimal (Basis 10):** Ziffern 0–9, normales Rechnen
- **Binär (Basis 2):** Ziffern 0 und 1. So speichert der Computer alles. Schreibweise im Code: `0b1010`
- **Hexadezimal (Basis 16):** Ziffern 0–9 und A–F. **Eine Hex-Ziffer entspricht genau 4 Bit (ein Nibble).** So lassen sich Bytes kompakt schreiben: `0xFF` = `0b11111111` = 255
## Bit, Nibble, Byte
- 1 **Bit** = 0 oder 1
- 1 **Nibble** = 4 Bit = eine Hex-Ziffer
- 1 **Byte** = 8 Bit = zwei Hex-Ziffern (`0x00` … `0xFF`)
- **MSB** = höchstwertiges Bit (ganz links), **LSB** = niederwertigstes Bit (ganz rechts, Bit 0)
## Negative Zahlen: Zweierkomplement
So werden signed-Zahlen gespeichert: **alle Bits invertieren und dann +1**.
- `+5` = `0000 0101`
- invertiert = `1111 1010`, +1 = `1111 1011` = **−5**
- Das MSB ist bei negativen Zahlen immer 1.
## Bit-Operationen
Damit setzt, löscht oder prüft man einzelne Bits, z.B. in Registern von Mikrocontrollern oder in Status-Bytes von Sensoren.
""",

    "bild": "zahlensysteme.png",
    "bild_text": "Ein Byte: Bit-Wertigkeiten, Binär und Hex",

    "tabelle": {
        "titel": "📊 Bit-Operatoren (in allen drei Sprachen gleich)",
        "kopf": ["Operator", "Name", "Beispiel", "Ergebnis", "Typische Verwendung"],
        "zeilen": [
            ["&", "UND (AND)", "0b1100 & 0b1010", "0b1000", "Bit prüfen / Bits löschen (maskieren)"],
            ["|", "ODER (OR)", "0b1100 | 0b1010", "0b1110", "Bit setzen"],
            ["^", "Exklusiv-ODER (XOR)", "0b1100 ^ 0b1010", "0b0110", "Bit umschalten (toggeln)"],
            ["~", "NICHT (invertieren)", "~0b0000_1111 (8 Bit)", "0b1111_0000", "Maske umdrehen"],
            ["<<", "Links schieben", "1 << 3", "0b1000 = 8", "Maske für Bit n erzeugen, ×2"],
            [">>", "Rechts schieben", "0b1000 >> 2", "0b0010 = 2", "Bits auslesen, ÷2"],
        ],
    },

    "beispiele": [
        {
            "titel": "Zahlen in verschiedenen Systemen",
            "code": {
                "Python": r'''zahl = 200

print(bin(zahl))           # 0b11001000
print(hex(zahl))           # 0xc8
print(f"{zahl:08b}")       # 11001000   (8 Stellen, mit führenden Nullen)
print(f"{zahl:02X}")       # C8

# Zurück in Dezimal
print(int("11001000", 2))  # 200
print(int("C8", 16))       # 200
print(0xC8, 0b11001000)    # 200 200''',
                "C++": r'''#include <iostream>
#include <bitset>
#include <string>

int main() {
    int zahl = 200;
    std::cout << std::bitset<8>(zahl) << "\n";          // 11001000
    std::cout << std::hex << std::uppercase << zahl << "\n";  // C8
    std::cout << std::dec;                              // zurück auf dezimal

    // Text -> Zahl
    int a = std::stoi("11001000", nullptr, 2);          // 200
    int b = std::stoi("C8", nullptr, 16);               // 200
    std::cout << a << " " << b << " " << 0xC8 << "\n";
    return 0;
}''',
                "C#": r'''int zahl = 200;

Console.WriteLine(Convert.ToString(zahl, 2).PadLeft(8, '0'));  // 11001000
Console.WriteLine(zahl.ToString("X2"));                        // C8

// Text -> Zahl
int a = Convert.ToInt32("11001000", 2);   // 200
int b = Convert.ToInt32("C8", 16);        // 200
Console.WriteLine($"{a} {b} {0xC8} {0b1100_1000}");''',
            },
        },
        {
            "titel": "Bits setzen, löschen, umschalten und prüfen",
            "text": "Klassiker aus der Embedded-Welt: Ein Status-Register mit 8 Bit, wir arbeiten mit Bit 3.",
            "code": {
                "Python": r'''register = 0b0000_0000
BIT = 3

register |= (1 << BIT)          # Bit 3 SETZEN       -> 0b00001000
ist_gesetzt = (register >> BIT) & 1   # Bit 3 PRÜFEN -> 1
register ^= (1 << BIT)          # Bit 3 UMSCHALTEN   -> 0b00000000
register |= 0b1111_0000
register &= ~(1 << 7)           # Bit 7 LÖSCHEN      -> 0b01110000

print(f"{register:08b}")        # 01110000''',
                "C++": r'''#include <cstdint>
#include <bitset>
#include <iostream>

int main() {
    uint8_t reg = 0;
    const int BIT = 3;

    reg |= (1 << BIT);                // Bit setzen
    bool gesetzt = (reg >> BIT) & 1;  // Bit prüfen
    reg ^= (1 << BIT);                // Bit umschalten
    reg |= 0xF0;
    reg &= ~(1 << 7);                 // Bit löschen

    std::cout << std::bitset<8>(reg) << "\n";   // 01110000
    return 0;
}''',
                "C#": r'''byte reg = 0;
const int BIT = 3;

reg |= (byte)(1 << BIT);             // Bit setzen   (Cast nötig: Ergebnis ist int)
bool gesetzt = ((reg >> BIT) & 1) == 1;
reg ^= (byte)(1 << BIT);             // Bit umschalten
reg |= 0xF0;
reg &= unchecked((byte)~(1 << 7));   // Bit löschen

Console.WriteLine(Convert.ToString(reg, 2).PadLeft(8, '0'));  // 01110000''',
            },
            "ausgabe": "01110000",
        },
    ],

    "tipps": [
        "Hex ↔ Binär im Kopf: Jede Hex-Ziffer einzeln in 4 Bit umwandeln. Beispiel `0xA5` = `1010 0101`.",
        "Unterstriche machen lange Zahlen lesbar: `0b1111_0000` (Python, C#) bzw. `0b1111'0000` (C++14).",
    ],
    "fehler": [
        "Bitoperatoren `&` `|` mit logischen Operatoren `&&` `||` (bzw. `and`/`or` in Python) verwechseln.",
        "Klammern vergessen: `reg & 1 << 3` wird wegen der Operator-Rangfolge anders ausgewertet als gedacht. Immer klammern!",
        "Python: `~5` ergibt `-6`, weil Python-ints unbegrenzt sind. Für 8 Bit: `~5 & 0xFF`.",
    ],
    "siehe_auch": ["datentypen", "operatoren"],
}
