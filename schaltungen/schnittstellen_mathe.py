# =============================================================================
# schaltungen/schnittstellen_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für SCHNITTSTELLEN- und LEISTUNGSSCHALTUNGEN - KEIN tkinter. Testbar, z.B.:
#
#   python -c "from schaltungen.schnittstellen_mathe import *; print(optokoppler(5, 1.2, 330, 0.5, 3.3, 4.7e3))"
#
#   pegel_teiler()        5 V -> 3.3 V mit Spannungsteiler: Pegel und Anstiegszeit
#   pegel_mosfet()        bidirektionaler Pegelwandler mit N-MOSFET (BSS138-Prinzip): Zustände, Anstiegszeiten
#   optokoppler()         LED-Strom, Kollektorstrom über CTR, Sättigung, Ausgangspegel
#   optokoppler_auslegen() R_V und grösster Pull-up für sichere Sättigung (mit CTR-Alterung)
#   h_bruecke()           Zustand der vier Schalter: Strompfad, Motorstrom, Verluste, Brückenkurzschluss
#   gate_ladung()         MOSFET einschalten: u_GS mit Miller-Plateau und u_DS über der Zeit, Schaltzeiten
#   bootstrap()           Bootstrap-Kondensator für einen High-Side-Treiber
#   adc_abtastung()       Abtastkondensator laden: Restfehler in LSB, ohne/mit externem C (Ladungsteilung)
#
# WER RUFT DAS AUF?  schaltungen/grafiken_schnittstellen.py, schaltungen/rechner.py
# =============================================================================

import math

from schaltungen.filter_mathe import _expm2                           # -> schaltungen/filter_mathe.py (e^A, 2×2)

U_DIODE = 0.6           # V, Body-Diode des MOSFET (Pegelwandler)


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


# =============================================================================
# PEGELWANDLER
# =============================================================================
def pegel_teiler(u_hoch, r1, r2, c_ein=10e-12):
    """U_aus = U · R2 / (R1 + R2);  Anstieg t_r (10 … 90 %) = 2.2 · (R1 ∥ R2) · C_ein;  f_max ≈ 0.1 / t_r."""
    _positiv(U=u_hoch, R1=r1, R2=r2, C=c_ein)
    r_par = r1 * r2 / (r1 + r2)
    t_r = 2.2 * r_par * c_ein
    return {"u_aus": u_hoch * r2 / (r1 + r2), "t_r": t_r, "f_max": 0.1 / t_r, "i": u_hoch / (r1 + r2),
            "r_par": r_par}


def pegel_mosfet(zustand, u_a, u_b, r_a, r_b, c_bus, u_th=1.5, r_on=5.0):
    """
    N-MOSFET zwischen Seite A (niedrige Spannung U_A, Source) und Seite B (hohe Spannung U_B, Drain),
    Gate fest an U_A, auf beiden Seiten ein Pull-up.
      beide frei:    U_GS = 0 -> MOSFET sperrt, A = U_A, B = U_B (jede Seite über ihren Pull-up)
      A zieht LOW:   U_GS = U_A > U_th -> MOSFET leitet, B wird mit nach unten gezogen
      B zieht LOW:   Body-Diode zieht A auf ≈ 0.6 V, dann U_GS > U_th -> Kanal leitet, A ≈ 0 V
    Anstieg (beim Loslassen) je Seite über den eigenen Pull-up: t_r = 2.2 · R · C.
    """
    _positiv(U_A=u_a, U_B=u_b, R_A=r_a, R_B=r_b, C=c_bus)
    if u_b < u_a:
        raise ValueError("Seite B muss die höhere Spannung haben (U_B ≥ U_A)")
    reserve = u_a - u_th
    if zustand == "beide frei":
        a, b, leitet = u_a, u_b, False
    elif zustand == "A zieht LOW":
        a = 0.0
        leitet = reserve > 0
        i = u_b / (r_b + r_on)
        b = i * r_on if leitet else u_b
    elif zustand == "B zieht LOW":
        b = 0.0
        leitet = reserve > 0
        a = u_a * r_on / (r_a + r_on) if leitet else U_DIODE
    else:
        raise ValueError(f"Unbekannter Zustand: {zustand}")
    return {"a": a, "b": b, "leitet": leitet, "reserve": reserve, "t_r_a": 2.2 * r_a * c_bus,
            "t_r_b": 2.2 * r_b * c_bus, "f_max": 0.1 / (2.2 * max(r_a, r_b) * c_bus)}


