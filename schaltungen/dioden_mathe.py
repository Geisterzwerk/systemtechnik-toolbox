# =============================================================================
# schaltungen/dioden_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für Dioden- und Schutzschaltungen - KEIN tkinter.
# Einzeln testbar, z.B.:
#
#   python -c "from schaltungen.dioden_mathe import *; print(gleichrichter('Brücke', 12, 0.5, 2200e-6))"
#
#   begrenzer()        Diodenbegrenzung (Clipper): Pegel, Strom, Kurvenform
#   eingangsschutz()   Serienwiderstand + Klemmdioden vor einem IC-Eingang
#   verpolschutz()     ohne / Si-Diode / Schottky / P-MOSFET: Spannungsfall, Verlust, Verhalten verpolt
#   gleichrichter()    Einweg / Brücke / Mittelpunkt mit Ladeelko (Formeln + Zeitsimulation)
#   z_arbeitspunkt()   Z-Dioden-Stabilisierung mit Last: Ua, Iz, Leistungen
#   tvs()              TVS-Diode gegen Spannungsspitzen: Klemmspannung, Spitzenstrom, Pulsleistung
#
# DIODENMODELL (bewusst einfach, reicht zum Verstehen):
#   leitet, sobald die Spannung über U_F liegt (Si 0.7 V, Schottky ca. 0.3 … 0.45 V), sonst sperrt sie.
#   Z-/TVS-Diode in Sperrrichtung: ab U_Z bzw. U_BR leitet sie, mit kleinem differentiellem Widerstand.
#
# WER RUFT DAS AUF?  schaltungen/grafiken_dioden.py, schaltungen/rechner.py,
#                    bauteile/rechner/halbleiter_rechner.py (Gleichrichter)
# =============================================================================

import math

U_F_SI = 0.7             # V, Silizium-Diode
U_F_SCHOTTKY = 0.45      # V, Schottky bei einigen 100 mA (Datenblatt!)
U_GS_MAX = 20.0          # V, übliche Gate-Grenze eines MOSFET
U_BR_FAKTOR = 1.11       # TVS: U_BR,min ≈ 1.11 · U_WM (typisch für „A“-Typen, Datenblatt!)
R_F_TVS = 0.02           # Ω, TVS in DURCHLASSrichtung (unidirektional): U_F ≈ 3.5 V bei 150 A (Datenblatt V_F)

GLEICHRICHTER = ["Brücke", "Einweg", "Mittelpunkt"]


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


# =============================================================================
# BEGRENZER
# =============================================================================
def begrenzer(art, u_hat, r_v, u_f=U_F_SI, u_z=None, punkte=241):
    """
    Sinus mit Scheitelwert u_hat über Vorwiderstand R_V, Dioden vom Ausgang nach GND.
      "einseitig"   eine Diode: nur die positive Halbwelle wird bei +U_F begrenzt
      "zweiseitig"  zwei Dioden antiparallel: ±U_F
      "z"           zwei Z-Dioden gegeneinander: ±(U_Z + U_F)
    Ohne Last am Ausgang: ua = ue, solange keine Diode leitet.
    """
    _positiv(R_V=r_v)
    if art == "einseitig":
        oben, unten = u_f, -math.inf
    elif art == "zweiseitig":
        oben, unten = u_f, -u_f
    elif art == "z":
        _positiv(U_Z=u_z)
        oben, unten = u_z + u_f, -(u_z + u_f)
    else:
        raise ValueError(f"Unbekannte Art: {art}")
    kurve_ein, kurve_aus = [], []
    for k in range(punkte):
        t = k / (punkte - 1)
        ue = u_hat * math.sin(2 * math.pi * t)
        kurve_ein.append((t, ue))
        kurve_aus.append((t, min(max(ue, unten), oben)))
    i_max = max(0.0, u_hat - oben) / r_v
    i_min = max(0.0, u_hat + unten) / r_v if unten > -math.inf else 0.0
    i_spitze = max(i_max, i_min)
    return {"oben": oben, "unten": unten, "i_spitze": i_spitze, "p_rv_spitze": i_spitze ** 2 * r_v,
            "begrenzt": u_hat > oben, "kurve_ein": kurve_ein, "kurve_aus": kurve_aus}


