# Seite "MOSFET als Schalter"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "N-MOSFET Low-Side / P-MOSFET High-Side Schalter",
    "reihenfolge": 20,
    "kurz": "Spannungsgesteuerter Schalter mit sehr kleinem Widerstand – wenn die Gate-Spannung reicht.",
    "stichworte": ["MOSFET", "N-Kanal", "P-Kanal", "Low-Side", "High-Side", "Logic-Level", "RDS(on)", "Gate",
                   "Gate-Widerstand", "Pull-down"],

    "grafiken": ["mosfet_simulator"],

    "erklaerung": """
## Funktion
Der MOSFET wird über die **Gate-Source-Spannung** gesteuert, im eingeschalteten Zustand fliesst kein Gate-Strom. Der Kanal wirkt dann wie ein kleiner Widerstand R_DS(on).
- **N-MOSFET Low-Side**: Source an GND, Last zwischen +U_B und Drain. `U_GS = U_Gate` → einfach mit einem µC-Pin anzusteuern.
- **P-MOSFET High-Side**: Source an +U_B, Last zwischen Drain und GND. Eingeschaltet wird mit `U_GS < 0`, also Gate deutlich **unter** U_B; aus mit Gate auf U_B.

## Dimensionierung
1. **U_DS,max** ≥ U_B mit Reserve (induktive Spitzen!), **I_D** ≥ Laststrom.
2. **R_DS(on) bei der tatsächlichen U_GS** aus dem Datenblatt lesen. U_GS(th) ist nur die Schwelle, bei der ein paar µA fliessen – nicht „eingeschaltet“! Für 3.3-V-Logik einen Logic-Level-Typ (spezifiziert bei 2.5 … 4.5 V) wählen.
3. **Verlust**: `P = I² · R_DS(on)` (heiss ca. 1.5 × grösser) plus Schaltverluste bei PWM.
4. **Gate-Beschaltung**: 10 … 100 Ω in Reihe (dämpft Schwingungen), 10 … 100 kΩ Gate→Source (hält den MOSFET beim Reset sicher AUS).
5. P-MOSFET an mehr als 20 V: Gate mit Z-Diode gegen Source schützen und über einen NPN/N-MOSFET nach unten ziehen.

## Betriebszustände
- **Aus**: U_GS < U_GS(th), sperrt, nur Leckstrom.
- **Linearbereich**: U_GS knapp über U_th – der Kanal ist nur halb offen, U_DS gross, der MOSFET heizt (Fehlerfall!).
- **Voll ein**: U_GS deutlich über der Datenblatt-Prüfspannung, U_DS = I · R_DS(on).
- **Umschalten**: Die Gate-Kapazität (Q_g) muss umgeladen werden – je grösser der Gate-Strom, desto schneller.

## Messpunkte
- **U_DS** im eingeschalteten Zustand: wenige mV bis 100 mV = voll durchgeschaltet; Volt = Gate-Spannung zu klein.
- **U_GS** direkt am MOSFET messen (nicht am µC-Pin), bei PWM mit dem Oszilloskop: saubere Flanken, kein Klingeln.
- Temperatur des Gehäuses nach einigen Minuten Last.

## Grenzfälle
- Gate offen (µC im Reset): Das Gate kann sich aufladen, der MOSFET schaltet halb ein → Pull-down-Widerstand.
- U_GS über ±20 V: Gate-Oxid schlägt durch, MOSFET ist sofort defekt.
- Sehr schnelle Flanken + lange Leitungen: Überschwinger am Drain → Snubber oder grösserer Gate-Widerstand.
""",

    "tipps": [
        "Für 3.3-V-µC: IRLML2502, AO3400, SI2302 (klein, SOT-23) – oder bei grossen Strömen einen Gate-Treiber verwenden.",
        "Die Body-Diode leitet in Rückrichtung – bei Brückenschaltungen und Verpolschutz wichtig.",
    ],
    "fehler": [
        "MOSFET nach U_GS(th) ausgewählt („2 V reicht für 3.3 V“) – R_DS(on) ist nur bei viel höherer U_GS garantiert.",
        "Kein Pull-down am Gate – Motor läuft beim Einschalten der Versorgung kurz an.",
        "P-MOSFET High-Side direkt am µC-Pin bei U_B > U_Pin – Gate kann nicht auf U_B, schaltet nie ganz ab.",
    ],
    "siehe_auch": ["transistorschalter", "lasten_ansteuern", "verpolschutz"],
    "rechner": ["mosfet_verlust", "mosfet_gate", "kuehlkoerper"],
}
