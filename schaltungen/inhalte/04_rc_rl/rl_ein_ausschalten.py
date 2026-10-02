# Seite "RL-Glied ein- und ausschalten"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Lernansicht "rl_kurve" (bauteile/grafiken/kurven.py) und Schaltplan "schaltung_freilauf"
# (schaltungen/grafiken_dioden.py) gibt es schon - hier nur wiederverwendet.

THEMA = {
    "titel": "RL-Glied ein- und ausschalten, Freilaufpfad",
    "reihenfolge": 40,
    "kurz": "Der Strom in einer Spule kann nicht springen – beim Einschalten steigt er langsam, beim Ausschalten braucht er einen Weg.",
    "stichworte": ["RL-Glied", "Einschaltvorgang", "Ausschaltvorgang", "Zeitkonstante", "L/R", "Freilaufpfad",
                   "Abschaltspannung", "Induktionsspannung", "Gegenspannung", "Freilaufdiode", "Z-Diode"],

    "grafiken": ["rl_kurve", "schaltung_freilauf"],

    "erklaerung": """
## Funktion
Die Spule wehrt sich gegen jede Stromänderung: `u_L = L · di/dt`.
- **Einschalten**: Zuerst liegt die ganze Spannung an der Spule, der Strom steigt mit `τ = L / R` an: `i(t) = U / R · (1 − e^(−t/τ))`.
- **Ausschalten**: Der Strom will weiterfliessen. Die Spulenspannung kehrt ihre Polarität um und wird so gross, wie nötig ist, damit er einen Weg findet: `u_L = −R_Pfad · i`.
- Gespeicherte Energie `W = ½ · L · I²` muss im Ausschaltpfad in Wärme umgesetzt werden.

Der **Freilaufpfad** entscheidet, wie hoch die Spannung wird und wie schnell der Strom verschwindet:
- ohne Pfad: Spannung riesig (Funke, Transistor-Durchbruch)
- Freilaufdiode: nur ≈ 0.7 V Gegenspannung, Strom klingt langsam mit L / R_Spule ab
- Diode + Z-Diode (oder Widerstand): Gegenspannung U_Z + 0.7 V – Strom ist schneller weg, Schalter muss U_B + U_Z aushalten

## Dimensionierung
1. τ_ein = L / R (R = Drahtwiderstand + Vorwiderstand); nach 5 τ ist der Endstrom U / R erreicht.
2. Freilaufdiode: I_F ≥ Spulenstrom, U_RRM ≥ U_B; bei PWM schnelle Diode (Schottky).
3. Schnelles Abschalten (Relais, Ventile): Z-Diode in Reihe. Abfallzeit ≈ `τ · ln(1 + I · R / U_Gegen)`, Schalter muss `U_B + U_Z + 0.7 V` sperren.
4. Energie pro Abschaltung ½ · L · I² mal Schaltfrequenz = Verlustleistung im Freilaufpfad.

## Betriebszustände
- **Einschalten**: u_L springt auf U, i steigt exponentiell.
- **Eingeschwungen**: u_L = 0, i = U / R (nur Drahtwiderstand begrenzt).
- **Ausschalten ohne Pfad**: Spannungsspitze (Hunderte Volt), sehr schneller Abfall – zerstört Transistoren.
- **Ausschalten mit Freilauf**: Strom kreist in Spule und Diode, klingt mit L / R_Spule ab – Relais fällt verzögert ab.

## Messpunkte
- **M1** (Kollektor/Drain des Schalters) mit dem Oszilloskop beim Abschalten: Spitze = U_B + U_Gegen. Tastkopf 10:1 und ausreichende Spannungsfestigkeit verwenden!
- Spulenstrom mit Stromzange oder Shunt: Einschalten = e-Funktion, Ausschalten mit Diode = langsamer Abfall.
- τ bestimmen: Zeit bis 63 % des Endstroms.

## Grenzfälle
- R → 0 (Supraleiter, sehr dicke Wicklung): Strom steigt linear `di/dt = U / L` – begrenzt nur durch die Quelle.
- Eisenkern in Sättigung: L bricht ein, Strom steigt plötzlich steil an (Trafo-Einschaltstromstoss).
- Ohne Freilaufpfad an mechanischem Kontakt: Abrissfunke – Kontaktabbrand, Störungen (EMV).
""",

    "tipps": [
        "Freilaufdiode immer direkt an die Spule, nicht an den Transistor – kurze Wege, kleine Schleife.",
        "Relais fallen mit reiner Freilaufdiode spürbar später ab (ms) – mit Z-Diode in Reihe deutlich schneller.",
    ],
    "fehler": [
        "Freilaufdiode falsch herum: Sie schliesst die Versorgung kurz, sobald der Transistor einschaltet.",
        "Die Abschaltspannung an einem Transistor ohne Freilaufpfad unterschätzt – er stirbt beim ersten Schalten.",
        "τ = L / R mit R der Quelle allein gerechnet – der Drahtwiderstand der Spule gehört dazu.",
    ],
    "siehe_auch": ["freilaufdiode", "rc_laden_entladen", "lasten_ansteuern"],
    "rechner": ["rl_zeit", "rl_kurve", "abschaltspitze", "freilauf"],
}
