# Seite "Verpolschutz"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Verpolschutz (Diode / P-MOSFET)",
    "reihenfolge": 30,
    "kurz": "Schützt die Elektronik, wenn Batterie oder Netzteil falsch herum angeschlossen werden.",
    "stichworte": ["Verpolschutz", "Verpolung", "P-MOSFET", "Schottky", "Body-Diode", "Batterie",
                   "reverse polarity", "Idealdiode"],

    "grafiken": ["schaltung_verpol"],

    "erklaerung": """
## Funktion
**Diode in der Plusleitung**: Richtig gepolt leitet sie, verpolt sperrt sie. Einfach und sicher, aber sie kostet immer die Durchlassspannung U_F (Si ≈ 0.7 V, Schottky ≈ 0.3 … 0.5 V) und erzeugt Wärme `P = U_F · I`.

**P-MOSFET in der Plusleitung** („verkehrt herum“: Drain an der Batterie, Source zur Last, Gate über einen Widerstand an GND):
- Beim Einschalten leitet zuerst die **Body-Diode** (Anode = Drain, Kathode = Source) → Source liegt bei ≈ U_B − 0.7 V.
- Damit ist `U_GS ≈ −U_B`: Der Kanal schaltet durch, die Body-Diode wird überbrückt. Übrig bleibt `ΔU = I · R_DS(on)` – oft nur Millivolt.
- Verpolt: Gate liegt positiv gegenüber Source → MOSFET sperrt, und die Body-Diode ist ebenfalls in Sperrrichtung.

## Dimensionierung
- **Diode**: Durchlassstrom ≥ Laststrom (mit Reserve), Sperrspannung U_RRM ≥ U_B (besser 2 ×), Verlustleistung `U_F · I` → ab ca. 1 W Kühlfläche.
- **P-MOSFET**:
  - `U_DS,max` ≥ U_B (mit Reserve), Dauerstrom I_D ≥ Laststrom.
  - R_DS(on) beim tatsächlichen `U_GS = U_B` aus dem Datenblatt nehmen, Verlust `P = I² · R_DS(on)`.
  - `U_GS,max` beachten (meist ±20 V): Bei höheren Spannungen eine **Z-Diode (z.B. 12 V) zwischen Gate und Source** und einen Widerstand (z.B. 10 … 100 kΩ) vom Gate nach GND.
  - Bei kleinen Spannungen (< 5 V) einen Logic-Level-Typ wählen, sonst schaltet der Kanal nicht voll durch.

## Betriebszustände
- **Richtig gepolt**: Last bekommt U_B − U_F (Diode) bzw. U_B − I · R_DS(on) (MOSFET).
- **Verpolt**: Kein Strom, die ganze Spannung liegt am Schutzbauteil (Sperrspannung!).
- **Beim Einstecken**: Beim MOSFET leitet für Mikrosekunden die Body-Diode, bis das Gate umgeladen ist.

## Messpunkte
- Spannung **über** dem Schutzbauteil (Drain–Source bzw. Anode–Kathode) bei Nennlast: Diode ≈ 0.4 … 0.8 V, MOSFET nur einige mV … 100 mV.
- U_GS am MOSFET: muss deutlich grösser als |U_GS(th)| sein, aber unter U_GS,max.
- Mit verpolter Versorgung (Labornetzteil mit Strombegrenzung!) prüfen: Strom ≈ 0, Last bekommt 0 V.

## Grenzfälle
- Sehr grosser Strom: Diode wird heiss (2 A × 0.7 V = 1.4 W) → MOSFET ist dann fast immer besser.
- Last mit grossem Elko und Rückspeisung (Motor bremst): Beim MOSFET kann Strom auch rückwärts fliessen, solange er leitet – für echte „Idealdioden“ gibt es Controller-ICs.
- Ohne Schutz: Elkos (verpolt) können platzen, ICs und Regler werden über ihre internen Dioden kurzgeschlossen.
""",

    "tipps": [
        "Alternative ohne Spannungsverlust im Betrieb: Diode parallel zur Last in Sperrrichtung + Sicherung – bei Verpolung leitet die Diode und die Sicherung brennt durch.",
        "Für Kfz-Anwendungen gibt es Idealdioden-Controller (N-MOSFET mit Ladungspumpe), die auch Lastabwurf-Spitzen beherrschen.",
    ],
    "fehler": [
        "P-MOSFET falsch herum eingebaut (Source an der Batterie): Die Body-Diode leitet dann auch bei Verpolung – kein Schutz.",
        "N-MOSFET in die Plusleitung gesetzt: Sein Gate müsste über U_B liegen – ohne Treiber schaltet er nicht.",
        "U_GS,max überschritten (24-V-System, Gate direkt an GND) – Gate-Oxid durchgeschlagen.",
        "Diode zu knapp dimensioniert: Einschaltstrom in einen grossen Elko überlastet sie.",
    ],
    "siehe_auch": ["tvs_schutz", "eingangsschutz"],
    "rechner": ["verpolschutz", "diode_verlust", "kuehlkoerper"],
}
