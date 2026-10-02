# =============================================================================
# bauteile/rechner/relais_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für Relais - KEIN tkinter hier drin.
# Einzeln testbar, z.B. in der Konsole:
#
#   python -c "from bauteile.rechner.relais_mathe import *; print(ansteuerung(5, 70, 3.3, 100))"
#
#   ansteuerung()      Relais mit NPN-Transistor schalten (Spulenstrom, R_B, Freilaufdiode)
#   spule_warm()       Reicht die Spannung noch, wenn die Spule heiss ist?
#   abschalten()       Freilaufdiode vs. Diode + Z-Diode: Spannung und Abfallzeit
#   kontakt_last()     Einschaltstrom der Last abschätzen (Lampe, Motor, Netzteil ...)
#
# WER RUFT DAS AUF?  bauteile/rechner/relais_rechner.py (Rechner-Karten)
# =============================================================================

import math

from bauteile.rechner import transistor_mathe      # -> rechner/transistor_mathe.py

ALPHA_CU = 0.00393       # 1/K, Temperaturkoeffizient Kupfer (Spulendraht)
U_F = 0.7                # V, Durchlassspannung der Freilaufdiode


def ansteuerung(u_b, r_spule, u_steuer, b_min, ue=transistor_mathe.UE_STANDARD):
    """
    Relais-Spule als Last eines NPN-Low-Side-Schalters.
    Die eigentliche Rechnung (I_C, I_B, R_B) macht transistor_mathe.schalter_dimensionieren().

    Zusätzlich:
      U_Spule = U_B − U_CE,sat       (so viel kommt an der Spule wirklich an)
      P_Spule = U_Spule² / R_Spule
      Freilaufdiode muss den Spulenstrom kurzzeitig tragen: I_F ≥ I_Spule, U_R ≥ U_B
    """
    if r_spule <= 0:
        raise ValueError("Spulenwiderstand muss grösser als 0 sein")
    e = transistor_mathe.schalter_dimensionieren(u_b, u_steuer, b_min, ue, r_last=r_spule)
    u_spule = u_b - transistor_mathe.U_CE_SAT
    e["u_spule"] = u_spule
    e["p_spule"] = u_spule ** 2 / r_spule
    # Diode vorschlagen: 1N4148 (I_F 300 mA, 100 V) für kleine Relais, sonst 1N4007 (1 A, 1000 V)
    e["diode"] = "1N4148" if e["i_c"] <= 0.2 and u_b <= 75 else "1N4007"
    return e


def spule_warm(u_n, r_20, t_spule, u_an_prozent=75.0, u_spule=None):
    """
    Kupfer hat bei Wärme mehr Widerstand -> weniger Strom -> weniger Magnetkraft.
    Die Ansprechspannung (Datenblatt, bei 20 °C, meist 70 … 80 % von U_N) steigt mit:

      R_T    = R_20 · (1 + α · (T − 20 °C))          α(Cu) = 0.00393 1/K
      U_an,T = U_an,20 · R_T / R_20

    u_spule   tatsächliche Spannung an der Spule (None = U_N)
    Rückgabe: dict  r_t, i_t, u_an_20, u_an_t, reserve (U_spule / U_an,T), ok
    """
    if r_20 <= 0 or u_n <= 0:
        raise ValueError("U_N und R_20 müssen grösser als 0 sein")
    u_spule = u_n if u_spule is None else u_spule
    faktor = 1 + ALPHA_CU * (t_spule - 20.0)
    r_t = r_20 * faktor
    u_an_20 = u_n * u_an_prozent / 100
    u_an_t = u_an_20 * faktor
    return {"r_t": r_t, "i_t": u_spule / r_t, "i_20": u_spule / r_20, "u_an_20": u_an_20,
            "u_an_t": u_an_t, "reserve": u_spule / u_an_t, "ok": u_spule >= u_an_t, "u_spule": u_spule}


def abschalten(u_b, r_spule, l=None, u_z=None):
    """
    Was passiert beim Abschalten der Spule?  Der Strom I = U_B / R will weiterfliessen.

      nur Diode:        U_CE,max ≈ U_B + U_F          Strom klingt langsam ab (lange Abfallzeit)
      Diode + Z-Diode:  U_CE,max ≈ U_B + U_Z + U_F    Strom klingt viel schneller ab

    Zeit bis der Strom 0 ist (Spule mit R, Gegenspannung U_G = U_F bzw. U_Z + U_F):
      i(t) = (I + U_G/R) · e^(−t/τ) − U_G/R     ->   t_0 = τ · ln(1 + I · R / U_G)     τ = L / R
    (Das Relais fällt schon bei ca. 10 … 30 % des Stroms ab - die Zeiten zeigen den VERGLEICH.)
    """
    if u_b <= 0 or r_spule <= 0:
        raise ValueError("U_B und Spulenwiderstand müssen grösser als 0 sein")
    i = u_b / r_spule
    tau = l / r_spule if l else None            # ohne L keine Zeiten, nur Spannungen

    def t_null(u_gegen):
        return tau * math.log(1 + i * r_spule / u_gegen) if tau is not None else None

    e = {"i": i, "tau": tau, "energie": 0.5 * l * i * i if l else None,
         "u_ce_diode": u_b + U_F, "t_diode": t_null(U_F),
         "u_ce_z": None, "t_z": None, "faktor": None}
    if u_z is not None:
        if u_z <= 0:
            raise ValueError("U_Z muss grösser als 0 sein")
        e["u_ce_z"] = u_b + u_z + U_F
        e["t_z"] = t_null(u_z + U_F)
        # wie viel schneller? (unabhängig von L)
        e["faktor"] = math.log(1 + u_b / U_F) / math.log(1 + u_b / (u_z + U_F))
    return e


# Lastart -> (Einschaltstrom-Faktor, Erklärung)
LASTARTEN = {
    "Ohmsch (Heizung)":            (1, "kein erhöhter Einschaltstrom"),
    "Glühlampe / Halogen":         (12, "kalter Glühfaden: 10 … 15 × Nennstrom für einige ms"),
    "Motor":                       (6, "Anlaufstrom 5 … 8 × Nennstrom, bis der Motor dreht"),
    "Trafo (Eisenkern)":           (10, "Einschalt-Rush bis 10 … 15 × (je nach Einschaltmoment)"),
    "LED-Treiber / Netzteil":      (30, "Ladeelko: sehr kurz 20 … 50 × – verschweisst Kontakte!"),
    "Induktiv DC (Ventil, Schütz)": (1, "kein Rush, aber Abschalt-Lichtbogen → Schutzbeschaltung"),
}


def kontakt_last(u, i_nenn, lastart, i_relais=None):
    """
    Grobe Abschätzung für die Kontaktbelastung:
      I_Ein ≈ Faktor · I_Nenn        (typische Faktoren, siehe LASTARTEN)
      P     = U · I_Nenn             (Scheinleistung bei AC)
    Rückgabe: dict  i_ein, faktor, text, p, reserve (Relais-Nennstrom / I_Nenn)
    """
    if lastart not in LASTARTEN:
        raise ValueError(f"Unbekannte Lastart: {lastart}")
    if i_nenn <= 0:
        raise ValueError("Laststrom muss grösser als 0 sein")
    faktor, text = LASTARTEN[lastart]
    return {"i_ein": faktor * i_nenn, "faktor": faktor, "text": text, "p": u * i_nenn if u else None,
            "reserve": i_relais / i_nenn if i_relais else None}
