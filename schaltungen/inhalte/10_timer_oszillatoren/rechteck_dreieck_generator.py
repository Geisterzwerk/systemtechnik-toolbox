# Seite "Rechteck-/Dreieckgenerator"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Bausteine: Schmitt-Trigger ("komparator_schmitt_trigger") und Integrator ("integrator_differenzierer") aus 05_opv.

THEMA = {
    "titel": "Rechteck-/Dreieckgenerator (Funktionsgenerator)",
    "reihenfolge": 30,
    "kurz": "Schmitt-Trigger und Integrator im Kreis: Rechteck und Dreieck gleichzeitig, Frequenz und Amplitude getrennt einstellbar.",
    "stichworte": ["Funktionsgenerator", "Dreieckgenerator", "Rechteckgenerator", "Relaxationsoszillator",
                   "Schmitt-Trigger", "Integrator", "Dreieck", "Rechteck", "VCO", "Sägezahn"],

    "grafiken": ["schaltung_funktionsgenerator"],

    "erklaerung": """
## Funktion
Zwei bekannte OPV-Schaltungen im Kreis:
- **OPV1: nichtinvertierender Schmitt-Trigger** – sein Ausgang ist +U_sat oder −U_sat (Rechteck).
- **OPV2: Integrator** – integriert das Rechteck: Bei konstantem Eingang läuft sein Ausgang linear mit der Steigung `U_sat / (R · C)` (Dreieck).
- Das Dreieck führt über R1 zurück zum Schmitt-Trigger. Erreicht es die Schwelle `±U_sat · R1 / R2`, kippt das Rechteck, und der Integrator läuft in die Gegenrichtung.

Ergebnis:
- Dreieck-Amplitude `û_D = U_sat · R1 / R2`
- Frequenz `f = R2 / (4 · R1 · R · C)`

## Dimensionierung
1. Dreieck-Amplitude über R1/R2 festlegen (R1 < R2, z.B. 10 kΩ / 20 kΩ → halbe Rechteckamplitude).
2. Frequenz über R und C: `C = R2 / (4 · R1 · R · f)` (Rechner „Rechteck-/Dreieckgenerator“).
3. Frequenz mit einem Poti statt R einstellbar (Bereichsumschaltung über verschiedene C).
4. OPV: Slew-Rate muss die Rechteckflanken schaffen (`SR ≫ 2 · U_sat · f`), Ausgänge Rail-to-Rail für definierte U_sat.
5. Für genaue, symmetrische Amplituden: Z-Dioden am Schmitt-Ausgang begrenzen statt U_sat zu nutzen.

## Betriebszustände
- **Rechteck +U_sat**: Integrator-Ausgang fällt linear (invertierender Integrator).
- **Dreieck erreicht −û_D**: Schmitt-Trigger kippt auf −U_sat, Dreieck steigt.
- **Einschalten**: Die Schaltung schwingt von selbst an – der Schmitt-Trigger hat keinen stabilen Zwischenzustand.

## Messpunkte
- **M1** (OPV1-Ausgang): Rechteck ±U_sat, Flanken zeigen die Slew-Rate.
- **M2** (OPV2-Ausgang): Dreieck ±û_D, Spitzen exakt an den Schwellen.
- Frequenz: mit dem Oszilloskop; Abweichungen kommen meist von C-Toleranz und U_sat.

## Grenzfälle
- R1 ≥ R2: Das Dreieck erreicht die Schwelle nie – keine Schwingung (Integrator läuft in die Begrenzung).
- Sehr hohe Frequenz: Slew-Rate begrenzt, das Rechteck wird trapezförmig, die Frequenz sinkt.
- U_sat unsymmetrisch (Einzelversorgung, nicht Rail-to-Rail): Dreieck nicht symmetrisch, Tastgrad ≠ 50 %.
- Mit einer Steuerspannung statt U_sat am Integrator wird daraus ein VCO (spannungsgesteuerter Oszillator).
""",

    "tipps": [
        "Frequenz und Amplitude sind unabhängig: R (Poti) ändert nur f, R1/R2 nur die Amplitude.",
        "Aus dem Dreieck wird mit einem Diodennetzwerk ein angenäherter Sinus – so arbeiten einfache Funktionsgeneratoren.",
    ],
    "fehler": [
        "Den Schmitt-Trigger invertierend aufgebaut – die Rückkopplung hat dann das falsche Vorzeichen, nichts schwingt.",
        "Elko als Integrationskondensator – er wird bei jeder Halbwelle verpolt.",
    ],
    "siehe_auch": ["komparator_schmitt_trigger", "integrator_differenzierer", "ne555_timer"],
    "rechner": ["funktionsgenerator", "schmitt_trigger", "integrator"],
}
