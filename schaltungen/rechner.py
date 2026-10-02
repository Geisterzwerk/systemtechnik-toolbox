# =============================================================================
# schaltungen/rechner.py
# -----------------------------------------------------------------------------
# RECHNER des Bereichs Schaltungen + Registrierung der interaktiven Schaltpläne.
#
#   stromteiler          Zweigströme beliebig vieler paralleler Widerstände
#   pull_widerstand      Pull-up/-down dimensionieren: R_min (Strom), R_max (Leckstrom, Flanke)
#   poti_last            Fehler eines belasteten Potentiometers
#   eingangsschutz       Serienwiderstand vor einem IC-Eingang (Injektionsstrom begrenzen)
#   verpolschutz         Si-Diode, Schottky und P-MOSFET im Vergleich
#   tvs_auswahl          passt eine TVS-Diode zu Betriebsspannung und Störimpuls?
#   emitterfolger        Kollektorschaltung: Ua, Ströme, Ein-/Ausgangswiderstand
#   konstantstrom        Konstantstromquelle mit Transistor + Z-Diode oder JFET + R_S dimensionieren
#   schaltung_*          INTERAKTIVE Schaltpläne (schaltungen/grafiken.py)
#
# Spannungsteiler und Brücke gibt es schon (widerstand_rechner.py, messtechnik/rechner.py)
# -> die Seiten benutzen diese Rechner per ID, hier wird nichts kopiert.
#
# Rechnung: schaltungen/netzwerk_mathe.py, dioden_mathe.py, verstaerker_mathe.py (ohne GUI, testbar)
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py (_MODULE) -> erstellen(master, "stromteiler")
# =============================================================================

from bauteile.rechner import normreihen                                          # -> bauteile/rechner/normreihen.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt             # -> bauteile/rechner/basis.py
from schaltungen import dioden_mathe as dm                                       # -> schaltungen/dioden_mathe.py
from schaltungen import netzwerk_mathe as nm                                     # -> schaltungen/netzwerk_mathe.py
from schaltungen import verstaerker_mathe as vm                                  # -> schaltungen/verstaerker_mathe.py
from schaltungen.grafiken_transistor import (EmitterfolgerSchaltung, EmitterSchaltung,  # -> schaltungen/grafiken_transistor.py
                                             KonstantstromSchaltung, LastTreiberSchaltung)
from schaltungen.grafiken_dioden import (BegrenzerSchaltung, EingangsschutzSchaltung,   # -> schaltungen/grafiken_dioden.py
                                         FreilaufSchaltung, GleichrichterSchaltung, TvsSchaltung,
                                         VerpolSchaltung, ZStabiSchaltung)
from schaltungen.grafiken import (BrueckeSchaltung, PotiSchaltung,               # -> schaltungen/grafiken.py
                                  PullSchaltung, SpannungsteilerSchaltung, StromteilerSchaltung)


def _fehler_umwandeln(funktion, *args):
    """ValueError aus netzwerk_mathe.py als verständliche Meldung im Ergebnisfeld zeigen."""
    try:
        return funktion(*args)
    except ValueError as fehler:
        raise RechnerFehler(str(fehler)) from None


# =============================================================================
# 1) STROMTEILER
# =============================================================================
def _stromteiler(w):
    if w["I"] is None or not w["liste"]:
        raise RechnerFehler("Gesamtstrom und mindestens zwei Widerstände eingeben, z.B.  100 300")
    if len(w["liste"]) < 2:
        raise RechnerFehler("Für einen Stromteiler mindestens zwei Widerstände eingeben")
    e = _fehler_umwandeln(nm.stromteiler, w["I"], *w["liste"])
    zeilen = [f"R_ges = {fmt(e['r_ges'], 'widerstand')}   ·   U = I · R_ges = {fmt(e['u'], 'spannung')}"]
    for nummer, (r, i, p) in enumerate(zip(w["liste"], e["stroeme"], e["leistungen"]), start=1):
        zeilen.append(f"I{nummer} = U / {fmt(r, 'widerstand')} = {fmt(i, 'strom')}  "
                      f"({i / w['I'] * 100:.1f} %),  P = {fmt(p, 'leistung')}")
    return zeilen


