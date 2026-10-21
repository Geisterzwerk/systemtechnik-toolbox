# Thema: Gültigkeitsbereich (Scope)  (Kategorie: Funktionen)
THEMA = {
    "titel": "Gültigkeitsbereich (Scope)",
    "reihenfolge": 3,
    "kurz": "Wo ist eine Variable sichtbar? Lokal, global und Block-Scope.",
    "stichworte": ["scope", "gueltigkeit", "gültigkeitsbereich", "lokal", "global", "sichtbarkeit",
                   "lebensdauer", "static", "block", "namespace", "nonlocal"],

    "erklaerung": """
## Stell dir vor …
Ein **Haus mit Zimmern**: Was in deinem Zimmer liegt (lokale Variable), sehen nur die, die im Zimmer sind. Was im Wohnzimmer liegt (globale Variable), sehen alle. Hast du in deinem Zimmer etwas mit demselben Namen wie im Wohnzimmer, gilt in deinem Zimmer deine Version.
## Lokale Variablen
Eine Variable, die **in einer Funktion** angelegt wird, existiert nur dort. Nach dem Ende der Funktion ist sie weg. Jede Funktion hat ihre eigenen lokalen Variablen, gleiche Namen stören sich also nicht.
## Globale Variablen
Diese werden **ausserhalb** jeder Funktion angelegt und sind überall sichtbar. **Möglichst vermeiden!** Jeder Teil des Programms kann sie ändern, und das macht Fehler schwer auffindbar. Besser ist es, Werte als Parameter zu übergeben.
## Block-Scope
- **C++ / C#:** Jeder `{ }`-Block ist ein eigener Bereich. Eine Variable, die in einem `if` oder `for` angelegt wird, gibt es danach nicht mehr.
- **Python:** `if` und `for` bilden **keinen** eigenen Bereich. Nur Funktionen, Klassen und Module tun das.
## 🔬 Genauer hingeschaut
- **Python sucht in vier Stufen (LEGB):** Lokal → umschliessende Funktion (Enclosing) → Global (Modul) → Built-in. Darum kann man versehentlich eine eingebaute Funktion überdecken, z.B. mit einer Variablen namens `list` oder `sum`.
- **`global` und `nonlocal`:** Will eine Funktion eine äussere Variable nicht nur lesen, sondern neu zuweisen, braucht Python `global name` bzw. `nonlocal name` für eine umschliessende Funktion. Meist ist ein Rückgabewert die bessere Lösung.
- **Python hat keinen Block-Scope:** Eine Variable, die in einem `if` oder einer `for`-Schleife angelegt wird, existiert danach weiter. In C++ und C# endet sie mit der schliessenden Klammer.
## 💡 Wusstest du?
- Nach `for i in range(3): pass` hat `i` in Python den Wert 2 – die Schleifenvariable bleibt nach der Schleife erhalten.
""",

    "beispiele": [
        {
            "titel": "Lokal vs. global",
            "code": {
                "Python": r'''zaehler = 0                  # global

def erhoehen():
    global zaehler           # ohne 'global' -> UnboundLocalError!
    zaehler += 1

def rechnen():
    ergebnis = 42            # lokal: nur hier sichtbar
    return ergebnis

erhoehen()
print(zaehler)               # 1
# print(ergebnis)            # NameError: name 'ergebnis' is not defined

if True:
    im_if = "sichtbar"
print(im_if)                 # funktioniert in Python!''',
                "C++": r'''#include <iostream>

int zaehler = 0;                 // global

void erhoehen() {
    zaehler++;                   // global direkt änderbar
}

int main() {
    erhoehen();
    std::cout << zaehler << "\n";      // 1

    if (true) {
        int imIf = 5;            // nur in diesem { } Block
    }
    // std::cout << imIf;       // FEHLER: imIf ist hier unbekannt

    for (int i = 0; i < 3; i++) { }
    // std::cout << i;          // FEHLER: i existiert nur in der Schleife
    return 0;
}''',
                "C#": r'''// C# hat keine echten globalen Variablen -> statisches Feld einer Klasse
Zaehler.Wert++;
Console.WriteLine(Zaehler.Wert);      // 1

if (true)
{
    int imIf = 5;
}
// Console.WriteLine(imIf);           // FEHLER CS0103

class Zaehler                         // Klassen stehen NACH den Top-Level-Statements
{
    public static int Wert = 0;       // für alle gemeinsam
}''',
            },
        },
        {
            "titel": "Lebensdauer: static in Funktionen (Wert bleibt erhalten)",
            "code": {
                "C++": r'''int aufrufZaehler() {
    static int anzahl = 0;   // wird nur EINMAL initialisiert
    return ++anzahl;         // Wert bleibt zwischen Aufrufen erhalten
}
// aufrufZaehler() -> 1, dann 2, dann 3 ...''',
                "Python": r'''# Python hat kein static in Funktionen.
# Übliche Lösung: eine Klasse (siehe OOP) oder ein Funktionsattribut:
def aufruf_zaehler():
    aufruf_zaehler.anzahl += 1
    return aufruf_zaehler.anzahl
aufruf_zaehler.anzahl = 0''',
            },
            "hinweis": {"C#": "Keine static-Variablen in Methoden. Stattdessen ein Feld in der Klasse verwenden."},
        },
    ],

    "tipps": [
        "Variablen so lokal wie möglich halten und erst dort deklarieren, wo man sie braucht.",
        "Statt globaler Variablen Werte als Parameter übergeben oder in einer Klasse kapseln.",
    ],
    "fehler": [
        "Python: Globale Variable in einer Funktion ändern ohne `global` gibt einen `UnboundLocalError`.",
        "Lokale Variable mit gleichem Namen wie eine globale (Shadowing): Man ändert unbemerkt die falsche.",
    ],
    "siehe_auch": ["variablen", "funktionen_grundlagen", "kapselung"],
}
