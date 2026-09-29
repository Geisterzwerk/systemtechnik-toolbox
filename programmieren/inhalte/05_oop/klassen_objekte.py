# Thema: Klassen & Objekte  (Kategorie: Objektorientierung)
THEMA = {
    "titel": "Klassen & Objekte",
    "reihenfolge": 1,
    "kurz": "Die Grundidee der Objektorientierung: Eine Klasse ist der Bauplan, ein Objekt ist das gebaute Ding.",
    "stichworte": ["klasse", "class", "objekt", "object", "instanz", "instance", "oop",
                   "objektorientiert", "objektorientierung", "attribut", "methode", "eigenschaft",
                   "bauplan", "self", "this", "member", "feld", "struct"],

    "erklaerung": """
## Die Idee
Bisher waren **Daten** (Variablen) und **Funktionen** getrennt. OOP packt beides zusammen: Ein **Objekt** weiss etwas (Attribute) und kann etwas (Methoden).
- **Klasse** = Bauplan, z.B. "Temperatursensor"
- **Objekt / Instanz** = ein konkretes Exemplar nach diesem Bauplan, z.B. "Sensor im Serverraum" und "Sensor im Labor"
- **Attribute** (Felder, Eigenschaften) = Daten des Objekts: `name`, `wert`
- **Methoden** = Funktionen des Objekts: `messen()`, `anzeigen()`
Jedes Objekt hat **eigene** Attributwerte, aber alle teilen sich dieselben Methoden.
## self / this
Innerhalb einer Methode verweist `self` (Python) bzw. `this` (C++/C#) auf **das Objekt, mit dem die Methode gerade aufgerufen wurde**. Bei `sensor1.messen()` ist `self` gleich `sensor1`.
- **Python:** `self` muss IMMER als erster Parameter stehen und beim Zugriff geschrieben werden: `self.wert`
- **C++ / C#:** `this` ist automatisch da und darf meistens weggelassen werden.
## Die 4 Säulen der OOP
- **Kapselung:** Interne Daten schützen, nur über Methoden zugreifen
- **Vererbung:** Eine Klasse übernimmt alles von einer anderen und erweitert es
- **Polymorphie:** Gleicher Methodenaufruf, unterschiedliches Verhalten je nach Objekt
- **Abstraktion:** Nur das Wichtige nach aussen zeigen, Details verstecken
""",

    "bild": "klasse_objekt.png",
    "bild_text": "Eine Klasse (Bauplan) → viele Objekte mit eigenen Werten",

    "beispiele": [
        {
            "titel": "Erste Klasse: Temperatursensor",
            "code": {
                "Python": r'''class TemperaturSensor:
    """Bauplan für einen Temperatursensor."""

    def __init__(self, name, grenzwert):    # Konstruktor (siehe nächstes Thema)
        self.name = name                    # Attribut
        self.grenzwert = grenzwert
        self.wert = 0.0

    def messen(self, neuer_wert):           # Methode
        self.wert = neuer_wert

    def ist_zu_heiss(self):
        return self.wert > self.grenzwert

    def anzeigen(self):
        print(f"{self.name}: {self.wert} °C")


# ---- Objekte erzeugen (Instanzen) ----
serverraum = TemperaturSensor("Serverraum", 30)
labor = TemperaturSensor("Labor", 25)

serverraum.messen(32.5)                 # Methode aufrufen
labor.messen(21.0)

serverraum.anzeigen()                   # Serverraum: 32.5 °C
print(serverraum.ist_zu_heiss())        # True
print(labor.ist_zu_heiss())             # False''',
                "C++": r'''#include <iostream>
#include <string>

class TemperaturSensor {
public:                                   // von aussen zugänglich
    std::string name;                     // Attribute
    double grenzwert;
    double wert = 0.0;

    TemperaturSensor(std::string n, double g) : name(n), grenzwert(g) {}   // Konstruktor

    void messen(double neuerWert) {       // Methode
        wert = neuerWert;                 // gleich wie this->wert = neuerWert;
    }

    bool istZuHeiss() const {             // const = ändert das Objekt nicht
        return wert > grenzwert;
    }

    void anzeigen() const {
        std::cout << name << ": " << wert << " C\n";
    }
};   // <- Semikolon nach der Klasse!

int main() {
    TemperaturSensor serverraum("Serverraum", 30);   // Objekt erzeugen
    TemperaturSensor labor("Labor", 25);

    serverraum.messen(32.5);
    labor.messen(21.0);

    serverraum.anzeigen();
    std::cout << std::boolalpha << serverraum.istZuHeiss() << "\n";   // true
    return 0;
}''',
                "C#": r'''var serverraum = new TemperaturSensor("Serverraum", 30);   // Objekt erzeugen mit new
var labor = new TemperaturSensor("Labor", 25);

serverraum.Messen(32.5);
labor.Messen(21.0);

serverraum.Anzeigen();                          // Serverraum: 32.5 °C
Console.WriteLine(serverraum.IstZuHeiss());     // True

class TemperaturSensor
{
    public string Name;                  // Felder (Attribute)
    public double Grenzwert;
    public double Wert = 0.0;

    public TemperaturSensor(string name, double grenzwert)   // Konstruktor
    {
        Name = name;
        Grenzwert = grenzwert;
    }

    public void Messen(double neuerWert) => Wert = neuerWert;
    public bool IstZuHeiss() => Wert > Grenzwert;
    public void Anzeigen() => Console.WriteLine($"{Name}: {Wert} °C");
}''',
            },
            "ausgabe": "Serverraum: 32.5 °C\nTrue\nFalse",
        },
    ],

    "unterschiede": """
- **Python:** `self` explizit, alles ist öffentlich (Privates nur per Konvention mit `_`). Objekt erzeugen ohne `new`: `Sensor()`.
- **C++:** `public:` / `private:` als Abschnitte, Semikolon nach `};`. Objekte liegen direkt auf dem Stack (`Sensor s(...)`) oder mit `new` / Smart-Pointer auf dem Heap.
- **C#:** Objekte immer mit `new`, Sichtbarkeit (`public`, `private`) bei jedem Member. Klassen sind **Referenztypen**, `struct` sind Werttypen.
""",

    "tipps": [
        "Klassennamen sind Substantive in PascalCase (`Motor`, `SerielleVerbindung`), Methoden sind Verben (`starten()`, `senden()`).",
        "Eine Klasse = eine Verantwortung. Ein `Sensor` misst, eine `Anzeige` zeigt an. Wie sie zusammenarbeiten, steht im Thema **Klassen in mehreren Dateien**.",
    ],
    "fehler": [
        "Python: `self` als ersten Parameter vergessen: `TypeError: messen() takes 1 positional argument but 2 were given`.",
        "Python: `wert = 5` statt `self.wert = 5` in einer Methode erzeugt nur eine lokale Variable, und das Attribut bleibt unverändert!",
        "C++: Semikolon nach der schliessenden `}` der Klasse vergessen.",
    ],
    "siehe_auch": ["konstruktor", "kapselung", "vererbung", "mehrere_dateien"],
}
