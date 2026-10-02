# =============================================================================
# schaltungen/opv_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für OPV-Grundschaltungen - KEIN tkinter.
# Einzeln testbar, z.B.:
#
#   python -c "from schaltungen.opv_mathe import *; print(verstaerker('nichtinvertierend', 10e3, 90e3, 0.5, 12))"
#
#   aussteuergrenzen()   wie weit kommt der Ausgang an ±U_B heran?
#   verstaerker()        Spannungsfolger, nichtinvertierend, invertierend (+ Bandbreite aus GBW)
#   addierer()           invertierender Summierer
#   differenz()          Differenzverstärker (4 Widerstände) und Gleichtaktfehler durch Toleranz
#   instrumenten()       Instrumentenverstärker (3 OPV), Verstärkung über R_G
#   schmitt_schwellen()  Schaltschwellen eines Schmitt-Triggers (invertierend / nichtinvertierend)
#   schmitt_auslegen()   Widerstandsverhältnis und U_ref für gewünschte Schwellen
#   komparator_sim()     Komparator / Schmitt-Trigger mit verrauschtem Sinus (Zeitdiagramm)
#   integrator_sim()     Integrator (Rechteck -> Dreieck) mit/ohne R_p parallel zu C
#   differenzierer_sim() Differenzierer (Dreieck -> Rechteck) mit/ohne R_s vor C
#
# MODELL (ideal, reicht für HF-Niveau):
#   Eingänge stromlos, Ausgang niederohmig, mit Gegenkopplung gilt U+ = U− (virtueller Kurzschluss),
#   Ausgang begrenzt auf ±(U_B − U_rest)  (klassisch ≈ 1.5 V, Rail-to-Rail ≈ 0.05 V),
#   Verstärkungs-Bandbreite-Produkt GBW:  f_g = GBW / Rauschverstärkung (1 + R2 / R1)
#
# WER RUFT DAS AUF?  schaltungen/grafiken_opv.py, schaltungen/rechner.py
# =============================================================================

import math

VERSTAERKER_ARTEN = ["Spannungsfolger", "nichtinvertierend", "invertierend"]
SCHMITT_ARTEN = ["invertierend", "nichtinvertierend"]
U_REST = 1.5                 # V, klassischer OPV (z.B. TL072) kommt so nah an die Versorgung
U_REST_RAIL = 0.05           # V, Rail-to-Rail-Ausgang
GBW = 1e6                    # Hz, typischer Universal-OPV (LM358, TL072 ≈ 3 MHz)


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


def aussteuergrenzen(u_b, rail=False):
    """Symmetrische Versorgung ±u_b -> (U_max, U_min) am Ausgang."""
    _positiv(U_B=u_b)
    rest = U_REST_RAIL if rail else U_REST
    if u_b <= rest:
        raise ValueError(f"Versorgung zu klein – der OPV braucht mehr als ±{rest:g} V")
    return u_b - rest, -(u_b - rest)


def _begrenzen(u, u_max, u_min):
    return min(max(u, u_min), u_max)


# =============================================================================
# VERSTÄRKER
# =============================================================================
def verstaerker(art, r1, r2, u_e, u_b, rail=False, gbw=GBW, u_hat=0.0):
    """
    art "Spannungsfolger":   Vu = 1                (R1, R2 werden ignoriert)
        "nichtinvertierend": Vu = 1 + R2 / R1      r_ein ≈ ∞ (Eingang am +)
        "invertierend":      Vu = −R2 / R1         r_ein = R1 (− ist virtuelle Masse)
    u_e:   Gleichspannung am Eingang,  u_hat: Scheitelwert eines überlagerten Sinus
    Rückgabe: vu, u_a (begrenzt), r_ein, Bandbreite f_g, Zeitkurven (ideal / begrenzt)
    """
    if art not in VERSTAERKER_ARTEN:
        raise ValueError(f"Unbekannte Schaltung: {art}")
    if art != "Spannungsfolger":
        _positiv(R1=r1, R2=r2)
    u_max, u_min = aussteuergrenzen(u_b, rail)
    if art == "Spannungsfolger":
        vu, rausch, r_ein = 1.0, 1.0, math.inf
    elif art == "nichtinvertierend":
        vu, rausch, r_ein = 1 + r2 / r1, 1 + r2 / r1, math.inf
    else:
        vu, rausch, r_ein = -r2 / r1, 1 + r2 / r1, r1
    ideal = [(k / 200, vu * (u_e + u_hat * math.sin(4 * math.pi * k / 200))) for k in range(201)]
    aus = [(t, _begrenzen(u, u_max, u_min)) for t, u in ideal]
    begrenzt = any(abs(u - v) > 1e-9 for (_, u), (_, v) in zip(ideal, aus))
    return {"vu": vu, "db": 20 * math.log10(abs(vu)), "u_a": _begrenzen(vu * u_e, u_max, u_min),
            "u_a_ideal": vu * u_e, "r_ein": r_ein, "f_g": gbw / rausch, "rauschverstaerkung": rausch,
            "u_max": u_max, "u_min": u_min, "begrenzt": begrenzt,
            "kurve_ein": [(k / 200, u_e + u_hat * math.sin(4 * math.pi * k / 200)) for k in range(201)],
            "kurve_ideal": ideal, "kurve_aus": aus}


