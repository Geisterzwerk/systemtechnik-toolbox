# Seite "Konstantstromquelle"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Konstantstromquelle (Transistor / JFET)",
    "reihenfolge": 60,
    "kurz": "Liefert einen festen Strom, unabhängig von der Last – solange die Spannung reicht.",
    "stichworte": ["Konstantstromquelle", "Stromquelle", "Stromregler", "JFET", "Stromsenke", "LED-Treiber",
                   "Arbeitsbereich", "Compliance", "Z-Diode"],

    "grafiken": ["schaltung_konstantstrom"],

    "erklaerung": """
## Funktion
**Transistor + Referenz**: Die Basis liegt auf einer festen Spannung U_ref (Z-Diode, zwei Dioden ≈ 1.4 V, LED ≈ 1.8 V). Am Emitterwiderstand liegt deshalb immer `U_ref − U_BE`, und es fliesst
- `I ≈ (U_ref − 0.7 V) / R_E`

Die Last im Kollektorkreis hat darauf keinen Einfluss – der Transistor passt U_CE automatisch an.

**JFET + R_S** (Zweipol-Stromquelle): Gate an GND, R_S zwischen Source und GND. Der Strom erzeugt `U_GS = −I · R_S`, die den Kanal so weit abschnürt, dass sich ein fester Strom einstellt:
- `I = I_DSS · (1 − U_GS / U_P)²` mit `U_GS = −I · R_S`;  R_S = 0 → I = I_DSS

## Dimensionierung
1. Transistor: `R_E = (U_ref − 0.7 V) / I`; U_ref ≥ ca. 2 V wählen, damit die Temperaturdrift von U_BE (−2 mV/K) wenig ausmacht.
2. Referenz speisen: Widerstand von U_B zur Z-Diode, I_Z ≈ 1 … 5 mA (deutlich grösser als I_B).
3. **Arbeitsbereich (Compliance)**: Die Last darf höchstens `U_B − (U_ref − 0.7 V) − U_CE,sat` bekommen. Darüber sättigt der Transistor, der Strom sinkt.
4. Verlust im Transistor: `P = U_CE · I` – am grössten bei kleiner Last (Kurzschluss).
5. JFET: I_DSS und U_P streuen stark (Faktor 2) – R_S am Exemplar abgleichen; `R_S = |U_P| · (1 − √(I / I_DSS)) / I`.

## Betriebszustände
- **Im Regelbereich**: Strom konstant, U_CE nimmt den Rest der Spannung auf.
- **Last zu gross**: Spannung reicht nicht mehr, Transistor sättigt, Strom ≈ (U_B − 0.2 V) / (R_L + R_E).
- **Last kurzgeschlossen**: Strom bleibt konstant (Kurzschlussfest!), aber U_CE und damit die Verlustleistung sind maximal.

## Messpunkte
- Spannung an R_E (bzw. R_S) messen → `I = U / R` (kein Amperemeter nötig).
- **M1** (Kollektor/Drain): muss mindestens ca. 0.3 V (bzw. |U_P| − |U_GS| beim JFET) über dem Emitter/Source liegen, sonst regelt die Quelle nicht.
- Last verändern (Poti): Der Strom darf sich im Regelbereich kaum ändern.

## Grenzfälle
- R_E → 0: Strom wird nur noch von β und dem Basisstrom begrenzt – Transistor zerstört.
- Sehr kleine Ströme (µA): Basisstrom und Leckströme verfälschen das Ergebnis → JFET oder OPV-Regler.
- Präzise Quellen: OPV + Transistor + Shunt (geregelte Stromquelle) oder Spezial-ICs (LM334).
""",

    "tipps": [
        "LED-Ketten an schwankender Spannung (Auto 12 … 14.4 V): Konstantstromquelle statt Vorwiderstand – die Helligkeit bleibt gleich.",
        "Zwei-Transistor-Stromquelle (zweiter Transistor misst die Spannung an R_E) braucht keine Z-Diode und regelt bei ≈ 0.6 V / R_E.",
    ],
    "fehler": [
        "Arbeitsbereich vergessen: Die Last braucht mehr Spannung, als übrig bleibt – der Strom ist nicht mehr konstant.",
        "Verlustleistung nur bei Nennlast gerechnet – bei Kurzschluss der Last wird der Transistor am heissesten.",
        "Z-Diode mit zu kleinem Strom betrieben – U_ref ist dann nicht stabil (Knick der Kennlinie).",
    ],
    "siehe_auch": ["emitterfolger", "z_stabilisierung", "lasten_ansteuern"],
    "rechner": ["konstantstrom", "kuehlkoerper"],
}
