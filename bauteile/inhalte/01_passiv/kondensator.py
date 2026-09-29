# =============================================================================
# Thema: Kondensator  (Kategorie: Passive Bauteile)
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner: bauteile/rechner/kondensator_rechner.py
# =============================================================================

THEMA = {
    "titel": "Kondensator",
    "reihenfolge": 2,
    "kurz": "Speichert Ladung im elektrischen Feld – puffert, glättet, entstört, filtert und bestimmt Zeiten.",
    "stichworte": ["kondensator", "capacitor", "kapazität", "farad", "elko", "elektrolyt", "keramik", "mlcc",
                   "folienkondensator", "tantal", "superkondensator", "goldcap", "rc", "rc-glied", "tau",
                   "zeitkonstante", "laden", "entladen", "ladekurve", "blindwiderstand", "xc", "filter",
                   "tiefpass", "hochpass", "grenzfrequenz", "abblockkondensator", "entkopplung", "100nf",
                   "esr", "dc-bias", "x7r", "c0g", "np0", "x2", "y-kondensator", "104", "glättung", "welligkeit"],

    "steckbrief": {
        "symbol": "kondensator",
        "zeilen": [
            ("Formelzeichen", "C"),
            ("Einheit", "Farad (F)  ·  meist pF, nF, µF  ·  1 µF = 1000 nF = 1'000'000 pF"),
            ("Grundformel", "`Q = C · U`   (Ladung = Kapazität × Spannung)"),
            ("Strom", "`i = C · du/dt`  – Strom fliesst nur, wenn sich die Spannung ÄNDERT"),
            ("Zeitkonstante", "`τ = R · C`  – nach 5τ gilt er als voll geladen"),
            ("Energie", "`W = ½ · C · U²`"),
            ("Wechselstrom", "`Xc = 1 / (2π · f · C)`  – Strom eilt der Spannung 90° voraus"),
            ("Polung", "Keramik/Folie: egal  ·  Elko/Tantal: gepolt, + beachten!"),
        ],
    },

    "grafiken": ["rc_ladekurve"],

    "erklaerung": """
## Was macht ein Kondensator?
Ein Kondensator besteht aus **zwei leitenden Platten**, getrennt durch einen Isolator (**Dielektrikum**). Legt man eine Spannung an, sammeln sich auf der einen Platte positive, auf der anderen negative Ladungen. Zwischen den Platten entsteht ein elektrisches Feld – darin steckt die gespeicherte Energie. **Gleichstrom kann nicht hindurchfliessen** – es fliesst nur so lange Strom, bis der Kondensator geladen ist.
## Die wichtigste Regel
Ein Kondensator **wehrt sich gegen schnelle Spannungsänderungen**: `i = C · du/dt`. Die Spannung an einem Kondensator kann nicht springen. Daraus folgt fast alles:
- **Gleichspannung** (du/dt = 0) → kein Strom → wirkt wie eine **Unterbrechung**
- **Wechselspannung** → Strom fliesst, umso mehr je höher die Frequenz → bei hohen Frequenzen wirkt er fast wie ein **Kurzschluss**
- Im ersten Moment beim Einschalten ist ein leerer Kondensator ein **Kurzschluss** → hoher Einschaltstrom
## Laden und Entladen (RC-Glied)
Über einen Widerstand geladen, steigt die Spannung **nicht linear**, sondern nach einer e-Funktion (siehe Kurve oben):
- Nach **1 τ** (τ = R · C) ist er zu **63 %** geladen
- Nach **5 τ** zu **99.3 %** → gilt als voll
- Beim Entladen genau umgekehrt: nach 1 τ sind noch **37 %** übrig
- Merkhilfe: Die Tangente am Anfang der Kurve trifft den Endwert genau bei **1 τ**
## Wofür braucht man ihn?
- **Abblocken / Entkoppeln:** 100 nF direkt an jedem IC fängt kurze Stromspitzen ab
- **Glätten:** Elko nach dem Gleichrichter macht aus pulsierender Gleichspannung eine (fast) glatte
- **Puffern:** Energie für kurze Spannungseinbrüche bereitstellen
- **Filtern:** RC-Tiefpass/-Hochpass, Entstörung (X/Y-Kondensatoren am Netz)
- **Koppeln:** Wechselanteil weiterleiten, Gleichanteil sperren (z.B. Audio)
- **Zeitglieder:** Verzögerungen, Oszillatoren (555-Timer), Reset-Schaltungen
## Wovon hängt die Kapazität ab?
`C = ε0 · εr · A / d` – grössere **Plattenfläche** A und kleinerer **Abstand** d ergeben mehr Kapazität, ebenso ein Dielektrikum mit grossem **εr**. Deshalb haben Elkos (sehr dünne Oxidschicht) viel Kapazität auf kleinem Raum.
## Reihen- und Parallelschaltung – umgekehrt wie beim Widerstand!
- **Parallel:** `C = C1 + C2 + …` – Kapazitäten addieren sich (mehr Plattenfläche)
- **Reihe:** `1/C = 1/C1 + 1/C2 + …` – kleiner als der kleinste. Die Spannung teilt sich **umgekehrt** zu C auf.
## Der echte Kondensator
Ein realer Kondensator hat neben C auch einen Serienwiderstand (**ESR**) und eine Serieninduktivität (**ESL**). Deshalb wirkt er nur bis zu seiner **Eigenresonanzfrequenz** als Kondensator – darüber verhält er sich wie eine Spule. Darum kombiniert man oft einen grossen Elko mit einem kleinen 100-nF-Keramik-Kondensator.
""",

    "tabellen": [
        {
            "titel": "📊 Kondensator-Arten",
            "kopf": ["Art", "Bereich", "Eigenschaften", "Typischer Einsatz"],
            "zeilen": [
                ["Keramik C0G / NP0", "pF … ~100 nF", "sehr stabil, kaum Temperatur-/Spannungseinfluss", "Filter, Oszillatoren, Präzision"],
                ["Keramik X7R / X5R", "nF … einige µF", "günstig, klein, ABER Kapazität sinkt mit Gleichspannung", "Abblocken, Entkoppeln (Standard)"],
                ["Keramik Y5V / Z5U", "nF … µF", "stark temperatur-/spannungsabhängig (−80 %!)", "unkritische Anwendungen – eher meiden"],
                ["Folie (PP, PET)", "nF … µF", "stabil, spannungsfest, selbstheilend", "Audio, Netzfilter (X2), Snubber"],
                ["Aluminium-Elko", "µF … F", "viel C, günstig, gepolt, altert, hoher ESR", "Glätten, Puffern, Netzteile"],
                ["Polymer-Elko", "µF … mF", "sehr kleiner ESR, langlebiger, teurer", "Schaltregler, Mainboards"],
                ["Tantal", "µF … einige 100 µF", "klein, stabil, gepolt, empfindlich auf Überspannung/Stromstösse", "kompakte Elektronik"],
                ["Superkondensator", "0.1 … 3000 F", "riesige Kapazität, nur ca. 2.7 V pro Zelle", "Pufferung, Echtzeituhr (RTC)"],
            ],
        },
        {
            "titel": "📊 Keramik-Klassen: Temperaturcode",
            "kopf": ["Code", "Temperaturbereich", "Kapazitätsänderung", "Bemerkung"],
            "zeilen": [
                ["C0G / NP0", "−55 … +125 °C", "±30 ppm/K (praktisch 0)", "Klasse 1 – stabil"],
                ["X7R", "−55 … +125 °C", "±15 %", "Klasse 2 – Standard"],
                ["X5R", "−55 … +85 °C", "±15 %", "Klasse 2"],
                ["Y5V", "−30 … +85 °C", "+22 / −82 %", "Klasse 2 – instabil"],
            ],
            "hinweis": "Der Code sagt NUR etwas über die Temperatur. Die Abnahme durch Gleichspannung (**DC-Bias**) kommt noch dazu und steht im Datenblatt als Kurve.",
        },
        {
            "titel": "📊 Beschriftung",
            "kopf": ["Aufdruck", "Bedeutung", "Wert"],
            "zeilen": [
                ["104", "10 × 10⁴ pF", "100 nF"],
                ["473", "47 × 10³ pF", "47 nF"],
                ["4n7 / 4.7n", "n = Komma in nF", "4.7 nF"],
                ["1u0 / 1µ", "u/µ = Komma in µF", "1 µF"],
                ["104K 100V", "K = Toleranz ±10 %, Spannung 100 V", "100 nF"],
                ["Toleranzbuchstaben", "F ±1 %, G ±2 %, J ±5 %, K ±10 %, M ±20 %, Z +80/−20 %", ""],
                ["Elko-Streifen", "Streifen mit „−“ = MINUS-Pol, kurzes Bein = Minus", ""],
                ["Tantal-Streifen", "Streifen = PLUS-Pol (genau umgekehrt!)", ""],
            ],
        },
        {
            "titel": "📊 Sicherheitskondensatoren am Netz",
            "kopf": ["Klasse", "Einbau", "Bei Ausfall", "Beispiel"],
            "zeilen": [
                ["X (X1, X2)", "zwischen L und N", "Kurzschluss → Sicherung löst aus", "Netzfilter, Entstörung"],
                ["Y (Y1, Y2)", "zwischen L/N und Schutzleiter PE", "darf NIE kurzschliessen (Berührungsschutz)", "Entstörung gegen Gehäuse"],
            ],
            "hinweis": "Am Netz nur zugelassene X/Y-Typen verwenden – niemals normale Kondensatoren!",
        },
    ],

    "tipps": [
        "**100 nF an jedes IC**, so nah wie möglich an die Versorgungspins (kurze Leitungen = kleine Induktivität). Bei schnellen ICs zusätzlich 1–10 µF in der Nähe.",
        "**DC-Bias bei Keramik:** Ein 10-µF-X5R-Kondensator (6.3 V) hat bei 5 V Gleichspannung oft nur noch **2–4 µF**. Bei Schaltreglern immer die DC-Bias-Kurve im Datenblatt prüfen oder grössere Bauform/Spannung wählen.",
        "**Elko-Lebensdauer:** Faustregel „10 °C kühler = doppelte Lebensdauer“. Ein Elko mit 2000 h bei 105 °C hält bei 65 °C ca. 32'000 h. Elkos nicht neben Kühlkörper setzen.",
        "**Spannungsfestigkeit mit Reserve:** Elko mind. 20–50 % über der Betriebsspannung, Tantal sogar ca. **doppelt** (sie mögen keine Spannungsspitzen und Einschaltströme).",
        "**Elkos altern auch im Lager:** Lange unbenutzte Geräte langsam hochfahren (Stelltrafo / Vorwiderstand), damit sich die Oxidschicht neu bildet.",
        "**Grosse Kondensatoren können lange geladen bleiben**, auch nach dem Ausschalten. Vor Arbeiten über einen Widerstand entladen und nachmessen – nie mit dem Schraubenzieher kurzschliessen.",
        "**Kapazität messen:** Kondensator vorher entladen und mindestens ein Bein auslöten. ESR-Meter finden defekte Elkos, die beim reinen Kapazitätsmessen noch gut aussehen.",
        "**Aufgeblähter Elko** (Deckel gewölbt, braune Rückstände) ist defekt – häufigste Ausfallursache in Netzteilen.",
        "**Keramik-Kondensatoren können „singen“** (Piezo-Effekt): Hörbares Pfeifen bei Schaltreglern kommt oft von MLCCs, nicht von der Spule.",
        "**Mehrere parallel statt einer grosser:** Zwei Kondensatoren parallel halbieren ESR und ESL – gut für Schaltregler.",
        "**Einschaltstrom:** Grosse Elkos am Eingang ziehen beim Einschalten einen hohen Stromstoss (Sicherung, Schalter, Stecker). Abhilfe: NTC, Softstart oder Vorwiderstand mit Relais.",
        "**Leckstrom:** Elkos lassen etwas Gleichstrom durch (µA-Bereich). Für lange Zeitglieder (Minuten) ungeeignet – dafür Folie oder Mikrocontroller nehmen.",
    ],
    "fehler": [
        "Elko verpolt → erwärmt sich, bläht auf, kann platzen. Minus-Streifen beachten!",
        "Tantal-Streifen als Minus gelesen – beim Tantal markiert der Streifen PLUS.",
        "Spannungsfestigkeit vergessen: 16-V-Elko an 24 V.",
        "X7R-Keramik für Filter/Zeitglieder mit genauem Wert verwendet – Kapazität ändert sich mit Temperatur UND Spannung. Dafür C0G oder Folie.",
        "Reihenschaltung von Kondensatoren gerechnet wie beim Widerstand (addiert).",
        "Abblockkondensator weit weg vom IC platziert – lange Leiterbahnen machen ihn fast wirkungslos.",
    ],
    "siehe_auch": ["widerstand", "spule", "transformator", "diode"],

    "rechner": ["rc_ladekurve", "rc_zeit", "rc_filter", "blindwiderstand_c", "energie_c",
                "reihe_parallel_c", "kondensator_code"],
}
