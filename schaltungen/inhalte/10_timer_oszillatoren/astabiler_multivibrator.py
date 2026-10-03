# Seite "Astabiler Multivibrator"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Astabiler Multivibrator (zwei Transistoren)",
    "reihenfolge": 20,
    "kurz": "Der einfachste Taktgeber aus Einzelteilen: zwei Transistoren schalten sich über Kondensatoren gegenseitig ab.",
    "stichworte": ["Multivibrator", "astabil", "Flip-Flop-Blinker", "Wechselblinker", "Kippschaltung",
                   "Transistor-Oszillator", "Kreuzkopplung", "Koppelkondensator", "Blinkschaltung"],

    "grafiken": ["schaltung_multivibrator"],

    "erklaerung": """
## Funktion
Zwei Transistorschalter, über Kondensatoren über Kreuz verbunden. Es leitet immer genau einer:
1. T1 schaltet ein → sein Kollektor springt von U_B auf ≈ 0.2 V.
2. Dieser Sprung geht über C1 an die Basis von T2 → sie springt auf etwa **−(U_B − 0.9 V)**, T2 sperrt.
3. C1 lädt sich über R_B2 um, bis die Basis von T2 wieder +0.7 V erreicht.
4. T2 schaltet ein und sperrt über C2 jetzt T1 – das Spiel beginnt von vorn.

Zeiten (je Hälfte): `t = ln((2·U_B − 0.7) / (U_B − 0.7)) · R_B · C ≈ ln2 · R_B · C = 0.69 · R_B · C`
Frequenz (symmetrisch): `f ≈ 0.72 / (R_B · C)`

## Dimensionierung
1. R_C nach dem gewünschten Kollektorstrom (z.B. LED mit Vorwiderstand statt R_C).
2. Sättigung sicherstellen: `R_B ≤ β · R_C` (mit Reserve: R_B ≈ β · R_C / 2).
3. C aus der gewünschten Zeit: `C = t / (0.69 · R_B)`. Unterschiedliche C oder R_B ergeben einen unsymmetrischen Takt.
4. Bei U_B > 5 V: Die Basis-Emitter-Strecke bricht in Sperrrichtung bei ca. 5 … 6 V durch → Diode in Reihe zur Basis oder Schaltung nur bis 5 V betreiben.
5. Grosse Elkos: Polung beachten – der Pluspol zeigt jeweils zum Kollektor.

## Betriebszustände
- **T1 leitet, T2 sperrt**: U_CE1 ≈ 0.2 V, U_CE2 steigt mit R_C · C auf U_B (abgerundete Flanke).
- **Umschalten**: Basis des abschaltenden Transistors springt negativ.
- **Beide leiten** (beim Einschalten möglich): Schaltung schwingt nicht an → leicht unsymmetrische Bauteile helfen.

## Messpunkte
- **M1** (Kollektor T1): Rechteck zwischen 0.2 V und U_B mit abgerundeter Anstiegsflanke.
- **M2** (Basis T2): Sägezahn-artig von −(U_B − 0.9 V) bis +0.7 V – zeigt, wie C umgeladen wird.
- Frequenz mit dem Oszilloskop oder einem Frequenzzähler.

## Grenzfälle
- R_B zu gross: Transistoren sättigen nicht, die Flanken werden schlecht oder die Schwingung reisst ab.
- R_C · C gross gegen R_B · C: Kollektorspannung erreicht U_B nicht mehr, bevor wieder umgeschaltet wird.
- Hohe Versorgung: Basis-Emitter-Durchbruch verändert die Frequenz und belastet die Transistoren.
- Sehr kleine C: Transistor-Schaltzeiten und Kapazitäten bestimmen die Frequenz.
""",

    "tipps": [
        "Klassischer Wechselblinker: statt R_C je eine LED mit Vorwiderstand, C = 47 µF, R_B = 47 kΩ → ≈ 0.3 Hz.",
        "Für genaue oder einstellbare Frequenzen ist ein NE555 einfacher – der Multivibrator ist vor allem lehrreich.",
    ],
    "fehler": [
        "Elkos falsch gepolt – sie werden über die Zeit zerstört.",
        "R_B grösser als β · R_C gewählt – keine sauberen Rechtecke.",
        "Bei 9 oder 12 V ohne Basis-Schutzdiode betrieben – Basis-Emitter-Durchbruch.",
    ],
    "siehe_auch": ["ne555_timer", "transistorschalter", "rc_laden_entladen"],
    "rechner": ["multivibrator", "rc_zeit"],
}
