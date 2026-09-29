# Thema: for-Schleife  (Kategorie: Kontrollstrukturen)
THEMA = {
    "titel": "for-Schleife",
    "reihenfolge": 3,
    "kurz": "Code eine bekannte Anzahl Mal wiederholen oder jedes Element einer Liste durchgehen.",
    "stichworte": ["for", "schleife", "loop", "foreach", "range", "zaehlschleife", "zählschleife",
                   "iterieren", "durchlaufen", "enumerate", "wiederholen", "for schleife", "for each"],

    "erklaerung": """
## Wann for?
Wenn **vorher klar ist, wie oft** wiederholt wird, oder wenn man **alle Elemente** einer Liste bzw. eines Arrays durchgehen will.
## Die klassische Zählschleife (C++ / C#)
`for (Start; Bedingung; Schritt)`
- **Start:** `int i = 0`, wird einmal am Anfang ausgeführt
- **Bedingung:** `i < 10`, wird VOR jedem Durchlauf geprüft
- **Schritt:** `i++`, wird NACH jedem Durchlauf ausgeführt
## Python ist anders
Python-`for` geht immer **über eine Sammlung**. Für Zahlen nimmt man `range()`:
- `range(5)` → 0, 1, 2, 3, 4  (**Ende nicht enthalten!**)
- `range(2, 8)` → 2 … 7
- `range(0, 10, 2)` → 0, 2, 4, 6, 8
- `range(10, 0, -1)` → 10 … 1 (rückwärts)
## foreach
Alle Elemente einer Sammlung durchgehen, ohne Index: C# `foreach`, C++ range-based `for (auto x : liste)`, Python `for x in liste`.
""",

    "bild": "for_schleife.png",
    "bild_text": "Ablauf einer for-Schleife: Start → Bedingung → Körper → Schritt",

    "beispiele": [
        {
            "titel": "Zählschleife 0 bis 4",
            "code": {
                "Python": r'''for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

for i in range(10, 0, -2):   # 10, 8, 6, 4, 2
    print(i, end=" ")''',
                "C++": r'''#include <iostream>

int main() {
    for (int i = 0; i < 5; i++) {        // Start; Bedingung; Schritt
        std::cout << i << "\n";
    }

    for (int i = 10; i > 0; i -= 2) {    // 10, 8, 6, 4, 2
        std::cout << i << " ";
    }
    return 0;
}''',
                "C#": r'''for (int i = 0; i < 5; i++)
{
    Console.WriteLine(i);
}

for (int i = 10; i > 0; i -= 2)      // 10, 8, 6, 4, 2
{
    Console.Write($"{i} ");
}''',
            },
            "ausgabe": "0\n1\n2\n3\n4\n10 8 6 4 2",
        },
        {
            "titel": "Über eine Liste iterieren (mit und ohne Index)",
            "code": {
                "Python": r'''messwerte = [12.1, 12.4, 11.9, 12.0]

# Nur Werte
for wert in messwerte:
    print(wert)

# Index UND Wert: enumerate
for index, wert in enumerate(messwerte):
    print(f"Messung {index}: {wert} V")

# Summe berechnen
summe = 0
for wert in messwerte:
    summe += wert
print("Mittelwert:", summe / len(messwerte))''',
                "C++": r'''#include <iostream>
#include <vector>

int main() {
    std::vector<double> messwerte = {12.1, 12.4, 11.9, 12.0};

    // range-based for (C++11): jedes Element
    for (double wert : messwerte) {
        std::cout << wert << "\n";
    }

    // mit Index
    for (size_t i = 0; i < messwerte.size(); i++) {
        std::cout << "Messung " << i << ": " << messwerte[i] << " V\n";
    }

    double summe = 0;
    for (const auto& wert : messwerte) {   // const auto& = keine Kopie
        summe += wert;
    }
    std::cout << "Mittelwert: " << summe / messwerte.size() << "\n";
    return 0;
}''',
                "C#": r'''var messwerte = new List<double> { 12.1, 12.4, 11.9, 12.0 };

// foreach: jedes Element
foreach (double wert in messwerte)
{
    Console.WriteLine(wert);
}

// mit Index
for (int i = 0; i < messwerte.Count; i++)
{
    Console.WriteLine($"Messung {i}: {messwerte[i]} V");
}

double summe = 0;
foreach (var wert in messwerte)
{
    summe += wert;
}
Console.WriteLine($"Mittelwert: {summe / messwerte.Count}");''',
            },
        },
        {
            "titel": "Verschachtelte Schleifen (z.B. Tabelle / Matrix)",
            "code": {
                "Python": r'''for zeile in range(1, 4):
    for spalte in range(1, 4):
        print(zeile * spalte, end="\t")
    print()     # neue Zeile''',
                "C++": r'''for (int zeile = 1; zeile <= 3; zeile++) {
    for (int spalte = 1; spalte <= 3; spalte++) {
        std::cout << zeile * spalte << "\t";
    }
    std::cout << "\n";
}''',
                "C#": r'''for (int zeile = 1; zeile <= 3; zeile++)
{
    for (int spalte = 1; spalte <= 3; spalte++)
    {
        Console.Write($"{zeile * spalte}\t");
    }
    Console.WriteLine();
}''',
            },
            "ausgabe": "1\t2\t3\n2\t4\t6\n3\t6\t9",
        },
    ],

    "tipps": [
        "Python: Statt `for i in range(len(liste))` lieber `for wert in liste` oder `enumerate()` verwenden.",
        "C++: In range-based for bei grossen Objekten `const auto&` nehmen, das vermeidet unnötige Kopien.",
        "Für Summen, Maximum usw. gibt es fertige Funktionen: Python `sum()`, `max()`; C# LINQ `.Sum()`, `.Max()`.",
    ],
    "fehler": [
        "Off-by-one: `i <= 5` statt `i < 5` macht einen Durchlauf zu viel. Beim Array-Zugriff führt das zum Absturz bzw. zu einer Exception.",
        "Eine Liste verändern (Elemente löschen), während man mit for darüber läuft.",
        "Python: `range(1, 10)` endet bei 9 und nicht bei 10.",
    ],
    "siehe_auch": ["while_schleife", "break_continue", "arrays_listen"],
}
