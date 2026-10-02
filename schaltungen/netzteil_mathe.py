# =============================================================================
# schaltungen/netzteil_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für Netzteile und Quellen - KEIN tkinter.
# Einzeln testbar, z.B.:
#
#   python -c "from schaltungen.netzteil_mathe import *; print(quelle('Spannungsquelle', 12, 2, 10))"
#
#   quelle()               ideale/reale Spannungs- und Stromquelle an einer Last (+ Kennlinien)
#   innenwiderstand()      R_i aus Leerlauf- und Lastmessung
#   netzteil_auslegen()    Trafo + Brücke + Elko rückwärts: welche Trafospannung, welcher Elko?
#   linearregler()         78xx / LDO / LM317: Dropout, Verlust, Wirkungsgrad, Sperrschichttemperatur
#   lm317_spannung(), lm317_r2()
#   laengsregler()         Z-Diode + Emitterfolger, wahlweise mit Strombegrenzung (Shunt + Transistor)
#   stromquelle_opv()      geregelte Stromsenke: OPV + MOSFET + Shunt
#   virtuelle_masse()      Rail-Splitter: Spannungsteiler mit/ohne OPV-Puffer bei ungleicher Last
#   schaltregler()         Buck / Boost im Dauerbetrieb (CCM): Tastgrad, Rippelstrom, Spitzenstrom
#
# Gleichrichter + Ladeelko (Simulation) steht schon in schaltungen/dioden_mathe.py.
# WER RUFT DAS AUF?  schaltungen/grafiken_netzteil.py, schaltungen/rechner.py
# =============================================================================

import math

QUELLEN_ARTEN = ["Spannungsquelle", "Stromquelle"]
U_BE = 0.7                 # V, Längstransistor
U_BE_BEGRENZUNG = 0.6      # V, ab hier leitet der Begrenzungstransistor merklich
U_CE_SAT = 0.2             # V
U_F = 0.7                  # V, Si-Diode
U_F_SCHOTTKY = 0.4         # V, Freilaufdiode im Schaltregler
LM317_REF, LM317_I_ADJ = 1.25, 50e-6
FAKTOR_I_EFF = 1.8         # Trafostrom (eff) ≈ 1.6 … 1.8 · I_DC bei Brücke mit Ladeelko (kurze Stromimpulse)


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


# =============================================================================
# QUELLENMODELL
# =============================================================================
def quelle(art, q, r_i, r_l, punkte=121):
    """
    Spannungsquelle (U0 in Reihe mit R_i):   I = U0 / (R_i + R_L),  U_K = U0 − I · R_i
    Stromquelle (I0 parallel zu R_i):          U_K = I0 · (R_i ∥ R_L), I_L = U_K / R_L
    Beide: Leistungsanpassung bei R_L = R_i, dann P_max = U_leer² / (4 · R_i), Wirkungsgrad 50 %.
    Kennlinien über R_L = R_i / 100 … 100 · R_i (logarithmisch): U_K / U_leer und P_L / P_max.
    """
    _positiv(Quelle=q, R_i=r_i, R_L=r_l)
    if art not in QUELLEN_ARTEN:
        raise ValueError(f"Unbekannte Quelle: {art}")
    u_leer = q if art == "Spannungsquelle" else q * r_i
    i_kurz = q / r_i if art == "Spannungsquelle" else q
    p_max = u_leer * u_leer / (4 * r_i)

    def an_last(r):
        u = u_leer * r / (r_i + r)                    # beide Modelle sind gleichwertig (Ersatzquelle)
        return u, u / r

    u_k, i = an_last(r_l)
    kurve_u, kurve_p = [], []
    for k in range(punkte):
        t = k / (punkte - 1)
        u, strom = an_last(r_i * 10 ** (4 * t - 2))
        kurve_u.append((t, u / u_leer))
        kurve_p.append((t, u * strom / p_max))
    eta = r_l / (r_i + r_l) if art == "Spannungsquelle" else r_i / (r_i + r_l)
    return {"u_leer": u_leer, "i_kurz": i_kurz, "u_k": u_k, "i": i, "p_l": u_k * i, "p_max": p_max,
            "p_ri": (u_leer - u_k) * i if art == "Spannungsquelle" else u_k * u_k / r_i,
            "eta": eta, "kurve_u": kurve_u, "kurve_p": kurve_p,
            "position": min(max((math.log10(r_l / r_i) + 2) / 4, 0.0), 1.0)}


