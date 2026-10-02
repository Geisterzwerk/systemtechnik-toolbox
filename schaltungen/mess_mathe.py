# =============================================================================
# schaltungen/mess_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für SENSOR-MESSSCHALTUNGEN - KEIN tkinter. Einzeln testbar, z.B.:
#
#   python -c "from schaltungen.mess_mathe import *; print(pt_leitung('2-Leiter', 25, 100, 1.0))"
#
#   pt_leitung()          Pt100/Pt1000 in 2-, 3- oder 4-Leiter-Schaltung: Leitungsfehler + Eigenerwärmung
#   ntc_widerstand()      R(T) mit der B-Gleichung
#   ntc_teiler()          NTC im Spannungsteiler: U_aus, Empfindlichkeit in mV/K und ADC-Stufen pro K
#   ntc_linear_r()        Festwiderstand, der den Teiler zwischen T1 und T2 am besten linearisiert
#   bruecke_dms()         DMS-Brücke (Viertel/Halb/Voll) mit exakter Brückengleichung
#   inamp_verstaerkung()  Instrumentenverstärker: G = 1 + R_intern / R_G und umgekehrt
#   dms_kette()           Brücke -> Instrumentenverstärker -> ADC (Ausgang, Aussteuerung, Auflösung)
#
# Die Pt-Kennlinie (Callendar-Van Dusen) steht schon in messtechnik/rechner.py -> wird importiert, nicht kopiert.
# WER RUFT DAS AUF?  schaltungen/grafiken_mess.py, schaltungen/rechner.py
# =============================================================================

import math

from messtechnik.rechner import pt_temperatur, pt_widerstand          # -> messtechnik/rechner.py

PT_ARTEN = ["2-Leiter", "3-Leiter", "4-Leiter"]
DMS_ARTEN = ["Viertelbrücke", "Halbbrücke", "Vollbrücke"]
# Instrumentenverstärker: G = 1 + R_intern / R_G (Datenblattwerte)
INAMPS = {"INA128 / INA129 (50 kΩ)": 50e3, "AD620 (49.4 kΩ)": 49.4e3, "INA333 (100 kΩ)": 100e3}
T25 = 298.15


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


# =============================================================================
# PT100 / PT1000: LEITUNGSWIDERSTAND UND EIGENERWÄRMUNG
# =============================================================================
def pt_leitung(art, t, r0, r_l, unsymmetrie=0.0, i_mess=1e-3, k_mw=0.4):
    """
    Konstantstrom I durch den Sensor, gemessen wird eine Spannung.
      2-Leiter: Strom und Messung über dieselben 2 Adern     R_gemessen = R_T + 2 · R_L
      3-Leiter: zweite Ader kompensiert die erste            R_gemessen = R_T + R_L1 − R_L2
                (gleich lange Adern -> fehlerfrei; unsymmetrie = (R_L2 − R_L1) / R_L1)
      4-Leiter: eigene Messadern ohne Strom                  R_gemessen = R_T
    Eigenerwärmung: P = I² · R_T, ΔT = P · k (k in K/mW aus dem Datenblatt, z.B. 0.4 K/mW in ruhender Luft)
    Rückgabe: R_T, R gemessen, T angezeigt, Fehler in K (Leitung, Eigenerwärmung, gesamt), U_mess, P
    """
    _positiv(R0=r0, I=i_mess)
    if r_l < 0:
        raise ValueError("Leitungswiderstand darf nicht negativ sein")
    if art not in PT_ARTEN:
        raise ValueError(f"Unbekannte Schaltung: {art}")
    r_t = pt_widerstand(t, r0)
    p = i_mess ** 2 * r_t
    dt_eigen = p * 1e3 * k_mw
    r_warm = pt_widerstand(t + dt_eigen, r0)                     # der Sensor ist um ΔT wärmer
    zusatz = {"2-Leiter": 2 * r_l, "3-Leiter": r_l - r_l * (1 + unsymmetrie), "4-Leiter": 0.0}[art]
    r_gem = r_warm + zusatz
    if not pt_widerstand(-200.0, r0) <= r_gem <= pt_widerstand(850.0, r0):
        raise ValueError(f"Gemessener Widerstand {r_gem:.4g} Ω liegt ausserhalb des Pt-Bereichs (−200 … 850 °C) – "
                         "Messstrom oder Leitungswiderstand viel zu gross?")
    t_anzeige = pt_temperatur(r_gem, r0)
    return {"r_t": r_t, "r_gem": r_gem, "t_anzeige": t_anzeige, "fehler": t_anzeige - t,
            "fehler_leitung": pt_temperatur(r_t + zusatz, r0) - t, "fehler_eigen": dt_eigen,
            "u_mess": i_mess * r_gem, "p": p, "zusatz": zusatz}


def pt_fehlerkurve(art, t, r0, r_l_max, unsymmetrie=0.0, punkte=41):
    """Leitungsfehler in K über dem Leitungswiderstand 0 … r_l_max (für das Diagramm, ohne Eigenerwärmung)."""
    kurve = []
    for k in range(punkte):
        r_l = r_l_max * k / (punkte - 1)
        kurve.append((k / (punkte - 1), pt_leitung(art, t, r0, r_l, unsymmetrie, 1e-9)["fehler_leitung"]))
    return kurve


# =============================================================================
# NTC IM SPANNUNGSTEILER
# =============================================================================
def ntc_widerstand(t, r25, b):
    """R(T) = R25 · e^(B · (1/T − 1/T25)), T in °C (intern Kelvin)."""
    _positiv(R25=r25, B=b)
    if t <= -273.15:
        raise ValueError("Temperatur muss über −273.15 °C liegen")
    return r25 * math.exp(b * (1 / (t + 273.15) - 1 / T25))


