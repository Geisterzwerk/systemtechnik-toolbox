# =============================================================================
# schaltungen/netzwerk_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für Widerstandsnetzwerke - KEIN tkinter hier drin.
# Einzeln testbar, z.B.:
#
#   python -c "from schaltungen.netzwerk_mathe import *; print(spannungsteiler(12, 10e3, 10e3, 10e3))"
#
#   parallel()          Parallelschaltung beliebig vieler Widerstände
#   spannungsteiler()   unbelastet und belastet, Querstromverhältnis
#   stromteiler()       Ströme in parallelen Zweigen
#   pull_widerstand()   Pull-up / Pull-down: Pegel am Eingang, Strom, Anstiegszeit
#   poti_teiler()       Potentiometer als Teiler, mit und ohne Last
#   bruecke()           Wheatstone-Brücke: Diagonalspannung
#
# Alle Werte in Basiseinheiten (V, A, Ω, F, s). Ungültige Eingaben -> ValueError
# mit einer Meldung, die man direkt anzeigen kann.
#
# WER RUFT DAS AUF?  schaltungen/grafiken.py (interaktive Schaltpläne),
#                    schaltungen/rechner.py (Formel-Rechner), messtechnik/rechner.py (Brücke)
# =============================================================================

import math

LOG_9 = math.log(9)                 # Anstiegszeit 10 % -> 90 % einer RC-Ladung = τ · ln 9 ≈ 2.2 τ
HIGH_ANTEIL, LOW_ANTEIL = 0.7, 0.3  # CMOS-Schwellen: HIGH sicher ab 0.7 · U_B, LOW sicher bis 0.3 · U_B


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


def parallel(*widerstaende):
    """1 / R = 1/R1 + 1/R2 + ...   (alle > 0)"""
    _positiv(**{f"R{i + 1}": r for i, r in enumerate(widerstaende)})
    return 1 / sum(1 / r for r in widerstaende)


def spannungsteiler(u_e, r1, r2, r_last=None):
    """
    R1 oben, R2 unten, Last R_L parallel zu R2 (None = unbelastet).
      Ua,0  = Ue · R2 / (R1 + R2)                       unbelastet
      Ua    = Ue · (R2 || RL) / (R1 + R2 || RL)         belastet
      q     = I_2 / I_L  (Querstromverhältnis; Faustregel: q ≥ 10 -> Ua bleibt stabil)
    """
    _positiv(R1=r1, R2=r2)
    ua0 = u_e * r2 / (r1 + r2)
    if r_last is None:
        r_unten = r2
    else:
        _positiv(RL=r_last)
        r_unten = parallel(r2, r_last)
    ua = u_e * r_unten / (r1 + r_unten)
    i1 = (u_e - ua) / r1
    i2 = ua / r2
    il = 0.0 if r_last is None else ua / r_last
    return {"ua": ua, "ua0": ua0, "abweichung": (ua / ua0 - 1) if ua0 else 0.0,
            "i1": i1, "i2": i2, "il": il, "q": (i2 / il) if il else None,
            "p1": i1 * i1 * r1, "p2": i2 * i2 * r2, "r_unten": r_unten}


def stromteiler(i_gesamt, *widerstaende):
    """
    Parallele Zweige an einer Stromquelle:  U = I · R_ges,   I_k = U / R_k
    Bei zwei Zweigen:  I1 = I · R2 / (R1 + R2)  (der KLEINERE Widerstand bekommt MEHR Strom)
    """
    r_ges = parallel(*widerstaende)
    u = i_gesamt * r_ges
    return {"r_ges": r_ges, "u": u, "stroeme": [u / r for r in widerstaende],
            "leistungen": [u * u / r for r in widerstaende]}


