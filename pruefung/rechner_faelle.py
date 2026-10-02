# =============================================================================
# pruefung/rechner_faelle.py
# -----------------------------------------------------------------------------
# BEKANNTE BEISPIELWERTE für alle Rechner - von Hand nachgerechnet.
#
# AUFBAU EINES FALLS (Formel-Rechner):
#   ("rechner_id", {Feld: "Text wie im Fenster getippt"}, erwartet, "Rechnung von Hand")
#
#   Eingabe     genau so, wie man sie ins Feld tippt. Ohne Vorsatz gilt die
#               Einheit, die im Dropdown vorausgewählt ist (z.B. "20" im mA-Feld = 20 mA).
#               Leere Felder einfach weglassen. Auswahl-Felder: Text der Option.
#   erwartet    Liste von Textstücken, die im Ergebnis vorkommen MÜSSEN
#               oder  fehler("Teil der Meldung")  -> Rechner muss eine Meldung zeigen
#   Rechnung    wie der erwartete Wert entstanden ist (wird bei Fehlern angezeigt)
#
# FUNKTIONEN (reine Rechenfunktionen ohne Fenster):
#   ("Beschreibung", lambda: funktion(...), erwartet)
#   erwartet    Zahl (Toleranz 0.1 %), Text/Liste (exakt) oder wirft(ValueError)
#
# NEUER RECHNER?  Hier mindestens einen Normalfall und einen Fehlerfall ergänzen.
#
# WER RUFT DAS AUF?  pruefen_rechner.py (im Projektordner)
# =============================================================================

from bauteile.rechner import mosfet_mathe, normreihen, schaltvorgaenge_mathe as sv, transistor_mathe
from bauteile.rechner.basis import RechnerFehler
from bauteile.rechner.widerstand_rechner import smd_entschluesseln, wert_zu_farben
from schaltungen import netzwerk_mathe as nm


def fehler(text):
    """Erwartung: Der Rechner zeigt eine Meldung, die 'text' enthält."""
    return {"fehler": text}


def wirft(fehlerklasse):
    """Erwartung: Die Funktion bricht mit dieser Fehlerklasse ab."""
    return {"wirft": fehlerklasse}


