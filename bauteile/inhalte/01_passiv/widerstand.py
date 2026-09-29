# =============================================================================
# Thema: Widerstand  (Kategorie: Passive Bauteile)
# -----------------------------------------------------------------------------
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Die Rechner stehen in bauteile/rechner/widerstand_rechner.py
# =============================================================================

THEMA = {
    "titel": "Widerstand",
    "reihenfolge": 1,
    "kurz": "Begrenzt den Strom und teilt Spannungen – das häufigste Bauteil überhaupt.",
    "stichworte": ["widerstand", "resistor", "ohm", "farbcode", "farbringe", "smd", "smd-code", "e-reihe",
                   "e12", "e24", "normwert", "spannungsteiler", "pull-up", "pullup", "pull-down", "vorwiderstand",
                   "led", "reihenschaltung", "parallelschaltung", "poti", "potentiometer", "trimmer", "ntc",
                   "ptc", "ldr", "varistor", "shunt", "leitung", "querschnitt", "spannungsfall", "belastbarkeit",
                   "pt100", "temperaturkoeffizient", "0603", "0805", "bauform"],

    # ---- Steckbrief oben (Schaltzeichen aus bauteile/grafiken/symbole.py) ----
    "steckbrief": {
        "symbol": "widerstand",
        "zeilen": [
            ("Formelzeichen", "R"),
            ("Einheit", "Ohm (Ω)   ·   1 kΩ = 1000 Ω   ·   1 MΩ = 1'000'000 Ω"),
            ("Kehrwert", "Leitwert G = 1/R in Siemens (S)"),
            ("Grundformel", "`R = U / I`   (Ohm'sches Gesetz)"),
            ("Leistung", "`P = U · I = I² · R = U² / R`"),
            ("Polung", "keine – Einbaurichtung egal"),
            ("Wichtigste Kennwerte", "Nennwert, Toleranz, Belastbarkeit (W), Grenzspannung, TK"),
        ],
    },

    "erklaerung": """
## Was macht ein Widerstand?
Ein Widerstand **bremst den Stromfluss**. Je grösser der Widerstand, desto kleiner der Strom bei gleicher Spannung. Die elektrische Energie, die dabei „verloren“ geht, wird in **Wärme** umgewandelt – deshalb hat jeder Widerstand eine maximale **Belastbarkeit in Watt**.
## Wofür braucht man ihn?
- **Strom begrenzen:** z.B. Vorwiderstand einer LED
- **Spannung teilen:** Spannungsteiler, z.B. um 24 V für einen 3.3-V-Messeingang herunterzuteilen
- **Definierte Pegel:** Pull-up / Pull-down an digitalen Eingängen (sonst „schwebt“ der Eingang)
- **Strom messen:** niederohmiger Shunt (z.B. 10 mΩ) – die Spannung daran ist proportional zum Strom
- **Zeitglieder:** zusammen mit einem Kondensator (RC-Glied, `τ = R · C`)
## Wovon hängt der Widerstandswert ab?
`R = ρ · l / A` – er steigt mit der **Länge** l, sinkt mit dem **Querschnitt** A und hängt vom **Material** ρ ab. Zusätzlich ändert er sich mit der **Temperatur** (Temperaturkoeffizient α bzw. TK in ppm/K). Bei Metallen steigt er mit der Temperatur (Kupfer ca. **+0.4 % pro Kelvin**).
## Reihen- und Parallelschaltung
- **Reihe:** `R = R1 + R2 + …` – der Gesamtwiderstand ist immer **grösser** als der grösste Einzelwiderstand. Durch alle fliesst derselbe Strom.
- **Parallel:** `1/R = 1/R1 + 1/R2 + …` – der Gesamtwiderstand ist immer **kleiner** als der kleinste. Zwei gleiche parallel = **halber Wert**. Für zwei Widerstände: `R = R1 · R2 / (R1 + R2)`
## Spannungsteiler
`Ua = Ue · R2 / (R1 + R2)` – gilt nur **unbelastet**! Hängt am Ausgang eine Last, liegt sie parallel zu R2 und die Spannung sinkt. Faustregel: Querstrom durch den Teiler mindestens **10× grösser** als der Laststrom.
## Wichtige Kennwerte
- **Nennwert** und **Toleranz** (z.B. 4.7 kΩ ±1 %)
- **Belastbarkeit** in W – gilt meist nur bis ca. **70 °C Umgebungstemperatur**, darüber weniger (Derating-Kurve im Datenblatt)
- **Grenzspannung** – maximale Spannung am Bauteil, auch wenn die Leistung noch passt (wichtig bei kleinen SMD-Bauformen!)
- **Temperaturkoeffizient (TK)** in ppm/K – wie stark sich der Wert mit der Temperatur ändert (100 ppm/K = 0.01 %/K)
""",

    "bilder": [
        {"titel": "🎨 Farbcode", "datei": "farbcode.png", "max_breite": 560,
         "text": "Farbcode für 4- und 5-Ring-Widerstände. Rechner im Tab 🧮 Rechner."},
    ],

    "tabellen": [
        {
            "titel": "📊 Normreihen (E-Reihen)",
            "kopf": ["Reihe", "Werte / Dekade", "Toleranz", "Werte"],
            "zeilen": [
                ["E6", "6", "±20 %", "1.0  1.5  2.2  3.3  4.7  6.8"],
                ["E12", "12", "±10 %", "1.0 1.2 1.5 1.8 2.2 2.7 3.3 3.9 4.7 5.6 6.8 8.2"],
                ["E24", "24", "±5 %", "E12 + 1.1 1.3 1.6 2.0 2.4 3.0 3.6 4.3 5.1 6.2 7.5 9.1"],
                ["E48", "48", "±2 %", "1.00 1.05 1.10 1.15 1.21 … (3 Stellen)"],
                ["E96", "96", "±1 %", "1.00 1.02 1.05 1.07 1.10 … (3 Stellen)"],
            ],
            "hinweis": "Die Werte gelten für jede Dekade: 4.7 → 4.7 Ω, 47 Ω, 470 Ω, 4.7 kΩ, 47 kΩ … Heute sind **E24** (±5 %) und **E96** (±1 %) Standard, weil 1-%-Metallschichtwiderstände kaum mehr kosten.",
        },
        {
            "titel": "📊 Widerstandsarten",
            "kopf": ["Art", "Eigenschaften", "Typischer Einsatz"],
            "zeilen": [
                ["Kohleschicht", "günstig, ±5 %, rauscht mehr, negativer TK", "einfache Schaltungen, veraltet"],
                ["Metallschicht", "±1 % oder besser, rauscharm, kleiner TK", "Standard (bedrahtet)"],
                ["Metalloxid", "hohe Leistung, impulsfest", "Netzteile, Einschaltstrom-Begrenzung"],
                ["Drahtwiderstand", "hohe Leistung, kleine Werte, INDUKTIV", "Leistung, Bremswiderstände"],
                ["SMD Dickschicht", "günstig, ±1–5 %", "Standard auf Leiterplatten"],
                ["SMD Dünnschicht", "±0.1 %, sehr kleiner TK", "Präzision, Messtechnik"],
                ["Shunt", "mΩ-Bereich, 4 Anschlüsse möglich", "Strommessung"],
            ],
        },
        {
            "titel": "📊 Spezialwiderstände",
            "kopf": ["Typ", "Reagiert auf", "Verhalten", "Einsatz"],
            "zeilen": [
                ["NTC (Heissleiter)", "Temperatur", "wärmer → Widerstand SINKT", "Temperaturmessung, Einschaltstrom-Begrenzung"],
                ["PTC (Kaltleiter)", "Temperatur", "wärmer → Widerstand STEIGT (teils sprunghaft)", "Überstromschutz (Polyfuse), Heizung"],
                ["Pt100 / Pt1000", "Temperatur", "100 Ω / 1000 Ω bei 0 °C, sehr linear", "Industrie-Temperaturmessung"],
                ["LDR (Fotowiderstand)", "Licht", "heller → Widerstand sinkt, träge", "Dämmerungsschalter"],
                ["VDR (Varistor)", "Spannung", "ab Schwellspannung sehr niederohmig", "Überspannungsschutz (Netz)"],
                ["Potentiometer / Trimmer", "Drehung / Schieber", "einstellbarer Spannungsteiler", "Einstellungen, Sollwertgeber"],
            ],
        },
        {
            "titel": "📊 SMD-Bauformen (typische Standard-Dickschicht)",
            "kopf": ["Zoll-Code", "Metrisch", "Masse (mm)", "Belastbarkeit", "Grenzspannung"],
            "zeilen": [
                ["0201", "0603M", "0.6 × 0.3", "1/20 W", "25 V"],
                ["0402", "1005M", "1.0 × 0.5", "1/16 W", "50 V"],
                ["0603", "1608M", "1.6 × 0.8", "1/10 W", "50–75 V"],
                ["0805", "2012M", "2.0 × 1.25", "1/8 W", "150 V"],
                ["1206", "3216M", "3.2 × 1.6", "1/4 W", "200 V"],
                ["1210", "3225M", "3.2 × 2.5", "1/2 W", "200 V"],
                ["2512", "6332M", "6.3 × 3.2", "1 W", "200 V"],
            ],
            "hinweis": "**Typische Werte** von Standardreihen – je nach Hersteller und Serie deutlich anders (es gibt z.B. 0603 mit 1/4 W). **Immer Datenblatt prüfen.** Achtung: „0603“ kann Zoll ODER metrisch meinen – metrisch 0603 ist winzig (= Zoll 0201)!",
        },
        {
            "titel": "📊 SMD-Kennzeichnung",
            "kopf": ["Format", "Regel", "Beispiele"],
            "zeilen": [
                ["3 Ziffern", "2 Ziffern + Anzahl Nullen", "472 → 4.7 kΩ   ·   100 → 10 Ω"],
                ["4 Ziffern", "3 Ziffern + Anzahl Nullen", "4701 → 4.7 kΩ   ·   1000 → 100 Ω"],
                ["mit R", "R = Komma", "4R7 → 4.7 Ω   ·   R10 → 0.1 Ω"],
                ["EIA-96", "Code 01–96 (E96-Wert) + Buchstabe (Multiplikator)", "01C → 10 kΩ   ·   68X → 49.9 Ω"],
                ["0 / 000", "0-Ω-Brücke", "Drahtbrücke als Bauteil"],
            ],
        },
    ],

    # ---- 💡 Kniffe: Dinge, die man auch nach Jahren gern vergisst ----
    "tipps": [
        "**Leistung nicht ausreizen:** Die Nennleistung gilt meist nur bis ca. 70 °C Umgebung. Faustregel: höchstens **50–60 %** der Nennleistung nutzen – der Widerstand wird sonst sehr heiss und driftet.",
        "**Grenzspannung bei SMD:** Ein 0603-Widerstand kann bei 230 V oder bei Messeingängen an der Spannung scheitern, obwohl die Leistung passt. Lösung: mehrere Widerstände in Reihe oder grössere Bauform.",
        "**Belasteter Spannungsteiler:** Querstrom mindestens 10× Laststrom. Für ADC-Eingänge hilft oft ein Kondensator (z.B. 100 nF) am Ausgang des Teilers.",
        "**Toleranzen im Worst Case:** Bei einem Teiler können R1 und R2 gegenläufig abweichen – mit ±5 % kann das Ergebnis fast ±10 % daneben liegen. Für Messaufgaben ±1 % oder besser nehmen.",
        "**Messen in der Schaltung verfälscht:** Parallele Pfade (andere Bauteile) gehen in die Messung ein. Ein Bein auslöten – und die Schaltung **immer spannungsfrei** messen, Kondensatoren vorher entladen.",
        "**Kleine Widerstände (< 1 Ω)** mit 4-Leiter-Messung (Kelvin) messen oder beim Multimeter den Leitungswiderstand abziehen (REL/Null-Taste). Messleitungen haben selbst ca. 0.1–0.3 Ω.",
        "**Drahtwiderstände sind Spulen:** Für schnelle Schaltvorgänge, PWM oder HF ungeeignet (Spannungsspitzen, Schwingungen). Dafür Metallschicht/-oxid oder induktionsarme Typen verwenden.",
        "**Pull-up-Werte:** typisch 4.7–10 kΩ. Bei I²C je nach Kabellänge und Geschwindigkeit eher 1–4.7 kΩ – zu grosse Pull-ups machen die Flanken langsam.",
        "**Kupfer wird warm → mehr Widerstand:** Eine Relais- oder Motorwicklung hat heiss ca. 20–30 % mehr Widerstand als kalt. Das Relais zieht dann weniger Strom – bei knapp ausgelegter Spannung zieht es nicht mehr an.",
        "**Metrisch vs. Zoll bei SMD:** „0603“ in einer Stückliste immer prüfen – metrisch 0603 ist die winzige Zoll-Bauform 0201.",
        "**Hochohmige Widerstände rauschen mehr** (thermisches Rauschen `U = √(4·k·T·R·B)`). In empfindlichen Messschaltungen möglichst niederohmig bleiben.",
        "**Farbcode lesen:** Der Toleranzring (oft Gold/Silber/Braun) sitzt meist rechts mit etwas Abstand. Bei 5-Ring-Widerständen mit Braun an beiden Enden hilft nur Nachmessen.",
    ],
    "fehler": [
        "Leistung nicht nachgerechnet → Widerstand verfärbt sich, riecht, Leiterplatte wird braun.",
        "Widerstand unter Spannung gemessen → falscher Wert oder defektes Multimeter.",
        "Mehrere LEDs parallel an EINEM gemeinsamen Vorwiderstand → Strom verteilt sich ungleich, eine LED stirbt zuerst. Jede LED braucht ihren eigenen Widerstand.",
        "`4R7` als 47 Ω gelesen – R ist das Komma: 4.7 Ω.",
        "Digitaler Eingang ohne Pull-up/Pull-down → „schwebt“, reagiert zufällig auf Störungen oder Berührung.",
        "Spannungsteiler als Spannungsquelle für eine Last verwendet (z.B. um 12 V auf 5 V für einen Verbraucher zu reduzieren) → dafür gibt es Spannungsregler.",
    ],
    "siehe_auch": ["kondensator", "diode"],

    # ---- 🧮 Rechner (IDs aus bauteile/rechner/widerstand_rechner.py) ----
    "rechner": ["ohm_leistung", "spannungsteiler", "farbcode_wert", "wert_farbcode", "led_vorwiderstand",
                "reihe_parallel", "smd_code", "e_reihe", "leitung", "temperatur"],
}
