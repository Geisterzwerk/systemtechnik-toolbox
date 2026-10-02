# =============================================================================
# bauteile/rechner/halbleiter_rechner.py
# -----------------------------------------------------------------------------
# RECHNER für Diode, Z-Diode, LED, Bipolartransistor und MOSFET (Etappe 3).
#
#   diode_kennlinie       INTERAKTIV: Kennlinie + Arbeitsgerade (grafiken/halbleiter_grafiken.py)
#   zdiode_kennlinie      wie oben, startet mit der Z-Diode (volle Kennlinie, −Uz)
#   transistor_simulator  INTERAKTIV: Bipolartransistor als Schalter (NPN / PNP)  -> grafiken/schalter_simulator.py
#   mosfet_simulator      INTERAKTIV: MOSFET als Schalter (N- / P-Kanal)          -> grafiken/schalter_simulator.py
#   diode_temperatur      Uf bei anderer Temperatur (−2 mV/K)
#   diode_verlust         Verlustleistung und Sperrschichttemperatur
#   gleichrichter         Einweg / Brücke / Mittelpunkt mit Ladeelko
#   zdiode_stabi          Z-Dioden-Stabilisierung: Rv, Worst Case, Glättungsfaktor
#   bjt_schalter          Basiswiderstand für den Schalterbetrieb
#   bjt_arbeitspunkt      Emitterschaltung mit Basis-Spannungsteiler
#   mosfet_verlust        Leit- und Schaltverluste
#   mosfet_gate           Gate-Strom und Treiberleistung aus der Gate-Ladung
#   kuehlkoerper          Wärmekette: welcher Kühlkörper wird gebraucht?
#
# Grundlagen u.a. nach: Zastrow, Elektronik (Kap. 2 Diode, 3 Z-Diode, 5 Transistor)
# =============================================================================

from bauteile.grafiken.halbleiter_grafiken import DiodenKennlinie                       # -> grafiken/halbleiter_grafiken.py
from bauteile.grafiken.schalter_simulator import BjtSchalter, MosfetSchalter            # -> grafiken/schalter_simulator.py
from bauteile.rechner import normreihen                                                 # -> rechner/normreihen.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt                   # -> rechner/basis.py
from schaltungen import dioden_mathe as dm                                             # -> schaltungen/dioden_mathe.py
from schaltungen import verstaerker_mathe as vm                                        # -> schaltungen/verstaerker_mathe.py


def _standard(wert, standard):
    """Leeres optionales Feld -> Standardwert."""
    return standard if wert is None else wert


# =============================================================================
# DIODE
# =============================================================================
def _diode_temperatur(w):
    if w["Uf"] is None or w["T"] is None:
        raise RechnerFehler("Uf bei 25 °C und neue Temperatur eingeben")
    tk = _standard(w["tk"], -2e-3)                     # V/K
    uf_t = w["Uf"] + tk * (w["T"] - 25)
    return [f"Uf({w['T']:g} °C) = {fmt(uf_t, 'spannung')}",
            f"Änderung: {fmt(uf_t - w['Uf'], 'spannung')}  (TK = {tk * 1000:g} mV/K)",
            "Wärmer → kleinere Durchlassspannung. Nutzbar als einfacher Temperatursensor."]


def diode_temperatur(master):
    return FormelRechner(
        master, "Durchlassspannung & Temperatur", "Uf sinkt bei Silizium um ca. 2 mV pro Kelvin",
        felder=[("Uf", "Uf bei 25 °C", "spannung", {"platzhalter": "z.B. 0.7"}),
                ("T", "Temperatur", "temperatur", {"platzhalter": "z.B. 85"}),
                ("tk", "TK (optional)", "spannung", {"einheit": "mV", "platzhalter": "−2"})],
        berechnen=_diode_temperatur, formel="Uf(T) ≈ Uf(25 °C) + TK · (T − 25 °C),   TK ≈ −2 mV/K")


def _diode_verlust(w):
    if w["Uf"] is None or w["I"] is None:
        raise RechnerFehler("Uf und mittleren Strom eingeben")
    p = w["Uf"] * w["I"]
    zeilen = [f"Verlustleistung P ≈ Uf · I = {fmt(p, 'leistung')}"]
    if w["rth"] is not None:
        ta = _standard(w["Ta"], 25.0)
        tj = ta + p * w["rth"]
        zeilen.append(f"Sperrschicht Tj = Ta + P · Rth = {tj:.0f} °C")
        if tj > 125:
            zeilen.append("⚠ Über ca. 125 °C (typische Grenze, Datenblatt prüfen) → grössere Diode oder Kühlung")
    zeilen.append("Schottky statt Si halbiert oft die Verluste (kleineres Uf)")
    return zeilen