# =============================================================================
# OPTOKOPPLER
# =============================================================================
def optokoppler(u_e, u_f, r_v, ctr, u_b, r_l, u_cesat=0.3, aktiv=True):
    """
    Eingang:  I_F = (U_e − U_F) / R_V
    Ausgang:  der Fototransistor kann höchstens I_C = CTR · I_F liefern.
              Der Pull-up verlangt für LOW: I_C,nötig = (U_B − U_CE,sat) / R_L
              Sättigung, wenn CTR · I_F ≥ I_C,nötig  ->  U_aus = U_CE,sat, sonst U_aus = U_B − CTR · I_F · R_L
    """
    _positiv(R_V=r_v, CTR=ctr, U_B=u_b, R_L=r_l)
    i_f = max(0.0, (u_e - u_f) / r_v) if aktiv else 0.0
    i_c_max = ctr * i_f
    i_noetig = (u_b - u_cesat) / r_l
    gesaettigt = i_c_max >= i_noetig and aktiv and i_f > 0
    if gesaettigt:
        u_aus, i_c = u_cesat, i_noetig
    else:
        i_c = i_c_max
        u_aus = u_b - i_c * r_l
    return {"i_f": i_f, "i_c_max": i_c_max, "i_c": i_c, "i_noetig": i_noetig, "gesaettigt": gesaettigt,
            "u_aus": u_aus, "reserve": i_c_max / i_noetig if i_noetig > 0 else math.inf,
            "p_led": i_f * u_f, "p_rv": i_f ** 2 * r_v}


def optokoppler_auslegen(u_e, u_f, i_f, ctr_min, u_b, u_cesat=0.3, alterung=0.5):
    """
    R_V = (U_e − U_F) / I_F.   Mit Alterung (CTR sinkt über die Jahre, z.B. auf 50 %):
    R_L,min = (U_B − U_CE,sat) / (CTR_min · Alterung · I_F)  - kleinere R_L sättigen nicht sicher.
    """
    _positiv(I_F=i_f, CTR=ctr_min, U_B=u_b, Alterung=alterung)
    if u_e <= u_f:
        raise ValueError("Die Eingangsspannung muss grösser als die LED-Flussspannung sein")
    ctr_eff = ctr_min * alterung
    return {"r_v": (u_e - u_f) / i_f, "p_rv": i_f ** 2 * (u_e - u_f) / i_f, "ctr_eff": ctr_eff,
            "i_c": ctr_eff * i_f, "r_l_min": (u_b - u_cesat) / (ctr_eff * i_f)}


# =============================================================================
# H-BRÜCKE
# =============================================================================
H_ZUSTAENDE = ["vorwärts", "rückwärts", "bremsen", "Freilauf", "⚠ Kurzschluss"]
# eingeschaltete Schalter: S1 links oben, S2 links unten, S3 rechts oben, S4 rechts unten
H_SCHALTER = {"vorwärts": {"S1", "S4"}, "rückwärts": {"S3", "S2"}, "bremsen": {"S2", "S4"}, "Freilauf": set(),
              "⚠ Kurzschluss": {"S1", "S2", "S4"}}


def h_bruecke(zustand, u_b, r_motor, r_ds=0.02, tastgrad=1.0, u_emk=0.0):
    """
    Motor als Widerstand R_M mit Gegenspannung U_EMK (dreht er, erzeugt er Spannung).
      vorwärts / rückwärts: I = ±(D·U_B − U_EMK) / (R_M + 2·R_DS) - Mittelwert bei PWM mit Tastgrad D
      bremsen: beide unteren Schalter ein -> Motor kurzgeschlossen: I = −U_EMK / (R_M + 2·R_DS)
      Freilauf: alle aus -> nur die Body-Dioden leiten (Strom klingt ab), hier I ≈ 0 angenommen
      Kurzschluss: S1 und S2 gleichzeitig -> I = U_B / (2·R_DS) - zerstört die Schalter
    """
    _positiv(U_B=u_b, R_M=r_motor, R_DS=r_ds)
    if zustand not in H_ZUSTAENDE:
        raise ValueError(f"Unbekannter Zustand: {zustand}")
    if not 0 <= tastgrad <= 1:
        raise ValueError("Tastgrad 0 … 1")
    r_kreis = r_motor + 2 * r_ds
    kurzschluss = 0.0
    if zustand == "vorwärts":
        i = (tastgrad * u_b - u_emk) / r_kreis
    elif zustand == "rückwärts":
        i = -(tastgrad * u_b - u_emk) / r_kreis
    elif zustand == "bremsen":
        i = -u_emk / r_kreis
    elif zustand == "Freilauf":
        i = 0.0
    else:
        i = (u_b - u_emk) / r_kreis
        kurzschluss = u_b / (2 * r_ds)
    p_schalter = i * i * 2 * r_ds * (tastgrad if zustand in ("vorwärts", "rückwärts") else 1)
    return {"i_motor": i, "u_motor": i * r_motor + (u_emk if zustand != "Freilauf" else 0.0),
            "p_schalter": p_schalter + kurzschluss ** 2 * 2 * r_ds, "i_kurzschluss": kurzschluss,
            "an": H_SCHALTER[zustand], "p_motor": i * i * r_motor}