def stromteiler(master):
    return FormelRechner(
        master, "Stromteiler", "Wie teilt sich ein Strom auf parallele Zweige auf?",
        felder=[("I", "Gesamtstrom I", "strom", {"einheit": "mA"}),
                ("liste", "Zweig-Widerstände", "widerstand", {"liste": True, "platzhalter": "100 300"})],
        berechnen=_stromteiler, formel="I_k = I · R_ges / R_k     zwei Zweige: I1 = I · R2 / (R1 + R2)")


# =============================================================================
# 2) PULL-UP / PULL-DOWN DIMENSIONIEREN
# =============================================================================
def _pull(w):
    ub, i_max = w["Ub"], w["Imax"]
    if ub is None or i_max is None:
        raise RechnerFehler("U_B und den erlaubten Strom bei gedrücktem Taster eingeben")
    if ub <= 0 or i_max <= 0:
        raise RechnerFehler("U_B und Strom müssen grösser als 0 sein")
    r_min = ub / i_max
    zeilen = [f"R_min = U_B / I_max = {fmt(r_min, 'widerstand')}   (sonst zu viel Strom beim Drücken)"]
    grenzen = []
    if w["Ileck"]:
        r_leck = (1 - nm.HIGH_ANTEIL) * ub / w["Ileck"]
        grenzen.append(r_leck)
        zeilen.append(f"R_max (Leckstrom) = 0.3 · U_B / I_leck = {fmt(r_leck, 'widerstand')}   "
                      "(Pegel bleibt sicher über 0.7 · U_B)")
    if w["C"] and w["tr"]:
        r_flanke = w["tr"] / (w["C"] * nm.LOG_9)
        grenzen.append(r_flanke)
        zeilen.append(f"R_max (Flanke) = t_r / (2.2 · C) = {fmt(r_flanke, 'widerstand')}")
    elif w["C"] or w["tr"]:
        zeilen.append("Für die Flanke C UND t_r eingeben")
    r_max = min(grenzen) if grenzen else None
    if r_max is not None and r_max < r_min:
        raise RechnerFehler(f"Kein Widerstand passt: R_min {fmt(r_min, 'widerstand')} > R_max "
                            f"{fmt(r_max, 'widerstand')} → mehr Strom erlauben oder Leckstrom/Kapazität senken")
    # Vorschlag: geometrische Mitte zwischen den Grenzen, als E12-Wert, der sicher innerhalb liegt
    ziel = (r_min * r_max) ** 0.5 if r_max else max(r_min * 10, 4.7e3)
    vorschlag = normreihen.naechste_werte(ziel, "E12")[2]
    if r_max:
        unten = normreihen.naechste_werte(r_min, "E12")[1]          # nächst GRÖSSERER Normwert
        oben = normreihen.naechste_werte(r_max, "E12")[0]           # nächst KLEINERER Normwert
        vorschlag = min(max(vorschlag, unten), oben) if unten <= oben else None
    if vorschlag is None:
        zeilen.append("Kein E12-Wert liegt dazwischen → E24/E96 verwenden oder Grenzen lockern")
    else:
        zeilen.append(f"Vorschlag (E12): {fmt(vorschlag, 'widerstand')}  →  Strom gedrückt "
                      f"{fmt(ub / vorschlag, 'strom')}, Verlust {fmt(ub * ub / vorschlag, 'leistung')}")
    zeilen.append("Typisch: Taster 4.7 … 47 kΩ · I²C 1 … 10 kΩ · interne µC-Pull-ups ca. 20 … 50 kΩ")
    return zeilen