def innenwiderstand(u_leer, u_last, r_last=None, i_last=None):
    """R_i = (U_leer − U_last) / I_last,  I_last = U_last / R_last (oder gemessen)."""
    _positiv(U_leer=u_leer)
    if u_last < 0 or u_last > u_leer:
        raise ValueError("U_last muss zwischen 0 und U_leer liegen")
    if i_last is None:
        _positiv(R_last=r_last)
        i_last = u_last / r_last
    _positiv(I_last=i_last)
    r_i = (u_leer - u_last) / i_last
    return {"r_i": r_i, "i": i_last, "i_kurz": math.inf if r_i == 0 else u_leer / r_i}


# =============================================================================
# UNGEREGELTES NETZTEIL RÜCKWÄRTS AUSLEGEN
# =============================================================================
def netzteil_auslegen(u_tal, i, delta_u=None, c=None, f=50.0, netz_toleranz=0.1, leerlauf=0.1, u_f=U_F):
    """
    Was muss der Trafo liefern, damit am Elko im Wellental noch u_tal anliegt (z.B. U_aus + Dropout)?
      ΔU = I / (2 · f · C)                     (Brücke: Elko wird 2 · f mal pro Sekunde nachgeladen)
      Û_sek,min = u_tal + ΔU + 2 · U_F         bei Netz −10 %
      U_sek (eff, Nenn) = Û_sek,min / (√2 · (1 − Toleranz))
      I_sek,eff ≈ 1.8 · I    ->   Trafo-Scheinleistung S = U_sek · I_sek,eff
      Elko-Spannung: Netz +10 % und Trafo-Leerlaufüberhöhung (+10 % bei kleinen Trafos)
    Entweder delta_u (Welligkeit) ODER c vorgeben; ohne beides: ΔU = 10 % von u_tal.
    """
    _positiv(U_Tal=u_tal, I=i, f=f)
    if c is not None:
        _positiv(C=c)
        delta_u = i / (2 * f * c)
    elif delta_u is None:
        delta_u = 0.1 * u_tal
    _positiv(Welligkeit=delta_u)
    c_noetig = i / (2 * f * delta_u)
    u_spitze_min = u_tal + delta_u + 2 * u_f
    u_sek = u_spitze_min / (math.sqrt(2) * (1 - netz_toleranz))
    u_elko_max = u_sek * math.sqrt(2) * (1 + netz_toleranz) * (1 + leerlauf) - 2 * u_f
    i_eff = FAKTOR_I_EFF * i
    return {"delta_u": delta_u, "c": c_noetig, "u_spitze_min": u_spitze_min, "u_sek": u_sek,
            "u_elko_max": u_elko_max, "i_sek_eff": i_eff, "s_trafo": u_sek * i_eff,
            "u_mittel_nenn": u_sek * math.sqrt(2) - 2 * u_f - delta_u / 2}