def h_verluste(u_b, i, r_ds, f_pwm, t_sw, tastgrad=1.0):
    """
    Leitverluste: zwei Schalter leiten -> P_L = I² · 2 · R_DS (bei PWM anteilig + Freilauf über Diode/Synchron)
    Schaltverluste (grob): P_S ≈ U_B · I · t_sw · f_PWM  (je Ein- und Ausschalten ½ · U · I · t_sw)
    """
    _positiv(U_B=u_b, R_DS=r_ds)
    p_l = i * i * 2 * r_ds
    p_s = u_b * abs(i) * t_sw * f_pwm
    return {"p_leit": p_l, "p_schalt": p_s, "p_gesamt": p_l + p_s, "u_mittel": tastgrad * u_b}


# =============================================================================
# MOSFET GATE-TREIBER
# =============================================================================
def gate_ladung(u_dr, r_g, q_gs, q_gd, q_g, u_pl, u_ds=24.0, u_q=10.0, punkte=240):
    """
    MOSFET einschalten mit Treiberspannung U_Tr über R_G (Gate-Ladungskurve aus dem Datenblatt):
      1) Gate lädt bis zum Plateau U_pl:      C1 = Q_gs / U_pl,  τ1 = R_G · C1
      2) Miller-Plateau: U_GS bleibt bei U_pl, U_DS fällt; Dauer  t2 = Q_gd · R_G / (U_Tr − U_pl)
      3) Rest bis U_Tr:                       C3 = (Q_g − Q_gs − Q_gd) / (U_Q − U_pl)  (Q_g gilt bei U_Q, meist 10 V)
    Rückgabe: Kurven u_GS und u_DS über t (0 … 1 = 0 … Dauer), t1, t2, t_gesamt, Gate-Spitzenstrom
    """
    _positiv(U_Tr=u_dr, R_G=r_g, Q_gs=q_gs, Q_gd=q_gd, Q_g=q_g, U_pl=u_pl)
    if u_dr <= u_pl:
        raise ValueError(f"Treiberspannung {u_dr:g} V liegt nicht über dem Miller-Plateau ({u_pl:g} V) – "
                         "der MOSFET schaltet nie ganz durch")
    if q_g <= q_gs + q_gd:
        raise ValueError("Q_g muss grösser als Q_gs + Q_gd sein")
    tau1 = r_g * q_gs / u_pl
    t1 = -tau1 * math.log(1 - u_pl / u_dr)
    t2 = q_gd * r_g / (u_dr - u_pl)
    tau3 = r_g * (q_g - q_gs - q_gd) / max(u_q - u_pl, 0.1)
    t3 = 3 * tau3
    gesamt = t1 + t2 + t3
    dauer = gesamt * 1.15
    u_gs, u_dsk = [], []
    for k in range(punkte + 1):
        t = dauer * k / punkte
        if t < t1:
            g, d = u_dr * (1 - math.exp(-t / tau1)), u_ds
        elif t < t1 + t2:
            g, d = u_pl, u_ds * (1 - (t - t1) / t2)
        else:
            g, d = u_dr - (u_dr - u_pl) * math.exp(-(t - t1 - t2) / tau3), 0.0
        u_gs.append((k / punkte, g))
        u_dsk.append((k / punkte, d))
    return {"u_gs": u_gs, "u_ds": u_dsk, "t1": t1, "t2": t2, "t3": t3, "gesamt": gesamt, "dauer": dauer,
            "i_spitze": u_dr / r_g, "i_plateau": (u_dr - u_pl) / r_g}


