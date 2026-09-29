# Thema: Arrays & Listen  (Kategorie: Datenstrukturen)
THEMA = {
    "titel": "Arrays & Listen",
    "reihenfolge": 1,
    "kurz": "Viele Werte unter einem Namen speichern und über den Index darauf zugreifen.",
    "stichworte": ["array", "liste", "list", "vector", "feld", "index", "append", "push_back", "add",
                   "slicing", "tupel", "tuple", "sortieren", "sort", "laenge", "länge", "len", "size",
                   "count", "zweidimensional", "matrix", "list comprehension"],

    "erklaerung": """
## Array vs. Liste
- **Array:** feste Grösse, die beim Anlegen festgelegt wird. Die Elemente liegen direkt hintereinander im Speicher und sind deshalb sehr schnell.
- **Liste (dynamisches Array):** kann wachsen und schrumpfen. C++: `std::vector`, C#: `List<T>`, Python: `list`
## Der Index beginnt bei 0!
Bei 5 Elementen gehen die Indizes von **0 bis 4**. `liste[5]` ist ausserhalb:
- **Python / C#:** Fehlermeldung (`IndexError` / `IndexOutOfRangeException`)
- **C++ mit `[]`:** **keine Prüfung**. Man liest oder überschreibt fremden Speicher (undefiniertes Verhalten)! Sicher ist `.at(i)`.
## Python-Besonderheiten
- Negative Indizes: `liste[-1]` ist das letzte Element
- **Slicing:** `liste[1:3]` gibt die Elemente 1 und 2 zurück, `liste[::-1]` die umgedrehte Liste
- Eine Liste kann gemischte Typen enthalten (sollte man aber vermeiden)
- **Tupel** `(1, 2, 3)` ist wie eine Liste, aber unveränderlich
""",

    "bild": "array_index.png",
    "bild_text": "Ein Array im Speicher: Index 0 bis n−1",

    "tabelle": {
        "titel": "📊 Wichtige Operationen",
        "kopf": ["Aktion", "Python (list)", "C++ (std::vector)", "C# (List<T>)"],
        "zeilen": [
            ["Anlegen", "w = [1, 2, 3]", "std::vector<int> w = {1, 2, 3};", "var w = new List<int> { 1, 2, 3 };"],
            ["Anzahl", "len(w)", "w.size()", "w.Count  (Array: .Length)"],
            ["Lesen", "w[0]", "w[0]  /  w.at(0)", "w[0]"],
            ["Hinten anfügen", "w.append(4)", "w.push_back(4);", "w.Add(4);"],
            ["Einfügen an Pos. 1", "w.insert(1, 9)", "w.insert(w.begin() + 1, 9);", "w.Insert(1, 9);"],
            ["Entfernen (Wert)", "w.remove(9)", "std::erase(w, 9); (C++20)", "w.Remove(9);"],
            ["Entfernen (Index)", "del w[0] / w.pop(0)", "w.erase(w.begin());", "w.RemoveAt(0);"],
            ["Enthalten?", "9 in w", "std::find(...) != w.end()", "w.Contains(9)"],
            ["Sortieren", "w.sort()", "std::sort(w.begin(), w.end());", "w.Sort();"],
            ["Leeren", "w.clear()", "w.clear();", "w.Clear();"],
        ],
    },

    "beispiele": [
        {
            "titel": "Array / Liste anlegen, lesen, ändern",
            "code": {
                "Python": r'''messwerte = [12.1, 12.4, 11.9]

print(messwerte[0])       # 12.1  (erstes Element)
print(messwerte[-1])      # 11.9  (letztes Element)
messwerte[1] = 12.5       # ändern
messwerte.append(12.0)    # hinzufügen
print(len(messwerte))     # 4
print(messwerte[1:3])     # [12.5, 11.9]  (Slicing)

# List Comprehension: neue Liste in einer Zeile erzeugen
in_mv = [w * 1000 for w in messwerte]
gueltig = [w for w in messwerte if w > 12]''',
                "C++": r'''#include <iostream>
#include <vector>
#include <array>

int main() {
    // Festes Array (Grösse 3, fix)
    std::array<double, 3> fest = {12.1, 12.4, 11.9};
    int klassisch[3] = {1, 2, 3};          // C-Array (alter Stil)

    // Dynamische Liste
    std::vector<double> messwerte = {12.1, 12.4, 11.9};
    std::cout << messwerte[0] << "\n";            // 12.1
    std::cout << messwerte.back() << "\n";        // 11.9 (letztes)
    messwerte[1] = 12.5;
    messwerte.push_back(12.0);
    std::cout << messwerte.size() << "\n";        // 4

    // messwerte[10]    -> KEIN Fehler, sondern undefiniertes Verhalten!
    // messwerte.at(10) -> wirft std::out_of_range (sicher)
    return 0;
}''',
                "C#": r'''// Festes Array
double[] fest = { 12.1, 12.4, 11.9 };
int[] leer = new int[5];              // 5 Elemente, alle 0
Console.WriteLine(fest.Length);        // 3

// Dynamische Liste
var messwerte = new List<double> { 12.1, 12.4, 11.9 };
Console.WriteLine(messwerte[0]);                   // 12.1
Console.WriteLine(messwerte[^1]);                  // 11.9 (letztes, C# 8)
messwerte[1] = 12.5;
messwerte.Add(12.0);
Console.WriteLine(messwerte.Count);                // 4

// LINQ (using System.Linq): wie Python List Comprehension
var inMv = messwerte.Select(w => w * 1000).ToList();
var gueltig = messwerte.Where(w => w > 12).ToList();''',
            },
        },
        {
            "titel": "Zweidimensional (Matrix / Tabelle)",
            "code": {
                "Python": r'''matrix = [
    [1, 2, 3],
    [4, 5, 6],
]
print(matrix[1][2])        # 6  (Zeile 1, Spalte 2)

for zeile in matrix:
    print(zeile)''',
                "C++": r'''int matrix[2][3] = {
    {1, 2, 3},
    {4, 5, 6},
};
std::cout << matrix[1][2];   // 6

// dynamisch:
std::vector<std::vector<int>> m = {{1, 2, 3}, {4, 5, 6}};''',
                "C#": r'''int[,] matrix = {
    { 1, 2, 3 },
    { 4, 5, 6 },
};
Console.WriteLine(matrix[1, 2]);           // 6
Console.WriteLine(matrix.GetLength(0));    // 2 Zeilen''',
            },
        },
    ],

    "tipps": [
        "In C++ fast immer `std::vector` statt C-Arrays verwenden. Er kennt seine Grösse und verwaltet den Speicher selbst.",
        "Python: `sorted(liste)` gibt eine NEUE sortierte Liste zurück, `liste.sort()` sortiert die bestehende.",
    ],
    "fehler": [
        "Index `len(liste)` bzw. `size()` verwenden: Das letzte gültige Element hat den Index `Länge − 1`!",
        "Python: `b = a` kopiert die Liste NICHT. Beide Namen zeigen auf dieselbe Liste. Eine Kopie macht man mit `b = a.copy()` oder `b = list(a)`.",
    ],
    "siehe_auch": ["for_schleife", "dictionaries", "strings", "pointer_referenzen"],
}