def pull_widerstand(master):
    return FormelRechner(
        master, "Pull-up / Pull-down dimensionieren", "Grenzen für R aus Strom, Leckstrom und Flanke",
        felder=[("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 3.3"}),
                ("Imax", "Strom gedrückt max.", "strom", {"einheit": "mA", "platzhalter": "z.B. 1"}),
                ("Ileck", "Leckstrom (opt.)", "strom", {"einheit": "µA", "platzhalter": "Datenblatt, z.B. 1"}),
                ("C", "Kapazität (opt.)", "kapazitaet", {"einheit": "pF", "platzhalter": "Pin + Leitung"}),
                ("tr", "Flanke t_r max (opt.)", "zeit", {"einheit": "µs", "platzhalter": "10 → 90 %"})],
        berechnen=_pull, formel="R_min = U_B / I_max     R_max = 0.3 · U_B / I_leck     R_max = t_r / (2.2 · C)")


# =============================================================================
# 3) POTENTIOMETER MIT LAST
# =============================================================================
def _poti(w):
    if None in (w["Ue"], w["Rp"], w["RL"]):
        raise RechnerFehler("Ue, R_P und R_L eingeben")
    anteil = 0.5 if w["a"] is None else w["a"]
    e = _fehler_umwandeln(nm.poti_teiler, w["Ue"], w["Rp"], anteil, w["RL"])
    kurve = nm.poti_kennlinie(w["Rp"], w["RL"], punkte=101)
    groesster = min(kurve, key=lambda k: k[1] - k[0])               # grösste Abweichung nach unten
    zeilen = [f"Bei {anteil * 100:g} %: Ua = {fmt(e['ua'], 'spannung')}  (ohne Last {fmt(e['ua0'], 'spannung')}, "
              f"Fehler {fmt(e['fehler'], 'spannung')})",
              f"Grösster Fehler bei ca. {groesster[0] * 100:.0f} %: {(groesster[1] - groesster[0]) * 100:+.1f} % von Ue",
              f"R_L / R_P = {w['RL'] / w['Rp']:.3g}   ·   Laststrom {fmt(e['i_last'], 'strom')}"]
    if w["RL"] < 10 * w["Rp"]:
        zeilen.append("⚠ R_L < 10 · R_P → kleineres Poti oder Spannungsfolger (OPV) dazwischen")
    return zeilen


def poti_last(master):
    return FormelRechner(
        master, "Potentiometer mit Last", "Wie stark verbiegt eine Last die Poti-Kennlinie?",
        felder=[("Ue", "Eingang Ue", "spannung", {"platzhalter": "z.B. 10"}),
                ("Rp", "Poti R_P", "widerstand", {"einheit": "kΩ"}),
                ("RL", "Last R_L", "widerstand", {"einheit": "kΩ"}),
                ("a", "Schleiferstellung", "prozent", {"platzhalter": "50"})],
        berechnen=_poti, formel="Ua = Ue · (R_u || R_L) / (R_o + R_u || R_L),   R_u = α · R_P")


