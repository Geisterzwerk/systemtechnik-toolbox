# Thema: Rekursion  (Kategorie: Funktionen)
THEMA = {
    "titel": "Rekursion",
    "reihenfolge": 4,
    "kurz": "Eine Funktion, die sich selbst aufruft. Braucht immer eine Abbruchbedingung.",
    "stichworte": ["rekursion", "rekursiv", "recursion", "fakultaet", "fakultät", "fibonacci",
                   "abbruchbedingung", "basisfall", "stack overflow", "selbstaufruf"],

    "erklaerung": """
## Prinzip
Ein Problem wird auf eine **kleinere Version desselben Problems** zurückgeführt:
- **Basisfall (Abbruchbedingung):** der einfachste Fall mit direkter Antwort, z.B. `0! = 1`
- **Rekursiver Fall:** Die Funktion ruft sich selbst mit einem kleineren Wert auf, z.B. `n! = n · (n−1)!`
## Achtung
Jeder Aufruf belegt Platz auf dem **Stack**. Ohne Abbruchbedingung oder bei zu tiefer Rekursion gibt es einen **Stack Overflow** (Python: `RecursionError`, Standardlimit ca. 1000 Aufrufe).
Jede Rekursion kann auch mit einer Schleife geschrieben werden. Die Schleife ist oft schneller.
## Typische Einsätze
Ordnerstrukturen durchsuchen (Ordner in Ordnern), Baumstrukturen, Sortierverfahren (Quicksort, Mergesort).
""",

    "beispiele": [
        {
            "titel": "Fakultät: 5! = 5 · 4 · 3 · 2 · 1 = 120",
            "code": {
                "Python": r'''def fakultaet(n):
    if n <= 1:                    # Basisfall -> Rekursion stoppt
        return 1
    return n * fakultaet(n - 1)   # rekursiver Aufruf

print(fakultaet(5))   # 120
# Ablauf: 5 * f(4) -> 5 * 4 * f(3) -> ... -> 5 * 4 * 3 * 2 * 1''',
                "C++": r'''#include <iostream>

long long fakultaet(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * fakultaet(n - 1);
}

int main() {
    std::cout << fakultaet(5) << "\n";   // 120
    return 0;
}''',
                "C#": r'''static long Fakultaet(int n)
{
    if (n <= 1)
    {
        return 1;
    }
    return n * Fakultaet(n - 1);
}

Console.WriteLine(Fakultaet(5));   // 120''',
            },
            "ausgabe": "120",
        },
        {
            "titel": "Alle Dateien in Unterordnern finden",
            "code": {
                "Python": r'''import os

def dateien_auflisten(ordner, ebene=0):
    for name in os.listdir(ordner):
        pfad = os.path.join(ordner, name)
        print("  " * ebene + name)
        if os.path.isdir(pfad):
            dateien_auflisten(pfad, ebene + 1)   # Rekursion für Unterordner

dateien_auflisten(".")''',
                "C++": r'''#include <filesystem>
#include <iostream>
namespace fs = std::filesystem;   // C++17

void auflisten(const fs::path& ordner, int ebene = 0) {
    for (const auto& eintrag : fs::directory_iterator(ordner)) {
        std::cout << std::string(ebene * 2, ' ') << eintrag.path().filename().string() << "\n";
        if (eintrag.is_directory()) {
            auflisten(eintrag.path(), ebene + 1);
        }
    }
}''',
                "C#": r'''static void Auflisten(string ordner, int ebene = 0)
{
    foreach (var pfad in Directory.GetFileSystemEntries(ordner))
    {
        Console.WriteLine(new string(' ', ebene * 2) + Path.GetFileName(pfad));
        if (Directory.Exists(pfad))
        {
            Auflisten(pfad, ebene + 1);
        }
    }
}

Auflisten(".");''',
            },
        },
    ],

    "fehler": [
        "Abbruchbedingung vergessen oder nie erreichbar (z.B. `fakultaet(-1)` bei der Prüfung `n == 0`) führt zu einer Endlosrekursion und einem Stack Overflow.",
        "Fakultät mit `int` berechnen: Ab 13! gibt es einen Überlauf bei 32 Bit. `long long` bzw. `long` verwenden.",
    ],
    "siehe_auch": ["funktionen_grundlagen", "while_schleife"],
}
