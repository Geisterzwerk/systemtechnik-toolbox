# =============================================================================
# Thema: Diode  (Kategorie: Dioden)
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner: bauteile/rechner/halbleiter_rechner.py
# ERSETZT die Übergangsseite ("alte_seite": "dioden")
# =============================================================================

THEMA = {
    "titel": "Diode",
    "reihenfolge": 1,
    "kurz": "Das elektrische Ventil: lässt Strom nur in eine Richtung durch – Gleichrichter, Schutz, Freilauf.",
    "stichworte": ["diode", "gleichrichter", "gleichrichterdiode", "schottky", "1n4148", "1n4007", "pn-übergang",
                   "durchlassspannung", "uf", "sperrspannung", "sperrstrom", "kennlinie", "arbeitspunkt",
                   "arbeitsgerade", "freilaufdiode", "verpolschutz", "brücke", "brückengleichrichter", "einweg",
                   "mittelpunkt", "erholzeit", "trr", "germanium", "silizium", "anode", "kathode", "begrenzer",
                   "verpolungsschutz", "tvs", "suppressordiode"],

    "steckbrief": {
        "symbol": "diode",
        "zeilen": [
            ("Anschlüsse", "Anode (A) und Kathode (K) – die Kathode ist mit einem Ring markiert"),
            ("Durchlassrichtung", "Strom fliesst von Anode zu Kathode (in Pfeilrichtung)"),
            ("Schwellspannung", "Si ≈ 0.6–0.7 V  ·  Schottky ≈ 0.2–0.45 V  ·  Ge ≈ 0.3 V"),
            ("Sperrrichtung", "nur winziger Sperrstrom – bis zur maximalen Sperrspannung U_RRM"),
            ("Temperatur", "Uf sinkt um ca. **2 mV pro Kelvin**"),
            ("Wichtigste Kennwerte", "I_F (Dauerstrom), U_RRM (Sperrspannung), U_F, t_rr (Erholzeit), I_FSM (Stossstrom)"),
        ],
    },

    "grafiken": ["diode_kennlinie"],

    "erklaerung": """
## Stell dir vor …
Ein **Drehkreuz** am Eingang eines Stadions: In die eine Richtung kommst du mit einem kleinen Schubs durch, in die andere Richtung bleibt es gesperrt, egal wie fest du drückst. Der kleine Schubs ist die **Schwellspannung** (bei Silizium etwa 0.7 V). Drückst du in Sperrrichtung mit enormer Kraft, bricht das Drehkreuz irgendwann – das ist die maximale Sperrspannung.
## Was macht eine Diode?
Eine Diode ist ein **Ventil für den Strom**. In Durchlassrichtung (Plus an der Anode) leitet sie, sobald die Spannung die **Schwellspannung** überschreitet. In Sperrrichtung (Plus an der Kathode) fliesst praktisch kein Strom.
## Wie funktioniert das?
Die Diode besteht aus zwei unterschiedlich dotierten Halbleiterschichten: **p** (Löcher als Ladungsträger) und **n** (Elektronen). An der Grenze entsteht eine **Sperrschicht** ohne freie Ladungsträger.
- **Durchlassrichtung:** Die äussere Spannung baut die Sperrschicht ab. Ab ca. 0.6–0.7 V (Silizium) steigt der Strom steil an.
- **Sperrrichtung:** Die Sperrschicht wird breiter, es fliesst nur ein sehr kleiner Sperrstrom. Wird die maximale Sperrspannung überschritten, bricht die Diode durch (bei normalen Dioden meist zerstörend).
## Kennlinie und Arbeitspunkt
Die Diode ist ein **nichtlinearer** Widerstand: Ihr Widerstand hängt vom Strom ab. Deshalb kann man ihren Strom nicht einfach mit U/R ausrechnen. Die Lösung ist die **Arbeitsgerade** (siehe Grafik oben):
- Die Gerade zeigt, was der **Vorwiderstand** zulässt: bei U_D = 0 fliesst Ub/R, bei U_D = Ub fliesst nichts.
- Die **Kennlinie** zeigt, was die **Diode** zulässt.
- Beide müssen gleichzeitig gelten, deshalb stellt sich der **Schnittpunkt** ein: der **Arbeitspunkt**.
In der Praxis reicht meist die Näherung: **U_D ≈ 0.7 V** (Si), der Rest der Spannung liegt am Widerstand.
## Wofür braucht man Dioden?
- **Gleichrichten:** aus Wechsel- wird pulsierende Gleichspannung (Einweg, Brücke, Mittelpunkt)
- **Freilaufdiode:** schützt Transistoren vor der Abschaltspitze von Relais, Motoren, Ventilen
- **Verpolschutz:** in Reihe (einfach, kostet ca. 0.7 V) oder als Schutzdiode parallel mit Sicherung
- **Begrenzen:** Signale auf einen Bereich klemmen (z.B. ADC-Eingang schützen)
- **Entkoppeln:** zwei Quellen zusammenführen, ohne dass sie gegeneinander arbeiten (ODER-Schaltung)
## Diodenarten im Überblick
- **Standard-Gleichrichter** (1N400x): robust, langsam, für 50 Hz
- **Schnelle / Ultrafast-Dioden:** kurze Erholzeit, für Schaltnetzteile
- **Schottky:** kleine Durchlassspannung, sehr schnell, aber grösserer Sperrstrom
- **Kleinsignaldiode** (1N4148): schnell, kleine Ströme
- **Z-Diode, LED, TVS-Diode:** eigene Seiten bzw. siehe unten
## Beispiel durchgerechnet
Eine Si-Diode mit 1 kΩ Vorwiderstand an 12 V: An der Diode liegen ≈ 0.7 V, am Widerstand der Rest. `I = (12 V − 0.7 V) / 1 kΩ ≈ 11.3 mA`. Die Diode setzt dabei nur `0.7 V · 11.3 mA ≈ 8 mW` um.
Bei grossem Strom sieht das anders aus: Eine 1N4007 hat bei 1 A bis zu ≈ 1.1 V Durchlassspannung → rund **1 W** Wärme. Darum werden Brückengleichrichter in Netzteilen warm – und darum sind Schottky-Dioden mit ihrer kleineren Durchlassspannung in Schaltreglern so beliebt.
## 🔬 Genauer hingeschaut
- **Die Diodengleichung:** `I = Is · (e^(U / (n · U_T)) − 1)` mit der Temperaturspannung `U_T = k · T / q ≈ 26 mV` bei Raumtemperatur. Is ist ein winziger Sättigungsstrom, n liegt zwischen 1 und 2. Folge: Etwa **60 mV mehr Spannung bringen 10× mehr Strom** (für n = 1). Darum ist die Näherung „0.7 V“ so brauchbar – der genaue Strom ändert die Spannung kaum.
- **Temperatur:** Die Durchlassspannung sinkt bei Silizium um ungefähr **2 mV pro Kelvin**. Das nutzt man sogar als einfachen Temperatursensor. Der Sperrstrom steigt dagegen stark mit der Temperatur.
- **Sperrerholzeit trr:** Schaltet eine Diode von Durchlass auf Sperren, fliesst kurz ein Strom rückwärts, bis die Ladungsträger ausgeräumt sind. Bei der 1N4148 sind das wenige Nanosekunden, bei Standard-Gleichrichtern wie der 1N4007 Mikrosekunden. In Schaltnetzteilen mit 100 kHz würde eine langsame Diode deshalb heiss.
- **Sperrschichtkapazität:** Die Sperrschicht wirkt wie ein kleiner Kondensator, dessen Kapazität mit der Sperrspannung sinkt. Bei der **Kapazitätsdiode** (Varicap) ist das gewollt – damit stimmt man Schwingkreise elektronisch ab.
## 💡 Wusstest du?
- Die Typen **1N4001 bis 1N4007** sind alle für 1 A gebaut und unterscheiden sich nur in der Sperrspannung: von 50 V (1N4001) bis 1000 V (1N4007).
- Den Gleichrichter-Effekt an einem Kontakt zwischen Metall und Kristall entdeckte Ferdinand Braun schon **1874** – lange bevor man ihn erklären konnte. Die ersten Radioempfänger („Detektorempfänger“) nutzten genau diesen Effekt.
- Auch eine LED, eine Solarzelle und ein Fotodetektor sind Dioden – nur auf andere Aufgaben optimiert.
## 📚 Vertiefung
Zastrow, *Elektronik*: Kapitel 1 (Widerstandsverhalten von Halbleitern), Kapitel 2 (Halbleiterdiode, Arbeiten mit Kennlinien, Begrenzerschaltungen), Kapitel 10 (Gleichrichtung).
""",

    "tabellen": [
        {
            "titel": "📊 Diodenarten",
            "kopf": ["Typ", "Uf typ.", "Stärke", "Schwäche", "Beispiele"],
            "zeilen": [
                ["Si-Gleichrichter", "0.7–1.1 V", "hohe Sperrspannung, günstig", "langsam (µs)", "1N4001…1N4007"],
                ["Kleinsignal", "0.6–0.7 V", "schnell (ns)", "nur ca. 100–200 mA", "1N4148, BAS16"],
                ["Schottky", "0.2–0.45 V", "sehr schnell, wenig Verlust", "Sperrstrom grösser, oft nur ≤ 100 V", "1N5817…1N5819, BAT46"],
                ["Ultrafast", "0.9–1.5 V", "kurze Erholzeit t_rr", "höheres Uf", "UF4007, MUR460"],
                ["TVS (Suppressor)", "–", "schluckt Spannungsspitzen", "nur kurzzeitig belastbar", "SMBJ-, P6KE-Serie"],
            ],
            "hinweis": "Typische Werte – für die Auslegung immer das Datenblatt verwenden.",
        },
        {
            "titel": "📊 Gleichrichterschaltungen",
            "kopf": ["Schaltung", "Dioden", "Brummfrequenz", "U_dc (mit Elko)", "Sperrspannung je Diode"],
            "zeilen": [
                ["Einweg", "1", "f (50 Hz)", "Û − Uf", "2 · Û"],
                ["Brücke (Graetz)", "4", "2f (100 Hz)", "Û − 2·Uf", "Û"],
                ["Mittelpunkt", "2", "2f (100 Hz)", "Û − Uf  (Û einer Hälfte)", "2 · Û"],
            ],
            "hinweis": "Û = U_eff · √2. Die Brücke ist heute Standard (fertige Brückengleichrichter-Bausteine).",
        },
        {
            "titel": "📊 Datenblatt-Kennwerte",
            "kopf": ["Kürzel", "Bedeutung"],
            "zeilen": [
                ["I_F / I_F(AV)", "maximaler Dauerstrom (Mittelwert)"],
                ["I_FSM", "einmaliger Stossstrom (z.B. beim Einschalten mit leerem Elko)"],
                ["U_RRM", "maximale periodische Sperrspannung"],
                ["U_F", "Durchlassspannung bei angegebenem Strom"],
                ["I_R", "Sperrstrom (steigt stark mit der Temperatur)"],
                ["t_rr", "Sperrverzögerungszeit – so lange leitet die Diode nach dem Umpolen noch rückwärts"],
            ],
        },
    ],

    "tipps": [
        "**Kathode = Ring.** Merksatz: Das Schaltzeichen zeigt einen Pfeil gegen eine Wand – der Strich ist die Kathode, genau wie der Ring auf dem Bauteil.",
        "**Freilaufdiode richtig herum:** Kathode an +Ub, Anode an den Transistor. Im Normalbetrieb sperrt sie, erst beim Abschalten leitet sie.",
        "**Diodentest mit dem Multimeter:** Durchlass zeigt ca. 0.5–0.7 V (Si) bzw. 0.2–0.4 V (Schottky), umgekehrt „OL“. 0 V in beide Richtungen = durchlegiert.",
        "**Schottky am Verpolschutz** spart Spannung (0.3 statt 0.7 V). Noch besser: P-MOSFET als idealer Verpolschutz (fast kein Verlust).",
        "**Sperrstrom der Schottky** verdoppelt sich ca. alle 10 K. In heissen oder sehr hochohmigen Schaltungen (Messtechnik, Akku-Anwendungen) kann das stören.",
        "**Dioden nicht einfach parallel schalten** für mehr Strom: Die Wärmste leitet am meisten (Uf sinkt mit der Temperatur) und wird noch wärmer. Nur mit kleinen Serienwiderständen.",
        "**Für Schaltnetzteile keine 1N4007:** Sie ist zu langsam (lange Erholzeit) und wird heiss. Schottky oder Ultrafast verwenden.",
        "**Einschaltstrom beachten (I_FSM):** Ein leerer Ladeelko wirkt beim Einschalten wie ein Kurzschluss – die Gleichrichterdioden müssen diesen Stoss aushalten.",
        "**Uf als Temperatursensor:** Mit konstantem Strom ändert sich Uf linear mit ca. −2 mV/K – so funktionieren viele einfache Temperatursensoren in ICs.",
    ],
    "fehler": [
        "Diode verkehrt herum eingebaut → Schaltung tot oder (bei Freilaufdiode) Kurzschluss der Versorgung.",
        "Diode ohne Strombegrenzung direkt an eine Spannungsquelle → wegen der steilen Kennlinie fliesst ein riesiger Strom.",
        "Sperrspannung vergessen: Beim Einweg-Gleichrichter mit Elko muss die Diode 2 · Û sperren, nicht nur Û.",
        "Mit „Uf = 0 V“ gerechnet – bei 3.3-V- oder 5-V-Schaltungen fehlen dann 0.7 V.",
    ],
    "siehe_auch": ["z_diode", "led", "bipolartransistor", "relais", "spule", "transformator", "kondensator"],

    "rechner": ["diode_kennlinie", "gleichrichter", "diode_verlust", "diode_temperatur", "kuehlkoerper",
                "freilauf"],                                    # freilauf -> rechner/relais_rechner.py
}
