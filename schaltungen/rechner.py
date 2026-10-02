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
#   rc_frequenzgang      Tief-/Hochpass bei einer Frequenz: |H|, dB, Phase, Ausgangsspannung
#   entprellung          Taster mit RC + Schmitt-Trigger: Zeiten bis zur Schwelle, passendes C
#   anti_aliasing        RC-Tiefpass vor dem ADC: Alias-Frequenz und Dämpfung
#   opv_verstaerker      Folger / nichtinvertierend / invertierend: Vu, Ua, r_ein, Bandbreite (oder R2 auslegen)
#   opv_addierer         invertierender Summierer mit beliebig vielen Eingängen
#   differenzverstaerker Differenz- und Instrumentenverstärker mit Gleichtaktfehler durch Toleranz
#   schmitt_trigger      Schwellen berechnen oder Widerstände/U_ref für gewünschte Schwellen
#   integrator           Integrator und Differenzierer: Steigung, Dreieck/Rechteck-Amplitude, Grenzfrequenzen
#   schaltung_*          INTERAKTIVE Schaltpläne (schaltungen/grafiken.py)
#
# Spannungsteiler und Brücke gibt es schon (widerstand_rechner.py, messtechnik/rechner.py)
# -> die Seiten benutzen diese Rechner per ID, hier wird nichts kopiert.
#
# Die Grenzfrequenz allein rechnet schon "rc_filter" (bauteile/rechner/kondensator_rechner.py).
#
# Rechnung: schaltungen/netzwerk_mathe.py, dioden_mathe.py, verstaerker_mathe.py, rc_mathe.py,
#           opv_mathe.py (ohne GUI, testbar)
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py (_MODULE) -> erstellen(master, "stromteiler")
# =============================================================================

import math

from bauteile.rechner import normreihen                                          # -> bauteile/rechner/normreihen.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt             # -> bauteile/rechner/basis.py
from schaltungen import dioden_mathe as dm                                       # -> schaltungen/dioden_mathe.py
from schaltungen import netzwerk_mathe as nm                                     # -> schaltungen/netzwerk_mathe.py
from schaltungen import opv_mathe as om                                          # -> schaltungen/opv_mathe.py
from schaltungen import rc_mathe as rm                                           # -> schaltungen/rc_mathe.py
from schaltungen import verstaerker_mathe as vm                                  # -> schaltungen/verstaerker_mathe.py
from schaltungen.grafiken_opv import (AddiererSchaltung, DifferenzSchaltung,      # -> schaltungen/grafiken_opv.py
                                      IntegratorSchaltung, OpvVerstaerkerSchaltung, SchmittSchaltung)
from schaltungen.grafiken_rc import (AntiAliasingSchaltung, EntprellSchaltung,   # -> schaltungen/grafiken_rc.py
                                     RcFilterSchaltung)
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
# 9) RC-FREQUENZGANG
# =============================================================================
def _rc_frequenzgang(w):
    if None in (w["R"], w["C"], w["f"]):
        raise RechnerFehler("R, C und die Frequenz f eingeben")
    e = _fehler_umwandeln(rm.rc_glied, w["art"], w["R"], w["C"], w["f"])
    zeilen = [f"fg = 1 / (2π · R · C) = {fmt(e['fg'], 'frequenz')}   ·   f / fg = {w['f'] / e['fg']:.3g}",
              f"Xc = 1 / (2π · f · C) = {fmt(e['x_c'], 'widerstand')}",
              f"|H| = {e['betrag']:.4f}  =  {e['db']:.2f} dB   ·   φ = {e['phase']:+.1f}°"]
    if w["Ue"] is not None:
        zeilen.append(f"Ua = |H| · Ue = {fmt(e['betrag'] * w['Ue'], 'spannung')}")
    if w["art"] == "Tiefpass":
        zeilen.append("Weit über fg: |H| ≈ fg / f (−20 dB pro Dekade), φ → −90°")
    else:
        zeilen.append("Weit unter fg: |H| ≈ f / fg (+20 dB pro Dekade), φ → +90°")
    return zeilen


