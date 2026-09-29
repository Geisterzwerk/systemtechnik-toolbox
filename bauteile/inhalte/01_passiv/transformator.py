# =============================================================================
# Thema: Transformator  (Kategorie: Passive Bauteile)
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner + Animation: bauteile/rechner/trafo_rechner.py, bauteile/grafiken/trafo_animation.py
# =============================================================================

THEMA = {
    "titel": "Transformator",
    "reihenfolge": 4,
    "kurz": "Setzt Wechselspannungen hoch oder herunter und trennt Stromkreise galvanisch.",
    "stichworte": ["transformator", "trafo", "transformer", "übersetzung", "windungen", "windungszahl",
                   "primär", "sekundär", "netztrafo", "ringkern", "ringkerntrafo", "trenntrafo", "spartrafo",
                   "stromwandler", "messwandler", "galvanische trennung", "leerlauf", "einschaltstrom",
                   "kurzschlussspannung", "uk", "sättigung", "wirkungsgrad", "va", "gleichrichter", "netzteil",
                   "induktion", "eisenkern", "streufeld", "sicherheitstrafo"],

    "steckbrief": {
        "symbol": "transformator",
        "zeilen": [
            ("Übersetzung", "`ü = N1/N2 = U1/U2 = I2/I1`"),
            ("Spannung", "`U2 = U1 · N2 / N1`  – mehr Windungen = mehr Spannung"),
            ("Strom", "umgekehrt: Seite mit weniger Spannung führt mehr Strom"),
            ("Leistung", "in VA (Scheinleistung), `S = U · I`, ideal gleich auf beiden Seiten"),
            ("Funktioniert nur mit", "Wechselspannung (oder gepulster Spannung)"),
            ("Wichtigste Kennwerte", "U1, U2, Nennleistung (VA), Frequenz, uk, Isolationsklasse"),
        ],
    },

    "grafiken": ["trafo_animation"],

    "erklaerung": """
## Wie funktioniert ein Transformator? (siehe Animation oben)
Ein Trafo besteht aus **zwei Spulen** auf einem gemeinsamen **Eisenkern**. Sie sind elektrisch **nicht** verbunden – die Energie wird nur über das Magnetfeld übertragen:
- **①** Die Wechselspannung U1 treibt einen Wechselstrom durch die **Primärspule**
- **②** Dieser Strom erzeugt im Eisenkern ein **Magnetfeld Φ**, das im Takt der Netzfrequenz ständig Richtung und Stärke wechselt
- **③** Der geschlossene Kern leitet dieses Feld fast verlustfrei durch die **Sekundärspule**
- **④** Weil sich das Feld dort **ständig ändert**, wird in jeder Windung eine Spannung induziert → U2
## Warum nur mit Wechselspannung?
Induziert wird nur bei einer **Änderung** des Magnetfelds. Bei Gleichspannung ist das Feld konstant → **U2 = 0** (nur beim Einschalten ein kurzer Impuls). Schlimmer noch: Die Primärspule wirkt bei Gleichstrom nur noch wie ihr kleiner Drahtwiderstand → **sehr hoher Strom, der Trafo brennt durch.** In der Animation mit dem AC/DC-Schalter ausprobieren!
## Das Übersetzungsverhältnis
Jede Windung bekommt **dieselbe Spannung** induziert. Mehr Windungen = mehr Spannung:
- `U1 / U2 = N1 / N2` → Beispiel: 230 V, N1 = 500, N2 = 50 → U2 = 23 V
- Die **Leistung bleibt (fast) gleich**: Wird die Spannung 10× kleiner, kann der Strom 10× grösser sein. Darum hat die Niederspannungsseite **dickeren Draht**.
- Auch Widerstände werden übersetzt: Eine Last erscheint auf der Primärseite mit **ü²** multipliziert (Impedanzanpassung, z.B. Audio-Übertrager).
## Galvanische Trennung
Weil Primär- und Sekundärseite nur magnetisch gekoppelt sind, gibt es **keine leitende Verbindung** zum Netz. Das ist die Grundlage für Sicherheit (Trenntrafo, Sicherheitskleinspannung) und für Messungen mit unterschiedlichem Bezugspotenzial.
## Der echte Trafo
- **Leerlaufstrom:** Auch ohne Last fliesst ein kleiner Magnetisierungsstrom (erwärmt den Kern leicht)
- **Verluste:** Kupferverluste (Drahtwiderstand, steigen mit I²) und Eisenverluste (Ummagnetisierung, Wirbelströme – deshalb ist der Kern aus dünnen, isolierten Blechen)
- **Spannung sinkt unter Last:** Im Leerlauf ist U2 höher als auf dem Typenschild (kleine Trafos teils 10–25 %!). Die Nennspannung gilt bei Nennlast.
- **Kurzschlussspannung uk:** Wie „weich“ der Trafo ist. Kleines uk → Spannung bleibt stabil, aber grosser Kurzschlussstrom.
## Frequenz und Baugrösse
Je höher die Frequenz, desto **kleiner** kann der Kern bei gleicher Leistung sein. Darum sind Schaltnetzteile (Trafo bei 50–500 kHz, Ferritkern) viel kleiner und leichter als klassische 50-Hz-Netztrafos.
""",

    "tabellen": [
        {
            "titel": "📊 Trafo-Arten",
            "kopf": ["Art", "Besonderheit", "Typischer Einsatz"],
            "zeilen": [
                ["Netztrafo (EI-Kern)", "günstig, robust, 50/60 Hz", "klassische Netzteile, Steuertrafos"],
                ["Ringkerntrafo", "kompakt, wenig Streufeld, hoher Einschaltstrom", "Audio, Netzteile höherer Leistung"],
                ["Trenntrafo", "Übersetzung 1:1, nur zur galvanischen Trennung", "Werkstatt, Medizin, Messungen am Netz"],
                ["Sicherheitstrafo", "Ausgang Kleinspannung (≤ 50 V AC), verstärkte Isolation", "Spielzeug, Steuerungen, Beleuchtung"],
                ["Spartrafo", "nur EINE Wicklung mit Anzapfung – KEINE galvanische Trennung", "Stelltrafo, Spannungsanpassung"],
                ["Stromwandler", "Primär = 1 Leiter, sekundär viele Windungen", "Strommessung (z.B. 100 A → 5 A)"],
                ["Spannungswandler", "präzise Übersetzung", "Messung in Mittel-/Hochspannung"],
                ["Schaltnetzteil-Trafo", "Ferritkern, 20 kHz … 1 MHz, sehr klein", "USB-Ladegeräte, PC-Netzteile"],
                ["Übertrager / Pulstrafo", "Signale statt Leistung, galvanisch getrennt", "Ethernet, Gate-Treiber, Audio"],
            ],
        },
        {
            "titel": "📊 Typische Wirkungsgrade",
            "kopf": ["Leistung", "Wirkungsgrad η", "Leerlauf-Überhöhung U2"],
            "zeilen": [
                ["< 10 VA", "60–75 %", "20–40 %"],
                ["10–100 VA", "75–90 %", "8–20 %"],
                ["100–1000 VA", "90–95 %", "3–8 %"],
                ["Verteiltrafo (MVA)", "> 98 %", "wenige %"],
            ],
            "hinweis": "Richtwerte für Netztrafos. Genaue Werte im Datenblatt.",
        },
    ],

    "tipps": [
        "**Leerlaufspannung ist höher:** Ein 12-V-Trafo liefert ohne Last oft 14–15 V. Nach Gleichrichtung und Elko sind das schnell **20 V** – Bauteile (Elko, Regler) darauf auslegen!",
        "**Einschaltstrom (Inrush):** Je nach Einschaltmoment sättigt der Kern kurz, der Strom kann das 10–50-fache des Nennstroms erreichen (Ringkern besonders). Darum **träge Sicherungen** oder Einschaltstrombegrenzung.",
        "**Stromwandler sekundär NIE offen betreiben!** Ohne Bürde entstehen lebensgefährliche Spannungen und der Kern überhitzt. Vor dem Abklemmen die Sekundärklemmen **kurzschliessen**.",
        "**Spartrafo trennt nicht:** Ein Stelltrafo ist meist ein Spartrafo – der Ausgang ist direkt mit dem Netz verbunden. Für Sicherheit einen Trenntrafo vorschalten.",
        "**Mit Trenntrafo am Netz messen:** Erlaubt Oszilloskop-Messungen an netzbetriebenen Schaltungen ohne Erdschleife. Achtung: Die Schaltung ist trotzdem gefährlich – nur ein Fehler weniger schützt dich.",
        "**VA ≠ W:** Die Trafoleistung gilt als Scheinleistung. Bei Gleichrichtung mit Ladeelko fliesst der Strom in kurzen Spitzen – Trafo ca. **1.5–1.8× grösser** wählen als die Gleichstromleistung.",
        "**50 Hz vs. 60 Hz:** Ein 60-Hz-Trafo an 50 Hz kann sättigen und heiss werden. Umgekehrt (50-Hz-Trafo an 60 Hz) ist unkritisch.",
        "**Wicklungssinn (Punkte im Schaltplan):** Werden zwei Sekundärwicklungen in Reihe geschaltet, müssen die Punkte richtig verbunden sein – sonst heben sich die Spannungen auf.",
        "**Trafo brummt:** Mechanisch lockere Bleche (Magnetostriktion) oder Gleichanteil im Netz. Ringkerntrafos reagieren besonders empfindlich auf DC-Anteile.",
        "**Wicklungen prüfen:** Mit dem Ohmmeter sieht man Unterbrechungen. Primär hat mehr Widerstand (dünner Draht, viele Windungen) als die Sekundärseite einer Kleinspannung. Zwischen Primär und Sekundär muss es ∞ Ω sein!",
    ],
    "fehler": [
        "Trafo an Gleichspannung angeschlossen → sehr hoher Strom, Wicklung brennt durch.",
        "Primär- und Sekundärseite verwechselt → 230 V an der 12-V-Wicklung ergäbe rechnerisch über 4000 V an der anderen Seite (praktisch sättigt der Kern sofort und der Trafo brennt durch).",
        "Leerlaufspannung nicht berücksichtigt → Elko oder Spannungsregler überlastet.",
        "Flinke Sicherung auf der Primärseite → löst beim Einschalten aus.",
        "Stromwandler bei laufender Anlage sekundär abgeklemmt.",
        "Spartrafo als Trenntrafo verwendet.",
    ],
    "siehe_auch": ["spule", "kondensator", "diode", "widerstand"],

    "rechner": ["uebersetzung", "leistung_trafo", "netzteil", "windungen", "trafo_animation"],
}
