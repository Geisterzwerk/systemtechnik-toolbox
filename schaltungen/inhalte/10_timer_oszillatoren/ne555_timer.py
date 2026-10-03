# Seite "NE555"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "NE555: Taktgeber und Monoflop",
    "reihenfolge": 10,
    "kurz": "Der Klassiker: zwei Komparatoren, ein Flipflop, ein Entladetransistor – astabil als Taktgeber, monostabil als Zeitglied.",
    "stichworte": ["NE555", "555", "Timer", "TLC555", "astabil", "monostabil", "Monoflop", "Taktgeber",
                   "Blinker", "Tastgrad", "Duty Cycle", "Impulsdauer", "Zeitglied", "Rechteckgenerator"],

    "grafiken": ["schaltung_ne555"],

    "erklaerung": """
## Funktion
Im NE555 teilen drei gleiche Widerstände die Versorgung in **⅓ U_B** und **⅔ U_B**. Zwei Komparatoren vergleichen damit:
- **Pin 6 (Threshold)** > ⅔ U_B → Flipflop zurücksetzen: Ausgang (Pin 3) LOW, Entladetransistor (Pin 7) leitet
- **Pin 2 (Trigger)** < ⅓ U_B → Flipflop setzen: Ausgang HIGH, Pin 7 sperrt

**Astabil** (Taktgeber): C lädt über R1 + R2 bis ⅔ U_B, dann entlädt Pin 7 ihn über R2 bis ⅓ U_B:
- `t_H = ln2 · (R1 + R2) · C`,  `t_L = ln2 · R2 · C`
- `f = 1.44 / ((R1 + 2 · R2) · C)`, Tastgrad immer > 50 %
- Mit **Diode parallel zu R2** lädt C nur über R1: `t_H = ln2 · R1 · C` → auch < 50 % möglich

**Monostabil** (Monoflop): Ein kurzer LOW-Impuls an Pin 2 startet; C lädt über R von 0 bis ⅔ U_B:
- `t = ln3 · R · C ≈ 1.1 · R · C`

Weil nur **Verhältnisse** von U_B zählen, hängen die Zeiten nicht von der Versorgungsspannung ab.

## Dimensionierung
1. C wählen (Folie oder C0G für genaue Zeiten; Elko nur für lange, ungenaue Zeiten wegen Leckstrom und Toleranz).
2. Astabil: aus f und Tastgrad R1 und R2 berechnen (Rechner „NE555 astabil auslegen“), R1 ≥ 1 kΩ (Strom in Pin 7).
3. Widerstände zwischen 1 kΩ und ca. 1 MΩ (darüber stören Leck- und Eingangsströme).
4. Pin 5 (Control) mit 10 nF an Masse – stabilisiert die Schwellen.
5. Pin 4 (Reset) an U_B, wenn nicht benutzt.
6. Für 3.3 V oder wenig Strom: CMOS-Version (TLC555, ICM7555) – kleinere Stromspitzen und Ruhestrom.

## Betriebszustände
- **Astabil**: u_C pendelt zwischen ⅓ und ⅔ U_B, Ausgang Rechteck.
- **Monostabil, Ruhe**: C entladen, Ausgang LOW.
- **Monostabil, Impuls**: Ausgang HIGH für 1.1 · R · C, neue Trigger werden ignoriert.
- **Reset (Pin 4 LOW)**: Ausgang sofort LOW, unabhängig von allem anderen.

## Messpunkte
- **M1** (Kondensator): Dreieck-ähnliche Ladekurve zwischen ⅓ und ⅔ U_B – sonst stimmen die Schwellen nicht.
- **M2** (Pin 3): Frequenz und Tastgrad mit dem Oszilloskop.
- Pin 5: sollte ⅔ U_B sein.

## Grenzfälle
- R1 sehr klein: Pin 7 muss beim Entladen U_B / R1 aufnehmen → überlastet.
- Sehr grosse R mit Elko: Leckstrom des Elkos verlängert die Zeit massiv (oder sie läuft nie ab).
- Bipolarer NE555 erzeugt beim Umschalten Stromspitzen von über 100 mA → 100 nF direkt an Pin 8.
- Trigger länger als der Impuls (monostabil): Ausgang bleibt so lange HIGH, wie der Trigger anliegt.
""",

    "tipps": [
        "Faustformel astabil: f ≈ 1.44 / ((R1 + 2·R2) · C) – mit R2 ≫ R1 wird der Tastgrad fast 50 %.",
        "Der Ausgang (Pin 3) kann ca. 200 mA treiben – für Relais trotzdem eine Freilaufdiode vorsehen.",
    ],
    "fehler": [
        "Pin 4 (Reset) offen gelassen – der Timer setzt sich zufällig zurück.",
        "Elko für eine genaue Zeit verwendet – Toleranz ±20 % und Leckstrom machen die Zeit unberechenbar.",
        "Für einen Tastgrad unter 50 % die Diode vergessen.",
    ],
    "siehe_auch": ["astabiler_multivibrator", "rechteck_dreieck_generator", "watchdog_schaltung", "rc_laden_entladen"],
    "rechner": ["ne555", "ne555_auslegen"],
}