def rc_frequenzgang(master):
    return FormelRechner(
        master, "RC-Tief-/Hochpass: Frequenzgang", "Wie viel kommt bei einer bestimmten Frequenz am Ausgang an?",
        felder=[("art", "Filter", "auswahl", {"werte": rm.FILTER_ARTEN}),
                ("R", "Widerstand R", "widerstand", {"einheit": "kΩ"}),
                ("C", "Kapazität C", "kapazitaet", {"einheit": "nF"}),
                ("f", "Frequenz f", "frequenz", {"platzhalter": "z.B. 1k"}),
                ("Ue", "Eingang Ue (opt.)", "spannung", {"platzhalter": "optional"})],
        berechnen=_rc_frequenzgang,
        formel="TP: |H| = 1 / √(1 + (f/fg)²)     HP: |H| = (f/fg) / √(1 + (f/fg)²)     dB = 20 · log|H|")


# =============================================================================
# 10) TASTER ENTPRELLEN
# =============================================================================
def _entprellung(w):
    if None in (w["Ub"], w["R1"], w["R2"]):
        raise RechnerFehler("U_B, R1 und R2 eingeben (dazu C oder die Prellzeit)")
    if w["C"] is None and w["tp"] is None:
        raise RechnerFehler("C eingeben – oder die Prellzeit, dann wird C berechnet")
    u_tp, u_tm = rm.schwellen(w["Ub"])
    zeilen = [f"Schmitt-Trigger (74HC14-typisch): U_T+ ≈ {fmt(u_tp, 'spannung')}, U_T− ≈ {fmt(u_tm, 'spannung')}"]
    c = w["C"]
    if c is None:
        # die langsamere Richtung bestimmt: beide Zeiten ≥ Prellzeit
        if w["tp"] <= 0:
            raise RechnerFehler("Prellzeit muss grösser als 0 sein")
        _fehler_umwandeln(rm.entprell_zeiten, w["Ub"], w["R1"], w["R2"], 1.0)
        c_ab = w["tp"] / (w["R2"] * math.log(w["Ub"] / u_tm))
        c_auf = w["tp"] / ((w["R1"] + w["R2"]) * math.log(w["Ub"] / (w["Ub"] - u_tp)))
        c_min = max(c_ab, c_auf)
        c = normreihen.naechste_werte(c_min, "E6")[2]
        zeilen.append(f"C ≥ t_prell / (R2 · ln(U_B / U_T−)) = {fmt(c_min, 'kapazitaet')}   →  E6: {fmt(c, 'kapazitaet')}")
    k = _fehler_umwandeln(rm.entprell_zeiten, w["Ub"], w["R1"], w["R2"], c)
    zeilen += [f"Drücken: τ = R2 · C = {fmt(k['tau_ab'], 'zeit')},  t bis U_T− = τ · ln(U_B / U_T−) = {fmt(k['t_ab'], 'zeit')}",
               f"Loslassen: τ = (R1 + R2) · C = {fmt(k['tau_auf'], 'zeit')},  "
               f"t bis U_T+ = τ · ln(U_B / (U_B − U_T+)) = {fmt(k['t_auf'], 'zeit')}",
               f"Entladestrom über den Kontakt ≤ U_B / R2 = {fmt(w['Ub'] / w['R2'], 'strom')}"]
    if w["tp"] is not None and min(k["t_ab"], k["t_auf"]) < w["tp"]:
        zeilen.append(f"⚠ Kürzer als die Prellzeit ({fmt(w['tp'], 'zeit')}) – mit Hysterese oft noch ok, "
                      "sicher erst mit t ≥ Prellzeit")
    return zeilen


def entprellung(master):
    return FormelRechner(
        master, "Taster entprellen (RC + Schmitt-Trigger)", "Pull-up R1, R2 zum Kondensator, Schmitt-Trigger-Eingang",
        felder=[("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 5"}),
                ("R1", "Pull-up R1", "widerstand", {"einheit": "kΩ"}),
                ("R2", "R2 (zum C)", "widerstand", {"einheit": "kΩ"}),
                ("C", "Kapazität C", "kapazitaet", {"platzhalter": "leer = berechnen"}),
                ("tp", "Prellzeit", "zeit", {"platzhalter": "z.B. 5 (ms)"})],
        berechnen=_entprellung, formel="t_ab = R2 · C · ln(U_B / U_T−)     t_auf = (R1 + R2) · C · ln(U_B / (U_B − U_T+))")