# =============================================================================
# LINEARREGLER
# =============================================================================
def linearregler(u_spitze, delta_u, u_a, i, u_drop, r_th=None, t_a=25.0, perioden=2, punkte=240):
    """
    Eingang = Elko nach dem Gleichrichter: Spitze u_spitze, Wellental u_spitze − ΔU (Sägezahn, 100 Hz).
      regelt, solange  U_ein ≥ U_aus + U_Dropout   (auch im Wellental!)
      P = (U_ein,mittel − U_aus) · I          η = U_aus / U_ein,mittel
      T_j = T_a + P · R_th                     (R_th: Sperrschicht -> Umgebung, inkl. Kühlkörper)
    Im Dropout folgt der Ausgang dem Eingang:  U_aus ≈ U_ein − U_Dropout  (Welligkeit kommt durch!)
    """
    _positiv(U_ein=u_spitze, U_aus=u_a, I=i)
    if delta_u < 0 or u_drop < 0:
        raise ValueError("Welligkeit und Dropout dürfen nicht negativ sein")
    u_tal = u_spitze - delta_u
    u_mittel = u_spitze - delta_u / 2
    ein, aus = [], []
    for k in range(punkte + 1):
        t = k / punkte
        phase = (t * perioden) % 1.0
        # schnelles Nachladen (15 % der Periode), dann lineares Entladen
        u = u_tal + delta_u * (phase / 0.15 if phase < 0.15 else 1 - (phase - 0.15) / 0.85)
        ein.append((t, u))
        aus.append((t, max(min(u_a, u - u_drop), 0.0)))
    p = max(u_mittel - u_a, 0.0) * i
    e = {"u_tal": u_tal, "u_mittel": u_mittel, "regelt": u_tal >= u_a + u_drop, "reserve": u_tal - u_a - u_drop,
         "p": p, "eta": min(u_a / u_mittel, 1.0) if u_mittel > 0 else 0.0, "kurve_ein": ein, "kurve_aus": aus}
    if r_th is not None:
        e["t_j"] = t_a + p * r_th
    return e


def lm317_spannung(r1, r2):
    """U_aus = 1.25 V · (1 + R2 / R1) + I_ADJ · R2   (I_ADJ ≈ 50 µA)"""
    _positiv(R1=r1)
    if r2 < 0:
        raise ValueError("R2 darf nicht negativ sein")
    return LM317_REF * (1 + r2 / r1) + LM317_I_ADJ * r2


def lm317_r2(u_a, r1=240.0):
    """R2 = (U_aus − 1.25 V) / (1.25 V / R1 + I_ADJ)   (R1 = 240 Ω -> 5.2 mA Mindestlast)"""
    _positiv(R1=r1)
    if u_a < LM317_REF:
        raise ValueError("Der LM317 liefert mindestens 1.25 V")
    return (u_a - LM317_REF) / (LM317_REF / r1 + LM317_I_ADJ)


# =============================================================================
# LÄNGSREGLER MIT STROMBEGRENZUNG
# =============================================================================
def laengsregler(u_e, u_z, r_l, r_s=None, punkte=121):
    """
    Z-Diode an der Basis, Längstransistor T1 als Emitterfolger:  U_a0 = U_Z − 0.7 V
    Mit Strombegrenzung: Shunt R_S im Ausgang, T2 (B-E über R_S) leitet ab ≈ 0.6 V
      I_max = 0.6 V / R_S  -> T2 zieht den Basisstrom von T1 ab, der Strom bleibt bei I_max.
      unterhalb:  U_a = U_a0 − I · R_S
    Verlust in T1:  (U_e − U_a − I · R_S) · I,  am grössten bei Kurzschluss: ≈ U_e · I_max
    Kennlinie U_a über I (Last von Leerlauf bis Kurzschluss).
    """
    _positiv(U_e=u_e, U_Z=u_z, R_L=r_l)
    u_a0 = min(u_z - U_BE, u_e - U_CE_SAT)
    if u_a0 <= 0:
        raise ValueError("U_Z muss über 0.7 V liegen")
    rs = 0.0 if r_s is None else r_s
    i_max = math.inf if r_s is None else U_BE_BEGRENZUNG / r_s

    def arbeitspunkt(r):
        strom = u_a0 / (r + rs)
        if strom > i_max:
            strom = i_max
        return strom * r, strom

    u_a, i = arbeitspunkt(r_l)
    i_k = u_a0 / rs if r_s is not None else math.inf                 # rechnerischer Kurzschlussstrom ohne T2
    i_achse = (1.5 * i_max) if r_s is not None else max(2.5 * i, 1e-3)
    kurve = []
    for k in range(punkte):
        strom = i_achse * k / (punkte - 1)
        if strom <= i_max:
            kurve.append((k / (punkte - 1), max(u_a0 - strom * rs, 0.0)))
    if r_s is not None:
        kurve.append((i_max / i_achse, 0.0))                          # senkrecht nach unten bis Kurzschluss
    return {"u_a0": u_a0, "u_a": u_a, "i": i, "i_max": i_max, "begrenzt": r_s is not None and i >= i_max - 1e-12,
            "p_t1": max(u_e - u_a - i * rs, 0.0) * i,
            "p_t1_kurz": (u_e - (i_max * rs)) * i_max if r_s is not None else math.inf,
            "p_rs": i * i * rs, "kurve": kurve, "i_achse": i_achse, "i_k_ohne": i_k}


