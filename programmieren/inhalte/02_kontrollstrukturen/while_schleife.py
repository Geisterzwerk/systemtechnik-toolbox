# Thema: while-Schleife  (Kategorie: Kontrollstrukturen)
THEMA = {
    "titel": "while-Schleife",
    "reihenfolge": 4,
    "kurz": "Wiederholen, SOLANGE eine Bedingung wahr ist. Die Anzahl Durchläufe ist vorher unbekannt.",
    "stichworte": ["while", "schleife", "loop", "solange", "endlosschleife", "while true",
                   "kopfgesteuert", "wiederholen", "wile", "while schleife", "polling", "warten"],

    "erklaerung": """
## Stell dir vor …
Du stellst Wasser auf den Herd und **wartest, bis es kocht**. Wie lange das dauert, weisst du vorher nicht – du schaust einfach immer wieder nach. Die while-Schleife macht genau das: Sie wiederholt, solange eine Bedingung gilt, und hört auf, sobald sie nicht mehr gilt.
## Prinzip
Die Bedingung wird **vor jedem Durchlauf** geprüft (kopfgesteuert). Ist sie gleich am Anfang falsch, läuft die Schleife **kein einziges Mal**.
## Wann while statt for?
Wenn man **nicht weiss, wie oft** wiederholt werden muss:
- warten, bis ein Sensor einen Wert erreicht
- Eingabe wiederholen, bis sie gültig ist
- Hauptschleife eines Programms oder Mikrocontrollers (`while True` / `while (true)`)
## Endlosschleifen
Wird die Bedingung nie falsch, läuft die Schleife ewig. Manchmal ist das gewollt (Server, Mikrocontroller-Loop, Menü). Dann braucht es aber einen Ausstieg mit `break`.
## 🔬 Genauer hingeschaut
- **Aktives Warten frisst Rechenzeit:** Eine Schleife, die nur ständig eine Bedingung prüft, lastet einen Prozessorkern voll aus. Mit einer kurzen Pause (`time.sleep(0.01)`) oder einem Ereignis statt dem Dauerprüfen bleibt der Rechner ruhig.
- **Immer eine Notbremse:** Beim Warten auf ein Gerät oder eine Netzwerkantwort gehört ein **Timeout** dazu – sonst hängt das Programm für immer, wenn das Gerät nie antwortet.
- **Kommazahl als Bedingung:** `while x != 1.0: x += 0.1` hört nie auf, weil x durch Rundungsfehler 1.0 nie genau trifft. Besser `while x < 1.0`.
## 💡 Wusstest du?
- In jedem Arduino-Programm steckt eine versteckte Endlosschleife: Das Hauptprogramm ruft deine Funktion `loop()` einfach immer und immer wieder auf.
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
