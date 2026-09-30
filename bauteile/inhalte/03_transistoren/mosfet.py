# =============================================================================
# Thema: MOSFET  (Kategorie: Transistoren)
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner: bauteile/rechner/halbleiter_rechner.py
# =============================================================================

THEMA = {
    "titel": "MOSFET",
    "reihenfolge": 2,
    "kurz": "Spannungsgesteuerter Schalter mit sehr kleinem Widerstand – Standard für Lasten, PWM und Schaltregler.",
    "stichworte": ["mosfet", "fet", "feldeffekttransistor", "n-kanal", "p-kanal", "gate", "drain", "source",
                   "rds(on)", "rdson", "ugs", "vgs", "schwellspannung", "vgs(th)", "logic level", "logic-level",
                   "gate-ladung", "qg", "gatetreiber", "gate-treiber", "body-diode", "bodydiode", "pwm",
                   "high-side", "low-side", "verpolschutz", "irlz44n", "irf540", "ao3400", "2n7000", "bss138",
                   "esd", "igbt", "schaltverluste", "leitverluste"],

    "steckbrief": {
        "symbol": "mosfet",
        "zeilen": [
            ("Anschlüsse", "Gate (G), Drain (D), Source (S)"),
            ("Typen", "**N-Kanal** (häufiger, schaltet gegen Masse) und **P-Kanal** (schaltet gegen Plus)"),
            ("Steuerung", "**spannungsgesteuert:** Ugs öffnet den Kanal, statisch fliesst **kein** Gatestrom"),
            ("Eingeschaltet", "wirkt wie ein kleiner Widerstand **Rds(on)** (mΩ-Bereich)"),
            ("Verlust", "`P = I² · Rds(on)` (+ Schaltverluste bei PWM)"),
            ("Eingebaut", "eine **Body-Diode** von Source nach Drain (N-Kanal)"),
            ("Wichtigste Kennwerte", "Uds,max, Id, Rds(on) **bei welcher Ugs**, Ugs(th), Ugs,max, Qg"),
        ],
    },

    "grafiken": ["mosfet_simulator"],

    "erklaerung": """
## Was macht ein MOSFET?
Ein MOSFET ist ein **spannungsgesteuerter Schalter**. Das Gate ist durch eine hauchdünne Oxidschicht isoliert – es bildet mit dem Kanal einen **Kondensator**. Liegt genug Spannung zwischen Gate und Source (**Ugs**), entsteht ein leitender Kanal zwischen Drain und Source. Solange sich Ugs nicht ändert, fliesst **kein Gatestrom**.
## Die drei Zustände (siehe Simulator oben)
- **Sperren:** Ugs unter der Schwellspannung **Ugs(th)** → Schalter offen.
- **Übergangsbereich:** Der Kanal ist nur teilweise offen. Der MOSFET begrenzt den Strom, an ihm fällt Spannung ab → er wird **heiss**. Diesen Bereich beim Schalten nur **kurz durchlaufen**!
- **Voll durchgeschaltet:** Ugs deutlich über der Schwelle → der MOSFET wirkt wie ein kleiner Widerstand **Rds(on)**, fast verlustfrei.
## Die wichtigste Falle: Ugs(th)
**Ugs(th) ist NICHT die Spannung, bei der der MOSFET voll durchschaltet!** Bei Ugs(th) fliesst nur ein winziger Strom (z.B. 250 µA). Voll offen ist er erst bei der Spannung, für die **Rds(on)** im Datenblatt angegeben ist – oft 10 V. Für 3.3-V- oder 5-V-Mikrocontroller braucht es **Logic-Level-MOSFETs** mit Rds(on)-Angabe bei 4.5 V oder 2.5 V.
## Das Gate ist ein Kondensator
Beim Schalten muss die **Gate-Ladung Qg** umgeladen werden. Je schneller, desto grösser der Strom (`Ig = Qg / t`). Bei hoher PWM-Frequenz reicht ein µC-Pin nicht mehr – dann braucht es einen **Gate-Treiber**. Ein kleiner **Gate-Widerstand** (ca. 10–100 Ω) dämpft Schwingungen, ein **Pull-down** (ca. 10–100 kΩ Gate→Source) sorgt dafür, dass der MOSFET beim Start sicher aus ist.
## Die Body-Diode
Jeder normale MOSFET hat eine eingebaute Diode (beim N-Kanal von Source nach Drain). Er sperrt deshalb nur in **einer** Richtung. Sie ist praktisch (Freilauf in H-Brücken), kann aber stören – z.B. wenn man eine Batterie abtrennen will.
## Verluste
- **Leitverluste:** `P = I² · Rds(on)` – Achtung: Rds(on) steigt mit der Temperatur (heiss ca. 1.5–2 × grösser)
- **Schaltverluste:** bei jedem Umschalten durchläuft er kurz den Übergangsbereich. Bei hoher PWM-Frequenz können sie grösser sein als die Leitverluste.
## N-Kanal oder P-Kanal?
- **N-Kanal, Low-Side** (Last an +Ub, Source an Masse): einfach anzusteuern, kleines Rds(on) → Standard
- **P-Kanal, High-Side** (Source an +Ub): einfach, wenn die Ansteuerspannung = Ub ist; Rds(on) meist grösser
- **N-Kanal, High-Side:** braucht eine Gate-Spannung **über** +Ub → Gate-Treiber mit Bootstrap / Ladungspumpe
## IGBT
Ein IGBT kombiniert MOSFET-Ansteuerung (Spannung am Gate) mit einem bipolaren Ausgang. Er ist gut bei **hohen Spannungen** (> 600 V) und grossen Strömen (Frequenzumrichter, Induktionsherd), aber langsamer als ein MOSFET.
## 📚 Vertiefung
Zastrow, *Elektronik*: Kapitel 1.4 (Halbleiter-Kanäle), Kapitel 4 (Feldeffekttransistor J-FET), Kapitel 8 (Analogschalter, Leistungsschalter), Kapitel 12.5 (Schaltregler).
""",

    "tabellen": [
        {
            "titel": "📊 Häufige Typen",
            "kopf": ["Typ", "Kanal", "Uds max", "Rds(on)", "Logic Level?", "Einsatz"],
            "zeilen": [
                ["2N7000 / BS170", "N", "60 V", "≈ 2–5 Ω", "teilweise", "Kleinsignal, Pegelwandler"],
                ["BSS138", "N (SMD)", "50 V", "≈ 1–3 Ω", "ja", "Pegelwandler I²C 3.3 ↔ 5 V"],
                ["AO3400", "N (SMD)", "30 V", "≈ 30–50 mΩ", "ja (2.5 V)", "LED-Streifen, kleine Motoren"],
                ["IRLZ44N", "N", "55 V", "≈ 25 mΩ @ 5 V", "✅ ja", "Arduino-Projekte, Motoren"],
                ["IRF540N", "N", "100 V", "≈ 44 mΩ @ 10 V", "❌ nein", "nur mit 10-V-Ansteuerung"],
                ["IRF9540N", "P", "−100 V", "≈ 0.12 Ω @ −10 V", "❌ nein", "High-Side-Schalter"],
            ],
            "hinweis": "Grobe Richtwerte. Entscheidend ist **bei welcher Ugs** Rds(on) angegeben ist – ein „L“ im Namen (IRLZ…) steht oft für Logic Level, aber immer das Datenblatt prüfen.",
        },
        {
            "titel": "📊 Datenblatt-Kennwerte",
            "kopf": ["Kürzel", "Bedeutung", "Worauf achten"],
            "zeilen": [
                ["Uds,max (V_DSS)", "maximale Drain-Source-Spannung", "mit Reserve wegen Spannungsspitzen"],
                ["Id", "maximaler Drainstrom", "gilt oft bei 25 °C Gehäuse – unrealistisch"],
                ["Rds(on)", "Widerstand eingeschaltet", "bei welcher Ugs und Temperatur?"],
                ["Ugs(th) / V_GS(th)", "Schwellspannung", "NICHT die Einschaltspannung!"],
                ["Ugs,max", "maximale Gate-Spannung (oft ±20 V)", "Überschreiten zerstört das Oxid"],
                ["Qg", "gesamte Gate-Ladung", "bestimmt Treiberstrom und Schaltzeit"],
                ["Rth,JC", "Wärmewiderstand Chip → Gehäuse", "für den Kühlkörper-Rechner"],
            ],
        },
    ],

    "tipps": [
        "**Rds(on) immer bei deiner Gate-Spannung lesen.** Ein IRF540N an 5 V vom Arduino ist nur halb offen und wird heiss – obwohl Ugs(th) mit 2–4 V „passt“.",
        "**Pull-down am Gate** (10–100 kΩ Gate→Source): Ein offenes Gate „fängt“ Ladung ein und der MOSFET schaltet zufällig ein – oft genau beim Einschalten.",
        "**ESD-empfindlich:** Das dünne Gate-Oxid verträgt kaum Überspannung. Nicht am Gate anfassen, Erdungsarmband benutzen, Gates nie offen lassen.",
        "**Rds(on) steigt mit der Temperatur** – dadurch teilen sich parallel geschaltete MOSFETs den Strom von selbst recht gut auf (anders als Bipolartransistoren).",
        "**Freilaufdiode trotz Body-Diode:** Bei Low-Side-Schaltern mit induktiver Last trotzdem eine Freilaufdiode über die Last, die Body-Diode liegt am falschen Ort.",
        "**P-MOSFET als Verpolschutz:** In die Plus-Leitung (Drain zur Quelle, Source zur Last, Gate über Widerstand an Masse) – fast kein Spannungsverlust, viel besser als eine Diode.",
        "**Kurze Gate-Leitungen:** Lange Leitungen zum Gate + schnelle Flanken = Schwingungen. Gate-Widerstand direkt am MOSFET.",
        "**MOSFET messen:** Im Diodentest zeigt S→D die Body-Diode (ca. 0.5 V). Gate kurz mit Plus berühren → D-S leitet (Gate bleibt geladen), Gate mit Source kurzschliessen → sperrt wieder.",
    ],
    "fehler": [
        "Nach Ugs(th) ausgewählt statt nach Rds(on) bei der vorhandenen Gate-Spannung.",
        "Gate ohne Pull-down → MOSFET schaltet beim Einschalten der Versorgung kurz oder dauernd ein.",
        "N-Kanal-MOSFET als High-Side-Schalter direkt vom µC angesteuert → er öffnet nie richtig (Gate müsste über +Ub liegen).",
        "Id aus dem Datenblatt ohne Kühlung ausgenutzt – der Wert gilt meist bei idealer Kühlung.",
        "Gate direkt an einen langsamen Treiber bei hoher PWM-Frequenz → MOSFET hängt lange im Übergangsbereich, wird heiss.",
    ],
    "siehe_auch": ["bipolartransistor", "diode", "led", "spule", "widerstand"],

    "rechner": ["mosfet_simulator", "mosfet_verlust", "mosfet_gate", "kuehlkoerper"],
}