# =============================================================================
# FORMEL-RECHNER
# =============================================================================
FAELLE = [
    # ---------------------------------------------------------------- Widerstand
    ("ohm_leistung", {"U": "12", "R": "1k"}, ["I = 12 mA", "P = 144 mW"],
     "I = 12 V / 1 kΩ = 12 mA,  P = 12 V · 12 mA = 144 mW"),
    ("ohm_leistung", {"I": "20", "R": "220"}, ["U = 4.4 V", "P = 88 mW"],
     "Strom-Feld steht auf mA: 20 mA · 220 Ω = 4.4 V,  P = (20 mA)² · 220 Ω = 88 mW"),
    ("ohm_leistung", {"I": "1A", "R": "10"}, ["U = 10 V"],
     "„1A“ im mA-Feld: getippte Einheit gilt -> 1 A · 10 Ω = 10 V (nicht 10 mV)"),
    ("ohm_leistung", {"P": "0.25", "R": "1k"}, ["I = 15.81 mA", "U = 15.81 V"],
     "I = √(P/R) = √(0.25 W / 1000 Ω) = 15.81 mA,  U = √(P·R) = 15.81 V"),
    ("ohm_leistung", {"U": "12"}, fehler("Genau ZWEI"), "nur ein Wert"),
    ("ohm_leistung", {"U": "5", "P": "0"}, fehler("Leistung P"), "R = U²/P -> Division durch 0"),
    ("ohm_leistung", {"U": "12", "R": "-1k"}, fehler("negativ"), "negativer Widerstand"),

    ("e_reihe", {"R": "4.6", "reihe": "E24 (±5 %)"}, ["4.7 kΩ  (+2.17 %)", "Kleiner: 4.3 kΩ"],
     "4.6 kΩ liegt zwischen 4.3 und 4.7 kΩ, logarithmisch näher an 4.7: (4.7 − 4.6) / 4.6 = +2.17 %"),
    ("e_reihe", {"R": "1", "reihe": "E12 (±10 %)"}, ["1 kΩ  (+0.00 %)"], "1 kΩ ist selbst ein Normwert"),
    ("e_reihe", {"R": "0"}, fehler("grösser als 0"), "0 Ω hat keinen Normwert"),

    ("reihe_parallel", {"liste": "1k 1k"}, ["Reihe:    R = 2 kΩ", "Parallel: R = 500 Ω"],
     "Reihe 1k + 1k = 2k,  parallel 1k·1k / 2k = 500 Ω"),
    ("reihe_parallel", {"liste": "1k 1k", "ziel": "400R"}, ["2 kΩ PARALLEL dazu (E24: 2 kΩ)"],
     "1 / (1/400 − 1/500) = 2000 Ω"),
    ("reihe_parallel", {"liste": "1k 0"}, fehler("grösser als 0"), "0 Ω in der Liste"),

    ("spannungsteiler", {"Ue": "12", "R1": "10", "R2": "10"},
     ["Ua = 6 V  (unbelastet)", "Querstrom = 600 µA", "P(R1) = 3.6 mW"],
     "12 V · 10k / 20k = 6 V,  I = 12 V / 20 kΩ = 0.6 mA,  P = (0.6 mA)² · 10 kΩ = 3.6 mW"),
    ("spannungsteiler", {"Ue": "12", "R2": "10", "Ua": "5"}, ["R1 = 14 kΩ", "E24-Wert 15 kΩ → Ua = 4.8 V"],
     "R1 = R2 · (Ue − Ua) / Ua = 10k · 7/5 = 14 kΩ; E24 15k -> 12 V · 10/25 = 4.8 V"),
    ("spannungsteiler", {"Ue": "12", "R1": "10", "R2": "10", "RL": "10"}, ["Ua = 4 V  (-33.3 %)", "Last zu klein"],
     "R2 || RL = 5k -> 12 V · 5/15 = 4 V statt 6 V = −33.3 %"),
    ("spannungsteiler", {"Ue": "5", "R2": "10", "Ua": "6"}, fehler("zwischen 0 und Ue"), "Ua > Ue unmöglich"),
    ("spannungsteiler", {"R1": "10", "R2": "10", "Ua": "-1"}, fehler("grösser als 0"), "negative Ausgangsspannung"),

    ("led_vorwiderstand", {"Ub": "5", "Uf": "2", "If": "10"},
     ["R = 300 Ω", "E12: 330 Ω → I = 9.091 mA, P = 27.27 mW", "E24: 300 Ω → I = 10 mA", "mind. 60 mW"],
     "R = (5 − 2) V / 10 mA = 300 Ω; E12 aufrunden 330 Ω -> 3 V / 330 Ω = 9.091 mA; P = 30 mW, ×2 = 60 mW"),
    ("led_vorwiderstand", {"Ub": "5", "Uf": "2", "If": "10", "n": "3"}, fehler("Versorgung zu klein"),
     "3 · 2 V = 6 V > 5 V"),
    ("led_vorwiderstand", {"Ub": "5", "Uf": "2", "If": "10", "n": "-1"}, fehler("ganze Zahl ab 1"), "−1 LEDs"),
    ("led_vorwiderstand", {"Ub": "5", "Uf": "2", "If": "10", "n": "1.5"}, fehler("ganze Zahl ab 1"), "1.5 LEDs"),

    ("leitung", {"l": "10", "A": "1.5", "mat": "Kupfer (κ = 56)", "I": "10", "U": "230"},
     ["R = 238.1 mΩ", "ΔU = 2.381 V", "23.81 W", "1.04 % der Nennspannung"],
     "R = 20 m / (56 · 1.5 mm²) = 0.2381 Ω; ΔU = 10 A · 0.2381 Ω; P = I² · R; 2.381 / 230 = 1.04 %"),
    ("leitung", {"l": "10", "A": "0"}, fehler("Querschnitt"), "Querschnitt 0"),

    ("temperatur", {"R": "100", "T": "70"}, ["R(70 °C) = 119.5 Ω", "+19.50 %", "ΔT = +50 K"],
     "Kupfer: 100 Ω · (1 + 0.0039 · 50 K) = 119.5 Ω  (Bezug leer = 20 °C)"),
    ("temperatur", {"R": "0", "T": "70"}, fehler("R bei Bezugstemp."), "R = 0 -> Änderung in % nicht definiert"),

    # --------------------------------------------------------------- Kondensator
    ("rc_zeit", {"R": "10", "C": "100", "p": "50"}, ["τ = R · C = 1 s", "5τ = 5 s", "t = 693.1 ms  (0.69 τ)"],
     "10 kΩ · 100 µF = 1 s;  50 %: t = τ · ln 2 = 0.693 s"),
    ("rc_zeit", {"R": "10", "C": "100", "U0": "10", "Uz": "6.32"}, ["t = 999.7 ms  (1.00 τ)"],
     "6.32 V von 10 V = 63.2 % -> t = −τ · ln(1 − 0.632) ≈ 1 τ"),
    ("rc_zeit", {"R": "10", "C": "100", "Uz": "5"}, fehler("auch U0"), "Zielspannung ohne Endspannung"),
    ("rc_zeit", {"R": "10", "C": "100", "p": "100"}, fehler("zwischen 0 und 100"), "100 % wird nie erreicht"),

    ("rc_filter", {"R": "1.6", "C": "100"}, ["fg = 994.7 Hz", "τ = 160 µs"],
     "fg = 1 / (2π · 1.6 kΩ · 100 nF) = 994.7 Hz"),
    ("rc_filter", {"R": "10", "fg": "1k"}, ["C = 15.92 nF  (E12: 15 nF)"], "C = 1 / (2π · 10 kΩ · 1 kHz)"),
    ("rc_filter", {"C": "10p", "fg": "1M"}, ["R = 15.92 kΩ  (E24: 16 kΩ)"], "R = 1 / (2π · 10 pF · 1 MHz)"),
    ("rc_filter", {"R": "1", "fg": "1G"}, ["C = 0.1592 pF  (E12: 0.15 pF)"],
     "Sehr kleine Werte: Normwert muss trotzdem stimmen (früher Rundungsfehler)"),
    ("rc_filter", {"R": "1", "C": "1", "fg": "1"}, fehler("Genau ZWEI"), "alle drei gegeben"),

    ("blindwiderstand_c", {"C": "10", "f": "50", "U": "230"}, ["Xc = 318.3 Ω", "I = 722.6 mA", "Q = 166.2 var"],
     "Xc = 1 / (2π · 50 Hz · 10 µF) = 318.3 Ω;  I = 230 V / 318.3 Ω;  Q = U · I"),
    ("blindwiderstand_c", {"C": "10", "f": "0"}, fehler("Frequenz f"), "Gleichspannung: Xc unendlich"),

    ("energie_c", {"C": "1000", "U": "400", "t": "10"}, ["Q = C · U = 400 mC", "W = ½ · C · U² = 80 J", "8 kW", "Funken"],
     "Q = 1 mF · 400 V;  W = ½ · 1 mF · (400 V)² = 80 J;  80 J / 10 ms = 8 kW"),

    ("reihe_parallel_c", {"liste": "100 100"}, ["Parallel: C = 200 nF", "Reihe:    C = 50 nF"],
     "Feld steht auf nF; parallel addieren, Reihe wie Widerstände parallel"),

    ("kondensator_code", {"code": "104K"}, ["C = 100 nF", "Toleranz K = ±10 %"], "10 · 10⁴ pF = 100 nF"),
    ("kondensator_code", {"code": "4n7"}, ["C = 4.7 nF"], "n als Komma"),
    ("kondensator_code", {"code": "p47"}, ["C = 0.47 pF"], "p als Komma, vorne"),
    ("kondensator_code", {"code": "47"}, ["C = 47 pF"], "zwei Ziffern = pF"),
    ("kondensator_code", {"code": "abc"}, fehler("kein bekanntes Format"), "Unsinn"),

    # --------------------------------------------------------------------- Spule
    ("blindwiderstand_l", {"L": "100", "f": "50", "R": "10", "U": "230"},
     ["XL = 31.42 Ω", "Z = 32.97 Ω, φ = 72.3°", "I = 6.976 A"],
     "XL = 2π · 50 Hz · 100 mH;  Z = √(10² + 31.42²);  φ = arctan(31.42/10);  I = 230 V / Z"),
    ("rl_zeit", {"L": "100", "R": "10", "U": "12", "t": "10"}, ["τ = L / R = 10 ms", "I = U / R = 1.2 A", "758.5 mA  (63.2 %)"],
     "τ = 100 mH / 10 Ω = 10 ms;  nach 1 τ: 1.2 A · (1 − e⁻¹)"),
    ("rl_zeit", {"L": "100", "R": "10", "t": "-1"}, fehler("negativ"), "negative Zeit"),
    ("abschaltspitze", {"L": "100", "I": "100", "dt": "1"}, ["= 10 kV", "= 500 µJ", "Freilaufdiode"],
     "u = 100 mH · 100 mA / 1 µs = 10 kV;  W = ½ · 0.1 H · (0.1 A)²"),
    ("abschaltspitze", {"L": "100", "I": "100", "dt": "0"}, fehler("Abschaltzeit"), "Δt = 0"),
    ("energie_l", {"L": "1000", "I": "2"}, ["W = ½ · L · I² = 2 J"], "½ · 1 H · (2 A)²"),
    ("lc_resonanz", {"L": "100", "C": "100"}, ["f0 = 50.33 kHz", "Z0 = √(L/C) = 31.62 Ω"],
     "f0 = 1 / (2π · √(100 µH · 100 nF));  Z0 = √(100 µH / 100 nF)"),
    ("lc_resonanz", {"L": "100", "f": "10"}, ["C = 2.533 µF"], "C = 1 / ((2π · 10 kHz)² · 100 µH)"),
    ("lc_resonanz", {"L": "-100", "C": "100"}, fehler("negativ"), "negative Induktivität"),
    ("reihe_parallel_l", {"liste": "10 10"}, ["Reihe:    L = 20 mH", "Parallel: L = 5 mH"], "wie Widerstände"),

    # ------------------------------------------------------------- Transformator
    ("uebersetzung", {"U1": "230", "U2": "12", "N1": "1000", "I2": "1"},
     ["N2 = 52 Windungen", "= 19.17  (Abwärts-Trafo)", "I1 = I2 / ü = 52.17 mA", "367.4"],
     "N2 = 1000 · 12/230 = 52.2;  ü = 230/12 = 19.17;  I1 = 1 A / 19.17;  ü² = 367.4"),
    ("uebersetzung", {"U1": "230", "U2": "23", "N2": "100"}, ["N1 = 1000 Windungen"], "N1 = 100 · 230/23"),
    ("leistung_trafo", {"U1": "230", "U2": "12", "I2": "2"}, ["S2 = U2 · I2 = 24 VA", "28.24 VA", "4.235 W", "I1 = 122.8 mA"],
     "S2 = 24 VA;  η leer = 85 % -> S1 = 28.24 VA;  I1 = 28.24 VA / 230 V"),
    ("leistung_trafo", {"U1": "230", "U2": "12", "I2": "2", "eta": "150"}, fehler("zwischen 1 und 100"), "η > 100 %"),
    ("windungen", {"A": "10", "B": "1.2", "U1": "230", "U2": "12"},
     ["3.75 Windungen pro Volt", "N1 = 863 Windungen", "N2 = 47 Windungen"],
     "1 / (4.44 · 50 Hz · 1.2 T · 10 cm²) = 3.754 Wdg/V;  230 V · 3.754;  12 V · 3.754 · 1.05"),
    ("netzteil", {"U2": "12", "I": "1A", "C": "4700"},
     ["Û = U2 · √2 = 16.97 V", "≈ 15.57 V", "ΔU ≈ I / (2·f·C) = 2.128 V", "Minimum ≈ 13.44 V", "22.4 V"],
     "Û = 16.97 V; − 2 · 0.7 V = 15.57 V; ΔU = 1 A / (2 · 50 Hz · 4.7 mF); Elko: Û · 1.1 · 1.2"),
    ("netzteil", {"U2": "12", "I": "1A"}, ["C ≥ 6.422 mF", "(E6: 6.8 mF)"], "C = 1 A / (2 · 50 Hz · 0.1 · 15.57 V)"),
    ("netzteil", {"U2": "0.9", "I": "100"}, fehler("U2 zu klein"), "Û = 1.27 V < 2 · 0.7 V"),

    # --------------------------------------------------------------- Halbleiter
    ("diode_temperatur", {"Uf": "0.7", "T": "85"}, ["Uf(85 °C) = 580 mV", "Änderung: -120 mV", "TK = -2 mV/K"],
     "0.7 V − 2 mV/K · 60 K = 0.58 V"),
    ("diode_temperatur", {"Uf": "0.7", "T": "125", "tk": "-2.2"}, ["Uf(125 °C) = 480 mV"], "0.7 V − 2.2 mV/K · 100 K"),
    ("diode_verlust", {"Uf": "0.9", "I": "2", "rth": "60"}, ["P ≈ Uf · I = 1.8 W", "Tj = Ta + P · Rth = 133 °C", "125 °C"],
     "P = 0.9 V · 2 A;  Tj = 25 °C + 1.8 W · 60 K/W = 133 °C"),
    ("gleichrichter", {"art": "Brücke (4 Dioden)", "U2": "12", "I": "500", "C": "2200"},
     ["≈ 15.57 V", "Brummfrequenz: 100 Hz", "mind. 16.97 V", "250 mA", "= 2.273 V", "Minimum ≈ 13.3 V"],
     "Brücke: 2 Dioden leiten, 100 Hz, Sperrspannung Û;  ΔU = 0.5 A / (100 Hz · 2.2 mF)"),
    ("gleichrichter", {"art": "Einweg (1 Diode)", "U2": "12"}, ["≈ 16.27 V", "Brummfrequenz: 50 Hz", "mind. 33.94 V"],
     "Einweg: 1 Diode, 50 Hz, Sperrspannung 2 · Û (Elko hält Û, Trafo liefert −Û)"),
    ("gleichrichter", {"art": "Mittelpunkt (2 Dioden, Trafo mit Mittelanzapfung)", "U2": "12"},
     ["≈ 16.27 V", "Brummfrequenz: 100 Hz", "mind. 33.94 V"], "Mittelpunkt: 1 Diode im Pfad, 100 Hz, 2 · Û"),
    ("gleichrichter", {"U2": "0.5"}, fehler("U2 zu klein"), "Û = 0.71 V < 2 · 0.7 V"),
    ("zdiode_stabi", {"Ue_min": "11", "Ue_max": "14", "Uz": "5.1", "IL_max": "20", "Pz_max": "500", "rz": "10"},
     ["Rv ≤ 236 Ω   →  E24: 220 Ω", "Iz = 40.45 mA", "Pz = 206.3 mW", "Verlustleistung Rv: 360 mW", "≈ 23"],
     "Rv = (11 − 5.1) V / (5 + 20) mA = 236 Ω -> 220 Ω;  Iz = (14 − 5.1) V / 220 Ω;  G = (220 + 10) / 10"),
    ("zdiode_stabi", {"Ue_min": "5", "Uz": "5.1", "IL_max": "20"}, fehler("grösser als Uz"), "Ue < Uz"),
    ("bjt_schalter", {"Ub": "12", "RL": "120", "Ue": "5", "beta": "100"},
     ["Ic = 98.33 mA", "Ib = 2.95 mA", "Rb = (Ue − Ube) / Ib = 1.458 kΩ  →  E24: 1.3 kΩ", "Ib = 3.308 mA", "19.67 mW"],
     "Ic = (12 − 0.2) V / 120 Ω;  Ib = 3 · Ic / 100;  Rb = 4.3 V / 2.95 mA;  E24 abrunden"),
    ("bjt_schalter", {"Ub": "12", "RL": "120", "Ue": "0.5", "beta": "100"}, fehler("grösser als Ube"), "Ue < 0.7 V"),
    ("bjt_arbeitspunkt", {"Ub": "12", "R1": "47", "R2": "10", "Rc": "2.2", "Re": "1k", "beta": "200"},
     ["U_Basis (Thevenin) = 2.105 V", "R_th = 8.246 kΩ", "Ib = 6.716 µA", "Ic = 1.343 mA", "= 7.695 V", "−Rc/Re = -2.2"],
     "U_th = 12 · 10/57;  R_th = 47k || 10k;  Ib = 1.405 V / (8.246k + 201 · 1k);  Uce = 12 − Ic·Rc − Ie·Re"),
    ("bjt_arbeitspunkt", {"Ub": "12", "R1": "100", "R2": "1", "Rc": "1", "beta": "100"}, ["SPERRT"],
     "U_th = 12 V · 1/101 = 0.12 V < 0.7 V"),
    ("bjt_arbeitspunkt", {"Ub": "12", "R1": "10", "R2": "10", "Rc": "10", "beta": "100"}, ["GESÄTTIGT", "1.18 mA"],
     "Ic wäre 106 mA, aber Rc lässt nur (12 − 0.2) V / 10 kΩ = 1.18 mA zu"),
    ("mosfet_verlust", {"I": "10", "Rds": "10", "U": "24", "f": "20", "t": "100"},
     ["= 1.5 W", "Rds heiss ≈ 15 mΩ", "= 240 mW", "Total ≈ 1.74 W"],
     "P = (10 A)² · 10 mΩ · 1.5;  P_sw = ½ · 24 V · 10 A · 100 ns · 20 kHz = 0.24 W"),
    ("mosfet_gate", {"Qg": "30", "Ugs": "10", "t": "100", "f": "20"},
     ["Ig = Qg / t = 300 mA", "Rg ≈ Ugs / Ig = 33.33 Ω", "P = Qg · Ugs · f = 6 mW", "= 600 µA"],
     "30 nC / 100 ns = 0.3 A;  10 V / 0.3 A;  30 nC · 10 V · 20 kHz"),
    ("mosfet_gate", {"Qg": "30", "Ugs": "10"}, fehler("Schaltzeit"), "nichts zum Rechnen"),
    ("kuehlkoerper", {"P": "10", "Rjc": "1.5", "Rja": "62"},
     ["Rth = (Tj − Ta) / P = 8.50 K/W", "Rth,SA ≤ 6.50 K/W", "Tj = 660 °C", "zu heiss"],
     "(125 − 40) °C / 10 W = 8.5 K/W;  − 1.5 − 0.5 = 6.5 K/W;  ohne KK: 40 + 10 · 62"),
    ("kuehlkoerper", {"P": "0", "Rjc": "1.5"}, fehler("Verlustleistung P"), "P = 0"),

    # --------------------------------------------------------- Transistor-Extra
    ("basiswiderstand", {"typ": "NPN (Low-Side)", "Ub": "12", "Rl": "120", "Us": "5", "B": "100"},
     ["I_C = 98.33 mA", "I_B = ü · I_C / B = 2.95 mA", "1.458 kΩ", "E12 (abgerundet): 1.2 kΩ", "I_B = 3.583 mA, ü = 3.6"],
     "R_B = 4.3 V / 2.95 mA = 1.458 kΩ -> E12 abrunden 1.2 kΩ -> 4.3 V / 1.2 kΩ = 3.583 mA"),
    ("basiswiderstand", {"typ": "PNP (High-Side)", "Ub": "12", "Rl": "120", "B": "100"},
     ["3.831 kΩ", "E12 (abgerundet): 3.3 kΩ", "Pegelwandler"],
     "PNP: U_RB = 12 − 0.7 − 0 V = 11.3 V;  11.3 V / 2.95 mA = 3.831 kΩ"),
    ("basiswiderstand", {"typ": "NPN (Low-Side)", "Ub": "12", "Rl": "120", "Us": "0.5", "B": "100"},
     fehler("grösser als U_BE"), "0.5 V < 0.7 V"),
    ("arbeitspunkt", {"Ub": "12", "Rl": "120", "Us": "5", "Rb": "4.7", "B": "100"},
     ["AKTIV", "I_B = 914.9 µA", "U_CE = 1.021 V", "nur 93 %"],
     "I_B = 4.3 V / 4.7 kΩ;  B · I_B = 91.5 mA < 98.3 mA -> aktiv;  U_CE = 12 − 91.5 mA · 120 Ω"),
    ("arbeitspunkt", {"Ub": "12", "Rl": "120", "Us": "5", "Rb": "1", "B": "100"}, ["GESÄTTIGT", "ü = B · I_B / I_C = 4.4"],
     "I_B = 4.3 mA -> 430 mA möglich, Last erlaubt 98.3 mA -> ü = 4.37"),
    ("arbeitspunkt", {"Ub": "12", "Rl": "120", "Us": "0", "Rb": "1", "B": "100"}, ["GESPERRT"], "U_St < 0.7 V"),
    ("arbeitspunkt", {"Ub": "0.1", "Rl": "120", "Us": "5", "Rb": "1", "B": "100"}, fehler("U_CE,sat"),
     "U_B unter U_CE,sat: kein Laststrom möglich (früher: „inf“)"),
    ("verlustleistung", {"Uce": "0.2", "Ic": "100", "Ib": "3", "D": "50", "f": "10", "t": "200", "Ub": "12"},
     ["P_D = 11.05 mW", "(Tastgrad 50 %)", "P_S ≈ 1.2 mW", "P_V = 12.25 mW"],
     "(0.2 V · 100 mA + 0.7 V · 3 mA) · 0.5;  ½ · 12 V · 100 mA · 200 ns · 10 kHz"),
    ("verlustleistung", {"Uce": "0.2", "Ic": "100", "f": "10"}, ["f UND Schaltzeit"], "nur f gegeben"),

    # ------------------------------------------------------------------ Relais
    ("relais_ansteuerung", {"Ub": "12", "Rsp": "400", "Us": "3.3", "B": "100"},
     ["Spulenstrom I = 29.5 mA", "11.8 V", "P = 348.1 mW", "I_B = ü · I / B = 885 µA", "2.938 kΩ", "E12: 2.7 kΩ", "963 µA", "1N4148"],
     "I = 11.8 V / 400 Ω;  I_B = 3 · 29.5 mA / 100;  R_B = 2.6 V / 0.885 mA -> 2.7 kΩ"),
    ("relais_temperatur", {"Un": "24", "R20": "1k", "T": "85"},
     ["1.255 kΩ", "24 mA kalt → 19.12 mA warm", "18 V bei 20 °C → 22.6 V", "Reserve 6 %"],
     "Faktor 1 + 0.00393 · 65 K = 1.2554;  U_an = 75 % · 24 V = 18 V -> 22.6 V"),
    ("relais_temperatur", {"Un": "24", "R20": "1k", "T": "85", "U": "21.6"}, ["zieht warm nicht mehr sicher an"],
     "21.6 V < 22.6 V"),
    ("freilauf", {"Ub": "24", "Rsp": "1k", "L": "2", "Uz": "24", "Uce0": "45"},
     ["24 mA", "= 576 µJ", "τ = L / R = 2 ms", "U_CE,max ≈ 24.7 V, Strom = 0 nach ≈ 7.127 ms",
      "U_CE,max ≈ 48.7 V, Strom = 0 nach ≈ 1.358 ms", "5.2× schneller", "schlägt durch"],
     "τ = 2 H / 1 kΩ;  t = τ · ln(1 + 24/0.7);  mit Z: τ · ln(1 + 24/24.7);  48.7 V > 45 V"),
    ("kontakt_last", {"art": "Glühlampe / Halogen", "U": "230", "I": "0.5", "Irel": "10"},
     ["12 × 500 mA = 6 A", "115 W", "Reserve 20.0×"], "Glühlampe ≈ 12 × I_Nenn;  230 V · 0.5 A"),
    ("kontakt_last", {"art": "LED-Treiber / Netzteil", "U": "230", "I": "1", "Irel": "5"}, ["inrush"],
     "30 × 1 A = 30 A > 4 × 5 A"),
    ("kontakt_last", {"art": "Ohmsch (Heizung)", "netz": "DC", "U": "48", "I": "1"}, ["DC über 30 V"], "DC-Lichtbogen"),

    # ------------------------------------------------------------ Messtechnik
    ("statistik", {"liste": "4.98 5.02 5.01 4.99 5.00"},
     ["Mittelwert x̄ = 5", "s = 0.01581", "s/√n = 0.007071", "x = 5 ± 0.0197", "(t = 2.78)", "± 0.393 %"],
     "s = √(0.001 / 4);  s/√5;  t(95 %, f = 4) = 2.78"),
    ("statistik", {"liste": "5"}, fehler("Mindestens zwei"), "ein Wert hat keine Streuung"),
    ("dmm_genauigkeit", {"x": "5", "p": "0.5", "d": "3", "res": "0.001", "bereich": "60"},
     ["= ± 0.028", "zwischen 4.972 und 5.028", "± 0.56 %", "< 10 %"],
     "5 · 0.5 % + 3 · 0.001 = 0.028;  5 < 10 % von 60"),
    ("fehlerfortpflanzung", {"art": "Produkt / Quotient (P = U·I, R = U/I)", "x": "12", "dx": "0.1", "y": "2", "dy": "0.05"},
     ["0.833 % und 2.5 %", "± 3.33 %", "± 2.64 %", "x · y = 24 ± 0.632"],
     "relativ 0.1/12 und 0.05/2;  worst: Summe;  statistisch: √(0.833² + 2.5²)"),
    ("fehlerfortpflanzung", {"art": "Summe / Differenz (U1 ± U2)", "x": "10", "dx": "0.1", "y": "9.9", "dy": "0.1"},
     ["x − y = 0.1 ± 0.141", "explodiert"], "√(0.1² + 0.1²) = 0.141 bei nur 0.1 Differenz"),
    ("signalform", {"art": "Sinus", "u": "325"}, ["U_eff = 229.8 V", "|Ū| = 206.9 V", "Crestfaktor Û/U_eff = 1.414", "stimmt hier"],
     "325 V / √2;  2 · 325 V / π"),
    ("signalform", {"art": "Rechteck symmetrisch (±Û)", "u": "10"}, ["U_eff = 10 V", "Fehler +11.1 %", "True RMS nötig"],
     "Rechteck: U_eff = |Ū| = Û -> Mittelwert-Messgerät zeigt 1.111 · 10 V"),
    ("signalform", {"art": "Dreieck symmetrisch (±Û)", "u": "10"}, ["U_eff = 5.774 V", "Fehler -3.8 %"],
     "Û / √3 = 5.774 V;  1.111 · 5 V = 5.554 V"),
    ("signalform", {"art": "PWM / Rechteck 0 … Û", "u": "5", "d": "25"}, ["U_eff = 2.5 V", "Ū = 1.25 V", "Fehler -44.5 %"],
     "Û · √D = 5 V · 0.5;  Û · D"),
    ("signalform", {"art": "Sinus", "u": "325", "d": "0"}, fehler("Tastgrad"), "0 %"),
    ("messbereich", {"Ri": "1k", "Iv": "100", "U": "10", "I": "1000m"},
     ["U = Ri · Iv = 100 mV", "10'000 Ω/V", "Rv = U/Iv − Ri = 99 kΩ", "Rs = Ri · Iv / (I − Iv) = 100 mΩ"],
     "1 kΩ · 100 µA;  10 V / 100 µA − 1 kΩ;  1 kΩ · 100 µA / (1 A − 100 µA)"),
    ("belastung_u", {"Uq": "10", "Rq": "1M"}, ["Anzeige = Uq · Ri / (Rq + Ri) = 9.091 V", "-9.09 %", "zu hochohmig"],
     "Ri leer = 10 MΩ:  10 V · 10M / 11M"),
    ("buerde_i", {"U": "3.3", "R": "100", "Rm": "1"}, ["ohne Messgerät: 33 mA", "32.67 mA", "-0.99 %"],
     "3.3 V / 100 Ω;  3.3 V / 101 Ω"),
    ("buerde_i", {"U": "3.3", "R": "100", "Ub": "200", "Iv": "200"}, ["Messgerät (1 Ω)"],
     "Bürde 200 mV bei 200 mA -> 1 Ω"),
    ("oszi", {"B": "100", "f": "33M", "tr": "10"}, ["tr ≈ 0.35 / B = 3.5 ns", "≈ 5.0 % zu klein", "≈ 10.59 ns"],
     "0.35 / 100 MHz;  1 − 1/√(1 + 0.33²);  √(10² + 3.5²) ns"),
    ("pt100", {"typ": "Pt100 (100 Ω bei 0 °C)", "T": "100"}, ["R(100 °C) = 138.51 Ω"], "IEC 60751 Tabelle: 138.51 Ω"),
    ("pt100", {"typ": "Pt100 (100 Ω bei 0 °C)", "T": "-50"}, ["R(-50 °C) = 80.306 Ω"], "IEC 60751 Tabelle: 80.31 Ω"),
    ("pt100", {"typ": "Pt100 (100 Ω bei 0 °C)", "R": "138.5055", "Rl": "0.5"}, ["T = 100.00 °C", "+2.60 K"],
     "Rückrechnung;  2 · 0.5 Ω / 0.385 Ω/K"),
    ("pt100", {"typ": "Pt100 (100 Ω bei 0 °C)", "R": "80.306"}, ["T = -50.00 °C"], "Rückrechnung unter 0 °C (Newton)"),
    ("pt100", {"typ": "Pt1000 (1000 Ω bei 0 °C)", "T": "0"}, ["R(0 °C) = 1 kΩ"], "Pt1000"),
    ("pt100", {"typ": "Pt100 (100 Ω bei 0 °C)", "T": "1000"}, fehler("IEC 60751"), "über 850 °C"),
    ("pt100", {"typ": "Pt100 (100 Ω bei 0 °C)", "R": "1M"}, fehler("ausserhalb"), "früher: Python-Fehler (Wurzel negativ)"),
    ("ntc", {"R25": "10k", "B": "3950", "T": "50"}, ["R(50 °C) = 3.588 kΩ", "-3.78 %/K"],
     "10 kΩ · e^(3950 · (1/323.15 − 1/298.15));  −B / T²"),
    ("ntc", {"R25": "10k", "B": "3950", "R": "10"}, ["T = 25.00 °C"], "R = R25 -> 25 °C"),
    ("ntc", {"R25": "10k", "B": "3950", "R": "0"}, fehler("grösser als 0"), "früher: Python-Fehler (log 0)"),
    ("ntc", {"R25": "10k", "B": "3950", "T": "-300"}, fehler("Nullpunkt"), "unter 0 K"),
    ("thermoelement", {"typ": "Typ K (NiCr-Ni)", "U": "4.1"}, ["Messstelle ≈ 125.0 °C"], "25 °C + 4.1 mV / 41 µV/K"),
    ("thermoelement", {"typ": "Typ K (NiCr-Ni)", "T": "525"}, ["Thermospannung ≈ 20.5 mV"], "500 K · 41 µV/K"),
    ("bruecke", {"Ue": "5", "R1": "1k", "R2": "1k", "R3": "1k", "R4": "1010"}, ["= -12.44 mV", "-2.488 mV/V"],
     "5 V · (0.5 − 1010/2010)"),
    ("bruecke", {"R1": "1k", "R2": "2k", "R3": "1k"}, ["R4 = R3 · R2 / R1 = 2 kΩ"], "Abgleich"),
    ("dms", {"art": "Viertelbrücke (1 aktiver DMS)", "Ue": "10", "eps": "1000", "R": "120"},
     ["= 5 mV   (0.5 mV/V)", "ΔR = R · k · ε = 240 mΩ"], "10 V · 2 · 1000 µm/m / 4;  120 Ω · 2 · 0.001"),
    ("dms", {"art": "Vollbrücke (4 aktive DMS)", "Ue": "10", "eps": "1000"}, ["= 20 mV"], "4 × Viertelbrücke"),
    ("adc", {"n": "10", "Uref": "5", "Uin": "2.5", "fmax": "1k"},
     ["1'024 Stufen", "4.883 mV", "± 2.441 mV", "62.0 dB", "Code 512  (0x200, binär 1000000000)", "fs > 2 · fmax = 2 kHz"],
     "5 V / 1024;  6.02 · 10 + 1.76;  2.5 V / 4.883 mV = 512"),
    ("adc", {"n": "10.5", "Uref": "5"}, fehler("ganze Zahl"), "halbe Bits gibt es nicht"),
    # ------------------------------------------------------------ Schaltungen
    ("stromteiler", {"I": "100", "liste": "100 300"},
     ["R_ges = 75 Ω", "U = I · R_ges = 7.5 V", "= 75 mA  (75.0 %),  P = 562.5 mW", "= 25 mA  (25.0 %),  P = 187.5 mW"],
     "100 Ω || 300 Ω = 75 Ω;  U = 100 mA · 75 Ω;  I1 = 7.5 V / 100 Ω;  P = U² / R"),
    ("stromteiler", {"I": "100", "liste": "100"}, fehler("mindestens zwei"), "ein Widerstand ist kein Teiler"),
    ("pull_widerstand", {"Ub": "3.3", "Imax": "1", "Ileck": "1", "C": "100", "tr": "1"},
     ["R_min = U_B / I_max = 3.3 kΩ", "= 990 kΩ", "= 4.551 kΩ", "Vorschlag (E12): 3.9 kΩ", "846.2 µA", "2.792 mW"],
     "3.3 V / 1 mA;  0.3 · 3.3 V / 1 µA;  1 µs / (2.2 · 100 pF);  Mitte √(3.3k · 4.55k) = 3.88 kΩ -> 3.9 kΩ"),
    ("pull_widerstand", {"Ub": "5", "Imax": "10", "C": "1000", "tr": "0.1"}, fehler("Kein Widerstand passt"),
     "R_min = 500 Ω > R_max = 0.1 µs / (2.2 · 1 nF) = 45 Ω"),
    ("poti_last", {"Ue": "10", "Rp": "10", "RL": "100", "a": "50"},
     ["Ua = 4.878 V", "ohne Last 5 V", "Fehler -122 mV", "ca. 67 %", "R_L / R_P = 10"],
     "R_u = 5k || 100k = 4.762 kΩ;  Ua = 10 V · 4.762 / (5 + 4.762);  grösster Fehler bei ≈ 2/3"),
    ("poti_last", {"Ue": "10", "Rp": "10", "RL": "10"}, ["R_L < 10 · R_P"], "Last so gross wie das Poti"),
    ("mid", {"D": "100", "v": "1", "B": "10"}, ["A = π·D²/4 = 78.54 cm²", "Q = 28.27 m³/h = 471.2 l/min", "U = B · D · v ≈ 1 mV"],
     "π · (0.1 m)² / 4;  1 m/s · A;  10 mT · 0.1 m · 1 m/s"),
]


