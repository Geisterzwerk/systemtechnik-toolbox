# =============================================================================
# bauteile/rechner/rechner_info.py
# -----------------------------------------------------------------------------
# METADATEN aller Rechner für den Rechner-Tab: Titel, Kategorie, Suchwörter und
# Wissensseite. Die Rechner selbst stehen weiterhin in den *_rechner.py-Dateien
# und werden NICHT kopiert - der Rechner-Tab baut sie über dieselbe Registry
# (bauteile/rechner/__init__.py -> erstellen()) wie die Wissensseiten.
#
# EIN EINTRAG:
#   "rechner_id": {
#       "titel":          Name in Liste und Suche
#       "kategorie":      einer aus KATEGORIEN (unten)
#       "unterkategorie": frei, z.B. "Netzteile" (Reihenfolge = erstes Auftreten hier)
#       "beschreibung":   ein Satz: Was rechnet er aus?
#       "stichworte":     Suchwörter (Fachbegriffe, Abkürzungen, Bauteilnamen)
#       "wissensseite":   ID der Seite, die das Thema erklärt (Dateiname ohne .py,
#                         aus bauteile/, messtechnik/ oder schaltungen/inhalte/)
#   }
#
# NEUER RECHNER?  1. in *_rechner.py registrieren   2. hier eintragen
#                 3. python pruefen_rechner.py  -> meldet fehlende/falsche Angaben
#
# WER RUFT DAS AUF?  gui/rechner_gui.py (Rechner-Tab), pruefen_rechner.py (Validierung)
# =============================================================================

# Kategorie -> (Icon, Beschreibung). Reihenfolge = Reihenfolge im Rechner-Tab.
KATEGORIEN = {
    "Grundlagen":     ("📘", "Ohm, Wechselstrom, Schaltvorgänge, Wärme"),
    "Bauteile":       ("🔧", "Kennwerte und Codes einzelner Bauteile"),
    "Schaltungen":    ("🔌", "Netzteile, Teiler, Filter, Schalten, Verstärker"),
    "Messtechnik":    ("📏", "Messunsicherheit, Messgeräte, Sensoren"),
    "Digitaltechnik": ("💾", "Zahlen, Pegel, Logik, Schaltnetze, Schaltwerke, Busse, Speicher, AD-Wandler"),
}

# Diese Bereiche enthalten Wissensseiten (Tab-Name -> Ordner mit den Seiten)
WISSENS_BEREICHE = {"Bauteile": "bauteile/inhalte", "Messtechnik": "messtechnik/inhalte",
                    "Schaltungen": "schaltungen/inhalte", "Digitaltechnik": "digitaltechnik/inhalte"}