# =============================================================================
# ADDIERER
# =============================================================================
def addierer(spannungen, widerstaende, r_f, u_b=15.0, rail=False):
    """
    Invertierender Summierer:  Ua = −R_f · (U1/R1 + U2/R2 + ...)
    Am − liegt virtuelle Masse: Jeder Eingang sieht nur seinen Widerstand, die Ströme addieren sich in R_f.
    """
    if len(spannungen) != len(widerstaende) or not spannungen:
        raise ValueError("Zu jeder Eingangsspannung gehört ein Widerstand")
    _positiv(R_f=r_f, **{f"R{i + 1}": r for i, r in enumerate(widerstaende)})
    u_max, u_min = aussteuergrenzen(u_b, rail)
    stroeme = [u / r for u, r in zip(spannungen, widerstaende)]
    ideal = -r_f * sum(stroeme)
    return {"stroeme": stroeme, "i_f": sum(stroeme), "u_a_ideal": ideal, "u_a": _begrenzen(ideal, u_max, u_min),
            "begrenzt": not u_min <= ideal <= u_max, "gewichte": [-r_f / r for r in widerstaende]}


# =============================================================================
# DIFFERENZ- UND INSTRUMENTENVERSTÄRKER
# =============================================================================
def differenz(u1, u2, r1, r2, toleranz=0.0, u_b=15.0, rail=False):
    """
    Differenzverstärker mit R1 (Eingänge) und R2 (Gegenkopplung bzw. nach GND):
      Ua = R2 / R1 · (U2 − U1)        (U2 am +, U1 am −)
    Toleranz der Widerstände (z.B. 0.01 = 1 %), ungünstigste Kombination:
      Gleichtaktverstärkung  A_cm ≈ 4 · tol · R2 / (R1 + R2)   ->   CMRR = A_d / A_cm ≈ (1 + R2/R1) / (4 · tol)
    Eingangswiderstand: − Eingang R1 (gegen virtuelle Masse), + Eingang R1 + R2 – NICHT hochohmig!
    """
    _positiv(R1=r1, R2=r2)
    if toleranz < 0 or toleranz >= 0.5:
        raise ValueError("Toleranz zwischen 0 und 50 % angeben")
    u_max, u_min = aussteuergrenzen(u_b, rail)
    a_d = r2 / r1
    u_cm = (u1 + u2) / 2
    a_cm = 4 * toleranz * r2 / (r1 + r2)
    ideal = a_d * (u2 - u1) + a_cm * u_cm
    cmrr = math.inf if toleranz == 0 else (1 + a_d) / (4 * toleranz)
    return {"a_d": a_d, "u_d": u2 - u1, "u_cm": u_cm, "a_cm": a_cm, "fehler_cm": a_cm * u_cm,
            "cmrr": cmrr, "cmrr_db": math.inf if toleranz == 0 else 20 * math.log10(cmrr),
            "u_a": _begrenzen(ideal, u_max, u_min), "begrenzt": not u_min <= ideal <= u_max,
            "r_ein_minus": r1, "r_ein_plus": r1 + r2}


