# Thema: Klassen in mehreren Dateien  (Kategorie: Objektorientierung)
THEMA = {
    "titel": "Klassen in mehreren Dateien",
    "reihenfolge": 6,
    "kurz": "Ein Projekt sauber aufteilen: Jede Klasse in eine eigene Datei. Wie die Klassen sich finden und miteinander kommunizieren.",
    "stichworte": ["mehrere dateien", "dateien", "projektstruktur", "import", "include", "header",
                   ".h", ".hpp", ".cpp", "namespace", "using", "komposition", "hat ein", "has a",
                   "aggregation", "kommunikation", "zusammenarbeit", "callback", "abhaengigkeit",
                   "modul", "package", "klassen verbinden", "objekte kommunizieren", "pragma once"],

    "erklaerung": """
## Warum aufteilen?
Sobald ein Programm wächst, wird eine einzige Datei unübersichtlich. Die Regel lautet: **Eine Klasse pro Datei**, und der Dateiname entspricht dem Klassennamen.
## Wie kommunizieren Objekte?
Objekte arbeiten zusammen, indem eines eine **Referenz auf ein anderes** besitzt und dessen **Methoden aufruft**. Diese Beziehung heisst **Komposition** ("hat ein"):
- Die `Steuerung` **hat einen** `Sensor` und **hat eine** `Anzeige`
- Die Steuerung ruft `sensor.messen()` auf, entscheidet und ruft dann `anzeige.zeigen(...)` auf
- Der Sensor weiss **nichts** von der Anzeige. Jede Klasse kennt nur, was sie wirklich braucht.
## Wie findet eine Datei die andere?
- **Python:** `from sensor import Sensor`. Dateien sind **Module**, Ordner mit `__init__.py` sind **Pakete**.
- **C++:** Aufteilung in **Header** (`.h` = Deklaration, das "Inhaltsverzeichnis") und **Quelldatei** (`.cpp` = Umsetzung). Andere Dateien binden den Header mit `#include "Sensor.h"` ein. Beim Kompilieren werden alle `.cpp` angegeben.
- **C#:** Alle `.cs`-Dateien eines Projekts kennen sich **automatisch**. Mit `namespace` ordnet man sie, mit `using` greift man auf andere Namespaces zu.
## Genau so ist diese Toolbox gebaut!
`main.py` erzeugt die `App`, die App ruft `programmieren_gui.create()` auf, und diese Funktion benutzt `lader.py`, `suche.py` und `seite.py`. Schau dir die Kommentare `# -> Datei.py` im Code an.
""",

    "bild": "mehrere_dateien.png",
    "bild_text": "Die Steuerung kennt Sensor und Anzeige und ruft deren Methoden auf",

    "beispiele": [
        {
            "titel": "Projektstruktur",
            "code": {
                "Python": r'''anlage/
├── main.py            <- Startpunkt: erzeugt die Objekte und verbindet sie
├── sensor.py          <- class Sensor
├── anzeige.py         <- class Anzeige
└── steuerung.py       <- class Steuerung (benutzt Sensor + Anzeige)''',
                "C++": r'''anlage/
├── main.cpp           <- Startpunkt
├── Sensor.h           <- Deklaration: WAS kann der Sensor?
├── Sensor.cpp         <- Umsetzung:  WIE macht er es?
├── Anzeige.h
├── Anzeige.cpp
├── Steuerung.h
└── Steuerung.cpp

Kompilieren:  g++ -std=c++17 main.cpp Sensor.cpp Anzeige.cpp Steuerung.cpp -o anlage''',
                "C#": r'''Anlage/
├── Anlage.csproj      <- Projektdatei (dotnet new console)
├── Program.cs         <- Startpunkt
├── Sensor.cs
├── Anzeige.cs
└── Steuerung.cs

Starten:  dotnet run   (alle .cs Dateien werden automatisch kompiliert)''',
            },
        },
        {
            "titel": "Datei 1: Sensor",
            "code": {
                "Python": r'''# ---------------- sensor.py ----------------
import random


class Sensor:
    """Liest einen Messwert. Kennt KEINE anderen Klassen."""

    def __init__(self, name):
        self.name = name

    def messen(self):
        return round(random.uniform(18, 35), 1)   # simulierter Messwert''',
                "C++": r'''// ---------------- Sensor.h ----------------
#pragma once            // verhindert, dass der Header doppelt eingebunden wird
#include <string>

class Sensor {
public:
    explicit Sensor(std::string name);
    double messen() const;
    const std::string& getName() const;
private:
    std::string name;
};

// ---------------- Sensor.cpp ----------------
#include "Sensor.h"     // eigenen Header einbinden (" " = eigene Datei)
#include <cstdlib>

Sensor::Sensor(std::string name) : name(std::move(name)) {}   // Sensor:: = gehört zu Sensor

double Sensor::messen() const {
    return 18.0 + (std::rand() % 170) / 10.0;                  // simulierter Messwert
}

const std::string& Sensor::getName() const { return name; }''',
                "C#": r'''// ---------------- Sensor.cs ----------------
namespace Anlage;

public class Sensor
{
    private static readonly Random zufall = new();
    public string Name { get; }

    public Sensor(string name) => Name = name;

    public double Messen() => Math.Round(18 + zufall.NextDouble() * 17, 1);  // simuliert
}''',
            },
        },
        {
            "titel": "Datei 2: Anzeige",
            "code": {
                "Python": r'''# ---------------- anzeige.py ----------------
class Anzeige:
    """Gibt Meldungen aus. Kennt KEINE anderen Klassen."""

    def zeigen(self, text, warnung=False):
        symbol = "⚠" if warnung else "✓"
        print(f"[{symbol}] {text}")''',
                "C++": r'''// ---------------- Anzeige.h ----------------
#pragma once
#include <string>

class Anzeige {
public:
    void zeigen(const std::string& text, bool warnung = false) const;
};

// ---------------- Anzeige.cpp ----------------
#include "Anzeige.h"
#include <iostream>

void Anzeige::zeigen(const std::string& text, bool warnung) const {
    std::cout << (warnung ? "[!] " : "[ok] ") << text << "\n";
}''',
                "C#": r'''// ---------------- Anzeige.cs ----------------
namespace Anlage;

public class Anzeige
{
    public void Zeigen(string text, bool warnung = false)
    {
        Console.WriteLine($"[{(warnung ? "⚠" : "✓")}] {text}");
    }
}''',
            },
        },
        {
            "titel": "Datei 3: Steuerung (verbindet Sensor und Anzeige)",
            "text": "Hier passiert die **Kommunikation**: Die Steuerung bekommt die Objekte im Konstruktor übergeben (**Dependency Injection**) und ruft ihre Methoden auf.",
            "code": {
                "Python": r'''# ---------------- steuerung.py ----------------
from sensor import Sensor          # -> Datei sensor.py, Klasse Sensor
from anzeige import Anzeige        # -> Datei anzeige.py, Klasse Anzeige


class Steuerung:
    def __init__(self, sensor: Sensor, anzeige: Anzeige, grenzwert):
        self.sensor = sensor       # Steuerung HAT EINEN Sensor (Komposition)
        self.anzeige = anzeige     # Steuerung HAT EINE Anzeige
        self.grenzwert = grenzwert

    def zyklus(self):
        wert = self.sensor.messen()                   # -> sensor.py: Sensor.messen()
        text = f"{self.sensor.name}: {wert} °C"
        zu_heiss = wert > self.grenzwert
        self.anzeige.zeigen(text, warnung=zu_heiss)   # -> anzeige.py: Anzeige.zeigen()''',
                "C++": r'''// ---------------- Steuerung.h ----------------
#pragma once
#include "Sensor.h"
#include "Anzeige.h"

class Steuerung {
public:
    Steuerung(const Sensor& sensor, const Anzeige& anzeige, double grenzwert);
    void zyklus() const;
private:
    const Sensor& sensor;      // Referenz: die Steuerung BESITZT die Objekte nicht,
    const Anzeige& anzeige;    // sie BENUTZT sie nur
    double grenzwert;
};

// ---------------- Steuerung.cpp ----------------
#include "Steuerung.h"

Steuerung::Steuerung(const Sensor& s, const Anzeige& a, double g)
    : sensor(s), anzeige(a), grenzwert(g) {}

void Steuerung::zyklus() const {
    double wert = sensor.messen();                                      // -> Sensor.cpp
    std::string text = sensor.getName() + ": " + std::to_string(wert) + " C";
    anzeige.zeigen(text, wert > grenzwert);                             // -> Anzeige.cpp
}''',
                "C#": r'''// ---------------- Steuerung.cs ----------------
namespace Anlage;

public class Steuerung
{
    private readonly Sensor sensor;     // HAT EINEN Sensor
    private readonly Anzeige anzeige;   // HAT EINE Anzeige
    private readonly double grenzwert;

    public Steuerung(Sensor sensor, Anzeige anzeige, double grenzwert)
    {
        this.sensor = sensor;
        this.anzeige = anzeige;
        this.grenzwert = grenzwert;
    }

    public void Zyklus()
    {
        double wert = sensor.Messen();                                // -> Sensor.cs
        anzeige.Zeigen($"{sensor.Name}: {wert} °C", wert > grenzwert); // -> Anzeige.cs
    }
}''',
            },
        },
        {
            "titel": "Datei 4: Startpunkt (alles zusammenstecken)",
            "code": {
                "Python": r'''# ---------------- main.py ----------------
import time

from sensor import Sensor
from anzeige import Anzeige
from steuerung import Steuerung


def main():
    # 1) Objekte erzeugen
    sensor = Sensor("Serverraum")
    anzeige = Anzeige()

    # 2) Objekte verbinden: Steuerung bekommt Sensor + Anzeige übergeben
    steuerung = Steuerung(sensor, anzeige, grenzwert=30)

    # 3) Laufen lassen
    for _ in range(5):
        steuerung.zyklus()        # -> steuerung.py: Steuerung.zyklus()
        time.sleep(1)


if __name__ == "__main__":
    main()''',
                "C++": r'''// ---------------- main.cpp ----------------
#include "Sensor.h"
#include "Anzeige.h"
#include "Steuerung.h"
#include <chrono>
#include <thread>

int main() {
    Sensor sensor("Serverraum");                      // 1) Objekte erzeugen
    Anzeige anzeige;
    Steuerung steuerung(sensor, anzeige, 30.0);       // 2) verbinden

    for (int i = 0; i < 5; i++) {                     // 3) laufen lassen
        steuerung.zyklus();
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    return 0;
}''',
                "C#": r'''// ---------------- Program.cs ----------------
using Anlage;                                    // Namespace der anderen Dateien

var sensor = new Sensor("Serverraum");           // 1) Objekte erzeugen
var anzeige = new Anzeige();
var steuerung = new Steuerung(sensor, anzeige, 30);   // 2) verbinden

for (int i = 0; i < 5; i++)                      // 3) laufen lassen
{
    steuerung.Zyklus();
    Thread.Sleep(1000);
}''',
            },
            "ausgabe": "[✓] Serverraum: 24.3 °C\n[⚠] Serverraum: 31.8 °C\n...",
        },
    ],

    "unterschiede": """
- **Python:** `import` lädt eine Datei zur Laufzeit. Die Dateien müssen im selben Ordner liegen oder in einem Paket (Ordner mit `__init__.py`).
- **C++:** Header (.h) = Deklaration, .cpp = Umsetzung. `#include` kopiert den Header-Text buchstäblich hinein. `#pragma once` schützt vor doppeltem Einbinden. Alle .cpp-Dateien müssen kompiliert und **gelinkt** werden.
- **C#:** Kein Import von Dateien nötig. Alles im Projekt ist bekannt. `namespace` + `using` sorgen für Ordnung.
""",

    "tipps": [
        "**Abhängigkeiten nur in eine Richtung:** Die Steuerung kennt den Sensor, aber der Sensor kennt die Steuerung NICHT. Sonst entstehen zyklische Imports.",
        "Objekte im Konstruktor übergeben (Dependency Injection) statt sie in der Klasse selbst zu erzeugen. So kann man später leicht einen echten durch einen simulierten Sensor ersetzen, z.B. zum Testen ohne Hardware.",
        "Soll ein Objekt ein anderes 'zurückrufen' (z.B. ein Button meldet einen Klick), übergibt man eine **Funktion** (Callback). So funktioniert `command=...` bei customtkinter!",
    ],
    "fehler": [
        "Python: **Zirkulärer Import** (a.py importiert b.py und b.py importiert a.py) führt zu `ImportError`. Lösung: Abhängigkeit auflösen oder gemeinsamen Teil auslagern.",
        "Python: Datei gleich benennen wie ein Standardmodul (`random.py`, `json.py`). Dann importiert Python DEINE Datei!",
        "C++: `undefined reference to Sensor::messen()` ist ein Linker-Fehler, weil die .cpp beim Kompilieren nicht angegeben wurde.",
        "C++: Header ohne `#pragma once` wird doppelt eingebunden und erzeugt den Fehler 'redefinition of class'.",
    ],
    "siehe_auch": ["module_imports", "klassen_objekte", "polymorphie", "konstruktor"],
}