# =============================================================================
# 11) ANTI-ALIASING
# =============================================================================
def _anti_aliasing(w):
    if w["fs"] is None or w["f"] is None:
        raise RechnerFehler("Abtastrate f_s und die Signal- bzw. Störfrequenz f eingeben")
    if (w["R"] is None) != (w["C"] is None):
        raise RechnerFehler("Für den Filter R UND C eingeben (oder beide leer = ohne Filter)")
    bits = None if w["N"] is None else w["N"]
    if bits is not None and bits != int(bits):
        raise RechnerFehler("Auflösung in ganzen Bit eingeben")
    e = _fehler_umwandeln(rm.anti_aliasing, w["fs"], w["f"], w["R"], w["C"], bits)
    zeilen = [f"Nyquist-Frequenz f_s / 2 = {fmt(e['nyquist'], 'frequenz')}"]
    if e["faltet"]:
        zeilen.append(f"f liegt darüber → Alias: |f − n · f_s| = {fmt(abs(e['f_alias']), 'frequenz')}")
    else:
        zeilen.append("f liegt darunter → wird richtig erfasst (kein Aliasing)")
    if e["fg"] is not None:
        zeilen.append(f"RC-Tiefpass: fg = {fmt(e['fg'], 'frequenz')},  bei f: |H| = {e['betrag']:.4f} "
                      f"({e['db']:.1f} dB),  bei f_s / 2: {e['db_nyquist']:.1f} dB")
    if bits is not None:
        zeilen.append(f"Nötige Dämpfung, damit eine Vollausschlag-Störung unter ½ LSB bleibt: "
                      f"6.02 · N dB = {e['noetig_db']:.1f} dB")
        if e["faltet"]:
            zeilen.append("✓ Störung verschwindet unter ½ LSB" if e["unsichtbar"] else
                          "⚠ Störung bleibt sichtbar → höhere Abtastrate oder Filter höherer Ordnung")
    return zeilen


def anti_aliasing(master):
    return FormelRechner(
        master, "Anti-Aliasing (RC vor dem ADC)", "Erscheint eine Frequenz nach dem Abtasten falsch – und wie stark?",
        felder=[("fs", "Abtastrate f_s", "frequenz", {"platzhalter": "z.B. 1k"}),
                ("f", "Signal-/Störfrequenz f", "frequenz", {"platzhalter": "z.B. 900"}),
                ("R", "R (opt.)", "widerstand", {"einheit": "kΩ", "platzhalter": "optional"}),
                ("C", "C (opt.)", "kapazitaet", {"einheit": "nF", "platzhalter": "optional"}),
                ("N", "ADC-Auflösung N (opt.)", "zahl", {"platzhalter": "z.B. 12"})],
        berechnen=_anti_aliasing, formel="f_alias = |f − n · f_s|     f_s > 2 · f_max     Dämpfung ≥ 6.02 · N dB")



# =============================================================================
# 12) OPV-VERSTÄRKER
# =============================================================================
def _opv_verstaerker(w):
    art = w["art"]
    if w["Ub"] is None:
        raise RechnerFehler("Versorgung ±U_B eingeben (z.B. 12 für ±12 V)")
    zeilen = []
    r1, r2 = w["R1"], w["R2"]
    if art != "Spannungsfolger":
        if r1 is None:
            raise RechnerFehler("R1 eingeben")
        if r2 is None:
            # Auslegen: R2 aus der gewünschten Verstärkung
            if w["Vu"] is None:
                raise RechnerFehler("R2 eingeben – oder die gewünschte Verstärkung Vu, dann wird R2 berechnet")
            vu = abs(w["Vu"])
            if art == "nichtinvertierend" and vu <= 1:
                raise RechnerFehler("Nichtinvertierend ist Vu immer ≥ 1 – für Vu = 1 den Spannungsfolger nehmen")
            r2_genau = r1 * (vu - 1) if art == "nichtinvertierend" else r1 * vu
            r2 = normreihen.naechste_werte(r2_genau, "E24")[1]
            zeilen.append(f"R2 = R1 · {'(Vu − 1)' if art == 'nichtinvertierend' else '|Vu|'} = "
                          f"{fmt(r2_genau, 'widerstand')}   →  E24: {fmt(r2, 'widerstand')}")
    ue = 0.0 if w["Ue"] is None else w["Ue"]
    gbw = om.GBW if w["GBW"] is None else w["GBW"]
    e = _fehler_umwandeln(om.verstaerker, art, r1 or 1.0, r2 or 1.0, ue, w["Ub"], False, gbw)
    formel = {"Spannungsfolger": "Vu = 1", "nichtinvertierend": "Vu = 1 + R2 / R1", "invertierend": "Vu = −R2 / R1"}[art]
    zeilen += [f"{formel} = {e['vu']:.4g}  ({e['db']:.1f} dB)",
               f"Ua = Vu · Ue = {fmt(e['u_a_ideal'], 'spannung')}" + ("" if not e["begrenzt"] else
                                                                     f"  → begrenzt auf {fmt(e['u_a'], 'spannung')}"),
               "Eingangswiderstand: " + ("sehr hoch (+ Eingang, ≈ 10¹² Ω bei FET-OPV)" if art != "invertierend"
                                         else f"R1 = {fmt(r1, 'widerstand')} (− ist virtuelle Masse)"),
               f"Bandbreite ≈ GBW / (1 + R2/R1) = {fmt(gbw, 'frequenz')} / {e['rauschverstaerkung']:.4g} = "
               f"{fmt(e['f_g'], 'frequenz')}",
               f"Aussteuerung (klassischer OPV, 1.5 V Abstand): {fmt(e['u_min'], 'spannung')} … +{fmt(e['u_max'], 'spannung')}"]
    if art == "invertierend" and r1 < 1e3:
        zeilen.append("⚠ R1 < 1 kΩ belastet die Quelle stark – r_ein der invertierenden Schaltung ist R1")
    return zeilen


