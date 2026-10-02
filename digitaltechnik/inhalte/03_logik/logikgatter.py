# Seite "Logikgatter"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Logikgatter und Wahrheitstabellen",
    "reihenfolge": 10,
    "kurz": "AND, OR, NOT, NAND, NOR, XOR, XNOR – Funktion, Symbole (IEC und ANSI), Wahrheitstabelle und typische Bausteine.",
    "stichworte": ["Gatter", "Logikgatter", "AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR", "UND", "ODER",
                   "NICHT", "Antivalenz", "Äquivalenz", "Wahrheitstabelle", "Schaltsymbol", "IEC 60617", "ANSI",
                   "7400", "74HC00", "Inverter"],

    "grafiken": ["werkzeug_gatter"],

    "erklaerung": """
## Grundlagen
Ein Gatter verknüpft binäre Eingänge zu einem Ausgang. Die **Wahrheitstabelle** listet für jede Eingangsbelegung den Ausgang (n Eingänge → `2^n` Zeilen).
- **NOT** (Inverter): `Y = ¬A`
- **AND** (UND): `Y = A·B` – nur 1, wenn alle Eingänge 1 sind
- **OR** (ODER): `Y = A + B` – 1, wenn mindestens ein Eingang 1 ist
- **NAND**: `Y = ¬(A·B)` – 0 nur, wenn alle 1 sind
- **NOR**: `Y = ¬(A + B)` – 1 nur, wenn alle 0 sind
- **XOR** (Antivalenz): `Y = A ⊕ B = A·¬B + ¬A·B` – 1, wenn die Eingänge verschieden sind (bei mehr Eingängen: ungerade Anzahl Einsen)
- **XNOR** (Äquivalenz): `Y = ¬(A ⊕ B)` – 1, wenn die Eingänge gleich sind

**Symbole**: IEC 60617 (in Europa / Schulen): Rechteck mit `&`, `≥1`, `=1`, `1`; Negation = Kreis am Ausgang. ANSI/IEEE (US-Datenblätter): eigene Formen (D-Form, Schild, Dreieck).

## Vorgehen
1. Aufgabe in Worten → Eingänge und Ausgang festlegen (was bedeutet 1?).
2. Wahrheitstabelle aufstellen: alle `2^n` Belegungen in Zählreihenfolge (000, 001, 010 …).
3. Für jede Zeile den gewünschten Ausgang eintragen.
4. Aus der Tabelle die Funktion ablesen (Normalform) und vereinfachen (KV-Diagramm).
5. Mit vorhandenen Gattern aufbauen – oft nur mit NAND (je 4 im 74HC00).

## Beispiel
Alarm: Die Hupe (Y) soll ertönen, wenn die Anlage scharf ist (S = 1) UND eine Tür offen ist (T1 ODER T2):
- `Y = S · (T1 + T2)` → 1 AND + 1 OR
- Wahrheitstabelle: 8 Zeilen, Y = 1 bei S = 1 und mindestens einer offenen Tür (3 Zeilen).

Nur mit NAND:
- NOT: `¬A = A NAND A`
- AND: NAND + NOT
- OR (De Morgan): `A + B = ¬A NAND ¬B`

## Praxis
- 74HC00 (4 × NAND), 74HC02 (4 × NOR), 74HC04 (6 × NOT), 74HC08 (4 × AND), 74HC32 (4 × OR), 74HC86 (4 × XOR); Einzelgatter in SOT-23 (74LVC1G…).
- Unbenutzte Eingänge an GND oder U_B legen, nie offen lassen (CMOS).
- Abblockkondensator 100 nF an jedes IC.
- Laufzeit (t_pd ≈ 5 … 20 ns bei 74HC) summiert sich über mehrere Gatterstufen.
""",

    "tipps": [
        "XOR als steuerbarer Inverter: Y = A ⊕ S – bei S = 0 geht A durch, bei S = 1 wird es invertiert.",
        "NAND und NOR heissen „universell“: Mit nur einem Gattertyp lässt sich jede Funktion bauen.",
    ],
    "fehler": [
        "XOR mit OR verwechselt: Bei A = B = 1 liefert OR 1, XOR aber 0.",
        "Wahrheitstabelle nicht in Zählreihenfolge – Zeilen fehlen oder doppelt.",
        "Unbenutzte CMOS-Eingänge offen gelassen – undefinierter Ausgang und erhöhte Stromaufnahme.",
    ],
    "siehe_auch": ["boolesche_algebra", "normalformen", "logikpegel_stoerabstand"],
    "rechner": ["wahrheitstabelle", "ausdruck_vergleichen"],
}
