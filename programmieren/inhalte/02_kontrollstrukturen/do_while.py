# Thema: do-while-Schleife  (Kategorie: Kontrollstrukturen)
THEMA = {
    "titel": "do-while-Schleife",
    "reihenfolge": 5,
    "kurz": "Zuerst ausführen, dann prüfen. Läuft also mindestens einmal.",
    "stichworte": ["do", "do while", "dowhile", "fussgesteuert", "fußgesteuert", "mindestens einmal",
                   "schleife", "loop", "eingabe wiederholen"],

    "erklaerung": """
## Prinzip
Die Bedingung wird **nach** dem Durchlauf geprüft (fussgesteuert). Der Block läuft deshalb **immer mindestens einmal**.
## Typischer Einsatz
Eingaben abfragen, **bis** sie gültig sind. Man muss ja zuerst mindestens einmal fragen.
## Python
Python hat **kein do-while**. Man baut es mit `while True` und `break` am Ende nach.
""",

    "bild": "do_while.png",
    "bild_text": "do-while: Zuerst ausführen, dann prüfen",

    "beispiele": [
        {
            "titel": "Eingabe wiederholen, bis sie gültig ist (1–10)",
            "code": {
                "Python": r'''# Python hat kein do-while -> nachbauen:
while True:
    zahl = int(input("Zahl von 1 bis 10: "))
    if 1 <= zahl <= 10:          # Bedingung AM ENDE prüfen
        break
print("Danke:", zahl)''',
                "C++": r'''#include <iostream>

int main() {
    int zahl;
    do {
        std::cout << "Zahl von 1 bis 10: ";
        std::cin >> zahl;
    } while (zahl < 1 || zahl > 10);    // Semikolon am Ende!

    std::cout << "Danke: " << zahl << "\n";
    return 0;
}''',
                "C#": r'''int zahl;
do
{
    Console.Write("Zahl von 1 bis 10: ");
    zahl = int.Parse(Console.ReadLine() ?? "0");
} while (zahl < 1 || zahl > 10);        // Semikolon am Ende!

Console.WriteLine($"Danke: {zahl}");''',
            },
        },
    ],

    "tabelle": {
        "titel": "📊 while vs. do-while",
        "kopf": ["", "while", "do-while"],
        "zeilen": [
            ["Prüfung", "vor dem Durchlauf (kopfgesteuert)", "nach dem Durchlauf (fussgesteuert)"],
            ["Mindestanzahl Durchläufe", "0", "1"],
            ["Typischer Einsatz", "warten, solange etwas gilt", "Eingabe abfragen, bis gültig"],
        ],
    },

    "fehler": [
        "C++/C#: Das Semikolon nach `while (...)` beim do-while vergessen.",
        "Die Variable für die Bedingung INNERHALB des do-Blocks deklarieren. Nach der `}` ist sie nicht mehr sichtbar, darum vorher deklarieren.",
    ],
    "siehe_auch": ["while_schleife", "break_continue"],
}
