# Thema: Konstruktor & Destruktor  (Kategorie: Objektorientierung)
THEMA = {
    "titel": "Konstruktor & Destruktor",
    "reihenfolge": 2,
    "kurz": "Was passiert beim Erzeugen und beim Zerstören eines Objekts?",
    "stichworte": ["konstruktor", "constructor", "init", "__init__", "destruktor", "destructor",
                   "__del__", "initialisierungsliste", "new", "instanziieren", "erzeugen",
                   "dispose", "using", "raii", "klassenvariable", "static", "statisch"],

    "erklaerung": """
## Konstruktor
Eine spezielle Methode, die **automatisch beim Erzeugen** eines Objekts aufgerufen wird. Sie sorgt dafür, dass das Objekt von Anfang an in einem **gültigen Zustand** ist.
- **Python:** `def __init__(self, ...)`
- **C++ / C#:** Methode mit dem **gleichen Namen wie die Klasse** und ohne Rückgabetyp
- Es kann mehrere Konstruktoren geben (Überladen, nur in C++/C#)
## Destruktor
Wird aufgerufen, wenn das Objekt **zerstört** wird. Hier gibt man Ressourcen frei (Datei schliessen, Verbindung trennen).
- **C++:** `~Klassenname()`. Er wird **genau dann** aufgerufen, wenn das Objekt seinen Gültigkeitsbereich verlässt. Das Prinzip heisst **RAII** und ist ein Kernkonzept von C++.
- **C# / Python:** Der **Garbage Collector** räumt irgendwann automatisch auf. Für ein sofortiges Aufräumen nutzt man `using` (C#, IDisposable) bzw. `with` (Python).
## Statische Member (Klassenvariablen)
Diese gehören der **Klasse** und nicht einem einzelnen Objekt. Alle Objekte teilen sie, z.B. einen Zähler, wie viele Sensoren es gibt.
""",

    "beispiele": [
        {
            "titel": "Konstruktor, Standardwerte und statischer Zähler",
            "code": {
                "Python": r'''class Motor:
    anzahl = 0                          # Klassenvariable (für alle Motoren gleich)

    def __init__(self, name, max_drehzahl=3000):
        # wird bei Motor(...) automatisch ausgeführt
        self.name = name
        self.max_drehzahl = max_drehzahl
        self.drehzahl = 0
        Motor.anzahl += 1
        print(f"{name} erstellt")

    def __del__(self):                  # "Destruktor" (Zeitpunkt nicht garantiert!)
        print(f"{self.name} entfernt")


m1 = Motor("Pumpe")                     # max_drehzahl = 3000 (Standard)
m2 = Motor("Lüfter", 1500)
print(Motor.anzahl)                     # 2''',
                "C++": r'''#include <iostream>
#include <string>

class Motor {
public:
    static int anzahl;                  // statisch: gehört der Klasse

    // Konstruktor mit Initialisierungsliste ( : name(n), ... )
    Motor(std::string n, int maxDrehzahl = 3000)
        : name(n), maxDrehzahl(maxDrehzahl), drehzahl(0) {
        anzahl++;
        std::cout << name << " erstellt\n";
    }

    ~Motor() {                          // Destruktor
        std::cout << name << " entfernt\n";
    }

private:
    std::string name;
    int maxDrehzahl;
    int drehzahl;
};

int Motor::anzahl = 0;                  // statisches Attribut definieren

int main() {
    Motor m1("Pumpe");
    {
        Motor m2("Luefter", 1500);
        std::cout << Motor::anzahl << "\n";   // 2
    }   // <- hier endet der Block: Destruktor von m2 läuft SOFORT
    std::cout << "Ende main\n";
    return 0;
}       // <- hier läuft der Destruktor von m1''',
                "C#": r'''var m1 = new Motor("Pumpe");
var m2 = new Motor("Lüfter", 1500);
Console.WriteLine(Motor.Anzahl);        // 2

class Motor
{
    public static int Anzahl = 0;       // statisch: gehört der Klasse

    private string name;
    private int maxDrehzahl;
    private int drehzahl = 0;

    public Motor(string name, int maxDrehzahl = 3000)   // Konstruktor
    {
        this.name = name;               // this. unterscheidet Feld und Parameter
        this.maxDrehzahl = maxDrehzahl;
        Anzahl++;
        Console.WriteLine($"{name} erstellt");
    }
}''',
            },
        },
        {
            "titel": "Ressourcen sicher freigeben",
            "code": {
                "Python": r'''# with ruft am Ende automatisch "schliessen" auf - auch bei Fehlern
with open("log.txt", "w") as datei:
    datei.write("Messung gestartet\n")
# hier ist die Datei garantiert geschlossen''',
                "C++": r'''#include <fstream>

void protokollieren() {
    std::ofstream datei("log.txt");     // öffnet im Konstruktor
    datei << "Messung gestartet\n";
}   // Destruktor schliesst die Datei automatisch (RAII)''',
                "C#": r'''// using ruft am Ende automatisch Dispose() auf
using (var datei = new StreamWriter("log.txt"))
{
    datei.WriteLine("Messung gestartet");
}
// Kurzform (C# 8): using var datei = new StreamWriter("log.txt");''',
            },
        },
    ],

    "tipps": [
        "Im Konstruktor alle Attribute setzen. Ein Objekt sollte nie halb initialisiert sein.",
        "C++: Initialisierungslisten (`: name(n)`) sind effizienter als Zuweisungen im Körper und für `const`- und Referenz-Attribute sogar Pflicht.",
    ],
    "fehler": [
        "Python: `def init(self)` oder `def _init_(self)` mit falschen Unterstrichen. Es müssen je ZWEI sein: `__init__`!",
        "C++: Statisches Attribut nur deklariert, aber nicht ausserhalb der Klasse definiert (`int Motor::anzahl = 0;`) führt zu einem Linker-Fehler.",
        "Sich in Python auf `__del__` verlassen: Wann es aufgerufen wird, ist nicht garantiert.",
    ],
    "siehe_auch": ["klassen_objekte", "kapselung", "dateien"],
}
