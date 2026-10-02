# Seite "Bipolartransistor als Schalter"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "NPN Low-Side / PNP High-Side Schalter",
    "reihenfolge": 10,
    "kurz": "Ein kleiner Basisstrom schaltet einen grossen Laststrom – sicher nur in der Sättigung.",
    "stichworte": ["Transistorschalter", "NPN", "PNP", "Low-Side", "High-Side", "Sättigung", "Basiswiderstand",
                   "Übersteuerung", "Bipolartransistor"],

    "grafiken": ["transistor_simulator"],

    "erklaerung": """
## Funktion
- **NPN Low-Side**: Last zwischen +U_B und Kollektor, Emitter an GND. HIGH an der Basis (über R_B) schaltet ein.
- **PNP High-Side**: Emitter an +U_B, Last zwischen Kollektor und GND. Eingeschaltet wird, wenn die Basis **unter** U_B − 0.7 V gezogen wird (LOW). Zum Ausschalten muss die Basis fast auf U_B.

Der Transistor ist **stromgesteuert**: `I_C ≤ B · I_B`. Als Schalter soll er **gesättigt** sein – dann begrenzt nur noch die Last den Strom, `U_CE,sat ≈ 0.1 … 0.3 V`, und es entsteht kaum Wärme.

## Dimensionierung
1. Laststrom: `I_C = (U_B − U_CE,sat) / R_Last` (oder Nennstrom der Last).
2. Basisstrom mit Übersteuerung: `I_B = ü · I_C / B_min`, ü = 2 … 5 (B_min aus dem Datenblatt, nicht der typische Wert!).
3. Basiswiderstand: NPN `R_B = (U_St − 0.7 V) / I_B`, PNP `R_B = (U_B − 0.7 V − U_St,LOW) / I_B` – Normwert **abrunden** (mehr Basisstrom = sicherer gesättigt).
4. Prüfen: Liefert der Steuerausgang I_B? (µC-Pins oft ≤ 10 … 20 mA)
5. Verlust: `P ≈ U_CE,sat · I_C + U_BE · I_B`, beim Schalten (PWM) kommen Schaltverluste dazu.

## Betriebszustände
- **Gesperrt**: I_B = 0, I_C ≈ 0, ganze Spannung am Transistor.
- **Aktiv (linear)**: zu wenig Basisstrom – der Transistor arbeitet als Verstärker, U_CE ist gross, er wird heiss (Fehlerfall für einen Schalter!).
- **Gesättigt**: U_CE ≈ 0.2 V, Last bekommt fast die volle Spannung.

## Messpunkte
- **U_CE** im eingeschalteten Zustand: < 0.3 V = gesättigt, mehrere Volt = zu wenig Basisstrom.
- **U_BE** ≈ 0.6 … 0.8 V, wenn er eingeschaltet ist; deutlich mehr deutet auf einen defekten Transistor.
- Basisstrom: Spannung an R_B messen und durch R_B teilen.

## Grenzfälle
- Ohne R_B: Der Steuerausgang treibt die Basis-Emitter-Diode direkt – Pin oder Transistor werden überlastet.
- PNP mit 3.3-V-µC an 12 V: Der Pin kann die Basis nicht auf 12 V ziehen → der PNP schaltet nie ab. Lösung: kleiner NPN als Pegelwandler davor.
- Induktive Last ohne Freilaufdiode: Durchbruch beim Abschalten (siehe Freilaufdiode).
""",

    "tipps": [
        "Ab ca. 0.5 A ist ein Logic-Level-MOSFET meist die bessere Wahl – er braucht keinen Dauer-Steuerstrom.",
        "Ein Widerstand Basis–Emitter (z.B. 10 … 100 kΩ) hält den Transistor beim Reset sicher AUS.",
    ],
    "fehler": [
        "Mit typischem B statt B_min gerechnet – bei einem Exemplar mit kleinem B ist der Transistor nicht gesättigt.",
        "Normwert für R_B aufgerundet statt abgerundet – zu wenig Basisstrom.",
        "PNP High-Side direkt am 3.3-V-Pin bei höherer Lastspannung – schaltet nie aus.",
    ],
    "siehe_auch": ["mosfet_schalter", "lasten_ansteuern", "freilaufdiode"],
    "rechner": ["basiswiderstand", "arbeitspunkt", "verlustleistung"],
}