def pull_widerstand(art, u_b, r, gedrueckt, i_leck=0.0, c=0.0):
    """
    art "pullup":   R von +U_B zum Eingang, Taster vom Eingang nach GND
    art "pulldown": R vom Eingang nach GND, Taster von +U_B zum Eingang
    i_leck  Leckstrom des Eingangs (Datenblatt, Betrag) -> Spannungsfall an R
    c       Kapazität von Eingang + Leitung -> Anstiegs-/Abfallzeit über R

    Rückgabe: u_pin, pegel ("HIGH" / "LOW" / "unsicher"), i_r (Strom durch R), p_r,
              t_flanke (10 → 90 %, über R umgeladen; der Taster selbst schaltet schnell)
    """
    if art not in ("pullup", "pulldown"):
        raise ValueError(f"Unbekannte Art: {art}")
    _positiv(U_B=u_b, R=r)
    if i_leck < 0 or c < 0:
        raise ValueError("Leckstrom und Kapazität dürfen nicht negativ sein")
    if gedrueckt:
        u_pin = 0.0 if art == "pullup" else u_b                  # Taster überbrückt: harter Pegel
        i_r = u_b / r
    else:
        abfall = i_leck * r                                       # Leckstrom erzeugt Spannung an R
        u_pin = max(0.0, u_b - abfall) if art == "pullup" else min(u_b, abfall)
        i_r = abs(u_b - u_pin) / r if art == "pullup" else u_pin / r
    if u_pin >= HIGH_ANTEIL * u_b:
        pegel = "HIGH"
    elif u_pin <= LOW_ANTEIL * u_b:
        pegel = "LOW"
    else:
        pegel = "unsicher"
    return {"u_pin": u_pin, "pegel": pegel, "i_r": i_r, "p_r": i_r * i_r * r,
            "t_flanke": r * c * LOG_9, "u_high": HIGH_ANTEIL * u_b, "u_low": LOW_ANTEIL * u_b}


def poti_teiler(u_e, r_poti, anteil, r_last=None):
    """
    Schleifer bei 'anteil' (0 = unten/GND, 1 = oben/Ue).
      unbelastet:  Ua = anteil · Ue                  (linear)
      belastet:    R_unten = anteil · R_P  parallel zu R_L -> Ua sinkt, Kennlinie "hängt durch"
    """
    _positiv(R_Poti=r_poti)
    if not 0 <= anteil <= 1:
        raise ValueError("Schleiferstellung zwischen 0 und 100 %")
    r_unten, r_oben = anteil * r_poti, (1 - anteil) * r_poti
    if r_last is None or r_unten == 0:
        ua = anteil * u_e
    else:
        _positiv(RL=r_last)
        r_par = parallel(r_unten, r_last)
        ua = u_e * r_par / (r_oben + r_par)
    ua0 = anteil * u_e
    return {"ua": ua, "ua0": ua0, "fehler": ua - ua0, "r_oben": r_oben, "r_unten": r_unten,
            "i_last": 0.0 if r_last is None else ua / r_last}


def poti_kennlinie(r_poti, r_last, punkte=41):
    """Ua/Ue über der Schleiferstellung (für die Grafik): Liste von (anteil, verhältnis)."""
    return [(k / (punkte - 1), poti_teiler(1.0, r_poti, k / (punkte - 1), r_last)["ua"]) for k in range(punkte)]


def bruecke(u_e, r1, r2, r3, r4):
    """
    Wheatstone-Brücke: linker Zweig R1 (oben) / R2 (unten), rechter Zweig R3 (oben) / R4 (unten).
      U_links  = Ue · R2 / (R1 + R2)       U_rechts = Ue · R4 / (R3 + R4)
      U_d      = U_links − U_rechts        abgeglichen (U_d = 0) wenn R1 / R2 = R3 / R4
    """
    _positiv(R1=r1, R2=r2, R3=r3, R4=r4)
    u_links = u_e * r2 / (r1 + r2)
    u_rechts = u_e * r4 / (r3 + r4)
    return {"u_links": u_links, "u_rechts": u_rechts, "u_d": u_links - u_rechts,
            "r4_abgleich": r3 * r2 / r1, "i_links": u_e / (r1 + r2), "i_rechts": u_e / (r3 + r4)}
