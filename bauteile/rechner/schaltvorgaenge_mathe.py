# =============================================================================
# bauteile/rechner/schaltvorgaenge_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für Schaltvorgänge an RC- und RL-Gliedern.
# KEIN tkinter hier drin - einzeln testbar, z.B.:
#
#   python -c "from bauteile.rechner.schaltvorgaenge_mathe import *; print(rc(0.1, 10e3, 10e-6, 0, 5))"
#
# VORZEICHEN (Verbraucher-Zählpfeilsystem, wie in der Grafik erklärt):
#   Kondensator: i_C > 0  = Strom fliesst IN den Kondensator (er lädt)
#                i_C < 0  = Strom fliesst HERAUS (er entlädt)
#   Spule:       u_L > 0  = Spannung bremst einen steigenden Strom (Einschalten)
#                u_L < 0  = Spannung kehrt um und treibt den Strom weiter (Ausschalten)
#
# WER RUFT DAS AUF?  bauteile/grafiken/kurven.py (Lernansicht RC / RL)
# =============================================================================

import math

U_DIODE = 0.7          # V, Durchlassspannung der Freilaufdiode

# Ausschaltpfad der Spule -> Text für die Anzeige
AUSSCHALTEN = ["ohne Freilaufdiode (R_aus)", "Freilaufdiode", "Diode + Z-Diode"]


# =============================================================================
# KONDENSATOR
# =============================================================================
def rc(t, r, c, u_start, u_ende):
    """
    Kondensator über R an eine Spannung u_ende geschaltet (Laden: Quelle, Entladen: 0 V).

      u_C(t) = u_ende + (u_start − u_ende) · e^(−t/τ)          τ = R · C
      i_C(t) = (u_ende − u_start) / R · e^(−t/τ)              (> 0 lädt, < 0 entlädt)

    Rückgabe: (u_C, i_C) zum Zeitpunkt t (t < 0: Zustand vor dem Schalten, i = 0)
    """
    if t < 0:
        return u_start, 0.0
    e = math.exp(-t / (r * c))
    return u_ende + (u_start - u_ende) * e, (u_ende - u_start) / r * e


# =============================================================================
# SPULE
# =============================================================================
def rl_ein(t, r, l, u, i_start=0.0):
    """
    Spule mit Drahtwiderstand R an die Spannung U geschaltet.

      i_L(t) = U/R + (i_start − U/R) · e^(−t/τ)                τ_ein = L / R
      u_L(t) = U − R · i_L(t)                                  (= L · di/dt, beim Einschalten zuerst = U)

    Rückgabe: (i_L, u_L)   (t < 0: vor dem Einschalten)
    """
    if t < 0:
        return i_start, 0.0
    i_end = u / r
    i = i_end + (i_start - i_end) * math.exp(-t * r / l)
    return i, u - r * i


def ausschaltpfad(art, r_spule, r_aus, u_z):
    """
    Welcher Widerstand und welche Gegenspannung wirken im AUSSCHALT-Pfad?
      ohne Freilaufdiode:  Strom muss über R_aus (Modell für den sperrenden Schalter / Durchbruch)
      Freilaufdiode:       Kreis Spule -> Diode, Gegenspannung U_F ≈ 0.7 V
      Diode + Z-Diode:     Gegenspannung U_F + U_Z  -> Strom klingt schneller ab

    Rückgabe: (R_Kreis, U_Gegen)
    """
    if art == AUSSCHALTEN[0]:
        return r_spule + r_aus, 0.0
    if art == AUSSCHALTEN[1]:
        return r_spule, U_DIODE
    if art == AUSSCHALTEN[2]:
        return r_spule, U_DIODE + u_z
    raise ValueError(f"Unbekannter Ausschaltpfad: {art}")


def rl_aus(t, r_kreis, l, i_start, u_gegen):
    """
    Spule wird abgeschaltet; der Strom fliesst im Ausschaltpfad weiter.
    Maschenregel:  L · di/dt + R_Kreis · i + U_Gegen = 0

      i_L(t) = (i_start + U_G/R) · e^(−t/τ) − U_G/R            τ_aus = L / R_Kreis
      u_L(t) = −(R_Kreis · i_L + U_Gegen)                      (negativ: Polarität kehrt um)
      ist i_L = 0 erreicht (bei Gegenspannung), bleibt alles bei 0.

    Rückgabe: (i_L, u_L)   (t < 0: Strom fliesst noch normal, u_L = 0)
    """
    if t < 0:
        return i_start, 0.0
    tau = l / r_kreis
    if u_gegen > 0:
        i = (i_start + u_gegen / r_kreis) * math.exp(-t / tau) - u_gegen / r_kreis
        if i <= 0:
            return 0.0, 0.0
    else:
        i = i_start * math.exp(-t / tau)
    return i, -(r_kreis * i + u_gegen)


def rl_aus_kennwerte(u, r_spule, l, art, r_aus, u_z):
    """
    Kennwerte des Ausschaltvorgangs (Strom vorher = U / R_Spule):
      tau_aus     L / R_Kreis
      t_null      Zeit bis i = 0 (nur mit Gegenspannung, sonst None = klingt nur ab)
      u_schalter  höchste Spannung am Schalter (Transistor):  U + |u_L(0)|
      energie     W = ½ · L · I²  (muss im Ausschaltpfad in Wärme umgesetzt werden)
    """
    i0 = u / r_spule
    r_kreis, u_gegen = ausschaltpfad(art, r_spule, r_aus, u_z)
    tau = l / r_kreis
    t_null = tau * math.log(1 + i0 * r_kreis / u_gegen) if u_gegen > 0 else None
    u_l0 = r_kreis * i0 + u_gegen
    # Am Schalter: ohne Diode liegt die volle Abschaltspannung an (U + I·R_aus),
    # mit Freilaufpfad nur U + Spannung an Diode (+ Z-Diode)
    u_schalter = u + (i0 * r_aus if art == AUSSCHALTEN[0] else u_gegen)
    return {"i0": i0, "r_kreis": r_kreis, "u_gegen": u_gegen, "tau": tau, "t_null": t_null,
            "u_l0": u_l0, "u_schalter": u_schalter, "energie": 0.5 * l * i0 * i0}
