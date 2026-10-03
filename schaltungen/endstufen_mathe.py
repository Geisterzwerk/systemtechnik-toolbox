# =============================================================================
# schaltungen/endstufen_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für ENDSTUFEN - KEIN tkinter. Testbar, z.B.:
#
#   python -c "from schaltungen.endstufen_mathe import *; print(gegentakt('B', 12, 8, 8, 0))"
#
#   darlington()          Einzeltransistor oder Darlington als Schalter: Basisstrom, Sättigung, U_CE, Verlust
#   gegentakt_kennlinie() u_a(u_e) einer Gegentaktstufe (Klasse B: Totzone ±0.65 V, AB: mit Vorspannung)
#   gegentakt()           Sinus durch die Stufe: Kurven, Klirrfaktor (THD), Leistungen, Wirkungsgrad
#   endstufe_leistung()   Klasse-B-Leistungsbilanz: P_aus, P_auf, η, Verlust je Transistor (auch das Maximum)
#
# WER RUFT DAS AUF?  schaltungen/grafiken_endstufen.py, schaltungen/rechner.py
# =============================================================================

import math

U_BE = 0.65                         # Schwelle, ab der ein Si-Transistor merklich leitet
KLASSEN = ["Klasse B", "Klasse AB"]


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


# =============================================================================
# DARLINGTON
# =============================================================================
def darlington(art, u_st, r_b, i_last, beta1=100.0, beta2=100.0, u_be=0.7, u_cesat=0.2):
    """
    Einzeltransistor:  I_B = (U_St − 0.7) / R_B,   gesättigt wenn β · I_B ≥ I_Last,   U_CE ≈ 0.2 V
    Darlington:        β ≈ β1 · β2,   I_B = (U_St − 1.4) / R_B,   der Ausgangstransistor kann NICHT sättigen:
                       U_CE ≥ U_CE,sat(T1) + U_BE(T2) ≈ 0.9 V  -> mehr Verlust bei grossen Strömen
    """
    _positiv(U_St=u_st, R_B=r_b, I_Last=i_last, beta1=beta1, beta2=beta2)
    if art == "Einzeltransistor":
        beta, u_bes, u_ce_min = beta1, u_be, u_cesat
    elif art == "Darlington":
        beta, u_bes, u_ce_min = beta1 * beta2 + beta1 + beta2, 2 * u_be, u_cesat + u_be
    else:
        raise ValueError(f"Unbekannte Art: {art}")
    i_b = max(0.0, (u_st - u_bes) / r_b)
    i_c_moeglich = beta * i_b
    gesaettigt = i_c_moeglich >= i_last
    i_c = i_last if gesaettigt else i_c_moeglich
    return {"beta": beta, "i_b": i_b, "u_bes": u_bes, "i_c_moeglich": i_c_moeglich, "gesaettigt": gesaettigt,
            "i_c": i_c, "u_ce": u_ce_min if gesaettigt else None, "p": i_c * u_ce_min if gesaettigt else None,
            "ueberst": i_c_moeglich / i_last}


# =============================================================================
# GEGENTAKT-ENDSTUFE (Komplementär-Emitterfolger)
# =============================================================================
def gegentakt_kennlinie(klasse, u_e, u_bias=1.3, u_b=None):
    """
    Zwei Emitterfolger (NPN oben, PNP unten). Ohne Vorspannung (Klasse B) leitet ein Transistor erst ab
    |u_e| > 0.65 V -> Totzone um 0 (Übernahmeverzerrung). Klasse AB: Vorspannung U_bias (z.B. zwei Dioden
    ≈ 1.3 V) verschiebt beide Basen um ±U_bias/2 -> die Totzone schrumpft auf max(0, 0.65 V − U_bias/2).
    Ausgang begrenzt auf ±(U_B − 1 V).
    """
    tot = U_BE if klasse == "Klasse B" else max(0.0, U_BE - u_bias / 2)
    if u_e > tot:
        u_a = u_e - tot
    elif u_e < -tot:
        u_a = u_e + tot
    else:
        u_a = 0.0
    if u_b is not None:
        grenze = max(u_b - 1.0, 0.0)
        u_a = max(-grenze, min(grenze, u_a))
    return u_a


