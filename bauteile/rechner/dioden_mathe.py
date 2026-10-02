# =============================================================================
# bauteile/rechner/dioden_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für Dioden - KEIN tkinter hier drin.
# Einzeln testbar, z.B. in der Konsole:
#
#   python -c "from bauteile.rechner.dioden_mathe import *; print(z_diode_vorwiderstand(11, 14, 5.1, 0.02, 0.005, 0.5))"
#
#   shockley()                  Diodengleichung I(U)
#   durchlassspannung()         U_F bei anderem Strom / anderer Temperatur
#   z_diode_vorwiderstand()     Z-Diode als Spannungsstabilisierung
#   gleichrichter()             Einweg / Mittelpunkt / Brücke mit Ladekondensator
#
# Der LED-Vorwiderstand steht schon in bauteile/rechner/widerstand_rechner.py (_led)
# und wird auf der Dioden-Seite einfach per ID "led_vorwiderstand" mitbenutzt.
#
# WER RUFT DAS AUF?
#   bauteile/rechner/dioden_rechner.py       (Rechner-Karten)
#   bauteile/grafiken/dioden_kennlinie.py    (interaktive Kennlinie)
# =============================================================================

import math

from bauteile.rechner import normreihen      # -> rechner/normreihen.py

U_F_SI = 0.7              # V, Durchlassspannung Silizium (Faustwert)
TK_U_F = -2e-3            # V/K, U_F sinkt um ca. 2 mV pro Kelvin
K_DURCH_Q = 8.617e-5      # V/K, Boltzmann-Konstante / Elementarladung  (U_T = k·T/q)


def temperaturspannung(t_celsius=25.0):
    """U_T = k · T / q  ->  ca. 25.7 mV bei 25 °C."""
    return K_DURCH_Q * (t_celsius + 273.15)


def shockley(u, i_s=1e-12, n=1.8, u_t=0.02585):
    """Diodengleichung (Shockley):  I = I_S · (e^(U / (n·U_T)) − 1)"""
    return i_s * (math.exp(u / (n * u_t)) - 1)


def durchlassspannung(u_f1, i_1, i_2=None, t=25.0, n=1.8):
    """
    Wie ändert sich U_F, wenn sich Strom oder Temperatur ändern?

      Strom:       ΔU = n · U_T · ln(I2 / I1)      -> pro Dekade (×10) ca. 60 … 120 mV mehr
      Temperatur:  ΔU ≈ −2 mV/K · (T − 25 °C)

    u_f1, i_1   Wertepaar aus dem Datenblatt (bei 25 °C)
    i_2         neuer Strom (None = gleicher Strom)
    Rückgabe: dict  u_f2, du_strom, du_temp, p (Verlust bei i_2)
    """
    if i_1 <= 0 or (i_2 is not None and i_2 <= 0):
        raise ValueError("Ströme müssen grösser als 0 sein")
    i_2 = i_1 if i_2 is None else i_2
    du_strom = n * temperaturspannung(t) * math.log(i_2 / i_1)
    du_temp = TK_U_F * (t - 25.0)
    u_f2 = u_f1 + du_strom + du_temp
    return {"u_f2": u_f2, "du_strom": du_strom, "du_temp": du_temp, "p": u_f2 * i_2, "i_2": i_2}


