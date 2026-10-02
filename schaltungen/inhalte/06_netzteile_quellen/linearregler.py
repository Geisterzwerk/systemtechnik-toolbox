# Seite "Linearregler"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Linearregler: 78xx, LDO und LM317",
    "reihenfolge": 30,
    "kurz": "Stabile Spannung durch einen geregelten Längstransistor – einfach und rauscharm, aber er verheizt die Differenz.",
    "stichworte": ["Linearregler", "Spannungsregler", "Festspannungsregler", "7805", "78xx", "79xx", "LDO",
                   "Low Dropout", "LM317", "Dropout", "Verlustleistung", "Kühlkörper", "Längsregler", "AMS1117"],

    "grafiken": ["schaltung_linearregler"],

    "erklaerung": """
## Funktion
Im Regler sitzt ein Längstransistor, den ein Regelverstärker so steuert, dass die Ausgangsspannung mit einer internen Referenz übereinstimmt – er wirkt wie ein automatisch verstellter Widerstand.
- **78xx** (7805, 7812 …): feste Spannung, Dropout ≈ 2 V, bis 1 … 1.5 A. 79xx für negative Spannungen.
- **LDO** (Low Dropout, z.B. AMS1117, LM1117, MCP1700): Dropout 0.1 … 1 V – nötig, wenn Ein- und Ausgang nahe beieinander liegen (5 V → 3.3 V, Akku).
- **LM317**: einstellbar, hält zwischen OUT und ADJ 1.25 V: `U_aus = 1.25 V · (1 + R2 / R1) + I_ADJ · R2`.
- Verlust: `P = (U_ein − U_aus) · I`, Wirkungsgrad `η ≈ U_aus / U_ein`.

## Dimensionierung
1. Eingang: Wellental ≥ U_aus + Dropout (Datenblatt beim maximalen Strom!).
2. Verlustleistung beim höchsten U_ein (Netz +10 %, Leerlaufüberhöhung) und maximalem Strom.
3. Sperrschichttemperatur `T_j = T_a + P · R_th,JA` ≤ 125 °C. TO-220 ohne Kühlkörper ≈ 50 K/W (≈ 1 … 2 W möglich), sonst Kühlkörper.
4. Kondensatoren nach Datenblatt: 78xx 330 nF am Eingang, 100 nF am Ausgang; viele LDO brauchen einen bestimmten Ausgangs-C (ESR!) für Stabilität.
5. LM317: R1 = 240 Ω (Mindestlast ≈ 5 mA), `R2 = (U_aus − 1.25 V) / (1.25 V / R1 + 50 µA)`, 10 µF an ADJ verbessert die Brummunterdrückung.

## Betriebszustände
- **Regelbereich**: U_aus konstant, Brumm vom Elko wird um 60 … 80 dB unterdrückt.
- **Dropout**: Eingang zu klein – der Regler ist voll durchgesteuert, die Welligkeit kommt durch.
- **Übertemperatur / Überstrom**: integrierte Schutzschaltungen regeln den Strom herunter oder schalten ab (Ausgang „pumpt“).

## Messpunkte
- **M1** (Eingang, Oszilloskop): Wellental muss über U_aus + Dropout liegen.
- **M2** (Ausgang): DC-Wert und Restwelligkeit (AC-Kopplung, mV-Bereich).
- Temperatur am Gehäuse unter Volllast (Thermometer/Wärmebild): T_case + P · R_th,JC ≈ T_j.

## Grenzfälle
- U_ein ≫ U_aus bei grossem Strom: Wirkungsgrad sehr schlecht (12 V → 3.3 V: 27 %) → Schaltregler.
- Ausgang an einem grossen Elko, Eingang kurzgeschlossen: Strom fliesst rückwärts durch den Regler → Schutzdiode OUT→IN.
- Sehr kleine Lasten am LM317: unter der Mindestlast steigt die Ausgangsspannung.
""",

    "tipps": [
        "Kombination: Schaltregler auf ≈ U_aus + 1 V, dann LDO – effizient UND rauscharm (z.B. für Audio oder ADC-Referenzen).",
        "Der LM317 wird mit einem Widerstand zwischen OUT und ADJ zur Konstantstromquelle: I = 1.25 V / R.",
    ],
    "fehler": [
        "Dropout mit der Spitzenspannung statt mit dem Wellental geprüft – Brumm am Ausgang.",
        "Verlustleistung ohne Kühlkörper unterschätzt – der Regler schaltet thermisch ab.",
        "LDO ohne den im Datenblatt geforderten Ausgangskondensator – er schwingt.",
    ],
    "siehe_auch": ["netzteil_ungeregelt", "strombegrenzung", "schaltregler_buck_boost"],
    "rechner": ["linearregler", "lm317", "kuehlkoerper", "netzteil_auslegen"],
}
