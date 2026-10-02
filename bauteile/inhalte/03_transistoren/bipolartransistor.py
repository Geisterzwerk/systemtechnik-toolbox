# =============================================================================
# Thema: Bipolartransistor  (Kategorie: Transistoren)
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner: bauteile/rechner/halbleiter_rechner.py
# =============================================================================

THEMA = {
    "titel": "Bipolartransistor",
    "reihenfolge": 1,
    "kurz": "Ein kleiner Basisstrom steuert einen grossen Kollektorstrom – zum Schalten und zum Verstärken.",
    "stichworte": ["transistor", "bipolartransistor", "bjt", "npn", "pnp", "basis", "kollektor", "emitter",
                   "stromverstärkung", "beta", "hfe", "basiswiderstand", "sättigung", "übersteuerung",
                   "schalter", "verstärker", "emitterschaltung", "kollektorschaltung", "emitterfolger",
                   "arbeitspunkt", "gegenkopplung", "bc547", "bc557", "bd139", "2n2222", "darlington",
                   "vce", "uce", "ube", "high-side", "low-side"],

    "steckbrief": {
        "symbol": "bipolartransistor",
        "zeilen": [
            ("Anschlüsse", "Basis (B), Kollektor (C), Emitter (E)"),
            ("Typen", "**NPN** (häufiger, schaltet gegen Masse) und **PNP** (schaltet gegen Plus)"),
            ("Steuerung", "**stromgesteuert:** Basisstrom Ib steuert Kollektorstrom Ic"),
            ("Grundgleichung", "`Ic = β · Ib`   (β = hFE, typisch 50 … 500)"),
            ("Ube", "ca. **0.7 V** (Silizium), sobald der Transistor leitet"),
            ("Voll durchgeschaltet", "Uce,sat ≈ 0.1 … 0.3 V (Sättigung)"),
            ("Wichtigste Kennwerte", "Ic,max, Uce,max, Ptot, hFE (Minimum!), Uce,sat"),
        ],
    },

    "grafiken": ["transistor_simulator"],

    "erklaerung": """
## Was macht ein Transistor?
Ein Bipolartransistor ist ein **stromgesteuertes Ventil**: Ein kleiner Strom in die **Basis** öffnet einen viel grösseren Strom vom **Kollektor** zum **Emitter**. Das Verhältnis heisst **Stromverstärkung β** (im Datenblatt **hFE**): `Ic = β · Ib`. Mit β = 100 steuert 1 mA Basisstrom bis zu 100 mA Kollektorstrom.
## Aufbau in Kurzform
Drei Halbleiterschichten: **NPN** oder **PNP**. Zwischen Basis und Emitter liegt ein pn-Übergang wie bei einer Diode – deshalb braucht es ca. **0.7 V** an der Basis, bevor überhaupt etwas passiert. Die Basisschicht ist sehr dünn: Die meisten Ladungsträger, die vom Emitter kommen, „fliegen“ durch sie hindurch zum Kollektor.
## Die drei Betriebszustände (siehe Simulator oben)
- **Sperren:** Ube < ca. 0.6 V → kein Basisstrom → kein Kollektorstrom. Schalter **offen**.
- **Aktiver Bereich (Verstärker):** Ic = β · Ib. Der Transistor „bremst“ den Strom und an ihm fällt eine grosse Spannung ab → er wird **warm**. Hier arbeiten Verstärker.
- **Sättigung (Übersteuerung):** Der Basisstrom ist grösser als nötig. Die Last begrenzt den Strom, am Transistor bleiben nur ca. 0.2 V. Schalter **zu**, kaum Verlust.
## Transistor als Schalter
Für einen sauberen Schalter will man **nur Sperren oder Sättigung** – nie den Bereich dazwischen, sonst wird der Transistor heiss.
- Laststrom Ic bestimmen, **β_min** aus dem Datenblatt nehmen (β streut stark!)
- `Ib = k · Ic / β_min` mit **Übersteuerungsfaktor k ≈ 2 … 5** (Sicherheit, dass er sicher sättigt)
- `Rb = (Ue − 0.7 V) / Ib` → nächst **kleineren** Normwert wählen
## Transistor als Verstärker
Im aktiven Bereich wird eine kleine Signaländerung an der Basis zu einer grossen Änderung am Kollektor. Dazu braucht der Transistor einen **Arbeitspunkt** in der Mitte (z.B. Uce ≈ Ub/2), eingestellt mit einem **Basis-Spannungsteiler**.
- **Problem:** β und Ube ändern sich mit Temperatur und von Exemplar zu Exemplar.
- **Lösung:** Emitterwiderstand **Re** = Gegenkopplung. Steigt der Strom, steigt die Spannung an Re, dadurch sinkt Ube – der Transistor bremst sich selbst. Die Verstärkung wird dann ungefähr `Vu ≈ −Rc/Re` und hängt nicht mehr von β ab.
## Grundschaltungen
- **Emitterschaltung:** Spannungs- und Stromverstärkung, invertiert – die klassische Verstärkerstufe
- **Kollektorschaltung (Emitterfolger):** Spannungsverstärkung ≈ 1, aber grosser Strom → Impedanzwandler, Längsregler
- **Basisschaltung:** für hohe Frequenzen
## 📚 Vertiefung
Zastrow, *Elektronik*: Kapitel 5 (Signalverstärkung mit Transistoren, Strom- und Spannungssteuerung, Arbeitspunktstabilisierung), Kapitel 8 (Schalten, Binärinverter, Leistungsschalter), Kapitel 12 (Emitterfolger als Längsregler).
""",

    "tabellen": [
        {
            "titel": "📊 Häufige Typen",
            "kopf": ["Typ", "Art", "Ic max", "Uce max", "Einsatz"],
            "zeilen": [
                ["BC547 / BC548", "NPN", "100 mA", "45 / 30 V", "Kleinsignal, kleine Lasten"],
                ["BC557 / BC558", "PNP", "100 mA", "45 / 30 V", "Gegenstück zu BC547"],
                ["2N2222 / PN2222", "NPN", "600–800 mA", "30–40 V", "Relais, LED-Gruppen"],
                ["BC337", "NPN", "800 mA", "45 V", "Schalten mittlerer Lasten"],
                ["BD139 / BD140", "NPN / PNP", "1.5 A", "80 V", "Leistung mit Kühlkörper"],
                ["TIP120", "NPN-Darlington", "5 A", "60 V", "hohe Verstärkung, aber Uce,sat ≈ 1–2 V"],
            ],
            "hinweis": "Grobe Richtwerte, je nach Hersteller verschieden. **Die Pinbelegung (E-B-C) ist je nach Typ und Gehäuse unterschiedlich – immer im Datenblatt nachsehen!**",
        },
        {
            "titel": "📊 Bipolartransistor oder MOSFET?",
            "kopf": ["Kriterium", "Bipolartransistor", "MOSFET"],
            "zeilen": [
                ["Steuerung", "Strom (Ib)", "Spannung (Ugs), statisch kein Strom"],
                ["Verlust eingeschaltet", "Uce,sat · Ic (≈ 0.2 V · I)", "I² · Rds(on) (bei grossen Strömen viel kleiner)"],
                ["Kleine Lasten, günstig", "✅ ideal", "✅ auch gut"],
                ["Grosse Ströme (> 1 A)", "braucht viel Basisstrom", "✅ ideal"],
                ["Analoge Verstärker", "✅ klassisch", "möglich, eher in ICs"],
                ["Empfindlichkeit", "robust", "Gate ESD-empfindlich"],
            ],
        },
    ],

    "tipps": [
        "**Immer mit β_min rechnen:** β streut stark zwischen Exemplaren (z.B. 110 … 800 beim BC547B). Wer mit dem typischen Wert rechnet, hat irgendwann einen Transistor, der nicht voll durchschaltet.",
        "**Basiswiderstand nie weglassen:** Die Basis-Emitter-Strecke ist eine Diode. Direkt an 5 V fliesst ein riesiger Basisstrom → Transistor oder µC-Pin defekt.",
        "**NPN = Low-Side:** Last zwischen +Ub und Kollektor, Emitter an Masse. Für High-Side (Last an Masse) braucht man einen **PNP** – und dessen Basis muss auf fast +Ub gezogen werden, um ihn auszuschalten.",
        "**Pull-down an der Basis** (z.B. 10–100 kΩ nach Masse) sorgt dafür, dass der Transistor sicher sperrt, wenn der Ansteuerpin beim Start noch hochohmig ist.",
        "**Sättigung macht langsam:** Ein stark übersteuerter Transistor braucht länger zum Abschalten (Ladungsspeicherung). Für schnelle PWM: nicht zu stark übersteuern oder MOSFET verwenden.",
        "**Darlington nur, wenn nötig:** Riesige Verstärkung, aber Uce,sat ist 1–2 V → mehr Wärme als ein einzelner Transistor oder MOSFET.",
        "**Transistor messen:** Im Diodentest zeigen B→E und B→C je ca. 0.6–0.7 V (NPN), alle anderen Richtungen „OL“. C↔E niederohmig = defekt.",
        "**Emitterfolger als einfacher Regler:** Z-Diode an die Basis, Last am Emitter → Ausgang ≈ Uz − 0.7 V mit viel mehr Strom als die Z-Diode allein.",
    ],
    "fehler": [
        "Mit β typisch statt β_min gerechnet → Transistor im aktiven Bereich, wird heiss.",
        "Kein Basiswiderstand → Basis-Emitter-Strecke oder Ansteuerpin zerstört.",
        "Induktive Last (Relais, Motor) ohne Freilaufdiode → Transistor stirbt beim Abschalten.",
        "PNP mit 3.3 V vom µC an einer 12-V-Last abschalten wollen → er bleibt immer leitend (Basis nie nahe genug an +Ub).",
        "Pinbelegung geraten – BC547 und 2N2222 haben z.B. unterschiedliche Anordnungen je nach Gehäuse.",
    ],
    "siehe_auch": ["mosfet", "diode", "z_diode", "led", "relais", "widerstand", "spule"],

    "rechner": ["transistor_simulator", "bjt_schalter", "bjt_arbeitspunkt", "kuehlkoerper",
                # Zusatz-Rechner -> rechner/transistor_rechner.py (PNP, Schaltzustand, PWM-Verluste)
                "basiswiderstand", "arbeitspunkt", "verlustleistung"],
}
