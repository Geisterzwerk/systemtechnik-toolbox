# Thema: switch / match  (Kategorie: Kontrollstrukturen)
THEMA = {
    "titel": "switch / match",
    "reihenfolge": 2,
    "kurz": "Einen Wert mit vielen festen Möglichkeiten vergleichen. Übersichtlicher als lange if-Ketten.",
    "stichworte": ["switch", "case", "match", "default", "fallthrough", "menue", "menü", "zustand",
                   "state machine", "zustandsautomat", "auswahl", "mehrfachauswahl"],

    "erklaerung": """
## Wann switch statt if?
Wenn **eine Variable** mit vielen **festen Werten** verglichen wird, z.B. Menüauswahl, Befehlscodes oder Zustände einer Zustandsmaschine.
## Wichtige Unterschiede
- **C++:** `switch` funktioniert nur mit **Ganzzahlen, char und enum**, nicht mit Strings! Ohne `break` läuft der Code in den nächsten `case` weiter (**Fallthrough**).
- **C#:** Funktioniert auch mit **Strings**. Vergessenes `break` ist ein **Compiler-Fehler** (kein versehentlicher Fallthrough). Seit C# 8 gibt es die kompakte **switch expression**.
- **Python:** Bis 3.9 gab es kein switch, man nutzte `if/elif` oder Dictionaries. Seit **Python 3.10** gibt es `match / case`.
""",

    "bild": "switch.png",
    "bild_text": "Ein Wert → genau ein passender Fall (oder default)",

    "beispiele": [
        {
            "titel": "Zustandsmaschine einer Maschine",
            "code": {
                "Python": r'''zustand = 2

# Python 3.10+
match zustand:
    case 0:
        print("AUS")
    case 1:
        print("STANDBY")
    case 2 | 3:                 # mehrere Werte
        print("LÄUFT")
    case _:                     # _ = default
        print("Unbekannter Zustand")

# Alternative (jede Python-Version): Dictionary
namen = {0: "AUS", 1: "STANDBY", 2: "LÄUFT"}
print(namen.get(zustand, "Unbekannt"))''',
                "C++": r'''#include <iostream>

int main() {
    int zustand = 2;

    switch (zustand) {
        case 0:
            std::cout << "AUS\n";
            break;                  // WICHTIG: sonst läuft es weiter!
        case 1:
            std::cout << "STANDBY\n";
            break;
        case 2:
        case 3:                     // gewollter Fallthrough: 2 und 3 gleich behandeln
            std::cout << "LAEUFT\n";
            break;
        default:
            std::cout << "Unbekannter Zustand\n";
    }
    return 0;
}''',
                "C#": r'''int zustand = 2;

switch (zustand)
{
    case 0:
        Console.WriteLine("AUS");
        break;
    case 1:
        Console.WriteLine("STANDBY");
        break;
    case 2:
    case 3:                         // leere cases dürfen zusammengefasst werden
        Console.WriteLine("LÄUFT");
        break;
    default:
        Console.WriteLine("Unbekannter Zustand");
        break;
}

// switch expression (C# 8+): gibt direkt einen Wert zurück
string text = zustand switch
{
    0 => "AUS",
    1 => "STANDBY",
    2 or 3 => "LÄUFT",
    _ => "Unbekannt"
};''',
            },
            "ausgabe": "LÄUFT",
        },
        {
            "titel": "Mit Text (Befehle auswerten)",
            "code": {
                "Python": r'''befehl = "start"

match befehl.lower():
    case "start":
        print("Motor startet")
    case "stop":
        print("Motor stoppt")
    case _:
        print(f"Unbekannter Befehl: {befehl}")''',
                "C++": r'''// C++: switch geht NICHT mit std::string -> if/else verwenden
std::string befehl = "start";

if (befehl == "start") {
    std::cout << "Motor startet\n";
} else if (befehl == "stop") {
    std::cout << "Motor stoppt\n";
} else {
    std::cout << "Unbekannter Befehl: " << befehl << "\n";
}''',
                "C#": r'''string befehl = "start";

switch (befehl.ToLower())
{
    case "start":
        Console.WriteLine("Motor startet");
        break;
    case "stop":
        Console.WriteLine("Motor stoppt");
        break;
    default:
        Console.WriteLine($"Unbekannter Befehl: {befehl}");
        break;
}''',
            },
        },
    ],

    "tipps": [
        "Für Zustände in C++/C# ein `enum` verwenden (`enum Zustand { Aus, Standby, Laeuft };`). Das ist lesbarer als Zahlen.",
        "Immer einen `default` / `case _` einbauen, der unerwartete Werte abfängt.",
    ],
    "fehler": [
        "C++: `break` vergessen. Dann wird der nächste case AUCH ausgeführt.",
        "C++: In einem case eine Variable deklarieren ohne `{ }` gibt einen Compiler-Fehler ('jump to case label'). Lösung: `case 1: { int x = 5; ... break; }`.",
        "Python < 3.10: `match` gibt einen SyntaxError. Python-Version prüfen mit `python --version`.",
    ],
    "siehe_auch": ["if_else", "dictionaries"],
}
