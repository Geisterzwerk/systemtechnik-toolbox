# Thema: Kapselung (public / private)  (Kategorie: Objektorientierung)
THEMA = {
    "titel": "Kapselung (public / private)",
    "reihenfolge": 3,
    "kurz": "Interne Daten schützen: Zugriff nur über kontrollierte Methoden, Getter/Setter und Properties.",
    "stichworte": ["kapselung", "encapsulation", "private", "public", "protected", "getter", "setter",
                   "property", "eigenschaft", "zugriff", "sichtbarkeit", "access modifier", "_",
                   "__", "readonly", "validieren"],

    "erklaerung": """
## Stell dir vor …
Ein **Kaffeeautomat**: Aussen gibt es Knöpfe und einen Münzschlitz – das darfst du benutzen. Das Innenleben mit Heizung, Pumpe und Kasse ist verschlossen. So kann niemand aus Versehen die Temperatur verstellen oder Geld herausnehmen. Kapselung macht dasselbe mit Objekten: Nur die vorgesehenen Methoden sind von aussen erreichbar.
## Warum kapseln?
Stell dir einen Motor mit dem Attribut `drehzahl` vor. Wenn jeder direkt `motor.drehzahl = 99999` schreiben kann, gibt es keine Kontrolle. Kapselung heisst:
- Attribute sind **privat**, also von aussen nicht direkt erreichbar
- Der Zugriff läuft über **Methoden**, die **prüfen** (validieren), ob ein Wert gültig ist
- Die interne Umsetzung kann sich ändern, ohne dass anderer Code angepasst werden muss
## Zugriffsmodifizierer
- **public:** von überall zugreifbar
- **private:** nur innerhalb der eigenen Klasse
- **protected:** in der Klasse und in abgeleiteten Klassen (siehe Vererbung)
- **C# internal:** nur innerhalb desselben Projekts
## Python
Python hat **kein echtes private**. Es gibt nur Konventionen:
- `_wert` (ein Unterstrich): "intern, bitte nicht von aussen benutzen"
- `__wert` (zwei Unterstriche): Der Name wird verschleiert (Name Mangling), der Zugriff ist dadurch erschwert
- `@property` erlaubt Getter und Setter, die sich wie normale Attribute anfühlen
## 🔬 Genauer hingeschaut
- **Regeln, die immer gelten:** Kapselung schützt sogenannte Invarianten – z.B. „der Kontostand wird nie negativ“ oder „der Widerstand ist immer grösser als 0“. Weil nur die eigenen Methoden die Werte ändern dürfen, reicht es, die Regel dort zu prüfen.
- **Properties:** Python (`@property`) und C# (`get`/`set`) erlauben, ein Attribut wie eine Variable zu benutzen und trotzdem beim Setzen zu prüfen. Von aussen sieht es aus wie `r.ohm = 100`, innen läuft eine Prüfung.
- **Python vertraut dir:** Ein führender Unterstrich (`_wert`) heisst nur „bitte nicht von aussen benutzen“. Zwei Unterstriche (`__wert`) benennen das Attribut intern um – ein echtes Verbot gibt es in Python nicht.
## 💡 Wusstest du?
- Das klassische Lehrbeispiel ist das **Bankkonto**: Der Kontostand ist privat, und nur `einzahlen()` und `abheben()` dürfen ihn ändern – mit Prüfung, ob genug Geld da ist.
""",

    "tabelle": {
        "titel": "📊 Zugriffsrechte",
        "kopf": ["Modifizierer", "Eigene Klasse", "Abgeleitete Klasse", "Überall", "Python-Entsprechung"],
        "zeilen": [
            ["public", "✅", "✅", "✅", "name"],
            ["protected", "✅", "✅", "❌", "_name (Konvention)"],
            ["private", "✅", "❌", "❌", "__name (Name Mangling)"],
        ],
    },

    "beispiele": [
        {
            "titel": "Drehzahl mit Prüfung (Getter / Setter / Property)",
            "code": {
                "Python": r'''class Motor:
    MAX = 3000

    def __init__(self):
        self._drehzahl = 0              # "privat" (Konvention)

    @property
    def drehzahl(self):                 # Getter: motor.drehzahl
        return self._drehzahl

    @drehzahl.setter
    def drehzahl(self, wert):           # Setter: motor.drehzahl = 1500
        if not 0 <= wert <= Motor.MAX:
            raise ValueError(f"Drehzahl muss 0..{Motor.MAX} sein")
        self._drehzahl = wert


motor = Motor()
motor.drehzahl = 1500       # ruft den Setter auf -> geprüft
print(motor.drehzahl)       # 1500
motor.drehzahl = 99999      # ValueError!''',
                "C++": r'''#include <stdexcept>

class Motor {
public:
    static const int MAX = 3000;

    int getDrehzahl() const {              // Getter
        return drehzahl;
    }

    void setDrehzahl(int wert) {           // Setter mit Prüfung
        if (wert < 0 || wert > MAX) {
            throw std::out_of_range("Drehzahl ungueltig");
        }
        drehzahl = wert;
    }

private:
    int drehzahl = 0;                      // von aussen NICHT erreichbar
};

// Motor m;
// m.setDrehzahl(1500);
// m.drehzahl = 5;   -> Compiler-Fehler: 'drehzahl' is private''',
                "C#": r'''var motor = new Motor();
motor.Drehzahl = 1500;          // ruft set auf -> geprüft
Console.WriteLine(motor.Drehzahl);
motor.Drehzahl = 99999;         // ArgumentOutOfRangeException

class Motor
{
    public const int Max = 3000;
    private int _drehzahl;              // privates Feld

    public int Drehzahl                 // Property (Eigenschaft)
    {
        get => _drehzahl;
        set
        {
            if (value < 0 || value > Max)          // value = zugewiesener Wert
                throw new ArgumentOutOfRangeException(nameof(value));
            _drehzahl = value;
        }
    }

    public string Name { get; private set; } = "Motor";   // Auto-Property: lesen öffentlich, schreiben privat
}''',
            },
        },
    ],

    "tipps": [
        "Standard: Attribute **private**, Methoden nur **public**, wenn sie von aussen gebraucht werden.",
        "Nicht für jedes Attribut blind Getter und Setter schreiben. Nur das freigeben, was wirklich gebraucht wird.",
    ],
    "fehler": [
        "Python: Im Setter `self.drehzahl = wert` statt `self._drehzahl = wert` schreiben. Der Setter ruft sich dann endlos selbst auf (RecursionError)!",
        "C++: `class` ist standardmässig private, `struct` standardmässig public. `public:` vergessen führt zu 'is private within this context'.",
    ],
    "siehe_auch": ["klassen_objekte", "vererbung", "fehlerbehandlung"],
}
