# Seite "MOSFET-Gate-Treiber"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Gate-Ladung allein: Rechner "mosfet_gate" (bauteile/rechner/transistor_rechner.py).

THEMA = {
    "titel": "MOSFET-Gate-Treiber",
    "reihenfolge": 40,
    "kurz": "Schnell schalten heisst: viel Gate-Strom. Miller-Plateau, Gate-Widerstand, µC-Pin vs. Treiber-IC, Bootstrap für High-Side.",
    "stichworte": ["Gate-Treiber", "Gatetreiber", "Gate Driver", "Miller-Plateau", "Miller-Effekt", "Gate-Ladung",
                   "Qg", "Qgd", "Gatewiderstand", "Schaltverluste", "Bootstrap", "High-Side", "TC4420", "IR2110",
                   "Logic-Level-MOSFET", "PWM"],

    "grafiken": ["schaltung_gate_treiber"],

    "erklaerung": """
## Funktion
Das Gate eines MOSFET ist ein Kondensator. Zum Einschalten muss die **Gate-Ladung Q_g** hineingeschoben werden – je mehr Strom, desto schneller.
Der Verlauf von u_GS hat drei Teile:
1. u_GS steigt bis zum **Miller-Plateau** U_pl (≈ 3 … 6 V, Datenblatt: „Gate Charge“-Kurve). Noch fliesst kaum Drainstrom.
2. **Plateau**: u_GS bleibt stehen, die Ladung Q_gd lädt die Gate-Drain-Kapazität um, u_DS fällt. Hier liegen Spannung und Strom gleichzeitig am MOSFET → **Schaltverlust**. Dauer: `t = Q_gd · R_G / (U_Tr − U_pl)`.
3. u_GS steigt weiter bis U_Tr, R_DS(on) wird minimal.

Ein µC-Pin liefert ca. 20 mA und 3.3 V – bei Standard-MOSFETs liegt das sogar unter dem Plateau. Ein **Gate-Treiber-IC** liefert 1 … 10 A und 10 … 15 V.

## Dimensionierung
1. Treiberspannung deutlich über dem Plateau: Standard-MOSFET 10 … 12 V, Logic-Level-MOSFET ab 4.5 V (3.3 V nur bei Typen, die R_DS(on) bei 2.5 V angeben).
2. Gate-Widerstand R_G (einige Ω): begrenzt den Spitzenstrom `U_Tr / R_G` und dämpft Schwingungen; kleiner = schneller, aber mehr Störungen.
3. Schaltzeit und Verlust: `t ≈ Q_gd · R_G / (U_Tr − U_pl)`, `P_S ≈ U_DS · I_D · t · f` (Rechner „MOSFET: Schaltzeit und Schaltverlust“).
4. Treiberleistung: `P = Q_g · U_Tr · f` (Rechner „MOSFET: Gate-Ansteuerung“).
5. **High-Side** (Source nicht an Masse): Die Gate-Spannung muss über U_B liegen → Bootstrap-Schaltung (Diode + Kondensator, `C ≥ 2 · Q_g / ΔU`) oder isolierter Treiber.
6. Pull-down (10 … 100 kΩ) Gate–Source: hält den MOSFET aus, solange der µC noch startet.

## Betriebszustände
- **Aus**: u_GS = 0, Gate über Pull-down entladen.
- **Umschalten**: Plateau-Phase – kurz halten!
- **Ein**: u_GS = U_Tr, R_DS(on) laut Datenblatt bei dieser Spannung.
- **Ausschalten**: dieselben drei Phasen rückwärts, das Plateau mit `(U_pl − 0) / R_G` Strom – oft langsamer als das Einschalten.

## Messpunkte
- **u_GS** am Gate (Tastkopf mit kurzer Masse direkt an der Source): Plateau sichtbar?
- **u_DS** gleichzeitig: Flankendauer = Plateaudauer.
- Überschwinger und Klingeln an u_GS → R_G vergrössern oder Leiterbahnen kürzer machen.

## Grenzfälle
- Treiberspannung unter dem Plateau: MOSFET bleibt halb leitend und überhitzt.
- Sehr kleines R_G und lange Gate-Leitung: Schwingungen, im schlimmsten Fall ungewolltes Einschalten.
- Miller-Effekt beim Abschalten der Gegenseite (Halbbrücke): u_DS-Sprung koppelt über C_gd ins Gate → kurzzeitiges Einschalten. Abhilfe: niederohmiger Pull-down im Treiber, negative Gate-Spannung.
""",

    "tipps": [
        "Faustregel: Gate-Strom ≈ Q_g / gewünschte Schaltzeit – für 50 ns bei 70 nC also 1.4 A.",
        "Im Datenblatt nicht nur U_GS(th) ansehen: R_DS(on) ist nur bei der angegebenen U_GS (z.B. 10 V oder 4.5 V) garantiert.",
    ],
    "fehler": [
        "MOSFET mit U_GS(th) = 2 … 4 V direkt am 3.3-V-µC-Pin – er schaltet nie ganz ein und wird heiss.",
        "Kein Pull-down am Gate – beim Einschalten der Versorgung „schwebt“ das Gate und der MOSFET leitet kurz.",
        "Gate-Treiber weit weg vom MOSFET – die Leitungsinduktivität verlangsamt die Flanken und verursacht Schwingungen.",
    ],
    "siehe_auch": ["mosfet_schalter", "h_bruecke_motor", "lasten_ansteuern", "schaltregler_buck_boost"],
    "rechner": ["gate_schaltzeit", "mosfet_gate", "bootstrap"],
}
