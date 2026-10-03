# Seite "VCO"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Grundschaltung ohne Steuereingang: "rechteck_dreieck_generator".

THEMA = {
    "titel": "VCO – spannungsgesteuerter Oszillator",
    "reihenfolge": 50,
    "kurz": "Eine Spannung stellt die Frequenz ein: f = K · U_st. Grundbaustein von PLL, Synthesizer und Spannungs-Frequenz-Wandler.",
    "stichworte": ["VCO", "Voltage Controlled Oscillator", "spannungsgesteuerter Oszillator", "PLL", "Steilheit",
                   "Spannungs-Frequenz-Wandler", "U/f-Wandler", "Frequenzmodulation", "FM", "CD4046", "Synthesizer"],

    "grafiken": ["schaltung_vco"],

    "erklaerung": """
## Funktion
Ein VCO erzeugt eine Schwingung, deren Frequenz von einer **Steuerspannung U_st** abhängt. Das einfachste Prinzip baut auf dem Rechteck-/Dreieckgenerator auf:
- Ein **Integrator** integriert die Steuerspannung: Das Dreieck steigt bzw. fällt mit der Steigung `U_st / (R · C)`.
- Ein **Schmitt-Trigger** erkennt die Schwellen `±U_sat · R1 / R2` und schaltet über einen **Umschalter** das Vorzeichen von U_st um.
- Doppelte Steuerspannung → doppelt steiles Dreieck → Schwellen doppelt so schnell erreicht → **doppelte Frequenz**.

`f = K · U_st` mit der **Steilheit** `K = R2 / (4 · R1 · R · C · U_sat)` in Hz/V.

Andere VCO-Arten: LC-Oszillator mit Kapazitätsdiode (Funk, hohe Frequenzen), Ringoszillator (in ICs), VCO im CD4046 (PLL-Baustein) oder NE555 mit Spannung an Pin 5.

## Dimensionierung
1. Frequenzbereich und Steuerspannungsbereich festlegen → Steilheit `K = Δf / ΔU_st`.
2. Dreieck-Amplitude über R1/R2 wählen (z.B. 10 kΩ / 20 kΩ → U_sat/2).
3. R wählen (10 … 100 kΩ), dann `C = R2 / (4 · R1 · R · U_sat · K)` (Rechner „VCO“).
4. Umschalter: Analogschalter (z.B. CD4053) oder ein invertierender Verstärker mit Transistor/FET, gesteuert vom Rechteck.
5. Für Linearität: OPV mit kleinem Offset (sonst läuft der Integrator bei kleinen U_st weg), Kondensator C0G/Folie.

## Betriebszustände
- **U_st klein**: niedrige Frequenz, lange Rampen.
- **U_st gross**: hohe Frequenz bis zur Grenze durch Slew-Rate und Schaltzeiten.
- **U_st = 0**: Integrator steht – keine Schwingung (in der Praxis driftet er wegen Offset langsam).
- **In einer PLL**: Der Phasenvergleicher regelt U_st so, dass die VCO-Frequenz exakt einer Referenz (mal Teiler) folgt.

## Messpunkte
- Rechteck und Dreieck am Oszilloskop, Frequenzzähler am Rechteck.
- Kennlinie aufnehmen: U_st in Schritten erhöhen, f notieren → Gerade? Steigung = K.
- Dreieck-Amplitude bei verschiedenen U_st: muss konstant bleiben.

## Grenzfälle
- Sehr kleine U_st: Offsetspannungen des OPV werden vergleichbar – die Kennlinie knickt bei kleinen Frequenzen ab.
- Sehr grosse U_st: Slew-Rate und Umschaltzeiten begrenzen – die Kennlinie flacht oben ab.
- Negative U_st (bei diesem Prinzip): kehrt nur die Richtung um, die Frequenz hängt vom Betrag ab.
""",

    "tipps": [
        "Die PLL im Mikrocontroller (z.B. 8 MHz Quarz → 72 MHz Takt) enthält genau so einen VCO.",
        "Ein U/f-Wandler (Spannung → Frequenz) überträgt Messwerte störfest über lange Leitungen oder Optokoppler.",
    ],
    "fehler": [
        "Elko als Integrationskondensator verwendet – Leckstrom und Verpolung verfälschen die Kennlinie.",
        "OPV-Offset nicht beachtet – bei kleinen Steuerspannungen stimmt die Frequenz nicht.",
    ],
    "siehe_auch": ["rechteck_dreieck_generator", "ne555_timer", "integrator_differenzierer"],
    "rechner": ["vco", "funktionsgenerator"],
}
