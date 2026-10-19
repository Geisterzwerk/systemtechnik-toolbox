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
## Stell dir vor …
Strom in einem Draht kann man sich wie Wasser in einem Rohr vorstellen: Die **Spannung** ist der Druck, der das Wasser antreibt, der **Strom** ist die Menge, die pro Sekunde durchfliesst. Ein **Widerstand** ist eine Engstelle im Rohr – bei gleichem Druck fliesst weniger durch. Ganz genau stimmt der Vergleich nicht, für den Einstieg hilft er aber sehr.
## So funktioniert es
In einem Leiter bewegen sich Elektronen. Auf ihrem Weg stossen sie ständig mit den Atomen des Materials zusammen und geben dabei Energie ab – das Material wird **warm**. Ein Widerstand ist ein Bauteil, bei dem dieser Effekt gewollt und genau bekannt ist:
- Er **begrenzt den Strom**: grösserer Widerstand → kleinerer Strom (bei gleicher Spannung).
- An ihm **fällt eine Spannung ab**: Die Spannung der Quelle teilt sich auf die Bauteile im Stromkreis auf.
- Er **wandelt elektrische Energie in Wärme** um. Darum hat jeder Widerstand eine maximale **Belastbarkeit in Watt**.
Ein Widerstand hat **keine Polung** – man kann ihn beliebig herum einbauen.
## Wofür braucht man ihn?
- **Strom begrenzen:** z.B. Vorwiderstand einer LED
- **Spannung teilen:** Spannungsteiler, z.B. um 24 V für einen 3.3-V-Messeingang herunterzuteilen
- **Definierte Pegel:** Pull-up / Pull-down an digitalen Eingängen (sonst „schwebt“ der Eingang)
- **Strom messen:** niederohmiger Shunt (z.B. 10 mΩ) – die Spannung daran ist proportional zum Strom
- **Zeitglieder:** zusammen mit einem Kondensator (RC-Glied, `τ = R · C`)
## Rechnen mit dem Ohm'schen Gesetz
Spannung, Strom und Widerstand hängen fest zusammen: `U = R · I`. Umgestellt: `R = U / I` und `I = U / R`. Die Einheiten passen dabei immer zusammen: 1 V / 1 A = 1 Ω.
**Beispiel LED-Vorwiderstand:** Eine rote LED soll an 5 V mit 20 mA leuchten. An der LED selbst fallen etwa 2 V ab (Wert aus dem Datenblatt). Für den Widerstand bleiben also 5 V − 2 V = 3 V.
- `R = U / I = 3 V / 0.02 A = 150 Ω` – 150 Ω gibt es als Normwert (E12).
- `P = U · I = 3 V · 0.02 A = 60 mW` – ein 1/4-W-Widerstand (250 mW) hat genug Reserve.
**Die Leistung nie vergessen:** `P = U · I = I² · R = U² / R`. Ein 1-kΩ-Widerstand an 12 V führt 12 mA und setzt **144 mW** in Wärme um. Ein 1/4-W-Typ wäre damit zu knapp 60 % ausgelastet und wird spürbar warm – ein 0.5-W-Typ ist hier die sichere Wahl.
## Reihen- und Parallelschaltung
- **Reihe:** `R = R1 + R2 + …` – durch alle fliesst **derselbe Strom**, der Gesamtwiderstand ist immer **grösser** als der grösste Einzelwiderstand. Beispiel: 1 kΩ + 1 kΩ = 2 kΩ.
- **Parallel:** `1/R = 1/R1 + 1/R2 + …` – an allen liegt **dieselbe Spannung**, der Gesamtwiderstand ist immer **kleiner** als der kleinste. Für zwei Widerstände: `R = R1 · R2 / (R1 + R2)`.
- Zwei gleiche parallel ergeben den **halben Wert**: 1 kΩ ∥ 1 kΩ = 500 Ω. Und 100 Ω ∥ 1 kΩ = 90.9 Ω – tatsächlich kleiner als 100 Ω.
## Spannungsteiler
Zwei Widerstände in Reihe teilen eine Spannung im Verhältnis ihrer Werte: `Ua = Ue · R2 / (R1 + R2)`.
**Beispiel:** 10 V mit R1 = 30 kΩ und R2 = 10 kΩ ergibt Ua = 10 V · 10 / 40 = **2.5 V**.
Das gilt aber nur **unbelastet**! Hängt am Ausgang eine Last, liegt sie parallel zu R2. Eine Last von 10 kΩ macht aus R2 zusammen 5 kΩ – die Spannung fällt auf **1.43 V**, also fast 43 % weniger. Faustregel: Der Querstrom durch den Teiler soll mindestens **10× grösser** sein als der Laststrom.
## Wovon hängt der Widerstandswert ab?
`R = ρ · l / A` – der Widerstand steigt mit der **Länge** l, sinkt mit dem **Querschnitt** A und hängt vom **Material** ab (spezifischer Widerstand ρ). Darum haben auch Kabel einen Widerstand:
**Beispiel:** Ein Verbraucher hängt an 10 m Kupferkabel mit 1.5 mm². Der Strom fliesst hin und zurück, also durch 20 m Leitung: R ≈ **0.24 Ω**. Bei 10 A fallen dort 2.4 V ab, und die Leitung erzeugt rund 24 W Wärme.
Ausserdem ändert sich der Widerstand mit der **Temperatur**. Bei Metallen steigt er, bei Kupfer um etwa **0.4 % pro Kelvin**. Eine Kupferwicklung mit 10 Ω bei 20 °C hat bei 80 °C rund **12.3 Ω** (+23 %).
## 🔬 Genauer hingeschaut
- **Toleranz und Normreihen:** Kein Widerstand hat exakt seinen Nennwert. Die E-Reihen (E12, E24, E96 …) sind so gestuft, dass die Toleranzbereiche benachbarter Werte ungefähr aneinander anschliessen – mehr Werte pro Dekade lohnen sich nur bei kleinerer Toleranz.
- **Belastbarkeit und Derating:** Die Nennleistung gilt meist nur bis etwa **70 °C Umgebungstemperatur**. Darüber muss die Leistung reduziert werden – wie stark, zeigt die Derating-Kurve im Datenblatt.
- **Grenzspannung:** Auch wenn die Leistung passt, darf die Spannung am Bauteil einen Höchstwert nicht überschreiten. Das betrifft vor allem kleine SMD-Bauformen.
- **Temperaturkoeffizient (TK):** Angabe in ppm/K. 100 ppm/K = 0.01 % pro Kelvin – bei 50 K Erwärmung ändert sich der Wert also um 0.5 %. Für Messschaltungen gibt es Typen mit wenigen ppm/K.
- **Rauschen:** Jeder Widerstand erzeugt eine winzige Rauschspannung (thermisches Rauschen): `U = √(4 · k · T · R · B)` mit k = 1.38 · 10⁻²³ J/K, Temperatur T in Kelvin und Bandbreite B. Bei 1 MΩ, 10 kHz und 27 °C sind das rund **13 µV**, bei 1 kΩ nur 0.4 µV. Deshalb arbeitet man in empfindlichen Messschaltungen möglichst niederohmig.
- **Kein Bauteil ist ideal:** Ein echter Widerstand hat zusätzlich etwas Induktivität (Anschlussdrähte, bei Drahtwiderständen die ganze Wicklung) und Kapazität. Bei Gleichstrom spielt das keine Rolle, bei hohen Frequenzen und schnellen Schaltflanken schon.
## In der Praxis
- **Wert erkennen:** Bedrahtete Widerstände (THT) tragen Farbringe, SMD-Widerstände einen Zahlencode – beides entschlüsseln die Rechner unten.
- **Messen:** Mit dem Multimeter im Ω-Bereich, immer **spannungsfrei**. In der Schaltung verfälschen parallele Bauteile das Ergebnis – im Zweifel ein Bein auslöten.
- **Auswählen:** Wert aus der E-Reihe, Toleranz (heute meist 1 %), Leistung mit Reserve (höchstens 50–60 % der Nennleistung nutzen), Grenzspannung und Bauform.
## 💡 Wusstest du?
- Das Ohm'sche Gesetz ist nach **Georg Simon Ohm** benannt, der den Zusammenhang 1827 veröffentlichte.
- Der Farbcode auf bedrahteten Widerständen ist international genormt (**IEC 60062**) – derselbe Code gilt auf der ganzen Welt.
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
