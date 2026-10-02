# =============================================================================
# schaltungen/verstaerker_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für Transistor-Grundschaltungen - KEIN tkinter.
# Einzeln testbar, z.B.:
#
#   python -c "from schaltungen.verstaerker_mathe import *; print(emitterschaltung(12, 47e3, 10e3, 2.2e3, 1e3))"
#
#   emitterschaltung()     Arbeitspunkt (Basisteiler, Rc, Re) + Kleinsignal: Verstärkung, r_ein, Übersteuerung
#   emitterfolger()        Kollektorschaltung: Ua = Ue − 0.7 V, Strom-/Impedanzwandler
#   konstantstrom_bjt()    Transistor-Stromquelle mit Z-Diode (oder Dioden/LED) an der Basis
#   konstantstrom_jfet()   JFET mit Source-Widerstand (2-Pol-Stromquelle)
#   r_s_fuer_jfet()        R_S für einen gewünschten JFET-Strom
#
# MODELL (Kleinsignal, reicht für HF-Niveau):
#   U_BE = 0.7 V,  U_CE,sat = 0.2 V,  Temperaturspannung U_T = 26 mV
#   r_e  = U_T / I_E   (differentieller Emitterwiderstand),   r_be = β · U_T / I_C
#   Spannungsverstärkung  Vu = −β · R_C,ac / (r_be + (β + 1) · R_E,ac)  ≈ −R_C,ac / (r_e + R_E,ac)
#
# WER RUFT DAS AUF?  schaltungen/grafiken_transistor.py, schaltungen/rechner.py,
#                    bauteile/rechner/halbleiter_rechner.py (Arbeitspunkt-Rechner)
# =============================================================================

import math

U_BE = 0.7
U_CE_SAT = 0.2
U_T = 0.026


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


def _parallel(a, b):
    return a * b / (a + b)


# =============================================================================
# EMITTERSCHALTUNG
# =============================================================================
def emitterschaltung(u_b, r1, r2, r_c, r_e=0.0, beta=200.0, u_be=U_BE, c_e=False, r_l=None, u_hat=0.0,
                     punkte=241):
    """
    Basisteiler R1 (oben) / R2 (unten), R_C am Kollektor, R_E am Emitter (optional mit C_E überbrückt),
    Ein- und Ausgang über Koppelkondensatoren (Gleichanteil wird abgetrennt).
    Rückgabe dict: zustand ("sperrt" | "gesättigt" | "aktiv"), Arbeitspunkt, vu, r_ein, r_aus,
                   kurve_ideal / kurve_aus (Wechselanteil am Ausgang, t 0…1, ein Sinus)
    """
    _positiv(U_B=u_b, R1=r1, R2=r2, R_C=r_c, beta=beta)
    if r_e < 0:
        raise ValueError("R_E darf nicht negativ sein")
    u_th = u_b * r2 / (r1 + r2)                               # Ersatzspannungsquelle des Basisteilers
    r_th = _parallel(r1, r2)
    e = {"u_th": u_th, "r_th": r_th, "i_quer": (u_b - u_th) / r1}
    if u_th <= u_be:
        e.update(zustand="sperrt", i_b=0.0, i_c=0.0, i_e=0.0, u_ce=u_b, u_c=u_b, u_e=0.0, p_t=0.0)
        return e
    i_b = (u_th - u_be) / (r_th + (beta + 1) * r_e)
    i_c = beta * i_b
    i_e = i_c + i_b
    u_e = i_e * r_e
    u_c = u_b - i_c * r_c
    u_ce = u_c - u_e
    e.update(i_b=i_b, i_c=i_c, i_e=i_e, u_e=u_e, u_c=u_c, u_ce=u_ce)
    if u_ce < 0.3:
        if r_c + r_e <= 0 or u_b <= U_CE_SAT:
            raise ValueError("Ub zu klein für einen Arbeitspunkt (Uce,sat ≈ 0.2 V)")
        e.update(zustand="gesättigt", i_c_sat=(u_b - U_CE_SAT) / (r_c + r_e))
        return e
    # ---- Kleinsignal ----
    r_e_diff = U_T / i_e
    r_be = beta * U_T / i_c
    r_e_ac = 0.0 if c_e else r_e
    r_c_ac = r_c if r_l is None else _parallel(r_c, r_l)
    vu = -beta * r_c_ac / (r_be + (beta + 1) * r_e_ac)
    r_ein = _parallel(r_th, r_be + (beta + 1) * r_e_ac)
    # ---- Aussteuerung: Kollektor kann zwischen U_E + U_CE,sat und U_B schwingen ----
    oben, unten = u_b - u_c, (u_e + U_CE_SAT) - u_c            # erlaubte Abweichung vom Arbeitspunkt
    ideal, aus = [], []
    for k in range(punkte):
        t = k / (punkte - 1)
        u = vu * u_hat * math.sin(2 * math.pi * t)
        ideal.append((t, u))
        aus.append((t, min(max(u, unten), oben)))
    e.update(zustand="aktiv", r_e_diff=r_e_diff, r_be=r_be, vu=vu, r_ein=r_ein, r_aus=r_c,
             p_t=u_ce * i_c, oben=oben, unten=unten, u_a_hat=abs(vu) * u_hat,
             uebersteuert=abs(vu) * u_hat > min(oben, -unten), kurve_ideal=ideal, kurve_aus=aus)
    return e


