# =============================================================================
# schaltungen/rc_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für RC-Schaltungen - KEIN tkinter.
# Einzeln testbar, z.B.:
#
#   python -c "from schaltungen.rc_mathe import *; print(rc_glied('Tiefpass', 10e3, 100e-9, 1e3))"
#
#   rc_glied()          Tief-/Hochpass 1. Ordnung: fg, Betrag |H|, Dämpfung in dB, Phase
#   bode_kurve()        Betrag in dB über log. Frequenzachse (für das Diagramm)
#   entprellung()       Taster + RC + Schmitt-Trigger: Simulation mit Prellen
#   entprell_zeiten()   Zeiten bis zu den Schaltschwellen (Dimensionierung)
#   anti_aliasing()     RC-Tiefpass vor einem ADC: Alias-Frequenz, Dämpfung, nötige Dämpfung
#
# Laden/Entladen (u_C(t)) und RL-Schaltvorgänge stehen schon in
#   bauteile/rechner/schaltvorgaenge_mathe.py  -> werden NICHT kopiert.
#
# WER RUFT DAS AUF?  schaltungen/grafiken_rc.py, schaltungen/rechner.py,
#                    messtechnik/grafiken.py (alias_frequenz für die Abtast-Grafik)
# =============================================================================

import math

FILTER_ARTEN = ["Tiefpass", "Hochpass"]

# Schmitt-Trigger-Schwellen als Anteil von U_B (typ. 74HC14 bei 5 V: 2.75 V / 1.65 V)
U_TP_ANTEIL = 0.55
U_TM_ANTEIL = 0.33

# Prellmuster beim DRÜCKEN: (Zeitpunkt als Anteil der Prellzeit, Kontakt geschlossen?)
# Die Pausen werden kürzer, bis der Kontakt nach der Prellzeit ruhig liegt.
PRELLEN = [(0.00, True), (0.10, False), (0.18, True), (0.34, False), (0.40, True),
           (0.58, False), (0.62, True), (0.80, False), (0.83, True)]


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


# =============================================================================
# TIEF- UND HOCHPASS
# =============================================================================
def rc_glied(art, r, c, f):
    """
    RC-Glied 1. Ordnung bei der Frequenz f.
      fg = 1 / (2π · R · C)          x = f / fg
      Tiefpass:  |H| = 1 / √(1 + x²)      φ = −arctan(x)
      Hochpass:  |H| = x / √(1 + x²)      φ = 90° − arctan(x)
      Dämpfung in dB = 20 · log10(|H|)
    Rückgabe: dict mit fg, tau, x_c (Blindwiderstand bei f), betrag, db, phase (Grad)
    """
    _positiv(R=r, C=c, f=f)
    if art not in FILTER_ARTEN:
        raise ValueError(f"Unbekannte Filterart: {art}")
    fg = 1 / (2 * math.pi * r * c)
    x = f / fg
    nenner = math.sqrt(1 + x * x)
    if art == "Tiefpass":
        betrag, phase = 1 / nenner, -math.degrees(math.atan(x))
    else:
        betrag, phase = x / nenner, 90 - math.degrees(math.atan(x))
    return {"fg": fg, "tau": r * c, "x_c": 1 / (2 * math.pi * f * c), "betrag": betrag,
            "db": 20 * math.log10(betrag), "phase": phase}


def bode_kurve(art, dekaden=2, punkte=121):
    """
    Betragsgang in dB für das Diagramm, Frequenz relativ zu fg:
    x-Achse 0 … 1  =  fg / 10^dekaden … fg · 10^dekaden (logarithmisch, Mitte = fg).
    """
    kurve = []
    for k in range(punkte):
        t = k / (punkte - 1)
        x = 10 ** (dekaden * (2 * t - 1))
        betrag = 1 / math.sqrt(1 + x * x) if art == "Tiefpass" else x / math.sqrt(1 + x * x)
        kurve.append((t, 20 * math.log10(betrag)))
    return kurve


