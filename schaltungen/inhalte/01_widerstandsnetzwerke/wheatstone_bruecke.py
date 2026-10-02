# Seite "Wheatstone-Brücke"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Wheatstone-Brücke",
    "reihenfolge": 50,
    "kurz": "Zwei Spannungsteiler nebeneinander: misst kleine Widerstandsänderungen als Differenzspannung.",
    "stichworte": ["Wheatstone", "Brücke", "Messbrücke", "Brückenschaltung", "Abgleich", "Diagonalspannung",
                   "DMS", "Pt100", "bridge"],

    "grafiken": ["schaltung_bruecke"],

    "erklaerung": """
## Funktion
Zwei Spannungsteiler (R1/R2 links, R3/R4 rechts) hängen an derselben Speisespannung Ue. Gemessen wird die **Diagonalspannung** zwischen den Mittelpunkten:
- `U(M1) = Ue · R2 / (R1 + R2)`     `U(M2) = Ue · R4 / (R3 + R4)`
- `U_d = U(M1) − U(M2)`
- **abgeglichen** (U_d = 0), wenn `R1 / R2 = R3 / R4`

Der Trick: Die grosse Grundspannung (z.B. 5 V an beiden Mittelpunkten) hebt sich auf. Übrig bleibt nur die kleine Änderung – sie lässt sich mit hoher Verstärkung messen, ohne dass der Verstärker übersteuert.

## Dimensionierung
1. Sensor in einen Zweig einbauen (z.B. R4 = Pt100 oder DMS), die anderen Widerstände so wählen, dass die Brücke im Nullpunkt (0 °C, unbelastet) abgeglichen ist.
2. **Gleiche Widerstände** (R1 = R2 = R3 = R4 = R) ergeben die grösste Empfindlichkeit: bei kleiner Änderung ΔR gilt `U_d ≈ Ue · ΔR / (4·R)`.
3. **Speisespannung** so hoch wie möglich (grösseres Signal), aber Eigenerwärmung des Sensors begrenzen (Pt100: Messstrom ≤ 1 mA).
4. Angabe der Empfindlichkeit in **mV/V**: Signal pro Volt Speisung (Wägezellen typ. 2 mV/V bei Nennlast).

## Betriebszustände
- **Abgeglichen**: U_d = 0.
- **Verstimmt**: U_d ≠ 0, Vorzeichen zeigt die Richtung (Widerstand grösser oder kleiner).
- **Ausschlag- vs. Abgleichverfahren**: Entweder U_d messen (Ausschlag) oder einen Widerstand nachstellen, bis U_d = 0 (Abgleich – sehr genau, weil nur „Null“ erkannt werden muss).

## Messpunkte
- **M1** und **M2** je gegen GND: beide ≈ Ue/2 bei gleichen Widerständen.
- **U_d zwischen M1 und M2** messen – mit einem Messgerät mit potentialfreiem Eingang (Multimeter) oder einem Instrumentenverstärker. Ein einfacher Oszilloskop-Tastkopf gegen GND misst NICHT U_d!
- Ue direkt an der Brücke messen (Leitungswiderstände), bei Präzisionsmessungen mit Sense-Leitungen.

## Grenzfälle
- Grosse Änderungen: U_d ist nicht mehr linear zu ΔR (Viertelbrücke). Halb- und Vollbrücke mit mehreren aktiven Elementen sind linearer und kompensieren Temperatur.
- Ein Zweig unterbrochen: M1 bzw. M2 springt auf 0 V oder Ue → U_d gross (Drahtbruch-Erkennung möglich).
- Leitungswiderstände zum Sensor liegen in Reihe zum Sensor → 3-Leiter-Schaltung (Messtechnik → Temperatur) kompensiert das.
""",

    "tipps": [
        "Für das Signal immer einen Instrumentenverstärker verwenden: hohe Gleichtaktunterdrückung, misst nur die Differenz.",
        "Brücke mit derselben Spannung speisen, die auch der ADC als Referenz nutzt (ratiometrische Messung) – dann kürzen sich Schwankungen von Ue heraus.",
    ],
    "fehler": [
        "U_d mit einem geerdeten Messgerät (Oszi) gegen GND gemessen – dabei wird ein Brückenzweig kurzgeschlossen.",
        "Abgleichbedingung verwechselt: Es gilt R1/R2 = R3/R4 (gleiche Teilerverhältnisse), nicht R1 = R3.",
        "Speisespannung zu hoch: Sensor erwärmt sich selbst und misst die eigene Wärme mit.",
    ],
    "siehe_auch": ["spannungsteiler"],
    "rechner": ["bruecke", "dms", "pt100"],
}