# =============================================================================
# EINGANGSSCHUTZ
# =============================================================================
def eingangsschutz(u_ein, r, u_dd, u_f=U_F_SI):
    """
    Serienwiderstand R vor dem Pin, Klemmdioden Pin -> U_DD und GND -> Pin (intern als ESD-Dioden
    vorhanden, extern z.B. BAT54S). Über U_DD + U_F bzw. unter −U_F leiten sie:
      U_Pin    = U_DD + U_F  bzw.  −U_F
      I_inj    = (U_ein − U_Pin) / R    (Injektionsstrom, Datenblatt: oft nur ±1 … 5 mA erlaubt)
    i_inj > 0: Strom fliesst über die obere Diode IN die Versorgung U_DD
    i_inj < 0: Strom wird über die untere Diode aus GND gezogen
    """
    _positiv(R=r, U_DD=u_dd)
    if u_ein > u_dd + u_f:
        u_pin, weg = u_dd + u_f, "U_DD"
    elif u_ein < -u_f:
        u_pin, weg = -u_f, "GND"
    else:
        u_pin, weg = u_ein, None
    i_inj = (u_ein - u_pin) / r
    return {"u_pin": u_pin, "i_inj": i_inj, "weg": weg, "p_r": i_inj * i_inj * r,
            "u_r": u_ein - u_pin}


# =============================================================================
# VERPOLSCHUTZ
# =============================================================================
VERPOL_ARTEN = ["ohne Schutz", "Si-Diode", "Schottky", "P-MOSFET"]


def verpolschutz(art, u_b, i_last, verpolt=False, r_ds=0.02):
    """
    Last = ohmscher Widerstand R_L = U_B / I_Nenn. Das Schutzelement liegt in der Plus-Leitung.
      Si-Diode / Schottky  Spannungsfall U_F, Verlust U_F · I, verpolt: sperrt
      P-MOSFET             Drain an Batterie +, Source zur Last, Gate an GND:
                           richtig gepolt U_GS = −U_B -> leitet, Spannungsfall I · R_DS(on)
                           verpolt: U_GS ≥ 0 -> sperrt, Body-Diode sperrt auch
      ohne Schutz          verpolt liegt −U_B an der Last
    """
    if art not in VERPOL_ARTEN:
        raise ValueError(f"Unbekannte Art: {art}")
    _positiv(U_B=u_b, I_Last=i_last)
    r_last = u_b / i_last
    e = {"art": art, "r_last": r_last, "gesperrt": False, "zerstoert": False, "gate_warnung": None}
    if verpolt:
        if art == "ohne Schutz":
            e.update(u_last=-u_b, i=-u_b / r_last, u_element=0.0, p_element=0.0, zerstoert=True)
        else:
            e.update(u_last=0.0, i=0.0, u_element=-u_b, p_element=0.0, gesperrt=True)
    elif art == "ohne Schutz":
        e.update(u_last=u_b, i=i_last, u_element=0.0, p_element=0.0)
    elif art == "P-MOSFET":
        _positiv(R_DS_on=r_ds)
        i = u_b / (r_last + r_ds)
        e.update(u_last=i * r_last, i=i, u_element=i * r_ds, p_element=i * i * r_ds)
    else:
        u_f = U_F_SI if art == "Si-Diode" else U_F_SCHOTTKY
        if u_b <= u_f:
            e.update(u_last=0.0, i=0.0, u_element=u_b, p_element=0.0)
        else:
            i = (u_b - u_f) / r_last
            e.update(u_last=u_b - u_f, i=i, u_element=u_f, p_element=u_f * i)
    if art == "P-MOSFET":
        if u_b > U_GS_MAX:
            e["gate_warnung"] = (f"U_GS = −{u_b:g} V überschreitet ±{U_GS_MAX:g} V → Z-Diode (z.B. 12 V) "
                                 "zwischen Gate und Source + Widerstand zum GND")
        elif u_b < 4.5:
            e["gate_warnung"] = "Unter ca. 4.5 V schaltet nur ein Logic-Level-P-MOSFET sicher durch (Datenblatt U_GS!)"
    e["wirkungsgrad"] = (e["u_last"] / u_b) if e["u_last"] > 0 else 0.0
    return e


