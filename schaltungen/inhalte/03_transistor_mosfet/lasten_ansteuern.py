# Seite "LED-, Relais- und Motoransteuerung"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "LED, Relais und Motor ansteuern",
    "reihenfolge": 30,
    "kurz": "Was jede Lastart am Mikrocontroller braucht: Vorwiderstand, Freilaufdiode, Anlaufstrom, Treiber.",
    "stichworte": ["Relaisansteuerung", "LED-Ansteuerung", "Motoransteuerung", "Low-Side-Treiber", "Freilaufdiode",
                   "ULN2003", "Anlaufstrom", "Mikrocontroller", "Treiber"],

    "grafiken": ["schaltung_lasttreiber"],

    "erklaerung": """
## Funktion
Ein µC-Pin liefert nur wenige mA bei 3.3 oder 5 V. Ein Transistor (NPN) oder MOSFET auf der **Low-Side** schaltet die eigentliche Last aus einer eigenen, oft höheren Versorgung. Jede Lastart braucht dazu etwas anderes:
- **LED**: Vorwiderstand begrenzt den Strom, `R_V = (U_B − U_F − U_CE,sat) / I_LED`.
- **Relais** (induktiv): Freilaufdiode antiparallel zur Spule, sonst zerstört die Abschaltspitze den Transistor.
- **DC-Motor** (induktiv + Anlaufstrom): Freilaufdiode, und der Schalter muss den **Anlaufstrom** (blockierter Motor: 3 … 10 × Nennstrom) aushalten. Bei PWM zusätzlich Schaltverluste.

## Dimensionierung
1. Laststrom bestimmen (LED: Datenblatt, Relais: `U_N / R_Spule`, Motor: Nenn- UND Anlaufstrom).
2. Schalter wählen:
   - bis ca. 100 … 300 mA: NPN (z.B. BC337, BC817) mit `I_B = 3 · I_C / B_min`.
   - darüber oder bei PWM: Logic-Level-N-MOSFET (kein Steuerstrom, kleiner Spannungsfall).
   - viele Relais/kleine Lasten: Treiber-IC ULN2003 (7 Darlington-Stufen mit eingebauten Freilaufdioden).
3. Freilaufdiode bei jeder Spule: I_F ≥ Laststrom, U_R ≥ U_B.
4. Gemeinsame Masse von µC und Lastversorgung verbinden, die Laststrom-Masse aber getrennt zur Quelle führen (Sternpunkt).

## Betriebszustände
- **Pin LOW / Reset**: Schalter aus (Pull-down am Gate bzw. Basis-Emitter-Widerstand sorgt dafür).
- **Pin HIGH**: Schalter voll ein, Last an U_B.
- **Abschalten einer Spule**: Freilaufstrom über die Diode, Relais fällt verzögert ab.
- **Motor-Anlauf**: kurzzeitig vielfacher Strom – Versorgung kann einbrechen und den µC zurücksetzen.

## Messpunkte
- **M1** (Kollektor/Drain): EIN ≈ 0.1 … 0.3 V, AUS = U_B; Abschaltspitze mit dem Oszilloskop prüfen.
- Pin-Spannung unter Last: darf nicht deutlich unter den HIGH-Pegel fallen (sonst Pin überlastet).
- U_B am µC beim Motorstart mit dem Oszilloskop (Trigger auf Einbruch): Bricht sie ein → Elko an die Motorversorgung, getrennte Regler.

## Grenzfälle
- Relais ohne Freilaufdiode: Transistor stirbt nach einigen Schaltvorgängen (oder sofort).
- Motor blockiert: Dauernd Anlaufstrom – Transistor und Motor überhitzen → Strombegrenzung oder Sicherung.
- Last direkt am µC-Pin: Nur bei sehr kleinen Strömen (LED mit wenigen mA) zulässig – Summe aller Pins beachten.
""",

    "tipps": [
        "LED direkt am Pin ist ok, wenn I ≤ ca. 10 mA und der Summenstrom des µC eingehalten wird.",
        "Für Motoren in beiden Drehrichtungen braucht es eine H-Brücke (z.B. DRV8833, L298 ist veraltet und verlustreich).",
        "Relais-Module mit Optokoppler trennen Steuer- und Lastseite – praktisch bei 230-V-Lasten.",
    ],
    "fehler": [
        "Transistor nur für den Nennstrom eines Motors ausgelegt – der Anlaufstrom zerstört ihn.",
        "Motor und µC an derselben Versorgung ohne Abblockung – Resets beim Anlaufen.",
        "Freilaufdiode bei PWM-Ansteuerung zu langsam (1N4007 bei 20 kHz) – Schottky verwenden.",
    ],
    "siehe_auch": ["transistorschalter", "mosfet_schalter", "freilaufdiode"],
    "rechner": ["led_vorwiderstand", "relais_ansteuerung", "basiswiderstand", "freilauf"],
}