def instrumenten(u1, u2, r, r_g, r1=10e3, r2=10e3, toleranz=0.0, u_b=15.0, rail=False):
    """
    Instrumentenverstärker aus 3 OPV:
      Eingangsstufe (2 nichtinvertierende OPV, R zwischen Ausgang und −, R_G zwischen den − Eingängen):
        Differenz wird um G1 = 1 + 2 · R / R_G verstärkt, Gleichtakt nur um 1
      Ausgangsstufe = Differenzverstärker mit R2 / R1
      Ua = (1 + 2 · R / R_G) · R2 / R1 · (U2 − U1)
    Vorteil: beide Eingänge hochohmig, Verstärkung mit EINEM Widerstand R_G einstellbar,
    Gleichtaktunterdrückung um G1 besser als beim einfachen Differenzverstärker.
    """
    _positiv(R=r, R_G=r_g)
    g1 = 1 + 2 * r / r_g
    # Ausgänge der Eingangsstufe: Gleichtakt bleibt, Differenz wird um G1 grösser
    #   o1 = U1 − R · (U2 − U1) / R_G,   o2 = U2 + R · (U2 − U1) / R_G
    u_cm, u_d = (u1 + u2) / 2, u2 - u1
    innen = [u_cm - g1 * u_d / 2, u_cm + g1 * u_d / 2]
    stufe2 = differenz(innen[0], innen[1], r1, r2, toleranz, u_b, rail)
    u_max, u_min = aussteuergrenzen(u_b, rail)
    return {**stufe2, "u_d": u_d, "u_cm": u_cm, "g1": g1, "g": g1 * r2 / r1, "u_innen": innen,
            "innen_begrenzt": any(not u_min <= u <= u_max for u in innen),
            "cmrr": stufe2["cmrr"] * g1, "cmrr_db": stufe2["cmrr_db"] + 20 * math.log10(g1),
            "r_ein_minus": math.inf, "r_ein_plus": math.inf}


# =============================================================================
# KOMPARATOR UND SCHMITT-TRIGGER
# =============================================================================
def schmitt_schwellen(art, r1, r_f, u_ref, u_sat_plus, u_sat_minus=None):
    """
    Mitkopplung über R_f vom Ausgang an den + Eingang.
    invertierend:      Signal an −, R1 von + nach U_ref
        U+ = (U_ref · R_f + U_a · R1) / (R1 + R_f)
        U_T± = (U_ref · R_f + U_sat± · R1) / (R1 + R_f)          Hysterese = (U_sat+ − U_sat−) · R1 / (R1 + R_f)
    nichtinvertierend: Signal über R1 an +, − an U_ref
        schaltet, wenn U+ = U_ref:   U_e = U_ref · (1 + R1 / R_f) − U_a · R1 / R_f
        U_T+ = U_ref · (1 + R1/R_f) − U_sat− · R1/R_f,  U_T− = U_ref · (1 + R1/R_f) − U_sat+ · R1/R_f
    Rückgabe: dict mit u_tp (obere Schwelle), u_tm (untere), hysterese, mitte
    """
    _positiv(R1=r1, R_f=r_f)
    if u_sat_minus is None:
        u_sat_minus = -u_sat_plus
    if art == "invertierend":
        u_tp = (u_ref * r_f + u_sat_plus * r1) / (r1 + r_f)
        u_tm = (u_ref * r_f + u_sat_minus * r1) / (r1 + r_f)
    elif art == "nichtinvertierend":
        k = r1 / r_f
        u_tp = u_ref * (1 + k) - u_sat_minus * k
        u_tm = u_ref * (1 + k) - u_sat_plus * k
    else:
        raise ValueError(f"Unbekannter Schmitt-Trigger: {art}")
    return {"u_tp": u_tp, "u_tm": u_tm, "hysterese": u_tp - u_tm, "mitte": (u_tp + u_tm) / 2}


