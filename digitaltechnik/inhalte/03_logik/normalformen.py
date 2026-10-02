# Seite "Normalformen"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Normalformen: DNF und KNF",
    "reihenfolge": 30,
    "kurz": "Aus jeder Wahrheitstabelle direkt eine Formel ablesen – als ODER von Mintermen (DNF) oder UND von Maxtermen (KNF).",
    "stichworte": ["Normalform", "DNF", "KNF", "disjunktive Normalform", "konjunktive Normalform", "Minterm",
                   "Maxterm", "Summe von Produkten", "SOP", "POS", "kanonisch", "Σm", "Πm"],

    "grafiken": ["werkzeug_ausdruck"],

    "erklaerung": """
## Grundlagen
- **Minterm**: UND-Verknüpfung ALLER Variablen (negiert oder nicht), die genau in EINER Zeile der Tabelle 1 ist. Die Zeilennummer (Belegung als Binärzahl) ist die Minterm-Nummer: Zeile 5 = `101` → `A·¬B·C`.
- **Maxterm**: ODER-Verknüpfung aller Variablen, die genau in EINER Zeile 0 ist: Zeile 5 → `(¬A + B + ¬C)`.
- **DNF** (disjunktive Normalform, Summe von Produkten): ODER aller Minterme der 1-Zeilen. Kurzschrift: `Y = Σm(1, 3, 6, 7)`.
- **KNF** (konjunktive Normalform, Produkt von Summen): UND aller Maxterme der 0-Zeilen. Kurzschrift: `Y = Πm(0, 2, 4, 5)`.
- Beide kanonischen Formen sind eindeutig und gleichwertig – aber meist nicht minimal.

## Vorgehen
DNF aus der Tabelle:
1. Alle Zeilen mit Y = 1 suchen.
2. Für jede: UND aller Variablen, Variable = 0 wird negiert.
3. Alle diese Terme mit ODER verbinden.

KNF aus der Tabelle:
1. Alle Zeilen mit Y = 0 suchen.
2. Für jede: ODER aller Variablen, Variable = 1 wird negiert (umgekehrt wie bei der DNF!).
3. Alle Klauseln mit UND verbinden.

Wahl: weniger Einsen → DNF kürzer, weniger Nullen → KNF kürzer. Danach minimieren (KV-Diagramm).

## Beispiel
Tabelle mit Y = 1 in den Zeilen 1, 3, 6, 7 (Variablen A, B, C):
- DNF: `¬A·¬B·C + ¬A·B·C + A·B·¬C + A·B·C`
- zusammengefasst: `¬A·C·(¬B + B) + A·B·(¬C + C)` = `¬A·C + A·B`
- KNF aus den Nullen 0, 2, 4, 5: `(A + B + C)·(A + ¬B + C)·(¬A + B + C)·(¬A + B + ¬C)`, minimal `(A + C)·(¬A + B)`

## Praxis
- DNF passt zu AND-OR-Schaltungen (bzw. NAND-NAND), KNF zu OR-AND (bzw. NOR-NOR).
- Programmierbare Logik (PAL/GAL, CPLD) ist intern genau eine Summe von Produkten.
- In VHDL/Verilog schreibt man die Funktion direkt hin – das Synthesewerkzeug minimiert selbst. Für Prüfungen und Fehlersuche muss man es trotzdem können.
""",

    "tipps": [
        "Merkhilfe: DNF ← Einsen, KNF ← Nullen; bei der KNF werden die Literale „verkehrt herum“ negiert.",
    ],
    "fehler": [
        "Bei der KNF die Variablen wie bei der DNF negiert – richtig: Variable = 1 → negiert.",
        "Minterm-Nummer mit vertauschter Bitreihenfolge gebildet (A ist das höchstwertige Bit).",
        "Kanonische Form als Ergebnis abgegeben, obwohl nach der minimalen gefragt war.",
    ],
    "siehe_auch": ["kv_diagramme", "boolesche_algebra", "logikgatter"],
    "rechner": ["wahrheitstabelle", "kv_minimieren"],
}
