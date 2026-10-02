# Seite "Pull-up und Pull-down"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Pull-up und Pull-down",
    "reihenfolge": 30,
    "kurz": "Ein Widerstand gibt einem offenen Digitaleingang einen festen Pegel – Taster, Open Drain, I²C.",
    "stichworte": ["Pull-up", "Pull-down", "Pullup", "Taster", "Eingang", "floating", "schwebend",
                   "Mikrocontroller", "Open Drain", "I2C", "Logikpegel"],

    "grafiken": ["schaltung_pull"],

    "erklaerung": """
## Funktion
Ein CMOS-Eingang ist extrem hochohmig (MΩ … GΩ). Ist er offen, **schwebt** er: Er nimmt Störungen auf und liest zufällig 0 oder 1, oft wechselnd. Ein Widerstand legt ihn auf einen festen Pegel, solange nichts anderes treibt:
- **Pull-up**: R von +U_B zum Eingang, Taster nach GND → offen = HIGH, gedrückt = LOW (aktiv-LOW).
- **Pull-down**: R vom Eingang nach GND, Taster nach +U_B → offen = LOW, gedrückt = HIGH (aktiv-HIGH).

Gedrückt überbrückt der Taster den Eingang hart; durch R fliesst dann `I = U_B / R`.

## Dimensionierung
R hat eine **Untergrenze** und eine **Obergrenze**:
- `R_min = U_B / I_max` – Strom bei gedrücktem Taster (Batterie, Verlustleistung, bei Open Drain: max. Sinkstrom des Ausgangs, z.B. 3 mA bei I²C).
- `R_max = (U_B − U_IH) / I_leck` – der Leckstrom des Eingangs darf den Pegel nicht unter die HIGH-Schwelle ziehen (CMOS: U_IH ≈ 0.7 · U_B).
- `R_max = t_r / (2.2 · C)` – die Leitung und der Pin bilden mit R ein RC-Glied, die Flanke (10 → 90 %) dauert `t_r ≈ 2.2 · R · C`.

Typische Werte: Taster 4.7 … 47 kΩ, I²C 1 … 10 kΩ (je nach Busgeschwindigkeit und Kapazität), interne µC-Pull-ups ca. 20 … 50 kΩ.

## Betriebszustände
- **Taster offen**: Eingang = Pegel des Pull-Widerstands (nur Leckstrom fliesst, wenige µA oder weniger).
- **Taster gedrückt**: Eingang = harter Gegenpegel, Strom `U_B / R` fliesst dauerhaft, solange gedrückt.
- **Prellen**: Mechanische Kontakte prellen 1 … 10 ms – der µC sieht mehrere Flanken (→ Tasterentprellung mit RC oder in Software).

## Messpunkte
- **M1** (Eingang gegen GND) mit Multimeter: offen ≈ U_B (Pull-up), gedrückt ≈ 0 V.
- Mit Oszilloskop die Flanke ansehen: langsamer Anstieg = R zu gross für die Kapazität; mehrere Pulse = Prellen.
- Liegt der Pegel offen zwischen 0.3 und 0.7 · U_B, ist R zu gross oder der Eingang defekt (Leckstrom zu hoch).

## Grenzfälle
- `R → ∞` (vergessen): Eingang schwebt – der klassische „Geister-Tastendruck“.
- `R → 0`: Kurzschluss beim Drücken (U_B direkt auf GND).
- Pull-up UND Pull-down am selben Pin: bilden einen Spannungsteiler, der Pegel liegt im verbotenen Bereich.
- Lange Leitungen (Taster im Gerät, Kabel 1 m+): Störungen koppeln ein → kleineres R, RC-Filter oder Schmitt-Trigger-Eingang.
""",

    "tipps": [
        "Interne Pull-ups des Mikrocontrollers (z.B. INPUT_PULLUP beim Arduino) sparen Bauteile – sind aber schwach (20 … 50 kΩ) und für lange Leitungen oder I²C oft zu hochohmig.",
        "Pull-up mit Taster nach GND ist üblicher als Pull-down: GND liegt überall, und ein Kurzschluss der Leitung nach GND ist harmlos.",
        "Unbenutzte CMOS-Eingänge nie offen lassen – auf festen Pegel legen (direkt oder über Widerstand).",
    ],
    "fehler": [
        "Pull-Widerstand vergessen – der Eingang schwebt und reagiert auf die Hand in der Nähe.",
        "Viel zu kleines R (z.B. 100 Ω) – unnötig 50 mA bei gedrücktem Taster, Batterie leer, Widerstand heiss.",
        "Zu grosses R bei I²C – die steigenden Flanken werden so langsam, dass die Kommunikation ausfällt.",
        "Pegel falsch herum ausgewertet: Bei Pull-up bedeutet „gedrückt“ = LOW (0).",
    ],
    "siehe_auch": ["spannungsteiler"],
    "rechner": ["pull_widerstand", "rc_zeit", "e_reihe"],
}
