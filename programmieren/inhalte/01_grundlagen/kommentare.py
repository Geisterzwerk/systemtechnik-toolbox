# Thema: Kommentare & Namensregeln  (Kategorie: Grundlagen)
THEMA = {
    "titel": "Kommentare & Namensregeln",
    "reihenfolge": 8,
    "kurz": "Code verständlich machen: Kommentare, Dokumentation und wie man Dinge benennt.",
    "stichworte": ["kommentar", "comment", "docstring", "dokumentation", "namensregeln",
                   "namenskonvention", "snake_case", "camelcase", "pascalcase", "stil", "style", "pep8"],

    "erklaerung": """
## Stell dir vor …
Ein **Bauplan mit Randnotizen**: Die Zeichnung zeigt, was gebaut wird. Die Notizen am Rand erklären, **warum** etwas so ist („Wand doppelt, wegen Lärm“). Kommentare sind diese Randnotizen. Der Computer überliest sie – sie sind für Menschen, auch für dich selbst in drei Monaten.
## Kommentare
Kommentare werden vom Computer ignoriert. Sie sind für **Menschen** geschrieben, also für Teamkollegen und für dich selbst in 3 Monaten.
- Erkläre das **Warum**, nicht das Was: `# 5τ warten, damit der Kondensator voll ist` statt `# warte 5 Sekunden`
- Funktionen und Klassen dokumentieren: Was machen sie, welche Parameter haben sie, was geben sie zurück?
## Namensregeln (Konventionen)
Jede Sprache hat ihren eigenen Stil. Wer sich daran hält, macht Code für andere sofort lesbar.
## 🔬 Genauer hingeschaut
- **Warum statt was:** `i += 1  # i um 1 erhöhen` hilft niemandem – das sieht man. Gut ist: `# Index 0 ist die Kopfzeile, darum ab 1`. Der beste Kommentar erklärt eine Entscheidung, die man dem Code nicht ansieht.
- **Dokumentations-Kommentare:** Python hat Docstrings (`\"\"\"…\"\"\"` direkt unter `def`), die `help()` anzeigt. C# hat `///`-Kommentare, C++ oft Doxygen-Kommentare. Editoren zeigen sie beim Überfahren mit der Maus an.
- **Kommentare veralten:** Wird Code geändert, aber der Kommentar nicht, lügt der Kommentar. Darum lieber gute Namen verwenden, die sich selbst erklären, und Kommentare beim Ändern mitpflegen.
## 💡 Wusstest du?
- Für Python gibt es seit 2001 einen offiziellen Stil-Leitfaden, **PEP 8**. Er regelt u.a. Einrückung (4 Leerzeichen), Zeilenlänge und Namensschreibweise – Werkzeuge wie Linter prüfen das automatisch.
""",

    "tabelle": {
        "titel": "📊 Namenskonventionen",
        "kopf": ["Was", "Python (PEP 8)", "C++ (üblich)", "C# (Microsoft)"],
        "zeilen": [
            ["Variable", "messwert_neu", "messwertNeu", "messwertNeu"],
            ["Funktion / Methode", "berechne_leistung()", "berechneLeistung()", "BerechneLeistung()"],
            ["Klasse", "TemperaturSensor", "TemperaturSensor", "TemperaturSensor"],
            ["Konstante", "MAX_SPANNUNG", "MAX_SPANNUNG / kMaxSpannung", "MaxSpannung"],
            ["Privates Attribut", "_wert", "m_wert / wert_", "_wert"],
            ["Datei", "temperatur_sensor.py", "TemperaturSensor.h / .cpp", "TemperaturSensor.cs"],
        ],
        "hinweis": "Stil-Namen: `snake_case` (klein_mit_unterstrich), `camelCase` (erstesWortKlein), `PascalCase` (JedesWortGross), `UPPER_CASE` (Konstanten).",
    },

    "beispiele": [
        {
            "titel": "Kommentare und Dokumentation",
            "code": {
                "Python": r'''# Einzeiliger Kommentar

def leistung(u, i):
    """
    Berechnet die elektrische Leistung.   <- Docstring (Dokumentation)

    u: Spannung in Volt
    i: Strom in Ampere
    Rückgabe: Leistung in Watt
    """
    return u * i   # P = U * I

# help(leistung) zeigt den Docstring an''',
                "C++": r'''// Einzeiliger Kommentar

/*
   Mehrzeiliger
   Kommentar
*/

/**
 * Berechnet die elektrische Leistung.   (Doxygen-Stil)
 * @param u Spannung in Volt
 * @param i Strom in Ampere
 * @return Leistung in Watt
 */
double leistung(double u, double i) {
    return u * i;   // P = U * I
}''',
                "C#": r'''// Einzeiliger Kommentar

/* Mehrzeiliger
   Kommentar */

/// <summary>
/// Berechnet die elektrische Leistung.   (XML-Doku, zeigt Visual Studio als Tooltip an)
/// </summary>
/// <param name="u">Spannung in Volt</param>
/// <param name="i">Strom in Ampere</param>
/// <returns>Leistung in Watt</returns>
static double Leistung(double u, double i)
{
    return u * i;   // P = U * I
}''',
            },
        },
    ],

    "tipps": [
        "VS Code: `Ctrl + K, Ctrl + C` kommentiert markierte Zeilen aus, `Ctrl + K, Ctrl + U` hebt es wieder auf.",
        "Einheiten in Namen oder Kommentare packen: `zeit_ms`, `spannung_v`.",
    ],
    "fehler": [
        "Auskommentierten alten Code ewig stehen lassen. Dafür gibt es Git!",
        "Kommentar und Code widersprechen sich, weil nur der Code geändert wurde.",
    ],
    "siehe_auch": ["programmablauf", "funktionen_grundlagen"],
}
