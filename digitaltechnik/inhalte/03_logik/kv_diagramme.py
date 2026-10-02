# Seite "KV-Diagramme"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "KV-Diagramme: Logik grafisch minimieren",
    "reihenfolge": 40,
    "kurz": "Karnaugh-Veitch-Diagramm: Einsen zu möglichst grossen Blöcken zusammenfassen – ergibt die minimale Schaltung.",
    "stichworte": ["KV-Diagramm", "Karnaugh", "Veitch", "Minimieren", "Vereinfachen", "Block", "Päckchen",
                   "don't care", "Quine-McCluskey", "Primimplikant", "Gray-Code", "minimale DNF"],

    "grafiken": ["werkzeug_kv"],

    "erklaerung": """
## Grundlagen
Das KV-Diagramm ist die Wahrheitstabelle als Rechteck. Zeilen und Spalten sind im **Gray-Code** beschriftet (00, 01, 11, 10), deshalb unterscheiden sich benachbarte Felder in genau einer Variable – auch über den Rand (oben ↔ unten, links ↔ rechts, die vier Ecken).
- Zwei benachbarte Einsen: `X·A + X·¬A = X` → eine Variable fällt weg.
- Block aus `2^k` Feldern → k Variablen fallen weg.
- **don't care** (X): Belegungen, die nie vorkommen (z.B. BCD 10 … 15) – dürfen als 1 oder 0 genutzt werden.

## Vorgehen
1. Tabelle ins Diagramm übertragen (Minterm-Nummern beachten – Gray-Reihenfolge!).
2. Blöcke bilden: nur Rechtecke aus 1, 2, 4, 8 … Feldern, so **gross** wie möglich, so **wenige** wie möglich. Überlappen ist erlaubt, Rand-Nachbarschaft nutzen.
3. Jede 1 muss in mindestens einem Block liegen; X nur mitnehmen, wenn der Block dadurch grösser wird.
4. Je Block den Term ablesen: Variablen, die im Block konstant sind, bleiben (1 → normal, 0 → negiert), wechselnde fallen weg.
5. Terme mit ODER verbinden = minimale DNF. Für die minimale KNF dasselbe mit den Nullen und De Morgan.

## Beispiel
4 Variablen, Einsen bei 0, 1, 2, 3, 8, 10:
- Block 1: obere Zeile (A = 0, B = 0, Minterme 0 … 3) → `¬A·¬B`
- Block 2: die vier Ecken-Spalten mit B = 0 und D = 0 (Minterme 0, 2, 8, 10) → `¬B·¬D`
- `Y = ¬A·¬B + ¬B·¬D` statt 6 Minterme mit je 4 Variablen.

Mit don't cares (BCD-Erkennung „Ziffer ≥ 5“, Eingänge 10 … 15 kommen nie vor): Die X-Felder machen die Blöcke grösser und den Term kürzer.

## Praxis
- KV-Diagramme lohnen sich bis 4 (höchstens 5) Variablen; darüber rechnet man mit dem Quine-McCluskey-Verfahren (macht der Rechner) oder überlässt es dem Synthesewerkzeug.
- Minimal heisst wenige Gatter und Eingänge – aber nicht immer am schnellsten oder störungsfrei: Bei Übergängen zwischen zwei Blöcken kann ein kurzer Glitch (Hazard) entstehen, ein zusätzlicher überdeckender Block verhindert ihn.
""",

    "tipps": [
        "Zuerst die Einsen suchen, die nur in EINEN möglichen Block passen – diese Blöcke sind sicher nötig (essentiell).",
        "Die vier Ecken eines 4×4-Diagramms sind Nachbarn – ein Block, den man leicht übersieht.",
    ],
    "fehler": [
        "Blöcke aus 3 oder 6 Feldern gebildet – erlaubt sind nur 1, 2, 4, 8, 16.",
        "Spalten in Binärreihenfolge (00, 01, 10, 11) statt Gray-Reihenfolge beschriftet – Nachbarschaften stimmen nicht.",
        "Zu kleine Blöcke gewählt, obwohl ein grösserer möglich war – das Ergebnis ist richtig, aber nicht minimal.",
    ],
    "siehe_auch": ["normalformen", "boolesche_algebra"],
    "rechner": ["kv_minimieren", "wahrheitstabelle"],
}