RECHNER_INFO = {
    # =========================================================================
    # GRUNDLAGEN
    # =========================================================================
    "ohm_leistung": {
        "titel": "Ohm'sches Gesetz & Leistung", "kategorie": "Grundlagen", "unterkategorie": "Gleichstrom",
        "beschreibung": "Zwei von U, I, R, P eingeben – die anderen zwei werden berechnet.",
        "stichworte": ["Ohm", "Spannung", "Strom", "Widerstand", "Leistung", "URI"],
        "wissensseite": "widerstand"},
    "reihe_parallel": {
        "titel": "Widerstände in Reihe & parallel", "kategorie": "Grundlagen", "unterkategorie": "Gleichstrom",
        "beschreibung": "Gesamtwiderstand beliebig vieler Widerstände und passender Ergänzungswiderstand.",
        "stichworte": ["Reihenschaltung", "Parallelschaltung", "Ersatzwiderstand", "Gesamtwiderstand"],
        "wissensseite": "widerstand"},
    "leitung": {
        "titel": "Leitungswiderstand & Spannungsfall", "kategorie": "Grundlagen", "unterkategorie": "Gleichstrom",
        "beschreibung": "Widerstand, Spannungsfall und Verluste einer Kupfer- oder Aluleitung.",
        "stichworte": ["Kabel", "Querschnitt", "Spannungsfall", "Kupfer", "Aluminium", "Leiter"],
        "wissensseite": "widerstand"},
    "temperatur": {
        "titel": "Widerstand bei anderer Temperatur", "kategorie": "Grundlagen", "unterkategorie": "Gleichstrom",
        "beschreibung": "Wie stark ändert sich ein Widerstand mit der Temperatur (α-Wert)?",
        "stichworte": ["Temperaturkoeffizient", "Alpha", "Kupfer", "Erwärmung", "PTC"],
        "wissensseite": "widerstand"},
    "blindwiderstand_c": {
        "titel": "Blindwiderstand Xc", "kategorie": "Grundlagen", "unterkategorie": "Wechselstrom",
        "beschreibung": "Blindwiderstand, Strom und Blindleistung eines Kondensators bei einer Frequenz.",
        "stichworte": ["Xc", "kapazitiv", "Blindleistung", "Wechselstrom", "Impedanz"],
        "wissensseite": "kondensator"},
    "blindwiderstand_l": {
        "titel": "Blindwiderstand XL", "kategorie": "Grundlagen", "unterkategorie": "Wechselstrom",
        "beschreibung": "Blindwiderstand, Impedanz mit Drahtwiderstand und Phasenwinkel einer Spule.",
        "stichworte": ["XL", "induktiv", "Impedanz", "Phasenwinkel", "Wechselstrom"],
        "wissensseite": "spule"},
    "lc_resonanz": {
        "titel": "LC-Schwingkreis", "kategorie": "Grundlagen", "unterkategorie": "Wechselstrom",
        "beschreibung": "Resonanzfrequenz oder fehlendes L bzw. C, dazu der Kennwiderstand.",
        "stichworte": ["Resonanz", "Schwingkreis", "Thomson", "f0", "Kennwiderstand"],
        "wissensseite": "spule"},
    "rc_ladekurve": {
        "titel": "Kondensator laden & entladen (interaktiv)", "kategorie": "Grundlagen", "unterkategorie": "Schaltvorgänge",
        "beschreibung": "Spannung und Strom am Kondensator über der Zeit, mit τ-Marken.",
        "stichworte": ["Ladekurve", "Entladekurve", "Zeitkonstante", "tau", "RC-Glied", "e-Funktion"],
        "wissensseite": "kondensator"},
    "rl_kurve": {
        "titel": "Spule ein- & ausschalten (interaktiv)", "kategorie": "Grundlagen", "unterkategorie": "Schaltvorgänge",
        "beschreibung": "Strom und Spannung an der Spule, Ausschalten mit und ohne Freilaufdiode.",
        "stichworte": ["Einschaltvorgang", "Abschaltspannung", "Zeitkonstante", "tau", "RL-Glied", "Freilauf"],
        "wissensseite": "spule"},
    "rc_zeit": {
        "titel": "RC-Zeiten", "kategorie": "Grundlagen", "unterkategorie": "Schaltvorgänge",
        "beschreibung": "Zeitkonstante τ und Zeit bis zu einer Zielspannung beim Laden oder Entladen.",
        "stichworte": ["Zeitkonstante", "tau", "Ladezeit", "Entladezeit", "Verzögerung"],
        "wissensseite": "kondensator"},
    "rl_zeit": {
        "titel": "RL-Zeiten", "kategorie": "Grundlagen", "unterkategorie": "Schaltvorgänge",
        "beschreibung": "Zeitkonstante τ = L/R und Strom nach einer bestimmten Zeit.",
        "stichworte": ["Zeitkonstante", "tau", "Stromanstieg", "Einschaltstrom"],
        "wissensseite": "spule"},
    "kuehlkoerper": {
        "titel": "Kühlkörper auslegen", "kategorie": "Grundlagen", "unterkategorie": "Wärme",
        "beschreibung": "Nötiger Wärmewiderstand des Kühlkörpers aus Verlustleistung und Temperaturen.",
        "stichworte": ["Wärmewiderstand", "Rth", "Sperrschicht", "Tj", "Kühlung", "Temperatur"],
        "wissensseite": "bipolartransistor"},

    # =========================================================================
    # BAUTEILE
    # =========================================================================
    "farbcode_wert": {
        "titel": "Farbcode → Wert", "kategorie": "Bauteile", "unterkategorie": "Widerstand",
        "beschreibung": "Farbringe auswählen und den Widerstandswert ablesen.",
        "stichworte": ["Farbcode", "Farbringe", "Ringe", "Widerstandswert", "IEC 60062"],
        "wissensseite": "widerstand"},
    "wert_farbcode": {
        "titel": "Wert → Farbcode", "kategorie": "Bauteile", "unterkategorie": "Widerstand",
        "beschreibung": "Welche Farbringe hat ein Widerstand mit diesem Wert?",
        "stichworte": ["Farbcode", "Farbringe", "Ringe", "4 Ringe", "5 Ringe"],
        "wissensseite": "widerstand"},
    "smd_code": {
        "titel": "SMD-Code entschlüsseln", "kategorie": "Bauteile", "unterkategorie": "Widerstand",
        "beschreibung": "Aufdruck wie 103, 4R7, 4701 oder EIA-96 (01C) in einen Wert umrechnen.",
        "stichworte": ["SMD", "Aufdruck", "EIA-96", "Code", "Beschriftung"],
        "wissensseite": "widerstand"},
    "e_reihe": {
        "titel": "Nächster Normwert (E-Reihe)", "kategorie": "Bauteile", "unterkategorie": "Widerstand",
        "beschreibung": "Gerechneten Wert auf einen käuflichen Wert aus E6 … E96 runden.",
        "stichworte": ["E-Reihe", "Normwert", "E12", "E24", "E96", "Normreihe"],
        "wissensseite": "widerstand"},
    "energie_c": {
        "titel": "Kondensator: Ladung & Energie", "kategorie": "Bauteile", "unterkategorie": "Kondensator",
        "beschreibung": "Ladung Q = C · U und gespeicherte Energie W = ½ · C · U².",
        "stichworte": ["Energie", "Ladung", "Elko", "Entladen", "Sicherheit"],
        "wissensseite": "kondensator"},
    "reihe_parallel_c": {
        "titel": "Kondensatoren in Reihe & parallel", "kategorie": "Bauteile", "unterkategorie": "Kondensator",
        "beschreibung": "Gesamtkapazität – genau umgekehrt wie beim Widerstand.",
        "stichworte": ["Reihenschaltung", "Parallelschaltung", "Gesamtkapazität", "Kapazität"],
        "wissensseite": "kondensator"},
    "kondensator_code": {
        "titel": "Kondensator-Aufdruck entschlüsseln", "kategorie": "Bauteile", "unterkategorie": "Kondensator",
        "beschreibung": "Codes wie 104, 4n7, 1u0 oder 104K in Kapazität und Toleranz umrechnen.",
        "stichworte": ["Aufdruck", "Code", "104", "Keramik", "Toleranzbuchstabe"],
        "wissensseite": "kondensator"},
    "energie_l": {
        "titel": "Spule: Energie im Magnetfeld", "kategorie": "Bauteile", "unterkategorie": "Spule",
        "beschreibung": "Gespeicherte Energie W = ½ · L · I².",
        "stichworte": ["Energie", "Magnetfeld", "Induktivität"],
        "wissensseite": "spule"},
    "reihe_parallel_l": {
        "titel": "Spulen in Reihe & parallel", "kategorie": "Bauteile", "unterkategorie": "Spule",
        "beschreibung": "Gesamtinduktivität ungekoppelter Spulen.",
        "stichworte": ["Reihenschaltung", "Parallelschaltung", "Induktivität", "Gesamtinduktivität"],
        "wissensseite": "spule"},
    "abschaltspitze": {
        "titel": "Abschalt-Spannungsspitze", "kategorie": "Bauteile", "unterkategorie": "Spule",
        "beschreibung": "Induzierte Spannung u = L · di/dt beim schnellen Abschalten.",
        "stichworte": ["Induktionsspannung", "Abschalten", "Überspannung", "di/dt", "Freilaufdiode"],
        "wissensseite": "spule"},
    "trafo_animation": {
        "titel": "So funktioniert ein Transformator (interaktiv)", "kategorie": "Bauteile", "unterkategorie": "Transformator",
        "beschreibung": "Spannungen, Ströme und Magnetfluss im Trafo zum Ausprobieren.",
        "stichworte": ["Trafo", "Animation", "Magnetfluss", "Übersetzung", "Windungen"],
        "wissensseite": "transformator"},
    "uebersetzung": {
        "titel": "Trafo: Übersetzung", "kategorie": "Bauteile", "unterkategorie": "Transformator",
        "beschreibung": "Spannungen, Windungen und Ströme eines idealen Transformators.",
        "stichworte": ["Trafo", "Übersetzungsverhältnis", "Windungszahl", "ü", "Primär", "Sekundär"],
        "wissensseite": "transformator"},
    "leistung_trafo": {
        "titel": "Trafo: Leistung & Wirkungsgrad", "kategorie": "Bauteile", "unterkategorie": "Transformator",
        "beschreibung": "Scheinleistung, Verluste, Primärstrom und Sicherung.",
        "stichworte": ["Trafo", "Scheinleistung", "VA", "Wirkungsgrad", "Primärstrom", "Sicherung"],
        "wissensseite": "transformator"},
    "windungen": {
        "titel": "Trafo: Windungen pro Volt", "kategorie": "Bauteile", "unterkategorie": "Transformator",
        "beschreibung": "Windungszahl aus Kernquerschnitt, Flussdichte und Frequenz.",
        "stichworte": ["Trafo", "Windungen", "Kern", "Flussdichte", "Eigenbau", "Umwickeln"],
        "wissensseite": "transformator"},
    "diode_kennlinie": {
        "titel": "Diodenkennlinie (interaktiv)", "kategorie": "Bauteile", "unterkategorie": "Dioden",
        "beschreibung": "Kennlinie und Arbeitspunkt von Si-, Schottky- und LED-Dioden.",
        "stichworte": ["Kennlinie", "Durchlassspannung", "Arbeitspunkt", "Schottky", "Shockley"],
        "wissensseite": "diode"},
    "zdiode_kennlinie": {
        "titel": "Z-Dioden-Kennlinie (interaktiv)", "kategorie": "Bauteile", "unterkategorie": "Dioden",
        "beschreibung": "Durchbruchbereich und Arbeitspunkt einer Z-Diode.",
        "stichworte": ["Z-Diode", "Zener", "Durchbruch", "Kennlinie", "Arbeitspunkt"],
        "wissensseite": "z_diode"},
    "diode_temperatur": {
        "titel": "Diode: Durchlassspannung & Temperatur", "kategorie": "Bauteile", "unterkategorie": "Dioden",
        "beschreibung": "Uf sinkt bei Silizium um ca. 2 mV pro Kelvin.",
        "stichworte": ["Temperaturkoeffizient", "Durchlassspannung", "Uf", "Temperatursensor"],
        "wissensseite": "diode"},
    "diode_verlust": {
        "titel": "Diode: Verlustleistung & Erwärmung", "kategorie": "Bauteile", "unterkategorie": "Dioden",
        "beschreibung": "Verlustleistung und Sperrschichttemperatur einer Diode.",
        "stichworte": ["Verlustleistung", "Sperrschicht", "Tj", "Rth", "Schottky"],
        "wissensseite": "diode"},
    "transistor_simulator": {
        "titel": "Bipolartransistor als Schalter (Simulator)", "kategorie": "Bauteile", "unterkategorie": "Transistoren",
        "beschreibung": "NPN/PNP: gesperrt, aktiv oder gesättigt – mit Lampe und Wärmeanzeige.",
        "stichworte": ["NPN", "PNP", "Sättigung", "Simulator", "Low-Side", "High-Side", "BJT"],
        "wissensseite": "bipolartransistor"},
    "mosfet_simulator": {
        "titel": "MOSFET als Schalter (Simulator)", "kategorie": "Bauteile", "unterkategorie": "Transistoren",
        "beschreibung": "N-/P-Kanal: Schwellspannung, R_DS(on) und Gate-Ladung zum Ausprobieren.",
        "stichworte": ["MOSFET", "N-Kanal", "P-Kanal", "Logic-Level", "RDS(on)", "Simulator", "Gate"],
        "wissensseite": "mosfet"},
    "arbeitspunkt": {
        "titel": "Transistor-Schalter: Arbeitspunkt prüfen", "kategorie": "Bauteile", "unterkategorie": "Transistoren",
        "beschreibung": "Ist ein vorhandener NPN-Schalter gesperrt, aktiv oder gesättigt?",
        "stichworte": ["NPN", "Sättigung", "Übersteuerung", "UCE", "Basisstrom"],
        "wissensseite": "bipolartransistor"},
    "verlustleistung": {
        "titel": "Transistor: Verlustleistung", "kategorie": "Bauteile", "unterkategorie": "Transistoren",
        "beschreibung": "Durchlass- und Schaltverluste eines Bipolartransistors, auch bei PWM.",
        "stichworte": ["Verlustleistung", "PWM", "Schaltverluste", "Tastgrad", "Ptot"],
        "wissensseite": "bipolartransistor"},
    "mosfet_verlust": {
        "titel": "MOSFET: Verlustleistung", "kategorie": "Bauteile", "unterkategorie": "Transistoren",
        "beschreibung": "Leitverluste mit R_DS(on) und Schaltverluste bei PWM.",
        "stichworte": ["MOSFET", "RDS(on)", "Leitverluste", "Schaltverluste", "PWM"],
        "wissensseite": "mosfet"},
    "mosfet_gate": {
        "titel": "MOSFET: Gate-Ansteuerung", "kategorie": "Bauteile", "unterkategorie": "Transistoren",
        "beschreibung": "Gate-Strom, Gate-Widerstand und Treiberleistung aus der Gate-Ladung.",
        "stichworte": ["MOSFET", "Gate", "Gate-Ladung", "Qg", "Treiber", "Gatewiderstand"],
        "wissensseite": "mosfet"},
    "relais_temperatur": {
        "titel": "Relais: zieht es warm noch an?", "kategorie": "Bauteile", "unterkategorie": "Relais",
        "beschreibung": "Spulenwiderstand und Ansprechspannung bei hoher Temperatur.",
        "stichworte": ["Relais", "Spule", "Ansprechspannung", "Temperatur", "Schaltschrank"],
        "wissensseite": "relais"},
    "kontakt_last": {
        "titel": "Relais: Kontaktbelastung", "kategorie": "Bauteile", "unterkategorie": "Relais",
        "beschreibung": "Einschaltstrom je Lastart und Hinweise zu DC-Lichtbogen.",
        "stichworte": ["Relais", "Kontakt", "Einschaltstrom", "Inrush", "Lichtbogen", "Schütz"],
        "wissensseite": "relais"},

    # =========================================================================
    # SCHALTUNGEN
    # =========================================================================
    "schaltung_spannungsteiler": {
        "titel": "Spannungsteiler (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Widerstandsnetzwerke",
        "beschreibung": "Schaltplan mit Werten: Widerstände verändern, Last zuschalten, Querstromverhältnis sehen.",
        "stichworte": ["Spannungsteiler", "belastet", "Querstrom", "Schaltplan", "Last"],
        "wissensseite": "spannungsteiler"},
    "spannungsteiler": {
        "titel": "Spannungsteiler", "kategorie": "Schaltungen", "unterkategorie": "Widerstandsnetzwerke",
        "beschreibung": "Ausgangsspannung oder fehlender Widerstand, auch mit Last.",
        "stichworte": ["Teiler", "Spannungsteiler", "Belastung", "Querstrom", "Potentiometer"],
        "wissensseite": "spannungsteiler"},
    "schaltung_stromteiler": {
        "titel": "Stromteiler (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Widerstandsnetzwerke",
        "beschreibung": "Wie teilt sich ein Strom auf zwei parallele Zweige auf? Werte direkt im Schaltplan.",
        "stichworte": ["Stromteiler", "Parallelschaltung", "Knotenregel", "Schaltplan"],
        "wissensseite": "stromteiler"},
    "stromteiler": {
        "titel": "Stromteiler", "kategorie": "Schaltungen", "unterkategorie": "Widerstandsnetzwerke",
        "beschreibung": "Zweigströme und Leistungen beliebig vieler paralleler Widerstände.",
        "stichworte": ["Stromteiler", "Parallelschaltung", "Zweigstrom", "Knotenregel", "Shunt"],
        "wissensseite": "stromteiler"},
    "schaltung_pull": {
        "titel": "Pull-up / Pull-down (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Widerstandsnetzwerke",
        "beschreibung": "Taster am µC-Eingang: Pegel, Strom, Leckstrom und Flanke im Schaltplan.",
        "stichworte": ["Pull-up", "Pull-down", "Taster", "Mikrocontroller", "Eingang", "Schaltplan"],
        "wissensseite": "pull_up_down"},
    "pull_widerstand": {
        "titel": "Pull-up / Pull-down dimensionieren", "kategorie": "Schaltungen", "unterkategorie": "Widerstandsnetzwerke",
        "beschreibung": "Grenzen für den Pull-Widerstand aus Strom, Leckstrom und Flankenzeit, mit E12-Vorschlag.",
        "stichworte": ["Pull-up", "Pull-down", "I2C", "Leckstrom", "Anstiegszeit", "Taster"],
        "wissensseite": "pull_up_down"},
    "schaltung_poti": {
        "titel": "Potentiometer als Teiler (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Widerstandsnetzwerke",
        "beschreibung": "Schleifer drehen, Last zuschalten – Schaltplan und Kennlinie nebeneinander.",
        "stichworte": ["Potentiometer", "Poti", "Schleifer", "Kennlinie", "Lastfehler", "Schaltplan"],
        "wissensseite": "potentiometer"},
    "poti_last": {
        "titel": "Potentiometer mit Last", "kategorie": "Schaltungen", "unterkategorie": "Widerstandsnetzwerke",
        "beschreibung": "Ausgangsspannung und grösster Fehler eines belasteten Potentiometers.",
        "stichworte": ["Potentiometer", "Poti", "Lastfehler", "Schleifer", "Trimmer"],
        "wissensseite": "potentiometer"},
    "schaltung_bruecke": {
        "titel": "Wheatstone-Brücke (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Widerstandsnetzwerke",
        "beschreibung": "Vier Widerstände verstellen und die Diagonalspannung beobachten.",
        "stichworte": ["Wheatstone", "Brücke", "Abgleich", "Diagonalspannung", "Schaltplan"],
        "wissensseite": "wheatstone_bruecke"},
    "schaltung_begrenzer": {
        "titel": "Diodenbegrenzung (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Sinus über Vorwiderstand an Dioden: einseitig, zweiseitig oder mit Z-Dioden begrenzt.",
        "stichworte": ["Begrenzer", "Clipper", "Diodenbegrenzung", "Z-Diode", "Zeitdiagramm"],
        "wissensseite": "diodenbegrenzung"},
    "schaltung_eingangsschutz": {
        "titel": "Eingangsschutz µC (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Überspannung am Pin: Klemmdioden, Injektionsstrom und Rückspeisung in U_DD.",
        "stichworte": ["Eingangsschutz", "Klemmdiode", "ESD", "Injektionsstrom", "Mikrocontroller"],
        "wissensseite": "eingangsschutz"},
    "eingangsschutz": {
        "titel": "Eingangsschutz: Serienwiderstand", "kategorie": "Schaltungen", "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Mindestwert des Serienwiderstands aus Überspannung und erlaubtem Injektionsstrom.",
        "stichworte": ["Eingangsschutz", "Serienwiderstand", "Injektionsstrom", "Klemmdiode", "BAT54S"],
        "wissensseite": "eingangsschutz"},
    "schaltung_verpol": {
        "titel": "Verpolschutz (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Ohne Schutz, Si-Diode, Schottky oder P-MOSFET – Batterie richtig oder verpolt.",
        "stichworte": ["Verpolschutz", "P-MOSFET", "Schottky", "Batterie", "Body-Diode"],
        "wissensseite": "verpolschutz"},
    "verpolschutz": {
        "titel": "Verpolschutz im Vergleich", "kategorie": "Schaltungen", "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Spannungsfall, Verlustleistung und Wirkungsgrad von Diode, Schottky und P-MOSFET.",
        "stichworte": ["Verpolschutz", "Verlustleistung", "P-MOSFET", "Schottky", "RDS(on)"],
        "wissensseite": "verpolschutz"},
    "schaltung_freilauf": {
        "titel": "Freilaufdiode am Relais (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Transistor schaltet eine Spule ab: ohne Diode, mit Freilaufdiode, mit Diode + Z-Diode.",
        "stichworte": ["Freilaufdiode", "Relais", "Abschaltspannung", "Z-Diode", "Spule"],
        "wissensseite": "freilaufdiode"},
    "schaltung_gleichrichter": {
        "titel": "Gleichrichter mit Ladeelko (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Einweg, Brücke, Mittelpunkt: Spannung am Elko über der Zeit, Welligkeit, Sperrspannung.",
        "stichworte": ["Gleichrichter", "Brückengleichrichter", "Graetz", "Mittelpunkt", "Ladeelko", "Brummspannung"],
        "wissensseite": "gleichrichter_ladeelko"},
    "schaltung_zstabi": {
        "titel": "Z-Dioden-Stabilisierung (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Eingangsspannung und Last verändern – wann reisst die Stabilisierung ab?",
        "stichworte": ["Z-Diode", "Zener", "Stabilisierung", "Vorwiderstand", "Schaltplan"],
        "wissensseite": "z_stabilisierung"},
    "schaltung_tvs": {
        "titel": "TVS-Diode gegen Spannungsspitzen (interaktiv)", "kategorie": "Schaltungen",
        "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Stossspannung 1.2/50 µs mit und ohne TVS, Klemmspannung, Pulsstrom, Pulsleistung.",
        "stichworte": ["TVS", "Suppressordiode", "Surge", "Überspannung", "Transient", "ESD"],
        "wissensseite": "tvs_schutz"},
    "tvs_auswahl": {
        "titel": "TVS-Diode prüfen", "kategorie": "Schaltungen", "unterkategorie": "Dioden & Schutz",
        "beschreibung": "Passen U_WM, U_C und I_PP zu Betriebsspannung, Störspitze und Gerät?",
        "stichworte": ["TVS", "Suppressordiode", "Stand-off", "Klemmspannung", "IPP"],
        "wissensseite": "tvs_schutz"},
    "led_vorwiderstand": {
        "titel": "LED-Vorwiderstand", "kategorie": "Schaltungen", "unterkategorie": "Vorwiderstände",
        "beschreibung": "Vorwiderstand für eine oder mehrere LEDs in Reihe, mit Normwert.",
        "stichworte": ["LED", "Vorwiderstand", "Leuchtdiode", "Uf", "If"],
        "wissensseite": "led"},
    "rc_filter": {
        "titel": "RC-Filter (Tief-/Hochpass)", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "Grenzfrequenz oder fehlendes R bzw. C eines RC-Glieds.",
        "stichworte": ["Tiefpass", "Hochpass", "Grenzfrequenz", "fg", "-3 dB", "Filter"],
        "wissensseite": "rc_tiefpass_hochpass"},
    "bjt_schalter": {
        "titel": "Transistor als Schalter: Basiswiderstand (kurz)", "kategorie": "Schaltungen", "unterkategorie": "Schalten",
        "beschreibung": "Basiswiderstand für einen NPN-Schalter mit E24-Normwert.",
        "stichworte": ["NPN", "Basiswiderstand", "Schalter", "Übersteuerung", "Mikrocontroller"],
        "wissensseite": "bipolartransistor"},
    "basiswiderstand": {
        "titel": "Basiswiderstand NPN/PNP (ausführlich)", "kategorie": "Schaltungen", "unterkategorie": "Schalten",
        "beschreibung": "Basiswiderstand für NPN Low-Side oder PNP High-Side mit E12-Normwert und Verlusten.",
        "stichworte": ["NPN", "PNP", "Basiswiderstand", "Low-Side", "High-Side", "Übersteuerung"],
        "wissensseite": "bipolartransistor"},
    "relais_ansteuerung": {
        "titel": "Relais mit Transistor ansteuern", "kategorie": "Schaltungen", "unterkategorie": "Schalten",
        "beschreibung": "Spulenstrom, Basiswiderstand und Freilaufdiode für ein Relais am µC.",
        "stichworte": ["Relais", "Transistor", "Basiswiderstand", "Freilaufdiode", "Mikrocontroller"],
        "wissensseite": "relais"},
    "freilauf": {
        "titel": "Freilaufdiode & Abschalten", "kategorie": "Schaltungen", "unterkategorie": "Schalten",
        "beschreibung": "Nur Diode oder Diode + Z-Diode: Spannung am Transistor gegen Abfallzeit.",
        "stichworte": ["Freilaufdiode", "Z-Diode", "Abschalten", "Induktive Last", "Abfallzeit"],
        "wissensseite": "freilaufdiode"},
    "schaltung_lasttreiber": {
        "titel": "LED, Relais, Motor am µC (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Schalten",
        "beschreibung": "Low-Side-Schalter mit NPN oder N-MOSFET: Vorwiderstand, Freilaufdiode, Anlaufstrom, Pin-Strom.",
        "stichworte": ["Low-Side", "Relais", "Motor", "LED", "Treiber", "MOSFET", "Mikrocontroller"],
        "wissensseite": "lasten_ansteuern"},
    "schaltung_emitter": {
        "titel": "Emitterschaltung (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Verstärker",
        "beschreibung": "Arbeitspunkt, Verstärkung mit/ohne C_E und Übersteuerung im Zeitdiagramm.",
        "stichworte": ["Emitterschaltung", "Verstärker", "Arbeitspunkt", "C_E", "Übersteuerung", "Phasendrehung"],
        "wissensseite": "emitterschaltung"},
    "schaltung_emitterfolger": {
        "titel": "Emitterfolger (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Verstärker",
        "beschreibung": "Ua = Ue − 0.7 V, Strom- statt Spannungsverstärkung, Abschneiden bei 0 V.",
        "stichworte": ["Emitterfolger", "Kollektorschaltung", "Impedanzwandler", "Puffer"],
        "wissensseite": "emitterfolger"},
    "emitterfolger": {
        "titel": "Emitterfolger", "kategorie": "Schaltungen", "unterkategorie": "Verstärker",
        "beschreibung": "Ausgangsspannung, Ströme, Ein- und Ausgangswiderstand und Verlust der Kollektorschaltung.",
        "stichworte": ["Emitterfolger", "Kollektorschaltung", "Impedanzwandler", "Eingangswiderstand"],
        "wissensseite": "emitterfolger"},
    "schaltung_konstantstrom": {
        "titel": "Konstantstromquelle (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Stromquellen",
        "beschreibung": "Transistor + Z-Diode oder JFET + R_S: Strom über der Last mit Arbeitsbereich.",
        "stichworte": ["Konstantstromquelle", "Stromquelle", "JFET", "Arbeitsbereich", "Kennlinie"],
        "wissensseite": "konstantstromquelle"},
    "konstantstrom": {
        "titel": "Konstantstromquelle dimensionieren", "kategorie": "Schaltungen", "unterkategorie": "Stromquellen",
        "beschreibung": "R_E bzw. R_S für einen gewünschten Strom, mit Normwert und Arbeitsbereich.",
        "stichworte": ["Konstantstromquelle", "Stromquelle", "JFET", "R_S", "LED-Treiber"],
        "wissensseite": "konstantstromquelle"},
    "rc_frequenzgang": {
        "titel": "RC-Tief-/Hochpass: Frequenzgang", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "Betrag, Dämpfung in dB, Phase und Ausgangsspannung bei einer bestimmten Frequenz.",
        "stichworte": ["Tiefpass", "Hochpass", "Frequenzgang", "Phase", "Dämpfung", "dB", "Bode"],
        "wissensseite": "rc_tiefpass_hochpass"},
    "schaltung_rc_filter": {
        "titel": "RC-Tiefpass und -Hochpass (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "Betragsgang mit Punkt für die eingestellte Frequenz und Sinus am Ein- und Ausgang.",
        "stichworte": ["Tiefpass", "Hochpass", "Bode", "Grenzfrequenz", "Phasenverschiebung"],
        "wissensseite": "rc_tiefpass_hochpass"},
    "entprellung": {
        "titel": "Taster entprellen (RC + Schmitt-Trigger)", "kategorie": "Schaltungen", "unterkategorie": "Digital-Eingänge",
        "beschreibung": "Zeiten bis zu den Schmitt-Trigger-Schwellen beim Drücken und Loslassen, passendes C.",
        "stichworte": ["Entprellung", "Prellen", "Debounce", "Schmitt-Trigger", "Taster", "74HC14"],
        "wissensseite": "tasterentprellung"},
    "schaltung_entprellung": {
        "titel": "Taster entprellen (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Digital-Eingänge",
        "beschreibung": "Prellender Kontakt, Spannung am Kondensator und erkannte Tastendrücke im Zeitdiagramm.",
        "stichworte": ["Entprellung", "Prellen", "Hysterese", "Schmitt-Trigger", "Zeitdiagramm"],
        "wissensseite": "tasterentprellung"},
    "anti_aliasing": {
        "titel": "Anti-Aliasing (RC vor dem ADC)", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "Alias-Frequenz nach dem Abtasten, Dämpfung des RC-Tiefpasses und nötige Dämpfung für N Bit.",
        "stichworte": ["Aliasing", "Nyquist", "Abtastrate", "ADC", "Abtasttheorem", "Tiefpass"],
        "wissensseite": "anti_aliasing_filter"},
    "schaltung_anti_aliasing": {
        "titel": "Anti-Aliasing vor dem ADC (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "Abtastpunkte und falsch erkannte Frequenz – mit und ohne RC-Tiefpass.",
        "stichworte": ["Aliasing", "Nyquist", "Abtastung", "ADC", "Zeitdiagramm"],
        "wissensseite": "anti_aliasing_filter"},
    "opv_verstaerker": {
        "titel": "OPV-Verstärker", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Folger, nichtinvertierend, invertierend: Verstärkung, Ua, Eingangswiderstand, Bandbreite – oder R2 aus Vu.",
        "stichworte": ["OPV", "Operationsverstärker", "Verstärkung", "nichtinvertierend", "invertierend", "GBW"],
        "wissensseite": "opv_verstaerker"},
    "schaltung_opv_verstaerker": {
        "titel": "OPV als Verstärker (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Drei Grundschaltungen mit Zeitdiagramm, Übersteuerung und Rail-to-Rail-Vergleich.",
        "stichworte": ["OPV", "Spannungsfolger", "virtuelle Masse", "Übersteuerung", "Rail-to-Rail"],
        "wissensseite": "opv_verstaerker"},
    "opv_addierer": {
        "titel": "OPV-Addierer", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Gewichtete Summe beliebig vieler Eingänge mit Strömen und Begrenzung.",
        "stichworte": ["Addierer", "Summierer", "Summierverstärker", "Mischpult"],
        "wissensseite": "opv_addierer"},
    "schaltung_addierer": {
        "titel": "Addierer (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Drei Eingänge, Ströme in den Summenknoten und Ausgang.",
        "stichworte": ["Addierer", "Summierer", "virtuelle Masse", "Ströme"],
        "wissensseite": "opv_addierer"},
    "differenzverstaerker": {
        "titel": "Differenz- / Instrumentenverstärker", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Ausgang, Gleichtaktfehler und CMRR bei Widerstandstoleranz, Verstärkung über R_G.",
        "stichworte": ["Differenzverstärker", "Instrumentenverstärker", "INA", "CMRR", "Gleichtakt"],
        "wissensseite": "differenz_instrumentenverstaerker"},
    "schaltung_differenz": {
        "titel": "Differenz- und Instrumentenverstärker (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Gleichtakt und Differenz getrennt einstellen, Toleranz und R_G verändern.",
        "stichworte": ["Differenzverstärker", "Instrumentenverstärker", "Gleichtakt", "Toleranz"],
        "wissensseite": "differenz_instrumentenverstaerker"},
    "schmitt_trigger": {
        "titel": "Schmitt-Trigger mit OPV", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Schaltschwellen und Hysterese berechnen oder R1 und U_ref für gewünschte Schwellen auslegen.",
        "stichworte": ["Schmitt-Trigger", "Hysterese", "Komparator", "Schaltschwelle", "Mitkopplung"],
        "wissensseite": "komparator_schmitt_trigger"},
    "schaltung_schmitt": {
        "titel": "Komparator und Schmitt-Trigger (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Verrauschter Sinus: Komparator flattert, Schmitt-Trigger schaltet einmal.",
        "stichworte": ["Komparator", "Schmitt-Trigger", "Flattern", "Hysterese", "Zeitdiagramm"],
        "wissensseite": "komparator_schmitt_trigger"},
    "integrator": {
        "titel": "Integrator / Differenzierer", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Steigung, Dreieck- bzw. Rechteckamplitude und Grenzfrequenzen mit R_p bzw. R_s.",
        "stichworte": ["Integrator", "Differenzierer", "Rampe", "Dreieck", "R_p"],
        "wissensseite": "integrator_differenzierer"},
    "schaltung_integrator": {
        "titel": "Integrator und Differenzierer (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "OPV",
        "beschreibung": "Rechteck zu Dreieck und zurück, Drift durch Offset, praxisgerechte Beschaltung.",
        "stichworte": ["Integrator", "Differenzierer", "Drift", "Offset", "Zeitdiagramm"],
        "wissensseite": "integrator_differenzierer"},
    "innenwiderstand": {
        "titel": "Innenwiderstand einer Quelle", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "R_i aus Leerlauf- und Lastmessung, Klemmenspannung, Leistung und Wirkungsgrad an einer Last.",
        "stichworte": ["Innenwiderstand", "Klemmenspannung", "Leistungsanpassung", "Kurzschlussstrom"],
        "wissensseite": "quellenmodell"},
    "schaltung_quelle": {
        "titel": "Reale Quelle mit Innenwiderstand (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Spannungs- und Stromquellenmodell, Kennlinien über der Last, Leistungsanpassung.",
        "stichworte": ["Innenwiderstand", "Thevenin", "Norton", "Leistungsanpassung"],
        "wissensseite": "quellenmodell"},
    "netzteil_auslegen": {
        "titel": "Netzteil auslegen (Trafo, Elko)", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Vom Ausgang rückwärts: Trafospannung, Elko, Trafoleistung und Elko-Spannung mit Netztoleranz.",
        "stichworte": ["Netzteil", "Trafo", "Ladeelko", "Welligkeit", "Netztoleranz"],
        "wissensseite": "netzteil_ungeregelt"},
    "linearregler": {
        "titel": "Linearregler (78xx / LDO / LM317)", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Dropout im Wellental, Verlustleistung, Wirkungsgrad und Sperrschichttemperatur.",
        "stichworte": ["Linearregler", "7805", "LDO", "Dropout", "Verlustleistung"],
        "wissensseite": "linearregler"},
    "schaltung_linearregler": {
        "titel": "Linearregler hinter dem Elko (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Wellental gegen Dropout, Ausgang im Zeitdiagramm, Temperatur mit und ohne Kühlkörper.",
        "stichworte": ["Linearregler", "Dropout", "Welligkeit", "LM317"],
        "wissensseite": "linearregler"},
    "lm317": {
        "titel": "LM317 einstellen", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Ausgangsspannung aus R1/R2 oder R2 für eine gewünschte Spannung.",
        "stichworte": ["LM317", "einstellbarer Regler", "R1", "R2", "ADJ"],
        "wissensseite": "linearregler"},
    "strombegrenzung": {
        "titel": "Strombegrenzung (Shunt + Transistor)", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Shunt für einen Maximalstrom und Verlust im Längstransistor bei Kurzschluss.",
        "stichworte": ["Strombegrenzung", "Kurzschlussschutz", "Shunt", "Längsregler"],
        "wissensseite": "strombegrenzung"},
    "schaltung_strombegrenzung": {
        "titel": "Längsregler mit Strombegrenzung (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Z-Diode + Transistor, Begrenzungstransistor und U-I-Kennlinie.",
        "stichworte": ["Strombegrenzung", "Längsregler", "Kennlinie", "Kurzschluss"],
        "wissensseite": "strombegrenzung"},
    "stromquelle_opv": {
        "titel": "Geregelte Stromquelle (OPV + MOSFET)", "kategorie": "Schaltungen", "unterkategorie": "Stromquellen",
        "beschreibung": "Shunt, Sollspannung, Arbeitsbereich und MOSFET-Verlust einer Stromsenke.",
        "stichworte": ["Stromquelle", "Stromsenke", "elektronische Last", "Shunt", "OPV"],
        "wissensseite": "geregelte_stromquelle"},
    "schaltung_stromquelle_opv": {
        "titel": "Geregelte Stromquelle (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Stromquellen",
        "beschreibung": "OPV + MOSFET + Shunt mit Kennlinie Strom über der Last.",
        "stichworte": ["Stromquelle", "OPV", "MOSFET", "Kennlinie"],
        "wissensseite": "geregelte_stromquelle"},
    "schaltung_virtuelle_masse": {
        "titel": "Virtuelle Masse / Rail-Splitter (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "±U aus einer Versorgung: Teiler mit und ohne OPV-Puffer bei ungleicher Last.",
        "stichworte": ["virtuelle Masse", "Rail-Splitter", "bipolare Versorgung", "±U"],
        "wissensseite": "bipolare_versorgung"},
    "schaltregler": {
        "titel": "Schaltregler Buck / Boost", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Tastgrad, Spule, Rippelstrom, Spitzenstrom und Ausgangswelligkeit.",
        "stichworte": ["Schaltregler", "Buck", "Boost", "DC-DC", "Tastgrad", "Spule"],
        "wissensseite": "schaltregler_buck_boost"},
    "schaltung_schaltregler": {
        "titel": "Schaltregler Buck / Boost (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Spulenstrom und Schaltknoten über zwei Perioden, Dauer- und Lückbetrieb.",
        "stichworte": ["Schaltregler", "Buck", "Boost", "Spulenstrom", "DCM"],
        "wissensseite": "schaltregler_buck_boost"},
    "zahlensystem": {
        "titel": "Zahlensysteme umrechnen", "kategorie": "Digitaltechnik", "unterkategorie": "Zahlen & Codes",
        "beschreibung": "Dezimal, Binär, Hex, Oktal, BCD, Gray und ASCII – mit Präfix-Erkennung.",
        "stichworte": ["Binär", "Hex", "Hexadezimal", "Oktal", "BCD", "Gray", "Umrechnen"],
        "wissensseite": "zahlensysteme_codes"},
    "werkzeug_zahlensystem": {
        "titel": "Zahlensysteme (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Zahlen & Codes",
        "beschreibung": "Bits anklicken oder Zahl eintippen – alle Schreibweisen gleichzeitig.",
        "stichworte": ["Bits", "Binär", "Hex", "Umrechnen", "Werkzeug"],
        "wissensseite": "zahlensysteme_codes"},
    "zweierkomplement": {
        "titel": "Zweierkomplement", "kategorie": "Digitaltechnik", "unterkategorie": "Zahlen & Codes",
        "beschreibung": "Negative Zahl als Bitmuster mit Rechenweg – oder Bitmuster als signed lesen.",
        "stichworte": ["Zweierkomplement", "signed", "negative Zahlen", "Vorzeichen"],
        "wissensseite": "zweierkomplement_ueberlauf"},
    "binaer_addieren": {
        "titel": "Binär addieren mit Carry und Overflow", "kategorie": "Digitaltechnik", "unterkategorie": "Zahlen & Codes",
        "beschreibung": "Summe mit n Bit, Carry-Flag (unsigned) und Overflow-Flag (signed).",
        "stichworte": ["Addition", "Carry", "Overflow", "Überlauf", "Flags"],
        "wissensseite": "zweierkomplement_ueberlauf"},
    "werkzeug_zweierkomplement": {
        "titel": "Zahlenkreis und Überlauf (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Zahlen & Codes",
        "beschreibung": "4- und 8-Bit-Zahlenkreis mit signed/unsigned, Addition, C- und V-Grenze.",
        "stichworte": ["Zahlenkreis", "Zweierkomplement", "Overflow", "Carry"],
        "wissensseite": "zweierkomplement_ueberlauf"},
    "bitmaske": {
        "titel": "Bitmaske anwenden", "kategorie": "Digitaltechnik", "unterkategorie": "Zahlen & Codes",
        "beschreibung": "Register-Bits setzen, löschen, umschalten, prüfen oder schieben – mit C-Ausdruck.",
        "stichworte": ["Bitmaske", "Register", "AND", "OR", "XOR", "Shift"],
        "wissensseite": "bitmasken"},
    "werkzeug_bitmaske": {
        "titel": "Bitmasken (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Zahlen & Codes",
        "beschreibung": "Register und Maske anklicken, geänderte Bits sehen.",
        "stichworte": ["Bitmaske", "Register", "Bit setzen", "Bit löschen"],
        "wissensseite": "bitmasken"},
    "logikpegel": {
        "titel": "Logikpegel-Kompatibilität", "kategorie": "Digitaltechnik", "unterkategorie": "Logikpegel",
        "beschreibung": "Störabstände S_H und S_L und Spannungsfestigkeit zwischen zwei Logikfamilien.",
        "stichworte": ["Logikpegel", "Störabstand", "3.3 V", "5 V", "Pegelwandler", "74HCT"],
        "wissensseite": "logikpegel_stoerabstand"},
    "werkzeug_logikpegel": {
        "titel": "Logikpegel und Störabstand (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Logikpegel",
        "beschreibung": "Pegelbänder von Sender und Empfänger nebeneinander, Störabstände als Pfeile.",
        "stichworte": ["Logikpegel", "Störabstand", "U_IH", "U_OH", "Werkzeug"],
        "wissensseite": "logikpegel_stoerabstand"},
    "wahrheitstabelle": {
        "titel": "Wahrheitstabelle und Normalformen", "kategorie": "Digitaltechnik", "unterkategorie": "Logik",
        "beschreibung": "Boolescher Ausdruck -> Tabelle, Minterme, kanonische und minimale DNF/KNF.",
        "stichworte": ["Wahrheitstabelle", "DNF", "KNF", "Minterm", "boolescher Ausdruck"],
        "wissensseite": "normalformen"},
    "werkzeug_ausdruck": {
        "titel": "Ausdruck → Wahrheitstabelle (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Logik",
        "beschreibung": "Ausdruck eintippen, Symbol-Knöpfe, Tabelle und alle Normalformen sofort.",
        "stichworte": ["Wahrheitstabelle", "Ausdruck", "Normalform", "Werkzeug"],
        "wissensseite": "boolesche_algebra"},
    "ausdruck_vergleichen": {
        "titel": "Zwei Ausdrücke vergleichen", "kategorie": "Digitaltechnik", "unterkategorie": "Logik",
        "beschreibung": "Prüft eine Umformung (z.B. De Morgan) über alle Belegungen, sonst Gegenbeispiel.",
        "stichworte": ["De Morgan", "Umformen", "Äquivalenz", "Vergleichen", "boolesche Algebra"],
        "wissensseite": "boolesche_algebra"},
    "kv_minimieren": {
        "titel": "Minimieren aus Mintermen", "kategorie": "Digitaltechnik", "unterkategorie": "Logik",
        "beschreibung": "Minimale DNF und KNF aus Mintermen und don't cares (Quine-McCluskey), bis 6 Variablen.",
        "stichworte": ["KV-Diagramm", "Quine-McCluskey", "Minimieren", "don't care", "Minterm"],
        "wissensseite": "kv_diagramme"},
    "werkzeug_kv": {
        "titel": "KV-Diagramm (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Logik",
        "beschreibung": "Felder anklicken (0/1/X), Blöcke und minimale Form werden eingezeichnet.",
        "stichworte": ["KV-Diagramm", "Karnaugh", "Block", "don't care", "Werkzeug"],
        "wissensseite": "kv_diagramme"},
    "werkzeug_gatter": {
        "titel": "Logikgatter-Simulator (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Logik",
        "beschreibung": "AND bis XNOR mit 2 oder 3 Eingängen, IEC- und ANSI-Symbol, Wahrheitstabelle.",
        "stichworte": ["Gatter", "AND", "OR", "XOR", "NAND", "Symbol", "Werkzeug"],
        "wissensseite": "logikgatter"},
    "addierer_laufzeit": {
        "titel": "Ripple-Carry-Addierer: Laufzeit", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltnetze",
        "beschreibung": "Worst-Case-Laufzeit der Übertragskette und höchste Taktfrequenz.",
        "stichworte": ["Addierer", "Ripple Carry", "Laufzeit", "Übertrag", "Taktfrequenz"],
        "wissensseite": "addierer"},
    "werkzeug_addierer": {
        "titel": "Addierwerk aus Volladdierern (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltnetze",
        "beschreibung": "4- oder 8-Bit-Addierer/Subtrahierer, Übertragskette und Flags sichtbar.",
        "stichworte": ["Volladdierer", "Addierer", "Subtraktion", "Carry", "Werkzeug"],
        "wissensseite": "addierer"},
    "mux_funktion": {
        "titel": "Logikfunktion mit Multiplexer", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltnetze",
        "beschreibung": "Belegung der Dateneingänge D0 … Dn für einen beliebigen Ausdruck (Shannon-Zerlegung).",
        "stichworte": ["Multiplexer", "MUX", "Shannon", "Logikfunktion", "Dateneingang"],
        "wissensseite": "multiplexer"},
    "werkzeug_mux": {
        "titel": "Multiplexer / Demultiplexer (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltnetze",
        "beschreibung": "4:1-MUX und 1:4-DEMUX mit hervorgehobenem Datenweg.",
        "stichworte": ["Multiplexer", "Demultiplexer", "Auswahl", "Select", "Werkzeug"],
        "wissensseite": "multiplexer"},
    "siebensegment": {
        "titel": "7-Segment-Code", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltnetze",
        "beschreibung": "Segmente a … g und Pegel für eine Hex-Ziffer, gemeinsame Kathode oder Anode.",
        "stichworte": ["7-Segment", "Siebensegment", "Anzeige", "gemeinsame Anode", "gemeinsame Kathode"],
        "wissensseite": "decoder_encoder"},
    "adressdecoder": {
        "titel": "Adressdecodierung (Chip-Select)", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltnetze",
        "beschreibung": "Adressbereiche der Decoder-Ausgänge bei N Adressbits und k Decoder-Eingängen.",
        "stichworte": ["Adressdecoder", "Chip-Select", "74HC138", "Speicher", "Adressraum"],
        "wissensseite": "decoder_encoder"},
    "werkzeug_decoder": {
        "titel": "Decoder, Encoder, 7-Segment (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltnetze",
        "beschreibung": "3:8-Decoder mit Freigabe, Prioritäts-Encoder und 7-Segment-Anzeige zum Anklicken.",
        "stichworte": ["Decoder", "Encoder", "Prioritäts-Encoder", "7-Segment", "Werkzeug"],
        "wissensseite": "decoder_encoder"},
    "open_drain_pullup": {
        "titel": "Pull-up für Open Drain / I²C", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltnetze",
        "beschreibung": "R_min aus dem LOW-Strom, R_max aus der Anstiegszeit nach I²C-Spezifikation.",
        "stichworte": ["Open Drain", "I²C", "Pull-up", "Anstiegszeit", "Buskapazität"],
        "wissensseite": "ausgangstypen"},
    "werkzeug_ausgang": {
        "titel": "Ausgangstypen an einer Leitung (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltnetze",
        "beschreibung": "Push-Pull, Open Drain und Tri-State: Buskonflikt, Wired-AND, Anstieg mit Pull-up.",
        "stichworte": ["Push-Pull", "Open Drain", "Tri-State", "Buskonflikt", "Werkzeug"],
        "wissensseite": "ausgangstypen"},
    "zaehler_entwurf": {
        "titel": "Synchronen Zähler entwerfen", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltwerke",
        "beschreibung": "Zustandsfolge -> minimierte Ansteuergleichungen für D- oder JK-Flipflops, mit Selbststart-Prüfung.",
        "stichworte": ["Zählerentwurf", "synchroner Zähler", "Ansteuergleichung", "JK-Flipflop", "D-Flipflop", "Selbststart"],
        "wissensseite": "zaehler_entwurf"},
    "fmax_schaltwerk": {
        "titel": "Höchste Taktfrequenz (synchron)", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltwerke",
        "beschreibung": "T_min aus t_pd, Logik, Setup und Taktversatz; Hold-Prüfung.",
        "stichworte": ["Taktfrequenz", "Setup", "Hold", "t_pd", "Timing", "f_max"],
        "wissensseite": "flipflops"},
    "frequenzteiler": {
        "titel": "Frequenzteiler mit Flipflops", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltwerke",
        "beschreibung": "Ausgangsfrequenz und Anzahl Flipflops für einen Teiler durch m.",
        "stichworte": ["Frequenzteiler", "Teiler", "Flipflop", "Zähler", "Uhrenquarz"],
        "wissensseite": "zaehler"},
    "werkzeug_flipflop": {
        "titel": "Flipflops und Latches (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltwerke",
        "beschreibung": "RS, D-Latch, D, JK, T: Eingänge setzen, Takt geben, Zeitdiagramm.",
        "stichworte": ["Flipflop", "Latch", "Takt", "Zeitdiagramm", "Werkzeug"],
        "wissensseite": "flipflops"},
    "werkzeug_zaehler": {
        "titel": "Zähler asynchron/synchron (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltwerke",
        "beschreibung": "Zeitdiagramm mit Zwischenzuständen des Ripple-Zählers, Modulo und Richtung einstellbar.",
        "stichworte": ["Zähler", "Ripple", "Modulo", "Glitch", "Werkzeug"],
        "wissensseite": "zaehler"},
    "werkzeug_schieberegister": {
        "titel": "Schieberegister (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Schaltwerke",
        "beschreibung": "SIPO, Ring- und Johnson-Zähler Takt für Takt mit Zeitdiagramm.",
        "stichworte": ["Schieberegister", "Ringzähler", "Johnson-Zähler", "SIPO", "Werkzeug"],
        "wissensseite": "schieberegister"},
    "uart_timing": {
        "titel": "UART: Bitzeit und Datenrate", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "Bitzeit, Rahmenzeit, Zeichen pro Sekunde und Taktoleranz eines Formats wie 8N1.",
        "stichworte": ["UART", "Baudrate", "8N1", "Bitzeit", "Rahmen", "seriell", "RS-232", "RS-485"],
        "wissensseite": "uart"},
    "uart_baudrate": {
        "titel": "UART: Baudraten-Teiler und Fehler", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "Teiler N = f / (16 · Baudrate), tatsächliche Baudrate und Fehler in % (AVR: UBRR).",
        "stichworte": ["UART", "Baudrate", "UBRR", "Baudratenfehler", "Quarz", "Teiler"],
        "wissensseite": "uart"},
    "spi_uebertragung": {
        "titel": "SPI: Modus und Übertragungsdauer", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "CPOL/CPHA, Abtastflanke und Dauer von n Bytes bei gegebenem SCLK.",
        "stichworte": ["SPI", "CPOL", "CPHA", "SPI-Modus", "SCLK", "MOSI", "MISO"],
        "wissensseite": "spi"},
    "i2c_uebertragung": {
        "titel": "I²C: Dauer einer Übertragung", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "Takte, Dauer und Nutzdatenrate beim Schreiben, Lesen oder Register-Lesen.",
        "stichworte": ["I²C", "I2C", "TWI", "SCL", "Übertragungsdauer", "Register lesen"],
        "wissensseite": "i2c"},
    "speicher_organisation": {
        "titel": "Speicher: Organisation und Kapazität", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "Aus Adress- und Datenbits: Anzahl Wörter, Kapazität in Bit/Byte, Adressbereich.",
        "stichworte": ["Speicher", "Kapazität", "Adressbits", "Datenbits", "RAM", "ROM", "Organisation"],
        "wissensseite": "speicher"},
    "speicher_erweitern": {
        "titel": "Speicher erweitern (Tiefe und Wortbreite)", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "Wie viele Chips, welche Adressbits an den Decoder?",
        "stichworte": ["Speichererweiterung", "Wortbreite", "Chip Select", "Decoder", "RAM", "Speicherchip"],
        "wissensseite": "speicher"},
    "werkzeug_uart": {
        "titel": "UART-Rahmen (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "Zeichen eingeben -> Startbit, Daten LSB zuerst, Parität, Stoppbit; TTL- und RS-232-Pegel.",
        "stichworte": ["UART", "Rahmen", "Zeitdiagramm", "Parität", "RS-232", "Werkzeug"],
        "wissensseite": "uart"},
    "werkzeug_spi": {
        "titel": "SPI-Übertragung (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "Modus 0 … 3 mit CS, SCLK, MOSI, MISO und Abtastflanken im Zeitdiagramm.",
        "stichworte": ["SPI", "Zeitdiagramm", "CPOL", "CPHA", "Werkzeug"],
        "wissensseite": "spi"},
    "werkzeug_i2c": {
        "titel": "I²C-Übertragung (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "START, Adresse, R/W, ACK/NACK, Daten und STOP auf SDA und SCL.",
        "stichworte": ["I²C", "I2C", "Zeitdiagramm", "ACK", "START", "STOP", "Werkzeug"],
        "wissensseite": "i2c"},
    "werkzeug_speicher": {
        "titel": "Speicherbaustein (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "Busse und Speicher",
        "beschreibung": "Adresse wählen, lesen und schreiben, Steuersignale CS/OE/WE sehen.",
        "stichworte": ["Speicher", "RAM", "Adresse", "CS", "OE", "WE", "Werkzeug"],
        "wissensseite": "speicher"},
    "lc_filter": {
        "titel": "LC-Tiefpass mit Last", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "f0, Kennwiderstand, Güte Q aus der Last, Überhöhung, −3-dB-Frequenz.",
        "stichworte": ["LC-Filter", "Tiefpass", "Güte", "Überhöhung", "Filter 2. Ordnung", "Z0"],
        "wissensseite": "lc_tiefpass"},
    "schwingkreis_filter": {
        "titel": "Schwingkreis als Bandpass / Bandsperre", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "RLC-Reihenkreis: f0, Q, Bandbreite und die beiden −3-dB-Frequenzen.",
        "stichworte": ["Bandpass", "Bandsperre", "Kerbfilter", "Schwingkreis", "Bandbreite", "Güte"],
        "wissensseite": "bandpass_bandsperre"},
    "sallen_key": {
        "titel": "Sallen-Key-Filter auslegen", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "Aktiver Tief-/Hochpass 2. Ordnung: Bauteile für f0 und Bessel/Butterworth/Tschebyscheff, mit Normwerten.",
        "stichworte": ["Sallen-Key", "aktives Filter", "Butterworth", "Bessel", "Tschebyscheff", "OPV-Filter"],
        "wissensseite": "aktive_filter_sallen_key"},
    "schaltung_lc_filter": {
        "titel": "LC-Tiefpass (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "Bode-Diagramm und Sprungantwort: Wie die Last die Güte und das Überschwingen bestimmt.",
        "stichworte": ["LC-Tiefpass", "Bode", "Sprungantwort", "Güte", "Simulation"],
        "wissensseite": "lc_tiefpass"},
    "schaltung_schwingkreis": {
        "titel": "Schwingkreis Bandpass/Bandsperre (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "RLC-Reihenkreis mit Ausgang am R oder an L + C, Bode-Diagramm und Zeitverlauf.",
        "stichworte": ["Bandpass", "Bandsperre", "Schwingkreis", "Bode", "Simulation"],
        "wissensseite": "bandpass_bandsperre"},
    "schaltung_sallen_key": {
        "titel": "Sallen-Key-Filter (interaktiv)", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "Tief- und Hochpass mit OPV: Q über die Bauteile einstellen, Bode und Sprungantwort.",
        "stichworte": ["Sallen-Key", "aktives Filter", "Bode", "Sprungantwort", "Simulation"],
        "wissensseite": "aktive_filter_sallen_key"},
    "bjt_arbeitspunkt": {
        "titel": "Arbeitspunkt Emitterschaltung", "kategorie": "Schaltungen", "unterkategorie": "Verstärker",
        "beschreibung": "Basisteiler, Kollektorstrom, U_CE und Verstärkung einer Emitterschaltung.",
        "stichworte": ["Emitterschaltung", "Arbeitspunkt", "Basisteiler", "Verstärker", "Gegenkopplung"],
        "wissensseite": "emitterschaltung"},

    "gleichrichter": {
        "titel": "Gleichrichter mit Ladeelko", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Gleichspannung, Welligkeit und Sperrspannung für Einweg, Brücke und Mittelpunkt.",
        "stichworte": ["Brücke", "Einweg", "Mittelpunkt", "Elko", "Brummspannung", "Graetz"],
        "wissensseite": "gleichrichter_ladeelko"},
    "netzteil": {
        "titel": "Trafo + Gleichrichter + Elko", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Was kommt nach Trafo und Brückengleichrichter heraus? Ladeelko dimensionieren.",
        "stichworte": ["Netzteil", "Ladeelko", "Welligkeit", "Brücke", "Spitzenwert"],
        "wissensseite": "netzteil_ungeregelt"},
    "zdiode_stabi": {
        "titel": "Z-Dioden-Stabilisierung", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Vorwiderstand und Belastung der Z-Diode im ungünstigsten Fall.",
        "stichworte": ["Z-Diode", "Zener", "Stabilisierung", "Vorwiderstand", "Glättungsfaktor"],
        "wissensseite": "z_stabilisierung"},
    # =========================================================================
    # MESSTECHNIK
    # =========================================================================
    "statistik": {
        "titel": "Messreihe auswerten", "kategorie": "Messtechnik", "unterkategorie": "Messunsicherheit",
        "beschreibung": "Mittelwert, Standardabweichung und Vertrauensbereich einer Messreihe.",
        "stichworte": ["Statistik", "Mittelwert", "Standardabweichung", "Student-t", "Vertrauensbereich"],
        "wissensseite": "messunsicherheit"},
    "dmm_genauigkeit": {
        "titel": "Multimeter-Genauigkeit", "kategorie": "Messtechnik", "unterkategorie": "Messunsicherheit",
        "beschreibung": "Fehlergrenze aus % vom Messwert + Digits.",
        "stichworte": ["Multimeter", "DMM", "Genauigkeit", "Digits", "Fehlergrenze"],
        "wissensseite": "messunsicherheit"},
    "fehlerfortpflanzung": {
        "titel": "Fehlerfortpflanzung", "kategorie": "Messtechnik", "unterkategorie": "Messunsicherheit",
        "beschreibung": "Unsicherheit von Produkt, Quotient, Summe und Differenz.",
        "stichworte": ["Fehlerfortpflanzung", "Unsicherheit", "Worst Case", "Gauss"],
        "wissensseite": "messunsicherheit"},
    "signalform": {
        "titel": "Effektivwert & Mittelwert", "kategorie": "Messtechnik", "unterkategorie": "Signale",
        "beschreibung": "Effektiv-, Mittel- und Gleichrichtwert, Crest- und Formfaktor je Signalform.",
        "stichworte": ["Effektivwert", "RMS", "True RMS", "Mittelwert", "Formfaktor", "Crestfaktor"],
        "wissensseite": "signalkenngroessen"},
    "oszi": {
        "titel": "Oszilloskop: Bandbreite & Anstiegszeit", "kategorie": "Messtechnik", "unterkategorie": "Signale",
        "beschreibung": "Eigene Anstiegszeit, Amplitudenfehler und angezeigte Anstiegszeit.",
        "stichworte": ["Oszilloskop", "Bandbreite", "Anstiegszeit", "Abtastrate", "Tastkopf"],
        "wissensseite": "oszilloskop"},
    "messbereich": {
        "titel": "Messbereich erweitern", "kategorie": "Messtechnik", "unterkategorie": "Messgeräte",
        "beschreibung": "Vorwiderstand und Shunt für ein Drehspul-Messwerk.",
        "stichworte": ["Vorwiderstand", "Shunt", "Messwerk", "Messbereich", "Ohm pro Volt"],
        "wissensseite": "multimeter"},
    "belastung_u": {
        "titel": "Belastungsfehler Spannungsmessung", "kategorie": "Messtechnik", "unterkategorie": "Messgeräte",
        "beschreibung": "Wie stark verfälscht der Innenwiderstand des Messgeräts die Spannung?",
        "stichworte": ["Belastungsfehler", "Innenwiderstand", "Voltmeter", "hochohmig"],
        "wissensseite": "multimeter"},
    "buerde_i": {
        "titel": "Bürdenspannung Strommessung", "kategorie": "Messtechnik", "unterkategorie": "Messgeräte",
        "beschreibung": "Messfehler durch den Widerstand des Strommessers.",
        "stichworte": ["Bürdenspannung", "Amperemeter", "Strommessung", "Shunt"],
        "wissensseite": "multimeter"},
    "pt100": {
        "titel": "Pt100 / Pt1000", "kategorie": "Messtechnik", "unterkategorie": "Sensoren",
        "beschreibung": "Widerstand ↔ Temperatur nach IEC 60751, Fehler der 2-Leiter-Schaltung.",
        "stichworte": ["Pt100", "Pt1000", "Widerstandsthermometer", "RTD", "Callendar-Van Dusen", "Temperatur"],
        "wissensseite": "temperatur"},
    "ntc": {
        "titel": "NTC-Thermistor", "kategorie": "Messtechnik", "unterkategorie": "Sensoren",
        "beschreibung": "Widerstand ↔ Temperatur mit der B-Wert-Gleichung.",
        "stichworte": ["NTC", "Thermistor", "Heissleiter", "B-Wert", "Temperatur"],
        "wissensseite": "temperatur"},
    "thermoelement": {
        "titel": "Thermoelement", "kategorie": "Messtechnik", "unterkategorie": "Sensoren",
        "beschreibung": "Thermospannung ↔ Temperatur (lineare Näherung) für Typ K, J, T, N, S.",
        "stichworte": ["Thermoelement", "Typ K", "Thermospannung", "Vergleichsstelle", "Temperatur"],
        "wissensseite": "temperatur"},
    "bruecke": {
        "titel": "Wheatstone-Brücke", "kategorie": "Messtechnik", "unterkategorie": "Sensoren",
        "beschreibung": "Brückenspannung und Abgleichbedingung.",
        "stichworte": ["Brücke", "Wheatstone", "Abgleich", "Brückenspannung", "mV/V"],
        "wissensseite": "bruecke_dms"},
    "dms": {
        "titel": "Dehnungsmessstreifen (DMS)", "kategorie": "Messtechnik", "unterkategorie": "Sensoren",
        "beschreibung": "Brückenspannung bei Viertel-, Halb- und Vollbrücke.",
        "stichworte": ["DMS", "Dehnung", "k-Faktor", "Vollbrücke", "Wägezelle"],
        "wissensseite": "bruecke_dms"},
    "mid": {
        "titel": "Magnetisch-induktive Durchflussmessung", "kategorie": "Messtechnik", "unterkategorie": "Sensoren",
        "beschreibung": "Fliessgeschwindigkeit, Volumenstrom und Messspannung eines MID.",
        "stichworte": ["MID", "Durchfluss", "Volumenstrom", "Fliessgeschwindigkeit", "Induktion"],
        "wissensseite": "durchfluss"},

    # =========================================================================
    # DIGITALTECHNIK
    # =========================================================================
    "adc": {
        "titel": "AD-Wandler", "kategorie": "Digitaltechnik", "unterkategorie": "AD-Wandler",
        "beschreibung": "LSB, Quantisierungsfehler, Signal-Rausch-Abstand und digitaler Code.",
        "stichworte": ["ADC", "AD-Wandler", "LSB", "Auflösung", "Quantisierung", "Bit"],
        "wissensseite": "ad_wandler"},
    "abtastung": {
        "titel": "Abtasttheorem & Aliasing (interaktiv)", "kategorie": "Digitaltechnik", "unterkategorie": "AD-Wandler",
        "beschreibung": "Was passiert, wenn zu langsam abgetastet wird?",
        "stichworte": ["Abtasttheorem", "Nyquist", "Shannon", "Aliasing", "Abtastrate"],
        "wissensseite": "ad_wandler"},
}


