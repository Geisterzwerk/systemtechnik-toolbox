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
    "Digitaltechnik": ("💾", "AD-Wandler und Abtastung"),
}

# Diese Bereiche enthalten Wissensseiten (Tab-Name -> Ordner mit den Seiten)
WISSENS_BEREICHE = {"Bauteile": "bauteile/inhalte", "Messtechnik": "messtechnik/inhalte",
                    "Schaltungen": "schaltungen/inhalte"}

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
    "led_vorwiderstand": {
        "titel": "LED-Vorwiderstand", "kategorie": "Schaltungen", "unterkategorie": "Vorwiderstände",
        "beschreibung": "Vorwiderstand für eine oder mehrere LEDs in Reihe, mit Normwert.",
        "stichworte": ["LED", "Vorwiderstand", "Leuchtdiode", "Uf", "If"],
        "wissensseite": "led"},
    "rc_filter": {
        "titel": "RC-Filter (Tief-/Hochpass)", "kategorie": "Schaltungen", "unterkategorie": "Filter",
        "beschreibung": "Grenzfrequenz oder fehlendes R bzw. C eines RC-Glieds.",
        "stichworte": ["Tiefpass", "Hochpass", "Grenzfrequenz", "fg", "-3 dB", "Filter"],
        "wissensseite": "kondensator"},
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
        "wissensseite": "relais"},
    "bjt_arbeitspunkt": {
        "titel": "Arbeitspunkt Emitterschaltung", "kategorie": "Schaltungen", "unterkategorie": "Verstärker",
        "beschreibung": "Basisteiler, Kollektorstrom, U_CE und Verstärkung einer Emitterschaltung.",
        "stichworte": ["Emitterschaltung", "Arbeitspunkt", "Basisteiler", "Verstärker", "Gegenkopplung"],
        "wissensseite": "bipolartransistor"},

    "gleichrichter": {
        "titel": "Gleichrichter mit Ladeelko", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Gleichspannung, Welligkeit und Sperrspannung für Einweg, Brücke und Mittelpunkt.",
        "stichworte": ["Brücke", "Einweg", "Mittelpunkt", "Elko", "Brummspannung", "Graetz"],
        "wissensseite": "diode"},
    "netzteil": {
        "titel": "Trafo + Gleichrichter + Elko", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Was kommt nach Trafo und Brückengleichrichter heraus? Ladeelko dimensionieren.",
        "stichworte": ["Netzteil", "Ladeelko", "Welligkeit", "Brücke", "Spitzenwert"],
        "wissensseite": "transformator"},
    "zdiode_stabi": {
        "titel": "Z-Dioden-Stabilisierung", "kategorie": "Schaltungen", "unterkategorie": "Netzteile",
        "beschreibung": "Vorwiderstand und Belastung der Z-Diode im ungünstigsten Fall.",
        "stichworte": ["Z-Diode", "Zener", "Stabilisierung", "Vorwiderstand", "Glättungsfaktor"],
        "wissensseite": "z_diode"},
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