def diode_verlust(master):
    return FormelRechner(
        master, "Verlustleistung & Erwärmung", "Wie heiss wird die Diode?",
        felder=[("Uf", "Durchlassspannung Uf", "spannung", {"platzhalter": "z.B. 0.9"}),
                ("I", "Mittlerer Strom", "strom"),
                ("rth", "Rth,JA (optional)", "zahl", {"platzhalter": "K/W, z.B. 60"}),
                ("Ta", "Umgebung Ta", "temperatur", {"platzhalter": "25"})],
        berechnen=_diode_verlust, formel="P = Uf · I     Tj = Ta + P · Rth,JA")


GLEICHRICHTER = ["Brücke (4 Dioden)", "Einweg (1 Diode)", "Mittelpunkt (2 Dioden, Trafo mit Mittelanzapfung)"]


def _gleichrichter(w):
    U2, art = w["U2"], w["art"]
    if U2 is None:
        raise RechnerFehler("Trafospannung U2 (Effektivwert) eingeben")
    try:                                                      # Rechnung: schaltungen/dioden_mathe.py
        e = dm.gleichrichter(art.split()[0], U2, w["I"], w["C"], _standard(w["f"], 50.0), _standard(w["uf"], 0.7))
    except ValueError as fehler:
        raise RechnerFehler(str(fehler)) from None
    zeilen = [f"Û = U2 · √2 = {fmt(e['u_spitze'], 'spannung')}",
              f"Gleichspannung (Leerlauf, mit Elko): ≈ {fmt(e['u_dc'], 'spannung')}",
              f"Brummfrequenz: {fmt(e['f_brumm'], 'frequenz')}",
              f"Diode muss sperren können: mind. {fmt(e['u_sperr'], 'spannung')} → mit Reserve ≥ "
              f"{fmt(e['u_sperr'] * 1.5, 'spannung')}"]
    if e["i_diode"] is not None:
        zeilen.append(f"Mittlerer Strom pro Diode: {fmt(e['i_diode'], 'strom')}  "
                      f"(Spitzenstrom beim Nachladen ein Vielfaches davon!)")
        if e["ripple"] is not None:
            zeilen.append(f"Welligkeit ΔU ≈ I / (f_Brumm · C) = {fmt(e['ripple'], 'spannung')}  "
                          f"→ Minimum ≈ {fmt(e['u_min'], 'spannung')}")
    return zeilen


def gleichrichter(master):
    return FormelRechner(
        master, "Gleichrichter mit Ladeelko", "Einweg, Brücke oder Mittelpunkt im Vergleich",
        felder=[("art", "Schaltung", "auswahl", {"werte": GLEICHRICHTER}),
                ("U2", "Trafo U2 (eff)", "spannung", {"platzhalter": "z.B. 12"}),
                ("I", "Laststrom (opt.)", "strom", {"einheit": "mA", "platzhalter": "optional"}),
                ("C", "Ladeelko (opt.)", "kapazitaet", {"platzhalter": "optional"}),
                ("uf", "Uf pro Diode", "spannung", {"platzhalter": "0.7"}),
                ("f", "Netzfrequenz", "frequenz", {"platzhalter": "50"})],
        berechnen=_gleichrichter, formel="Û = U · √2     ΔU ≈ I / (f_Brumm · C)")