# =============================================================================
# REINE FUNKTIONEN
# =============================================================================
FUNKTIONEN = [
    # ---- Farbcode / SMD (Widerstand) ----
    ("Farbcode 4.7 kΩ, 4 Ringe", lambda: wert_zu_farben(4700, 4, "Gold")[0], ["Gelb", "Violett", "Rot", "Gold"]),
    ("Farbcode 4.65 kΩ rundet kaufmännisch auf 4.7 kΩ", lambda: wert_zu_farben(4650, 4, "Gold")[1], 4700),
    ("Farbcode 999.6 Ω -> 1 kΩ (Stellenwechsel)", lambda: wert_zu_farben(999.6, 4, "Gold")[0], ["Braun", "Schwarz", "Rot", "Gold"]),
    ("Farbcode 0.47 Ω -> Silber als Multiplikator", lambda: wert_zu_farben(0.47, 4, "Gold")[0], ["Gelb", "Violett", "Silber", "Gold"]),
    ("Farbcode 10 kΩ, 5 Ringe", lambda: wert_zu_farben(10e3, 5, "Braun")[0], ["Braun", "Schwarz", "Schwarz", "Rot", "Braun"]),
    ("Farbcode 0 Ω", lambda: wert_zu_farben(0, 4, "Gold"), wirft(RechnerFehler)),
    ("SMD 103 = 10 kΩ", lambda: smd_entschluesseln("103")[0], 10e3),
    ("SMD 4R7 = 4.7 Ω", lambda: smd_entschluesseln("4R7")[0], 4.7),
    ("SMD R47 = 0.47 Ω", lambda: smd_entschluesseln("R47")[0], 0.47),
    ("SMD 4701 = 4.7 kΩ", lambda: smd_entschluesseln("4701")[0], 4700),
    ("SMD EIA-96 01C = 10 kΩ", lambda: smd_entschluesseln("01C")[0], 10e3),
    ("SMD 000 = Drahtbrücke", lambda: smd_entschluesseln("000")[0], 0.0),
    ("SMD EIA-96 Code 97 gibt es nicht", lambda: smd_entschluesseln("97C"), wirft(RechnerFehler)),

    # ---- Normreihen ----
    ("E24 um 4.6 kΩ", lambda: normreihen.naechste_werte(4600, "E24"), [4300, 4700, 4700]),
    ("E12 bei 0.15 pF (früher Rundungsfehler)", lambda: normreihen.naechste_werte(0.15e-12, "E12")[2], 0.15e-12),
    ("4.7 pF ist E12-Normwert (früher: 5 pF)", lambda: normreihen.ist_normwert(4.7e-12, "E12"), True),
    ("E96 bei 10.05 kΩ", lambda: normreihen.naechste_werte(10050, "E96")[2], 10e3),
    ("Normwert bei sehr grossem Wert", lambda: normreihen.naechste_werte(9.5e15, "E6")[1], 1e16),

    # ---- Transistor ----
    ("NPN gesättigt", lambda: transistor_mathe.schalter("NPN", 12, 120, 5, 1000, 100)["zustand"], "gesättigt"),
    ("NPN aktiv: U_CE", lambda: transistor_mathe.schalter("NPN", 12, 120, 5, 4700, 100)["u_ce"], 1.02128),
    ("PNP: Steuerung auf U_B = aus", lambda: transistor_mathe.schalter("PNP", 12, 120, 12, 1000, 100)["zustand"], "gesperrt"),
    ("PNP: Steuerung auf 0 V = an", lambda: transistor_mathe.schalter("PNP", 12, 120, 0, 1000, 100)["zustand"], "gesättigt"),
    ("Transistor: R_Last 0", lambda: transistor_mathe.schalter("NPN", 12, 0, 5, 1000, 100), wirft(ValueError)),

    # ---- MOSFET ----
    ("R_DS(on) bei 5 V statt 10 V", lambda: mosfet_mathe.rds_on(5, 2, 0.05, 10), 0.05 * 8 / 3),
    ("MOSFET voll an: Strom", lambda: mosfet_mathe.schalter("N", 12, 24, 10, 2, 0.05, 10)["i"], 12 / 24.05),
    ("MOSFET knapp über U_th: linear", lambda: mosfet_mathe.schalter("N", 12, 24, 2.5, 2, 0.05, 10)["zustand"], "linear"),
    ("MOSFET linear: Verlust", lambda: mosfet_mathe.schalter("N", 12, 24, 2.5, 2, 0.05, 10)["p_t"], 1.5),
    ("MOSFET P-Kanal: Gate auf U_B = aus", lambda: mosfet_mathe.schalter("P", 12, 24, 12, 2, 0.05, 10)["zustand"], "sperrt"),
    ("MOSFET: U_GS über 20 V erkannt", lambda: mosfet_mathe.schalter("N", 12, 24, 25, 2, 0.05, 10)["zu_hoch"], True),
    ("Gate umladen: Strom", lambda: mosfet_mathe.gate_umladen(30e-9, 10, 10)["i_g"], 1.0),
    ("Gate umladen: Zeit", lambda: mosfet_mathe.gate_umladen(30e-9, 10, 10)["t_schalt"], 30e-9),

    # ---- Widerstandsnetzwerke (Schaltungen) ----
    ("Spannungsteiler belastet: Ua", lambda: nm.spannungsteiler(12, 10e3, 10e3, 10e3)["ua"], 4.0),
    ("Spannungsteiler belastet: q = I2 / I_L", lambda: nm.spannungsteiler(12, 10e3, 10e3, 10e3)["q"], 1.0),
    ("Spannungsteiler unbelastet: kein q", lambda: nm.spannungsteiler(12, 10e3, 10e3)["q"], None),
    ("Spannungsteiler R2 = 0", lambda: nm.spannungsteiler(12, 10e3, 0), wirft(ValueError)),
    ("Stromteiler 100 Ω / 300 Ω", lambda: nm.stromteiler(0.1, 100, 300)["stroeme"], [0.075, 0.025]),
    ("Pull-up gedrückt: Strom U_B / R", lambda: nm.pull_widerstand("pullup", 5, 10e3, True)["i_r"], 5e-4),
    ("Pull-up offen mit 1 µA Leckstrom", lambda: nm.pull_widerstand("pullup", 5, 10e3, False, 1e-6)["u_pin"], 4.99),
    ("Pull-down 10 kΩ, 100 µA Leck: noch LOW", lambda: nm.pull_widerstand("pulldown", 5, 10e3, False, 100e-6)["pegel"], "LOW"),
    ("Pull-down 20 kΩ, 100 µA Leck: unsicher", lambda: nm.pull_widerstand("pulldown", 5, 20e3, False, 100e-6)["pegel"], "unsicher"),
    ("Pull-Flanke 10 kΩ · 100 pF · ln 9", lambda: nm.pull_widerstand("pullup", 5, 10e3, False, 0, 100e-12)["t_flanke"], 2.1972e-6),
    ("Poti Mitte mit R_L = R_P", lambda: nm.poti_teiler(10, 10e3, 0.5, 10e3)["ua"], 4.0),
    ("Poti Anschlag oben: Last egal", lambda: nm.poti_teiler(10, 10e3, 1.0, 100.0)["ua"], 10.0),
    ("Poti Stellung 120 %", lambda: nm.poti_teiler(10, 10e3, 1.2), wirft(ValueError)),
    ("Brücke: U_d", lambda: nm.bruecke(10, 1e3, 1e3, 1e3, 1.01e3)["u_d"], -0.0248756),
    ("Brücke: Abgleichwert R4", lambda: nm.bruecke(10, 1e3, 2e3, 3e3, 1e3)["r4_abgleich"], 6e3),

    # ---- Schaltvorgänge RC / RL (Lernansicht) ----
    ("RC laden nach 1 τ: Spannung", lambda: sv.rc(1e-3, 1e3, 1e-6, 0, 5)[0], 5 * (1 - 0.36787944)),
    ("RC laden nach 1 τ: Strom", lambda: sv.rc(1e-3, 1e3, 1e-6, 0, 5)[1], 5e-3 * 0.36787944),
    ("RC entladen: Strom negativ", lambda: sv.rc(0, 1e3, 1e-6, 5, 0)[1], -5e-3),
    ("RL ein nach 1 τ", lambda: sv.rl_ein(1e-3, 100, 0.1, 10)[0], 0.1 * (1 - 0.36787944)),
    ("RL aus ohne Diode: Spannung am Schalter",
     lambda: sv.rl_aus_kennwerte(10, 100, 0.1, sv.AUSSCHALTEN[0], 10e3, 24)["u_schalter"], 1010),
    ("RL aus Freilaufdiode: Zeit bis 0",
     lambda: sv.rl_aus_kennwerte(10, 100, 0.1, sv.AUSSCHALTEN[1], 10e3, 24)["t_null"], 1e-3 * 2.72696),
    ("RL aus Z-Diode: Zeit bis 0",
     lambda: sv.rl_aus_kennwerte(10, 100, 0.1, sv.AUSSCHALTEN[2], 10e3, 24)["t_null"], 1e-3 * 0.339936),
]