def z_diode_vorwiderstand(u_e_min, u_e_max, u_z, i_l_max, i_z_min, p_tot=None, i_l_min=0.0, reihe="E12"):
    """
    Z-Diode als einfache Spannungsstabilisierung:   U_E ──[R_V]──┬── U_Z ── Last
                                                                  Z
    Zwei schlimmste Fälle prüfen:
      1) U_E MIN und Last MAX:  Durch die Z-Diode muss noch I_Z,min fliessen
         -> R_V ≤ (U_E,min − U_Z) / (I_L,max + I_Z,min)       -> Normwert ABrunden
      2) U_E MAX und Last MIN (Leerlauf): fast alles fliesst durch die Z-Diode
         -> I_Z,max = (U_E,max − U_Z) / R_V − I_L,min
         -> P_Z = U_Z · I_Z,max  muss kleiner als P_tot sein

    Rückgabe: dict mit allen Zwischenwerten
    """
    if u_e_max < u_e_min:
        raise ValueError("U_E,max muss grösser oder gleich U_E,min sein")
    if u_e_min <= u_z:
        raise ValueError("U_E,min muss grösser als U_Z sein (sonst bleibt nichts für R_V)")
    if i_l_max < 0 or i_z_min <= 0:
        raise ValueError("I_Z,min muss grösser als 0 sein")

    r_max = (u_e_min - u_z) / (i_l_max + i_z_min)
    r_v = normreihen.naechste_werte(r_max, reihe)[0]            # [0] = nächst KLEINERER Normwert
    i_z_max = (u_e_max - u_z) / r_v - i_l_min
    p_z = u_z * i_z_max
    p_rv = (u_e_max - u_z) ** 2 / r_v

    # Kleinster erlaubter R_V (sonst wird die Z-Diode im Leerlauf zu heiss)
    r_min = None
    if p_tot is not None:
        i_z_erlaubt = p_tot / u_z
        r_min = (u_e_max - u_z) / (i_z_erlaubt + i_l_min)
    return {
        "r_max": r_max, "r_v": r_v, "r_min": r_min,
        "i_z_max": i_z_max, "p_z": p_z, "p_rv": p_rv,
        "i_z_bei_min": (u_e_min - u_z) / r_v - i_l_max,          # Z-Strom im Fall 1 (mit Normwert)
        "ok": p_tot is None or p_z <= p_tot,
    }


# Gleichrichter-Schaltungen:  Dioden im Strompfad, Brummfrequenz-Faktor, Sperrspannung (× Û), Strom pro Diode
SCHALTUNGEN = {
    "Einweg (M1)":        {"n": 1, "f_faktor": 1, "sperr": 2.0, "i_anteil": 1.0, "dioden": 1},
    "Mittelpunkt (M2)":   {"n": 1, "f_faktor": 2, "sperr": 2.0, "i_anteil": 0.5, "dioden": 2},
    "Brücke (B2 Graetz)": {"n": 2, "f_faktor": 2, "sperr": 1.0, "i_anteil": 0.5, "dioden": 4},
}


def gleichrichter(u_eff, schaltung, u_f=U_F_SI, i_last=None, c=None, u_brumm_soll=None, f_netz=50.0):
    """
    Gleichrichter mit Ladekondensator.

      Û       = U_eff · √2                      (Mittelpunkt: U_eff pro Wicklungshälfte)
      U_DC    ≈ Û − n · U_F                     n = Dioden im Strompfad (Brücke: 2)
      U_Br,ss ≈ I / (f_Br · C)                  f_Br = f (Einweg) oder 2f (Mittelpunkt, Brücke)
      C       ≥ I / (f_Br · U_Br,ss)            wenn eine Brummspannung vorgegeben ist
      Sperrspannung pro Diode: Brücke ≥ Û, Einweg und Mittelpunkt ≥ 2 · Û (mit Ladekondensator)

    Rückgabe: dict
    """
    if schaltung not in SCHALTUNGEN:
        raise ValueError(f"Unbekannte Schaltung: {schaltung}")
    if u_eff <= 0:
        raise ValueError("U_eff muss grösser als 0 sein")
    s = SCHALTUNGEN[schaltung]
    u_spitze = u_eff * math.sqrt(2)
    u_dc = u_spitze - s["n"] * u_f
    if u_dc <= 0:
        raise ValueError("Spannung zu klein – die Dioden brauchen schon alles")
    f_brumm = s["f_faktor"] * f_netz
    e = {"u_spitze": u_spitze, "u_dc": u_dc, "f_brumm": f_brumm,
         "u_sperr": s["sperr"] * u_spitze, "u_brumm": None, "c_noetig": None,
         "i_diode": None, "p_dioden": None, "dioden": s["dioden"]}
    if i_last is not None:
        e["i_diode"] = s["i_anteil"] * i_last                     # Mittelwert pro Diode
        e["p_dioden"] = s["n"] * u_f * i_last                      # alle leitenden Dioden zusammen
        if c is not None:
            e["u_brumm"] = i_last / (f_brumm * c)
        if u_brumm_soll is not None:
            if u_brumm_soll <= 0:
                raise ValueError("Brummspannung muss grösser als 0 sein")
            e["c_noetig"] = i_last / (f_brumm * u_brumm_soll)
    return e