def schmitt_auslegen(art, u_tp, u_tm, u_sat, r_f=100e3):
    """
    Umkehrung von schmitt_schwellen() bei symmetrischem Ausgang ±u_sat:
      invertierend:      R1 / (R1 + R_f) = ΔU / (2 · U_sat),   U_ref = Mitte / (1 − R1/(R1 + R_f))
      nichtinvertierend: R1 / R_f = ΔU / (2 · U_sat),           U_ref = Mitte / (1 + R1 / R_f)
    """
    _positiv(U_sat=u_sat, R_f=r_f)
    if u_tp <= u_tm:
        raise ValueError("Die obere Schwelle U_T+ muss grösser als die untere U_T− sein")
    delta, mitte = u_tp - u_tm, (u_tp + u_tm) / 2
    if art == "invertierend":
        k = delta / (2 * u_sat)
        if k >= 1:
            raise ValueError("Hysterese grösser als 2 · U_sat – mit diesem OPV nicht möglich")
        r1 = k * r_f / (1 - k)
        u_ref = mitte / (1 - k)
    elif art == "nichtinvertierend":
        k = delta / (2 * u_sat)
        r1 = k * r_f
        u_ref = mitte / (1 + k)
    else:
        raise ValueError(f"Unbekannter Schmitt-Trigger: {art}")
    return {"r1": r1, "r_f": r_f, "u_ref": u_ref, "verhaeltnis": r1 / r_f}


def eingang_verrauscht(t, u_hat, rauschen):
    """Langsamer Sinus (2 Perioden auf t = 0 … 1) mit schneller Störung (deterministisch, wiederholbar)."""
    stoerung = rauschen * (0.6 * math.sin(2 * math.pi * 37 * t) + 0.4 * math.sin(2 * math.pi * 91 * t + 1.3))
    return u_hat * math.sin(4 * math.pi * t) + stoerung


def komparator_sim(art, u_hat, rauschen, u_b, r1=10e3, r_f=100e3, u_ref=0.0, rail=False, punkte=1200, _soll=True):
    """
    art "Komparator" (ohne Hysterese, Signal an +, U_ref an −) oder ein Eintrag aus SCHMITT_ARTEN.
    Rückgabe: Kurven Eingang / Ausgang, Schwellen, Zahl der Umschaltungen
    wechsel_soll = Umschaltungen OHNE Störung (2 Perioden Sinus: meist 4) – mehr = Störung schaltet mit, „Flattern“.
    """
    u_max, u_min = aussteuergrenzen(u_b, rail)
    if art == "Komparator":
        u_tp = u_tm = u_ref
        invertiert = False
    else:
        s = schmitt_schwellen(art, r1, r_f, u_ref, u_max, u_min)
        u_tp, u_tm = s["u_tp"], s["u_tm"]
        invertiert = art == "invertierend"
    ein, aus = [], []
    oben = eingang_verrauscht(-0.02, u_hat, 0.0) > (u_tp + u_tm) / 2      # Zustand kurz VOR dem Bild (ohne Störung)
    wechsel = 0
    for n in range(punkte + 1):
        t = n / punkte
        u = eingang_verrauscht(t, u_hat, rauschen)
        neu = True if u > u_tp else (False if u < u_tm else oben)
        if n and neu != oben:
            wechsel += 1
        oben = neu
        ein.append((t, u))
        aus.append((t, (u_min if oben else u_max) if invertiert else (u_max if oben else u_min)))
    soll = komparator_sim(art, u_hat, 0.0, u_b, r1, r_f, u_ref, rail, punkte, False)["wechsel"] if _soll else wechsel
    return {"u_tp": u_tp, "u_tm": u_tm, "hysterese": u_tp - u_tm, "u_max": u_max, "u_min": u_min,
            "kurve_ein": ein, "kurve_aus": aus, "wechsel": wechsel, "wechsel_soll": soll, "invertiert": invertiert,
            "erreicht": u_hat + rauschen > u_tp and -u_hat - rauschen < u_tm}


# =============================================================================
# INTEGRATOR UND DIFFERENZIERER
# =============================================================================
def integrator_kennwerte(r, c, u_e, f=None, r_p=None):
    """
    Ua = −1 / (R · C) · ∫ Ue dt   ->  Steigung bei konstantem Ue:  dUa/dt = −Ue / (R · C)
    Rechteck ±Ue mit Frequenz f -> Dreieck mit Spitze-Spitze  ΔUa = Ue / (R · C) · 1 / (2 · f)
    R_p parallel zu C: Gleichspannungsverstärkung −R_p / R (verhindert Weglaufen),
                       integriert erst oberhalb f_u = 1 / (2π · R_p · C)
    """
    _positiv(R=r, C=c)
    e = {"tau": r * c, "steigung": -u_e / (r * c)}
    if f is not None:
        _positiv(f=f)
        e["dreieck_ss"] = abs(u_e) / (r * c) / (2 * f)
    if r_p is not None:
        _positiv(R_p=r_p)
        e["f_u"] = 1 / (2 * math.pi * r_p * c)
        e["v_dc"] = -r_p / r
    return e


