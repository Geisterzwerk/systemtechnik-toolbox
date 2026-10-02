# =============================================================================
# bauteile/rechner/transistor_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für den Bipolartransistor - KEIN tkinter hier drin.
# Dadurch einzeln testbar, z.B. in der Konsole:
#
#   python -c "from bauteile.rechner.transistor_mathe import *; print(schalter_dimensionieren(12, 5, 100, r_last=120))"
#
#   schalter_dimensionieren()   Basiswiderstand für NPN/PNP als Schalter
#   arbeitspunkt()              gesperrt / aktiv / gesättigt?
#   verlustleistung()           Durchlass- + Schaltverluste
#
# Vereinfachtes Modell (reicht für Schalteranwendungen und die Prüfung):
#   U_BE ≈ 0.7 V        wenn der Transistor leitet (Si, wie eine Diode)
#   U_CE,sat ≈ 0.2 V    wenn er voll durchgeschaltet (gesättigt) ist
#   I_C = B · I_B       NUR im aktiven Bereich (B = Stromverstärkung, auch β / hFE)
#
# WER RUFT DAS AUF?
#   bauteile/rechner/transistor_rechner.py       (Zusatz-Rechner Bipolartransistor)
#   bauteile/rechner/relais_mathe.py             (Relais mit Transistor ansteuern)
# =============================================================================

from bauteile.rechner import normreihen      # -> rechner/normreihen.py

U_BE = 0.7            # V, Basis-Emitter-Spannung (Si)
U_CE_SAT = 0.2        # V, Kollektor-Emitter-Spannung in Sättigung
UE_STANDARD = 3       # Übersteuerungsfaktor, wenn nichts eingegeben wird


def schalter_dimensionieren(u_b, u_steuer, b_min, ue=UE_STANDARD, r_last=None, i_last=None,
                            typ="NPN", u_be=U_BE, u_ce_sat=U_CE_SAT, reihe="E12"):
    """
    Basiswiderstand für einen Transistor-Schalter.

    u_b       Versorgungsspannung der Last in V
    u_steuer  NPN: HIGH-Pegel der Steuerung (z.B. 3.3 V vom µC)
              PNP: LOW-Pegel der Steuerung (meist 0 V) - dann leitet der PNP
    b_min     kleinste Stromverstärkung aus dem Datenblatt
    ue        Übersteuerungsfaktor ü (2 ... 5)
    r_last    Lastwiderstand in Ω   ODER
    i_last    Laststrom in A (z.B. Relais-Nennstrom)

    Rechenweg:
      I_C  = (U_B − U_CE,sat) / R_Last                 Strom durch die Last
      I_B  = ü · I_C / B_min                           Basisstrom mit Übersteuerung
      U_RB = U_Steuer − U_BE              (NPN)        Spannung am Basiswiderstand
      U_RB = U_B − U_EB − U_Steuer        (PNP)        (Emitter liegt an +U_B)
      R_B  = U_RB / I_B   -> Normwert ABRUNDEN (mehr Basisstrom = sicherer gesättigt)

    Rückgabe: dict mit allen Zwischenwerten (Einheiten: V, A, Ω, W)
    """
    if b_min is None or b_min <= 0:
        raise ValueError("B min muss grösser als 0 sein")
    if ue <= 0:
        raise ValueError("Übersteuerungsfaktor ü muss grösser als 0 sein")

    # ---- 1) Kollektorstrom ----
    if i_last is not None:
        i_c = i_last
    elif r_last is not None:
        if r_last <= 0:
            raise ValueError("Lastwiderstand muss grösser als 0 sein")
        i_c = (u_b - u_ce_sat) / r_last
    else:
        raise ValueError("Lastwiderstand ODER Laststrom angeben")
    if i_c <= 0:
        raise ValueError("Versorgungsspannung zu klein - es fliesst kein Laststrom")

    # ---- 2) Spannung am Basiswiderstand ----
    if typ == "NPN":
        u_rb = u_steuer - u_be
    else:                                   # PNP: Basis wird nach unten gezogen
        u_rb = u_b - u_be - u_steuer
    if u_rb <= 0:
        if typ == "NPN":
            raise ValueError(f"Steuerspannung muss grösser als U_BE = {u_be:g} V sein")
        raise ValueError("LOW-Pegel zu hoch - die Basis muss mind. 0.7 V unter U_B gezogen werden")

    # ---- 3) Basisstrom und Basiswiderstand ----
    i_b = ue * i_c / b_min
    r_b = u_rb / i_b
    r_b_norm = normreihen.naechste_werte(r_b, reihe)[0]      # [0] = nächst KLEINERER Normwert

    # ---- 4) Was ergibt sich mit dem Normwert wirklich? ----
    i_b_echt = u_rb / r_b_norm
    ue_echt = i_b_echt * b_min / i_c
    return {
        "i_c": i_c,
        "u_rb": u_rb,
        "i_b": i_b,
        "r_b": r_b,
        "r_b_norm": r_b_norm,
        "i_b_echt": i_b_echt,
        "ue_echt": ue_echt,
        "p_rb": u_rb ** 2 / r_b_norm,                          # Leistung im Basiswiderstand
        "p_t": u_ce_sat * i_c + u_be * i_b_echt,               # Verlust im Transistor (Sättigung)
    }


