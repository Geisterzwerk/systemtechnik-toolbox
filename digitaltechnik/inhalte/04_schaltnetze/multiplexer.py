# Seite "Multiplexer"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Multiplexer und Demultiplexer",
    "reihenfolge": 20,
    "kurz": "Digital gesteuerter Umschalter: einen von n Eingängen durchschalten – oder einen Eingang auf n Ausgänge verteilen.",
    "stichworte": ["Multiplexer", "MUX", "Demultiplexer", "DEMUX", "Datenselektor", "Auswahleingang", "Select",
                   "74HC151", "74HC153", "74HC4051", "Analog-Multiplexer", "Shannon", "Zeitmultiplex"],

    "grafiken": ["werkzeug_mux"],

    "erklaerung": """
## Grundlagen
- **Multiplexer (MUX)** `2^k : 1`: k Auswahleingänge (Select) wählen einen von `2^k` Dateneingängen. 4:1: `Y = ¬S1·¬S0·D0 + ¬S1·S0·D1 + S1·¬S0·D2 + S1·S0·D3`.
- **Demultiplexer (DEMUX)** `1 : 2^k`: ein Eingang wird auf den gewählten Ausgang gelegt, alle anderen sind inaktiv. Ein DEMUX ist im Kern ein Decoder mit Daten-Eingang.
- Anzahl Auswahlleitungen: `k = ⌈log2 n⌉`.
- **Logikfunktion mit MUX** (Shannon-Zerlegung): Mit n Variablen reicht ein `2^(n−1):1`-MUX – n−1 Variablen an die Auswahl, an jeden Dateneingang kommt 0, 1, X oder ¬X.

## Vorgehen
Logikfunktion mit MUX:
1. Variablen festlegen: die ersten k an die Auswahl (S_{k−1} … S0), der Rest bleibt für die Dateneingänge.
2. Wahrheitstabelle in Gruppen teilen: jede Kombination der Auswahlvariablen ist eine Gruppe.
3. In jeder Gruppe die Restfunktion ablesen (bei einer Restvariable X: immer 0 → `0`, immer 1 → `1`, wie X → `X`, umgekehrt → `¬X`).
4. Diese Werte an D0 … D(2^k − 1) anschliessen.

## Beispiel
`Y = A·B + ¬A·C` mit einem 4:1-MUX, Auswahl A, B, Rest C:
- A B = 00 → Y = C → `D0 = C`
- 01 → Y = C → `D1 = C`
- 10 → Y = 0 → `D2 = 0`
- 11 → Y = 1 → `D3 = 1`

## Praxis
- Analog-Multiplexer (74HC4051, CD4051): mehrere Sensoren nacheinander an EINEN ADC-Eingang – Achtung: Durchgangswiderstand (≈ 100 Ω) und Umschaltzeit, nach dem Umschalten kurz warten.
- Zeitmultiplex bei 7-Segment-Anzeigen: Stellen nacheinander einschalten, Segmentleitungen gemeinsam.
- In FPGAs sind LUTs (Lookup-Tables) im Grunde Multiplexer, deren Dateneingänge die Wahrheitstabelle enthalten.
- Bei µC-Pins: „Alternate Function Multiplexer“ wählt, welches Peripheriemodul den Pin benutzt.
""",

    "tipps": [
        "Eine Wahrheitstabelle an die Dateneingänge eines 2^n:1-MUX gelegt – und die Eingänge an die Auswahl: fertig ist jede Funktion mit n Variablen.",
    ],
    "fehler": [
        "Reihenfolge der Auswahlbits vertauscht (S0 ist das niederwertige Bit).",
        "Analog-MUX ohne Wartezeit nach dem Umschalten ausgelesen – der Sample-Kondensator des ADC hängt noch am alten Kanal.",
        "Enable-Eingang (oft aktiv LOW) nicht beschaltet – der Ausgang bleibt inaktiv.",
    ],
    "siehe_auch": ["decoder_encoder", "normalformen", "addierer"],
    "rechner": ["mux_funktion", "wahrheitstabelle"],
}
