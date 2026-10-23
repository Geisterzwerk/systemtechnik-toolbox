# Thema: Funktionen – Grundlagen  (Kategorie: Funktionen)
THEMA = {
    "titel": "Funktionen – Grundlagen",
    "reihenfolge": 1,
    "kurz": "Code in einen benannten, wiederverwendbaren Baustein packen und beliebig oft aufrufen.",
    "stichworte": ["funktion", "function", "methode", "method", "def", "void", "aufrufen", "aufruf",
                   "definieren", "prozedur", "unterprogramm", "wiederverwenden", "signatur", "prototyp",
                   "deklaration"],

    "erklaerung": """
## Stell dir vor …
Eine **Kaffeemaschine**: Oben kommen Wasser und Bohnen hinein (Parameter), unten kommt Kaffee heraus (Rückgabewert). Wie es innen funktioniert, musst du nicht wissen – du drückst einfach den Knopf. Eine Funktion ist so eine Maschine im Code: einmal gebaut, beliebig oft benutzt.
## Warum Funktionen?
- **Wiederverwendung:** Einmal schreiben, überall benutzen
- **Übersicht:** Ein grosses Problem in kleine, benannte Schritte zerlegen
- **Testbarkeit:** Jede Funktion kann einzeln geprüft werden
- **DRY-Prinzip:** "Don't Repeat Yourself". Kopierten Code gehört in eine Funktion.
## Aufbau
Eine Funktion ist wie eine **Blackbox**: Es kommen **Parameter** hinein, sie macht etwas und gibt einen **Rückgabewert** heraus.
- **Definition:** Hier wird festgelegt, WAS die Funktion tut (einmal)
- **Aufruf:** Hier wird sie benutzt (beliebig oft)
- `void` (C++/C#) bzw. kein `return` (Python) bedeutet: Die Funktion gibt nichts zurück.
## Funktion vs. Methode
Eine **Methode** ist eine Funktion, die zu einer **Klasse** gehört. In C# ist fast alles eine Methode, weil jeder Code in einer Klasse steht.
## 🔬 Genauer hingeschaut
- **Eine Aufgabe pro Funktion:** Eine Funktion sollte genau eine Sache gut machen und einen Namen haben, der sagt, was sie tut (`berechne_widerstand`, `lese_sensor`). Wird der Name lang oder braucht ein „und“, ist sie meist zu gross.
- **Reine Funktionen:** Eine Funktion, die nur aus ihren Parametern ein Ergebnis berechnet und sonst nichts verändert, ist am einfachsten zu testen. Funktionen mit Nebenwirkungen (Datei schreiben, globale Variable ändern) sind manchmal nötig, sollten aber klar als solche erkennbar sein.
- **DRY – Don't Repeat Yourself:** Steht derselbe Code an drei Stellen, gehört er in eine Funktion. Ein Fehler muss dann nur einmal korrigiert werden.
## 💡 Wusstest du?
- Python bringt rund 70 eingebaute Funktionen mit, die man ohne Import benutzen kann – von `print()` und `len()` bis `sorted()` und `round()`.
""",

    "bild": "funktion_blackbox.png",
    "bild_text": "Eine Funktion als Blackbox: Eingabe → Verarbeitung → Ausgabe",

    "beispiele": [
        {
            "titel": "Funktion definieren und aufrufen",
            "code": {
                "Python": r'''# ---- Definition ----
def begruessen():                        # keine Parameter, keine Rückgabe
    print("Willkommen bei SystemLab!")


def leistung(spannung, strom):           # 2 Parameter
    return spannung * strom              # Rückgabewert


# ---- Aufruf ----
begruessen()
p = leistung(24, 1.5)                    # 36.0
print(f"P = {p} W")
print(f"P = {leistung(230, 0.5)} W")     # direkt verwenden''',
                "C++": r'''#include <iostream>

// ---- Definition ----
void begruessen() {                          // void = keine Rückgabe
    std::cout << "Willkommen bei SystemLab!\n";
}

double leistung(double spannung, double strom) {   // Rückgabetyp double
    return spannung * strom;
}

int main() {
    // ---- Aufruf ----
    begruessen();
    double p = leistung(24, 1.5);
    std::cout << "P = " << p << " W\n";
    return 0;
}''',
                "C#": r'''// ---- Aufruf (Top-Level-Statements) ----
Begruessen();
double p = Leistung(24, 1.5);
Console.WriteLine($"P = {p} W");

// ---- Definition ----
static void Begruessen()                     // void = keine Rückgabe
{
    Console.WriteLine("Willkommen bei SystemLab!");
}

static double Leistung(double spannung, double strom)
{
    return spannung * strom;
}''',
            },
            "ausgabe": "Willkommen bei SystemLab!\nP = 36 W",
        },
        {
            "titel": "C++: Deklaration (Prototyp) vor main",
            "text": "C++ liest die Datei von oben nach unten. Eine Funktion muss **bekannt** sein, bevor sie aufgerufen wird. Deshalb schreibt man oben einen Prototyp (oder die Deklaration steht in einer .h-Datei).",
            "code": {
                "C++": r'''#include <iostream>

double leistung(double u, double i);   // Prototyp / Deklaration (mit ;)

int main() {
    std::cout << leistung(12, 2) << "\n";   // funktioniert, weil oben deklariert
    return 0;
}

double leistung(double u, double i) {  // Definition (weiter unten)
    return u * i;
}''',
            },
            "hinweis": {
                "Python": "Nicht nötig. Die Funktion muss nur definiert sein, BEVOR die Zeile mit dem Aufruf ausgeführt wird.",
                "C#": "Nicht nötig. C# kennt alle Methoden einer Klasse, egal wo sie stehen.",
            },
        },
    ],

    "unterschiede": """
- **Python:** `def name(parameter):`, kein Rückgabetyp nötig (optional mit Type Hints: `def leistung(u: float, i: float) -> float:`).
- **C++:** `Rückgabetyp name(Typ parameter)`. Muss VOR dem Aufruf deklariert sein.
- **C#:** wie C++, Namen in PascalCase, Methoden stehen immer in einer Klasse (bzw. als lokale Funktion in den Top-Level-Statements).
""",

    "tipps": [
        "Eine Funktion sollte **eine** Aufgabe erfüllen. Der Name beschreibt sie mit einem Verb: `berechne_leistung`, `lese_sensor`.",
        "Faustregel: Wenn eine Funktion nicht mehr auf den Bildschirm passt, ist sie zu lang.",
        "Python Type Hints (`-> float`) helfen VS Code bei der Autovervollständigung und machen Code lesbarer.",
    ],
    "fehler": [
        "Python: Funktion ohne Klammern aufrufen: `begruessen` statt `begruessen()`. Dabei passiert nichts!",
        "`return` vergessen. Python gibt dann `None` zurück, C++ ein undefiniertes Ergebnis (Warnung beachten!).",
        "Code nach `return` wird nie ausgeführt.",
    ],
    "siehe_auch": ["parameter_rueckgabe", "scope", "rekursion", "klassen_objekte"],
}
