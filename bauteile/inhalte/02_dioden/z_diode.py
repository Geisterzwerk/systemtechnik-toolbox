# =============================================================================
# Thema: Z-Diode  (Kategorie: Dioden)
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner: bauteile/rechner/halbleiter_rechner.py
# =============================================================================

THEMA = {
    "titel": "Z-Diode",
    "reihenfolge": 2,
    "kurz": "Eine Diode, die in Sperrrichtung gezielt bei einer festen Spannung leitet – für Referenzen, Begrenzung und Schutz.",
    "stichworte": ["z-diode", "zener", "zenerdiode", "zener-diode", "stabilisierung", "spannungsstabilisierung",
                   "referenzspannung", "uz", "rz", "vorwiderstand", "rv", "glättungsfaktor", "durchbruch",
                   "avalanche", "lawinendurchbruch", "begrenzung", "überspannungsschutz", "bzx", "bzx79", "bzx55"],

    "steckbrief": {
        "symbol": "diode",
        "zeilen": [
            ("Betrieb", "in **Sperrrichtung** (Kathode an Plus) – anders als eine normale Diode"),
            ("Kennlinie", "Durchlass bei ca. **+0.7 V**, Z-Durchbruch bei **U_AK = −Uz** (3. Quadrant)"),
            ("Z-Spannung", "Uz, erhältlich ca. 2.4 V … 200 V (E24-Reihe: 3.3, 3.9, 4.7, 5.1, 5.6, 6.2, 6.8 …)"),
            ("Differenzieller Widerstand", "rz: je kleiner, desto besser die Stabilisierung (Datenblatt)"),
            ("Immer nötig", "ein **Vorwiderstand Rv** zur Strombegrenzung"),
            ("Temperaturverhalten", "unter ca. 5 V: TK negativ · über ca. 6 V: TK positiv · um 5.6 V: fast 0"),
            ("Wichtigste Kennwerte", "Uz (mit Toleranz), Pz,max (z.B. 0.5 W / 1.3 W), Iz,min, rz"),
        ],
    },

    "grafiken": ["zdiode_kennlinie"],

    "erklaerung": """
## Was macht eine Z-Diode?
In Durchlassrichtung verhält sie sich wie eine normale Diode. Interessant ist die **Sperrrichtung**: Bis zur **Z-Spannung Uz** sperrt sie, danach leitet sie – und die Spannung bleibt dabei **fast konstant**, auch wenn sich der Strom stark ändert. Dieser Durchbruch ist **nicht zerstörend**, solange die maximale Verlustleistung eingehalten wird.
## Die Kennlinie – warum −Uz?
In der Kennlinie wird die Spannung immer **von Anode zu Kathode (U_AK)** gezählt. Der Z-Durchbruch liegt deshalb im **negativen Bereich bei −Uz** (links unten, 3. Quadrant), der normale Durchlassbereich bei ca. **+0.7 V** (rechts oben). In der Schaltung baut man die Z-Diode **mit der Kathode an Plus** ein – gegen Masse gemessen zeigt das Multimeter dann **+Uz**. Beides beschreibt denselben Zustand, nur aus zwei Blickrichtungen (siehe Grafik oben).
## Die Grundschaltung: Stabilisierung mit Vorwiderstand
Die Z-Diode liegt parallel zur Last, davor sitzt ein Vorwiderstand **Rv**. Die Eingangsspannung teilt sich auf: **Ue = U_Rv + Uz**. Steigt Ue, nimmt die Z-Diode mehr Strom auf, und der zusätzliche Spannungsabfall landet am Rv – am Ausgang bleibt Uz.
- **Rv zu gross:** Bei kleiner Eingangsspannung und grosser Last reicht der Strom nicht mehr für die Z-Diode (unter Iz,min) → sie hört auf zu stabilisieren.
- **Rv zu klein:** Bei grosser Eingangsspannung und ohne Last fliesst der ganze Strom durch die Z-Diode → sie überhitzt.
Darum wird immer mit dem **ungünstigsten Fall** gerechnet (siehe Rechner): Rv für Ue,min und IL,max, Verlustleistung für Ue,max und IL,min.
## Wie gut stabilisiert sie?
Der **Glättungsfaktor** G gibt an, wie stark Schwankungen am Eingang verkleinert werden: `G = ΔUe / ΔUa ≈ (Rv + rz) / rz`. Ein grosser Vorwiderstand und ein kleines rz ergeben eine gute Stabilisierung – aber Rv darf nicht so gross werden, dass Iz,min unterschritten wird.
## Grenzen
Die Z-Diode „verheizt“ immer den Strom, den die Last gerade nicht braucht. Sie eignet sich deshalb für **kleine Ströme** (Referenzspannung, Hilfsspannung, Schutz). Für mehr Strom kombiniert man sie mit einem Transistor (Längsregler) oder verwendet einen **Spannungsregler-IC**.
## Weitere Anwendungen
- **Überspannungsschutz** von Eingängen (zusammen mit einem Vorwiderstand)
- **Begrenzung** von Signalen auf einen maximalen Wert
- **Pegelverschiebung:** eine feste Spannung „abziehen“
- **Schnelles Abschalten von Relais:** Z-Diode in Reihe zur Freilaufdiode
## 📚 Vertiefung
Zastrow, *Elektronik*: Kapitel 3 (Spannungsstabilisierung, Z-Diode, Analyse der Stabilisierungs-Grundschaltung), Kapitel 12 (Stabilisierte Stromversorgung).
""",

    "tabellen": [
        {
            "titel": "📊 Z-Diode oder was anderes?",
            "kopf": ["Aufgabe", "Z-Diode geeignet?", "Besser"],
            "zeilen": [
                ["Referenzspannung, wenige mA", "✅ ja", "Präzisionsreferenz (z.B. TL431) wenn genau"],
                ["Versorgung für ICs (> 20 mA)", "❌ nein, zu viel Verlust", "Linearregler / LDO, Schaltregler"],
                ["Eingang gegen Überspannung schützen", "✅ ja, mit Vorwiderstand", "TVS-Diode für schnelle Spitzen"],
                ["Netz-Überspannung (Blitz, Schaltspitzen)", "❌ zu langsam, zu schwach", "Varistor, TVS, Gasableiter"],
            ],
        },
    ],

    "tipps": [
        "**Einbaurichtung:** Die Kathode (Ring) kommt an **Plus** – umgekehrt als bei der normalen Diode in Durchlassrichtung.",
        "**Z-Spannung hat Toleranz** (oft ±5 %) und hängt vom Strom ab. Die Datenblattangabe gilt bei einem bestimmten Teststrom (z.B. 5 mA).",
        "**Z-Dioden um 5.6–6.2 V** sind am temperaturstabilsten – zwei Effekte heben sich dort gegenseitig auf.",
        "**Kleine Z-Spannungen (< 4 V) sind „weich“:** Der Übergang ist nicht scharf, die Spannung ändert sich stark mit dem Strom.",
        "**Leistungsreserve:** Die Z-Diode höchstens mit ca. 50–70 % der Nennleistung betreiben, die Angabe gilt oft nur bei kurzen Anschlussdrähten und 25 °C.",
        "**Parallelkondensator** (z.B. 100 nF) an der Z-Diode reduziert das Rauschen und fängt kurze Spitzen ab.",
        "**Z-Diode als Schutz:** Bei Überspannung leitet sie – der Vorwiderstand (oder eine Sicherung) muss den Strom begrenzen, sonst brennt sie durch.",
    ],
    "fehler": [
        "Z-Diode in Durchlassrichtung eingebaut → Ausgang nur ca. 0.7 V.",
        "Keinen Vorwiderstand eingesetzt → Z-Diode wird sofort zerstört.",
        "Rv nur für den Normalfall berechnet → im Leerlauf mit maximaler Eingangsspannung überhitzt die Z-Diode.",
        "Z-Diode als Versorgung für eine Schaltung mit schwankender, grosser Last verwendet – dafür ist ein Spannungsregler da.",
    ],
    "siehe_auch": ["diode", "led", "bipolartransistor", "widerstand"],

    "rechner": ["zdiode_stabi", "zdiode_kennlinie", "kuehlkoerper"],
}
