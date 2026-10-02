# Seite "Pt100 in 2-, 3- und 4-Leiter-Schaltung"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Kennlinie und Umrechnung: Rechner "pt100" (messtechnik/rechner.py) - hier geht es um die Beschaltung.

THEMA = {
    "titel": "Pt100 / Pt1000 in 2-, 3- und 4-Leiter-Schaltung",
    "reihenfolge": 10,
    "kurz": "Konstantstrom durch den Sensor, Spannung messen – und dabei Leitungswiderstand und Eigenerwärmung im Griff behalten.",
    "stichworte": ["Pt100", "Pt1000", "RTD", "Widerstandsthermometer", "2-Leiter", "3-Leiter", "4-Leiter",
                   "Zweileiter", "Dreileiter", "Vierleiter", "Leitungswiderstand", "Eigenerwärmung", "Messstrom",
                   "Konstantstromquelle", "MAX31865", "Kelvin-Messung"],

    "grafiken": ["schaltung_pt_leitung"],

    "erklaerung": """
## Funktion
Ein Pt100 hat bei 0 °C genau 100 Ω und ändert sich um etwa **0.385 Ω/K** (Pt1000: 3.85 Ω/K). Man schickt einen kleinen, konstanten Strom I hindurch und misst die Spannung: `R = U / I`.
Das Problem: Auch die Zuleitung hat Widerstand – 20 m Kupfer mit 0.25 mm² sind schon 1.4 Ω je Ader.
- **2-Leiter**: Strom und Messung über dieselben Adern → gemessen wird `R_T + 2 · R_L`. Beim Pt100 sind 2 × 1.4 Ω gleich **+7.4 K** Fehler.
- **3-Leiter**: Eine dritte, stromlose Ader erlaubt eine zweite Messung. Daraus wird ein Leitungswiderstand abgezogen: `R = U1/I − U2/I`. Fehlerfrei, solange die Adern gleich sind.
- **4-Leiter** (Kelvin-Messung): Zwei Adern führen den Strom, zwei andere messen die Spannung direkt am Sensor. Durch die Messadern fliesst kein Strom → kein Spannungsabfall, **kein Leitungsfehler**.

Zusätzlich heizt der Messstrom den Sensor: `P = I² · R`, Erwärmung `ΔT = P · k` (k aus dem Datenblatt in K/mW, abhängig vom Einbau).

## Dimensionierung
1. Schaltung nach Leitungslänge und Genauigkeit wählen: 2-Leiter nur bei kurzen Leitungen oder Pt1000, Industrie meist 3-Leiter, Labor/Kalibrierung 4-Leiter.
2. Leitungswiderstand abschätzen: `R_L = 0.0178 Ω·mm²/m · l / A` (Kupfer) → Rechner „Pt100/Pt1000: Leitungsfehler“.
3. Messstrom: Pt100 typisch 0.5 … 1 mA, Pt1000 0.1 … 0.3 mA – genug Signal, aber Eigenerwärmung deutlich unter der geforderten Genauigkeit.
4. Spannung: Pt100 bei 1 mA → 100 … 140 mV (0 … 100 °C), also 0.385 mV/K – ein ADC mit kleiner Referenz oder Verstärkung ist nötig.
5. Ratiometrisch messen: Referenzwiderstand im selben Stromkreis (z.B. MAX31865) – dann kürzt sich die Genauigkeit der Stromquelle heraus.

## Betriebszustände
- **Normalbetrieb**: U steigt linear mit der Temperatur (genauer: Callendar-Van-Dusen-Gleichung, Rechner „Pt100 / Pt1000“).
- **Lange Leitung, 2-Leiter**: Anzeige konstant zu hoch, umso mehr, je länger die Leitung und je wärmer sie ist.
- **3-Leiter mit ungleichen Adern** (Klemme oxidiert, unterschiedliche Länge): Restfehler = Unterschied der Adern.
- **Leitungsbruch**: Strom wird null bzw. Spannung geht an den Anschlag der Quelle → gute Auswerter melden „Sensorfehler“.
- **Kurzschluss**: R ≈ 0 → Anzeige weit unter −200 °C.

## Messpunkte
- Sensor abklemmen und mit dem Multimeter messen (bei 20 °C ≈ 107.8 Ω für Pt100).
- Leitungswiderstand: am fernen Ende kurzschliessen, Schleife messen, halbieren.
- 4-Leiter-Ohmmeter (Kelvin-Klemmen) für genaue Sensorwerte verwenden.
- Eigenerwärmung prüfen: Messstrom halbieren – ändert sich die Anzeige, ist der Strom zu gross.

## Grenzfälle
- Sehr hohe Temperaturen: Isolationswiderstand der Leitung sinkt und liegt parallel zum Sensor → Anzeige zu tief.
- Pt1000 statt Pt100 erkannt (oder umgekehrt): Anzeige völlig falsch (z.B. 1000 Ω als Pt100 = 2000 °C).
- Thermospannungen an Steckern mit verschiedenen Metallen → bei sehr kleinen Messströmen Strom umpolen und mitteln.
- Störungen auf langen Leitungen: verdrillte und geschirmte Leitung, Filter vor dem ADC.
""",

    "tipps": [
        "Pt1000 statt Pt100 verkleinert den Leitungsfehler um den Faktor 10 – oft reicht dann die 2-Leiter-Schaltung.",
        "Der 3-Leiter-Abgleich funktioniert nur mit gleichen Adern: gleiche Länge, gleicher Querschnitt, gleiche Klemmen.",
        "Klasse B (IEC 60751): ±(0.3 K + 0.005 · |T|) – bei 100 °C also ±0.8 K. Mehr Genauigkeit braucht auch eine bessere Schaltung.",
    ],
    "fehler": [
        "2-Leiter-Schaltung mit langer Leitung – der Leitungswiderstand wird als Temperatur angezeigt.",
        "Bei 3-Leiter-Anschluss die Adern vertauscht – die Kompensation wirkt in die falsche Richtung (doppelter Fehler).",
        "Messstrom zu gross gewählt (z.B. 10 mA beim Pt100) – der Sensor heizt sich selbst um mehrere Kelvin auf.",
    ],
    "siehe_auch": ["ntc_spannungsteiler", "dms_messverstaerker", "konstantstromquelle", "geregelte_stromquelle"],
    "rechner": ["pt_leitung", "pt100"],
}