def gegentakt(klasse, u_b, u_hat, r_l, u_bias=1.3, punkte=400):
    """
    Sinus û am Eingang durch die Stufe (2 Perioden). Klirrfaktor aus den Oberschwingungen (DFT, Harmonische 2 … 15):
      THD = √(U2² + U3² + …) / U1
    Leistungen (Klasse B, idealisiert mit dem tatsächlichen Ausgang):
      P_aus = U_eff² / R_L      P_auf = 2 · U_B · Ī  (Mittelwert des Stroms aus jeder Versorgung)
    """
    _positiv(U_B=u_b, R_L=r_l)
    if u_hat < 0:
        raise ValueError("Amplitude darf nicht negativ sein")
    ein, aus = [], []
    for k in range(punkte):
        x = k / punkte
        ue = u_hat * math.sin(4 * math.pi * x)
        ein.append((x, ue))
        aus.append((x, gegentakt_kennlinie(klasse, ue, u_bias, u_b)))
    werte = [y for _x, y in aus]
    # Fourier-Koeffizienten (Grundschwingung = 2 Perioden im Fenster)
    def harmonische(n):
        a = sum(y * math.cos(2 * math.pi * 2 * n * k / punkte) for k, y in enumerate(werte)) * 2 / punkte
        b = sum(y * math.sin(2 * math.pi * 2 * n * k / punkte) for k, y in enumerate(werte)) * 2 / punkte
        return math.hypot(a, b)
    u1 = harmonische(1)
    oberw = math.sqrt(sum(harmonische(n) ** 2 for n in range(2, 16)))
    thd = oberw / u1 if u1 > 1e-12 else 0.0
    u_eff = math.sqrt(sum(y * y for y in werte) / punkte)
    i_mittel = sum(abs(y) for y in werte) / punkte / r_l
    p_aus = u_eff ** 2 / r_l
    p_auf = u_b * i_mittel                    # jede Halbwelle aus ihrer Versorgung: 2 · U_B · (Ī/2)
    ruhe = 0.0
    if klasse == "Klasse AB":
        ruhe = 0.02 * u_b * 2                  # angenommener Ruhestrom 20 mA durch beide Transistoren (Richtwert)
    p_auf += ruhe
    aus_ideal = [(x, y) for x, y in ein]
    return {"ein": ein, "aus": aus, "ideal": aus_ideal, "thd": thd, "p_aus": p_aus, "p_auf": p_auf,
            "eta": p_aus / p_auf if p_auf > 0 else 0.0, "p_verlust": p_auf - p_aus, "u_hat_aus": max(werte),
            "begrenzt": u_hat - (U_BE if klasse == "Klasse B" else 0) > u_b - 1.0 + 1e-9,
            "kennlinie": [(k / 100, gegentakt_kennlinie(klasse, -u_hat * 1.1 + 2.2 * u_hat * k / 100, u_bias, u_b))
                          for k in range(101)]}


def endstufe_leistung(u_b, r_l, u_hat=None, p_soll=None):
    """
    Klasse B, symmetrische Versorgung ±U_B, idealer Ausgang û:
      P_aus = û² / (2 · R_L)      P_auf = 2 · U_B · û / (π · R_L)      η = π/4 · û / U_B  (max. 78.5 %)
      Verlust beider Transistoren P_V = P_auf − P_aus, am grössten bei û = 2·U_B/π:  P_V,max = 2·U_B² / (π²·R_L)
    Mit p_soll statt u_hat: nötiges û = √(2 · P · R_L).
    """
    _positiv(U_B=u_b, R_L=r_l)
    if u_hat is None:
        _positiv(P=p_soll)
        u_hat = math.sqrt(2 * p_soll * r_l)
    p_aus = u_hat ** 2 / (2 * r_l)
    p_auf = 2 * u_b * u_hat / (math.pi * r_l)
    return {"u_hat": u_hat, "p_aus": p_aus, "p_auf": p_auf, "eta": p_aus / p_auf if p_auf else 0.0,
            "p_v": p_auf - p_aus, "p_v_max": 2 * u_b ** 2 / (math.pi ** 2 * r_l), "u_hat_max": u_b - 1.0,
            "i_spitze": u_hat / r_l, "reicht": u_hat <= u_b - 1.0}
