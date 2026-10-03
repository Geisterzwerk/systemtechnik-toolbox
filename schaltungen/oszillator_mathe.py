# =============================================================================
# schaltungen/oszillator_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für TIMER, OSZILLATOREN und WATCHDOG - KEIN tkinter. Testbar, z.B.:
#
#   python -c "from schaltungen.oszillator_mathe import *; print(ne555_astabil(1e3, 10e3, 100e-9))"
#
#   ne555_astabil()       f, Tastgrad, t_H, t_L (optional mit Diode parallel zu R2)
#   ne555_astabil_auslegen()  R1, R2 für gewünschte Frequenz und Tastgrad bei gegebenem C
#   ne555_mono()          Impulsdauer t = ln(3) · R · C
#   ne555_kurven()        u_C (zwischen U/3 und 2U/3) und Ausgang über der Zeit
#   multivibrator()       astabiler Multivibrator mit zwei Transistoren: Zeiten, Sättigung, Basis-Sperrspannung
#   multivibrator_kurven() U_CE1, U_CE2 und U_BE2 (negativer Ausschlag!) über der Zeit
#   funktionsgenerator()  Schmitt-Trigger + Integrator: Frequenz, Dreieckamplitude
#   funktions_kurven()    Rechteck und Dreieck über der Zeit
#   watchdog_zeitachse()  Trigger, Zähler und Reset über der Zeit (normal und Fenster-Watchdog)
#
# WER RUFT DAS AUF?  schaltungen/grafiken_oszillator.py, schaltungen/rechner.py
# =============================================================================

import math

LN2, LN3 = math.log(2), math.log(3)
U_BE, U_CE_SAT, U_D = 0.7, 0.2, 0.7


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


# =============================================================================
# NE555
# =============================================================================
def ne555_astabil(r1, r2, c, diode=False):
    """
    C lädt über R1 + R2 von U/3 auf 2U/3 (Ausgang HIGH), entlädt über R2 in Pin 7 (Ausgang LOW).
      t_H = ln2 · (R1 + R2) · C      t_L = ln2 · R2 · C      f = 1.44 / ((R1 + 2·R2) · C)
    Mit Diode parallel zu R2 lädt C nur über R1:  t_H ≈ ln2 · R1 · C  -> Tastgrad auch unter 50 %
    (Diodenspannung vernachlässigt).
    """
    _positiv(R1=r1, R2=r2, C=c)
    t_h = LN2 * (r1 if diode else r1 + r2) * c
    t_l = LN2 * r2 * c
    t = t_h + t_l
    return {"t_h": t_h, "t_l": t_l, "t": t, "f": 1 / t, "tastgrad": t_h / t}


def ne555_astabil_auslegen(f, tastgrad, c):
    """
    Ohne Diode: Tastgrad D > 50 %:  R2 = (1 − D) / (ln2 · f · C),  R1 = (2D − 1) / (ln2 · f · C)
    Für D ≤ 50 % braucht es die Diode parallel zu R2:  R1 = D / (ln2 · f · C), R2 = (1 − D) / (ln2 · f · C)
    """
    _positiv(f=f, C=c)
    if not 0 < tastgrad < 1:
        raise ValueError("Tastgrad zwischen 0 und 1 (0 … 100 %)")
    k = 1 / (LN2 * f * c)
    if tastgrad > 0.5:
        return {"r1": (2 * tastgrad - 1) * k, "r2": (1 - tastgrad) * k, "diode": False}
    return {"r1": tastgrad * k, "r2": (1 - tastgrad) * k, "diode": True}


def ne555_mono(r, c):
    """Ein Triggerimpuls (Pin 2 < U/3) startet: C lädt über R von 0 bis 2U/3 -> t = ln3 · R · C ≈ 1.1 · R · C."""
    _positiv(R=r, C=c)
    return {"t": LN3 * r * c}


