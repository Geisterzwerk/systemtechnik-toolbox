# Thema: Wie ein Programm läuft  (Kategorie: Grundlagen)
THEMA = {
    "titel": "Wie ein Programm läuft",
    "reihenfolge": 1,
    "kurz": "Kompiliert oder interpretiert? Aufbau eines Programms und das erste 'Hallo Welt'.",
    "stichworte": ["compiler", "interpreter", "kompilieren", "hello world", "hallo welt", "main",
                   "programmaufbau", "einstieg", "start", "anfang", "runtime", ".net", "exe"],

    "erklaerung": """
## Vom Quellcode zum laufenden Programm
Ein Computer versteht nur **Maschinencode** (Nullen und Einsen). Der Code, den wir schreiben (Quellcode), muss also übersetzt werden. Dafür gibt es zwei Wege:
- **Kompilieren (C++):** Ein Compiler übersetzt den ganzen Code VOR dem Start in eine `.exe`. Fehler werden schon beim Kompilieren gefunden. Das Programm ist sehr schnell.
- **Interpretieren (Python):** Der Interpreter liest den Code zur Laufzeit Zeile für Zeile und führt ihn direkt aus. Kein Kompilieren nötig, dafür langsamer. Viele Fehler merkt man erst, wenn die Zeile ausgeführt wird.
- **Zwischenweg (C#):** Der Compiler erzeugt einen Zwischencode (IL). Die .NET-Laufzeit übersetzt ihn beim Ausführen in Maschinencode (JIT = Just-In-Time).
## Der Einstiegspunkt
- **C++ / C#:** Jedes Programm startet in der Funktion `main` (C#: `Main`).
- **Python:** Die Datei wird von oben nach unten ausgeführt. Mit `if __name__ == "__main__":` markiert man den Startpunkt, wenn die Datei direkt gestartet wird.
## Statement-Ende und Blöcke
- **Python:** Zeilenende = Befehlsende. Blöcke werden durch **Einrückung** gebildet.
- **C++ / C#:** Jeder Befehl endet mit `;`. Blöcke stehen in geschweiften Klammern `{ }`.
""",

    "bild": "programmablauf.png",
    "bild_text": "Kompiliert (C++), JIT (C#) und interpretiert (Python)",

    "beispiele": [
        {
            "titel": "Hallo Welt",
            "code": {
                "Python": r'''# Python: kein main() nötig, der Code läuft von oben nach unten
def main():
    print("Hallo Welt")      # print() gibt Text aus


# Startpunkt: nur ausführen, wenn DIESE Datei gestartet wird
if __name__ == "__main__":
    main()''',
                "C++": r'''#include <iostream>   // Bibliothek für Ein-/Ausgabe einbinden

// Hier startet jedes C++-Programm
int main() {
    std::cout << "Hallo Welt" << std::endl;   // Text ausgeben
    return 0;                                  // 0 = Programm erfolgreich beendet
}''',
                "C#": r'''using System;   // Namespace mit Console usw.

class Program
{
    // Hier startet jedes C#-Programm
    static void Main()
    {
        Console.WriteLine("Hallo Welt");   // Text ausgeben
    }
}''',
            },
            "ausgabe": "Hallo Welt",
        },
        {
            "titel": "Kompilieren und Starten im Terminal",
            "code": {
                "Python": r'''# Kein Kompilieren nötig - direkt starten:
python hallo.py''',
                "C++": r'''# 1. Kompilieren (erstellt hallo.exe bzw. ./hallo)
g++ -std=c++17 -Wall hallo.cpp -o hallo
# 2. Starten
./hallo''',
                "C#": r'''# Neues Projekt anlegen und starten (.NET SDK)
dotnet new console -n Hallo
cd Hallo
dotnet run''',
            },
        },
    ],

    "unterschiede": """
- **Python:** interpretiert, dynamisch typisiert, Einrückung statt Klammern. Ideal zum Automatisieren, für Tools, Daten und Skripte.
- **C++:** kompiliert, sehr schnell, direkter Zugriff auf Speicher (Pointer). Typisch für Embedded, Mikrocontroller, Treiber, Games.
- **C#:** kompiliert zu .NET, automatische Speicherverwaltung. Typisch für Windows-Programme, GUIs, Industrie-Software, Unity.
""",

    "tipps": [
        "Beim C++-Compiler immer `-Wall` verwenden: So zeigt er Warnungen an, die auf versteckte Fehler hinweisen.",
        "C# ab .NET 6 kennt **Top-Level-Statements**: Man darf `class Program` und `Main` weglassen und den Code direkt in `Program.cs` schreiben. Viele Beispiele in diesem Wiki nutzen diese Kurzform.",
        "In VS Code: Python mit F5 starten. Für C++ braucht es zusätzlich einen Compiler (z.B. MinGW / g++).",
    ],
    "fehler": [
        "C++/C#: `;` am Ende vergessen führt zu einem Compiler-Fehler, oft erst in der NÄCHSTEN Zeile gemeldet.",
        "Python: Tabs und Leerzeichen gemischt führen zu `IndentationError`. Immer 4 Leerzeichen verwenden.",
    ],
    "siehe_auch": ["variablen", "kommentare", "ein_ausgabe"],
}
