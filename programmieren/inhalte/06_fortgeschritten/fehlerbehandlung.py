# Thema: Fehlerbehandlung (Exceptions)  (Kategorie: Fortgeschritten)
THEMA = {
    "titel": "Fehlerbehandlung (Exceptions)",
    "reihenfolge": 1,
    "kurz": "Fehler zur Laufzeit abfangen, statt dass das Programm abstürzt: try / catch / finally.",
    "stichworte": ["exception", "fehler", "try", "catch", "except", "finally", "raise", "throw",
                   "fehlerbehandlung", "error", "absturz", "valueerror", "traceback", "eigene exception",
                   "try catch", "try except"],

    "erklaerung": """
## Das Problem
Manche Fehler passieren erst **zur Laufzeit**: Die Datei fehlt, der Benutzer tippt "abc" statt einer Zahl, der Sensor antwortet nicht, oder es wird durch 0 geteilt. Ohne Behandlung **stürzt das Programm ab**.
## Die Lösung: try / catch
- **try:** Hier steht Code, der schiefgehen **könnte**
- **catch / except:** wird **nur bei einem Fehler** ausgeführt und behandelt ihn
- **finally:** wird **immer** ausgeführt, egal ob ein Fehler auftrat oder nicht. Hier räumt man auf (Verbindung schliessen).
- **Python else:** läuft nur, wenn KEIN Fehler auftrat
## Fehler selbst auslösen
Wenn deine Funktion ungültige Werte bekommt, **wirf** einen Fehler: `raise` (Python) / `throw` (C++/C#). So merkt der Aufrufer sofort, dass etwas nicht stimmt.
## Den Traceback lesen (Python)
Die Fehlermeldung von unten nach oben lesen: Die **letzte Zeile** nennt den Fehlertyp, darüber steht die Datei mit der Zeilennummer.
""",

    "bild": "try_catch.png",
    "bild_text": "Ablauf von try / catch / finally",

    "tabelle": {
        "titel": "📊 Häufige Fehlertypen",
        "kopf": ["Situation", "Python", "C++", "C#"],
        "zeilen": [
            ["Text ist keine Zahl", "ValueError", "std::invalid_argument", "FormatException"],
            ["Division durch 0", "ZeroDivisionError", "(kein Exception! undefiniert bzw. inf)", "DivideByZeroException (int)"],
            ["Index ausserhalb", "IndexError", "std::out_of_range (.at())", "IndexOutOfRangeException / ArgumentOutOfRangeException"],
            ["Schlüssel fehlt", "KeyError", "std::out_of_range (.at())", "KeyNotFoundException"],
            ["Datei fehlt", "FileNotFoundError", "(Stream prüfen: !datei)", "FileNotFoundException"],
            ["Objekt ist leer (None / null)", "AttributeError / TypeError", "(Absturz!)", "NullReferenceException"],
            ["Falscher Typ", "TypeError", "(Compiler-Fehler)", "InvalidCastException"],
        ],
    },

    "beispiele": [
        {
            "titel": "Eingabe prüfen mit try / catch / finally",
            "code": {
                "Python": r'''def teilen(a, b):
    return a / b

try:
    zahl = float(input("Zahl: "))
    ergebnis = teilen(100, zahl)
except ValueError:                        # speziellen Fehler abfangen
    print("Keine gültige Zahl!")
except ZeroDivisionError:
    print("Division durch 0!")
except Exception as e:                    # alle anderen (Sicherheitsnetz)
    print(f"Unerwarteter Fehler: {e}")
else:
    print(f"Ergebnis: {ergebnis}")        # nur wenn KEIN Fehler
finally:
    print("Fertig.")                      # IMMER''',
                "C++": r'''#include <iostream>
#include <stdexcept>
#include <string>

double teilen(double a, double b) {
    if (b == 0) {
        throw std::runtime_error("Division durch 0");   // selbst auslösen
    }
    return a / b;
}

int main() {
    std::string eingabe;
    std::cout << "Zahl: ";
    std::getline(std::cin, eingabe);

    try {
        double zahl = std::stod(eingabe);
        std::cout << "Ergebnis: " << teilen(100, zahl) << "\n";
    } catch (const std::invalid_argument&) {
        std::cout << "Keine gueltige Zahl!\n";
    } catch (const std::runtime_error& e) {
        std::cout << "Fehler: " << e.what() << "\n";    // what() = Fehlertext
    } catch (...) {                                      // alle anderen
        std::cout << "Unbekannter Fehler\n";
    }
    // C++ hat kein finally -> Aufräumen macht der Destruktor (RAII)
    return 0;
}''',
                "C#": r'''static double Teilen(double a, double b)
{
    if (b == 0)
        throw new DivideByZeroException("Division durch 0");   // selbst auslösen
    return a / b;
}

try
{
    double zahl = double.Parse(Console.ReadLine() ?? "");
    Console.WriteLine($"Ergebnis: {Teilen(100, zahl)}");
}
catch (FormatException)
{
    Console.WriteLine("Keine gültige Zahl!");
}
catch (DivideByZeroException ex)
{
    Console.WriteLine($"Fehler: {ex.Message}");
}
catch (Exception ex)                                           // alle anderen
{
    Console.WriteLine($"Unerwarteter Fehler: {ex.Message}");
}
finally
{
    Console.WriteLine("Fertig.");                              // IMMER
}''',
            },
        },
        {
            "titel": "Eigene Fehlerklasse (z.B. für Hardware)",
            "code": {
                "Python": r'''class SensorFehler(Exception):
    """Eigener Fehlertyp für Sensorprobleme."""


def lese_sensor(adresse):
    if adresse not in (0x48, 0x49):
        raise SensorFehler(f"Kein Sensor an Adresse {adresse:#04x}")
    return 23.5

try:
    lese_sensor(0x50)
except SensorFehler as e:
    print("Sensorproblem:", e)''',
                "C++": r'''class SensorFehler : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;    // Konstruktor übernehmen
};

double leseSensor(int adresse) {
    if (adresse != 0x48 && adresse != 0x49) {
        throw SensorFehler("Kein Sensor an dieser Adresse");
    }
    return 23.5;
}''',
                "C#": r'''static double LeseSensor(int adresse)
{
    if (adresse is not (0x48 or 0x49))
        throw new SensorFehler($"Kein Sensor an Adresse 0x{adresse:X2}");
    return 23.5;
}

class SensorFehler : Exception          // eigene Fehlerklasse
{
    public SensorFehler(string meldung) : base(meldung) { }
}''',
            },
        },
    ],

    "tipps": [
        "Möglichst **spezifische** Fehler abfangen (`ValueError`) und nicht pauschal alles. Sonst versteckt man echte Programmierfehler.",
        "Den try-Block klein halten: nur die Zeilen, die wirklich fehlschlagen können.",
        "Nicht jede Situation braucht eine Exception. Vorher prüfen (`if b != 0`) oder TryParse (C#) ist oft einfacher.",
    ],
    "fehler": [
        "Leeres `except: pass` bzw. `catch {}` verschluckt jeden Fehler, und niemand merkt, dass etwas schiefgeht.",
        "C++: Division durch 0 bei `int` wirft KEINE Exception, sondern führt zu einem Absturz bzw. undefiniertem Verhalten. Vorher prüfen!",
    ],
    "siehe_auch": ["typumwandlung", "dateien", "kapselung"],
}