def opv_verstaerker(master):
    return FormelRechner(
        master, "OPV-Verstärker", "Folger, nichtinvertierend oder invertierend – leeres R2 wird aus Vu berechnet",
        felder=[("art", "Schaltung", "auswahl", {"werte": om.VERSTAERKER_ARTEN, "standard": "nichtinvertierend"}),
                ("R1", "R1", "widerstand", {"einheit": "kΩ"}),
                ("R2", "R2 (Gegenkopplung)", "widerstand", {"einheit": "kΩ", "platzhalter": "leer = aus Vu"}),
                ("Vu", "gewünschte Vu (opt.)", "zahl", {"platzhalter": "z.B. 10"}),
                ("Ue", "Eingang Ue (opt.)", "spannung", {"platzhalter": "z.B. 0.5"}),
                ("Ub", "Versorgung ±U_B", "spannung", {"platzhalter": "z.B. 12"}),
                ("GBW", "GBW (opt.)", "frequenz", {"einheit": "MHz", "platzhalter": "1 MHz"})],
        berechnen=_opv_verstaerker, formel="nichtinv.: Vu = 1 + R2/R1     inv.: Vu = −R2/R1     f_g = GBW / (1 + R2/R1)")


# =============================================================================
# 13) ADDIERER
# =============================================================================
def _opv_addierer(w):
    if not w["U"] or not w["R"] or w["Rf"] is None:
        raise RechnerFehler("Eingangsspannungen, Eingangswiderstände (gleich viele) und R_f eingeben")
    if len(w["U"]) != len(w["R"]):
        raise RechnerFehler(f"{len(w['U'])} Spannungen, aber {len(w['R'])} Widerstände – je Eingang einen Widerstand")
    e = _fehler_umwandeln(om.addierer, w["U"], w["R"], w["Rf"], w["Ub"] if w["Ub"] is not None else 15.0)
    zeilen = []
    for k, (u, r, i) in enumerate(zip(w["U"], w["R"], e["stroeme"]), start=1):
        zeilen.append(f"I{k} = U{k} / R{k} = {fmt(u, 'spannung')} / {fmt(r, 'widerstand')} = {fmt(i, 'strom')}"
                      f"   (Gewicht {-w['Rf'] / r:.4g})")
    zeilen.append(f"Ua = −R_f · ΣI = −{fmt(w['Rf'], 'widerstand')} · {fmt(e['i_f'], 'strom')} = "
                  f"{fmt(e['u_a_ideal'], 'spannung')}")
    if e["begrenzt"]:
        zeilen.append(f"⚠ Liegt ausserhalb der Aussteuerung – Ausgang begrenzt auf {fmt(e['u_a'], 'spannung')}")
    return zeilen


def opv_addierer(master):
    return FormelRechner(
        master, "OPV-Addierer (Summierer)", "Mehrere Werte mit Leerzeichen trennen, z.B.  1 2 -0.5",
        felder=[("U", "Eingangsspannungen", "spannung", {"liste": True, "platzhalter": "z.B. 1 2 -0.5"}),
                ("R", "Eingangswiderstände", "widerstand", {"liste": True, "einheit": "kΩ", "platzhalter": "z.B. 10 10 10"}),
                ("Rf", "R_f", "widerstand", {"einheit": "kΩ"}),
                ("Ub", "Versorgung ±U_B (opt.)", "spannung", {"platzhalter": "15"})],
        berechnen=_opv_addierer, formel="Ua = −R_f · (U1/R1 + U2/R2 + …)")