def bode_position(f, fg, dekaden=2):
    """Wo liegt f auf der x-Achse von bode_kurve()? (0 … 1, ausserhalb abgeschnitten)"""
    t = (math.log10(f / fg) / dekaden + 1) / 2
    return min(max(t, 0.0), 1.0)


# =============================================================================
# TASTER ENTPRELLEN
# =============================================================================
def schwellen(u_b):
    """Schmitt-Trigger-Schwellen (U_T+, U_T−) für die Versorgung u_b."""
    return U_TP_ANTEIL * u_b, U_TM_ANTEIL * u_b


def entprell_zeiten(u_b, r1, r2, c):
    """
    Schaltung: Pull-up R1 von U_B zum Knoten A, Taster von A nach GND,
               R2 von A zum Kondensator C (Eingang des Schmitt-Triggers).
      Drücken:    C entlädt über R2           τ_ab = R2 · C
                  bis U_T−:  t_ab = R2 · C · ln(U_B / U_T−)
      Loslassen:  C lädt über R1 + R2          τ_auf = (R1 + R2) · C
                  bis U_T+:  t_auf = (R1 + R2) · C · ln(U_B / (U_B − U_T+))
    Damit das Prellen nicht durchkommt, sollten t_ab und t_auf länger als die Prellzeit sein.
    """
    _positiv(U_B=u_b, R1=r1, R2=r2, C=c)
    u_tp, u_tm = schwellen(u_b)
    tau_ab, tau_auf = r2 * c, (r1 + r2) * c
    return {"u_tp": u_tp, "u_tm": u_tm, "tau_ab": tau_ab, "tau_auf": tau_auf,
            "t_ab": tau_ab * math.log(u_b / u_tm), "t_auf": tau_auf * math.log(u_b / (u_b - u_tp)),
            "i_kontakt": u_b / r2 + u_b / r1}


def kontakt(t, t_druck, t_los, t_prell):
    """Kontakt geschlossen? Drücken bei t_druck, Loslassen bei t_los, jeweils mit Prellen."""
    if t < t_druck:
        return False
    if t < t_druck + t_prell:
        zustand = True
        for anteil, geschlossen in PRELLEN:
            if t >= t_druck + anteil * t_prell:
                zustand = geschlossen
        return zustand
    if t < t_los:
        return True
    if t < t_los + t_prell:
        zustand = False
        for anteil, geschlossen in PRELLEN:
            if t >= t_los + anteil * t_prell:
                zustand = not geschlossen
        return zustand
    return False


