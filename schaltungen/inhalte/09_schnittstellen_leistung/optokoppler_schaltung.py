# Seite "Optokoppler"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Optokoppler",
    "reihenfolge": 20,
    "kurz": "Signale galvanisch getrennt übertragen – z.B. 24-V-Industriesignal an einen 3.3-V-µC. Entscheidend: CTR und Pull-up.",
    "stichworte": ["Optokoppler", "Optokuppler", "galvanische Trennung", "CTR", "Current Transfer Ratio",
                   "Fototransistor", "PC817", "Isolationsspannung", "24 V Eingang", "SPS-Eingang", "Potentialtrennung"],

    "grafiken": ["schaltung_optokoppler"],

    "erklaerung": """
## Funktion
Eine Infrarot-LED leuchtet auf einen Fototransistor – zwischen Eingang und Ausgang gibt es **keine elektrische Verbindung** (Isolationsspannung typ. 3 … 5 kV). Eingangs- und Ausgangsseite haben getrennte Massen.
- Eingang: `I_F = (U_e − U_F) / R_V` (U_F ≈ 1.2 V)
- Ausgang: Der Fototransistor kann höchstens `I_C = CTR · I_F` liefern (**Current Transfer Ratio**, z.B. PC817: 50 … 600 %).
- Mit Pull-up R_L ist der Ausgang LOW, wenn der Transistor sättigt: `CTR · I_F ≥ (U_B − U_CE,sat) / R_L`. Sonst bleibt der Ausgang in der Mitte – ein undefinierter Pegel.

## Dimensionierung
1. LED-Strom wählen (typ. 2 … 10 mA, Datenblatt-Arbeitspunkt der CTR), `R_V = (U_e − U_F) / I_F`; Leistung im R_V beachten (24 V, 5 mA → 114 mW).
2. CTR-Minimum aus dem Datenblatt und **Alterung** einrechnen (CTR sinkt über die Jahre, mit Faktor 0.5 rechnen).
3. `R_L ≥ (U_B − 0.3 V) / (CTR_min · 0.5 · I_F)` – grösser ist sicherer gesättigt, aber langsamer.
4. Schaltzeit: Grosse R_L und hohe Sättigung → einige 10 µs. Für schnelle Signale (UART, Encoder) Optokoppler mit Logik-Ausgang (z.B. 6N137).
5. Eingangsseite für 24-V-Signale: Verpolschutz-Diode, ggf. Z-Diode oder Teiler, damit unter einer Schwelle (z.B. 5 V) sicher „aus“ erkannt wird.

## Betriebszustände
- **Eingang aus**: I_F = 0 → Transistor sperrt → Ausgang HIGH (Pull-up). Ausgang ist invertiert!
- **Eingang ein, gesättigt**: Ausgang ≈ 0.3 V.
- **Eingang ein, nicht gesättigt**: `U_aus = U_B − CTR · I_F · R_L` – irgendwo dazwischen.
- **Eingangsspannung verpolt**: LED sperrt (maximal ca. 6 V Sperrspannung!) → antiparallele Diode vorsehen.

## Messpunkte
- **M1** (Ausgang): LOW sicher < 0.4 V? HIGH = U_B?
- LED-Strom über die Spannung an R_V bestimmen.
- Mit Rechtecksignal am Eingang die Verzögerung und die Flanken am Ausgang messen.

## Grenzfälle
- Kleine Eingangsspannung (z.B. 12 V statt 24 V): I_F halbiert sich → evtl. keine Sättigung mehr.
- Hohe Temperatur: CTR sinkt.
- Störungen zwischen den Massen (schnelle Spannungssprünge): koppeln über die Koppelkapazität (≈ 1 pF) durch → Typen mit hoher CMTI.
""",

    "tipps": [
        "Ausgang ist invertiert (LED an → Ausgang LOW) – in der Software beachten oder Transistor als Emitterfolger beschalten.",
        "Für viele Eingänge gibt es Mehrfach-Optokoppler (z.B. 4 Kanäle in einem Gehäuse).",
    ],
    "fehler": [
        "Mit der typischen statt der minimalen CTR gerechnet – bei einem Teil der Bauteile sättigt der Ausgang nicht.",
        "Pull-up zu klein gewählt (z.B. 330 Ω) – der Fototransistor kann den Strom nicht ziehen.",
        "Eingangs- und Ausgangsmasse doch verbunden – die galvanische Trennung ist damit wirkungslos.",
    ],
    "siehe_auch": ["pegelwandler_schaltung", "transistorschalter", "eingangsschutz"],
    "rechner": ["optokoppler", "led_vorwiderstand"],
}