# =============================================================================
# 14) DIFFERENZ- UND INSTRUMENTENVERSTÄRKER
# =============================================================================
DIFFERENZ_ARTEN = ["Differenzverstärker (4 Widerstände)", "Instrumentenverstärker (3 OPV)"]


def _differenzverstaerker(w):
    if None in (w["U1"], w["U2"], w["R1"], w["R2"]):
        raise RechnerFehler("U1, U2, R1 und R2 eingeben")
    tol = 0.0 if w["tol"] is None else w["tol"]
    ub = 15.0 if w["Ub"] is None else w["Ub"]
    if w["art"] == DIFFERENZ_ARTEN[1]:
        if w["RG"] is None:
            raise RechnerFehler("R_G eingeben (Eingangsstufe mit 2 × 25 kΩ wie INA128)")
        e = _fehler_umwandeln(om.instrumenten, w["U1"], w["U2"], 25e3, w["RG"], w["R1"], w["R2"], tol, ub)
        zeilen = [f"G = (1 + 2 · 25 kΩ / R_G) · R2 / R1 = {e['g1']:.4g} · {w['R2'] / w['R1']:.4g} = {e['g']:.4g}",
                  f"Ausgänge der Eingangsstufe: {fmt(e['u_innen'][0], 'spannung')} und {fmt(e['u_innen'][1], 'spannung')}"]
    else:
        e = _fehler_umwandeln(om.differenz, w["U1"], w["U2"], w["R1"], w["R2"], tol, ub)
        zeilen = [f"A_d = R2 / R1 = {e['a_d']:.4g}   ·   Eingangswiderstand: − {fmt(e['r_ein_minus'], 'widerstand')}, "
                  f"+ {fmt(e['r_ein_plus'], 'widerstand')}"]
    zeilen += [f"U_d = U2 − U1 = {fmt(e['u_d'], 'spannung')}   ·   U_cm = (U1 + U2) / 2 = {fmt(e['u_cm'], 'spannung')}",
               f"Ua = {fmt(e['u_a'], 'spannung')}" + (f"   (davon Gleichtaktfehler {fmt(e['fehler_cm'], 'spannung')})"
                                                     if tol else "")]
    if tol:
        zeilen.append(f"CMRR ≈ (1 + R2/R1) / (4 · Toleranz){' · G1' if w['art'] == DIFFERENZ_ARTEN[1] else ''} = "
                      f"{e['cmrr_db']:.1f} dB")
    if e["begrenzt"] or e.get("innen_begrenzt"):
        zeilen.append("⚠ Ein Ausgang erreicht die Aussteuergrenze (±U_B − 1.5 V)")
    return zeilen


def differenzverstaerker(master):
    return FormelRechner(
        master, "Differenz- / Instrumentenverstärker", "Ua aus U2 − U1, Gleichtaktfehler durch Widerstandstoleranz",
        felder=[("art", "Schaltung", "auswahl", {"werte": DIFFERENZ_ARTEN}),
                ("U1", "U1 (an −)", "spannung", {"platzhalter": "z.B. 2.45"}),
                ("U2", "U2 (an +)", "spannung", {"platzhalter": "z.B. 2.55"}),
                ("R1", "R1", "widerstand", {"einheit": "kΩ"}),
                ("R2", "R2", "widerstand", {"einheit": "kΩ"}),
                ("RG", "R_G (nur INA)", "widerstand", {"einheit": "kΩ", "platzhalter": "nur Instrumentenv."}),
                ("tol", "Toleranz (opt.)", "prozent", {"platzhalter": "z.B. 1"}),
                ("Ub", "Versorgung ±U_B (opt.)", "spannung", {"platzhalter": "15"})],
        berechnen=_differenzverstaerker, formel="Ua = R2/R1 · (U2 − U1)     INA: G = 1 + 2R/R_G     CMRR ≈ (1 + R2/R1)/(4 · tol)")


