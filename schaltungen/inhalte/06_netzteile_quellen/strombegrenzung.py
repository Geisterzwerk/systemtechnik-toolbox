# Seite "Längsregler mit Strombegrenzung"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Längsregler mit Strombegrenzung",
    "reihenfolge": 40,
    "kurz": "Z-Diode + Leistungstransistor als einfacher Regler – und ein zweiter Transistor macht ihn kurzschlussfest.",
    "stichworte": ["Strombegrenzung", "Kurzschlussschutz", "Längsregler", "Serienregler", "Shunt", "Foldback",
                   "U-I-Kennlinie", "Labornetzteil", "Konstantstrombetrieb", "CC", "CV"],

    "grafiken": ["schaltung_strombegrenzung"],

    "erklaerung": """
## Funktion
**Einfacher Längsregler**: Die Z-Diode legt die Basis von T1 fest, T1 arbeitet als Emitterfolger: `U_a ≈ U_Z − 0.7 V`. Der Laststrom fliesst durch T1, die Z-Diode liefert nur den Basisstrom (I_L / β) – sie kann klein bleiben.

**Strombegrenzung**: Ein Shunt R_S liegt im Laststrom, T2 sitzt mit Basis-Emitter-Strecke parallel zu R_S:
- Solange `I · R_S < 0.6 V`, sperrt T2 – der Regler arbeitet normal.
- Ab `I_max ≈ 0.6 V / R_S` leitet T2 und zieht Basisstrom von T1 ab – der Strom steigt nicht weiter, die Ausgangsspannung bricht ein.
- U-I-Kennlinie: waagrecht (Konstantspannung, CV) bis I_max, dann senkrecht (Konstantstrom, CC) – wie beim Labornetzteil.

## Dimensionierung
1. U_Z = U_a + 0.7 V (+ Spannung an R_S bei Volllast, falls die Ausgangsspannung genau sein muss).
2. Vorwiderstand der Z-Diode: Basisstrom bei Volllast (`I_L / β_min`) plus Z-Mindeststrom (≈ 5 mA) muss bei U_e,min fliessen.
3. `R_S = 0.6 V / I_max`, Leistung `0.6 V · I_max`.
4. **Kurzschlussfall rechnen**: T1 muss `P ≈ U_e · I_max` aushalten (sicherer Arbeitsbereich SOA, Kühlkörper). Bei grossen Strömen Foldback-Begrenzung: Der Kurzschlussstrom wird kleiner als I_max.
5. T1: Darlington oder Leistungstransistor, wenn der Basisstrom die Z-Diode überlasten würde.

## Betriebszustände
- **Normalbetrieb**: U_a ≈ U_Z − 0.7 V − I · R_S, T2 sperrt.
- **Strombegrenzung**: I = I_max, U_a = I_max · R_L (sinkt mit der Last).
- **Kurzschluss**: U_a = 0, I = I_max, T1 verheizt fast die ganze Eingangsspannung mal I_max.

## Messpunkte
- **M1** (Ausgang): Spannung über dem Laststrom aufnehmen (Lastwiderstand in Stufen) → Kennlinie mit Knick.
- Spannung an R_S: erreicht sie ≈ 0.6 V, ist die Begrenzung aktiv.
- Temperatur von T1 im Kurzschluss beobachten (nur kurz testen!).

## Grenzfälle
- R_S → 0: keine Begrenzung (I_max → ∞), ein Kurzschluss zerstört T1.
- R_S zu gross: Spannung fällt schon bei kleinem Strom deutlich ab (schlechte Lastregelung).
- Heisse Umgebung: U_BE von T2 sinkt (−2 mV/K), I_max wird kleiner – Begrenzung ist nur ±20 % genau.
""",

    "tipps": [
        "Der Begrenzungstransistor ist das gleiche Prinzip wie in fast jedem IC-Regler (7805, LM317) – nur dort integriert.",
        "Mit einem Poti statt fester Z-Diode (oder OPV-Regler) wird daraus ein einfaches einstellbares Labornetzteil.",
    ],
    "fehler": [
        "Strombegrenzung eingebaut, aber T1 nicht für den Kurzschlussverlust U_e · I_max ausgelegt.",
        "Z-Diode ohne Berücksichtigung des Basisstroms dimensioniert – bei Volllast bricht U_Z ein.",
        "R_S in die falsche Leitung gelegt – T2 sieht den Laststrom nicht.",
    ],
    "siehe_auch": ["z_stabilisierung", "emitterfolger", "linearregler", "konstantstromquelle"],
    "rechner": ["strombegrenzung", "zdiode_stabi", "kuehlkoerper", "emitterfolger"],
}
