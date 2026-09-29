# Thema: Variablen  (Kategorie: Grundlagen)
THEMA = {
    "titel": "Variablen",
    "reihenfolge": 2,
    "kurz": "Ein benannter Speicherplatz für einen Wert. Deklarieren, zuweisen, ändern, Konstanten.",
    "stichworte": ["variable", "deklaration", "zuweisung", "konstante", "const", "var", "auto",
                   "speicher", "wert", "initialisieren", "readonly", "zuweisen"],

    "erklaerung": """
## Was ist eine Variable?
Eine Variable ist ein **Name für einen Speicherplatz** im Arbeitsspeicher (RAM). Stell sie dir wie eine beschriftete Schublade vor: Der Name steht aussen, der Wert liegt drin.
- **Deklarieren:** Die Variable anlegen (Name + in C++/C# auch den Typ)
- **Initialisieren:** Ihr den ersten Wert geben
- **Zuweisen:** Mit `=` einen neuen Wert hineinlegen. `=` heisst "bekommt" und nicht "ist gleich"!
## Statisch vs. dynamisch typisiert
- **C++ / C#:** Der Typ steht fest (`int alter = 25;`). Eine int-Variable kann danach nie einen Text speichern. Der Compiler prüft das.
- **Python:** Der Typ gehört zum **Wert**, nicht zur Variable. `x = 5` und danach `x = "Hallo"` ist erlaubt.
## Konstanten
Werte, die sich nie ändern dürfen (z.B. π, Maximalwerte):
- **C++:** `const double PI = 3.14159;`  (oder `constexpr`)
- **C#:** `const double PI = 3.14159;`
- **Python:** Es gibt keine echten Konstanten. Man schreibt den Namen GROSS (`PI = 3.14159`) als Abmachung.
""",

    "bild": "variable_speicher.png",
    "bild_text": "Eine Variable = Name + Typ + Wert an einer Adresse im Speicher",

    "beispiele": [
        {
            "titel": "Variablen anlegen und ändern",
            "code": {
                "Python": r'''alter = 25            # int
spannung = 24.5       # float
name = "Jorick"       # str
aktiv = True          # bool

alter = alter + 1     # neuen Wert zuweisen -> 26
alter += 1            # Kurzform -> 27

PI = 3.14159          # "Konstante" (nur Konvention: GROSS geschrieben)
print(name, alter)''',
                "C++": r'''#include <iostream>
#include <string>

int main() {
    int alter = 25;              // Typ Name = Wert;
    double spannung = 24.5;
    std::string name = "Jorick";
    bool aktiv = true;

    alter = alter + 1;           // 26
    alter += 1;                  // 27

    const double PI = 3.14159;   // Konstante: kann nicht mehr geändert werden
    auto zaehler = 10;           // auto: Compiler erkennt den Typ (int)

    std::cout << name << " " << alter << std::endl;
    return 0;
}''',
                "C#": r'''int alter = 25;              // Typ Name = Wert;
double spannung = 24.5;
string name = "Jorick";
bool aktiv = true;

alter = alter + 1;           // 26
alter += 1;                  // 27

const double PI = 3.14159;   // Konstante
var zaehler = 10;            // var: Compiler erkennt den Typ (int)

Console.WriteLine($"{name} {alter}");''',
            },
            "ausgabe": "Jorick 27",
        },
        {
            "titel": "Dynamische vs. statische Typisierung",
            "code": {
                "Python": r'''x = 5          # x zeigt auf einen int
x = "Hallo"    # erlaubt! x zeigt jetzt auf einen str
print(type(x)) # <class 'str'>''',
                "C++": r'''int x = 5;
x = "Hallo";   // FEHLER beim Kompilieren: ein int kann keinen Text speichern''',
                "C#": r'''int x = 5;
x = "Hallo";   // FEHLER CS0029: string kann nicht in int umgewandelt werden''',
            },
        },
    ],

    "unterschiede": """
- **Python:** kein Typ bei der Deklaration, Variable entsteht bei der ersten Zuweisung.
- **C++:** Typ muss angegeben werden (oder `auto`). **Achtung:** Nicht initialisierte lokale Variablen enthalten zufälligen "Müll"!
- **C#:** Typ oder `var`. Der Compiler verbietet es, eine nicht initialisierte lokale Variable zu lesen.
""",

    "tipps": [
        "Sprechende Namen verwenden: `spannung_v` statt `x`. Dein zukünftiges Ich wird es dir danken.",
        "Variablen in C++ IMMER direkt initialisieren: `int summe = 0;`",
    ],
    "fehler": [
        "`=` (Zuweisung) mit `==` (Vergleich) verwechseln.",
        "C++: `int summe;` ohne Startwert und dann `summe += 5;` ergibt einen zufälligen Wert.",
        "Python: Tippfehler im Namen (`spanung = 5`) erzeugt einfach eine NEUE Variable und keinen Fehler.",
    ],
    "siehe_auch": ["datentypen", "typumwandlung", "scope"],
}