def ne555_kurven(art, u_b, r1, r2, c, diode=False, perioden=2.5, punkte=300):
    """
    Kurven [(t 0 … 1, wert)] für u_C, Ausgang und (monostabil) Trigger.
    astabil: Start im eingeschwungenen Zustand bei U/3 (Ladebeginn).
    monostabil: r1 = R, Trigger kurz nach Beginn.
    """
    oben, unten = 2 * u_b / 3, u_b / 3
    u_c, aus, trig = [], [], []
    if art == "astabil":
        e = ne555_astabil(r1, r2, c, diode)
        tau_l, tau_e = (r1 if diode else r1 + r2) * c, r2 * c
        dauer = perioden * e["t"]
        for k in range(punkte + 1):
            t = dauer * k / punkte
            x = t % e["t"]
            if x < e["t_h"]:
                u = u_b - (u_b - unten) * math.exp(-x / tau_l)
                a = u_b
            else:
                u = oben * math.exp(-(x - e["t_h"]) / tau_e)
                a = 0.0
            u_c.append((k / punkte, u))
            aus.append((k / punkte, a))
            trig.append((k / punkte, u))
        return {"u_c": u_c, "aus": aus, "dauer": dauer, **e}
    e = ne555_mono(r1, c)
    start, dauer = 0.1 * e["t"] / 0.7, e["t"] / 0.6
    for k in range(punkte + 1):
        t = dauer * k / punkte
        if t < start:
            u, a = 0.0, 0.0
        elif t < start + e["t"]:
            u, a = u_b * (1 - math.exp(-(t - start) / (r1 * c))), u_b
        else:
            u, a = 0.0, 0.0
        u_c.append((k / punkte, u))
        aus.append((k / punkte, a))
        trig.append((k / punkte, 0.0 if start <= t < start + 0.05 * dauer else u_b))
    return {"u_c": u_c, "aus": aus, "trigger": trig, "dauer": dauer, "start": start / dauer, **e}


# =============================================================================
# ASTABILER MULTIVIBRATOR (zwei Transistoren)
# =============================================================================
def multivibrator(u_b, r_c, r_b1, r_b2, c1, c2, beta=100.0):
    """
    Jeder Transistor sperrt, bis sich der Koppelkondensator über seinen Basiswiderstand umgeladen hat:
      t1 = ln2 · R_B1 · C1      t2 = ln2 · R_B2 · C2      f = 1 / (t1 + t2)
    (genau: ln((2·U_B − 0.7) / (U_B − 0.7)) statt ln2 - bei U_B ≫ 0.7 V praktisch ln2)
    Sättigung: I_B = (U_B − 0.7) / R_B muss ≥ I_C / β = (U_B − 0.2) / (R_C · β) sein  -> R_B ≤ β · R_C
    Beim Umschalten springt die Basis des anderen Transistors auf ≈ −(U_B − 0.7 V): Die B-E-Strecke verträgt
    meist nur 5 … 6 V in Sperrrichtung.
    """
    _positiv(U_B=u_b, R_C=r_c, R_B1=r_b1, R_B2=r_b2, C1=c1, C2=c2, beta=beta)
    if u_b <= U_BE:
        raise ValueError("U_B muss grösser als 0.7 V sein")
    faktor = math.log((2 * u_b - U_BE) / (u_b - U_BE))
    t1, t2 = faktor * r_b1 * c1, faktor * r_b2 * c2
    i_c = (u_b - U_CE_SAT) / r_c
    i_b = (u_b - U_BE) / max(r_b1, r_b2)
    return {"t1": t1, "t2": t2, "t": t1 + t2, "f": 1 / (t1 + t2), "tastgrad": t1 / (t1 + t2), "faktor": faktor,
            "i_c": i_c, "i_b": i_b, "ueberst": i_b * beta / i_c, "gesaettigt": i_b * beta >= i_c,
            "u_be_min": -(u_b - U_BE - U_CE_SAT), "flanke": 2.2 * r_c * max(c1, c2)}


