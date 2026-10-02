# Seite "Spannungsteiler" (unbelastet und belastet)  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Spannungsteiler (unbelastet & belastet)",
    "reihenfolge": 10,
    "kurz": "Zwei Widerstände in Reihe teilen eine Spannung – mit Last sinkt die Ausgangsspannung.",
    "stichworte": ["Spannungsteiler", "belasteter Spannungsteiler", "Querstrom", "Querstromverhältnis",
                   "voltage divider", "Teilerverhältnis", "Belastung"],

    "grafiken": ["schaltung_spannungsteiler"],

    "erklaerung": """
## Funktion
R1 und R2 liegen in Reihe, durch beide fliesst derselbe Strom `I = Ue / (R1 + R2)`. Nach der Maschenregel teilt sich Ue im Verhältnis der Widerstände auf:
- `Ua = Ue · R2 / (R1 + R2)`   (unbelastet, Ua liegt an R2)
- `U_R1 / U_R2 = R1 / R2`      (grösserer Widerstand = grössere Teilspannung)

Wird am Ausgang eine Last R_L angeschlossen, liegt sie **parallel zu R2**. Der untere Widerstand wird kleiner (`R2 || R_L`), Ua sinkt:
- `Ua = Ue · (R2 || R_L) / (R1 + R2 || R_L)`   mit `R2 || R_L = R2 · R_L / (R2 + R_L)`

## Dimensionierung
1. Teilerverhältnis festlegen: `R2 / (R1 + R2) = Ua / Ue`
2. Querstrom wählen: Für eine stabile Ausgangsspannung soll der Strom durch R2 mindestens **10 × grösser** als der Laststrom sein (Querstromverhältnis `q = I2 / I_L ≥ 10`).
3. Daraus `R1 + R2 = Ue / I_quer`, dann R1 und R2 aufteilen und auf **E-Reihe** runden (Rechner E-Reihe).
4. Verlustleistung prüfen: `P = I² · R` je Widerstand, mit Reserve (Faktor 2).

Beispiel: 12 V → 5 V an einem ADC-Eingang (R_L ≈ 1 MΩ). Mit R1 = 14 kΩ, R2 = 10 kΩ fliessen 0.5 mA Querstrom, der Laststrom ist nur 5 µA (q = 100) → Ua bleibt bei 5 V.

## Betriebszustände
- **Leerlauf** (keine Last): Ua = Ua,0, grösster Wert.
- **Belastet**: Ua sinkt. Bei `R_L = R2` und R1 = R2 fällt Ua von Ue/2 auf Ue/3 (−33 %).
- **Kurzschluss am Ausgang** (R_L = 0): Ua = 0, der Strom wird nur noch von R1 begrenzt (`I = Ue / R1`) – R1 muss das aushalten.

## Messpunkte
- **M1** (Mittelpunkt) gegen GND: Ua. Mit Multimeter (Ri ≈ 10 MΩ) messen – bei Teilern mit MΩ-Widerständen belastet sogar das Messgerät merklich (siehe Messtechnik → Multimeter, Belastungsfehler).
- Ue direkt an der Quelle messen, nicht am Teiler.
- Querstrom ohne Auftrennen bestimmen: Spannung an R1 messen und durch R1 teilen.

## Grenzfälle
- `R2 → 0`: Ua → 0.   `R2 → ∞` (Unterbrechung): Ua → Ue.
- `R1 → 0`: Ua = Ue – der Teiler ist überbrückt.
- `R_L ≫ R2`: Last spielt keine Rolle.   `R_L ≪ R2`: Ua wird fast nur noch von R1 und R_L bestimmt.
- Ein Spannungsteiler ist **keine Spannungsversorgung**: Für Lasten mit wechselndem Strom braucht es einen Spannungsregler oder einen Spannungsfolger (OPV).
""",

    "tipps": [
        "Faustregel: Querstrom ≥ 10 × Laststrom. Ein OPV-Spannungsfolger hinter dem Teiler macht die Last praktisch unendlich gross.",
        "Für ADC-Eingänge: Teiler nicht zu hochohmig (Datenblatt: max. Quellwiderstand, oft ≤ 10 kΩ) oder einen kleinen Kondensator an den ADC-Pin.",
        "Batteriegeräte: Teiler zur Spannungsmessung über einen Transistor/MOSFET nur bei Bedarf einschalten – sonst entlädt der Querstrom die Batterie dauernd.",
    ],
    "fehler": [
        "Teiler als Netzteil missbraucht (z.B. 12 V → 5 V für einen Motor oder µC) – Ua bricht unter Last zusammen.",
        "R1 und R2 vertauscht: Ua = Ue · R2 / (R1 + R2) – R2 ist der Widerstand, an dem Ua abgegriffen wird.",
        "Belastung durch das Messgerät oder den ADC vergessen – bei MΩ-Teilern stimmt die Messung dann nicht.",
        "Verlustleistung nicht geprüft: Bei 230 V oder kleinen Widerständen werden 0.25-W-Widerstände schnell zu heiss (auch Spannungsfestigkeit beachten!).",
    ],
    "siehe_auch": ["potentiometer", "wheatstone_bruecke", "stromteiler"],
    "rechner": ["spannungsteiler", "e_reihe", "ohm_leistung"],
}
