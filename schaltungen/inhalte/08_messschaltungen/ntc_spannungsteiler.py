# Seite "NTC im Spannungsteiler"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# R(T) des NTC allein: Rechner "ntc" (messtechnik/rechner.py).

THEMA = {
    "titel": "NTC im Spannungsteiler vor dem ADC",
    "reihenfolge": 20,
    "kurz": "Heissleiter + Festwiderstand: einfache, empfindliche Temperaturmessung – mit dem richtigen R_fix auch fast linear.",
    "stichworte": ["NTC", "Heissleiter", "Thermistor", "Spannungsteiler", "Linearisierung", "B-Wert", "R25",
                   "ratiometrisch", "ADC", "Temperatursensor", "Steinhart-Hart", "Akkutemperatur"],

    "grafiken": ["schaltung_ntc_teiler"],

    "erklaerung": """
## Funktion
Ein NTC wird mit steigender Temperatur stark niederohmiger: `R(T) = R25 · e^(B · (1/T − 1/298.15 K))` (T in Kelvin). Ein 10-kΩ-NTC mit B = 3950 hat bei 0 °C etwa 34 kΩ, bei 100 °C nur noch 700 Ω.
Mit einem Festwiderstand R_fix entsteht ein Spannungsteiler:
- NTC unten (gegen GND): `U = U_B · R_NTC / (R_fix + R_NTC)` – fällt mit steigender Temperatur
- NTC oben: `U = U_B · R_fix / (R_fix + R_NTC)` – steigt mit steigender Temperatur

Die Kennlinie ist ein **S**: am steilsten und fast gerade dort, wo `R_NTC ≈ R_fix`. An den Rändern wird sie flach – dort bringt ein Kelvin nur noch wenige ADC-Stufen.

## Dimensionierung
1. Messbereich T1 … T2 festlegen.
2. R_fix für beste Linearität: `R_fix = (R1·R2 + R2·R3 − 2·R1·R3) / (R1 + R3 − 2·R2)` mit R1, R2, R3 = R_NTC bei T1, Bereichsmitte und T2 (Rechner „NTC-Spannungsteiler auslegen“). Einfacher Richtwert: R_fix ≈ R_NTC in der Bereichsmitte.
3. Teiler aus derselben Spannung speisen wie die ADC-Referenz (**ratiometrisch**) – dann spielt die genaue Versorgungsspannung keine Rolle.
4. Eigenerwärmung prüfen: `P = I² · R_NTC` deutlich unter Datenblatt-Angabe (Verlustkoeffizient, z.B. 1.5 mW/K) halten – lieber grössere Widerstände.
5. Kondensator (z.B. 100 nF) parallel zum ADC-Eingang: filtert Störungen und liefert die Ladung für den Abtastkondensator.
6. In der Software: aus der ADC-Zahl R_NTC berechnen, dann mit der B-Gleichung (oder Steinhart-Hart, Tabelle) die Temperatur.

## Betriebszustände
- **Mitte des Bereichs**: grösste Empfindlichkeit (z.B. 30 mV/K, 38 ADC-Stufen/K bei 12 Bit).
- **Ränder**: geringe Empfindlichkeit, Auflösung schlechter als 0.1 K möglich.
- **Fühlerbruch**: NTC unten → U = U_B; NTC oben → U = 0 – als Fehler auswerten.
- **Kurzschluss**: NTC unten → U = 0; NTC oben → U = U_B.

## Messpunkte
- **M1** (Teilermitte) mit dem Multimeter gegen die erwartete Spannung aus der Grafik prüfen.
- NTC bei bekannter Temperatur (Eiswasser 0 °C, Raum) messen und gegen das Datenblatt vergleichen.
- Querstrom (U_B / (R_fix + R_NTC)) für die Eigenerwärmung abschätzen.

## Grenzfälle
- B-Wert-Gleichung ist eine Näherung: ausserhalb ca. 0 … 100 °C einige Kelvin Fehler → Steinhart-Hart oder Herstellertabelle.
- R_fix viel kleiner als R_NTC im ganzen Bereich: Spannung klebt am oberen Rand, kaum Auflösung.
- Hochohmiger Teiler ohne Kondensator am ADC: Abtastfehler (siehe „ADC-Eingang“).
- Sehr hohe Temperaturen: NTC wird so niederohmig, dass der Strom ihn selbst aufheizt.
""",

    "tipps": [
        "Schnellwahl: R_fix = R25 ergibt die beste Empfindlichkeit um 25 °C.",
        "Fühlerbruch und Kurzschluss lassen sich an Spannungen nahe 0 V oder U_B erkennen – in der Software abfragen.",
    ],
    "fehler": [
        "Teiler aus 5 V gespeist, ADC-Referenz aber 3.3 V (oder intern) – nicht ratiometrisch, Fehler bei jeder Versorgungsschwankung.",
        "Mit der linearen Formel gerechnet – der NTC ist stark nichtlinear.",
        "Kleine Widerstände (z.B. 1 kΩ) gewählt – merkliche Eigenerwärmung und unnötiger Stromverbrauch.",
    ],
    "siehe_auch": ["spannungsteiler", "pt100_leiterschaltung", "adc_eingang_beschaltung"],
    "rechner": ["ntc_teiler", "ntc", "adc"],
}
