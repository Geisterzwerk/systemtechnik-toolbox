# Thema: Strings (Text)  (Kategorie: Datenstrukturen)
THEMA = {
    "titel": "Strings (Text)",
    "reihenfolge": 3,
    "kurz": "Mit Text arbeiten: verbinden, teilen, suchen, ersetzen, zuschneiden.",
    "stichworte": ["string", "str", "text", "zeichenkette", "split", "join", "replace", "strip",
                   "trim", "substring", "find", "suchen", "ersetzen", "upper", "lower", "char",
                   "zeichen", "escape", "unicode", "utf-8", "verketten", "concat"],

    "erklaerung": """
## Was ist ein String?
Eine **Folge von Zeichen**. Man kann ihn wie eine Liste mit Index ansprechen: `text[0]` ist das erste Zeichen.
## Unveränderlich (immutable)
In **Python** und **C#** kann ein String nicht verändert werden. Jede "Änderung" (replace, upper, …) erzeugt einen **neuen** String. In **C++** ist `std::string` veränderbar.
## Escape-Zeichen
Sonderzeichen im Text werden mit einem Backslash geschrieben: `\\n` = neue Zeile, `\\t` = Tab, `\\"` = Anführungszeichen, `\\\\` = Backslash
- Für Windows-Pfade praktisch: Python `r"C:\\temp"`, C# `@"C:\\temp"` (dabei werden Backslashes NICHT als Escape gelesen)
""",

    "tabelle": {
        "titel": "📊 Wichtige String-Operationen",
        "kopf": ["Aktion", "Python", "C++ (std::string)", "C#"],
        "zeilen": [
            ["Länge", "len(s)", "s.length()", "s.Length"],
            ["Verbinden", 's1 + s2', "s1 + s2", "s1 + s2"],
            ["Teilstück", "s[2:5]", "s.substr(2, 3)", "s.Substring(2, 3)"],
            ["Suchen", 's.find("x")  (-1 = nicht da)', 's.find("x")  (npos = nicht da)', 's.IndexOf("x")  (-1)'],
            ["Enthält", '"x" in s', 's.find("x") != std::string::npos', 's.Contains("x")'],
            ["Ersetzen", 's.replace("a", "b")', "(Schleife mit find / replace)", 's.Replace("a", "b")'],
            ["Gross / klein", "s.upper()  s.lower()", "std::toupper je Zeichen", "s.ToUpper()  s.ToLower()"],
            ["Leerzeichen weg", "s.strip()", "(manuell / eigene Funktion)", "s.Trim()"],
            ["Aufteilen", 's.split(";")', "std::getline mit Trennzeichen", "s.Split(';')"],
            ["Liste → Text", '";".join(liste)', "(Schleife)", 'string.Join(";", liste)'],
            ["Beginnt mit", 's.startswith("AB")', 's.starts_with("AB") (C++20)', 's.StartsWith("AB")'],
        ],
    },

    "beispiele": [
        {
            "titel": "Eine Messzeile auseinandernehmen (z.B. von UART / CSV)",
            "code": {
                "Python": r'''zeile = "  TEMP;23.5;C  \n"

sauber = zeile.strip()                 # "TEMP;23.5;C"
teile = sauber.split(";")              # ["TEMP", "23.5", "C"]
name, wert, einheit = teile

print(name.lower())                    # temp
print(float(wert) + 1)                 # 24.5
print(f"{name}: {wert} °{einheit}")    # TEMP: 23.5 °C
print(";".join(teile))                 # zurück zusammenfügen''',
                "C++": r'''#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int main() {
    std::string zeile = "TEMP;23.5;C";

    // Aufteilen mit stringstream + getline
    std::vector<std::string> teile;
    std::stringstream ss(zeile);
    std::string teil;
    while (std::getline(ss, teil, ';')) {
        teile.push_back(teil);
    }

    double wert = std::stod(teile[1]);
    std::cout << teile[0] << ": " << wert + 1 << " " << teile[2] << "\n";

    if (zeile.find("TEMP") != std::string::npos) {
        std::cout << "Temperatur-Meldung\n";
    }
    return 0;
}''',
                "C#": r'''using System.Globalization;

string zeile = "  TEMP;23.5;C  ";

string[] teile = zeile.Trim().Split(';');          // ["TEMP", "23.5", "C"]
double wert = double.Parse(teile[1], CultureInfo.InvariantCulture);

Console.WriteLine(teile[0].ToLower());             // temp
Console.WriteLine(wert + 1);                       // 24.5
Console.WriteLine($"{teile[0]}: {wert} °{teile[2]}");
Console.WriteLine(string.Join(";", teile));

if (zeile.Contains("TEMP"))
{
    Console.WriteLine("Temperatur-Meldung");
}''',
            },
        },
    ],

    "unterschiede": """
- **Python:** `'text'` und `"text"` sind gleich. Mehrzeilige Strings mit `\"\"\"...\"\"\"`.
- **C++:** `"text"` ist ein String, `'t'` ist EIN Zeichen (char). Immer `std::string` verwenden, nicht `char*`.
- **C#:** `"text"` ist ein string, `'t'` ein char. `$"..."` für Interpolation, `@"..."` für wörtliche Strings.
""",

    "tipps": [
        "C#: Viele Strings in einer Schleife zusammenbauen? Dafür `StringBuilder` verwenden, das ist viel schneller als `+=`.",
        "Vor dem Vergleichen von Benutzereingaben `.strip()` / `.Trim()` und `.lower()` / `.ToLower()` anwenden.",
    ],
    "fehler": [
        "`\"5\" + \"3\"` ergibt `\"53\"` und nicht 8. Zuerst in Zahlen umwandeln!",
        "Python: `\"Wert: \" + 5` gibt einen TypeError. `str(5)` oder einen f-String verwenden.",
        "Windows-Pfad `\"C:\\neu\"`: `\\n` wird als Zeilenumbruch gelesen! Deshalb einen Raw-String verwenden.",
    ],
    "siehe_auch": ["typumwandlung", "arrays_listen", "ein_ausgabe", "dateien"],
}