# =============================================================================
# 4) EINGANGSSCHUTZ
# =============================================================================
def _eingangsschutz(w):
    u_max, u_dd = w["Umax"], w["Udd"]
    if None in (u_max, u_dd):
        raise RechnerFehler("Grösste Spannung am Eingang und U_DD eingeben")
    i_inj = 1e-3 if w["Iinj"] is None else w["Iinj"]
    u_f = dm.U_F_SI if w["Uf"] is None else w["Uf"]
    if i_inj <= 0 or u_dd <= 0:
        raise RechnerFehler("U_DD und Injektionsstrom müssen grösser als 0 sein")
    u_min = w["Umin"]
    grenzen, zeilen = [], []
    if u_max > u_dd + u_f:
        r_pos = (u_max - u_dd - u_f) / i_inj
        grenzen.append(r_pos)
        zeilen.append(f"Positiv: R ≥ (U_max − U_DD − U_F) / I_inj = {fmt(r_pos, 'widerstand')}")
    if u_min is not None and u_min < -u_f:
        r_neg = (-u_min - u_f) / i_inj
        grenzen.append(r_neg)
        zeilen.append(f"Negativ: R ≥ (|U_min| − U_F) / I_inj = {fmt(r_neg, 'widerstand')}")
    if not grenzen:
        return ["Die Spannung bleibt zwischen −U_F und U_DD + U_F – die Schutzdioden leiten nie.",
                "Ein Serienwiderstand (z.B. 1 kΩ) schützt trotzdem gegen ESD und Verdrahtungsfehler."]
    r_min = max(grenzen)
    r = normreihen.naechste_werte(r_min, "E12")[1]                   # nächst GRÖSSERER Normwert
    zeilen.append(f"→ R ≥ {fmt(r_min, 'widerstand')}   E12: {fmt(r, 'widerstand')}")
    u_r = max(u_max - u_dd - u_f, (-u_min - u_f) if u_min is not None else 0.0)
    zeilen.append(f"Dauerleistung im Widerstand: {fmt(u_r * u_r / r, 'leistung')}  (bei anhaltender Überspannung)")
    zeilen.append("Für ADC-Eingänge: grosses R verfälscht die Messung → Kondensator direkt am Pin "
                  "oder externe Schottky-/TVS-Dioden und kleineres R")
    return zeilen


def eingangsschutz(master):
    return FormelRechner(
        master, "Eingangsschutz: Serienwiderstand", "Wie gross muss R sein, damit die Klemmdioden überleben?",
        felder=[("Umax", "Grösste Spannung am Eingang", "spannung", {"platzhalter": "z.B. 24"}),
                ("Umin", "Kleinste Spannung (opt.)", "spannung", {"platzhalter": "z.B. −24"}),
                ("Udd", "Versorgung U_DD", "spannung", {"platzhalter": "z.B. 3.3"}),
                ("Iinj", "Injektionsstrom max.", "strom", {"einheit": "mA", "platzhalter": "Datenblatt, leer = 1"}),
                ("Uf", "U_F der Dioden (opt.)", "spannung", {"platzhalter": "0.7 (Schottky 0.3)"})],
        berechnen=_eingangsschutz, formel="R ≥ (U_max − U_DD − U_F) / I_inj")


# =============================================================================
# 5) VERPOLSCHUTZ IM VERGLEICH
# =============================================================================
def _verpolschutz(w):
    if w["Ub"] is None or w["I"] is None:
        raise RechnerFehler("Batteriespannung und Laststrom eingeben")
    r_ds = 0.02 if w["Rds"] is None else w["Rds"]
    zeilen = []
    for art in dm.VERPOL_ARTEN[1:]:
        e = _fehler_umwandeln(dm.verpolschutz, art, w["Ub"], w["I"], False, r_ds)
        zeilen.append(f"{art}: ΔU = {fmt(e['u_element'], 'spannung')},  P = {fmt(e['p_element'], 'leistung')},  "
                      f"Last bekommt {fmt(e['u_last'], 'spannung')} ({e['wirkungsgrad'] * 100:.1f} %)")
        if e["gate_warnung"]:
            zeilen.append("⚠ " + e["gate_warnung"])
    zeilen.append("Verpolt sperren alle drei. Sperrspannung des Bauteils ≥ U_B wählen (mit Reserve).")
    return zeilen


def verpolschutz(master):
    return FormelRechner(
        master, "Verpolschutz im Vergleich", "Si-Diode, Schottky oder P-MOSFET in der Plusleitung?",
        felder=[("Ub", "Batterie U_B", "spannung", {"platzhalter": "z.B. 12"}),
                ("I", "Laststrom (Nenn)", "strom", {"einheit": "A"}),
                ("Rds", "R_DS(on) P-MOSFET", "widerstand", {"einheit": "mΩ", "platzhalter": "leer = 20"})],
        berechnen=_verpolschutz, formel="Diode: P = U_F · I     P-MOSFET: P = I² · R_DS(on)")