# =============================================================================
# GEREGELTE STROMQUELLE (OPV + MOSFET + SHUNT)
# =============================================================================
def stromquelle_opv(u_soll, r_shunt, u_b, r_last, r_ds=0.05, punkte=81):
    """
    OPV regelt die Shunt-Spannung auf U_soll:  I = U_soll / R_Shunt  (unabhängig von der Last)
    Arbeitsbereich: I · (R_Last + R_Shunt + R_DS,on) ≤ U_B  -> darüber ist der MOSFET voll durch.
    Verlust im MOSFET: P = (U_B − I · (R_Last + R_Shunt)) · I
    """
    _positiv(U_soll=u_soll, R_Shunt=r_shunt, U_B=u_b)
    if r_last < 0:
        raise ValueError("R_Last darf nicht negativ sein")
    i_soll = u_soll / r_shunt

    def strom(r):
        return min(i_soll, u_b / (r + r_shunt + r_ds))

    i = strom(r_last)
    r_max = max(u_b / i_soll - r_shunt - r_ds, 0.0)
    r_achse = max(2.0 * r_max, 1.3 * r_last, 1.0)
    return {"i_soll": i_soll, "i": i, "regelt": i >= i_soll * 0.999, "r_last_max": r_max,
            "u_last": i * r_last, "p_mos": max(u_b - i * (r_last + r_shunt), 0.0) * i,
            "p_mos_max": max(u_b - i_soll * r_shunt, 0.0) * i_soll, "p_shunt": i * i * r_shunt,
            "kurve": [(k / (punkte - 1), strom(r_achse * k / (punkte - 1))) for k in range(punkte)], "r_achse": r_achse}


# =============================================================================
# VIRTUELLE MASSE (RAIL-SPLITTER)
# =============================================================================
def virtuelle_masse(u_b, r, r_l1, r_l2, opv=False, i_opv_max=0.02):
    """
    Einzelne Versorgung U_B, Teiler aus 2 · R erzeugt die Mitte M (= neue Masse).
    Last R_L1 zwischen +U_B und M (positive Seite), R_L2 zwischen M und 0 V (negative Seite).
    Knotengleichung an M (ohne OPV):
      U_M = U_B · (1/R + 1/R_L1) / (2/R + 1/R_L1 + 1/R_L2)
    Mit OPV-Folger an M: U_M = U_B / 2, der OPV liefert/schluckt die Differenz der Lastströme
      I_OPV = U_M / R_L2 − (U_B − U_M) / R_L1   (begrenzt auf ±i_opv_max, z.B. 20 mA)
    """
    _positiv(U_B=u_b, R=r, R_L1=r_l1, R_L2=r_l2)
    g_oben, g_unten = 1 / r + 1 / r_l1, 1 / r + 1 / r_l2
    u_m = u_b * g_oben / (g_oben + g_unten)
    i_opv = 0.0
    if opv:
        noetig = (u_b / 2) / r_l2 - (u_b / 2) / r_l1
        if abs(noetig) <= i_opv_max:
            u_m, i_opv = u_b / 2, noetig
        else:
            i_opv = math.copysign(i_opv_max, noetig)
            u_m = (u_b * g_oben + i_opv) / (g_oben + g_unten)
    return {"u_m": u_m, "u_plus": u_b - u_m, "u_minus": -u_m, "i_l1": (u_b - u_m) / r_l1, "i_l2": u_m / r_l2,
            "i_opv": i_opv, "i_teiler": u_b / (2 * r), "abweichung": u_m - u_b / 2,
            "opv_am_limit": opv and abs(i_opv) >= i_opv_max - 1e-12}


