# Thema: if / else  (Kategorie: Kontrollstrukturen)
THEMA = {
    "titel": "if / else if / else",
    "reihenfolge": 1,
    "kurz": "Entscheidungen treffen: Code nur ausführen, wenn eine Bedingung erfüllt ist.",
    "stichworte": ["if", "else", "elif", "else if", "ifelse", "if else", "bedingung", "verzweigung",
                   "entscheidung", "wenn", "dann", "sonst", "if schleife", "abfrage", "condition"],

    "erklaerung": """
## Prinzip
`if` prüft eine **Bedingung**, also einen Ausdruck, der wahr oder falsch ist.
- Ist sie **wahr**, wird der Block darunter ausgeführt.
- `else if` (Python: `elif`) prüft eine weitere Bedingung, **aber nur, wenn alle vorherigen falsch waren**.
- `else` fängt alle übrigen Fälle ab.
Es wird **immer höchstens EIN Block** ausgeführt, und zwar der erste, dessen Bedingung zutrifft. Deshalb ist die Reihenfolge wichtig!
## Hinweis
`if` ist **keine Schleife**. Der Block wird höchstens einmal ausgeführt. Wiederholungen macht man mit `for` oder `while`.
""",

    "bild": "if_else.png",
    "bild_text": "Flussdiagramm: if / else if / else",

    "beispiele": [
        {
            "titel": "Temperatur auswerten",
            "code": {
                "Python": r'''temperatur = 65

if temperatur >= 80:
    print("ALARM: Überhitzung!")
elif temperatur >= 60:          # nur geprüft, wenn >= 80 falsch war
    print("Warnung: warm")
else:
    print("OK")

# Einzeiler (ternär):
status = "warm" if temperatur >= 60 else "OK"''',
                "C++": r'''#include <iostream>

int main() {
    int temperatur = 65;

    if (temperatur >= 80) {                 // Bedingung in ( )
        std::cout << "ALARM: Ueberhitzung!\n";
    } else if (temperatur >= 60) {
        std::cout << "Warnung: warm\n";
    } else {
        std::cout << "OK\n";
    }

    // Einzeiler (ternärer Operator):
    const char* status = (temperatur >= 60) ? "warm" : "OK";
    return 0;
}''',
                "C#": r'''int temperatur = 65;

if (temperatur >= 80)
{
    Console.WriteLine("ALARM: Überhitzung!");
}
else if (temperatur >= 60)
{
    Console.WriteLine("Warnung: warm");
}
else
{
    Console.WriteLine("OK");
}

string status = temperatur >= 60 ? "warm" : "OK";''',
            },
            "ausgabe": "Warnung: warm",
        },
        {
            "titel": "Verschachtelt und mit mehreren Bedingungen",
            "code": {
                "Python": r'''spannung = 23.8
sicherung_ok = True

if sicherung_ok:
    if 22.0 <= spannung <= 26.0:        # Python kann Bereiche direkt prüfen
        print("Versorgung im Toleranzbereich")
    else:
        print("Spannung ausserhalb!")
else:
    print("Sicherung prüfen")

# Besser lesbar, ohne Verschachtelung:
if sicherung_ok and 22.0 <= spannung <= 26.0:
    print("Alles OK")''',
                "C++": r'''double spannung = 23.8;
bool sicherungOk = true;

if (sicherungOk && spannung >= 22.0 && spannung <= 26.0) {
    std::cout << "Alles OK\n";
} else if (!sicherungOk) {                 // ! = NICHT
    std::cout << "Sicherung pruefen\n";
} else {
    std::cout << "Spannung ausserhalb!\n";
}''',
                "C#": r'''double spannung = 23.8;
bool sicherungOk = true;

if (sicherungOk && spannung is >= 22.0 and <= 26.0)   // Pattern (C# 9)
{
    Console.WriteLine("Alles OK");
}
else if (!sicherungOk)
{
    Console.WriteLine("Sicherung prüfen");
}
else
{
    Console.WriteLine("Spannung ausserhalb!");
}''',
            },
        },
    ],

    "unterschiede": """
- **Python:** `elif`, Doppelpunkt `:` am Ende, Block = Einrückung, keine Klammern um die Bedingung nötig. Logik mit `and / or / not`.
- **C++ / C#:** `else if`, Bedingung in `( )`, Block in `{ }`, Logik mit `&& || !`.
- **C++:** Auch Zahlen gelten als Bedingung (0 = false, alles andere = true). **C#** erlaubt nur echte `bool`-Werte.
""",

    "tipps": [
        "Die strengste bzw. speziellste Bedingung zuerst prüfen (≥ 80 vor ≥ 60).",
        "Tiefe Verschachtelung vermeiden: Mit **Early Return** (`if fehler: return`) bleibt Code flach und lesbar.",
        "In C++/C# auch bei nur einer Zeile immer `{ }` setzen. Das verhindert fiese Fehler beim späteren Erweitern.",
    ],
    "fehler": [
        "Python: Doppelpunkt nach der Bedingung vergessen gibt einen `SyntaxError`.",
        "C++: `if (x = 5)` ist eine Zuweisung und deshalb immer wahr. Richtig ist `==`.",
        "C++: `if (x > 5);` mit Semikolon ist ein leerer Befehl. Der Block danach läuft IMMER.",
    ],
    "siehe_auch": ["switch_match", "operatoren", "while_schleife"],
}
