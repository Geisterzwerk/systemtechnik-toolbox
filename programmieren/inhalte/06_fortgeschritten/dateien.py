# Thema: Dateien lesen & schreiben  (Kategorie: Fortgeschritten)
THEMA = {
    "titel": "Dateien lesen & schreiben",
    "reihenfolge": 2,
    "kurz": "Textdateien, CSV und JSON speichern und laden, z.B. für Messwerte, Logs und Einstellungen.",
    "stichworte": ["datei", "file", "open", "lesen", "schreiben", "read", "write", "csv", "json",
                   "log", "speichern", "laden", "fstream", "ifstream", "ofstream", "streamreader",
                   "streamwriter", "readalllines", "pfad", "path", "with", "anhaengen", "append"],

    "erklaerung": """
## Dateimodi
- **Lesen** (`"r"`): Die Datei muss existieren
- **Schreiben** (`"w"`): erstellt die Datei neu, **ein bestehender Inhalt wird gelöscht!**
- **Anhängen** (`"a"`): schreibt ans Ende. Ideal für Logs und Messreihen.
## Immer schliessen
Eine offene Datei blockiert sie für andere Programme, und Daten landen evtl. nicht auf der Festplatte. Deshalb:
- **Python:** `with open(...) as f:`, das schliesst automatisch
- **C++:** `std::ifstream` / `std::ofstream` schliessen automatisch am Blockende (Destruktor)
- **C#:** `using`, oder `File.ReadAllText` / `File.WriteAllText`, die selbst öffnen und schliessen
## Formate
- **TXT:** einfacher Text, z.B. für Logs
- **CSV:** Tabelle mit Trennzeichen (`;`), öffnet sich direkt in Excel. Gut für Messreihen.
- **JSON:** strukturierte Daten (wie ein Dictionary). Ideal für Einstellungen und Konfigurationen.
## Encoding
Immer `utf-8` angeben, sonst werden Umlaute (ä, ö, ü, °) unter Windows falsch gespeichert.
""",

    "beispiele": [
        {
            "titel": "Textdatei schreiben, anhängen und lesen",
            "code": {
                "Python": r'''# Schreiben (überschreibt!)
with open("log.txt", "w", encoding="utf-8") as f:
    f.write("Messung gestartet\n")

# Anhängen
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("Temperatur: 23.5 °C\n")

# Lesen - Zeile für Zeile
with open("log.txt", "r", encoding="utf-8") as f:
    for zeile in f:
        print(zeile.strip())

# Ganze Datei auf einmal
text = open("log.txt", encoding="utf-8").read()''',
                "C++": r'''#include <fstream>
#include <iostream>
#include <string>

int main() {
    {   // Schreiben (überschreibt)
        std::ofstream datei("log.txt");
        datei << "Messung gestartet\n";
    }   // hier automatisch geschlossen

    {   // Anhängen
        std::ofstream datei("log.txt", std::ios::app);
        datei << "Temperatur: 23.5 C\n";
    }

    // Lesen
    std::ifstream datei("log.txt");
    if (!datei) {                                  // Fehler prüfen!
        std::cerr << "Datei nicht gefunden\n";
        return 1;
    }
    std::string zeile;
    while (std::getline(datei, zeile)) {
        std::cout << zeile << "\n";
    }
    return 0;
}''',
                "C#": r'''// Schreiben (überschreibt)
File.WriteAllText("log.txt", "Messung gestartet\n");

// Anhängen
File.AppendAllText("log.txt", "Temperatur: 23.5 °C\n");

// Lesen - alle Zeilen
foreach (string zeile in File.ReadAllLines("log.txt"))
{
    Console.WriteLine(zeile);
}

// Für grosse Dateien: Zeile für Zeile mit StreamReader
using var reader = new StreamReader("log.txt");
string? z;
while ((z = reader.ReadLine()) != null)
{
    Console.WriteLine(z);
}''',
            },
        },
        {
            "titel": "Messreihe als CSV speichern (öffnet in Excel)",
            "code": {
                "Python": r'''import csv

messungen = [("08:00", 22.1), ("08:05", 22.4), ("08:10", 23.0)]

with open("messung.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["Zeit", "Temperatur"])      # Kopfzeile
    writer.writerows(messungen)

with open("messung.csv", encoding="utf-8") as f:
    for zeile in csv.DictReader(f, delimiter=";"):
        print(zeile["Zeit"], float(zeile["Temperatur"]))''',
                "C++": r'''#include <fstream>
#include <vector>
#include <utility>
#include <string>

int main() {
    std::vector<std::pair<std::string, double>> messungen = {
        {"08:00", 22.1}, {"08:05", 22.4}, {"08:10", 23.0}
    };

    std::ofstream csv("messung.csv");
    csv << "Zeit;Temperatur\n";
    for (const auto& [zeit, temp] : messungen) {
        csv << zeit << ";" << temp << "\n";
    }
    return 0;
}''',
                "C#": r'''var messungen = new List<(string Zeit, double Temp)>
{
    ("08:00", 22.1), ("08:05", 22.4), ("08:10", 23.0)
};

var zeilen = new List<string> { "Zeit;Temperatur" };
foreach (var m in messungen)
{
    zeilen.Add($"{m.Zeit};{m.Temp}");
}
File.WriteAllLines("messung.csv", zeilen);''',
            },
        },
        {
            "titel": "Einstellungen als JSON speichern und laden",
            "code": {
                "Python": r'''import json

einstellungen = {"sprache": "Python", "dark_mode": True, "letzte_themen": ["while", "if_else"]}

with open("settings.json", "w", encoding="utf-8") as f:
    json.dump(einstellungen, f, indent=4, ensure_ascii=False)

with open("settings.json", encoding="utf-8") as f:
    geladen = json.load(f)                # -> dict
print(geladen["sprache"])''',
                "C#": r'''using System.Text.Json;

var einstellungen = new Einstellungen { Sprache = "C#", DarkMode = true };

string json = JsonSerializer.Serialize(einstellungen,
                                       new JsonSerializerOptions { WriteIndented = true });
File.WriteAllText("settings.json", json);

var geladen = JsonSerializer.Deserialize<Einstellungen>(File.ReadAllText("settings.json"));
Console.WriteLine(geladen?.Sprache);

class Einstellungen
{
    public string Sprache { get; set; } = "";
    public bool DarkMode { get; set; }
}''',
            },
            "hinweis": {
                "C++": "Die C++-Standardbibliothek hat kein JSON. Die bekannteste Bibliothek dafür ist **nlohmann/json** (eine einzelne Header-Datei).",
            },
        },
    ],

    "tipps": [
        "Pfade in Python mit `os.path.join()` oder `pathlib.Path` zusammenbauen, das funktioniert unter Windows UND Linux.",
        "Relative Pfade (`\"log.txt\"`) beziehen sich auf den Ordner, aus dem das Programm GESTARTET wird, und nicht auf den Ordner des Skripts. Deshalb nutzt diese Toolbox `config.BASIS_PFAD`.",
    ],
    "fehler": [
        "Modus `\"w\"` statt `\"a\"`: Die ganze bisherige Messreihe ist weg!",
        "Python CSV unter Windows ohne `newline=\"\"` ergibt leere Zeilen zwischen den Datensätzen.",
        "Datei ist in Excel geöffnet: Beim Schreiben kommt `PermissionError` bzw. `IOException`.",
    ],
    "siehe_auch": ["fehlerbehandlung", "strings", "dictionaries", "konstruktor"],
}
