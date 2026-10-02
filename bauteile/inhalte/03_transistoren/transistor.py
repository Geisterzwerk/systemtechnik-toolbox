# =============================================================================
# Thema: Transistor (Bipolartransistor NPN/PNP)  (Kategorie: Transistoren)
# -----------------------------------------------------------------------------
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner + Simulator:  bauteile/rechner/transistor_rechner.py
# Rechenlogik:          bauteile/rechner/transistor_mathe.py
# Schaltzeichen:        bauteile/grafiken/symbole.py  ("npn_pnp")
# =============================================================================

THEMA = {
    "titel": "Transistor (Bipolar)",
    "reihenfolge": 1,
    "kurz": "Ein kleiner Basisstrom steuert einen grossen Kollektorstrom – als Schalter oder Verstärker.",
    "stichworte": ["transistor", "bipolartransistor", "bjt", "npn", "pnp", "basis", "kollektor", "emitter",
                   "hfe", "stromverstärkung", "beta", "sättigung", "übersteuerung", "übersteuerungsfaktor",
                   "basiswiderstand", "schalter", "low-side", "high-side", "arbeitspunkt", "arbeitsbereich",
                   "sperrbereich", "aktiver bereich", "kennlinie", "lastgerade", "emitterschaltung",
                   "kollektorschaltung", "emitterfolger", "basisschaltung", "darlington", "verlustleistung",
                   "kühlkörper", "thermik", "rth", "speicherzeit", "bc547", "bc557", "bc337", "2n2222",
                   "bd139", "tip120", "treiber", "mikrocontroller"],

    # ---- Steckbrief oben (Schaltzeichen aus bauteile/grafiken/symbole.py) ----
    "steckbrief": {
        "symbol": "npn_pnp",
        "zeilen": [
            ("Anschlüsse", "Basis (B), Kollektor (C), Emitter (E)"),
            ("Typen", "NPN (Pfeil nach aussen) und PNP (Pfeil nach innen)"),
            ("Steuerung", "stromgesteuert – kleiner Basisstrom steuert grossen Kollektorstrom"),
            ("Stromverstärkung", "`B = I_C / I_B`   (Datenblatt: hFE, typ. 50 … 800, streut stark)"),
            ("Knotenregel", "`I_E = I_B + I_C`"),
            ("Typische Spannungen", "`U_BE ≈ 0.7 V` (leitend)   ·   `U_CE,sat ≈ 0.1 … 0.3 V` (gesättigt)"),
            ("Wichtigste Grenzwerte", "I_C,max, U_CE0, P_tot, T_j,max – nie überschreiten"),
        ],
    },

    # Interaktiver Simulator direkt im Wissen-Teil (-> bauteile/grafiken/transistor_simulator.py)
    "grafiken": ["transistor_simulator"],

    "erklaerung": """
## Was macht ein Transistor?
Ein Bipolartransistor ist ein **stromgesteuerter Stromverstärker**: Ein kleiner Strom in die **Basis** lässt einen grossen Strom vom **Kollektor** zum **Emitter** fliessen. Mit `B = I_C / I_B ≈ 100` steuern 1 mA Basisstrom rund 100 mA Kollektorstrom. Damit kann ein Mikrocontroller-Pin (wenige mA) ein Relais, einen Motor oder eine LED-Kette schalten.
## Aufbau: NPN und PNP
Ein Bipolartransistor besteht aus drei Halbleiterschichten, also **zwei pn-Übergängen** – man kann ihn sich wie zwei Dioden vorstellen (Basis-Emitter-Diode und Basis-Kollektor-Diode). Das Diodenmodell reicht zum **Durchmessen**, erklärt aber nicht die Verstärkung.
- **NPN:** Strom fliesst in Basis und Kollektor **hinein** und aus dem Emitter **heraus**. Leitet, wenn die Basis ca. **0.7 V über dem Emitter** liegt. Emitter meist an GND.
- **PNP:** alles umgekehrt – Strom fliesst in den Emitter hinein. Leitet, wenn die Basis ca. **0.7 V unter dem Emitter** liegt. Emitter meist an +U_B.
- **Merksatz:** Der Pfeil sitzt immer am Emitter und zeigt die technische Stromrichtung. NPN = „**N**icht **P**feil **N**ach innen“.
## Die Arbeitsbereiche
- **Sperrbereich:** `U_BE < 0.5 … 0.7 V` → kein Strom, der Schalter ist **offen**, `U_CE ≈ U_B`
- **Aktiver Bereich (Normalbetrieb):** BE-Diode leitet, BC-Diode sperrt → `I_C = B · I_B`. Der Transistor arbeitet als **Verstärker**. Als Schalter schlecht: `P = U_CE · I_C` ist gross, er wird heiss.
- **Sättigung (Übersteuerung):** Es fliesst **mehr** Basisstrom, als für den Laststrom nötig wäre. Beide Dioden leiten, `U_CE` fällt auf ca. **0.2 V** → Schalter **geschlossen**, wenig Verlust. Hier gilt `I_C < B · I_B` – die **Last** begrenzt den Strom, nicht mehr der Transistor.
- **Inversbetrieb:** Kollektor und Emitter vertauscht – funktioniert, aber mit sehr kleinem B. Praktisch nur als Fehlerbild relevant (Transistor falsch herum eingelötet).
## Kennlinien und Lastgerade
- **Eingangskennlinie** `I_B = f(U_BE)`: sieht aus wie eine Diodenkennlinie, Knick bei ca. 0.6 … 0.7 V.
- **Ausgangskennlinienfeld** `I_C = f(U_CE)` mit I_B als Parameter: waagrechte Linien im aktiven Bereich, steiler Anstieg ganz links (Sättigung).
- **Lastgerade:** `I_C = (U_B − U_CE) / R_C` – verbindet `U_CE = U_B` (gesperrt) mit `I_C = U_B / R_C` (Kurzschluss). Der **Arbeitspunkt** liegt immer auf dieser Geraden: als Schalter an den beiden Enden, als Verstärker in der Mitte.
## Transistor als Schalter – Vorgehen
- 1. **Laststrom:** `I_C = (U_B − U_CE,sat) / R_Last`   (bei Relais: Nennstrom aus dem Datenblatt)
- 2. **Basisstrom mit Übersteuerung:** `I_B = ü · I_C / B_min`   mit ü = 2 … 5
- 3. **Basiswiderstand:** `R_B = (U_Steuer − U_BE) / I_B` → nächsten **kleineren** Normwert wählen
- 4. **Prüfen:** I_C ≤ I_C,max, U_B < U_CE0 (mit Reserve), Verlustleistung < P_tot, kann die Steuerquelle I_B liefern?
- 5. **Induktive Last?** → Freilaufdiode antiparallel zur Last!
## Der Übersteuerungsfaktor ü
`ü = I_B,tatsächlich / I_B,min = I_B · B_min / I_C` – sagt, wie viel **mehr** Basisstrom fliesst, als rechnerisch gerade reichen würde (ü = 1 ist genau die Grenze zwischen aktivem Bereich und Sättigung).
- **Warum ü > 1?** B streut stark zwischen Exemplaren, sinkt bei grossen Strömen und tiefen Temperaturen, und Widerstände haben Toleranzen. Mit ü = 2 … 5 ist der Transistor trotzdem sicher gesättigt.
- **Warum nicht ü = 20?** Zu viel Basisstrom speichert Ladung in der Basis → **Speicherzeit t_s**: der Transistor schaltet verzögert aus (µs statt ns). Ausserdem wird die Steuerquelle unnötig belastet.
## Verlustleistung und Wärme
- **Gesättigt:** `P_V = U_CE,sat · I_C + U_BE · I_B` – klein, z.B. 0.2 V · 100 mA = 20 mW
- **Aktiver Bereich:** `P_V = U_CE · I_C` – mit ohmscher Last maximal bei `U_CE = U_B / 2`: `P_max = U_B² / (4 · R_C)`. Deshalb ist „halb offen“ als Schalter so schlecht.
- **Schalten mit PWM:** Bei jedem Umschalten durchläuft der Transistor kurz den aktiven Bereich → **Schaltverluste** `P_S ≈ ½ · U_B · I_C · (t_r + t_f) · f` steigen mit der Frequenz.
- **Thermik:** `T_j = T_U + P_V · R_th` – ein TO-92 (R_thJA ≈ 200 K/W) wird bei 0.5 W schon ca. 100 K wärmer als die Umgebung.
## Low-Side und High-Side
- **Low-Side (NPN):** Last zwischen +U_B und Kollektor, Emitter an GND. Einfach, Steuerspannung bezieht sich auf GND → **Standard** für µC-Ausgänge.
- **High-Side (PNP):** Emitter an +U_B, Last zwischen Kollektor und GND. Die Last liegt dann einseitig an Masse (z.B. Fahrzeug, Sensorversorgung). Zum **Ausschalten** muss die Basis auf U_B – ist U_B grösser als die µC-Spannung (z.B. 12 V vs. 3.3 V), braucht es einen kleinen NPN als **Pegelwandler** davor.
- **NPN auf der High-Side** funktioniert nur als Emitterfolger: am Emitter kommt höchstens `U_Basis − 0.7 V` an → Transistor schaltet nicht voll durch und wird warm.
## Grundschaltungen (Verstärker)
Benannt nach dem Anschluss, der für Ein- und Ausgang **gemeinsam** ist:
- **Emitterschaltung:** hohe Spannungs- und Stromverstärkung, Ausgang **invertiert** (180°) → Standard-Verstärker. Mit Emitterwiderstand R_E (Gegenkopplung) gilt `v_u ≈ −R_C / R_E` – stabil, unabhängig von B.
- **Kollektorschaltung (Emitterfolger):** `U_A ≈ U_E − 0.7 V`, Spannungsverstärkung ≈ 1, hoher Eingangs- und kleiner Ausgangswiderstand → **Impedanzwandler**, Puffer.
- **Basisschaltung:** Stromverstärkung ≈ 1, kleiner Eingangswiderstand, sehr hohe Grenzfrequenz → HF-Technik.
## Temperaturverhalten
`U_BE` sinkt um ca. **2 mV/K**, B steigt mit der Temperatur. In linearen Schaltungen kann das zur **thermischen Mitkopplung** führen: wärmer → mehr Strom → noch wärmer. Abhilfe: Emitterwiderstand (Gegenkopplung) und ausreichende Kühlung.
""",

    "tabellen": [
        {
            "titel": "📊 Arbeitsbereiche im Überblick",
            "kopf": ["Bereich", "BE-Diode", "BC-Diode", "Kennzeichen", "Anwendung"],
            "zeilen": [
                ["Sperrbereich", "sperrt", "sperrt", "I_C ≈ 0, U_CE ≈ U_B", "Schalter AUS"],
                ["Aktiver Bereich", "leitet", "sperrt", "I_C = B · I_B, U_CE > U_CE,sat", "Verstärker"],
                ["Sättigung", "leitet", "leitet", "U_CE ≈ 0.2 V, I_C < B · I_B", "Schalter EIN"],
                ["Inversbetrieb", "sperrt", "leitet", "C und E vertauscht, B sehr klein", "kaum genutzt (Fehlerbild)"],
            ],
        },
        {
            "titel": "📊 NPN und PNP im Vergleich",
            "kopf": ["Merkmal", "NPN", "PNP"],
            "zeilen": [
                ["Pfeil im Symbol", "zeigt nach aussen", "zeigt nach innen"],
                ["Stromrichtung", "B und C hinein, E heraus", "E hinein, B und C heraus"],
                ["Leitet, wenn …", "Basis ≈ 0.7 V ÜBER Emitter", "Basis ≈ 0.7 V UNTER Emitter"],
                ["Emitter liegt an", "GND", "+U_B"],
                ["Typischer Einsatz", "Low-Side-Schalter", "High-Side-Schalter"],
                ["Beispiel", "BC547, BC337, 2N2222", "BC557, BC327, 2N2907"],
            ],
            "hinweis": "Alle Spannungen und Ströme sind beim PNP **umgekehrt** – die Formeln bleiben gleich, wenn man mit Beträgen rechnet.",
        },
        {
            "titel": "📊 Übersteuerungsfaktor ü – Richtwerte",
            "kopf": ["ü", "Wirkung"],
            "zeilen": [
                ["< 1", "nicht gesättigt → aktiver Bereich, Transistor wird heiss"],
                ["1", "genau an der Grenze – unsicher (Streuung von B, Temperatur)"],
                ["2 … 3", "Standard: sicher gesättigt, schaltet noch schnell aus"],
                ["5", "robust, auch bei tiefer Temperatur – etwas längere Speicherzeit"],
                ["> 10", "unnötig: lange Ausschaltverzögerung, belastet die Steuerquelle"],
            ],
        },
        {
            "titel": "📊 Wichtige Datenblatt-Kennwerte",
            "kopf": ["Kürzel", "Bedeutung", "Worauf achten?"],
            "zeilen": [
                ["U_CE0 (U_CEO)", "max. Kollektor-Emitter-Spannung, Basis offen", "mit Reserve: U_B + Spannungsspitzen"],
                ["U_EB0 (U_EBO)", "max. Sperrspannung Emitter-Basis", "nur ca. 5 … 6 V! (PNP-High-Side, AC-Signale)"],
                ["I_C / I_CM", "Dauer- / Spitzen-Kollektorstrom", "Einschaltstrom von Lampen und Motoren beachten"],
                ["P_tot", "max. Verlustleistung", "gilt meist bei 25 °C – darüber Derating"],
                ["h_FE", "Gleichstromverstärkung B", "Minimalwert beim eigenen I_C nehmen"],
                ["U_CE(sat)", "Sättigungsspannung", "wird bei grossem I_C deutlich grösser"],
                ["U_BE(sat)", "Basis-Emitter-Spannung in Sättigung", "oft 0.8 … 1 V statt 0.7 V"],
                ["f_T", "Transitfrequenz (B sinkt auf 1)", "für Verstärker und schnelles Schalten"],
                ["R_thJA / R_thJC", "Wärmewiderstand zur Umgebung / zum Gehäuse", "→ Kühlkörper-Rechner"],
            ],
        },
        {
            "titel": "📊 Grundschaltungen",
            "kopf": ["Schaltung", "Spannungsverstärkung", "Eingang / Ausgang", "Typischer Einsatz"],
            "zeilen": [
                ["Emitterschaltung", "gross, invertiert (180°)", "mittel / ≈ R_C", "Standard-Verstärker, Schalter"],
                ["Kollektorschaltung", "≈ 1, nicht invertiert", "hoch / klein", "Impedanzwandler (Emitterfolger)"],
                ["Basisschaltung", "gross, nicht invertiert", "klein / ≈ R_C", "HF-Verstärker"],
            ],
        },
        {
            "titel": "📊 Typische Transistoren",
            "kopf": ["Typ", "Daten", "Bemerkung"],
            "zeilen": [
                ["BC547 (NPN)", "I_C 100 mA, U_CE0 45 V, P_tot 0.5 W", "Standard Kleinsignal; B-Gruppen A/B/C: 110–220 / 200–450 / 420–800"],
                ["BC557 (PNP)", "I_C 100 mA, U_CE0 45 V, P_tot 0.5 W", "Gegenstück zum BC547"],
                ["BC337 (NPN)", "I_C 800 mA, U_CE0 45 V, P_tot 0.625 W", "gut für Relais bis ca. 300 mA"],
                ["2N2222A (NPN)", "I_C 600 mA, U_CE0 40 V", "Klassiker, v.a. in US-Schaltungen"],
                ["BD139 (NPN)", "I_C 1.5 A, U_CE0 80 V, TO-126", "mittlere Leistung, mit Kühlkörper"],
                ["TIP120 (NPN-Darlington)", "I_C 5 A, U_CE0 60 V, B ≥ 1000", "U_CE,sat bis 2 V → hohe Verluste"],
                ["IRLZ44N (MOSFET)", "Logic-Level, R_DS(on) ≈ 25 mΩ", "zum Vergleich: grosse Ströme direkt vom µC"],
            ],
            "hinweis": "Richtwerte – immer das Datenblatt des konkreten Herstellers nehmen. **Pinbelegung** (E-B-C oder C-B-E …) ist je nach Typ und Hersteller verschieden!",
        },
        {
            "titel": "📊 Bipolartransistor oder MOSFET?",
            "kopf": ["Merkmal", "Bipolar (BJT)", "MOSFET"],
            "zeilen": [
                ["Steuerung", "Strom (I_B fliesst dauernd)", "Spannung (Strom nur beim Umladen des Gates)"],
                ["Durchlassverlust", "P ≈ U_CE,sat · I (U_CE,sat ≈ 0.2 V fix)", "P = I² · R_DS(on)"],
                ["Gut für", "kleine Ströme, Analogtechnik, günstig", "grosse Ströme, schnelle PWM"],
                ["Achtung", "Basisstrom muss geliefert werden", "Logic-Level-Typ nötig für 3.3 / 5 V"],
            ],
        },
    ],

    # ---- 💡 Kniffe: Dinge, die man auch nach Jahren gern vergisst ----
    "tipps": [
        "Als Schalter immer mit Übersteuerung **ü = 2 … 5** rechnen – und mit **B min** aus dem Datenblatt, nie mit dem typischen Wert.",
        "R_B auf den nächst **kleineren** Normwert runden (mehr Basisstrom = sicherer gesättigt).",
        "**Pull-down Basis → Emitter** (z.B. 10 … 100 kΩ): Transistor sperrt sicher, solange der µC-Pin beim Start noch hochohmig ist.",
        "Last immer auf der **Kollektorseite**, Emitter direkt an GND (Low-Side) – so schaltet der NPN voll durch.",
        "**Freilaufdiode** (z.B. 1N4148 / 1N4007) antiparallel zu Relais und Motoren – sonst zerstört die Abschaltspitze den Transistor.",
        "Schaltet zu langsam aus? Zu stark übersteuert → ü verkleinern, **Speed-up-Kondensator** (z.B. 100 pF … 1 nF) parallel zu R_B oder Schottky-Diode Basis → Kollektor (Baker-Clamp).",
        "**Durchmessen** mit dem Dioden-Test: B→E und B→C je ca. 0.6 … 0.7 V (NPN: rote Leitung an B), C↔E in beide Richtungen sperrend.",
        "Mehrere Ausgänge mit Transistoren? Ein **ULN2003/ULN2803** enthält 7/8 Darlington-Treiber inkl. Freilaufdioden.",
        "Ab ca. **0.5 A** oder bei schneller PWM lieber einen **Logic-Level-MOSFET** – fast kein Steuerstrom, kleinere Verluste.",
        "U_CE,sat im Datenblatt gilt nur für das dort angegebene Verhältnis I_C/I_B (oft 10:1 = ü ≈ 10 bei B = 100). Bei kleinerem ü ist U_CE,sat grösser.",
    ],
    "fehler": [
        "Basis ohne Widerstand direkt an den µC-Pin oder an 5 V → Basis-Emitter-Strecke und/oder Pin brennen durch.",
        "Mit typischem statt minimalem B gerechnet → Transistor bleibt im aktiven Bereich und wird heiss.",
        "Freilaufdiode bei Relais / Motor vergessen → Spannungsspitze zerstört den Transistor.",
        "NPN auf der High-Side eingesetzt → Emitter folgt der Basis, Last bekommt nur U_Steuer − 0.7 V.",
        "PNP mit 3.3-V-µC an 12 V geschaltet → lässt sich nie ganz ausschalten (Basis kommt nicht auf 12 V).",
        "Pinbelegung (E-B-C) nicht im Datenblatt geprüft → Transistor läuft invers mit winzigem B.",
        "Kein Pull-down an der Basis → Transistor schaltet beim Einschalten oder bei offenem Pin zufällig.",
        "Verlustleistung im aktiven Bereich unterschätzt (z.B. Linearregler, Konstantstromquelle) → P = U_CE · I_C nachrechnen!",
    ],
    "siehe_auch": ["diode", "relais", "widerstand", "spule"],

    # ---- 🧮 Rechner (IDs aus bauteile/rechner/transistor_rechner.py) ----
    "rechner": ["basiswiderstand", "arbeitspunkt", "verlustleistung", "kuehlkoerper", "transistor_simulator"],
}