def arbeitspunkt(u_b, r_last, u_steuer, r_b, b, u_be=U_BE, u_ce_sat=U_CE_SAT):
    """
    In welchem Zustand ist ein NPN-Schalter (Last am Kollektor, Emitter an GND)?

    Rückgabe: dict  zustand = "gesperrt" | "aktiv" | "gesättigt"
      gesperrt  : U_Steuer ≤ U_BE -> kein Strom, Schalter offen
      aktiv     : I_C = B · I_B ist kleiner, als die Last erlauben würde
                  -> Transistor ist nur "halb offen" und wird heiss
      gesättigt : B · I_B wäre grösser, als die Last zulässt
                  -> voll durchgeschaltet, U_CE ≈ U_CE,sat
    """
    if min(u_b, r_last, r_b, b) <= 0:
        raise ValueError("U_B, R_Last, R_B und B müssen grösser als 0 sein")
    i_c_max = (u_b - u_ce_sat) / r_last             # mehr lässt die Last nicht zu
    if u_steuer <= u_be:
        return {"zustand": "gesperrt", "i_b": 0.0, "i_c": 0.0, "i_c_max": i_c_max,
                "u_ce": u_b, "p_t": 0.0, "ue": 0.0}
    i_b = (u_steuer - u_be) / r_b
    i_c = b * i_b
    ue = i_c / i_c_max                              # > 1 = übersteuert (gesättigt)
    if i_c >= i_c_max:
        return {"zustand": "gesättigt", "i_b": i_b, "i_c": i_c_max, "i_c_max": i_c_max,
                "u_ce": u_ce_sat, "p_t": u_ce_sat * i_c_max + u_be * i_b, "ue": ue}
    u_ce = u_b - i_c * r_last
    return {"zustand": "aktiv", "i_b": i_b, "i_c": i_c, "i_c_max": i_c_max,
            "u_ce": u_ce, "p_t": u_ce * i_c + u_be * i_b, "ue": ue}


def verlustleistung(u_ce, i_c, i_b=0.0, u_be=U_BE, tastgrad=1.0, f=None, t_schalt=None, u_sperr=None):
    """
    Verlustleistung im Transistor.

      Durchlassverlust:  P_D = (U_CE · I_C + U_BE · I_B) · D        D = Tastgrad (0 ... 1)
      Schaltverlust:     P_S ≈ ½ · U_sperr · I_C · (t_r + t_f) · f  (Abschätzung, induktive Last)
                         bei ohmscher Last eher 1/6 statt ½ -> Formel liegt auf der sicheren Seite

    Rückgabe: dict  p_durchlass, p_schalt (oder None), p_gesamt
    """
    if not 0 < tastgrad <= 1:
        raise ValueError("Tastgrad muss zwischen 0 und 100 % liegen")
    p_durchlass = (u_ce * i_c + u_be * (i_b or 0.0)) * tastgrad
    p_schalt = None
    if f is not None and t_schalt is not None:
        u = u_sperr if u_sperr is not None else u_ce
        p_schalt = 0.5 * u * i_c * t_schalt * f
    return {"p_durchlass": p_durchlass, "p_schalt": p_schalt,
            "p_gesamt": p_durchlass + (p_schalt or 0.0)}

