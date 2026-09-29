# Thema: Vererbung  (Kategorie: Objektorientierung)
THEMA = {
    "titel": "Vererbung",
    "reihenfolge": 4,
    "kurz": "Eine Klasse übernimmt Attribute und Methoden einer anderen und erweitert sie.",
    "stichworte": ["vererbung", "inheritance", "erben", "basisklasse", "oberklasse", "elternklasse",
                   "unterklasse", "abgeleitet", "kindklasse", "super", "base", "ist ein", "is a",
                   "override", "ueberschreiben", "überschreiben", "extends"],

    "erklaerung": """
## Prinzip
Viele Dinge haben Gemeinsamkeiten: Ein Temperatursensor und ein Drucksensor haben beide einen Namen, einen Wert und eine Einheit. Statt das doppelt zu programmieren:
- **Basisklasse** (Ober-/Elternklasse) `Sensor` enthält alles Gemeinsame
- **Abgeleitete Klassen** (Unter-/Kindklassen) `TemperaturSensor` und `DruckSensor` **erben** davon und ergänzen nur das Spezielle
## Die "ist-ein"-Regel
Vererbung passt nur, wenn der Satz "**X ist ein Y**" stimmt:
- ✅ Ein Temperatursensor **ist ein** Sensor
- ❌ Ein Auto **ist ein** Motor. Falsch! Ein Auto **hat einen** Motor, das nennt man **Komposition** (siehe *Klassen in mehreren Dateien*).
## Basisklasse aufrufen
Die Kindklasse ruft den Konstruktor der Basisklasse auf, damit deren Teil initialisiert wird:
- **Python:** `super().__init__(...)`
- **C++:** in der Initialisierungsliste: `: Sensor(name)`
- **C#:** `: base(name)`
## Methoden überschreiben
Die Kindklasse kann eine geerbte Methode **ersetzen** (override). Wie das Programm dann zur Laufzeit die richtige Methode wählt, erklärt das Thema **Polymorphie**.
""",

    "bild": "vererbung.png",
    "bild_text": "UML-Klassendiagramm: Sensor als Basisklasse, zwei abgeleitete Klassen",

    "beispiele": [
        {
            "titel": "Sensor → TemperaturSensor / DruckSensor",
            "code": {
                "Python": r'''class Sensor:                                   # Basisklasse
    def __init__(self, name, einheit):
        self.name = name
        self.einheit = einheit
        self.wert = 0.0

    def anzeigen(self):
        print(f"{self.name}: {self.wert} {self.einheit}")


class TemperaturSensor(Sensor):                 # erbt von Sensor
    def __init__(self, name):
        super().__init__(name, "°C")            # Basisklasse initialisieren

    def in_fahrenheit(self):                    # NEUE Methode, nur hier
        return self.wert * 9 / 5 + 32


class DruckSensor(Sensor):
    def __init__(self, name, max_bar):
        super().__init__(name, "bar")
        self.max_bar = max_bar                  # zusätzliches Attribut

    def anzeigen(self):                         # Methode ÜBERSCHREIBEN
        super().anzeigen()                      # Original trotzdem nutzen
        if self.wert > self.max_bar:
            print("  ⚠ Überdruck!")


t = TemperaturSensor("Kühlwasser")
t.wert = 20
t.anzeigen()                  # geerbt: Kühlwasser: 20 °C
print(t.in_fahrenheit())      # 68.0

d = DruckSensor("Leitung", 6)
d.wert = 7.2
d.anzeigen()                  # Leitung: 7.2 bar + Warnung
print(isinstance(t, Sensor))  # True -> ein TemperaturSensor IST EIN Sensor''',
                "C++": r'''#include <iostream>
#include <string>

class Sensor {                                   // Basisklasse
public:
    Sensor(std::string name, std::string einheit) : name(name), einheit(einheit) {}
    virtual ~Sensor() = default;                 // wichtig bei Vererbung!

    virtual void anzeigen() const {              // virtual = darf überschrieben werden
        std::cout << name << ": " << wert << " " << einheit << "\n";
    }

    double wert = 0.0;

protected:                                       // für Kindklassen sichtbar
    std::string name;
    std::string einheit;
};

class TemperaturSensor : public Sensor {         // erbt von Sensor
public:
    TemperaturSensor(std::string name) : Sensor(name, "C") {}   // Basis-Konstruktor

    double inFahrenheit() const { return wert * 9 / 5 + 32; }
};

class DruckSensor : public Sensor {
public:
    DruckSensor(std::string name, double maxBar) : Sensor(name, "bar"), maxBar(maxBar) {}

    void anzeigen() const override {             // überschreiben
        Sensor::anzeigen();                      // Original aufrufen
        if (wert > maxBar) std::cout << "  Ueberdruck!\n";
    }

private:
    double maxBar;
};

int main() {
    TemperaturSensor t("Kuehlwasser");
    t.wert = 20;
    t.anzeigen();
    std::cout << t.inFahrenheit() << "\n";

    DruckSensor d("Leitung", 6);
    d.wert = 7.2;
    d.anzeigen();
    return 0;
}''',
                "C#": r'''var t = new TemperaturSensor("Kühlwasser") { Wert = 20 };
t.Anzeigen();
Console.WriteLine(t.InFahrenheit());     // 68

var d = new DruckSensor("Leitung", 6) { Wert = 7.2 };
d.Anzeigen();
Console.WriteLine(t is Sensor);          // True

class Sensor                                        // Basisklasse
{
    public double Wert { get; set; }
    protected string Name;                          // für Kindklassen sichtbar
    protected string Einheit;

    public Sensor(string name, string einheit)
    {
        Name = name;
        Einheit = einheit;
    }

    public virtual void Anzeigen() =>               // virtual = überschreibbar
        Console.WriteLine($"{Name}: {Wert} {Einheit}");
}

class TemperaturSensor : Sensor                     // erbt von Sensor
{
    public TemperaturSensor(string name) : base(name, "°C") { }

    public double InFahrenheit() => Wert * 9 / 5 + 32;
}

class DruckSensor : Sensor
{
    private double maxBar;

    public DruckSensor(string name, double maxBar) : base(name, "bar")
    {
        this.maxBar = maxBar;
    }

    public override void Anzeigen()                 // überschreiben
    {
        base.Anzeigen();                            // Original aufrufen
        if (Wert > maxBar) Console.WriteLine("  ⚠ Überdruck!");
    }
}''',
            },
        },
    ],

    "unterschiede": """
- **Python:** `class Kind(Eltern):`, alle Methoden sind automatisch überschreibbar. Mehrfachvererbung ist möglich.
- **C++:** `class Kind : public Eltern`. Methoden müssen `virtual` sein, damit Überschreiben polymorph funktioniert. Die Basisklasse braucht einen `virtual`-Destruktor. Mehrfachvererbung ist möglich.
- **C#:** `class Kind : Eltern`, `virtual` in der Basis und `override` in der Kindklasse sind Pflicht. **Nur EINE Basisklasse**, dafür beliebig viele Interfaces.
""",

    "tipps": [
        "Vererbung sparsam einsetzen. Eine tiefe Hierarchie (5 Ebenen) wird schnell unübersichtlich. Oft ist Komposition die bessere Wahl.",
        "Die `override`-Markierung in C++ immer schreiben. Dann merkt der Compiler, wenn man sich im Methodennamen vertippt hat.",
    ],
    "fehler": [
        "Python: `super().__init__()` vergessen. Dann fehlen die Attribute der Basisklasse (`AttributeError`).",
        "C++: `virtual` in der Basisklasse vergessen. Dann wird bei einem Basis-Zeiger die FALSCHE (Basis-)Methode aufgerufen.",
        "Vererbung für eine 'hat-ein'-Beziehung verwenden (Auto erbt von Motor).",
    ],
    "siehe_auch": ["polymorphie", "klassen_objekte", "kapselung", "mehrere_dateien"],
}