# =============================================================================
# Z-DIODE
# =============================================================================
def _zdiode(w):
    ue_min, ue_max, uz, il_max = w["Ue_min"], w["Ue_max"], w["Uz"], w["IL_max"]
    if None in (ue_min, uz, il_max):
        raise RechnerFehler("Mindestens Ue min, Uz und maximalen Laststrom eingeben")
    ue_max = _standard(ue_max, ue_min)
    il_min = _standard(w["IL_min"], 0.0)
    iz_min = _standard(w["Iz_min"], 5e-3)
    if ue_min <= uz:
        raise RechnerFehler("Ue min muss grösser als Uz sein – sonst kann die Z-Diode nicht stabilisieren")
    if ue_max < ue_min:
        raise RechnerFehler("Ue max muss mindestens Ue min sein")

    # 1) Rv so, dass bei KLEINSTER Eingangsspannung und GRÖSSTER Last noch Iz_min fliesst
    rv_max = (ue_min - uz) / (iz_min + il_max)
    rv = normreihen.naechste_werte(rv_max, "E24")[0]          # nächst KLEINERER Normwert
    # 2) Worst Case für die Z-Diode: GRÖSSTE Eingangsspannung, KLEINSTE Last
    i_rv_max = (ue_max - uz) / rv
    iz_max = i_rv_max - il_min
    pz = uz * iz_max
    p_rv = (ue_max - uz) ** 2 / rv
    zeilen = [f"Rv ≤ {fmt(rv_max, 'widerstand')}   →  E24: {fmt(rv, 'widerstand')}",
              f"Worst Case (Ue max, Last min): Iz = {fmt(iz_max, 'strom')}",
              f"Verlustleistung Z-Diode: Pz = {fmt(pz, 'leistung')}  → Typ mit ≥ {fmt(pz * 1.5, 'leistung')} wählen",
              f"Verlustleistung Rv: {fmt(p_rv, 'leistung')}  → Widerstand ≥ {fmt(p_rv * 2, 'leistung')}"]
    if w["Pz_max"] is not None and pz > w["Pz_max"]:
        zeilen.append("⚠ Z-Diode überlastet! Grössere Z-Diode oder Längsregler (Transistor / Spannungsregler)")
    if w["rz"] is not None and w["rz"] > 0:
        g = (rv + w["rz"]) / w["rz"]
        zeilen.append(f"Glättungsfaktor G = ΔUe/ΔUa = (Rv + rz)/rz ≈ {g:.0f}  "
                      f"(1 V Schwankung am Eingang → ca. {fmt(1 / g, 'spannung')} am Ausgang)")
    zeilen.append("Für mehr als ein paar mA Laststrom: besser Spannungsregler (LDO) verwenden")
    return zeilen


def zdiode_stabi(master):
    return FormelRechner(
        master, "Z-Dioden-Stabilisierung", "Vorwiderstand Rv und Belastung im ungünstigsten Fall",
        felder=[("Ue_min", "Ue min", "spannung", {"platzhalter": "z.B. 11"}),
                ("Ue_max", "Ue max (opt.)", "spannung", {"platzhalter": "z.B. 14"}),
                ("Uz", "Z-Spannung Uz", "spannung", {"platzhalter": "z.B. 5.1"}),
                ("IL_max", "Laststrom max", "strom", {"einheit": "mA"}),
                ("IL_min", "Laststrom min (opt.)", "strom", {"einheit": "mA", "platzhalter": "0"}),
                ("Iz_min", "Iz min (opt.)", "strom", {"einheit": "mA", "platzhalter": "5"}),
                ("Pz_max", "Pz max der Diode (opt.)", "leistung", {"einheit": "mW", "platzhalter": "z.B. 500"}),
                ("rz", "rz (opt., Datenblatt)", "widerstand", {"platzhalter": "z.B. 10"})],
        berechnen=_zdiode, formel="Rv = (Ue,min − Uz) / (Iz,min + IL,max)     Pz = Uz · Iz,max")


# =============================================================================
# BIPOLARTRANSISTOR
# =============================================================================
def _bjt_schalter(w):
    ub, ue, beta = w["Ub"], w["Ue"], w["beta"]
    if None in (ub, ue, beta):
        raise RechnerFehler("Ub, Ansteuerspannung und β (Minimum aus dem Datenblatt) eingeben")
    ube = _standard(w["Ube"], 0.7)
    k = _standard(w["k"], 3.0)
    uce_sat = 0.2
    if w["Ic"] is not None:
        ic = w["Ic"]
    elif w["RL"] is not None:
        ic = (ub - uce_sat) / w["RL"]
    else:
        raise RechnerFehler("Laststrom Ic ODER Lastwiderstand RL eingeben")
    if ue <= ube:
        raise RechnerFehler(f"Ansteuerspannung muss grösser als Ube ({fmt(ube, 'spannung')}) sein")
    ib_min = ic / beta
    ib = k * ib_min
    rb = (ue - ube) / ib
    rb_norm = normreihen.naechste_werte(rb, "E24")[0]          # kleiner = sicher durchgeschaltet
    ib_echt = (ue - ube) / rb_norm
    return [f"Ic = {fmt(ic, 'strom')}   Ib,min = Ic / β = {fmt(ib_min, 'strom')}",
            f"Mit Übersteuerung ×{k:g}: Ib = {fmt(ib, 'strom')}",
            f"Rb = (Ue − Ube) / Ib = {fmt(rb, 'widerstand')}  →  E24: {fmt(rb_norm, 'widerstand')}  "
            f"(Ib = {fmt(ib_echt, 'strom')})",
            f"Verlust im Transistor (voll an): ≈ Uce,sat · Ic = {fmt(uce_sat * ic, 'leistung')}",
            f"Strom aus der Ansteuerung (z.B. µC-Pin): {fmt(ib_echt, 'strom')} – Pin-Grenze beachten!",
            "Induktive Last (Relais, Motor)? → Freilaufdiode nicht vergessen"]


