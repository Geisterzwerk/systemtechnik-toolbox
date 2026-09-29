# Thema: Datentypen & Speichergrössen  (Kategorie: Grundlagen)
THEMA = {
    "titel": "Datentypen & Speichergrössen",
    "reihenfolge": 3,
    "kurz": "Welcher Typ speichert was, wie viele Bit braucht er und welcher Wertebereich ist möglich?",
    "stichworte": ["datentyp", "int", "float", "double", "char", "bool", "string", "str", "byte",
                   "long", "short", "decimal", "bit", "bits", "groesse", "speicher", "wertebereich",
                   "sizeof", "unsigned", "signed", "uint8_t", "int32_t", "ganzzahl", "kommazahl",
                   "gleitkomma", "overflow", "typ"],

    "erklaerung": """
## Warum Datentypen?
Im Speicher liegen nur Bits. Erst der **Datentyp** sagt, wie diese Bits gelesen werden: als Ganzzahl, als Kommazahl oder als Buchstabe. Er legt ausserdem fest, **wie viel Speicher** eine Variable belegt und **welcher Wertebereich** möglich ist.
## Die Grundregel für den Wertebereich
Mit **n Bit** gibt es `2^n` Kombinationen:
- **unsigned** (nur positiv): `0 … 2^n − 1`  z.B. 8 Bit: 0 … 255
- **signed** (mit Vorzeichen, Zweierkomplement): `−2^(n−1) … 2^(n−1) − 1`  z.B. 8 Bit: −128 … 127
## Ganzzahlen vs. Gleitkommazahlen
- **Ganzzahlen** (int, long, …) sind exakt, haben aber einen festen Bereich. Wird er überschritten, gibt es einen **Overflow**.
- **Gleitkommazahlen** (float, double) haben einen riesigen Bereich, sind aber **nicht exakt**. `0.1 + 0.2` ergibt `0.30000000000000004`.
- **float** hat ca. 7 gültige Stellen, **double** ca. 15–16. Im Zweifel `double` nehmen.
- **C# decimal** rechnet dezimal-exakt (28–29 Stellen). Ideal für Geldbeträge.
## Python ist anders
- `int` ist in Python **unbegrenzt gross**. Es gibt keinen Overflow, Python nimmt einfach mehr Speicher.
- `float` ist in Python immer ein 64-Bit-**double**.
- Jeder Wert ist ein Objekt mit Zusatzinfos. `sys.getsizeof(1)` ergibt **28 Byte** (64-Bit-System), obwohl die Zahl selbst nur 4 Byte bräuchte.
""",

    "bild": "datentypen_bits.png",
    "bild_text": "Speichergrösse der wichtigsten Datentypen in Bit",

    "tabellen": [
        {
            "titel": "📊 Ganzzahlen (Integer)",
            "kopf": ["Bit", "Wertebereich", "C++", "C#", "Python"],
            "zeilen": [
                ["8 signed", "−128 … 127", "int8_t / signed char", "sbyte", "int"],
                ["8 unsigned", "0 … 255", "uint8_t / unsigned char", "byte", "int"],
                ["16 signed", "−32 768 … 32 767", "int16_t / short", "short", "int"],
                ["16 unsigned", "0 … 65 535", "uint16_t / unsigned short", "ushort", "int"],
                ["32 signed", "−2 147 483 648 … 2 147 483 647  (±2.1 Mrd.)", "int32_t / int (!)", "int", "int"],
                ["32 unsigned", "0 … 4 294 967 295", "uint32_t / unsigned int", "uint", "int"],
                ["64 signed", "±9.22 · 10¹⁸", "int64_t / long long", "long", "int"],
                ["64 unsigned", "0 … 1.8 · 10¹⁹", "uint64_t / unsigned long long", "ulong", "int"],
                ["beliebig", "nur durch RAM begrenzt", "–", "BigInteger", "int ✅"],
            ],
            "hinweis": "**(!) C++-Achtung:** Die Grösse von `int` und `long` ist in C++ NICHT fest vorgeschrieben. `int` hat heute fast immer 32 Bit. `long` hat unter **Windows 32 Bit**, unter **Linux (64-Bit) aber 64 Bit**! Auf kleinen Mikrocontrollern (z.B. Arduino Uno) ist `int` nur **16 Bit** gross. Wer eine feste Grösse braucht, nimmt `int32_t` usw. aus `<cstdint>`. In C# sind alle Grössen fest.",
        },
        {
            "titel": "📊 Kommazahlen, Zeichen, Wahrheitswerte",
            "kopf": ["Typ", "Bit", "Genauigkeit / Inhalt", "C++", "C#", "Python"],
            "zeilen": [
                ["Gleitkomma einfach", "32", "≈ 7 Stellen, ±3.4 · 10³⁸", "float", "float", "–"],
                ["Gleitkomma doppelt", "64", "≈ 15–16 Stellen, ±1.7 · 10³⁰⁸", "double", "double", "float ✅"],
                ["Dezimal", "128", "28–29 Stellen, exakt dezimal", "–", "decimal", "decimal.Decimal"],
                ["Wahrheitswert", "8 (1 Byte)", "true / false", "bool", "bool", "bool (True/False)"],
                ["Zeichen", "8 / 16", "ein Buchstabe", "char (8 Bit)", "char (16 Bit, UTF-16)", "– (str mit Länge 1)"],
                ["Text", "variabel", "Zeichenkette", "std::string", "string", "str"],
                ["Nichts", "–", "kein Wert", "void / nullptr", "void / null", "None"],
            ],
            "hinweis": "Ein `bool` bräuchte theoretisch nur 1 Bit. Der Computer kann aber nur ganze Bytes adressieren, deshalb belegt er 1 Byte.",
        },
    ],

    "beispiele": [
        {
            "titel": "Datentypen verwenden und Grösse abfragen",
            "code": {
                "Python": r'''import sys

ganz = 42                 # int   (unbegrenzt gross)
komma = 3.14              # float (intern immer 64-Bit double)
text = "Hallo"            # str
wahr = True               # bool

print(type(ganz), type(komma), type(text), type(wahr))

# Speicherbedarf des Python-OBJEKTS in Byte (inkl. Verwaltungsdaten)
print(sys.getsizeof(ganz))       # 28
print(sys.getsizeof(2**100))     # 40  -> wächst mit der Zahl

# Kein Overflow in Python:
print(2 ** 100)                  # 1267650600228229401496703205376''',
                "C++": r'''#include <iostream>
#include <cstdint>    // int8_t, uint16_t, int32_t, ...
#include <climits>    // INT_MAX, INT_MIN

int main() {
    int ganz = 42;
    double komma = 3.14;
    float klein = 3.14f;         // f am Ende = float-Literal
    char zeichen = 'A';          // einfache Anführungszeichen!
    bool wahr = true;
    uint8_t sensorwert = 200;    // garantiert 8 Bit, 0..255

    // sizeof gibt die Grösse in BYTE zurück
    std::cout << "int:    " << sizeof(int)    << " Byte\n";   // meist 4
    std::cout << "double: " << sizeof(double) << " Byte\n";   // 8
    std::cout << "char:   " << sizeof(char)   << " Byte\n";   // 1
    std::cout << "long:   " << sizeof(long)   << " Byte\n";   // Windows 4, Linux 8!
    std::cout << "INT_MAX = " << INT_MAX << "\n";            // 2147483647
    return 0;
}''',
                "C#": r'''int ganz = 42;
double komma = 3.14;
float klein = 3.14f;          // f = float-Literal
decimal geld = 19.95m;        // m = decimal-Literal
char zeichen = 'A';
bool wahr = true;
byte sensorwert = 200;        // 0..255

// sizeof gibt die Grösse in BYTE (in C# immer gleich, egal welcher PC)
Console.WriteLine($"int:     {sizeof(int)} Byte");      // 4
Console.WriteLine($"long:    {sizeof(long)} Byte");     // 8
Console.WriteLine($"char:    {sizeof(char)} Byte");     // 2 (UTF-16)
Console.WriteLine($"decimal: {sizeof(decimal)} Byte");  // 16
Console.WriteLine($"int.MaxValue = {int.MaxValue}");    // 2147483647''',
            },
        },
        {
            "titel": "Overflow: Was passiert beim Überlauf?",
            "text": "Ein 8-Bit-Wert (unsigned) kann maximal 255 speichern. Rechnet man +1, fällt er auf 0 zurück, wie ein Kilometerzähler.",
            "code": {
                "Python": r'''# Python-int läuft nie über:
x = 255
x += 1
print(x)            # 256

# Einen 8-Bit-Überlauf "nachbauen" (z.B. für Mikrocontroller-Logik):
print((255 + 1) % 256)   # 0''',
                "C++": r'''#include <iostream>
#include <cstdint>

int main() {
    uint8_t x = 255;
    x = x + 1;                      // Überlauf -> 0 (unsigned ist definiert)
    std::cout << (int)x << "\n";    // 0  ((int), sonst wird es als Zeichen ausgegeben)

    int y = 2147483647;             // INT_MAX
    // y = y + 1;  -> signed Overflow = "undefiniertes Verhalten" in C++! Vermeiden!
    return 0;
}''',
                "C#": r'''byte x = 255;
x++;                               // Überlauf -> 0
Console.WriteLine(x);              // 0

int y = int.MaxValue;
// Mit checked wirft C# eine Exception statt still überzulaufen:
checked
{
    y = y + 1;                     // OverflowException!
}''',
            },
            "ausgabe": "0",
        },
        {
            "titel": "Gleitkomma-Ungenauigkeit",
            "code": {
                "Python": r'''print(0.1 + 0.2)             # 0.30000000000000004
print(0.1 + 0.2 == 0.3)      # False !

# Richtig vergleichen: mit Toleranz
import math
print(math.isclose(0.1 + 0.2, 0.3))   # True''',
                "C++": r'''#include <iostream>
#include <cmath>

int main() {
    double a = 0.1 + 0.2;
    std::cout << (a == 0.3) << "\n";                    // 0 (false)
    std::cout << (std::fabs(a - 0.3) < 1e-9) << "\n";   // 1 (true) -> mit Toleranz
    return 0;
}''',
                "C#": r'''double a = 0.1 + 0.2;
Console.WriteLine(a == 0.3);                      // False
Console.WriteLine(Math.Abs(a - 0.3) < 1e-9);      // True

decimal b = 0.1m + 0.2m;
Console.WriteLine(b == 0.3m);                     // True  (decimal ist exakt)''',
            },
        },
    ],

    "unterschiede": """
- **Python:** wenige Typen, keine Grössenwahl, kein Overflow. Einfach, aber mehr Speicherbedarf pro Wert.
- **C++:** viele Typen, Grössen teils **plattformabhängig**. Für Embedded und Hardware immer `<cstdint>`-Typen (`uint8_t`, `int16_t`, …) verwenden.
- **C#:** feste Grössen auf jedem System, zusätzlich `decimal` für exaktes Rechnen.
""",

    "tipps": [
        "Faustregel: Ganzzahl → `int`, Kommazahl → `double`, Geld (C#) → `decimal`.",
        "Registerwerte, Sensordaten und Protokolle (UART, I2C, Modbus) mit festen Typen wie `uint8_t` / `uint16_t` bzw. `byte` / `ushort` speichern.",
        "Kommazahlen nie mit `==` vergleichen, sondern immer mit einer Toleranz.",
    ],
    "fehler": [
        "C++: `char` mit `cout` ausgeben zeigt das ZEICHEN (z.B. 'A') und nicht die Zahl. Mit `(int)` umwandeln.",
        "`float x = 3.14;` in C#: Fehler, weil 3.14 ein double ist. Es muss `3.14f` heissen.",
        "Ganzzahl-Division: `7 / 2` ergibt in C++/C# `3` und nicht 3.5 (siehe Operatoren).",
    ],
    "siehe_auch": ["zahlensysteme", "typumwandlung", "operatoren", "variablen"],
}
