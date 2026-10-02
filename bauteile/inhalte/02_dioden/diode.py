# =============================================================================
# Thema: Diode  (Kategorie: Dioden)
# -----------------------------------------------------------------------------
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner + Kennlinie:  bauteile/rechner/dioden_rechner.py
# Rechenlogik:          bauteile/rechner/dioden_mathe.py
# Mitbenutzt:           "led_vorwiderstand" (widerstand_rechner.py), "freilauf" (relais_rechner.py)
# Schaltzeichen:        bauteile/grafiken/symbole.py  ("dioden")
# =============================================================================

THEMA = {
    "titel": "Diode",
    "reihenfolge": 1,
    "kurz": "Lässt Strom nur in eine Richtung durch – Gleichrichter, Z-Diode, LED, Schutz- und Freilaufdiode.",
    "stichworte": ["diode", "pn-übergang", "anode", "kathode", "durchlassspannung", "sperrspannung", "uf", "urrm",
                   "gleichrichter", "graetz", "brückengleichrichter", "einweg", "mittelpunkt", "ladekondensator",
                   "brummspannung", "welligkeit", "z-diode", "zenerdiode", "zener", "stabilisierung", "referenz",
                   "led", "leuchtdiode", "vorwiderstand", "schottky", "freilaufdiode", "freilauf", "verpolschutz",
                   "tvs", "suppressor", "esd", "shockley", "kennlinie", "1n4007", "1n4148", "1n5819", "bzx55",
                   "sperrverzögerung", "trr"],

    # ---- Steckbrief oben (Schaltzeichen aus bauteile/grafiken/symbole.py) ----
    "steckbrief": {
        "symbol": "dioden",
        "zeilen": [
            ("Anschlüsse", "Anode (A) und Kathode (K) – Kathode = Ring am Gehäuse"),
            ("Durchlassrichtung", "Strom von A nach K, wenn A positiver ist (Pfeilrichtung im Symbol)"),
            ("Durchlassspannung U_F", "Si ≈ 0.7 V · Schottky ≈ 0.3 V · LED 1.8 … 3.3 V"),
            ("Sperrrichtung", "nur winziger Sperrstrom – bis zur Durchbruchspannung U_RRM"),
            ("Kennlinie", "`I = I_S · (e^(U / (n · U_T)) − 1)`   (Shockley, U_T ≈ 26 mV)"),
            ("Temperatur", "U_F sinkt um ca. 2 mV/K"),
            ("Wichtigste Grenzwerte", "I_F(AV), I_FSM (Stossstrom), U_RRM, P_tot, t_rr"),
        ],
    },

    # Interaktive Kennlinie direkt im Wissen-Teil (-> bauteile/grafiken/dioden_kennlinie.py)
    "grafiken": ["dioden_kennlinie"],

    "erklaerung": """
## Was macht eine Diode?
Eine Diode ist ein **elektrisches Ventil**: Sie lässt Strom nur in eine Richtung durch – von der **Anode** zur **Kathode**. Im Schaltzeichen zeigt das Dreieck in die Durchlassrichtung, der Balken ist die Kathode (am Bauteil der **Ring**).
## Aufbau: der pn-Übergang
Eine Diode besteht aus einem p-dotierten und einem n-dotierten Halbleiter. An der Grenze bildet sich eine **Sperrschicht** ohne freie Ladungsträger.
- **Durchlassrichtung** (Anode +): Die Sperrschicht wird abgebaut. Ab der **Schwellspannung** (Si ≈ 0.6 … 0.7 V) steigt der Strom **exponentiell** – die Spannung bleibt dann fast konstant.
- **Sperrrichtung** (Kathode +): Die Sperrschicht wird breiter, es fliesst nur ein winziger **Sperrstrom** (nA … µA). Ab der **Durchbruchspannung** steigt der Strom plötzlich stark an – bei normalen Dioden zerstörerisch, bei Z-Dioden gewollt.
## Die Kennlinie
- **Shockley-Gleichung:** `I = I_S · (e^(U / (n · U_T)) − 1)` mit `U_T = k · T / q ≈ 26 mV` bei 25 °C, n = 1 … 2
- Faustregel daraus: **10× mehr Strom → nur ca. 60 … 120 mV mehr Spannung**. Deshalb darf man in Rechnungen oft mit festen 0.7 V rechnen.
- **Temperatur:** U_F sinkt um ca. **2 mV/K**, der Sperrstrom verdoppelt sich ungefähr alle 10 K.
- **Bahnwiderstand:** Bei grossen Strömen kommt ein ohmscher Anteil dazu – U_F steigt dann linear weiter (Datenblatt-Kurve!).
## Gleichrichter
- **Einweg (M1):** eine Diode, nur eine Halbwelle wird genutzt. Brummfrequenz = `f` (50 Hz). Einfach, aber viel Brumm und der Trafo wird einseitig belastet.
- **Mittelpunkt (M2):** zwei Dioden, Trafo mit Mittelanzapfung. Beide Halbwellen, Brummfrequenz `2f`, nur **eine** Diode im Strompfad (gut bei kleinen Spannungen).
- **Brücke (B2, Graetz):** vier Dioden, beide Halbwellen, Brummfrequenz `2f`. **Zwei** Dioden im Strompfad → `2 · U_F` Verlust. Standard in Netzteilen.
- **Ladekondensator:** lädt sich auf den Spitzenwert `Û = U_eff · √2` auf und liefert dazwischen den Strom. Brummspannung `U_Br,ss ≈ I / (f_Br · C)`.
- **Achtung Spitzenströme:** Die Dioden leiten nur kurz am Scheitel der Sinuswelle (kleiner **Stromflusswinkel**) – der Spitzenstrom ist dabei 5 … 10× grösser als der Laststrom. Beim Einschalten ist der leere Elko fast ein Kurzschluss → Stossstrom I_FSM beachten.
- **Sperrspannung:** Brücke `U_RRM ≥ Û`, Einweg und Mittelpunkt mit Ladekondensator `U_RRM ≥ 2 · Û` – plus Reserve für Netzüberspannung.
## Z-Diode (Zenerdiode)
Wird bewusst in **Sperrrichtung** betrieben. Ab der Z-Spannung U_Z hält sie die Spannung nahezu konstant – der Strom durch sie darf sich stark ändern.
- **Immer mit Vorwiderstand R_V**, der die Differenzspannung aufnimmt und den Strom begrenzt.
- **Dimensionieren für zwei schlimmste Fälle:** (1) kleinste Eingangsspannung + grösster Laststrom → es muss noch **I_Z,min** fliessen. (2) grösste Eingangsspannung + Leerlauf → **P_Z = U_Z · I_Z,max** muss unter P_tot bleiben.
- **Temperaturverhalten:** unter ca. 5 V dominiert der Zener-Effekt (TK negativ), über ca. 6 V der Lawinen-Effekt (TK positiv). Um **5 … 6 V** heben sie sich auf → beste Referenz.
- **Innenwiderstand r_Z:** U_Z ändert sich trotzdem ein wenig mit dem Strom (`ΔU_Z = r_Z · ΔI_Z`). Für präzise Spannungen besser einen Referenz-IC (TL431, LM4040) oder Spannungsregler.
## LED (Leuchtdiode)
- Leuchtet in Durchlassrichtung. U_F hängt von der **Farbe** (Halbleitermaterial) ab: rot ≈ 1.8 V … blau/weiss ≈ 3 V.
- Die Helligkeit hängt vom **Strom** ab, nicht von der Spannung. Wegen der steilen Kennlinie **immer Strom begrenzen**: Vorwiderstand `R = (U_B − U_F) / I_F` oder Konstantstromquelle.
- Heutige LEDs sind schon bei 1 … 5 mA gut sichtbar – 20 mA ist oft unnötig hell.
- **Sperrspannung nur ca. 5 V!** An Wechselspannung eine antiparallele Diode dazu.
## Schottky-Diode
Metall-Halbleiter-Übergang statt pn. **Kleine U_F** (0.2 … 0.45 V) und praktisch **keine Sperrverzögerung** → schnell und verlustarm. Nachteile: grösserer Sperrstrom (steigt stark mit der Temperatur), meist kleinere Sperrspannung. Einsatz: Schaltnetzteile, Verpolschutz, Solar.
## Freilaufdiode
Antiparallel zu einer **Spule** (Relais, Motor, Magnetventil): Kathode an Plus. Beim Abschalten will der Spulenstrom weiterfliessen – ohne Diode entsteht eine hohe Spannungsspitze (`u = L · di/dt`), die den schaltenden Transistor zerstört. Mit Diode fliesst der Strom im Kreis und klingt ab. Nachteil: das Relais fällt langsamer ab → Details auf der Relais-Seite.
## Weitere Schutzdioden
- **Verpolschutz:** Diode in Reihe (einfach, kostet U_F · I Verlust – Schottky ist besser) oder Diode parallel + Sicherung (brennt bei Verpolung durch).
- **TVS-Diode (Suppressor):** wie eine sehr schnelle, robuste Z-Diode für kurze Spitzen (ESD, Burst, Surge) an Leitungen und Eingängen. Uni- oder bidirektional.
- **Klemmdioden:** zwei Dioden von einem Eingang nach GND und nach U_B begrenzen die Spannung auf `−0.7 V … U_B + 0.7 V` (in vielen ICs schon eingebaut).
## Sperrverzögerung (t_rr)
Eine leitende pn-Diode braucht beim Umschalten in Sperrrichtung kurz Zeit, bis die Ladungsträger ausgeräumt sind – solange fliesst Strom **rückwärts**. Bei 50 Hz egal, bei Schaltnetzteilen (kHz … MHz) erzeugt das Verluste und Störungen → **Fast-Recovery**- oder **Schottky**-Dioden verwenden.
""",

    "tabellen": [
        {
            "titel": "📊 Diodentypen im Überblick",
            "kopf": ["Typ", "Beispiel", "Besonderheit", "Typischer Einsatz"],
            "zeilen": [
                ["Gleichrichterdiode", "1N4007", "1 A, 1000 V, langsam (t_rr ≈ µs)", "Netzteile 50 Hz, Verpolschutz, Freilauf"],
                ["Schaltdiode", "1N4148", "300 mA, 100 V, sehr schnell (4 ns)", "Signale, Freilauf bei kleinen Relais"],
                ["Schottky", "1N5819", "U_F ≈ 0.3 V, schnell, höherer Sperrstrom", "Schaltnetzteile, Verpolschutz"],
                ["Fast Recovery", "UF4007", "wie 1N4007, aber t_rr ≈ 75 ns", "Schaltnetzteile, Umrichter"],
                ["Z-Diode", "BZX55C5V1", "in Sperrrichtung, U_Z fest (2.4 … 200 V)", "Referenz, einfache Stabilisierung"],
                ["LED", "–", "U_F 1.8 … 3.3 V, U_R nur ≈ 5 V", "Anzeige, Beleuchtung, Optokoppler"],
                ["TVS-Diode", "SMBJ24A, P6KE", "klemmt Spitzen in ns, hohe Pulsleistung", "ESD- und Überspannungsschutz"],
                ["Brückengleichrichter", "B80C1500", "4 Dioden in einem Gehäuse", "Netzteile (Graetz)"],
            ],
            "hinweis": "Bezeichnung **B80C1500**: B = Brücke, 80 = max. Anschlussspannung 80 V_eff, C = mit Ladekondensator, 1500 = 1500 mA Dauerstrom.",
        },
        {
            "titel": "📊 Typische Durchlassspannungen",
            "kopf": ["Diode", "U_F", "Bemerkung"],
            "zeilen": [
                ["Germanium", "≈ 0.3 V", "selten, alte Schaltungen"],
                ["Schottky", "0.2 … 0.45 V", "steigt mit dem Strom"],
                ["Silizium", "0.6 … 0.7 V", "Standard für Rechnungen (bei 1 A eher 0.9 … 1 V)"],
                ["LED rot / gelb", "1.8 … 2.1 V", ""],
                ["LED grün", "2.0 … 3.2 V", "alte Typen ≈ 2 V, InGaN (hell) ≈ 3 V"],
                ["LED blau / weiss", "2.8 … 3.3 V", "weiss = blau + Leuchtstoff"],
                ["LED infrarot", "1.2 … 1.5 V", "Fernbedienung, Lichtschranken, Optokoppler"],
            ],
            "hinweis": "Richtwerte – genaue Werte im Datenblatt (abhängig von Strom und Temperatur).",
        },
        {
            "titel": "📊 Gleichrichter-Schaltungen",
            "kopf": ["Schaltung", "Dioden", "U_F-Verlust", "Brummfrequenz", "Sperrspannung pro Diode"],
            "zeilen": [
                ["Einweg (M1)", "1", "1 · U_F", "f (50 Hz)", "≥ 2 · Û (mit Ladeelko)"],
                ["Mittelpunkt (M2)", "2 + Trafo mit Mittelanzapfung", "1 · U_F", "2f (100 Hz)", "≥ 2 · Û"],
                ["Brücke (B2, Graetz)", "4", "2 · U_F", "2f (100 Hz)", "≥ Û"],
            ],
            "hinweis": "Û = Spitzenwert der (halben) Trafowicklung. Zur Sperrspannung immer **Reserve** (Netz +10 %, Trafo im Leerlauf höher, Spitzen) – typisch Faktor 1.5 … 2.",
        },
        {
            "titel": "📊 Wichtige Datenblatt-Kennwerte",
            "kopf": ["Kürzel", "Bedeutung", "Worauf achten?"],
            "zeilen": [
                ["U_RRM", "max. periodische Sperrspannung", "mit Reserve über der höchsten Sperrspannung"],
                ["I_F(AV)", "max. mittlerer Durchlassstrom", "gilt bei bestimmter Temperatur (Derating)"],
                ["I_FSM", "Stossstrom (einmalig, z.B. 10 ms)", "Einschaltstrom in den leeren Ladeelko"],
                ["U_F", "Durchlassspannung bei I_F", "bestimmt die Verluste P = U_F · I_F"],
                ["I_R", "Sperrstrom", "bei Schottky gross und stark temperaturabhängig"],
                ["t_rr", "Sperrverzögerungszeit", "wichtig beim schnellen Schalten"],
                ["U_Z, r_Z, P_tot", "Z-Spannung, Innenwiderstand, Verlustleistung", "nur bei Z-Dioden"],
            ],
        },
    ],

    # ---- 💡 Kniffe: Dinge, die man auch nach Jahren gern vergisst ----
    "tipps": [
        "Kathode = Seite mit dem **Ring**. Bei LEDs: **kürzeres Bein** bzw. abgeflachte Gehäuseseite = Kathode. Merksatz: **K**athode = **k**urz = **K**ante.",
        "Diodentest mit dem Multimeter: Durchlass zeigt ca. **0.5 … 0.7 V** (Schottky ≈ 0.2 V, LED leuchtet evtl. schwach), Sperrrichtung **OL**. Beides ≈ 0 V = Kurzschluss, beides OL = Unterbrechung.",
        "Z-Dioden um **5 … 6 V** haben den kleinsten Temperaturkoeffizienten → beste einfache Referenz.",
        "Z-Diode als Überspannungsschutz eines Eingangs: Vorwiderstand nicht vergessen, sonst fliesst der ganze Strom der Quelle.",
        "Verpolschutz mit wenig Verlust: Schottky in Reihe – oder noch besser ein **P-Kanal-MOSFET** (fast kein Spannungsverlust).",
        "Mehrere LEDs **nie** parallel an einem Vorwiderstand – jede LED bekommt ihren eigenen (oder alle in Reihe mit einem Widerstand).",
        "Freilaufdiode bei einem Relais: **1N4148** reicht bei kleinen Relais (< 200 mA), sonst **1N4007**. Kathode an Plus!",
        "Dioden in **Reihe** für mehr Sperrspannung brauchen Symmetrierwiderstände; Dioden **parallel** für mehr Strom teilen sich den Strom schlecht (negativer TK von U_F).",
        "Eine Si-Diode in Durchlassrichtung ist eine grobe **0.7-V-Referenz** oder ein **Temperatursensor** (−2 mV/K).",
        "Ladeelko am Gleichrichter: Spannungsfestigkeit auf **Û × 1.1 × Reserve** auslegen – der Trafo liefert im Leerlauf mehr als auf dem Typenschild.",
    ],
    "fehler": [
        "LED ohne Vorwiderstand angeschlossen → LED brennt sofort durch.",
        "Diode verkehrt eingebaut → Schaltung ohne Funktion oder Kurzschluss (bei Verpolschutz parallel brennt die Sicherung).",
        "Z-Diode in Durchlassrichtung eingebaut → nur 0.7 V statt U_Z.",
        "Z-Diode im Leerlauf nicht geprüft → P_Z zu gross, Diode überhitzt.",
        "Sperrspannung zu klein gewählt – bei Einweg mit Ladeelko muss sie ≥ 2 · Û sein.",
        "Freilaufdiode verkehrt herum (Anode an Plus) → Kurzschluss, sobald der Transistor einschaltet.",
        "Langsame 1N4007 in einem Schaltnetzteil → wird heiss, weil sie bei jedem Takt kurz rückwärts leitet (t_rr).",
        "Mit U_F = 0.7 V bei 1 A gerechnet → real eher 0.9 … 1 V, Verlustleistung zu klein geschätzt.",
    ],
    "siehe_auch": ["widerstand", "kondensator", "transistor", "relais"],

    # ---- 🧮 Rechner (IDs aus dioden_rechner.py + mitbenutzt aus widerstand_/relais_rechner.py) ----
    "rechner": ["led_vorwiderstand", "z_diode", "gleichrichter", "durchlassspannung", "freilauf", "dioden_kennlinie"],
}