# =============================================================================
# 6) TVS-DIODE PRÜFEN
# =============================================================================
def _tvs(w):
    ub, uwm, uc, ipp, up = w["Ub"], w["Uwm"], w["Uc"], w["Ipp"], w["Up"]
    if None in (ub, uwm, uc, ipp, up):
        raise RechnerFehler("U_B, U_WM, U_C und I_PP (Datenblatt) sowie die Störspitze eingeben")
    rq = 2.0 if w["Rq"] is None else w["Rq"]
    if min(ub, uwm, uc, ipp, rq) <= 0:
        raise RechnerFehler("Alle Werte müssen grösser als 0 sein")
    if uc <= uwm:
        raise RechnerFehler("U_C (Klemmspannung) liegt immer über U_WM – Datenblattwerte prüfen")
    zeilen = []
    if uwm < ub:
        zeilen.append(f"❌ U_WM {fmt(uwm, 'spannung')} < U_B {fmt(ub, 'spannung')}: Die TVS leitet schon im Betrieb")
    elif uwm < 1.1 * ub:
        zeilen.append(f"⚠ U_WM nur {(uwm / ub - 1) * 100:.0f} % über U_B – Toleranz der Versorgung (+10 %) beachten")
    else:
        zeilen.append(f"✅ U_WM {fmt(uwm, 'spannung')} ≥ 1.1 · U_B – sperrt im Betrieb sicher")
    i_puls = max(0.0, (up - uc) / rq)
    zeilen.append(f"Pulsstrom ≈ (U_peak − U_C) / R_q = {fmt(i_puls, 'strom')}   (Datenblatt I_PP = {fmt(ipp, 'strom')})")
    zeilen.append(f"Spitzenleistung ≈ U_C · I = {fmt(uc * i_puls, 'leistung')}")
    if i_puls == 0:
        zeilen.append("Die Störspitze liegt unter U_C – die TVS wird kaum belastet")
    elif i_puls > ipp:
        zeilen.append("❌ Pulsstrom grösser als I_PP → grössere TVS, Vorwiderstand oder Vorstufe (Varistor)")
    else:
        zeilen.append(f"✅ Pulsstrom unter I_PP (Reserve {ipp / i_puls:.1f}×)")
    if w["Umax"] is not None:
        passt = uc <= w["Umax"]
        zeilen.append(("✅" if passt else "❌") + f" Klemmspannung U_C {fmt(uc, 'spannung')} "
                      + ("≤" if passt else ">") + f" U_max des Geräts {fmt(w['Umax'], 'spannung')}")
    zeilen.append("I_PP gilt für eine bestimmte Pulsform (meist 10/1000 µs) – mit der erwarteten Störung vergleichen")
    return zeilen


def tvs_auswahl(master):
    return FormelRechner(
        master, "TVS-Diode prüfen", "Passt die TVS zu Betriebsspannung, Störspitze und Gerät?",
        felder=[("Ub", "Betriebsspannung U_B", "spannung", {"platzhalter": "z.B. 24"}),
                ("Uwm", "TVS U_WM (Stand-off)", "spannung", {"platzhalter": "Datenblatt, z.B. 26"}),
                ("Uc", "TVS U_C bei I_PP", "spannung", {"platzhalter": "Datenblatt, z.B. 42.1"}),
                ("Ipp", "TVS I_PP", "strom", {"einheit": "A", "platzhalter": "Datenblatt, z.B. 14.3"}),
                ("Up", "Störspitze U_peak", "spannung", {"platzhalter": "z.B. 500"}),
                ("Rq", "Quellwiderstand R_q", "widerstand", {"platzhalter": "leer = 2 Ω (Norm)"}),
                ("Umax", "U_max des Geräts (opt.)", "spannung", {"platzhalter": "optional"})],
        berechnen=_tvs, formel="U_WM ≥ U_B     I ≈ (U_peak − U_C) / R_q ≤ I_PP     U_C ≤ U_max")