def bjt_schalter(master):
    return FormelRechner(
        master, "Transistor als Schalter: Basiswiderstand", "NPN, Last zwischen +Ub und Kollektor, Emitter an GND",
        felder=[("Ub", "Versorgung Ub", "spannung", {"platzhalter": "z.B. 12"}),
                ("RL", "Lastwiderstand RL", "widerstand", {"platzhalter": "oder Ic eingeben"}),
                ("Ic", "… oder Laststrom Ic", "strom", {"einheit": "mA", "platzhalter": "optional"}),
                ("Ue", "Ansteuerspannung", "spannung", {"platzhalter": "z.B. 3.3"}),
                ("beta", "β (hFE) minimal", "zahl", {"platzhalter": "z.B. 100"}),
                ("k", "Übersteuerung (opt.)", "zahl", {"platzhalter": "3"}),
                ("Ube", "Ube (opt.)", "spannung", {"platzhalter": "0.7"})],
        berechnen=_bjt_schalter, formel="Ib = k · Ic / β_min     Rb = (Ue − Ube) / Ib     (k = 2 … 5)")


def _bjt_arbeitspunkt(w):
    ub, r1, r2, rc, re, beta = w["Ub"], w["R1"], w["R2"], w["Rc"], w["Re"], w["beta"]
    if None in (ub, r1, r2, rc, beta):
        raise RechnerFehler("Ub, R1, R2, Rc und β eingeben (Re optional)")
    re = _standard(re, 0.0)
    try:                                                      # Rechnung: schaltungen/verstaerker_mathe.py
        e = vm.emitterschaltung(ub, r1, r2, rc, re, beta, _standard(w["Ube"], 0.7))
    except ValueError as fehler:
        raise RechnerFehler(str(fehler)) from None
    if e["zustand"] == "sperrt":
        return [f"Basisspannung {fmt(e['u_th'], 'spannung')} < Ube → Transistor SPERRT (Ic ≈ 0)"]
    zeilen = [f"U_Basis (Thevenin) = {fmt(e['u_th'], 'spannung')}   R_th = {fmt(e['r_th'], 'widerstand')}",
              f"Ib = {fmt(e['i_b'], 'strom')}   Ic = {fmt(e['i_c'], 'strom')}"]
    if e["zustand"] == "gesättigt":
        zeilen.append(f"⚠ Rechnerisch würde Uce unter 0.3 V fallen → Transistor ist GESÄTTIGT "
                      f"(Ic wird von Rc/Re auf ca. {fmt(e['i_c_sat'], 'strom')} begrenzt). "
                      "Als Verstärker ungeeignet: Basisspannung oder Rc verkleinern")
        return zeilen
    zeilen.append(f"Uce = Ub − Ic·Rc − Ie·Re = {fmt(e['u_ce'], 'spannung')}   (ideal ≈ Ub/2 = {fmt(ub / 2, 'spannung')})")
    zeilen.append(f"Verlust: P = Uce · Ic = {fmt(e['p_t'], 'leistung')}")
    if e["i_quer"] < 10 * e["i_b"]:
        zeilen.append(f"⚠ Querstrom durch den Teiler ({fmt(e['i_quer'], 'strom')}) < 10 · Ib → Arbeitspunkt hängt stark von β ab")
    if re > 0:
        zeilen.append(f"Spannungsverstärkung ohne C_E: Vu ≈ −Rc/Re = {-rc / re:.1f}  (stabil dank Gegenkopplung)")
        mit_ce = vm.emitterschaltung(ub, r1, r2, rc, re, beta, _standard(w["Ube"], 0.7), c_e=True)
        zeilen.append(f"Mit C_E (Re überbrückt): Vu ≈ −Rc / r_e = {mit_ce['vu']:.0f}   "
                      f"(r_e = 26 mV / Ie = {fmt(mit_ce['r_e_diff'], 'widerstand')}, hängt von Temperatur und Ic ab)")
    else:
        zeilen.append("Ohne Re: Arbeitspunkt driftet mit Temperatur und β → Re einbauen (Gegenkopplung)")
    zeilen.append(f"Eingangswiderstand ≈ {fmt(e['r_ein'], 'widerstand')}   ·   Ausgangswiderstand ≈ Rc = {fmt(rc, 'widerstand')}")
    return zeilen