# =============================================================================
# 15) SCHMITT-TRIGGER
# =============================================================================
def _schmitt(w):
    art = w["art"]
    if w["Usat"] is None:
        raise RechnerFehler("Ausgangsspannung U_sat eingeben (z.B. 10.5 bei ±12 V, 5 bei Rail-to-Rail an 5 V → ±)")
    if w["UTp"] is not None or w["UTm"] is not None:
        if w["UTp"] is None or w["UTm"] is None:
            raise RechnerFehler("Zum Auslegen BEIDE Schwellen U_T+ und U_T− eingeben")
        rf = 100e3 if w["Rf"] is None else w["Rf"]
        e = _fehler_umwandeln(om.schmitt_auslegen, art, w["UTp"], w["UTm"], w["Usat"], rf)
        r1_norm = normreihen.naechste_werte(e["r1"], "E24")[1]
        s = _fehler_umwandeln(om.schmitt_schwellen, art, r1_norm, rf, e["u_ref"], w["Usat"])
        return [f"Hysterese ΔU = {fmt(w['UTp'] - w['UTm'], 'spannung')}, Mitte {fmt((w['UTp'] + w['UTm']) / 2, 'spannung')}",
                f"R1 / {'(R1 + R_f)' if art == 'invertierend' else 'R_f'} = ΔU / (2 · U_sat)  →  "
                f"R1 = {fmt(e['r1'], 'widerstand')} bei R_f = {fmt(rf, 'widerstand')}   →  E24: {fmt(r1_norm, 'widerstand')}",
                f"U_ref = {fmt(e['u_ref'], 'spannung')}",
                f"Kontrolle mit E24: U_T+ = {fmt(s['u_tp'], 'spannung')}, U_T− = {fmt(s['u_tm'], 'spannung')}"]
    if w["R1"] is None or w["Rf"] is None:
        raise RechnerFehler("R1 und R_f eingeben – oder die gewünschten Schwellen U_T+ und U_T−")
    u_ref = 0.0 if w["Uref"] is None else w["Uref"]
    s = _fehler_umwandeln(om.schmitt_schwellen, art, w["R1"], w["Rf"], u_ref, w["Usat"])
    formel = ("U_T± = (U_ref · R_f ± U_sat · R1) / (R1 + R_f)" if art == "invertierend"
              else "U_T± = U_ref · (1 + R1/R_f) ± U_sat · R1/R_f")
    zeilen = [formel,
              f"U_T+ = {fmt(s['u_tp'], 'spannung')}   ·   U_T− = {fmt(s['u_tm'], 'spannung')}",
              f"Hysterese = {fmt(s['hysterese'], 'spannung')}   ·   Mitte = {fmt(s['mitte'], 'spannung')}"]
    if art == "nichtinvertierend" and w["R1"] > w["Rf"]:
        zeilen.append("⚠ R1 > R_f: Hysterese grösser als 2 · U_sat – das Signal muss sehr gross werden")
    return zeilen


def schmitt_trigger(master):
    return FormelRechner(
        master, "Schmitt-Trigger mit OPV", "Schwellen berechnen – oder U_T+ / U_T− vorgeben, dann R1 und U_ref auslegen",
        felder=[("art", "Schaltung", "auswahl", {"werte": om.SCHMITT_ARTEN}),
                ("Usat", "U_sat (± am Ausgang)", "spannung", {"platzhalter": "z.B. 10.5"}),
                ("R1", "R1", "widerstand", {"einheit": "kΩ"}),
                ("Rf", "R_f (Mitkopplung)", "widerstand", {"einheit": "kΩ", "platzhalter": "z.B. 100"}),
                ("Uref", "U_ref (opt.)", "spannung", {"platzhalter": "0"}),
                ("UTp", "gewünschte U_T+ (opt.)", "spannung", {"platzhalter": "zum Auslegen"}),
                ("UTm", "gewünschte U_T− (opt.)", "spannung", {"platzhalter": "zum Auslegen"})],
        berechnen=_schmitt, formel="Hysterese: inv. 2·U_sat·R1/(R1 + R_f)     nichtinv. 2·U_sat·R1/R_f")


# =============================================================================
# 16) INTEGRATOR / DIFFERENZIERER
# =============================================================================
INTEGRATOR_ARTEN = ["Integrator", "Differenzierer"]