# =============================================================================
# 7) EMITTERFOLGER
# =============================================================================
def _emitterfolger(w):
    if None in (w["Ub"], w["Ue"], w["Re"]):
        raise RechnerFehler("U_B, Eingangsspannung und R_E eingeben")
    beta = 200.0 if w["beta"] is None else w["beta"]
    e = _fehler_umwandeln(vm.emitterfolger, w["Ub"], w["Ue"], w["Re"], w["RL"], beta)
    if not e["leitet"]:
        raise RechnerFehler("Ue unter 0.7 V – der Transistor sperrt, Ausgang 0 V")
    zeilen = [f"Ua = Ue − 0.7 V = {fmt(e['u_a'], 'spannung')}" + ("  (oben begrenzt)" if e["begrenzt"] else ""),
              f"I_E = Ua / (R_E || R_L) = {fmt(e['i_e'], 'strom')}   ·   I_B = I_E / (β + 1) = {fmt(e['i_b'], 'strom')}",
              f"Vu = {e['vu']:.3f}   ·   r_ein ≈ (β + 1) · (r_e + R) = {fmt(e['r_ein'], 'widerstand')}   ·   "
              f"r_aus ≈ r_e = {fmt(e['r_aus'], 'widerstand')}",
              f"Verlust im Transistor: (U_B − Ua) · I_E = {fmt(e['p_t'], 'leistung')}"]
    if e["p_t"] > 0.5:
        zeilen.append("⚠ Über 0.5 W – TO-92 ist überfordert → Leistungstransistor mit Kühlkörper")
    return zeilen


def emitterfolger(master):
    return FormelRechner(
        master, "Emitterfolger", "Kollektorschaltung als Impedanzwandler",
        felder=[("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 12"}),
                ("Ue", "Eingang (Basis)", "spannung", {"platzhalter": "z.B. 6"}),
                ("Re", "R_E", "widerstand", {"einheit": "kΩ"}),
                ("RL", "Last R_L (opt.)", "widerstand", {"platzhalter": "optional"}),
                ("beta", "β (opt.)", "zahl", {"platzhalter": "200"})],
        berechnen=_emitterfolger, formel="Ua = Ue − 0.7 V     I_B = I_E / (β + 1)     r_ein ≈ β · R_E")


# =============================================================================
# 8) KONSTANTSTROMQUELLE
# =============================================================================
KONSTANT_ARTEN = ["Transistor + Z-Diode (oder LED / 2 Dioden)", "JFET mit Source-Widerstand"]