def ntc_teiler(t, r25, b, r_fix, u_b, ntc_unten=True, bits=12):
    """
    NTC unten: U_aus = U_B · R_NTC / (R_fix + R_NTC)  (fällt mit steigender Temperatur)
    NTC oben:  U_aus = U_B · R_fix / (R_fix + R_NTC)  (steigt mit steigender Temperatur)
    Empfindlichkeit dU/dT numerisch; ADC-Stufen pro Kelvin = |dU/dT| / (U_B / 2^bits) (ratiometrisch, U_ref = U_B).
    """
    _positiv(R_fix=r_fix, U_B=u_b)

    def u(temp):
        r = ntc_widerstand(temp, r25, b)
        return u_b * (r if ntc_unten else r_fix) / (r_fix + r)

    r = ntc_widerstand(t, r25, b)
    steigung = (u(t + 0.05) - u(t - 0.05)) / 0.1
    lsb = u_b / 2 ** bits
    i = u_b / (r_fix + r)
    return {"r_ntc": r, "u_aus": u(t), "steigung": steigung, "stufen_pro_k": abs(steigung) / lsb,
            "aufloesung_k": lsb / abs(steigung) if steigung else math.inf, "i": i, "p_ntc": i * i * r}


def ntc_kurve(r25, b, r_fix, u_b, ntc_unten=True, t_min=-20.0, t_max=120.0, punkte=71):
    """U_aus über der Temperatur (t 0 … 1 = t_min … t_max) für das Diagramm."""
    kurve = []
    for k in range(punkte):
        t = t_min + (t_max - t_min) * k / (punkte - 1)
        kurve.append((k / (punkte - 1), ntc_teiler(t, r25, b, r_fix, u_b, ntc_unten)["u_aus"]))
    return kurve


def ntc_linear_r(r25, b, t1, t2):
    """
    Festwiderstand für die beste Linearität zwischen t1 und t2 (Wendepunkt in die Mitte legen):
      R_fix = (R1·R2 + R2·R3 − 2·R1·R3) / (R1 + R3 − 2·R2)    R1 = R(t1), R2 = R((t1 + t2)/2), R3 = R(t2)
    """
    if t2 <= t1:
        raise ValueError("t2 muss grösser als t1 sein")
    r1, r2, r3 = (ntc_widerstand(t, r25, b) for t in (t1, (t1 + t2) / 2, t2))
    nenner = r1 + r3 - 2 * r2
    if nenner <= 0:
        raise ValueError("Für diesen Bereich gibt es keinen sinnvollen Linearisierungswiderstand")
    return (r1 * r2 + r2 * r3 - 2 * r1 * r3) / nenner


# =============================================================================
# DMS-BRÜCKE + INSTRUMENTENVERSTÄRKER
# =============================================================================
def bruecke_dms(art, u_e, dehnung, k=2.0):
    """
    Relative Widerstandsänderung x = ΔR / R = k · ε  (ε in m/m, z.B. 1000 µm/m = 1e-3)
      Viertelbrücke: U_d = U_e · x / (4 + 2x)   - leicht nichtlinear
      Halbbrücke:    U_d = U_e · x / 2          - 2 aktive DMS mit +ε und −ε (Biegebalken)
      Vollbrücke:    U_d = U_e · x              - 4 aktive DMS
    Die Brückenmitte liegt bei U_e / 2 (Gleichtaktspannung für den Verstärker).
    """
    _positiv(U_e=u_e, k=k)
    x = k * dehnung
    if art == "Viertelbrücke":
        u_d = u_e * x / (4 + 2 * x)
    elif art == "Halbbrücke":
        u_d = u_e * x / 2
    elif art == "Vollbrücke":
        u_d = u_e * x
    else:
        raise ValueError(f"Unbekannte Brücke: {art}")
    linear = u_e * x / 4 * {"Viertelbrücke": 1, "Halbbrücke": 2, "Vollbrücke": 4}[art]
    return {"x": x, "u_d": u_d, "mv_v": u_d / u_e * 1e3, "u_cm": u_e / 2,
            "nichtlinear": (u_d - linear) / linear * 100 if linear else 0.0}


def inamp_verstaerkung(r_g=None, g=None, r_intern=50e3):
    """G = 1 + R_intern / R_G  bzw.  R_G = R_intern / (G − 1)."""
    if r_g is not None:
        _positiv(R_G=r_g)
        return 1 + r_intern / r_g
    if g is None or g <= 1:
        raise ValueError("Verstärkung G muss grösser als 1 sein")
    return r_intern / (g - 1)


def dms_kette(art, u_e, dehnung, k, g, u_ref=0.0, u_b=5.0, bits=16, u_adc=None):
    """
    Brücke -> Instrumentenverstärker (Verstärkung g, Referenz u_ref) -> ADC.
    Ausgang bei Rail-to-Rail-Ausgang zwischen ca. 0.1 V und U_B − 0.1 V (vereinfacht).
    """
    b = bruecke_dms(art, u_e, dehnung, k)
    u_aus = u_ref + g * b["u_d"]
    grenze = (0.1, u_b - 0.1)
    begrenzt = not grenze[0] <= u_aus <= grenze[1]
    u_adc = u_adc or u_b
    lsb = u_adc / 2 ** bits
    return {**b, "u_aus": min(max(u_aus, grenze[0]), grenze[1]), "u_aus_ideal": u_aus, "begrenzt": begrenzt,
            "lsb": lsb, "lsb_eingang": lsb / g, "dehnung_pro_lsb": lsb / g / (u_e * k / 4 *
                                                                           {"Viertelbrücke": 1, "Halbbrücke": 2,
                                                                            "Vollbrücke": 4}[art])}
