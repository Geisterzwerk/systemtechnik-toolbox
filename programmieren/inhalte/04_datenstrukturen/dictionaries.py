# Thema: Dictionaries / Maps  (Kategorie: Datenstrukturen)
THEMA = {
    "titel": "Dictionaries / Maps",
    "reihenfolge": 2,
    "kurz": "Werte unter einem Schlüssel speichern (Schlüssel → Wert), wie ein Nachschlagewerk.",
    "stichworte": ["dictionary", "dict", "map", "unordered_map", "hashmap", "schluessel", "schlüssel",
                   "key", "value", "wert", "zuordnung", "nachschlagen", "json", "set", "menge"],

    "erklaerung": """
## Prinzip
Statt über einen Index (0, 1, 2, …) greift man über einen **Schlüssel** zu, z.B. einen Namen:
`farbcode["Rot"]` → `2`
- Jeder Schlüssel kommt **nur einmal** vor
- Das Nachschlagen ist **sehr schnell**, auch bei Millionen Einträgen (Hash-Tabelle)
## Namen in den Sprachen
- **Python:** `dict`, z.B. `{"Rot": 2, "Orange": 3}`
- **C++:** `std::map` (sortiert) oder `std::unordered_map` (schneller, unsortiert)
- **C#:** `Dictionary<TKey, TValue>`
## Set (Menge)
Wie ein Dictionary, aber nur mit Schlüsseln. Es speichert jeden Wert **nur einmal** und eignet sich gut zum Entfernen von Duplikaten. Python `set`, C++ `std::set`, C# `HashSet<T>`.
""",

    "beispiele": [
        {
            "titel": "Widerstands-Farbcode als Dictionary",
            "code": {
                "Python": r'''farbcode = {"Schwarz": 0, "Braun": 1, "Rot": 2, "Orange": 3}

print(farbcode["Rot"])              # 2
farbcode["Gelb"] = 4                # hinzufügen / ändern
print("Grün" in farbcode)           # False  (Schlüssel vorhanden?)
print(farbcode.get("Grün", -1))     # -1  (Standardwert statt Fehler)
del farbcode["Schwarz"]             # löschen

for farbe, wert in farbcode.items():   # Schlüssel UND Wert
    print(f"{farbe:8} = {wert}")''',
                "C++": r'''#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> farbcode = {
        {"Schwarz", 0}, {"Braun", 1}, {"Rot", 2}, {"Orange", 3}
    };

    std::cout << farbcode["Rot"] << "\n";        // 2
    farbcode["Gelb"] = 4;                        // hinzufügen / ändern
    bool vorhanden = farbcode.count("Gruen") > 0; // false
    farbcode.erase("Schwarz");

    for (const auto& [farbe, wert] : farbcode) { // C++17
        std::cout << farbe << " = " << wert << "\n";
    }
    return 0;
}
// ACHTUNG: farbcode["Gruen"] LEGT einen Eintrag mit 0 AN, wenn er fehlt!''',
                "C#": r'''var farbcode = new Dictionary<string, int>
{
    ["Schwarz"] = 0, ["Braun"] = 1, ["Rot"] = 2, ["Orange"] = 3
};

Console.WriteLine(farbcode["Rot"]);             // 2
farbcode["Gelb"] = 4;                           // hinzufügen / ändern
bool vorhanden = farbcode.ContainsKey("Grün");  // false
if (farbcode.TryGetValue("Grün", out int wert)) // sicher lesen
{
    Console.WriteLine(wert);
}
farbcode.Remove("Schwarz");

foreach (var (farbe, w) in farbcode)
{
    Console.WriteLine($"{farbe,-8} = {w}");
}''',
            },
        },
        {
            "titel": "Duplikate entfernen mit einem Set",
            "code": {
                "Python": r'''ids = [3, 1, 3, 2, 1]
eindeutig = set(ids)          # {1, 2, 3}
print(sorted(eindeutig))      # [1, 2, 3]''',
                "C++": r'''#include <set>
std::vector<int> ids = {3, 1, 3, 2, 1};
std::set<int> eindeutig(ids.begin(), ids.end());   // {1, 2, 3} (sortiert)''',
                "C#": r'''int[] ids = { 3, 1, 3, 2, 1 };
var eindeutig = new HashSet<int>(ids);   // {3, 1, 2}
// oder mit LINQ: ids.Distinct()''',
            },
        },
    ],

    "tipps": [
        "Dictionaries sind die Grundlage von **JSON**. Python `json.load()` liefert direkt ein dict.",
        "Ein Dictionary kann lange `if/elif`-Ketten ersetzen (siehe switch / match).",
    ],
    "fehler": [
        "Python: `d[\"fehlt\"]` gibt einen `KeyError`. Besser `.get()` verwenden oder vorher mit `in` prüfen.",
        "C#: `d[\"fehlt\"]` wirft eine `KeyNotFoundException`. Besser `TryGetValue` verwenden.",
        "C++: `map[\"fehlt\"]` legt still einen neuen Eintrag an. Zum Prüfen `.count()`, `.find()` oder `.contains()` (C++20) nutzen.",
    ],
    "siehe_auch": ["arrays_listen", "switch_match", "dateien"],
}
