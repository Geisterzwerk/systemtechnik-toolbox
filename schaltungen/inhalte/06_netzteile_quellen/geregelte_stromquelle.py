# Seite "Geregelte Stromquelle"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Geregelte Stromquelle mit OPV und MOSFET",
    "reihenfolge": 50,
    "kurz": "Präzise Stromquelle: Der OPV regelt die Spannung an einem Shunt – der Strom folgt der Sollspannung.",
    "stichworte": ["Stromquelle", "Stromsenke", "Konstantstrom", "elektronische Last", "LED-Treiber",
                   "4-20 mA", "Shunt", "OPV", "MOSFET", "Stromregelung", "Akku-Tester"],

    "grafiken": ["schaltung_stromquelle_opv"],

    "erklaerung": """
## Funktion
Die Last liegt zwischen +U_B und dem Drain eines N-MOSFET, unter dem Source sitzt der Shunt R_S gegen GND. Der OPV vergleicht die Sollspannung U_soll (+ Eingang) mit der Spannung am Shunt (− Eingang) und steuert das Gate:
- Gleichgewicht bei `U_Shunt = U_soll` → `I = U_soll / R_S`
- Die Last hat keinen Einfluss, solange der MOSFET noch Spannung „übrig“ hat (Arbeitsbereich).
- Im Gegensatz zur einfachen Transistor-Stromquelle (Konstantstromquelle) ist sie genau (Offset des OPV statt U_BE) und über U_soll einstellbar – z.B. vom DAC eines µC.

## Dimensionierung
1. U_soll bei Maximalstrom 0.1 … 1 V: grösser = genauer (Offset relativ kleiner), kleiner = weniger Verlust im Shunt.
2. `R_S = U_soll / I`, Leistung `I² · R_S`, Toleranz/Temperaturkoeffizient bestimmen die Genauigkeit.
3. Arbeitsbereich: `R_L,max = U_B / I − R_S − R_DS,on`.
4. MOSFET: Verlust `P = (U_B − I · (R_L + R_S)) · I` – am grössten bei R_L = 0. Für elektronische Lasten: Typ mit grossem SOA, Kühlkörper.
5. OPV: Eingangsbereich bis GND (Single-Supply, z.B. LM358, MCP6002), kleiner Offset bei kleinem U_soll. Gate-Widerstand 100 Ω … 1 kΩ gegen Schwingen.

## Betriebszustände
- **Regelbereich**: I = U_soll / R_S, Spannung am MOSFET nimmt den Rest auf.
- **Last zu gross**: MOSFET voll durchgesteuert, OPV-Ausgang an der Grenze, Strom kleiner als gewünscht.
- **U_soll = 0**: MOSFET sperrt, kein Strom (bei Offset des OPV evtl. ein kleiner Reststrom).

## Messpunkte
- **M1** (Shunt): Spannung = U_soll im Regelbereich → Strom ohne Amperemeter bestimmen.
- Drain-Spannung: muss deutlich über U_Shunt liegen, sonst ist der MOSFET am Anschlag.
- Mit dem Oszilloskop am Gate: Schwingt die Regelschleife (MHz), Gate-Widerstand bzw. kleinen C vom Ausgang an − ergänzen.

## Grenzfälle
- R_S sehr klein (mΩ): grosse Ströme möglich, aber Leiterbahn- und Kontaktwiderstände verfälschen → Kelvin-Anschluss (4-Leiter).
- Kapazitive Last oder lange Leitungen: Regelkreis kann schwingen.
- High-Side-Variante (P-MOSFET oder PNP) für Lasten, die einseitig an GND liegen müssen.
""",

    "tipps": [
        "Mit einer PWM + RC-Tiefpass als U_soll wird ein µC zur einstellbaren elektronischen Last.",
        "Für 4 … 20 mA-Stromschleifen gibt es fertige Sender-ICs (XTR115) – das Prinzip ist dasselbe.",
    ],
    "fehler": [
        "OPV ohne Eingangsbereich bis GND – bei kleinen U_soll regelt er nicht.",
        "MOSFET-Verlust nur bei Nennlast gerechnet – bei kleiner Last verheizt er fast U_B · I.",
        "Shunt über lange Leiterbahn angeschlossen – Spannungsabfall auf der Masse verfälscht den Strom.",
    ],
    "siehe_auch": ["konstantstromquelle", "strombegrenzung", "opv_verstaerker"],
    "rechner": ["stromquelle_opv", "konstantstrom", "mosfet_verlust"],
}
