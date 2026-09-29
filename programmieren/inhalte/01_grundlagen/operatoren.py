# Thema: Operatoren  (Kategorie: Grundlagen)
THEMA = {
    "titel": "Operatoren",
    "reihenfolge": 6,
    "kurz": "Rechnen, vergleichen, logisch verknüpfen. Mit den typischen Stolperfallen zwischen den Sprachen.",
    "stichworte": ["operator", "plus", "minus", "modulo", "rest", "division", "ganzzahldivision",
                   "vergleich", "gleich", "ungleich", "und", "oder", "nicht", "and", "or", "not",
                   "&&", "||", "potenz", "hoch", "inkrement", "++", "+=", "rangfolge", "ternär"],

    "erklaerung": """
## Arten von Operatoren
- **Arithmetisch:** rechnen (`+ - * / %`)
- **Vergleich:** ergeben `true`/`false` (`== != < > <= >=`)
- **Logisch:** Bedingungen verknüpfen (UND, ODER, NICHT)
- **Zuweisung:** `=`, `+=`, `-=`, `*=`, `/=`
- **Bit-Operatoren:** siehe Thema *Zahlensysteme*
## ⚠️ Die grösste Falle: Division
- **Python:** `7 / 2` = `3.5` (immer float), `7 // 2` = `3` (Ganzzahl-Division)
- **C++ / C#:** `7 / 2` = `3` wenn **beide** Werte int sind! Für 3.5 braucht es `7.0 / 2`.
## Kurzschluss-Auswertung (Short-Circuit)
Bei `A && B` wird B **nicht mehr geprüft**, wenn A schon false ist. So kann man sicher schreiben: `if (liste != null && liste.Count > 0)`
""",

    "tabellen": [
        {
            "titel": "📊 Arithmetik",
            "kopf": ["Bedeutung", "Python", "C++", "C#", "Beispiel / Ergebnis"],
            "zeilen": [
                ["Addition / Subtraktion", "+  -", "+  -", "+  -", "5 + 3 → 8"],
                ["Multiplikation", "*", "*", "*", "5 * 3 → 15"],
                ["Division", "/  (immer float)", "/  (int/int → int!)", "/  (int/int → int!)", "7 / 2 → Py 3.5 | C++/C# 3"],
                ["Ganzzahl-Division", "//", "/ (bei int)", "/ (bei int)", "7 // 2 → 3"],
                ["Rest (Modulo)", "%", "%", "%", "7 % 3 → 1"],
                ["Potenz", "**", "std::pow(a, b)", "Math.Pow(a, b)", "2 ** 10 → 1024"],
                ["+1 / −1", "x += 1", "x++  ++x", "x++  ++x", "–"],
            ],
        },
        {
            "titel": "📊 Vergleich & Logik",
            "kopf": ["Bedeutung", "Python", "C++", "C#"],
            "zeilen": [
                ["gleich / ungleich", "==  !=", "==  !=", "==  !="],
                ["kleiner / grösser (gleich)", "<  >  <=  >=", "<  >  <=  >=", "<  >  <=  >="],
                ["UND", "and", "&&", "&&"],
                ["ODER", "or", "||", "||"],
                ["NICHT", "not", "!", "!"],
                ["Bereich prüfen", "0 <= x < 10", "x >= 0 && x < 10", "x >= 0 && x < 10  /  x is >= 0 and < 10"],
                ["Kurz-if (ternär)", "a if bed else b", "bed ? a : b", "bed ? a : b"],
            ],
        },
    ],

    "beispiele": [
        {
            "titel": "Rechnen und Division im Vergleich",
            "code": {
                "Python": r'''a, b = 7, 2
print(a + b, a - b, a * b)   # 9 5 14
print(a / b)                 # 3.5
print(a // b)                # 3
print(a % b)                 # 1
print(a ** b)                # 49
print(-7 // 2, -7 % 2)       # -4 1   (Python rundet nach unten!)''',
                "C++": r'''#include <iostream>
#include <cmath>

int main() {
    int a = 7, b = 2;
    std::cout << a + b << " " << a - b << " " << a * b << "\n";  // 9 5 14
    std::cout << a / b << "\n";              // 3  (!)
    std::cout << 7.0 / 2 << "\n";            // 3.5
    std::cout << a % b << "\n";              // 1
    std::cout << std::pow(a, b) << "\n";     // 49
    std::cout << -7 / 2 << " " << -7 % 2 << "\n";   // -3 -1  (Richtung 0)

    int i = 5;
    int x = i++;   // x = 5, danach i = 6  (Post-Inkrement)
    int y = ++i;   // i = 7, dann y = 7    (Pre-Inkrement)
    return 0;
}''',
                "C#": r'''int a = 7, b = 2;
Console.WriteLine($"{a + b} {a - b} {a * b}");  // 9 5 14
Console.WriteLine(a / b);                        // 3  (!)
Console.WriteLine(7.0 / 2);                      // 3.5
Console.WriteLine(a % b);                        // 1
Console.WriteLine(Math.Pow(a, b));               // 49
Console.WriteLine($"{-7 / 2} {-7 % 2}");         // -3 -1

int i = 5;
int x = i++;   // x = 5, i = 6
int y = ++i;   // i = 7, y = 7''',
            },
        },
        {
            "titel": "Logische Verknüpfung und Kurz-if",
            "code": {
                "Python": r'''temperatur = 72
luefter_an = True

if temperatur > 70 and luefter_an:
    print("Warnung: heiss trotz Lüfter")

status = "OK" if temperatur < 80 else "ÜBERHITZT"   # Kurz-if
print(status)''',
                "C++": r'''int temperatur = 72;
bool luefterAn = true;

if (temperatur > 70 && luefterAn) {
    std::cout << "Warnung: heiss trotz Luefter\n";
}

std::string status = (temperatur < 80) ? "OK" : "UEBERHITZT";   // ternärer Operator''',
                "C#": r'''int temperatur = 72;
bool luefterAn = true;

if (temperatur > 70 && luefterAn)
{
    Console.WriteLine("Warnung: heiss trotz Lüfter");
}

string status = temperatur < 80 ? "OK" : "ÜBERHITZT";''',
            },
        },
    ],

    "tipps": [
        "Modulo prüft Teilbarkeit: `x % 2 == 0` bedeutet gerade Zahl.",
        "Im Zweifel Klammern setzen. Das ist lesbarer als die Rangfolge auswendig zu kennen.",
    ],
    "fehler": [
        "`if (x = 5)` in C++ ist eine ZUWEISUNG und kein Vergleich, und sie ist immer wahr. C# meldet hier einen Fehler, C++ nur eine Warnung.",
        "`&` statt `&&` in C++/C#: Beide Seiten werden ausgewertet (kein Kurzschluss).",
        "Python: `&&` gibt es nicht, dort heisst es `and`.",
    ],
    "siehe_auch": ["zahlensysteme", "if_else", "datentypen"],
}
