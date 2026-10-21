# Seite "Synchrone Zähler entwerfen"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py
# Das KV-Werkzeug "werkzeug_kv" (digitaltechnik/grafiken_logik.py) wird wiederverwendet.

THEMA = {
    "titel": "Synchrone Zähler und Zustandsautomaten entwerfen",
    "reihenfolge": 40,
    "kurz": "Von der gewünschten Zustandsfolge zur Schaltung: Folgetabelle, Ansteuergleichungen für D- oder JK-Flipflops, KV-Minimierung.",
    "stichworte": ["Zählerentwurf", "synchroner Zähler", "Zustandsautomat", "Automat", "Moore", "Mealy",
                   "Zustandsfolgetabelle", "Ansteuertabelle", "Ansteuergleichung", "Übergangstabelle",
                   "Selbststart", "Lock-up", "BCD-Zähler", "Gray-Zähler", "FSM"],

    "grafiken": ["werkzeug_kv"],

    "erklaerung": """
## Stell dir vor …
Eine **Verkehrsampel** kennt nur wenige Zustände: Rot, Rot-Gelb, Grün, Gelb. Bei jedem Takt (Zeitablauf oder Taster) wechselt sie nach einer festen Regel in den nächsten Zustand. Einen Zähler oder Automaten zu entwerfen heisst: diese Zustände aufschreiben, die Regeln festlegen und daraus die Logik für die Flipflops ableiten.
## Grundlagen
Ein synchrones Schaltwerk = **Zustandsregister** (n D-Flipflops am gemeinsamen Takt) + **Übergangslogik** (Schaltnetz, das aus dem aktuellen Zustand und den Eingängen den nächsten Zustand berechnet) + ggf. **Ausgangslogik**.
- **Moore-Automat**: Ausgänge hängen nur vom Zustand ab.
- **Mealy-Automat**: Ausgänge hängen auch direkt von den Eingängen ab.

Ein Zähler ist ein Automat ohne Eingänge.
- **D-Flipflop**: Die Ansteuerung ist einfach der Folgezustand, `D_i = Q_i⁺`.
- **JK-Flipflop**: Die Ansteuertabelle zeigt, was nötig ist, damit Q von Q nach Q⁺ wechselt:
  - 0 → 0: J = 0, K = X
  - 0 → 1: J = 1, K = X
  - 1 → 0: J = X, K = 1
  - 1 → 1: J = X, K = 0

## Vorgehen
1. Zustände und Folge festlegen, binär codieren (Anzahl Flipflops `n = ⌈log2 m⌉`).
2. **Zustandsfolgetabelle**: Q (jetzt) → Q⁺ (nach dem Takt), letzter Zustand → erster.
3. Unbenutzte Zustände als **don't care** eintragen.
4. Je Flipflop die Ansteuerfunktion (D_i bzw. J_i, K_i) als KV-Diagramm aufstellen und minimieren.
5. **Selbststart prüfen**: Landen die unbenutzten Zustände mit den fertigen Gleichungen wieder in der Folge? Sonst kann der Zähler nach einer Störung hängen bleiben (Lock-up) → don't cares gezielt festlegen.
6. Schaltung zeichnen, f_max prüfen.

## Beispiel
BCD-Zähler 0 … 9 mit D-Flipflops (Q3 … Q0), unbenutzt 10 … 15:
- `D0 = ¬Q0`
- `D1 = ¬Q3·¬Q1·Q0 + Q1·¬Q0`
- `D2 = Q2·¬Q1 + Q2·¬Q0 + ¬Q2·Q1·Q0`
- `D3 = Q3·¬Q0 + Q2·Q1·Q0`
- Selbststart: 10 → 11 → 4, 14 → 15 → 8 … alle finden zurück.

Mit JK-Flipflops wird es kürzer: `J3 = Q2·Q1·Q0, K3 = Q0, J1 = ¬Q3·Q0, K1 = Q0, J0 = K0 = 1`.

Gray-Zähler 0, 1, 3, 2: `D1 = Q0`, `D0 = ¬Q1` – nur zwei Leitungen, keine Gatter.

## Praxis
- In VHDL/Verilog schreibt man den Automaten als `case`-Anweisung, das Synthesewerkzeug erzeugt Register und Logik – das Prinzip (Zustand, Übergang, Ausgang) bleibt gleich.
- Typische Automaten: Ampelsteuerung, Sequenzerkennung (z.B. „101“ im Bitstrom), Protokolle (UART-Empfänger), Tastenentprellung mit Zustandsautomat.
- Der KV-Rechner unten hilft beim Minimieren jeder einzelnen Ansteuerfunktion.
## 🔬 Genauer hingeschaut
- **Unbenutzte Zustände abfangen:** Ein Zähler mit 3 Flipflops hat 8 mögliche Zustände. Nutzt er nur 6, müssen auch die 2 übrigen in den normalen Ablauf zurückführen. Sonst kann er nach einer Störung oder beim Einschalten in einer Schleife hängen bleiben.
- **One-Hot-Codierung:** Statt die Zustände binär zu nummerieren, bekommt jeder Zustand sein eigenes Flipflop – immer genau eines ist 1. Das braucht mehr Flipflops, aber weniger Logik und ist in FPGAs oft schneller.
- **Moore oder Mealy?** Mealy-Ausgänge reagieren sofort auf Eingänge, können aber kurze Störimpulse weitergeben. Moore-Ausgänge ändern sich nur mit dem Takt – sauberer, dafür einen Takt später.
## 💡 Wusstest du?
- Ein **Getränkeautomat** ist ein klassisches Beispiel für einen Automaten: Die Zustände sind „0 Fr. eingeworfen“, „1 Fr.“, „2 Fr.“ …, die Eingänge sind Münzen und Tasten, und die Ausgänge sind „Getränk ausgeben“ und „Rückgeld“.
""",

    "tipps": [
        "Mit JK-Flipflops gibt es mehr don't cares – die Gleichungen werden meist kürzer als mit D-Flipflops.",
        "Für störarme Ausgänge die Zustände so codieren, dass sich bei jedem Übergang nur ein Bit ändert (Gray).",
    ],
    "fehler": [
        "Rückkehr vom letzten zum ersten Zustand in der Tabelle vergessen.",
        "Bei JK-Flipflops die Ansteuertabelle mit der Wahrheitstabelle verwechselt.",
        "Selbststart nicht geprüft – nach dem Einschalten bleibt der Zähler in einem unbenutzten Zustand hängen.",
    ],
    "siehe_auch": ["zaehler", "kv_diagramme", "flipflops"],
    "rechner": ["zaehler_entwurf", "kv_minimieren", "fmax_schaltwerk"],
}
