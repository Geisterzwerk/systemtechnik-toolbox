# Seite "Bipolare Versorgung"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Bipolare Versorgung ±U und virtuelle Masse",
    "reihenfolge": 60,
    "kurz": "OPV-Schaltungen brauchen oft ±U: per Trafo mit Mittelanzapfung, Ladungspumpe – oder als virtuelle Masse aus einer Spannung.",
    "stichworte": ["bipolare Versorgung", "symmetrische Versorgung", "±15 V", "virtuelle Masse", "Rail-Splitter",
                   "TLE2426", "Mittelanzapfung", "7812", "7912", "Ladungspumpe", "Split Supply"],

    "grafiken": ["schaltung_virtuelle_masse"],

    "erklaerung": """
## Funktion
Drei Wege zu ±U:
- **Trafo mit Mittelanzapfung**: Die Mittelanzapfung wird GND, ein Brückengleichrichter liefert an zwei Elkos +Û und −Û. Dahinter 78xx für + und 79xx für −. Echte, belastbare ±U.
- **Ladungspumpe / invertierender Schaltregler**: macht aus +U eine −U (z.B. ICL7660, kleine Ströme).
- **Virtuelle Masse**: Aus einer Spannung U_B erzeugt ein Teiler die Mitte M = U_B / 2 als neuen Bezug. Dann gilt +U = U_B/2 und −U = −U_B/2 gegenüber M.

Die einfache Teilermitte verschiebt sich, sobald die Lasten oben und unten ungleich sind – der Differenzstrom fliesst durch den Teiler:
- `U_M = U_B · (1/R + 1/R_L1) / (2/R + 1/R_L1 + 1/R_L2)`
- **Rail-Splitter**: Ein OPV als Spannungsfolger (oder ein IC wie TLE2426) hält M auf U_B/2 und liefert bzw. schluckt die Differenz der Lastströme – bis zu seinem Ausgangsstrom.

## Dimensionierung
1. Ströme der positiven und negativen Seite abschätzen – die DIFFERENZ muss der Puffer liefern können.
2. Teiler: R ≈ 10 … 100 kΩ (nur die Referenz für den OPV), Kondensator 1 … 10 µF parallel zum unteren R gegen Störungen.
3. Puffer: OPV mit genügend Ausgangsstrom; für mehr als ≈ 20 mA eine Push-Pull-Stufe hinter den OPV oder ein Spezial-IC.
4. Ausgang des Puffers mit kleinem Widerstand (≈ 10 … 50 Ω) entkoppeln, bevor grosse Kondensatoren an M hängen (Stabilität).
5. Mittelanzapfungs-Netzteil: Beide Elkos und Regler wie bei der einfachen Version auslegen (Rechner „Netzteil auslegen“).

## Betriebszustände
- **Symmetrische Last**: Mitte bleibt bei U_B/2, auch ohne Puffer.
- **Unsymmetrische Last ohne Puffer**: Mitte wandert zur weniger belasteten Seite – eine Seite hat zu wenig Spannung.
- **Unsymmetrische Last mit Puffer**: Mitte bleibt, bis der OPV an seine Stromgrenze kommt.

## Messpunkte
- **M** gegen beide Schienen messen: +U und −U müssen gleich gross sein.
- Ausgangsstrom des Puffers indirekt über einen kleinen Serienwiderstand.
- Achtung: Die virtuelle Masse ist NICHT die Schutzerde – Oszilloskop-Masse (geerdet) nicht an M anschliessen, wenn U_B selbst geerdet ist, sonst Kurzschluss der unteren Hälfte.

## Grenzfälle
- R_L2 → ∞ (nur positive Seite belastet): ohne Puffer fliesst der ganze Laststrom durch den unteren Teiler-R – die Mitte steigt stark.
- Teiler ohne Puffer, aber R ≪ R_L: funktioniert, kostet aber viel Querstrom (Batterie!).
- Signale mit Gleichanteil gegen die echte Masse (GND der Batterie) und gegen M verwechselt – der Pegel ist um U_B/2 verschoben.
""",

    "tipps": [
        "Bei Batteriegeräten mit OPV ist die virtuelle Masse Standard – oder man nimmt Rail-to-Rail-OPV mit einer Versorgung und legt die Signale auf U_B/2.",
        "Für ±12 V bis ±15 V aus 5 V gibt es fertige isolierte DC/DC-Wandler-Module.",
    ],
    "fehler": [
        "Einfachen Spannungsteiler als Masse verwendet und ungleiche Lasten angeschlossen – die Spannungen sind nicht mehr symmetrisch.",
        "Geerdetes Oszilloskop an die virtuelle Masse gehängt – Kurzschluss gegen die echte Masse.",
        "79xx wie 78xx beschaltet – die Pinbelegung ist anders (IN und GND vertauscht).",
    ],
    "siehe_auch": ["netzteil_ungeregelt", "opv_verstaerker", "spannungsteiler"],
    "rechner": ["spannungsteiler", "netzteil_auslegen", "linearregler"],
}