# =============================================================================
# GLEICHRICHTER MIT LADEELKO
# =============================================================================
def gleichrichter(art, u2, i_last=None, c=None, f=50.0, u_f=U_F_SI):
    """
    u2 = Effektivwert der Trafo-Sekundärspannung (Mittelpunkt: EINE Wicklungshälfte).
      Brücke       2 Dioden im Strompfad, Brummfrequenz 2·f, Sperrspannung je Diode Û
      Einweg       1 Diode,                  Brummfrequenz f,   Sperrspannung 2·Û (Elko hält +Û)
      Mittelpunkt  1 Diode,                  Brummfrequenz 2·f, Sperrspannung 2·Û
    Welligkeit (Näherung: Elko entlädt sich linear mit I während einer ganzen Brummperiode):
      ΔU ≈ I / (f_Brumm · C)
      -> liegt auf der SICHEREN Seite: In Wirklichkeit wird ein Teil der Periode nachgeladen,
         die echte Welligkeit ist 5 … 35 % kleiner (siehe gleichrichter_kurve()).
    """
    if art not in GLEICHRICHTER:
        raise ValueError(f"Unbekannte Schaltung: {art}")
    _positiv(U2=u2, f=f)
    u_spitze = u2 * math.sqrt(2)
    n_dioden, f_brumm, u_sperr, anteil = {"Brücke": (2, 2 * f, u_spitze, 0.5),
                                          "Einweg": (1, f, 2 * u_spitze, 1.0),
                                          "Mittelpunkt": (1, 2 * f, 2 * u_spitze, 0.5)}[art]
    u_dc = u_spitze - n_dioden * u_f
    if u_dc <= 0:
        raise ValueError(f"U2 zu klein: Der Spitzenwert {u_spitze:.3g} V reicht nicht für die "
                         f"Durchlassspannung von {n_dioden} Diode(n)")
    e = {"art": art, "u_spitze": u_spitze, "u_dc": u_dc, "n_dioden": n_dioden, "f_brumm": f_brumm,
         "u_sperr": u_sperr, "i_diode": None, "ripple": None, "u_min": None}
    if i_last is not None:
        e["i_diode"] = i_last * anteil
        if c is not None:
            _positiv(C=c)
            e["ripple"] = i_last / (f_brumm * c)
            e["u_min"] = u_dc - e["ripple"]
    return e


def gleichrichter_kurve(art, u2, i_last, c, f=50.0, u_f=U_F_SI, perioden=2, schritte_pro_periode=400):
    """
    Zeitsimulation (eingeschwungen): Elko wird nachgeladen, wenn die gleichgerichtete Spannung
    über seiner Spannung liegt, sonst entlädt ihn die Last mit konstantem Strom I.
    Rückgabe: (quelle, ausgang, ripple_simuliert, u_min, i_laden)
              i_laden = MITTLERER Diodenstrom während des kurzen Nachladens (der Spitzenwert ist noch höher)
              quelle/ausgang = [(t 0…1, U)], über 'perioden' Netzperioden
    """
    e = gleichrichter(art, u2, i_last, c, f, u_f)
    u_hat, dt = e["u_spitze"], 1 / (f * schritte_pro_periode)
    v = e["u_dc"]
    quelle, ausgang = [], []
    gesamt = (perioden + 2) * schritte_pro_periode           # 2 Perioden Einschwingen
    nachladen = 0
    for k in range(gesamt):
        u = u_hat * math.sin(2 * math.pi * f * k * dt)
        if art == "Einweg":
            gleich = u - u_f
        elif art == "Brücke":
            gleich = abs(u) - 2 * u_f
        else:
            gleich = abs(u) - u_f
        v -= i_last / c * dt
        if gleich > v:
            v = gleich
            if k >= 2 * schritte_pro_periode:
                nachladen += 1
        v = max(v, 0.0)
        if k >= 2 * schritte_pro_periode:
            t = (k - 2 * schritte_pro_periode) / (perioden * schritte_pro_periode)
            quelle.append((t, u))
            ausgang.append((t, v))
    werte = [w for _, w in ausgang]
    ripple = max(werte) - min(werte)
    # Die Ladung, die die Last in einer Brummperiode entnimmt (I / f_Brumm), muss in der kurzen
    # Nachladezeit wieder hinein -> mittlerer Ladestrom = I · T_Brumm / t_Nachladen
    t_laden = nachladen * dt / (perioden * e["f_brumm"] / f)       # Nachladezeit pro Brummperiode
    i_laden = i_last / (e["f_brumm"] * t_laden) if t_laden > 0 else None
    return quelle, ausgang, ripple, min(werte), i_laden


