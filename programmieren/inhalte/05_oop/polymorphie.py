# Thema: Polymorphie & abstrakte Klassen  (Kategorie: Objektorientierung)
THEMA = {
    "titel": "Polymorphie & Interfaces",
    "reihenfolge": 5,
    "kurz": "Gleicher Aufruf, unterschiedliches Verhalten. Abstrakte Klassen und Interfaces als Vertrag.",
    "stichworte": ["polymorphie", "polymorphism", "virtual", "override", "abstrakt", "abstract",
                   "interface", "schnittstelle", "abc", "abstractmethod", "rein virtuell",
                   "pure virtual", "= 0", "vielgestaltigkeit", "dynamic dispatch", "duck typing"],

    "erklaerung": """
## Die Idee
Man hat eine Liste mit **verschiedenen** Geräten (Motor, Lampe, Ventil) und ruft bei allen `einschalten()` auf. **Jedes Gerät weiss selbst, was es dabei tun muss.** Der aufrufende Code muss den genauen Typ nicht kennen.
Das macht Programme **erweiterbar**: Ein neues Gerät (z.B. eine Pumpe) braucht nur eine neue Klasse. Die Schleife, die alle einschaltet, bleibt unverändert.
## Abstrakte Klasse
Eine Basisklasse, von der man **keine Objekte erzeugen** kann. Sie gibt nur vor, **welche Methoden** jede Kindklasse haben **muss**.
- **Python:** `from abc import ABC, abstractmethod`
- **C++:** "rein virtuelle" Methode: `virtual void einschalten() = 0;`
- **C#:** `abstract class` und `abstract void Einschalten();`
## Interface (Schnittstelle)
Ein reiner **Vertrag**: "Jede Klasse, die mich umsetzt, hat diese Methoden." In C# sehr verbreitet (`interface IGeraet`), eine Klasse kann **mehrere** Interfaces umsetzen.
## Python: Duck Typing
"Wenn es quakt wie eine Ente, ist es eine Ente." In Python funktioniert Polymorphie auch **ohne** gemeinsame Basisklasse. Es reicht, dass jedes Objekt die aufgerufene Methode hat.
""",

    "beispiele": [
        {
            "titel": "Verschiedene Geräte gemeinsam steuern",
            "code": {
                "Python": r'''from abc import ABC, abstractmethod


class Geraet(ABC):                          # abstrakte Basisklasse
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def einschalten(self):                  # MUSS jede Kindklasse umsetzen
        pass


class Motor(Geraet):
    def einschalten(self):
        print(f"{self.name}: fährt Drehzahl hoch")


class Lampe(Geraet):
    def einschalten(self):
        print(f"{self.name}: leuchtet")


class Ventil(Geraet):
    def einschalten(self):
        print(f"{self.name}: öffnet")


anlage = [Motor("M1"), Lampe("H1"), Ventil("Y1")]

for geraet in anlage:          # gleicher Aufruf ...
    geraet.einschalten()       # ... unterschiedliches Verhalten

# Geraet("x") -> TypeError: Can't instantiate abstract class''',
                "C++": r'''#include <iostream>
#include <memory>
#include <string>
#include <vector>

class Geraet {                                   // abstrakte Klasse
public:
    explicit Geraet(std::string name) : name(std::move(name)) {}
    virtual ~Geraet() = default;
    virtual void einschalten() const = 0;        // rein virtuell: MUSS überschrieben werden
protected:
    std::string name;
};

class Motor : public Geraet {
public:
    using Geraet::Geraet;                        // Konstruktor übernehmen
    void einschalten() const override { std::cout << name << ": faehrt hoch\n"; }
};

class Lampe : public Geraet {
public:
    using Geraet::Geraet;
    void einschalten() const override { std::cout << name << ": leuchtet\n"; }
};

int main() {
    // Basisklassen-ZEIGER auf verschiedene Objekte -> Polymorphie
    std::vector<std::unique_ptr<Geraet>> anlage;
    anlage.push_back(std::make_unique<Motor>("M1"));
    anlage.push_back(std::make_unique<Lampe>("H1"));

    for (const auto& geraet : anlage) {
        geraet->einschalten();                   // richtige Methode zur Laufzeit
    }
    return 0;
}''',
                "C#": r'''var anlage = new List<IGeraet> { new Motor("M1"), new Lampe("H1") };

foreach (IGeraet geraet in anlage)
{
    geraet.Einschalten();            // gleicher Aufruf, anderes Verhalten
}

interface IGeraet                    // Interface = Vertrag (Name beginnt mit I)
{
    string Name { get; }
    void Einschalten();
}

abstract class GeraetBasis : IGeraet // abstrakte Klasse setzt das Interface um
{
    public string Name { get; }
    protected GeraetBasis(string name) => Name = name;
    public abstract void Einschalten();   // MUSS überschrieben werden
}

class Motor : GeraetBasis
{
    public Motor(string name) : base(name) { }
    public override void Einschalten() => Console.WriteLine($"{Name}: fährt hoch");
}

class Lampe : GeraetBasis
{
    public Lampe(string name) : base(name) { }
    public override void Einschalten() => Console.WriteLine($"{Name}: leuchtet");
}''',
            },
            "ausgabe": "M1: fährt Drehzahl hoch\nH1: leuchtet\nY1: öffnet",
        },
    ],

    "tipps": [
        "Wenn du im Code `if typ == \"Motor\": ... elif typ == \"Lampe\": ...` schreibst, ist das oft ein Zeichen, dass Polymorphie die bessere Lösung wäre.",
        "C++: Polymorphie funktioniert nur über **Zeiger oder Referenzen** auf die Basisklasse. Moderne Wahl: `std::unique_ptr`.",
    ],
    "fehler": [
        "C++: Objekt als WERT in einen `std::vector<Geraet>` speichern. Dabei wird der Kind-Teil 'abgeschnitten' (Object Slicing). Zeiger verwenden!",
        "Abstrakte Methode in der Kindklasse vergessen: Python `TypeError` beim Erzeugen, C++/C# Compiler-Fehler.",
    ],
    "siehe_auch": ["vererbung", "mehrere_dateien", "pointer_referenzen"],
}
