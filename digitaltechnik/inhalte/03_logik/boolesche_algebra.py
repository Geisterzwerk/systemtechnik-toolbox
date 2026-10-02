# Seite "Boolesche Algebra"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Boolesche Algebra und De Morgan",
    "reihenfolge": 20,
    "kurz": "Rechenregeln für 0 und 1: Ausdrücke umformen und vereinfachen – und mit De Morgan zwischen UND und ODER wechseln.",
    "stichworte": ["boolesche Algebra", "Schaltalgebra", "De Morgan", "Absorption", "Distributivgesetz",
                   "Assoziativgesetz", "Kommutativgesetz", "Vereinfachen", "Umformen", "Negation", "Idempotenz",
                   "Komplement"],

    "grafiken": ["werkzeug_ausdruck"],

    "erklaerung": """
## Grundlagen
Schreibweise in der Toolbox: `¬A` (NICHT), `A·B` (UND), `A + B` (ODER), `A ⊕ B` (XOR). Rangfolge: NICHT vor UND vor ODER.

Regeln mit einer Variable:
- `A·0 = 0`, `A·1 = A`, `A + 0 = A`, `A + 1 = 1`
- `A·A = A`, `A + A = A` (Idempotenz)
- `A·¬A = 0`, `A + ¬A = 1` (Komplement)
- `¬¬A = A` (doppelte Negation)

Regeln mit mehreren Variablen:
- Kommutativ: `A·B = B·A`; Assoziativ: `(A·B)·C = A·(B·C)`
- Distributiv: `A·(B + C) = A·B + A·C` **und** `A + B·C = (A + B)·(A + C)` (gilt nur in der booleschen Algebra!)
- Absorption: `A + A·B = A`, `A·(A + B) = A`, `A + ¬A·B = A + B`
- **De Morgan**: `¬(A·B) = ¬A + ¬B` und `¬(A + B) = ¬A·¬B` – Strich teilen, Operator tauschen.

## Vorgehen
1. Ausdruck aufschreiben, Klammern setzen, wo die Rangfolge unklar ist.
2. Negationen über Klammern mit De Morgan nach innen ziehen.
3. Ausmultiplizieren (Distributivgesetz), dann gleiche Terme zusammenfassen (Idempotenz), `A + ¬A` = 1 ausnutzen, Absorption anwenden.
4. Ergebnis mit dem Rechner „Zwei Ausdrücke vergleichen“ prüfen – eine einzige falsche Belegung reicht als Gegenbeispiel.

## Beispiel
`Y = A·B + A·¬B + ¬A·B`
- `A·B + A·¬B = A·(B + ¬B) = A·1 = A`
- `Y = A + ¬A·B = A + B` (Absorption) → statt 3 AND + 1 OR nur ein OR.

De Morgan:
- `¬(A + B·C) = ¬A·¬(B·C) = ¬A·(¬B + ¬C)`

## Praxis
- De Morgan erklärt, warum ein NAND mit negierten Eingängen ein OR ist – wichtig, wenn nur NAND-Bausteine vorhanden sind.
- Aktiv-LOW-Signale (z.B. `¬CS`, `¬RESET`): „Chip aktiv, wenn ¬CS1 ODER ¬CS2 LOW“ lässt sich mit De Morgan als AND der High-aktiven Signale schreiben.
- In Programmen (if-Bedingungen) gilt dasselbe: `!(a && b) == (!a || !b)`.
""",

    "tipps": [
        "De Morgan merken: „Strich bricht, Zeichen wechselt“.",
        "Bei Unsicherheit lieber eine Wahrheitstabelle machen als lange umformen – mit 3 Variablen sind es nur 8 Zeilen.",
    ],
    "fehler": [
        "¬(A·B) = ¬A·¬B gerechnet – bei De Morgan muss das Zeichen wechseln (¬A + ¬B).",
        "AB + C als A·(B + C) gelesen – UND bindet stärker als ODER.",
        "Gewohnte Algebra übertragen: A + A = 2A gibt es nicht, in der booleschen Algebra ist A + A = A.",
    ],
    "siehe_auch": ["logikgatter", "normalformen", "kv_diagramme"],
    "rechner": ["ausdruck_vergleichen", "wahrheitstabelle"],
}