def _konstantstrom(w):
    i_soll, ub = w["I"], w["Ub"]
    if i_soll is None or ub is None:
        raise RechnerFehler("Gewünschten Strom und U_B eingeben")
    if i_soll <= 0 or ub <= 0:
        raise RechnerFehler("Strom und U_B müssen grösser als 0 sein")
    if w["art"] == KONSTANT_ARTEN[0]:
        u_ref = w["Uref"]
        if u_ref is None:
            raise RechnerFehler("Referenzspannung an der Basis eingeben (Z-Diode, 2 Dioden ≈ 1.4 V, rote LED ≈ 1.8 V)")
        if u_ref <= vm.U_BE:
            raise RechnerFehler("U_ref muss über 0.7 V liegen")
        r_e = (u_ref - vm.U_BE) / i_soll
        r_norm = normreihen.naechste_werte(r_e, "E24")[2]
        e = _fehler_umwandeln(vm.konstantstrom_bjt, ub, u_ref, r_norm, 0.0)
        return [f"R_E = (U_ref − 0.7 V) / I = {fmt(r_e, 'widerstand')}   →  E24: {fmt(r_norm, 'widerstand')} "
                f"(I = {fmt(e['i'], 'strom')})",
                f"Konstant bis zu einer Lastspannung von {fmt(e['u_last_max'], 'spannung')} "
                f"(R_L ≤ {fmt(e['r_last_max'], 'widerstand')})",
                f"Verlust im Transistor bei Kurzschluss der Last: {fmt(e['p_t'], 'leistung')}",
                "Z-Diode über einen Widerstand von U_B speisen (I_Z ≈ 1 … 5 mA); Dioden/LED driften mit −2 mV/K"]
    if w["IDSS"] is None or w["UP"] is None:
        raise RechnerFehler("I_DSS und |U_P| aus dem Datenblatt eingeben (streuen stark – Exemplar messen!)")
    r_s, u_gs = _fehler_umwandeln(vm.r_s_fuer_jfet, i_soll, w["IDSS"], abs(w["UP"]))
    r_norm = normreihen.naechste_werte(r_s, "E24")[2] if r_s > 0 else 0.0
    e = _fehler_umwandeln(vm.konstantstrom_jfet, ub, w["IDSS"], abs(w["UP"]), r_norm, 0.0)
    return [f"U_GS = −U_P · (1 − √(I / I_DSS)) = {fmt(u_gs, 'spannung')}",
            f"R_S = |U_GS| / I = {fmt(r_s, 'widerstand')}   →  E24: {fmt(r_norm, 'widerstand')} (I = {fmt(e['i'], 'strom')})",
            f"Konstant bis zu einer Lastspannung von {fmt(e['u_last_max'], 'spannung')} (U_B − |U_P|)",
            "Nur 2 Anschlüsse nötig – aber I_DSS und U_P streuen pro Exemplar oft um Faktor 2"]


def konstantstrom(master):
    return FormelRechner(
        master, "Konstantstromquelle dimensionieren", "Transistor + Referenz oder JFET + R_S",
        felder=[("art", "Schaltung", "auswahl", {"werte": KONSTANT_ARTEN}),
                ("I", "Gewünschter Strom", "strom", {"einheit": "mA", "platzhalter": "z.B. 10"}),
                ("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 12"}),
                ("Uref", "U_ref an der Basis", "spannung", {"platzhalter": "Transistor: z.B. 3.3"}),
                ("IDSS", "JFET I_DSS", "strom", {"einheit": "mA", "platzhalter": "JFET: z.B. 10"}),
                ("UP", "JFET |U_P|", "spannung", {"platzhalter": "JFET: z.B. 2.5"})],
        berechnen=_konstantstrom, formel="Transistor: I = (U_ref − 0.7 V) / R_E     JFET: I = I_DSS · (1 − U_GS / U_P)²")

# =============================================================================
# REGISTRIERUNG (IDs müssen sich von allen anderen unterscheiden)
# =============================================================================
RECHNER = {
    "stromteiler": stromteiler,
    "pull_widerstand": pull_widerstand,
    "poti_last": poti_last,
    "schaltung_spannungsteiler": SpannungsteilerSchaltung,
    "schaltung_stromteiler": StromteilerSchaltung,
    "schaltung_pull": PullSchaltung,
    "schaltung_poti": PotiSchaltung,
    "schaltung_bruecke": BrueckeSchaltung,
    "eingangsschutz": eingangsschutz,
    "verpolschutz": verpolschutz,
    "tvs_auswahl": tvs_auswahl,
    "schaltung_begrenzer": BegrenzerSchaltung,
    "schaltung_eingangsschutz": EingangsschutzSchaltung,
    "schaltung_verpol": VerpolSchaltung,
    "schaltung_freilauf": FreilaufSchaltung,
    "schaltung_gleichrichter": GleichrichterSchaltung,
    "schaltung_zstabi": ZStabiSchaltung,
    "schaltung_tvs": TvsSchaltung,
    "emitterfolger": emitterfolger,
    "konstantstrom": konstantstrom,
    "schaltung_lasttreiber": LastTreiberSchaltung,
    "schaltung_emitter": EmitterSchaltung,
    "schaltung_emitterfolger": EmitterfolgerSchaltung,
    "schaltung_konstantstrom": KonstantstromSchaltung,
}