def _integrator(w):
    if None in (w["R"], w["C"]):
        raise RechnerFehler("R und C eingeben")
    if w["R"] <= 0 or w["C"] <= 0:
        raise RechnerFehler("R und C müssen grösser als 0 sein")
    rc = w["R"] * w["C"]
    f_1 = 1 / (2 * math.pi * rc)
    if w["art"] == INTEGRATOR_ARTEN[0]:
        zeilen = [f"τ = R · C = {fmt(rc, 'zeit')}   ·   |Vu| = 1 / (2π · f · R · C) = 1 bei {fmt(f_1, 'frequenz')}"]
        if w["Ue"] is not None:
            zeilen.append(f"Konstantes Ue: Rampe dUa/dt = −Ue / (R · C) = {-w['Ue'] / rc:.4g} V/s")
            if w["f"] is not None:
                k = _fehler_umwandeln(om.integrator_kennwerte, w["R"], w["C"], w["Ue"], w["f"])
                zeilen.append(f"Rechteck ±Ue mit f: Dreieck Spitze-Spitze = Ue / (R · C) · 1/(2f) = "
                              f"{fmt(k['dreieck_ss'], 'spannung')}")
        if w["Rx"] is not None:
            k = _fehler_umwandeln(om.integrator_kennwerte, w["R"], w["C"], 0.0, None, w["Rx"])
            zeilen.append(f"R_p = {fmt(w['Rx'], 'widerstand')}: Gleichspannungsverstärkung {k['v_dc']:.4g}, "
                          f"integriert erst über f_u = 1/(2π · R_p · C) = {fmt(k['f_u'], 'frequenz')}")
        else:
            zeilen.append("Ohne R_p ∥ C läuft jeder Offset in die Begrenzung – in der Praxis R_p ≈ 10 … 100 · R")
        return zeilen
    zeilen = [f"τ = R · C = {fmt(rc, 'zeit')}   ·   |Vu| = 2π · f · R · C = 1 bei {fmt(f_1, 'frequenz')}"]
    if w["Ue"] is not None and w["f"] is not None:
        zeilen.append(f"Dreieck ±Ue mit f: Steigung 4 · Ue · f → Rechteck Ua = ∓R · C · 4 · Ue · f = "
                      f"∓{fmt(rc * 4 * abs(w['Ue']) * w['f'], 'spannung')}")
    if w["Rx"] is not None:
        zeilen.append(f"R_s = {fmt(w['Rx'], 'widerstand')}: Verstärkung höchstens R / R_s = {w['R'] / w['Rx']:.4g} "
                      f"ab f = 1/(2π · R_s · C) = {fmt(1 / (2 * math.pi * w['Rx'] * w['C']), 'frequenz')}")
    else:
        zeilen.append("Ohne R_s vor C steigt die Verstärkung unbegrenzt mit f – Rauschen, Schwingneigung")
    return zeilen


def integrator(master):
    return FormelRechner(
        master, "Integrator / Differenzierer", "Mit OPV (invertierend): Steigung, Amplitude, Grenzfrequenzen",
        felder=[("art", "Schaltung", "auswahl", {"werte": INTEGRATOR_ARTEN}),
                ("R", "R", "widerstand", {"einheit": "kΩ"}),
                ("C", "C", "kapazitaet", {"einheit": "nF"}),
                ("Ue", "Eingang Ue / û (opt.)", "spannung", {"platzhalter": "z.B. 1"}),
                ("f", "Frequenz f (opt.)", "frequenz", {"platzhalter": "z.B. 1k"}),
                ("Rx", "R_p bzw. R_s (opt.)", "widerstand", {"einheit": "kΩ", "platzhalter": "optional"})],
        berechnen=_integrator, formel="Integrator: Ua = −1/(R·C) · ∫Ue dt     Differenzierer: Ua = −R·C · dUe/dt")


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
    "rc_frequenzgang": rc_frequenzgang,
    "entprellung": entprellung,
    "anti_aliasing": anti_aliasing,
    "schaltung_rc_filter": RcFilterSchaltung,
    "schaltung_entprellung": EntprellSchaltung,
    "schaltung_anti_aliasing": AntiAliasingSchaltung,
    "opv_verstaerker": opv_verstaerker,
    "opv_addierer": opv_addierer,
    "differenzverstaerker": differenzverstaerker,
    "schmitt_trigger": schmitt_trigger,
    "integrator": integrator,
    "schaltung_opv_verstaerker": OpvVerstaerkerSchaltung,
    "schaltung_addierer": AddiererSchaltung,
    "schaltung_differenz": DifferenzSchaltung,
    "schaltung_schmitt": SchmittSchaltung,
    "schaltung_integrator": IntegratorSchaltung,
}