def bjt_arbeitspunkt(master):
    return FormelRechner(
        master, "Arbeitspunkt Emitterschaltung", "Basisspannungsteiler R1 (oben) / R2 (unten), Rc, Re",
        felder=[("Ub", "Versorgung Ub", "spannung"), ("R1", "R1 (oben)", "widerstand", {"einheit": "kΩ"}),
                ("R2", "R2 (unten)", "widerstand", {"einheit": "kΩ"}), ("Rc", "Rc", "widerstand", {"einheit": "kΩ"}),
                ("Re", "Re (opt.)", "widerstand", {"platzhalter": "optional"}),
                ("beta", "β (hFE)", "zahl", {"platzhalter": "z.B. 200"}),
                ("Ube", "Ube (opt.)", "spannung", {"platzhalter": "0.7"})],
        berechnen=_bjt_arbeitspunkt, formel="Ib = (U_th − Ube) / (R_th + (β+1)·Re)     Uce = Ub − Ic·Rc − Ie·Re")


# =============================================================================
# MOSFET
# =============================================================================
def _mosfet_verlust(w):
    i, rds = w["I"], w["Rds"]
    if i is None or rds is None:
        raise RechnerFehler("Strom und Rds(on) eingeben")
    faktor = _standard(w["faktor"], 1.5)
    p_leit = i * i * rds * faktor
    zeilen = [f"Leitverluste P = I² · Rds(on) · Faktor = {fmt(p_leit, 'leistung')}  "
              f"(Rds heiss ≈ {fmt(rds * faktor, 'widerstand')})"]
    p_total = p_leit
    if None not in (w["U"], w["f"], w["t"]):
        p_sw = 0.5 * w["U"] * i * w["t"] * w["f"]
        p_total += p_sw
        zeilen.append(f"Schaltverluste ≈ ½ · U · I · (tr + tf) · f = {fmt(p_sw, 'leistung')}")
    zeilen.append(f"Total ≈ {fmt(p_total, 'leistung')}  → Kühlung mit dem Kühlkörper-Rechner prüfen")
    if w["f"] is not None and w["t"] is None:
        zeilen.append("Für Schaltverluste zusätzlich die Schaltzeit (tr + tf) eingeben")
    return zeilen


def mosfet_verlust(master):
    return FormelRechner(
        master, "MOSFET: Verlustleistung", "Leitverluste + Schaltverluste bei PWM",
        felder=[("I", "Drainstrom I (eff)", "strom"),
                ("Rds", "Rds(on) bei 25 °C", "widerstand", {"einheit": "mΩ"}),
                ("faktor", "Faktor heiss (opt.)", "zahl", {"platzhalter": "1.5"}),
                ("U", "Schaltspannung (opt.)", "spannung", {"platzhalter": "für PWM"}),
                ("f", "PWM-Frequenz (opt.)", "frequenz", {"einheit": "kHz", "platzhalter": "für PWM"}),
                ("t", "tr + tf (opt.)", "zeit", {"einheit": "ns", "platzhalter": "z.B. 100"})],
        berechnen=_mosfet_verlust, formel="P_leit = I² · Rds(on)     P_schalt ≈ ½ · U · I · (tr + tf) · f")


def _mosfet_gate(w):
    qg, ugs = w["Qg"], w["Ugs"]
    if qg is None or ugs is None:
        raise RechnerFehler("Gate-Ladung Qg und Treiberspannung eingeben")
    zeilen = []
    if w["t"] is not None:
        ig = qg / w["t"]
        zeilen.append(f"Gate-Strom für {fmt(w['t'], 'zeit')} Schaltzeit: Ig = Qg / t = {fmt(ig, 'strom')}")
        zeilen.append(f"Gate-Widerstand grob: Rg ≈ Ugs / Ig = {fmt(ugs / ig, 'widerstand')}")
        if ig > 0.02:
            zeilen.append("⚠ Mehr als ein µC-Pin liefert (ca. 10–20 mA) → Gate-Treiber-IC verwenden")
    if w["f"] is not None:
        zeilen.append(f"Treiberleistung P = Qg · Ugs · f = {fmt(qg * ugs * w['f'], 'leistung')}")
        zeilen.append(f"Mittlerer Treiberstrom = Qg · f = {fmt(qg * w['f'], 'strom')}")
    if not zeilen:
        raise RechnerFehler("Zusätzlich Schaltzeit und/oder Frequenz eingeben")
    return zeilen


