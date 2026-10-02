# Seite "Addierer"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Addierer (Summierverstärker)",
    "reihenfolge": 20,
    "kurz": "Invertierender Verstärker mit mehreren Eingängen – addiert gewichtete Spannungen, ohne dass sie sich stören.",
    "stichworte": ["Addierer", "Summierer", "Summierverstärker", "Mischpult", "gewichtete Summe", "virtuelle Masse",
                   "Offset addieren", "Pegelverschiebung", "D/A-Wandler"],

    "grafiken": ["schaltung_addierer"],

    "erklaerung": """
## Funktion
Der invertierende Verstärker bekommt mehrere Eingangswiderstände, die alle am − Eingang (virtuelle Masse, 0 V) zusammentreffen:
- Jeder Eingang liefert `I_k = U_k / R_k` – unabhängig von den anderen, weil der Knoten auf 0 V festgehalten wird.
- Kein Strom in den OPV → alle Ströme fliessen durch R_f: `Ua = −R_f · (U1/R1 + U2/R2 + …)`
- Gleiche Widerstände: `Ua = −(U1 + U2 + …)`; verschiedene: gewichtete Summe mit Gewicht `−R_f / R_k`.

## Dimensionierung
1. R_f und die Gewichte festlegen: `R_k = R_f / |Gewicht_k|`.
2. Die Summe muss in die Aussteuerung passen: grösste mögliche Eingänge einsetzen und |Ua| ≤ U_B − 1.5 V prüfen.
3. Eingangswiderstand jedes Eingangs = R_k → die Quellen müssen diesen Strom liefern können.
4. Soll das Ergebnis positiv sein: einen invertierenden Verstärker mit Vu = −1 nachschalten (oder einen Differenzverstärker).
5. Gleichspannung addieren (Pegel verschieben): einen Eingang an eine feste Referenz legen, z.B. Wechselsignal + 1.65 V für einen 3.3-V-ADC.

## Betriebszustände
- **Normal**: Ua = −R_f · ΣI, jeder Eingang lässt sich einzeln ändern, ohne die anderen zu beeinflussen.
- **Eingang offen**: liefert keinen Strom → zählt einfach nicht mit.
- **Begrenzt**: Summe grösser als die Aussteuerung – Ausgang klebt an der Grenze, alle Signale werden verzerrt.

## Messpunkte
- **M1** (Summenknoten, − Eingang): muss ≈ 0 V sein. Liegt hier eine Spannung, ist der Ausgang übersteuert.
- Einzelne Ströme: Spannung an R_k messen, `I = U_R / R_k`.
- Mit dem Oszilloskop: Ausgang = invertierte Summe, z.B. Rechteck + Sinus.

## Grenzfälle
- Ein R_k → 0: dieser Eingang bekommt unendliches Gewicht (Kurzschluss gegen virtuelle Masse, Quelle wird überlastet).
- Sehr viele Eingänge: Die Rauschverstärkung `1 + R_f / (R1 ∥ R2 ∥ …)` steigt → Bandbreite sinkt (f_g = GBW / Rauschverstärkung).
- R-2R-Netzwerk mit Schaltern an den Eingängen: wird zum D/A-Wandler (gewichtete Summe von Bits).
""",

    "tipps": [
        "Ein Audiomischpult ist im Kern ein Addierer – jeder Kanal-Fader verändert sein Gewicht.",
        "Nichtinvertierend addieren geht auch (Widerstände am + Eingang), dann beeinflussen sich die Eingänge aber gegenseitig.",
    ],
    "fehler": [
        "Vorzeichen vergessen – der Addierer invertiert.",
        "Summe aller grössten Eingänge nicht geprüft – der Ausgang geht bei Spitzen in die Begrenzung.",
        "Quellen mit Innenwiderstand: R_i addiert sich zu R_k und verfälscht das Gewicht.",
    ],
    "siehe_auch": ["opv_verstaerker", "differenz_instrumentenverstaerker"],
    "rechner": ["opv_addierer", "opv_verstaerker"],
}
