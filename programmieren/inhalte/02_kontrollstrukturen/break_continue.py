# Thema: break & continue  (Kategorie: Kontrollstrukturen)
THEMA = {
    "titel": "break & continue",
    "reihenfolge": 6,
    "kurz": "Eine Schleife vorzeitig verlassen oder einen Durchlauf überspringen.",
    "stichworte": ["break", "continue", "abbrechen", "ueberspringen", "überspringen", "schleife verlassen",
                   "pass", "else", "for else", "vorzeitig"],

    "erklaerung": """
## Stell dir vor …
Du suchst in einem **Stapel Briefe** nach einer bestimmten Rechnung. Findest du sie, hörst du sofort auf zu suchen – das ist `break`. Ist ein Brief nur Werbung, legst du ihn ungelesen weg und nimmst den nächsten – das ist `continue`.
## break
Beendet die **innerste** Schleife sofort. Das Programm macht nach der Schleife weiter.
## continue
Bricht nur den **aktuellen Durchlauf** ab und springt direkt zum nächsten.
## Python-Extra
- `pass` ist ein leerer Befehl, ein Platzhalter, wo Python einen Block erwartet.
- `for … else`: Der `else`-Block läuft nur, wenn die Schleife **ohne** break beendet wurde. Das ist praktisch für Suchen.
## 🔬 Genauer hingeschaut
- **Nur die innerste Schleife:** `break` verlässt nur die Schleife, in der es steht. Bei verschachtelten Schleifen läuft die äussere weiter. Lösungen: eine Merker-Variable, oder die Schleifen in eine Funktion packen und mit `return` aussteigen.
- **Sparsam einsetzen:** Viele `break` und `continue` in einer langen Schleife machen den Ablauf schwer verständlich. Oft lässt sich die Bedingung direkt in den Schleifenkopf schreiben.
- **`continue` in while-Schleifen:** Steht das Hochzählen am Ende des Schleifenkörpers, wird es durch `continue` übersprungen – und die Schleife läuft endlos. In `for`-Schleifen passiert das nicht.
## 💡 Wusstest du?
- 1968 schrieb Edsger Dijkstra den berühmten Artikel „Go To Statement Considered Harmful“. `break` und `continue` sind gezähmte Sprünge: Sie springen nur an klar definierte Stellen.
""",

    "beispiele": [
        {
            "titel": "Ungültige Messwerte überspringen, bei Fehler abbrechen",
            "code": {
                "Python": r'''messwerte = [12.0, -1, 12.3, 99.9, 11.8]

for wert in messwerte:
    if wert < 0:
        continue            # ungültig -> nächster Wert
    if wert > 50:
        print("Fehler: Wert zu gross, Abbruch!")
        break               # ganze Schleife beenden
    print("OK:", wert)''',
                "C++": r'''#include <iostream>
#include <vector>

int main() {
    std::vector<double> messwerte = {12.0, -1, 12.3, 99.9, 11.8};

    for (double wert : messwerte) {
        if (wert < 0) {
            continue;
        }
        if (wert > 50) {
            std::cout << "Fehler: Wert zu gross, Abbruch!\n";
            break;
        }
        std::cout << "OK: " << wert << "\n";
    }
    return 0;
}''',
                "C#": r'''double[] messwerte = { 12.0, -1, 12.3, 99.9, 11.8 };

foreach (double wert in messwerte)
{
    if (wert < 0)
    {
        continue;
    }
    if (wert > 50)
    {
        Console.WriteLine("Fehler: Wert zu gross, Abbruch!");
        break;
    }
    Console.WriteLine($"OK: {wert}");
}''',
            },
            "ausgabe": "OK: 12.0\nOK: 12.3\nFehler: Wert zu gross, Abbruch!",
        },
        {
            "titel": "Suchen mit for-else (nur Python)",
            "code": {
                "Python": r'''geraete = ["Sensor", "Pumpe", "Ventil"]

for g in geraete:
    if g == "Motor":
        print("Motor gefunden")
        break
else:                       # läuft nur, wenn KEIN break passiert ist
    print("Motor nicht gefunden")''',
            },
            "hinweis": {
                "C++": "Kein for-else. Eine `bool gefunden = false;`-Variable verwenden oder `std::find` nutzen.",
                "C#": "Kein for-else. Eine `bool gefunden`-Variable verwenden oder LINQ `.Contains()` / `.Any()` nutzen.",
            },
        },
    ],

    "tipps": [
        "Aus **verschachtelten** Schleifen kommt man mit break nur eine Ebene raus. Lösung: den Code in eine Funktion packen und `return` verwenden.",
    ],
    "fehler": [
        "`continue` in einer while-Schleife VOR dem Hochzählen des Zählers führt zu einer Endlosschleife.",
    ],
    "siehe_auch": ["for_schleife", "while_schleife"],
}
