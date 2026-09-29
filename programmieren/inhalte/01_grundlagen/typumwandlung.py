# Thema: Typumwandlung (Casting)  (Kategorie: Grundlagen)
THEMA = {
    "titel": "Typumwandlung (Casting)",
    "reihenfolge": 5,
    "kurz": "Werte von einem Datentyp in einen anderen umwandeln: Text ↔ Zahl, double ↔ int.",
    "stichworte": ["cast", "casting", "umwandeln", "konvertieren", "parse", "tryparse", "stoi",
                   "to_string", "static_cast", "convert", "int()", "str()", "float()", "string zu int",
                   "text zu zahl", "implizit", "explizit"],

    "erklaerung": """
## Implizit vs. explizit
- **Implizit (automatisch):** Der Compiler wandelt selbst um, wenn **nichts verloren geht**, z.B. `int` → `double`.
- **Explizit (Cast):** Du erzwingst die Umwandlung, obwohl Information verloren gehen kann, z.B. `double` → `int` (Nachkommastellen fallen weg).
## Text ↔ Zahl
Eingaben von der Tastatur, aus Dateien oder von der seriellen Schnittstelle sind **immer Text**. Bevor man damit rechnen kann, muss man sie umwandeln. Das kann schiefgehen (z.B. bei "abc"), deshalb gehört eine Fehlerbehandlung dazu.
## Achtung beim Runden
- `int(3.9)` (Python), `static_cast<int>(3.9)` (C++) und `(int)3.9` (C#) **schneiden ab** → `3`
- `Convert.ToInt32(3.9)` in C# **rundet** → `4`. Bei `.5` rundet es auf die nächste gerade Zahl ("Banker's Rounding"): `Convert.ToInt32(2.5)` = `2`!
- Python `round(2.5)` = `2` (ebenfalls Banker's Rounding)
""",

    "tabelle": {
        "titel": "📊 Spickzettel Umwandlungen",
        "kopf": ["Von → Nach", "Python", "C++", "C#"],
        "zeilen": [
            ["Text → Ganzzahl", 'int("42")', 'std::stoi("42")', 'int.Parse("42")  /  int.TryParse(...)'],
            ["Text → Kommazahl", 'float("3.14")', 'std::stod("3.14")', 'double.Parse("3.14", CultureInfo.InvariantCulture)'],
            ["Zahl → Text", "str(42)", "std::to_string(42)", "42.ToString()"],
            ["double → int (abschneiden)", "int(3.9) → 3", "static_cast<int>(3.9) → 3", "(int)3.9 → 3"],
            ["int → double", "float(3)", "static_cast<double>(3)", "(double)3  oder implizit"],
            ["Zeichen → Code", 'ord("A") → 65', "(int)'A' → 65", "(int)'A' → 65"],
            ["Code → Zeichen", "chr(65) → 'A'", "(char)65", "(char)65"],
        ],
    },

    "beispiele": [
        {
            "titel": "Benutzereingabe sicher in eine Zahl umwandeln",
            "code": {
                "Python": r'''eingabe = input("Spannung in V: ")    # immer ein str!

try:
    spannung = float(eingabe.replace(",", "."))   # "4,7" erlauben
    print(f"Doppelt: {spannung * 2} V")
except ValueError:
    print("Das war keine Zahl!")''',
                "C++": r'''#include <iostream>
#include <string>

int main() {
    std::string eingabe;
    std::cout << "Spannung in V: ";
    std::getline(std::cin, eingabe);

    try {
        double spannung = std::stod(eingabe);    // wirft Exception bei "abc"
        std::cout << "Doppelt: " << spannung * 2 << " V\n";
    } catch (const std::invalid_argument&) {
        std::cout << "Das war keine Zahl!\n";
    }
    return 0;
}''',
                "C#": r'''using System.Globalization;

Console.Write("Spannung in V: ");
string? eingabe = Console.ReadLine();

// TryParse wirft KEINE Exception, sondern gibt true/false zurück
if (double.TryParse(eingabe?.Replace(",", "."), NumberStyles.Float,
                    CultureInfo.InvariantCulture, out double spannung))
{
    Console.WriteLine($"Doppelt: {spannung * 2} V");
}
else
{
    Console.WriteLine("Das war keine Zahl!");
}''',
            },
        },
        {
            "titel": "Casts zwischen Zahlentypen",
            "code": {
                "Python": r'''x = 3.9
print(int(x))        # 3   (abschneiden)
print(round(x))      # 4   (runden)
print(round(2.5))    # 2   (Banker's Rounding!)

a, b = 7, 2
print(a / b)         # 3.5 (in Python ergibt / immer einen float)''',
                "C++": r'''#include <iostream>
#include <cmath>

int main() {
    double x = 3.9;
    int abgeschnitten = static_cast<int>(x);     // 3  (moderner C++-Cast)
    int gerundet = static_cast<int>(std::round(x)); // 4

    int a = 7, b = 2;
    double ergebnis = static_cast<double>(a) / b;   // 3.5 (erst casten, DANN teilen)
    std::cout << abgeschnitten << " " << gerundet << " " << ergebnis << "\n";
    return 0;
}''',
                "C#": r'''double x = 3.9;
int abgeschnitten = (int)x;              // 3
int gerundet = (int)Math.Round(x);       // 4
int convert = Convert.ToInt32(2.5);      // 2  (Banker's Rounding!)

int a = 7, b = 2;
double ergebnis = (double)a / b;         // 3.5
Console.WriteLine($"{abgeschnitten} {gerundet} {convert} {ergebnis}");''',
            },
        },
    ],

    "tipps": [
        "C#: Für Benutzereingaben lieber `TryParse` als `Parse` verwenden. Das braucht kein try/catch.",
        "C#: Beim Umwandeln von Zahlen `CultureInfo.InvariantCulture` angeben. Sonst hängt es von der Windows-Spracheinstellung ab, ob `.` oder `,` als Dezimalzeichen gilt!",
        "C++: `static_cast<>` statt dem alten C-Cast `(int)x` verwenden. Das ist sicherer und im Code leichter zu finden.",
    ],
    "fehler": [
        "`(double)(a / b)` ergibt 3.0, weil zuerst als int geteilt wird. Richtig ist `(double)a / b`.",
        "Python: `int(\"3.5\")` gibt einen ValueError. Zuerst `float()`, dann `int()`.",
    ],
    "siehe_auch": ["datentypen", "ein_ausgabe", "fehlerbehandlung", "strings"],
}