def bootstrap(q_g, u_dd, i_leck=10e-6, t_ein_max=1e-3, delta_u=0.5, u_diode=0.6):
    """
    Bootstrap-Kondensator (High-Side-Treiber): Er liefert die Gate-Ladung und den Ruhestrom, solange der High-Side-
    Schalter eingeschaltet ist.  Q = Q_g + I_leck · t_ein,max;  C ≥ 2 · Q / ΔU  (Faktor 2 Reserve).
    Spannung am Kondensator ≈ U_DD − U_Diode.
    """
    _positiv(Q_g=q_g, U_DD=u_dd, ΔU=delta_u)
    q = q_g + i_leck * t_ein_max
    return {"q": q, "c_min": q / delta_u, "c_empf": 2 * q / delta_u, "u_boot": u_dd - u_diode}


# =============================================================================
# ADC-EINGANG: ABTASTKONDENSATOR
# =============================================================================
def adc_abtastung(u, r_ext, c_ext, r_sw, c_s, t_s, bits, u_ref, u_vorher=0.0, punkte=200):
    """
    Während der Abtastzeit t_s wird der Abtastkondensator C_S über R_sw (Schalter) an den Pin gelegt.
      ohne C_ext (c_ext = 0): C_S lädt über R_ext + R_sw:  Fehler = (U − U_vorher) · e^(−t_s / τ)
      mit C_ext: zuerst Ladungsteilung (C_ext gibt Ladung an C_S ab), dann lädt R_ext langsam nach.
    Gelöst exakt mit der Übergangsmatrix (zwei Kondensatoren). Fehler in LSB = (U − u_CS) / (U_ref / 2^N).
    Faustregeln:  R_ext + R_sw ≤ t_s / (C_S · ln(2^(N+1)))   (ohne C_ext, Fehler < ½ LSB)
                  C_ext ≥ (2^(N+1) − 1) · C_S                 (Ladungsteilung < ½ LSB)
    """
    _positiv(R_sw=r_sw, C_S=c_s, t_s=t_s, U_ref=u_ref)
    if r_ext < 0 or c_ext < 0:
        raise ValueError("R_ext und C_ext dürfen nicht negativ sein")
    lsb = u_ref / 2 ** bits
    kurve_s, kurve_p = [], []
    if c_ext <= 0:
        tau = (r_ext + r_sw) * c_s
        for k in range(punkte + 1):
            t = t_s * k / punkte
            v2 = u + (u_vorher - u) * math.exp(-t / tau)
            kurve_s.append((k / punkte, v2))
            kurve_p.append((k / punkte, v2 + (u - v2) * r_sw / (r_ext + r_sw)))     # Spannung am Pin
        v_ende = kurve_s[-1][1]
    else:
        r_e = max(r_ext, 1e-3)
        a = [[-(1 / r_e + 1 / r_sw) / c_ext, 1 / (r_sw * c_ext)], [1 / (r_sw * c_s), -1 / (r_sw * c_s)]]
        dt = t_s / punkte
        phi = _expm2([[x * dt for x in zeile] for zeile in a])
        v1, v2 = u, u_vorher                                    # C_ext ist geladen, C_S hat den alten Wert
        for k in range(punkte + 1):
            kurve_s.append((k / punkte, v2))
            kurve_p.append((k / punkte, v1))
            d1, d2 = v1 - u, v2 - u
            v1 = u + phi[0][0] * d1 + phi[0][1] * d2
            v2 = u + phi[1][0] * d1 + phi[1][1] * d2
        v_ende = kurve_s[-1][1]
    fehler_lsb = (u - v_ende) / lsb
    ln = math.log(2 ** (bits + 1))
    return {"kurve_s": kurve_s, "kurve_pin": kurve_p, "fehler_lsb": fehler_lsb, "lsb": lsb,
            "r_max": max(0.0, t_s / (c_s * ln) - r_sw), "c_ext_min": (2 ** (bits + 1) - 1) * c_s,
            "teilung_lsb": abs(u - u_vorher) * c_s / (c_s + c_ext) / lsb if c_ext > 0 else None,
            "f_g": 1 / (2 * math.pi * r_ext * c_ext) if r_ext > 0 and c_ext > 0 else None,
            "fehler_kurve": [(t, min((u - v) / lsb, 1e9)) for t, v in kurve_s]}
