# =============================================================================
# Thema: Relais  (Kategorie: Leistung & Schalten)
# -----------------------------------------------------------------------------
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner:        bauteile/rechner/relais_rechner.py
# Rechenlogik:    bauteile/rechner/relais_mathe.py (nutzt transistor_mathe.py)
# Schaltzeichen:  bauteile/grafiken/symbole.py  ("relais")
# =============================================================================

THEMA = {
    "titel": "Relais",
    "reihenfolge": 1,
    "kurz": "Elektromagnetischer Schalter: kleiner Steuerstrom, galvanisch getrennt, schaltet grosse Lasten.",
    "stichworte": ["relais", "relay", "spule", "anker", "kontakt", "schliesser", "öffner", "wechsler",
                   "arbeitskontakt", "ruhekontakt", "no", "nc", "com", "spdt", "spst", "dpdt", "form a", "form c",
                   "a1", "a2", "11", "12", "14", "freilaufdiode", "freilauf", "ansprechspannung",
                   "abfallspannung", "haltespannung", "kontaktbelastung", "lichtbogen", "einschaltstrom",
                   "inrush", "schütz", "koppelrelais", "ssr", "halbleiterrelais", "reed", "bistabil",
                   "stromstoss", "selbsthaltung", "zwangsgeführt", "sicherheitsrelais", "galvanische trennung",
                   "uln2003", "prellen"],

    # ---- Steckbrief oben (Schaltzeichen aus bauteile/grafiken/symbole.py) ----
    "steckbrief": {
        "symbol": "relais",
        "zeilen": [
            ("Kennbuchstabe", "K (z.B. K1) – nach EN 81346 auch KF / QA"),
            ("Anschlüsse Spule", "A1 (+) und A2 (−)"),
            ("Kontakte", "Schliesser (NO) 13-14 · Öffner (NC) 11-12 · Wechsler 11-12-14"),
            ("Prinzip", "Strom in der Spule → Magnetfeld → Anker zieht → Kontakte schalten"),
            ("Steuerseite", "Nennspannung U_N (5, 12, 24 V DC, 230 V AC …), Spulenwiderstand, Leistung"),
            ("Lastseite", "max. Schaltstrom, Schaltspannung (AC/DC), Schaltleistung"),
            ("Vorteil", "galvanische Trennung zwischen Steuer- und Lastkreis, AC und DC schaltbar"),
        ],
    },

    "erklaerung": """
## Was macht ein Relais?
Ein Relais ist ein **elektrisch betätigter Schalter**. Ein kleiner Strom durch die **Spule** erzeugt ein Magnetfeld, das einen beweglichen **Anker** anzieht. Der Anker bewegt die **Kontakte**. Steuerkreis und Lastkreis sind dabei **galvanisch getrennt** – mit 5 V vom Mikrocontroller lassen sich so sicher 230-V-Lasten schalten.
## Aufbau
- **Spule** mit Eisenkern (Anschlüsse A1/A2) – erzeugt das Magnetfeld
- **Joch** und **Anker** – führen das Magnetfeld, der Anker bewegt sich
- **Rückstellfeder** – zieht den Anker zurück, wenn die Spule stromlos wird
- **Kontaktsatz** – Kontaktfedern mit Kontaktmaterial (AgNi, AgSnO₂ für Lasten, Gold für kleine Signale)
- **Gehäuse** – oft staubdicht oder gewaschen (RT III), bei Leiterplatten-Relais mit Mindestabständen für die Isolation
## Kontaktarten
- **Schliesser (NO, normally open, Arbeitskontakt, Form A):** offen in Ruhe, schliesst bei erregter Spule. Klemmen **13-14** (Endziffern 3-4).
- **Öffner (NC, normally closed, Ruhekontakt, Form B):** geschlossen in Ruhe, öffnet bei erregter Spule. Klemmen **11-12** bzw. **21-22** (Endziffern 1-2).
- **Wechsler (CO, changeover, Form C):** ein gemeinsamer Kontakt (**COM, 11**) liegt in Ruhe am Öffner (**12**) und wechselt zum Schliesser (**14**).
- **Mehrere Kontakte:** Die erste Ziffer zählt die Kontakte (11-14, 21-24 …). Englisch: SPST = 1 Kontakt ein/aus, SPDT = 1 Wechsler, DPDT = 2 Wechsler.
- Im Schaltplan wird ein Relais **immer in Ruhelage** (Spule stromlos) gezeichnet.
## Wichtige Kennwerte der Spule
- **Nennspannung U_N** und **Spulenwiderstand R** → Spulenstrom `I = U_N / R`, Leistung `P = U_N² / R` (typ. 0.2 … 0.5 W bei Print-Relais)
- **Ansprechspannung** (must operate): ab dieser Spannung zieht das Relais sicher an – meist **≤ 70 … 80 % von U_N** (bei 20 °C!)
- **Abfallspannung** (must release): darunter fällt es sicher ab – meist **≥ 5 … 10 % von U_N**
- **Hysterese:** Einmal angezogen, hält das Relais schon mit viel weniger Spannung (Luftspalt kleiner). Das nutzen **Sparschaltungen** (Haltestrom per PWM oder Vorwiderstand mit Elko).
- **Temperatur:** Kupfer hat **+0.39 %/K** mehr Widerstand. Eine 85 °C warme Spule braucht ca. 25 % mehr Spannung zum Anziehen – in heissen Schaltschränken kritisch.
## Wichtige Kennwerte der Kontakte
- **Max. Schaltstrom und Schaltspannung** – getrennt für **AC und DC**. Ein „10 A / 250 V AC“-Relais schafft bei DC oft nur **30 V** mit vollem Strom!
- **Schaltleistung** (VA bzw. W) und die **DC-Lastgrenzkurve** im Datenblatt
- **Einschaltstrom (Inrush):** Lampen, Netzteile und Motoren ziehen beim Einschalten ein Vielfaches des Nennstroms → Kontakte verschweissen
- **Mindestlast:** Leistungskontakte brauchen eine Mindestlast (z.B. 10 mA / 5 V), sonst bildet sich eine Fremdschicht. Für Signale (SPS-Eingänge, Messsignale) **Gold-Kontakte** nehmen.
- **Lebensdauer:** mechanisch z.B. 10 Mio. Schaltspiele, **elektrisch** unter Nennlast oft nur **100'000** – der Lichtbogen verschleisst die Kontakte.
- **Prellen:** Die Kontakte federn beim Schliessen einige ms nach → Digitaleingänge müssen **entprellen**.
## Warum DC schwieriger ist als AC
Beim Öffnen unter Last entsteht ein **Lichtbogen**. Bei AC geht der Strom 100× pro Sekunde durch null – dort erlischt der Bogen von selbst. Bei **DC** gibt es keinen Nulldurchgang: Der Bogen brennt weiter, bis der Kontaktabstand gross genug ist. Deshalb dürfen DC-Lasten über ca. 30 V nur mit stark reduziertem Strom geschaltet werden. Induktive DC-Lasten (Ventile, Schützspulen) brauchen zusätzlich eine **Schutzbeschaltung**.
## Die Freilaufdiode
Die Spule ist eine **Induktivität**. Schaltet der Transistor ab, will der Strom weiterfliessen: `u = L · di/dt` erzeugt eine Spannungsspitze von oft **über 100 V** – der Transistor schlägt durch.
- **Freilaufdiode** antiparallel zur Spule (**Kathode an A1 / Plus**): Der Strom fliesst beim Abschalten im Kreis Spule → Diode und klingt ab. Spannung am Transistor nur `U_B + 0.7 V`.
- **Nachteil:** Der Strom klingt langsam ab → das Relais **fällt verzögert ab** (einige ms länger), die Kontakte öffnen langsamer und verschleissen mehr.
- **Diode + Z-Diode** in Reihe: Die Spannung wird auf `U_B + U_Z + 0.7 V` begrenzt, der Strom klingt **viel schneller** ab. Die Z-Spannung so wählen, dass der Transistor (U_CE0) es verträgt.
- **Alternativen:** Varistor oder TVS (bei AC- und DC-Spulen), **RC-Glied** (bei AC-Spulen). Viele Koppelrelais haben die Schutzbeschaltung schon eingebaut (LED + Freilaufdiode) → dann auf die **Polarität** achten!
## Ansteuerung mit Transistor
Ein µC-Pin liefert nur wenige mA – ein Print-Relais braucht 30 … 100 mA. Dazwischen kommt ein Transistor als Low-Side-Schalter:
- `+U_B → Relaisspule → Kollektor`, Emitter an GND, Freilaufdiode parallel zur Spule
- Basiswiderstand mit Übersteuerung: `I_B = ü · I_Spule / B_min`, `R_B = (U_µC − 0.7 V) / I_B`
- **Pull-down** (10 … 100 kΩ) von der Basis nach GND, damit das Relais beim Start nicht klappert
- Viele Relais: Treiber-IC **ULN2003 / ULN2803** (7/8 Darlington-Stufen mit eingebauten Freilaufdioden, Pin COM an +U_B!)
- Beispiel: 5-V-Relais mit 70 Ω → `(5 V − 0.2 V) / 70 Ω ≈ 69 mA`. Mit 3.3 V, B_min = 100, ü = 3: `I_B ≈ 2.1 mA`, `R_B = 2.6 V / 2.1 mA ≈ 1.26 kΩ` → **1.2 kΩ**. BC547 (100 mA) ist knapp → **BC337**.
## Selbsthaltung
Klassische Steuerungsschaltung (vor allem mit Schützen): Ein **Start-Taster** (Schliesser) erregt die Spule K1, ein **Schliesser von K1 parallel zum Taster** hält den Stromkreis danach selbst geschlossen. Ein **Stopp-Taster** (Öffner) in Reihe unterbricht die Selbsthaltung. Vorteil: Nach einem Stromausfall läuft die Maschine **nicht** von selbst wieder an.
## Relais, Schütz oder Halbleiterrelais?
- **Relais:** kleine bis mittlere Lasten (bis ca. 16 A), Leiterplatte oder Koppelrelais auf der Hutschiene
- **Schütz:** Relais für grosse Leistungen (Motoren, Heizungen), mehrpolig, mit Hilfskontakten und Funkenlöschkammern
- **Halbleiterrelais (SSR):** kein Verschleiss, lautlos, sehr schnell, schaltet bei AC im Nulldurchgang. Aber: **Spannungsfall ≈ 1 … 1.5 V** → Wärme (Kühlkörper!), Leckstrom im ausgeschalteten Zustand, bei Defekt meist **durchlegiert** (bleibt ein).
""",

    "tabellen": [
        {
            "titel": "📊 Kontaktarten und Klemmenbezeichnung",
            "kopf": ["Kontakt", "Englisch", "In Ruhe", "Erregt", "Klemmen"],
            "zeilen": [
                ["Schliesser (Arbeitskontakt)", "NO, Form A, SPST-NO", "offen", "geschlossen", "13-14, 23-24 …"],
                ["Öffner (Ruhekontakt)", "NC, Form B, SPST-NC", "geschlossen", "offen", "11-12, 21-22 …"],
                ["Wechsler", "CO, Form C, SPDT", "COM–NC (11-12)", "COM–NO (11-14)", "11-12-14, 21-22-24 …"],
                ["Spule", "coil", "–", "–", "A1 (+), A2 (−)"],
            ],
            "hinweis": "Erste Ziffer = Nummer des Kontakts, zweite Ziffer = Funktion: **1-2 Öffner, 3-4 Schliesser**, beim Wechsler 1 = COM, 2 = Öffner, 4 = Schliesser.",
        },
        {
            "titel": "📊 Relaisarten",
            "kopf": ["Art", "Merkmal", "Typischer Einsatz"],
            "zeilen": [
                ["Monostabiles Relais", "fällt ohne Spulenstrom zurück (Standard)", "fast alles"],
                ["Bistabiles Relais (Latching)", "bleibt ohne Strom in der letzten Stellung, Impuls zum Umschalten", "Energie sparen, Zustand halten"],
                ["Stromstossrelais", "jeder Impuls schaltet um (ein/aus)", "Treppenhaus-/Lichtsteuerung mit Tastern"],
                ["Reed-Relais", "Glasröhrchen mit Kontaktzungen, sehr schnell, kleine Ströme", "Messtechnik, Signale"],
                ["Koppelrelais", "Hutschiene, Sockel, LED + Schutzbeschaltung", "SPS-Ausgänge verstärken / trennen"],
                ["Sicherheitsrelais", "zwangsgeführte Kontakte (Öffner und Schliesser nie gleichzeitig zu)", "Not-Halt, Schutztüren"],
                ["Schütz", "grosse Leistung, mehrpolig, Hilfskontakte", "Motoren, Heizungen"],
                ["Halbleiterrelais (SSR)", "Triac/MOSFET + Optokoppler, kein Verschleiss", "häufiges Schalten, Heizungsregelung"],
            ],
        },
        {
            "titel": "📊 Relais oder Halbleiterrelais (SSR)?",
            "kopf": ["Merkmal", "Elektromech. Relais", "Halbleiterrelais (SSR)"],
            "zeilen": [
                ["Verschleiss", "ja (Kontakte, Mechanik)", "keiner"],
                ["Schaltgeschwindigkeit", "5 … 15 ms, prellt", "µs … eine Halbwelle, prellfrei"],
                ["Verlust im EIN-Zustand", "sehr klein (mΩ Kontakt)", "≈ 1 … 1.5 V · I → Kühlkörper"],
                ["AUS-Zustand", "echt offen (Luftstrecke)", "Leckstrom (mA), keine sichere Trennung"],
                ["Typischer Defekt", "Kontakt verschweisst oder offen", "durchlegiert (bleibt EIN)"],
                ["Geräusch", "klickt", "lautlos"],
            ],
        },
        {
            "titel": "📊 Einschaltströme typischer Lasten",
            "kopf": ["Last", "Einschaltstrom", "Hinweis"],
            "zeilen": [
                ["Heizung (ohmsch)", "≈ 1 × I_N", "unkritisch"],
                ["Glühlampe / Halogen", "10 … 15 × I_N", "kalter Glühfaden hat kleinen Widerstand"],
                ["Motor", "5 … 8 × I_N", "bis er dreht; Abschalten: induktiv"],
                ["Trafo", "bis 10 … 15 × I_N", "je nach Einschaltmoment (Rush)"],
                ["LED-Treiber, Schaltnetzteil", "20 … 50 × I_N (sehr kurz)", "Ladeelko – häufigster Grund für verschweisste Kontakte"],
            ],
            "hinweis": "Für kritische Lasten Relais mit **Inrush-Angabe** (z.B. „TV-8“ oder „80 A / 20 ms“), mit vorlaufendem Wolfram-Kontakt, oder einen Einschaltstrombegrenzer (NTC) verwenden.",
        },
        {
            "titel": "📊 Schutzbeschaltung der Spule",
            "kopf": ["Beschaltung", "Spannungsspitze", "Abfallverzögerung", "Spule"],
            "zeilen": [
                ["keine", "sehr hoch (> 100 V)", "kurz", "– (Transistor stirbt)"],
                ["Freilaufdiode", "U_B + 0.7 V", "lang (Faktor 3 … 10)", "nur DC, gepolt"],
                ["Diode + Z-Diode", "U_B + U_Z + 0.7 V", "kurz", "nur DC, gepolt"],
                ["Varistor / TVS", "Klemmspannung", "kurz", "AC und DC"],
                ["RC-Glied", "gedämpft", "kurz", "vor allem AC"],
            ],
        },
    ],

    # ---- 💡 Kniffe: Dinge, die man auch nach Jahren gern vergisst ----
    "tipps": [
        "**Freilaufdiode immer** direkt an die Spule, Kathode an A1 / Plus. Ohne sie stirbt früher oder später der Transistor.",
        "Relais fällt zu langsam ab (Kontakte kleben, schmoren)? → **Z-Diode in Reihe** zur Freilaufdiode.",
        "Koppelrelais mit eingebauter LED / Diode sind **gepolt** – A1 an Plus, sonst leuchtet nichts oder die Diode schliesst kurz.",
        "Für **Signale** (SPS-Eingang, Messsignal, wenige mA) ein Relais mit **Goldkontakten** nehmen – Leistungskontakte werden bei Kleinstströmen unzuverlässig.",
        "Ein Kontakt, der einmal grosse Lasten geschaltet hat, taugt **nicht mehr** für kleine Signale (Gold ist weggebrannt).",
        "**DC-Lasten** über 30 V: DC-Lastgrenzkurve im Datenblatt prüfen – oder zwei Kontakte in Reihe schalten (doppelter Kontaktabstand).",
        "Heisser Schaltschrank? Ansprechspannung bei Spulentemperatur prüfen (Kupfer +0.39 %/K) – sonst zieht das Relais im Sommer nicht mehr an.",
        "Viele Relais an einem µC: **ULN2003/ULN2803** – Freilaufdioden sind drin, Pin **COM an +U_B** anschliessen!",
        "**Spulenstrom sparen:** Nach dem Anziehen reicht oft 40 … 60 % der Spannung (Haltespannung) – PWM oder Vorwiderstand mit parallelem Elko.",
        "Relais-Kontakte prellen einige ms → Digitaleingänge per Software oder RC-Glied **entprellen**.",
        "Relais-Spulen an AC (z.B. 230 V AC) sind anders gebaut (Kurzschlussring gegen Brummen) – nie eine DC-Spule an AC betreiben und umgekehrt.",
    ],
    "fehler": [
        "Freilaufdiode vergessen → Transistor oder Treiber-IC nach kurzer Zeit defekt.",
        "Freilaufdiode falsch herum (Anode an Plus) → Kurzschluss über die Diode, sobald der Transistor schaltet.",
        "Relais direkt an einen µC-Pin gehängt → Pin liefert zu wenig Strom (und die Abschaltspitze zerstört ihn).",
        "Nur den Nennstrom der Last angeschaut → Einschaltstrom von Lampe oder Netzteil verschweisst die Kontakte.",
        "AC-Relais-Daten für DC-Lasten verwendet → Lichtbogen, Kontakte brennen ab.",
        "Öffner und Schliesser verwechselt – im Schaltplan ist das Relais immer in **Ruhelage** gezeichnet.",
        "Mehr als 5 V auf ein 5-V-Relais aus Bequemlichkeit → Spule wird heiss, Isolation altert.",
        "Kein Pull-down an der Transistorbasis → Relais klappert beim Einschalten oder beim Flashen des µC.",
    ],
    "siehe_auch": ["bipolartransistor", "mosfet", "diode", "spule", "widerstand"],

    # ---- 🧮 Rechner (IDs aus bauteile/rechner/relais_rechner.py) ----
    "rechner": ["relais_ansteuerung", "freilauf", "relais_temperatur", "kontakt_last"],
}
