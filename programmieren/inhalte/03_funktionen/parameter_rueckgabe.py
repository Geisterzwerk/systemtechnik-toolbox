# Thema: Parameter & Rückgabewerte  (Kategorie: Funktionen)
THEMA = {
    "titel": "Parameter & Rückgabewerte",
    "reihenfolge": 2,
    "kurz": "Standardwerte, benannte Parameter, mehrere Rückgabewerte, Call by Value vs. Reference, Überladen.",
    "stichworte": ["parameter", "argument", "return", "rueckgabe", "rückgabe", "rückgabewert",
                   "standardwert", "default", "optional", "by value", "by reference", "referenz",
                   "ref", "out", "tuple", "mehrere rueckgabewerte", "ueberladen", "überladen",
                   "overloading", "kwargs", "args", "benannte parameter"],

    "erklaerung": """
## Parameter vs. Argument
- **Parameter:** die Variable in der Definition: `def f(x)`
- **Argument:** der konkrete Wert beim Aufruf: `f(5)`
## Standardwerte (optionale Parameter)
Ein Parameter mit Standardwert darf beim Aufruf weggelassen werden. Solche Parameter müssen **hinten** stehen.
## Call by Value vs. Call by Reference
- **By Value (Kopie):** Die Funktion bekommt eine **Kopie**. Änderungen wirken nicht nach aussen. (Standard in C++/C# bei int, double, struct)
- **By Reference:** Die Funktion arbeitet mit dem **Original**. C++: `int& x`, C#: `ref int x`
- **Python:** Es wird immer eine Referenz auf das Objekt übergeben. **Unveränderliche** Objekte (int, str, tuple) wirken dadurch wie eine Kopie. **Veränderliche** Objekte (list, dict) können in der Funktion geändert werden, und das sieht man dann auch aussen!
## Mehrere Rückgabewerte
- **Python:** einfach mit Komma zurückgeben, das ergibt ein Tupel
- **C++:** `std::pair`, `std::tuple`, ein `struct` oder Referenz-Parameter
- **C#:** Tupel `(double, double)` oder `out`-Parameter
## Überladen (Overloading)
C++ und C# erlauben **mehrere Funktionen mit gleichem Namen**, aber unterschiedlichen Parametern. Python nicht. Dort nutzt man Standardwerte.
""",

    "beispiele": [
        {
            "titel": "Standardwerte und benannte Argumente",
            "code": {
                "Python": r'''def spannungsteiler(u_ein, r1, r2=10_000):      # r2 optional
    return u_ein * r2 / (r1 + r2)

print(spannungsteiler(5, 10_000))              # 2.5
print(spannungsteiler(5, 10_000, 4_700))       # mit r2
print(spannungsteiler(r1=1_000, u_ein=12))     # benannt, Reihenfolge egal''',
                "C++": r'''double spannungsteiler(double uEin, double r1, double r2 = 10000) {
    return uEin * r2 / (r1 + r2);
}

// Aufruf:
spannungsteiler(5, 10000);          // 2.5
spannungsteiler(5, 10000, 4700);
// C++ hat keine benannten Argumente''',
                "C#": r'''static double Spannungsteiler(double uEin, double r1, double r2 = 10000)
{
    return uEin * r2 / (r1 + r2);
}

Spannungsteiler(5, 10000);                 // 2.5
Spannungsteiler(5, 10000, 4700);
Spannungsteiler(r1: 1000, uEin: 12);       // benannte Argumente''',
            },
        },
        {
            "titel": "Mehrere Rückgabewerte: Minimum und Maximum",
            "code": {
                "Python": r'''def min_max(werte):
    return min(werte), max(werte)        # gibt ein Tupel zurück

kleinster, groesster = min_max([3, 8, 1, 9])   # "Entpacken"
print(kleinster, groesster)              # 1 9''',
                "C++": r'''#include <iostream>
#include <vector>
#include <utility>     // std::pair
#include <algorithm>   // std::minmax_element

std::pair<int, int> minMax(const std::vector<int>& werte) {
    auto [minIt, maxIt] = std::minmax_element(werte.begin(), werte.end());
    return {*minIt, *maxIt};
}

int main() {
    auto [kleinster, groesster] = minMax({3, 8, 1, 9});   // C++17 "structured binding"
    std::cout << kleinster << " " << groesster << "\n";    // 1 9
    return 0;
}''',
                "C#": r'''static (int min, int max) MinMax(int[] werte)
{
    return (werte.Min(), werte.Max());    // Tupel (braucht using System.Linq)
}

var (kleinster, groesster) = MinMax(new[] { 3, 8, 1, 9 });
Console.WriteLine($"{kleinster} {groesster}");   // 1 9''',
            },
            "ausgabe": "1 9",
        },
        {
            "titel": "By Value vs. By Reference",
            "code": {
                "Python": r'''def verdoppeln(zahl):
    zahl = zahl * 2          # neue lokale Variable, Original bleibt

def anhaengen(liste):
    liste.append(99)         # verändert das ORIGINAL-Objekt!

x = 5
verdoppeln(x)
print(x)                     # 5

daten = [1, 2]
anhaengen(daten)
print(daten)                 # [1, 2, 99]''',
                "C++": r'''#include <iostream>

void verdoppelnKopie(int zahl) {    // by value: Kopie
    zahl = zahl * 2;
}

void verdoppelnRef(int& zahl) {     // by reference: & = Original
    zahl = zahl * 2;
}

int main() {
    int x = 5;
    verdoppelnKopie(x);
    std::cout << x << "\n";   // 5
    verdoppelnRef(x);
    std::cout << x << "\n";   // 10
    return 0;
}
// Tipp: Grosse Objekte als  const std::vector<int>& v  übergeben
//       -> keine Kopie, aber auch keine Änderung möglich''',
                "C#": r'''static void VerdoppelnKopie(int zahl) { zahl *= 2; }
static void VerdoppelnRef(ref int zahl) { zahl *= 2; }
static void Lesen(out int wert) { wert = 42; }   // out: MUSS gesetzt werden

int x = 5;
VerdoppelnKopie(x);
Console.WriteLine(x);          // 5
VerdoppelnRef(ref x);          // ref auch beim Aufruf schreiben!
Console.WriteLine(x);          // 10
Lesen(out int y);
Console.WriteLine(y);          // 42
// Achtung: Klassen-Objekte (List<>, eigene Klassen) sind Referenztypen
//          -> Änderungen am Objekt sieht man auch aussen (wie Python)''',
            },
        },
        {
            "titel": "Überladen (Overloading)",
            "code": {
                "C++": r'''int flaeche(int seite) {               // Quadrat
    return seite * seite;
}
int flaeche(int breite, int hoehe) {   // Rechteck: gleicher Name, andere Parameter
    return breite * hoehe;
}
double flaeche(double radius) {        // Kreis
    return 3.14159 * radius * radius;
}
// flaeche(4) -> 16,  flaeche(4, 5) -> 20,  flaeche(2.0) -> 12.56''',
                "C#": r'''static int Flaeche(int seite) => seite * seite;
static int Flaeche(int breite, int hoehe) => breite * hoehe;
static double Flaeche(double radius) => Math.PI * radius * radius;
// Flaeche(4) -> 16,  Flaeche(4, 5) -> 20,  Flaeche(2.0) -> 12.57''',
            },
            "hinweis": {
                "Python": "Kein Überladen möglich. Die letzte Definition mit gleichem Namen überschreibt die vorherige. Stattdessen Standardwerte nutzen: `def flaeche(a, b=None): return a * a if b is None else a * b`",
            },
        },
    ],

    "tipps": [
        "C#: `=>` (Expression Body) ist die Kurzform für Methoden mit nur einem `return`.",
        "C++: Grosse Objekte (vector, string, eigene Klassen) als `const Typ&` übergeben, das ist schnell und sicher.",
    ],
    "fehler": [
        "Python: Veränderliche Standardwerte `def f(liste=[])`. Die Liste wird zwischen den Aufrufen GETEILT! Richtig: `def f(liste=None): if liste is None: liste = []`",
        "C#: `ref` beim Aufruf vergessen gibt einen Compiler-Fehler.",
    ],
    "siehe_auch": ["funktionen_grundlagen", "scope", "pointer_referenzen"],
}
