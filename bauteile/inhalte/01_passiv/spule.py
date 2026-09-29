# =============================================================================
# Thema: Spule  (Kategorie: Passive Bauteile)
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner: bauteile/rechner/spule_rechner.py
# =============================================================================

THEMA = {
    "titel": "Spule",
    "reihenfolge": 3,
    "kurz": "Speichert Energie im Magnetfeld – glättet Ströme, filtert Störungen und ist das Herz jedes Schaltreglers.",
    "stichworte": ["spule", "induktivität", "inductor", "drossel", "henry", "induktion", "magnetfeld",
                   "ferrit", "ringkern", "sättigung", "sättigungsstrom", "freilaufdiode", "abschaltspitze",
                   "rl", "rl-glied", "xl", "blindwiderstand", "schwingkreis", "resonanz", "lc", "gleichtaktdrossel",
                   "ferritperle", "emv", "entstörung", "lenz", "selbstinduktion", "dcr", "srf"],

    "steckbrief": {
        "symbol": "spule",
        "zeilen": [
            ("Formelzeichen", "L"),
            ("Einheit", "Henry (H)  ·  meist nH, µH, mH"),
            ("Grundformel", "`u = L · di/dt`  – Spannung entsteht nur, wenn sich der Strom ÄNDERT"),
            ("Zeitkonstante", "`τ = L / R`"),
            ("Energie", "`W = ½ · L · I²`  (im Magnetfeld)"),
            ("Wechselstrom", "`XL = 2π · f · L`  – Strom eilt der Spannung 90° nach"),
            ("Wichtige Kennwerte", "L, Sättigungsstrom Isat, Nennstrom Irms, Drahtwiderstand DCR, Eigenresonanz SRF"),
        ],
    },

    "grafiken": ["rl_kurve"],

    "erklaerung": """
## Was macht eine Spule?
Eine Spule ist ein aufgewickelter Draht, oft um einen Kern aus Eisen oder Ferrit. Fliesst Strom hindurch, entsteht ein **Magnetfeld** – darin steckt Energie. Die Spule ist das Gegenstück zum Kondensator: Sie **wehrt sich gegen schnelle Stromänderungen**.
## Die wichtigste Regel
`u = L · di/dt` – **der Strom durch eine Spule kann nicht springen.**
- **Gleichstrom** (konstant) → keine Spannung an der Spule → sie wirkt nur wie ihr **Drahtwiderstand** (fast ein Kurzschluss)
- **Wechselstrom** → sie bremst umso stärker, je höher die Frequenz (`XL` steigt)
- **Einschalten:** Der Strom steigt langsam an (e-Funktion, siehe Kurve oben)
- **Abschalten:** Die Spule will den Strom weitertreiben – wird der Stromkreis hart unterbrochen, erzeugt sie eine **sehr hohe Spannungsspitze** (Hunderte Volt aus 12 V!)
## Warum die Spannungsspitze so wichtig ist
Relaisspulen, Magnetventile, Motoren und Schütze sind Spulen. Schaltet ein Transistor sie ab, zerstört die Induktionsspitze den Transistor. Deshalb braucht jede induktive Last eine **Freilaufdiode** (oder RC-Glied / TVS / Varistor), die dem Strom einen Weg lässt, bis die Energie abgebaut ist.
## Induktion und Lenz'sche Regel
Ändert sich das Magnetfeld in einer Spule, wird darin eine Spannung **induziert**. Diese ist immer so gerichtet, dass sie ihrer Ursache **entgegenwirkt** (Lenz'sche Regel). Das ist der Grund für das „Trägheitsverhalten“ – und das Prinzip von Transformator, Generator und Induktionsherd.
## Wovon hängt die Induktivität ab?
`L ≈ µ0 · µr · N² · A / l` – die **Windungszahl geht quadratisch** ein (doppelte Windungen = vierfache Induktivität). Ein Kern mit grossem **µr** (Eisen, Ferrit) erhöht L stark.
## Sättigung – die wichtigste Grenze
Ein Kern kann nur ein begrenztes Magnetfeld aufnehmen. Wird der Strom zu gross, geht er in **Sättigung**: Die Induktivität bricht plötzlich zusammen, der Strom steigt sprunghaft. Im Schaltregler führt das zu Überstrom und defekten Bauteilen. Darum ist **Isat** im Datenblatt entscheidend.
## Wofür braucht man sie?
- **Schaltregler** (Buck/Boost): Energiespeicher zwischen den Schaltvorgängen
- **Filter / Entstörung:** Drosseln, Ferritperlen, Gleichtaktdrosseln an Kabeln
- **Schwingkreise:** zusammen mit C (Funk, Oszillatoren, NFC)
- **Aktoren:** Relais, Magnetventile, Motoren (dort ist die Spule das Bauteil selbst)
- **Sensoren:** induktive Näherungsschalter, Stromzangen
## Reihen- und Parallelschaltung
Wie beim Widerstand (solange sich die Spulen magnetisch nicht beeinflussen): Reihe addiert sich, parallel wird es kleiner.
""",

    "tabellen": [
        {
            "titel": "📊 Spulen-Arten",
            "kopf": ["Art", "Eigenschaften", "Typischer Einsatz"],
            "zeilen": [
                ["Luftspule", "kein Kern → keine Sättigung, kleine L", "HF, Schwingkreise"],
                ["Ferritkern (Stab, Trommel)", "kompakt, gut bis in den MHz-Bereich", "Schaltregler, Filter"],
                ["Geschirmte SMD-Leistungsspule", "wenig Streufeld, EMV-freundlich", "Schaltregler (Standard)"],
                ["Ringkern (Toroid)", "Feld bleibt im Kern, wenig Streuung", "Netzfilter, Leistungsdrosseln"],
                ["Eisenkern (Blech)", "grosse L, nur tiefe Frequenzen", "Netzdrosseln, 50 Hz"],
                ["Gleichtaktdrossel", "zwei Wicklungen, bremst nur Gleichtaktstörungen", "Netzfilter, USB, CAN, Ethernet"],
                ["Ferritperle", "wirkt bei HF als Widerstand (verheizt Störungen)", "Entstörung an Leitungen/IC-Versorgung"],
            ],
        },
        {
            "titel": "📊 Kondensator vs. Spule",
            "kopf": ["", "Kondensator C", "Spule L"],
            "zeilen": [
                ["Speichert Energie im", "elektrischen Feld", "magnetischen Feld"],
                ["Kann nicht springen", "die Spannung", "der Strom"],
                ["Bei Gleichstrom", "Unterbrechung (nach Aufladung)", "Kurzschluss (nur Drahtwiderstand)"],
                ["Bei hoher Frequenz", "wie Kurzschluss", "wie Unterbrechung"],
                ["Phasenlage", "Strom eilt vor (+90°)", "Strom eilt nach (−90°)"],
                ["Zeitkonstante", "τ = R · C", "τ = L / R"],
                ["Gefahr beim", "Kurzschliessen (Funken, Stromstoss)", "Abschalten (Spannungsspitze)"],
            ],
            "hinweis": "Merksatz für die Phasenlage: **„Beim Kondensator eilt der Strom vor, bei Induktivitäten wird er sich verspäten.“**",
        },
        {
            "titel": "📊 Datenblatt-Kennwerte",
            "kopf": ["Kennwert", "Bedeutung", "Worauf achten"],
            "zeilen": [
                ["L", "Nenninduktivität (meist ±20 %)", "gilt bei kleinem Strom"],
                ["Isat", "Strom, bei dem L um z.B. 30 % gesunken ist", "Spitzenstrom muss darunter bleiben!"],
                ["Irms / Nennstrom", "Strom für z.B. 40 K Erwärmung", "Effektivstrom muss darunter bleiben"],
                ["DCR", "Drahtwiderstand", "Verluste P = I² · DCR"],
                ["SRF", "Eigenresonanzfrequenz", "darüber wirkt die Spule wie ein Kondensator"],
            ],
        },
    ],

    "tipps": [
        "**Jede induktive Last braucht eine Freilaufdiode** (Relais, Ventil, Motor, Schütz) – antiparallel zur Spule, Kathode an Plus.",
        "**Isat UND Irms prüfen:** Isat für den Spitzenstrom (Sättigung), Irms für die Erwärmung. Im Schaltregler ist der Spitzenstrom = Laststrom + halbe Welligkeit.",
        "**Sättigung ist tückisch:** Eine gesättigte Spule sieht auf dem Oszilloskop wie ein Strom aus, der plötzlich steil ansteigt (Knick in der Dreieckform).",
        "**Freilaufdiode macht Relais langsam:** Das Relais fällt verzögert ab, weil der Strom langsam abklingt. Für schnelles Abschalten Z-Diode oder TVS in Reihe zur Diode.",
        "**Magnetfelder koppeln:** Ungeschirmte Spulen streuen ihr Feld und stören benachbarte Leiterbahnen/Spulen. Im Layout genug Abstand oder geschirmte Typen verwenden.",
        "**Keine Leiterbahnen unter Schaltregler-Spulen** mit empfindlichen Signalen führen.",
        "**Induktivität von Leitungen:** Jeder Draht hat ca. **1 µH pro Meter** – bei schnellen Schaltvorgängen entstehen daran Spannungsspitzen. Darum kurze Leitungen im Leistungskreis.",
        "**Multimeter misst nur den DCR**, nicht die Induktivität. Für L braucht es ein LCR-Meter. Ein Windungsschluss verändert den DCR oft kaum, senkt aber L deutlich.",
        "**Warme Kupferwicklung:** Widerstand steigt um ca. 0.4 %/K – Relaisspulen ziehen heiss weniger Strom und schalten evtl. nicht mehr sicher.",
        "**Ferrit ist temperaturempfindlich:** Isat sinkt bei hoher Temperatur – Datenblattwerte gelten meist bei 25 °C.",
    ],
    "fehler": [
        "Relais oder Magnetventil ohne Freilaufdiode am Transistor → Transistor stirbt nach einigen Schaltvorgängen.",
        "Freilaufdiode verkehrt herum eingebaut → Kurzschluss der Versorgung beim Einschalten.",
        "Spule nur nach Induktivität ausgewählt, Sättigungsstrom vergessen.",
        "Glauben, eine Spule sperre Gleichstrom – das macht der Kondensator. Die Spule lässt Gleichstrom durch.",
        "Gleichtaktdrossel verkehrt angeschlossen (beide Wicklungen gleichsinnig durchflossen) → sie wirkt dann gegen den Nutzstrom und sättigt.",
    ],
    "siehe_auch": ["kondensator", "transformator", "relais", "diode", "widerstand"],

    "rechner": ["rl_kurve", "abschaltspitze", "blindwiderstand_l", "rl_zeit", "lc_resonanz",
                "energie_l", "reihe_parallel_l"],
}
