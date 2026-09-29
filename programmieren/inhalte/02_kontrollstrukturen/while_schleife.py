# Thema: while-Schleife  (Kategorie: Kontrollstrukturen)
THEMA = {
    "titel": "while-Schleife",
    "reihenfolge": 4,
    "kurz": "Wiederholen, SOLANGE eine Bedingung wahr ist. Die Anzahl Durchläufe ist vorher unbekannt.",
    "stichworte": ["while", "schleife", "loop", "solange", "endlosschleife", "while true",
                   "kopfgesteuert", "wiederholen", "wile", "while schleife", "polling", "warten"],

    "erklaerung": """
## Prinzip
Die Bedingung wird **vor jedem Durchlauf** geprüft (kopfgesteuert). Ist sie gleich am Anfang falsch, läuft die Schleife **kein einziges Mal**.
## Wann while statt for?
Wenn man **nicht weiss, wie oft** wiederholt werden muss:
- warten, bis ein Sensor einen Wert erreicht
- Eingabe wiederholen, bis sie gültig ist
- Hauptschleife eines Programms oder Mikrocontrollers (`while True` / `while (true)`)
## Endlosschleifen
Wird die Bedingung nie falsch, läuft die Schleife ewig. Manchmal ist das gewollt (Server, Mikrocontroller-Loop, Menü). Dann braucht es aber einen Ausstieg mit `break`.
""",

    "bild": "while_schleife.png",
    "bild_text": "while: Zuerst prüfen, dann ausführen",

    "beispiele": [
        {
            "titel": "Kondensator laden, bis 99 % erreicht sind",
            "code": {
                "Python": r'''spannung = 0.0
ziel = 5.0 * 0.99
schritt = 0

while spannung < ziel:          # prüfen VOR jedem Durchlauf
    spannung += (5.0 - spannung) * 0.2
    schritt += 1

print(f"Nach {schritt} Schritten: {spannung:.2f} V")''',
                "C++": r'''#include <iostream>

int main() {
    double spannung = 0.0;
    const double ziel = 5.0 * 0.99;
    int schritt = 0;

    while (spannung < ziel) {
        spannung += (5.0 - spannung) * 0.2;
        schritt++;
    }
    std::cout << "Nach " << schritt << " Schritten: " << spannung << " V\n";
    return 0;
}''',
                "C#": r'''double spannung = 0.0;
const double ziel = 5.0 * 0.99;
int schritt = 0;

while (spannung < ziel)
{
    spannung += (5.0 - spannung) * 0.2;
    schritt++;
}
Console.WriteLine($"Nach {schritt} Schritten: {spannung:F2} V");''',
            },
            "ausgabe": "Nach 21 Schritten: 4.95 V",
        },
        {
            "titel": "Menü-Schleife mit Ausstieg (gewollte Endlosschleife)",
            "code": {
                "Python": r'''while True:                      # läuft "für immer"
    auswahl = input("1=Messen, q=Beenden: ")
    if auswahl == "q":
        break                        # Schleife verlassen
    if auswahl == "1":
        print("Messe ...")
print("Programm beendet")''',
                "C++": r'''#include <iostream>
#include <string>

int main() {
    std::string auswahl;
    while (true) {
        std::cout << "1=Messen, q=Beenden: ";
        std::getline(std::cin, auswahl);
        if (auswahl == "q") {
            break;
        }
        if (auswahl == "1") {
            std::cout << "Messe ...\n";
        }
    }
    std::cout << "Programm beendet\n";
    return 0;
}''',
                "C#": r'''while (true)
{
    Console.Write("1=Messen, q=Beenden: ");
    string? auswahl = Console.ReadLine();
    if (auswahl == "q")
    {
        break;
    }
    if (auswahl == "1")
    {
        Console.WriteLine("Messe ...");
    }
}
Console.WriteLine("Programm beendet");''',
            },
        },
    ],

    "tipps": [
        "Bei Endlosschleifen, die auf Hardware warten, einen **Timeout** einbauen (maximale Wartezeit oder Anzahl Versuche).",
        "Programm hängt in einer Endlosschleife? Im Terminal mit `Ctrl + C` abbrechen.",
        "In GUI-Programmen (customtkinter) KEIN `while True` verwenden, das friert das Fenster ein. Stattdessen `widget.after(ms, funktion)` benutzen.",
    ],
    "fehler": [
        "Die Variable in der Bedingung wird in der Schleife nie verändert. Das ergibt eine ungewollte Endlosschleife.",
        "Kommazahlen mit `!=` prüfen (`while x != 1.0`). Wegen der Rundungsfehler wird x vielleicht nie genau 1.0. Besser `<` verwenden.",
    ],
    "siehe_auch": ["do_while", "for_schleife", "break_continue"],
}
