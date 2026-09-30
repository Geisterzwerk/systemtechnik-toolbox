# Thema: Temperatur messen  (Messtechnik / Sensoren)
THEMA = {
    "titel": "Temperatur messen",
    "reihenfolge": 1,
    "kurz": "Pt100, NTC und Thermoelement im Vergleich – wie sie funktionieren und wo sie ihre Tücken haben.",
    "stichworte": ["temperatur", "temperatursensor", "pt100", "pt1000", "rtd", "widerstandsthermometer", "ntc",
                   "heissleiter", "ptc", "kaltleiter", "thermoelement", "typ k", "vergleichsstelle",
                   "kaltstelle", "2-leiter", "3-leiter", "4-leiter", "selbsterwärmung", "callendar", "b-wert",
                   "iec 60751", "genauigkeitsklasse", "klasse a", "klasse b"],

    "steckbrief": {
        "zeilen": [
            ("Pt100 / Pt1000", "Platin, 100 Ω / 1000 Ω bei 0 °C, ca. +0.385 %/K, sehr genau und linear"),
            ("NTC (Heissleiter)", "wärmer → Widerstand SINKT, sehr empfindlich (ca. −3 … −5 %/K), stark nichtlinear, günstig"),
            ("PTC (Kaltleiter)", "wärmer → Widerstand STEIGT (oft sprunghaft) – eher für Schutz als zum Messen"),
            ("Thermoelement", "zwei Metalle erzeugen eine Spannung (µV/K) – für sehr hohe Temperaturen, misst nur Differenzen"),
            ("Halbleitersensor", "IC mit linearer Spannung oder digitalem Ausgang – einfach, begrenzter Bereich"),
        ],
    },

    "erklaerung": """
## Widerstandsthermometer (Pt100 / Pt1000)
Der Widerstand von Platin steigt fast **linear** mit der Temperatur: Pt100 hat bei 0 °C genau 100 Ω und ändert sich um ca. **0.385 Ω pro Kelvin**. Er ist **genau, stabil und genormt** (IEC 60751) – der Standard in der Industrie und Prozessmesstechnik.
- **Leitungswiderstand:** Bei 2-Leiter-Schaltung wird der Widerstand der Zuleitungen mitgemessen. 0.5 Ω pro Ader ergibt beim Pt100 schon rund **2.6 K** Fehler! Abhilfe: **3-Leiter** (kompensiert) oder **4-Leiter** (misst die Spannung stromlos direkt am Sensor).
- **Selbsterwärmung:** Der Messstrom erwärmt den Sensor. Deshalb klein halten (typisch ca. 1 mA bei Pt100).
- **Pt1000** hat 10× mehr Widerstand → der Leitungswiderstand wirkt 10× weniger, beliebt bei 2-Leiter-Schaltungen.
## NTC (Heissleiter)
Halbleiterkeramik, deren Widerstand mit steigender Temperatur **stark sinkt**. Sehr empfindlich und günstig, aber **stark nichtlinear** – deshalb braucht es eine Kennlinie, die B-Wert-Gleichung oder eine Tabelle (Steinhart-Hart). Typisch in Geräten, Akkus, Klimatechnik. Oft mit einem festen Widerstand als **Spannungsteiler** am ADC.
## Thermoelement
Zwei verschiedene Metalle, an einem Ende verbunden: Ist die **Messstelle** wärmer als die **Vergleichsstelle** (die Klemmen), entsteht eine kleine Spannung (Seebeck-Effekt), z.B. Typ K ca. **41 µV/K**. Vorteile: sehr hohe Temperaturen (Typ K bis über 1000 °C), robust, schnell. Nachteile: kleine Signale, **misst nur die Temperaturdifferenz** – die Temperatur der Vergleichsstelle muss separat gemessen und addiert werden (Vergleichsstellenkompensation).
## Welchen Sensor wofür?
- **Genau, Prozess, bis ca. 600 °C:** Pt100 / Pt1000
- **Günstig, Geräte, −40 … 150 °C:** NTC
- **Sehr heiss (Ofen, Abgas):** Thermoelement
- **Auf der Leiterplatte, digital:** Halbleiter-Sensor-IC
## 📚 Vertiefung
Schrüfer, *Elektrische Messtechnik*: Kapitel 3.6 (Widerstandstemperaturfühler: Metall, Heissleiter, Kaltleiter, Fehlermöglichkeiten), Kapitel 2.5 (Thermoelement, Sperrschicht-Temperatursensor).
""",

    "tabellen": [
        {
            "titel": "📊 Pt100 – Widerstandswerte",
            "kopf": ["Temperatur", "−50 °C", "0 °C", "25 °C", "50 °C", "100 °C", "200 °C"],
            "zeilen": [["R (Pt100)", "80.31 Ω", "100.00 Ω", "109.73 Ω", "119.40 Ω", "138.51 Ω", "175.86 Ω"]],
            "hinweis": "Berechnet nach IEC 60751 (Callendar-Van Dusen). Pt1000: Werte × 10.",
        },
        {
            "titel": "📊 Genauigkeitsklassen Pt100 (IEC 60751)",
            "kopf": ["Klasse", "Toleranz", "bei 0 °C", "bei 100 °C"],
            "zeilen": [
                ["AA", "±(0.1 + 0.0017·|T|) °C", "±0.10 K", "±0.27 K"],
                ["A", "±(0.15 + 0.002·|T|) °C", "±0.15 K", "±0.35 K"],
                ["B", "±(0.3 + 0.005·|T|) °C", "±0.30 K", "±0.80 K"],
            ],
        },
        {
            "titel": "📊 Thermoelemente (Richtwerte)",
            "kopf": ["Typ", "Material", "Empfindlichkeit ca.", "Einsatzbereich ca."],
            "zeilen": [
                ["K", "NiCr-Ni", "41 µV/K", "−200 … 1200 °C, am häufigsten"],
                ["J", "Fe-CuNi", "52 µV/K", "−40 … 750 °C"],
                ["T", "Cu-CuNi", "43 µV/K", "−200 … 350 °C"],
                ["N", "NiCrSi-NiSi", "27–39 µV/K", "bis 1200 °C, stabiler als K"],
                ["S", "PtRh10-Pt", "6–10 µV/K", "bis 1600 °C, Labor/Referenz"],
            ],
            "hinweis": "Empfindlichkeit ist nicht konstant – genaue Werte aus den Grundwerttabellen (IEC 60584).",
        },
    ],

    "tipps": [
        "**2-Leiter nur bei kurzen Leitungen** oder mit Pt1000. Sonst 3- oder 4-Leiter-Schaltung.",
        "**Thermoelement-Verlängerung** nur mit passender Ausgleichsleitung – normale Kupferkabel erzeugen neue, falsche Thermospannungen an den Übergängen.",
        "**Einbautiefe:** Ein Fühler misst die Temperatur seiner eigenen Spitze. Zu kurz eingetaucht → Wärme fliesst über das Schutzrohr ab und der Wert ist falsch.",
        "**Ansprechzeit:** Dicke Schutzrohre machen den Sensor träge (Zeitkonstante von Sekunden bis Minuten).",
        "**NTC am ADC:** Den Festwiderstand im Spannungsteiler etwa gleich gross wie den NTC-Wert in der Mitte des Messbereichs wählen – dann ist die Empfindlichkeit am grössten.",
        "**Sensor prüfen:** Pt100 bei Raumtemperatur ≈ 108–110 Ω. Unendlich = Unterbruch, 0 Ω = Kurzschluss.",
    ],
    "fehler": [
        "2-Leiter-Pt100 mit langer Leitung → mehrere Kelvin zu warm.",
        "Thermoelement ohne Vergleichsstellenkompensation → gemessen wird nur die Differenz zur Klemmentemperatur.",
        "NTC mit einer linearen Formel umgerechnet.",
        "Zu grosser Messstrom → Pt100 erwärmt sich selbst.",
    ],
    "siehe_auch": ["bruecke_dms", "ad_wandler", "messunsicherheit"],

    "rechner": ["pt100", "ntc", "thermoelement"],
}
