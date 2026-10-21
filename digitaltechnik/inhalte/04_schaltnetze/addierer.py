# Seite "Addierer"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Halbaddierer, Volladdierer und Addierwerk",
    "reihenfolge": 10,
    "kurz": "Wie Hardware addiert und subtrahiert: Stelle für Stelle mit Übertrag – und warum der Übertrag Zeit kostet.",
    "stichworte": ["Addierer", "Halbaddierer", "Volladdierer", "Ripple Carry", "Carry Lookahead", "Übertrag",
                   "Carry", "Subtrahierer", "ALU", "74HC283", "Laufzeit", "Rechenwerk"],

    "grafiken": ["werkzeug_addierer"],

    "erklaerung": """
## Stell dir vor …
Erinnerst du dich ans **schriftliche Addieren** in der Schule? Du rechnest Stelle für Stelle von rechts nach links, und wird eine Stelle grösser als 9, schreibst du einen kleinen Übertrag zur nächsten Stelle. Ein Addierer macht genau das – nur ist bei Binärzahlen schon 1 + 1 ein Übertrag.
## Grundlagen
- **Halbaddierer** (2 Eingänge A, B): Summe `S = A ⊕ B`, Übertrag `C = A·B`. Er kann keinen Übertrag von der vorigen Stelle aufnehmen.
- **Volladdierer** (A, B, C_ein): `S = A ⊕ B ⊕ C_ein`, `C_aus = A·B + C_ein·(A ⊕ B)` – aus zwei Halbaddierern und einem OR.
- **Ripple-Carry-Addierer** (n Bit): n Volladdierer hintereinander, `C_aus` jeder Stufe geht an `C_ein` der nächsten. Einfach, aber langsam: Der Übertrag muss im schlimmsten Fall durch alle Stufen laufen (`t ≈ n · t_C`).
- **Carry-Lookahead**: berechnet die Überträge parallel aus „Generate“ (A·B) und „Propagate“ (A ⊕ B) – schneller, aber mehr Gatter.
- **Subtraktion**: `A − B = A + ¬B + 1` – B mit XOR invertieren, `C_ein = 1`. Dasselbe Addierwerk rechnet beides (ALU).

## Vorgehen
1. Wahrheitstabelle des Volladdierers aufstellen (8 Zeilen), S und C_aus ablesen.
2. Für n Bit: n Volladdierer verketten, LSB bekommt C_ein = 0 (Addition) bzw. 1 (Subtraktion).
3. Flags auswerten: C = Übertrag aus dem MSB (unsigned), V = C_ein(MSB) ⊕ C_aus(MSB) (signed Overflow).
4. Laufzeit prüfen: Reicht `n · t_C` für die Taktperiode?

## Beispiel
4 Bit, 0110 + 0011 (6 + 3):
- Stelle 0: 0 + 1 + 0 = 1, C = 0
- Stelle 1: 1 + 1 + 0 = 0, C = 1
- Stelle 2: 1 + 0 + 1 = 0, C = 1
- Stelle 3: 0 + 0 + 1 = 1, C = 0
- Ergebnis `1001` = 9 (unsigned richtig), signed: 6 + 3 = −7 → Overflow V = 1 (der Übertrag in Stelle 3 ist 1, aus Stelle 3 heraus 0).

Subtraktion 3 − 5: `0011 + 1010 + 1 = 1110` = −2, C = 0 (geborgt).

## Praxis
- 74HC283: 4-Bit-Volladdierer mit schnellem Übertrag; mehrere kaskadierbar.
- In µC und FPGAs steckt das Addierwerk in der ALU bzw. in speziellen Carry-Ketten – im VHDL/Verilog schreibt man einfach `a + b`.
- 16 Bit Ripple-Carry mit 10 ns pro Stufe: 160 ns → höchstens ≈ 6 MHz Takt; mit Lookahead deutlich schneller.
## 🔬 Genauer hingeschaut
- **Der Übertrag ist der Flaschenhals:** Beim Ripple-Carry-Addierer muss der Übertrag im schlimmsten Fall durch alle Stufen laufen (z.B. 0111…1 + 1). Die Rechenzeit wächst mit der Bitbreite. Carry-Lookahead rechnet die Überträge vorab und wird damit viel schneller – kostet aber mehr Gatter.
- **Flags entstehen gleich mit:** Aus dem Addierwerk fallen Carry (Übertrag aus der letzten Stufe), Overflow (Vorzeichenfehler), Zero (Ergebnis 0) und Negative (MSB) heraus. Prozessoren werten genau diese Flags für Vergleiche und Sprünge aus.
- **Vergleichen heisst subtrahieren:** Ein Prozessor prüft `A < B` meist, indem er `A − B` rechnet und nur die Flags ansieht.
## 💡 Wusstest du?
- 1937 baute George Stibitz in den Bell Labs einen binären Addierer aus Relais auf seinem Küchentisch – das „Model K“, nach dem englischen Wort für Küche (kitchen).
""",

    "tipps": [
        "Der Volladdierer zählt einfach die Einsen seiner drei Eingänge: S = niederwertiges Bit, C_aus = höherwertiges Bit dieser Anzahl.",
    ],
    "fehler": [
        "Bei der Subtraktion nur B invertiert, C_ein = 1 vergessen – das Ergebnis ist um 1 zu klein.",
        "Carry als Overflow gedeutet – bei signed Zahlen zählt V, nicht C.",
        "Laufzeit der Übertragskette vergessen – bei hoher Taktfrequenz wird ein falsches Zwischenergebnis übernommen.",
    ],
    "siehe_auch": ["zweierkomplement_ueberlauf", "logikgatter", "multiplexer"],
    "rechner": ["binaer_addieren", "addierer_laufzeit"],
}