def entprellung(u_b, r1, r2, c, t_prell, mit_rc=True, punkte=900):
    """
    Simulation: Taste wird gedrückt (prellt), gehalten, losgelassen (prellt wieder).
      mit_rc=True   Knoten A -> R2 -> C -> Schmitt-Trigger (invertierend, z.B. 74HC14)
      mit_rc=False  Knoten A direkt an einen Eingang mit EINER Schwelle (U_B / 2)
    Jeder Zeitschritt wird exakt gerechnet (Kontakt ist innerhalb eines Schritts konstant):
      u_neu = u_ziel + (u − u_ziel) · e^(−Δt/τ)
    Rückgabe: Kurven [(t 0…1, wert)] für Kontakt, u_C (bzw. u_A), Ausgang (1 = gedrückt erkannt)
              und die Zahl der erkannten Tastendrücke / Loslass-Flanken.
    """
    _positiv(U_B=u_b, R1=r1, C=c, Prellzeit=t_prell)
    if mit_rc:
        _positiv(R2=r2)
    k = entprell_zeiten(u_b, r1, r2 if mit_rc else r1, c)
    # Fenster: Prellen + Umladen müssen sichtbar sein
    abschnitt = max(1.6 * t_prell, 1.3 * (k["t_auf"] if mit_rc else 0), 1.3 * (k["t_ab"] if mit_rc else 0))
    t_druck, t_los, t_ende = 0.12 * abschnitt, 1.12 * abschnitt, 2.12 * abschnitt
    dt = t_ende / punkte
    u, aus = u_b, 0
    u_tp, u_tm = (k["u_tp"], k["u_tm"]) if mit_rc else (u_b / 2, u_b / 2)
    kurve_k, kurve_u, kurve_a = [], [], []
    druecke = loslassen = 0
    verzoegerung = None
    for n in range(punkte + 1):
        t = n * dt
        zu = kontakt(t, t_druck, t_los, t_prell)
        if mit_rc:
            ziel, tau = (0.0, r2 * c) if zu else (u_b, (r1 + r2) * c)
            u = ziel + (u - ziel) * math.exp(-dt / tau) if n else u
        else:
            u = 0.0 if zu else u_b
        neu = 1 if u < u_tm else (0 if u > u_tp else aus)      # Hysterese (ohne RC: beide Schwellen gleich)
        if neu != aus:
            if neu:
                druecke += 1
                if verzoegerung is None:
                    verzoegerung = t - t_druck
            else:
                loslassen += 1
        aus = neu
        kurve_k.append((t / t_ende, 1.0 if zu else 0.0))
        kurve_u.append((t / t_ende, u))
        kurve_a.append((t / t_ende, float(aus)))
    return {**k, "u_tp": u_tp, "u_tm": u_tm, "kontakt": kurve_k, "u_c": kurve_u, "ausgang": kurve_a,
            "druecke": druecke, "loslassen": loslassen, "verzoegerung": verzoegerung,
            "t_ende": t_ende, "t_druck": t_druck, "t_los": t_los, "sauber": druecke == 1 and loslassen == 1}


# =============================================================================
# ANTI-ALIASING
# =============================================================================
def alias_frequenz(f, f_s):
    """
    Frequenz, die nach dem Abtasten mit f_s sichtbar ist (mit Vorzeichen, −f_s/2 … +f_s/2):
      f_alias = f − n · f_s   (n = nächste ganze Zahl zu f / f_s)
    Unter f_s / 2 (Nyquist) bleibt die Frequenz erhalten.
    """
    _positiv(f=f, f_s=f_s)
    return f - round(f / f_s) * f_s


def anti_aliasing(f_s, f, r=None, c=None, bits=None):
    """
    RC-Tiefpass vor einem ADC.
      f_alias            sichtbare Frequenz nach dem Abtasten
      betrag / db        Dämpfung des Filters bei f (ohne R/C: 1 bzw. 0 dB)
      betrag_nyquist     Dämpfung bei f_s / 2
      noetig_db          damit eine Vollausschlag-Störung unter 1/2 LSB fällt:  6.02 · N dB
                         (Sinus über den ganzen Bereich: Amplitude 2^(N−1) LSB -> Faktor 2^N bis 1/2 LSB)
      unsichtbar         Störung nach dem Filter kleiner als 1/2 LSB?
    """
    _positiv(f_s=f_s, f=f)
    f_alias = alias_frequenz(f, f_s)
    if r is None or c is None:
        betrag, betrag_ny, fg = 1.0, 1.0, None
    else:
        tp = rc_glied("Tiefpass", r, c, f)
        betrag, fg = tp["betrag"], tp["fg"]
        betrag_ny = rc_glied("Tiefpass", r, c, f_s / 2)["betrag"]
    e = {"f_alias": f_alias, "faltet": f > f_s / 2, "fg": fg, "nyquist": f_s / 2,
         "betrag": betrag, "db": 20 * math.log10(betrag),
         "betrag_nyquist": betrag_ny, "db_nyquist": 20 * math.log10(betrag_ny)}
    if bits is not None:
        if bits < 1 or bits > 32:
            raise ValueError("Auflösung zwischen 1 und 32 Bit eingeben")
        e["noetig_db"] = 6.02 * bits
        e["unsichtbar"] = -e["db"] >= e["noetig_db"]
    return e