def multivibrator_kurven(u_b, r_c, r_b1, r_b2, c1, c2, perioden=2.5, punkte=400):
    """U_CE1, U_CE2 (mit abgerundeter Anstiegsflanke über R_C·C) und U_BE2 über der Zeit."""
    e = multivibrator(u_b, r_c, r_b1, r_b2, c1, c2)
    dauer = perioden * e["t"]
    ce1, ce2, be2 = [], [], []
    for k in range(punkte + 1):
        t = dauer * k / punkte
        x = t % e["t"]
        if x < e["t1"]:                  # T1 sperrt (C1 lädt über R_B1), T2 leitet
            ce1.append((k / punkte, u_b - (u_b - U_CE_SAT) * math.exp(-x / (r_c * c2))))
            ce2.append((k / punkte, U_CE_SAT))
            be2.append((k / punkte, U_BE))
        else:                            # T2 sperrt: seine Basis startet bei −(U_B − 0.9) und lädt über R_B2 Richtung U_B
            y = x - e["t1"]
            ce1.append((k / punkte, U_CE_SAT))
            ce2.append((k / punkte, u_b - (u_b - U_CE_SAT) * math.exp(-y / (r_c * c1))))
            u = u_b - (u_b - e["u_be_min"]) * math.exp(-y / (r_b2 * c2))
            be2.append((k / punkte, min(u, U_BE)))
    return {"ce1": ce1, "ce2": ce2, "be2": be2, "dauer": dauer, **e}


# =============================================================================
# RECHTECK-/DREIECKGENERATOR (Schmitt-Trigger + Integrator)
# =============================================================================
def funktionsgenerator(r1, r2, r, c, u_sat):
    """
    Nichtinvertierender Schmitt-Trigger (R1 vom Integrator-Ausgang, R2 Mitkopplung) kippt bei
    u_Dreieck = ±U_sat · R1 / R2.  Der Integrator läuft mit der Steigung U_sat / (R · C).
      Dreieck-Amplitude û_D = U_sat · R1 / R2       f = R2 / (4 · R1 · R · C)
    """
    _positiv(R1=r1, R2=r2, R=r, C=c, U_sat=u_sat)
    if r1 >= r2:
        raise ValueError("R1 muss kleiner als R2 sein, sonst erreicht das Dreieck die Schaltschwelle nie")
    u_d = u_sat * r1 / r2
    f = r2 / (4 * r1 * r * c)
    return {"u_d": u_d, "f": f, "t": 1 / f, "steigung": u_sat / (r * c)}


def funktions_kurven(r1, r2, r, c, u_sat, perioden=2.5, punkte=300):
    e = funktionsgenerator(r1, r2, r, c, u_sat)
    dauer = perioden * e["t"]
    recht, drei = [], []
    for k in range(punkte + 1):
        t = dauer * k / punkte
        x = (t / e["t"]) % 1.0
        if x < 0.5:                       # Rechteck +U_sat -> Integrator (invertierend) läuft abwärts
            recht.append((k / punkte, u_sat))
            drei.append((k / punkte, e["u_d"] - 4 * e["u_d"] * x))
        else:
            recht.append((k / punkte, -u_sat))
            drei.append((k / punkte, -e["u_d"] + 4 * e["u_d"] * (x - 0.5)))
    return {"rechteck": recht, "dreieck": drei, "dauer": dauer, **e}