# =============================================================================
# Z-DIODEN-STABILISIERUNG
# =============================================================================
def z_arbeitspunkt(u_e, r_v, u_z, r_l=None, r_z=5.0, i_z_min=1e-3):
    """
    Ue -- R_V --+-- Ua           Z-Diode als U_Z + r_z · I_Z (sobald sie leitet).
                |   |
               Z-D  R_L          Ersatzquelle aus Ue, R_V, R_L:  U_th = Ue · R_L / (R_V + R_L)
                |   |            leitet die Z-Diode nicht (U_th < U_Z): Ua = U_th
    """
    _positiv(R_V=r_v, U_Z=u_z)
    if u_e < 0:
        raise ValueError("Ue muss positiv sein (sonst leitet die Z-Diode in Durchlassrichtung)")
    if r_l is None:
        u_th, r_th = u_e, r_v
    else:
        _positiv(R_L=r_l)
        u_th, r_th = u_e * r_l / (r_v + r_l), r_v * r_l / (r_v + r_l)
    if u_th <= u_z:
        i_z, u_a = 0.0, u_th
    else:
        i_z = (u_th - u_z) / (r_th + r_z)
        u_a = u_z + r_z * i_z
    i_rv = (u_e - u_a) / r_v
    i_l = 0.0 if r_l is None else u_a / r_l
    return {"u_a": u_a, "i_z": i_z, "i_rv": i_rv, "i_l": i_l, "p_z": u_a * i_z, "p_rv": i_rv ** 2 * r_v,
            "stabil": i_z >= i_z_min, "leitet": i_z > 0}


# =============================================================================
# TVS-DIODE
# =============================================================================
def tvs_puls(t):
    """Normierte Stossspannung 1.2/50 µs (IEC 61000-4-5, Leerlauf), t in s, Maximum = 1."""
    t1, t2, k = 68.22e-6, 0.4074e-6, 1.037
    return max(0.0, k * (math.exp(-t / t1) - math.exp(-t / t2)))


def tvs(u_peak, r_q, u_wm, r_d=0.5, bidirektional=False, u_b=None, punkte=161, t_ende=120e-6):
    """
    Störquelle U_peak mit Innenwiderstand R_q (IEC 61000-4-5: 2 Ω Leitung-Leitung, 12/42 Ω gegen Erde).
    TVS-Modell:  ab U_BR ≈ 1.11 · U_WM leitet sie, mit differentiellem Widerstand r_d:
      I_Puls   = (U_peak − U_BR) / (R_q + r_d)
      U_Klemm  = U_BR + I_Puls · r_d          P_Spitze = U_Klemm · I_Puls
    u_peak < 0 (negative Spitze): unidirektional leitet wie eine normale Diode (−U_F − I · r_F, r_F klein),
                                  bidirektional klemmt symmetrisch bei −U_BR.
    U_WM (Stand-off) muss ≥ Betriebsspannung U_B sein, sonst leitet die TVS schon im Normalbetrieb.
    """
    _positiv(R_q=r_q, U_WM=u_wm, r_d=r_d)
    u_br = U_BR_FAKTOR * u_wm

    def klemmen(u):
        if u >= 0 or bidirektional:
            schwelle, r_diode = u_br, r_d                       # Durchbruch (Sperrrichtung)
        else:
            schwelle, r_diode = U_F_SI, R_F_TVS                 # Durchlassrichtung
        if abs(u) <= schwelle:
            return u, 0.0
        i = (abs(u) - schwelle) / (r_q + r_diode)
        return math.copysign(schwelle + i * r_diode, u), math.copysign(i, u)

    u_klemm, i_puls = klemmen(u_peak)
    ein, aus = [], []
    for k in range(punkte):
        t = k / (punkte - 1)
        u = u_peak * tvs_puls(t * t_ende)
        ein.append((t, u))
        aus.append((t, klemmen(u)[0]))
    return {"u_br": u_br, "u_klemm": u_klemm, "i_puls": i_puls, "p_spitze": abs(u_klemm * i_puls),
            "leitet": i_puls != 0, "betrieb_ok": u_b is None or u_b <= u_wm,
            "kurve_ein": ein, "kurve_aus": aus, "t_ende": t_ende}
