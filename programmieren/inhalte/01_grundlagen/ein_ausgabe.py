# Thema: Ein- und Ausgabe  (Kategorie: Grundlagen)
THEMA = {
    "titel": "Ein- und Ausgabe",
    "reihenfolge": 7,
    "kurz": "Text auf der Konsole ausgeben, Eingaben einlesen und Zahlen schön formatieren.",
    "stichworte": ["print", "input", "cout", "cin", "console", "writeline", "readline", "ausgabe",
                   "eingabe", "formatieren", "f-string", "interpolation", "nachkommastellen",
                   "setprecision", "format", "konsole", "terminal"],

    "erklaerung": """
## Ausgabe
- **Python:** `print()`. Mehrere Werte mit Komma trennen, Formatierung mit **f-Strings**: `f"U = {u:.2f} V"`
- **C++:** `std::cout << wert;`  Mit `<<` werden Teile aneinandergehängt, `"\\n"` oder `std::endl` macht eine neue Zeile.
- **C#:** `Console.WriteLine()` mit Zeilenumbruch, `Console.Write()` ohne. Formatierung mit **String-Interpolation**: `$"U = {u:F2} V"`
## Eingabe
Eingaben kommen **immer als Text** an und müssen für Berechnungen umgewandelt werden (siehe *Typumwandlung*).
- **Python:** `input("Frage: ")` gibt einen `str` zurück
- **C++:** `std::cin >> zahl;` liest bis zum nächsten Leerzeichen. Für ganze Zeilen `std::getline(std::cin, text);`
- **C#:** `Console.ReadLine()` gibt einen `string?` zurück (kann null sein)
""",

    "tabelle": {
        "titel": "📊 Zahlen formatieren",
        "kopf": ["Ziel", "Python", "C++", "C#"],
        "zeilen": [
            ["2 Nachkommastellen", 'f"{x:.2f}"', "std::fixed << std::setprecision(2) << x", '$"{x:F2}"'],
            ["Breite 8, rechtsbündig", 'f"{x:>8}"', "std::setw(8) << x", '$"{x,8}"'],
            ["Führende Nullen", 'f"{n:04d}"  → 0042', "std::setw(4) << std::setfill('0') << n", '$"{n:D4}"'],
            ["Hex", 'f"{n:X}"', "std::hex << n", '$"{n:X}"'],
            ["Tausendertrennung", 'f"{n:,}"', "(locale nötig)", '$"{n:N0}"'],
            ["Prozent", 'f"{0.25:.0%}"  → 25%', "x * 100 << \"%\"", '$"{0.25:P0}"'],
        ],
        "hinweis": "C++ `setprecision`, `setw`, `setfill` brauchen `#include <iomanip>`. Ab C++20 gibt es auch `std::format(\"{:.2f}\", x)`, ähnlich wie in Python.",
    },

    "beispiele": [
        {
            "titel": "Einlesen, rechnen, formatiert ausgeben",
            "code": {
                "Python": r'''name = input("Name: ")
u = float(input("Spannung (V): "))
i = float(input("Strom (A): "))

p = u * i
print(f"Hallo {name}!")
print(f"Leistung: {p:.2f} W")         # 2 Nachkommastellen
print("U =", u, "V", sep=" ")         # mehrere Werte, Trennzeichen
print("ohne Zeilenumbruch", end="")''',
                "C++": r'''#include <iostream>
#include <iomanip>   // setprecision
#include <string>

int main() {
    std::string name;
    double u, i;

    std::cout << "Name: ";
    std::getline(std::cin, name);        // ganze Zeile (mit Leerzeichen)
    std::cout << "Spannung (V): ";
    std::cin >> u;                       // liest direkt eine Zahl
    std::cout << "Strom (A): ";
    std::cin >> i;

    double p = u * i;
    std::cout << "Hallo " << name << "!\n";
    std::cout << std::fixed << std::setprecision(2)
              << "Leistung: " << p << " W\n";
    return 0;
}''',
                "C#": r'''Console.Write("Name: ");
string name = Console.ReadLine() ?? "";           // ?? "" -> falls null
Console.Write("Spannung (V): ");
double u = double.Parse(Console.ReadLine() ?? "0");
Console.Write("Strom (A): ");
double i = double.Parse(Console.ReadLine() ?? "0");

double p = u * i;
Console.WriteLine($"Hallo {name}!");
Console.WriteLine($"Leistung: {p:F2} W");         // 2 Nachkommastellen''',
            },
            "ausgabe": "Hallo Jorick!\nLeistung: 12.00 W",
        },
    ],

    "tipps": [
        "Python-f-Strings können rechnen: `f\"{u * i:.1f} W\"`. Zum Debuggen gibt es `f\"{u=}\"`, das gibt `u=12.0` aus.",
        "C++: `\"\\n\"` ist schneller als `std::endl`, weil `endl` zusätzlich den Puffer leert.",
    ],
    "fehler": [
        "C++: Nach `std::cin >> zahl;` bleibt das Enter im Puffer. Ein folgendes `getline` liest dann eine leere Zeile. Lösung: vorher `std::cin.ignore();` aufrufen.",
        "Python: `input()` gibt Text zurück. `input() + 5` ergibt einen TypeError.",
    ],
    "siehe_auch": ["typumwandlung", "strings", "dateien"],
}