# =============================================================================
# WISSENSSEITEN FINDEN (ohne Fenster - auch vom Prüfskript benutzt)
# =============================================================================
def wissensseiten_laden():
    """
    Lädt alle Wissensseiten aus WISSENS_BEREICHE.
    Rückgabe: {thema_id: {"bereich": "Bauteile", "titel": "Diode", "rechner": [ids auf dieser Seite]}}
              + Liste von Meldungen (Ladefehler, doppelte Seiten-IDs)
    """
    import os
    from programmieren.engine import lader               # -> programmieren/engine/lader.py

    projekt = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    seiten, meldungen = {}, []
    for bereich, ordner in WISSENS_BEREICHE.items():
        _, themen, ladefehler = lader.alle_laden(os.path.join(projekt, ordner))
        meldungen += [f"{ordner}: {f}" for f in ladefehler]
        for thema in themen.values():
            if thema.id in seiten:
                meldungen.append(f"Seiten-ID „{thema.id}“ gibt es in {seiten[thema.id]['bereich']} UND {bereich}")
            seiten[thema.id] = {"bereich": bereich, "titel": thema.titel,
                                "rechner": thema.daten.get("rechner", []) + thema.daten.get("grafiken", [])}
    return seiten, meldungen


def seiten_mit_rechner(seiten, rechner_id):
    """Alle Seiten-IDs, auf denen dieser Rechner vorkommt (in Ladereihenfolge)."""
    return [seite_id for seite_id, s in seiten.items() if rechner_id in s["rechner"]]
