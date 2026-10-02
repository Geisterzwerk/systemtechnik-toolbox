# Seite "Schaltregler Buck / Boost"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Schaltregler: Buck (abwärts) und Boost (aufwärts)",
    "reihenfolge": 70,
    "kurz": "Schalter, Spule, Diode, Kondensator: Spannung wandeln mit 85 … 95 % Wirkungsgrad statt sie zu verheizen.",
    "stichworte": ["Schaltregler", "Schaltnetzteil", "DC-DC-Wandler", "Buck", "Boost", "Abwärtswandler",
                   "Aufwärtswandler", "Tiefsetzsteller", "Hochsetzsteller", "Tastgrad", "Duty Cycle", "PWM",
                   "Rippelstrom", "CCM", "DCM", "Lückbetrieb", "LM2596", "MT3608"],

    "grafiken": ["schaltung_schaltregler"],

    "erklaerung": """
## Funktion
Ein MOSFET schaltet mit f = 50 kHz … 2 MHz ein und aus. Die Spule speichert in jeder Periode Energie und gibt sie wieder ab (`u_L = L · di/dt`), der Kondensator glättet. Weil der Schalter entweder ganz ein (kaum Spannung) oder ganz aus (kein Strom) ist, entstehen fast keine Verluste.
- Tastgrad `D = t_ein / T`.
- **Buck** (Schalter in der Längsleitung, Diode nach GND, Spule zum Ausgang): `U_a = D · U_e`.
  - EIN: Strom steigt mit `(U_e − U_a) / L`.
  - AUS: Die Spule treibt den Strom über die Freilaufdiode weiter, er fällt mit `U_a / L`.
- **Boost** (Spule in der Längsleitung, Schalter nach GND, Diode zum Ausgang): `U_a = U_e / (1 − D)`.
  - EIN: Die Spule lädt sich gegen GND auf.
  - AUS: Ihre Spannung addiert sich zu U_e und lädt den Ausgang.
- Im Gleichgewicht ist die mittlere Spulenspannung 0 (Volt-Sekunden-Gleichgewicht) – daraus folgen beide Formeln.

## Dimensionierung
1. Tastgrad: Buck `D = U_a / U_e`, Boost `D = 1 − U_e / U_a` (real etwas grösser wegen Verlusten).
2. Spulenstrom: Buck `I_L = I_a`, Boost `I_L = I_a / (1 − D)`.
3. Rippelstrom ΔI ≈ 20 … 40 % von I_L wählen:
   - Buck: `L = (U_e − U_a) · D / (f · ΔI)`
   - Boost: `L = U_e · D / (f · ΔI)`
4. Spitzenstrom `I_L + ΔI / 2` → Sättigungsstrom der Spule, Strombelastbarkeit von Schalter und Diode.
5. Ausgangskondensator (Keramik, kleiner ESR):
   - Buck: `ΔU ≈ ΔI / (8 · f · C)`
   - Boost: `ΔU ≈ I_a · D / (f · C)` (der Ausgang bekommt Strompulse!)
6. Diode: Schottky (schnell, kleine U_F) oder Synchrongleichrichtung mit zweitem MOSFET. Layout: Schleife Schalter–Diode–C_ein so klein wie möglich.

## Betriebszustände
- **CCM** (Dauerbetrieb): Spulenstrom fliesst immer, Formeln gelten.
- **DCM** (Lückbetrieb, kleine Last oder kleine Spule): Strom wird jede Periode 0 – U_a hängt dann von der Last ab, der Regler verkleinert D. Am Schaltknoten klingelt es.
- **Anlauf**: Softstart begrenzt den Einschaltstrom in den leeren Ausgangskondensator.
- **Boost ohne Last**: Ohne Regelung steigt U_a immer weiter – Überspannung! (Regler-IC begrenzt).

## Messpunkte
- **SW** (Schaltknoten) mit dem Oszilloskop: Rechteck mit Tastgrad D, Überschwinger an den Flanken (Masse-Feder des Tastkopfs verwenden, nicht die lange Krokoklemme).
- Spulenstrom mit Stromzange: Dreieck um I_L, Lücken = DCM, Spitzen abgerundet = Spule in Sättigung.
- Ausgangswelligkeit mit AC-Kopplung und 20-MHz-Bandbreitenbegrenzung.

## Grenzfälle
- D → 1 beim Boost: U_a → ∞ in der Formel – praktisch begrenzen Verluste auf ≈ 5 … 10 × U_e.
- Spule zu klein: grosser Rippel, DCM, hohe Spitzenströme; Spule in Sättigung: L bricht ein, Strom schiesst hoch → Schalter stirbt.
- Buck kann nicht aufwärts, Boost nicht abwärts – für beides: Buck-Boost, SEPIC oder Inverter.
""",

    "tipps": [
        "In der Praxis: fertiger Regler-IC (LM2596, MP1584, TPS5430 / MT3608) – Datenblatt-Layout genau nachbauen.",
        "Wirkungsgrad grob: Buck 12 V → 5 V ≈ 90 %, ein Linearregler schafft hier nur 42 %.",
        "Schaltregler stören (EMV) – Eingangsfilter, kurze Schleifen und geschirmte Spulen helfen.",
    ],
    "fehler": [
        "Spule nur nach Induktivität gekauft – der Sättigungsstrom war zu klein.",
        "Elko mit grossem ESR als Ausgangskondensator – die Welligkeit ist viel grösser als berechnet.",
        "Lange Leitungen im Schaltkreis (Schalter–Diode–Eingangskondensator) – Spannungsspitzen und Störungen.",
    ],
    "siehe_auch": ["linearregler", "freilaufdiode", "rl_ein_ausschalten"],
    "rechner": ["schaltregler", "mosfet_verlust", "diode_verlust"],
}