# =============================================================================
# SCHALTREGLER BUCK / BOOST
# =============================================================================
SCHALTREGLER_ARTEN = ["Buck (abwärts)", "Boost (aufwärts)"]


def schaltregler(art, u_e, u_a, i_a, f, l, c=None, perioden=2, punkte=400):
    """
    Idealer Wandler im Dauerbetrieb (CCM, Spulenstrom wird nie 0), Verluste vernachlässigt:
      Buck:   D = U_a / U_e          ΔI = (U_e − U_a) · D / (f · L)     I_L = I_a
              ΔU_a ≈ ΔI / (8 · f · C)
      Boost:  D = 1 − U_e / U_a      ΔI = U_e · D / (f · L)             I_L = I_a / (1 − D)
              ΔU_a ≈ I_a · D / (f · C)
      I_Spitze = I_L + ΔI / 2   (Schalter, Diode und Spule müssen das aushalten)
      CCM, solange I_L > ΔI / 2 – sonst lückt der Strom (DCM) und die Formel für D gilt nicht mehr.
    Kurven über 'perioden' Schaltperioden: Spulenstrom i_L und Spannung am Schaltknoten u_SW.
    """
    _positiv(U_e=u_e, U_a=u_a, I_a=i_a, f=f, L=l)
    if art == SCHALTREGLER_ARTEN[0]:
        if u_a >= u_e:
            raise ValueError("Buck: U_a muss kleiner als U_e sein")
        d = u_a / u_e
        di = (u_e - u_a) * d / (f * l)
        i_l = i_a
        anstieg, abfall = (u_e - u_a) / l, u_a / l
        u_sw_ein, u_sw_aus = u_e, -U_F_SCHOTTKY
        du = None if c is None else di / (8 * f * c)
    elif art == SCHALTREGLER_ARTEN[1]:
        if u_a <= u_e:
            raise ValueError("Boost: U_a muss grösser als U_e sein")
        d = 1 - u_e / u_a
        di = u_e * d / (f * l)
        i_l = i_a / (1 - d)
        anstieg, abfall = u_e / l, (u_a - u_e) / l
        u_sw_ein, u_sw_aus = 0.0, u_a + U_F_SCHOTTKY
        du = None if c is None else i_a * d / (f * c)
    else:
        raise ValueError(f"Unbekannter Schaltregler: {art}")
    if c is not None:
        _positiv(C=c)
    ccm = i_l > di / 2
    t_per = 1 / f
    i_start = i_l - di / 2 if ccm else 0.0
    kurve_i, kurve_u = [], []
    for k in range(punkte + 1):
        t = k / punkte
        phase = (t * perioden) % 1.0
        if phase < d:
            strom = i_start + anstieg * phase * t_per
            u_sw = u_sw_ein
        else:
            strom = max(i_start + anstieg * d * t_per - abfall * (phase - d) * t_per, 0.0)
            u_sw = u_sw_aus if (ccm or strom > 0) else (u_a if art == SCHALTREGLER_ARTEN[0] else u_e)
        kurve_i.append((t, strom))
        kurve_u.append((t, u_sw))
    return {"d": d, "delta_i": di, "i_l": i_l, "i_spitze": i_l + di / 2 if ccm else anstieg * d * t_per,
            "ccm": ccm, "delta_u": du, "l_30": (di * l) / (0.3 * i_l),
            "kurve_i": kurve_i, "kurve_u": kurve_u, "u_sw_max": max(u_sw_ein, u_sw_aus)}