# =============================================================================
# WATCHDOG
# =============================================================================
def watchdog_zeitachse(t_trigger, t_wd, t_haenger, t_reset=0.05, t_start=0.2, toleranz=0.3, fenster=False,
                       t_fenster=0.0, dauer=None, punkte=800):
    """
    Zeitachse eines Watchdogs: Jeder Trigger des Programms setzt den Zähler zurück. Erreicht der Zähler den
    Timeout, gibt der Watchdog einen Reset-Impuls (t_reset); danach startet das Programm neu (Bootzeit t_start,
    der Watchdog zählt dabei schon mit!) und triggert wieder.
      t_haenger: ab hier hängt das Programm (erster Lauf) und triggert nicht mehr
      toleranz:  Streuung des Timeouts laut Datenblatt (0.3 = ±30 %) - gerechnet wird mit dem KÜRZESTEN Timeout
      fenster:   Fenster-Watchdog - ein Trigger früher als t_fenster nach dem letzten ist ebenfalls ein Fehler
    Rückgabe: Kurven Trigger (0/1), Zähler (0 … 1 = kürzester Timeout), Reset (0/1), Ereignisse.
    """
    _positiv(Trigger=t_trigger, Timeout=t_wd, Reset=t_reset)
    if not 0 <= toleranz < 1:
        raise ValueError("Toleranz 0 … 99 %")
    t_wd_min = t_wd * (1 - toleranz)
    dauer = dauer or max(t_haenger + 2.5 * t_wd + t_reset + t_start, 6 * t_trigger)
    dt = dauer / punkte
    lauf_start, erster_lauf, zaehl_start, reset_bis = 0.0, True, 0.0, -1.0
    naechster = t_trigger
    trig, zael, res, ereignisse = [], [], [], []

    def reset_ausloesen(t, grund):
        nonlocal reset_bis, zaehl_start, lauf_start, naechster, erster_lauf
        reset_bis = t + t_reset
        zaehl_start = reset_bis
        lauf_start = reset_bis + t_start
        naechster = lauf_start + t_trigger
        erster_lauf = False
        ereignisse.append((t, grund))

    for k in range(punkte + 1):
        t = k * dt
        trigger = 0
        if t >= reset_bis:
            aktiv = t >= lauf_start and not (erster_lauf and t >= t_haenger)
            if aktiv and t >= naechster:
                trigger = 1
                naechster += t_trigger
                if fenster and t - zaehl_start < t_fenster:
                    reset_ausloesen(t, "Trigger zu früh (Fenster) → Reset")
                else:
                    zaehl_start = t
            if t >= reset_bis and t - zaehl_start >= t_wd_min:
                reset_ausloesen(t, "kein Trigger (Timeout) → Reset")
        im_reset = t < reset_bis
        trig.append((k / punkte, trigger))
        zael.append((k / punkte, 0.0 if im_reset else min(max(t - zaehl_start, 0.0) / t_wd_min, 1.0)))
        res.append((k / punkte, 1 if im_reset else 0))
    sicher = t_trigger < t_wd_min and t_start + t_trigger < t_wd_min and (not fenster or t_trigger > t_fenster)
    return {"trigger": trig, "zaehler": zael, "reset": res, "ereignisse": ereignisse, "dauer": dauer,
            "t_wd_min": t_wd_min, "sicher": sicher, "bootschleife": t_start + t_trigger >= t_wd_min}


# =============================================================================
# VCO (spannungsgesteuerter Oszillator) - Prinzip mit Integrator + Schmitt-Trigger
# =============================================================================
def vco(r1, r2, r, c, u_sat, u_st):
    """
    Wie der Rechteck-/Dreieckgenerator, aber der Integrator integriert die STEUERSPANNUNG ±U_st (ein Umschalter
    wählt das Vorzeichen nach dem Schmitt-Trigger). Steigung U_st / (R · C), Schwellen ±U_sat · R1 / R2:
      f = U_st · R2 / (4 · R1 · R · C · U_sat)      -> Frequenz proportional zur Steuerspannung
      Steilheit K_VCO = f / U_st = R2 / (4 · R1 · R · C · U_sat)   in Hz/V
    """
    _positiv(R1=r1, R2=r2, R=r, C=c, U_sat=u_sat)
    if u_st < 0:
        raise ValueError("Steuerspannung U_st ≥ 0 eingeben")
    if r1 >= r2:
        raise ValueError("R1 muss kleiner als R2 sein")
    k = r2 / (4 * r1 * r * c * u_sat)
    return {"f": k * u_st, "k": k, "u_d": u_sat * r1 / r2, "steigung": u_st / (r * c)}


def vco_kurven(r1, r2, r, c, u_sat, u_st, dauer, punkte=400):
    """Rechteck und Dreieck über eine FESTE Zeitspanne - so sieht man, wie U_st die Frequenz ändert."""
    e = vco(r1, r2, r, c, u_sat, u_st)
    recht, drei = [], []
    for k in range(punkte + 1):
        t = dauer * k / punkte
        x = (t * e["f"]) % 1.0 if e["f"] > 0 else 0.25
        if x < 0.5:
            recht.append((k / punkte, u_sat))
            drei.append((k / punkte, e["u_d"] - 4 * e["u_d"] * x))
        else:
            recht.append((k / punkte, -u_sat))
            drei.append((k / punkte, -e["u_d"] + 4 * e["u_d"] * (x - 0.5)))
    return {"rechteck": recht, "dreieck": drei, **e}