def integrator_sim(r, c, u_e, f, u_b, r_p=None, offset=0.0, zeige=2, punkte_pro_periode=200):
    """
    Rechteck ±u_e (+ offset) am Eingang. Gerechnet wird Schritt für Schritt (exakt je Schritt):
      ohne R_p:  Ua(t + Δt) = Ua − Ue / (R · C) · Δt
      mit R_p:   Ua -> −R_p / R · Ue mit τ = R_p · C
    Ausgang begrenzt auf die Aussteuergrenzen. Gezeigt werden die letzten 'zeige' Perioden:
      ohne R_p nach 20 Perioden (ein Offset ist dann als Drift sichtbar),
      mit R_p nach ≈ 5 · R_p · C (eingeschwungen), mindestens 6, höchstens 400 Perioden.
    """
    _positiv(R=r, C=c, f=f)
    perioden = 20 if r_p is None else min(max(6, math.ceil(5 * r_p * c * f) + zeige), 400)
    u_max, u_min = aussteuergrenzen(u_b)
    dt = 1 / (f * punkte_pro_periode)
    ua, ein, aus = 0.0, [], []
    gesamt = perioden * punkte_pro_periode
    start = gesamt - zeige * punkte_pro_periode
    for n in range(gesamt + 1):
        phase = (n % punkte_pro_periode) / punkte_pro_periode
        ue = (u_e if phase < 0.5 else -u_e) + offset
        if n >= start:
            t = (n - start) / (zeige * punkte_pro_periode)
            ein.append((t, ue))
            aus.append((t, ua))
        if r_p is None:
            ua = ua - ue / (r * c) * dt
        else:
            ziel = -r_p / r * ue
            ua = ziel + (ua - ziel) * math.exp(-dt / (r_p * c))
        ua = _begrenzen(ua, u_max, u_min)
    werte = [u for _, u in aus]
    return {"kurve_ein": ein, "kurve_aus": aus, "u_max": u_max, "u_min": u_min,
            "aus_max": max(werte), "aus_min": min(werte),
            "gesaettigt": max(werte) >= u_max - 1e-9 or min(werte) <= u_min + 1e-9}


def differenzierer_sim(r, c, u_e, f, u_b, r_s=None, zeige=2, punkte_pro_periode=400):
    """
    Dreieck ±u_e mit Frequenz f am Eingang:  Steigung s = ±4 · u_e · f
      ideal:     Ua = −R · C · dUe/dt = ∓R · C · 4 · u_e · f          (Rechteck)
      mit R_s:   Strom durch C:  i + R_s · C · di/dt = C · dUe/dt      ->  Flanken runden mit τ_s = R_s · C ab
                 (R_s begrenzt die Verstärkung hoher Frequenzen auf −R / R_s -> kein Rauschen/Schwingen)
    """
    _positiv(R=r, C=c, f=f)
    u_max, u_min = aussteuergrenzen(u_b)
    s = 4 * u_e * f
    gesamt = (zeige + 2) * punkte_pro_periode                 # 2 Perioden Einschwingen
    dt = 1 / (f * punkte_pro_periode)
    i, ein, aus = 0.0, [], []
    start = 2 * punkte_pro_periode
    for n in range(gesamt + 1):
        phase = (n % punkte_pro_periode) / punkte_pro_periode
        ue = u_e * (4 * phase - 1 if phase < 0.5 else 3 - 4 * phase)
        steigung = s if phase < 0.5 else -s
        if r_s is None:
            i = c * steigung
        else:
            ziel = c * steigung
            i = ziel + (i - ziel) * math.exp(-dt / (r_s * c))
        ua = _begrenzen(-r * i, u_max, u_min)
        if n >= start:
            t = (n - start) / (zeige * punkte_pro_periode)
            ein.append((t, ue))
            aus.append((t, ua))
    ideal = r * c * s
    return {"kurve_ein": ein, "kurve_aus": aus, "u_max": u_max, "u_min": u_min, "u_a_ideal": ideal,
            "gesaettigt": ideal > u_max, "f_s": None if r_s is None else 1 / (2 * math.pi * r_s * c)}
