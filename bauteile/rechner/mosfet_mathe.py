# =============================================================================
# bauteile/rechner/mosfet_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für den MOSFET als Schalter - KEIN tkinter hier drin.
# Einzeln testbar, z.B. in der Konsole:
#
#   python -c "from bauteile.rechner.mosfet_mathe import *; print(schalter('N', 12, 24, 10, 2, 0.05, 10))"
#
#   schalter()       N-Kanal (Low-Side) / P-Kanal (High-Side): sperrt, linear, voll durchgeschaltet?
#   rds_on()         R_DS(on) bei einer anderen Gate-Spannung als im Datenblatt
#   gate_umladen()   Gate-Strom und Schaltzeit aus Gate-Ladung Q_g
#
# VEREINFACHTES MODELL (reicht zum Verstehen, ersetzt kein Datenblatt):
#   U_GS ≤ U_th             -> sperrt, kein Strom
#   voll eingeschaltet      -> Widerstand R_DS(on); er wird kleiner, je weiter U_GS über U_th liegt:
#                              R_on(U_GS) = R_DS(on),spec · (U_spec − U_th) / (U_GS − U_th)
#   kurz über U_th          -> der Kanal lässt nur I = K · (U_GS − U_th)² durch ("linear"/Verstärkerbereich)
#                              -> der MOSFET wird heiss (P = U_DS · I)
#   K (Steilheit) ist hier fest - echte Werte stehen als Kennlinienfeld im Datenblatt.
#
# WER RUFT DAS AUF?  bauteile/grafiken/schalter_simulator.py (MosfetSchalter)
# =============================================================================

K_STEILHEIT = 1.0          # A/V², typische Grössenordnung für kleine Leistungs-MOSFETs
U_GS_MAX = 20.0            # V, übliche Grenze ±20 V (viele Logic-Level-Typen: nur ±12 V!)


def rds_on(u_gs, u_th, rds_spec, u_spec):
    """R_DS(on) bei der tatsächlichen Gate-Spannung (Näherung, siehe Kopf). None = sperrt."""
    if u_gs <= u_th:
        return None
    return rds_spec * (u_spec - u_th) / (u_gs - u_th)


def schalter(kanal, u_b, r_last, u_gate, u_th, rds_spec, u_spec, k=K_STEILHEIT):
    """
    kanal "N"  LOW-SIDE:   +U_B ── Last ── D   S ── GND,  U_GS = U_Gate
    kanal "P"  HIGH-SIDE:  +U_B ── S   D ── Last ── GND,  U_SG = U_B − U_Gate
               -> zum AUSschalten muss das Gate auf U_B, zum Einschalten nach unten gezogen werden

    u_th      Schwellspannung |U_GS(th)| (Betrag, auch beim P-Kanal positiv eingeben)
    rds_spec  R_DS(on) aus dem Datenblatt, gemessen bei |U_GS| = u_spec

    Rückgabe: dict
      zustand  "sperrt" | "linear" | "voll"
      u_gs     wirksame Steuerspannung (Betrag: U_GS beim N-, U_SG beim P-Kanal)
      i, u_ds, r_on, p_t, u_last, i_max (Strom bei idealem Schalter)
      unter_spec  True, wenn |U_GS| kleiner als die Datenblatt-Prüfspannung ist
      zu_hoch     True, wenn |U_GS| die übliche Grenze U_GS,max überschreitet
    """
    if kanal not in ("N", "P"):
        raise ValueError(f"Unbekannter Kanal: {kanal}")
    if min(u_b, r_last, rds_spec, u_spec) <= 0 or u_th <= 0:
        raise ValueError("U_B, R_Last, R_DS(on), U_spec und U_th müssen grösser als 0 sein")
    if u_spec <= u_th:
        raise ValueError("Die Datenblatt-Prüfspannung muss über U_th liegen")
    u_gs = u_gate if kanal == "N" else u_b - u_gate
    i_max = u_b / r_last
    e = {"kanal": kanal, "u_gs": u_gs, "i_max": i_max, "unter_spec": u_gs < u_spec,
         "zu_hoch": abs(u_gs) > U_GS_MAX, "r_on": None}
    if u_gs <= u_th:
        e.update(zustand="sperrt", i=0.0, u_ds=u_b, p_t=0.0, u_last=0.0)
        return e
    r_on = rds_on(u_gs, u_th, rds_spec, u_spec)
    i_kanal = k * (u_gs - u_th) ** 2                         # was der Kanal bei dieser U_GS zulässt
    i_voll = u_b / (r_last + r_on)                           # was Last + R_on zulassen
    if i_kanal < i_voll:
        i, zustand = i_kanal, "linear"
    else:
        i, zustand = i_voll, "voll"
    u_ds = u_b - i * r_last
    e.update(zustand=zustand, i=i, u_ds=u_ds, r_on=r_on, p_t=u_ds * i, u_last=i * r_last)
    return e


def gate_umladen(q_g, u_treiber, r_g):
    """
    Beim Umschalten muss die Gate-Ladung Q_g bewegt werden:
      I_G,spitze ≈ U_Treiber / R_G        t_schalt ≈ Q_g / I_G = Q_g · R_G / U_Treiber  (grobe Näherung)
    """
    if u_treiber <= 0 or r_g <= 0 or q_g <= 0:
        raise ValueError("Q_g, Treiberspannung und R_G müssen grösser als 0 sein")
    i_g = u_treiber / r_g
    return {"i_g": i_g, "t_schalt": q_g / i_g}