# =============================================================================
# EMITTERFOLGER
# =============================================================================
def emitterfolger(u_b, u_e, r_e, r_l=None, beta=200.0, r_q=0.0, u_hat=0.0, punkte=241):
    """
    Kollektor an +U_B, Eingang an der Basis (gleichstromgekoppelt), R_E (parallel R_L) nach GND.
      Ua = Ue − U_BE   (solange 0 < Ua < U_B − U_CE,sat)
      Vu = R / (r_e + R) ≈ 1,   r_ein ≈ (β + 1) · (r_e + R),   r_aus ≈ r_e + R_q / (β + 1)
    """
    _positiv(U_B=u_b, R_E=r_e, beta=beta)
    r = r_e if r_l is None else _parallel(r_e, r_l)
    u_max = u_b - U_CE_SAT

    def ausgang(u):
        return min(max(u - U_BE, 0.0), u_max)

    u_a = ausgang(u_e)
    i_e = u_a / r
    i_b = i_e / (beta + 1)
    e = {"u_a": u_a, "i_e": i_e, "i_b": i_b, "r": r, "p_t": (u_b - u_a) * i_e,
         "leitet": u_a > 0, "begrenzt": u_e - U_BE >= u_max}
    if i_e > 0:
        r_diff = U_T / i_e
        e.update(vu=r / (r_diff + r), r_ein=(beta + 1) * (r_diff + r), r_aus=r_diff + r_q / (beta + 1))
    else:
        e.update(vu=0.0, r_ein=None, r_aus=None)
    ein, aus = [], []
    for k in range(punkte):
        t = k / (punkte - 1)
        u = u_e + u_hat * math.sin(2 * math.pi * t)
        ein.append((t, u))
        aus.append((t, ausgang(u)))
    e.update(kurve_ein=ein, kurve_aus=aus,
             abgeschnitten=(u_e - u_hat - U_BE < 0) or (u_e + u_hat - U_BE > u_max))
    return e


# =============================================================================
# KONSTANTSTROMQUELLEN
# =============================================================================
def konstantstrom_bjt(u_b, u_ref, r_e, r_last, beta=200.0):
    """
    Basis auf fester Spannung U_ref (Z-Diode, 2 Dioden, LED), Last im Kollektor, R_E am Emitter:
      I ≈ (U_ref − U_BE) / R_E                 unabhängig von der Last
    solange der Transistor nicht sättigt:  I · R_Last ≤ U_B − (U_ref − U_BE) − U_CE,sat
    """
    _positiv(U_B=u_b, R_E=r_e)
    if r_last < 0:
        raise ValueError("R_Last darf nicht negativ sein")
    if u_ref <= U_BE:
        raise ValueError("U_ref muss über U_BE = 0.7 V liegen")
    if u_ref >= u_b:
        raise ValueError("U_ref muss kleiner als U_B sein")
    i_soll = (u_ref - U_BE) / r_e * beta / (beta + 1)          # I_C = α · I_E
    u_last_max = u_b - (u_ref - U_BE) - U_CE_SAT
    r_last_max = u_last_max / i_soll
    if r_last <= r_last_max:
        i, regelt = i_soll, True
    else:
        i, regelt = (u_b - U_CE_SAT) / (r_last + r_e), False    # gesättigt: Last + R_E begrenzen
    u_ce = u_b - i * r_last - i * r_e
    return {"i": i, "i_soll": i_soll, "regelt": regelt, "u_last_max": u_last_max, "r_last_max": r_last_max,
            "u_ce": u_ce, "p_t": max(u_ce, 0.0) * i, "u_last": i * r_last}


def jfet_strom(i_dss, u_p, r_s):
    """Arbeitspunkt JFET mit Source-Widerstand:  I_D = I_DSS · (1 − I_D · R_S / U_P)²   (U_P als Betrag)."""
    _positiv(I_DSS=i_dss, U_P=u_p)
    if r_s < 0:
        raise ValueError("R_S darf nicht negativ sein")
    if r_s == 0:
        return i_dss
    a = r_s / u_p
    A, B, C = i_dss * a * a, -(2 * i_dss * a + 1), i_dss
    return (-B - math.sqrt(B * B - 4 * A * C)) / (2 * A)      # kleinere Lösung (U_GS zwischen U_P und 0)


def konstantstrom_jfet(u_b, i_dss, u_p, r_s, r_last):
    """
    N-Kanal-JFET, Gate an GND, R_S zwischen Source und GND -> U_GS = −I · R_S regelt sich selbst ein.
    Konstant, solange der Kanal abgeschnürt ist:  U_DS ≥ U_P − |U_GS|
    """
    i_k = jfet_strom(i_dss, u_p, r_s)
    u_gs = -i_k * r_s
    u_ds_min = u_p - abs(u_gs)
    u_last_max = u_b - i_k * r_s - u_ds_min
    r_last_max = u_last_max / i_k if u_last_max > 0 else 0.0
    if r_last <= r_last_max:
        i, regelt = i_k, True
    else:                                                     # ohmscher Bereich: Kanal ≈ Widerstand
        r_on = u_p / (2 * i_dss)
        i, regelt = min(i_k, u_b / (r_last + r_s + r_on)), False
    return {"i": i, "i_soll": i_k, "u_gs": u_gs, "regelt": regelt, "u_last_max": u_last_max,
            "r_last_max": r_last_max, "u_ds": u_b - i * (r_last + r_s), "u_last": i * r_last}


def r_s_fuer_jfet(i_soll, i_dss, u_p):
    """R_S für einen gewünschten Strom:  U_GS = −U_P · (1 − √(I / I_DSS)),  R_S = |U_GS| / I."""
    _positiv(I=i_soll, I_DSS=i_dss, U_P=u_p)
    if i_soll > i_dss:
        raise ValueError("Mehr als I_DSS liefert der JFET nicht (Gate an Source = grösster Strom)")
    u_gs = -u_p * (1 - math.sqrt(i_soll / i_dss))
    return abs(u_gs) / i_soll, u_gs