def mosfet_gate(master):
    return FormelRechner(
        master, "MOSFET: Gate-Ansteuerung", "Das Gate ist ein Kondensator – umladen kostet Strom",
        felder=[("Qg", "Gate-Ladung Qg", "ladung", {"einheit": "nC", "platzhalter": "Datenblatt"}),
                ("Ugs", "Treiberspannung Ugs", "spannung", {"platzhalter": "z.B. 10"}),
                ("t", "Schaltzeit (opt.)", "zeit", {"einheit": "ns", "platzhalter": "z.B. 100"}),
                ("f", "PWM-Frequenz (opt.)", "frequenz", {"einheit": "kHz", "platzhalter": "optional"})],
        berechnen=_mosfet_gate, formel="Ig = Qg / t     P_Treiber = Qg · Ugs · f")


# =============================================================================
# KÜHLKÖRPER (für alle Leistungshalbleiter)
# =============================================================================
def _kuehlkoerper(w):
    p, tj, ta, rjc = w["P"], w["Tj"], w["Ta"], w["Rjc"]
    if None in (p, rjc):
        raise RechnerFehler("Verlustleistung und Rth,JC eingeben")
    tj = _standard(tj, 125.0)
    ta = _standard(ta, 40.0)
    rcs = _standard(w["Rcs"], 0.5)
    r_total = (tj - ta) / p
    r_sa = r_total - rjc - rcs
    zeilen = [f"Erlaubt total: Rth = (Tj − Ta) / P = {r_total:.2f} K/W",
              f"Davon Chip→Gehäuse {rjc:g} K/W + Gehäuse→Kühlkörper {rcs:g} K/W"]
    if r_sa <= 0:
        zeilen.append("⚠ Auch mit idealem Kühlkörper zu heiss → Verluste senken oder mehrere Bauteile parallel")
    else:
        zeilen.append(f"Kühlkörper nötig: Rth,SA ≤ {r_sa:.2f} K/W  (mit Reserve ≤ {r_sa * 0.8:.2f} K/W)")
    if w["Rja"] is not None:
        tj_ohne = ta + p * w["Rja"]
        zeilen.append(f"Ohne Kühlkörper: Tj = {tj_ohne:.0f} °C  → " +
                      ("reicht ✅" if tj_ohne < tj else "zu heiss ❌"))
    return zeilen


def kuehlkoerper(master):
    return FormelRechner(
        master, "Kühlkörper auslegen", "Wärme fliesst wie Strom: Temperatur = Leistung × Wärmewiderstand",
        felder=[("P", "Verlustleistung P", "leistung"),
                ("Tj", "Tj max (opt.)", "temperatur", {"platzhalter": "125 (mit Reserve)"}),
                ("Ta", "Umgebung Ta (opt.)", "temperatur", {"platzhalter": "40"}),
                ("Rjc", "Rth,JC (Datenblatt)", "zahl", {"platzhalter": "K/W"}),
                ("Rcs", "Rth,CS (opt.)", "zahl", {"platzhalter": "0.5 K/W (Paste)"}),
                ("Rja", "Rth,JA ohne KK (opt.)", "zahl", {"platzhalter": "K/W"})],
        berechnen=_kuehlkoerper, formel="Tj = Ta + P · (Rth,JC + Rth,CS + Rth,SA)")


# =============================================================================
# REGISTRIERUNG
# =============================================================================
RECHNER = {
    "diode_kennlinie": DiodenKennlinie,
    "zdiode_kennlinie": lambda master: DiodenKennlinie(master, start_typ="Z-Diode 5.1 V"),
    "transistor_simulator": BjtSchalter,
    "mosfet_simulator": MosfetSchalter,
    "diode_temperatur": diode_temperatur,
    "diode_verlust": diode_verlust,
    "gleichrichter": gleichrichter,
    "zdiode_stabi": zdiode_stabi,
    "bjt_schalter": bjt_schalter,
    "bjt_arbeitspunkt": bjt_arbeitspunkt,
    "mosfet_verlust": mosfet_verlust,
    "mosfet_gate": mosfet_gate,
    "kuehlkoerper": kuehlkoerper,
}
