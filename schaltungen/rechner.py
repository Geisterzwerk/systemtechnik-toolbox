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
#   innenwiderstand      R_i aus Leerlauf- und Lastmessung, Klemmenspannung und Leistung an einer Last
#   netzteil_auslegen    Trafospannung, Elko, Trafoleistung für eine gewünschte Spannung nach dem Regler
#   linearregler         Dropout im Wellental, Verlust, Wirkungsgrad, Sperrschichttemperatur
#   lm317                Ausgangsspannung aus R1/R2 oder R2 für eine gewünschte Spannung
#   strombegrenzung      Shunt für einen Maximalstrom, Verlust bei Kurzschluss
#   stromquelle_opv      geregelte Stromsenke OPV + MOSFET + Shunt
#   schaltregler         Buck / Boost: Tastgrad, Spule, Rippelstrom, Spitzenstrom, Welligkeit
#   lc_filter            LC-Tiefpass mit Last: f0, Q, Überhöhung, −3-dB-Frequenz, Dämpfung bei f
#   schwingkreis_filter  RLC-Reihenkreis als Bandpass / Bandsperre: f0, Q, Bandbreite, Grenzfrequenzen
#   sallen_key           aktives Filter 2. Ordnung für f0 und Charakteristik auslegen (mit Normwerten)
#   pt_leitung           Pt100/Pt1000: Leitungswiderstand aus Länge/Querschnitt, Fehler in 2/3/4-Leiter-Schaltung
#   ntc_teiler           NTC-Spannungsteiler: Festwiderstand für beste Linearität, Spannungen, Auflösung
#   dms_verstaerker      Wägezelle/DMS-Brücke: Verstärkung und R_G für den gewünschten Ausgangsbereich
#   pegelteiler          5 V -> 3.3 V: R2 für einen Teiler, Pegel und Anstiegszeit
#   optokoppler          Vorwiderstand und Pull-up für sichere Sättigung (mit CTR-Alterung)
#   h_bruecke            H-Brücke: Leit- und Schaltverluste, mittlere Motorspannung
#   gate_schaltzeit      Miller-Plateau: Schaltzeit und Schaltverlust aus Q_gd und Gate-Strom
#   bootstrap            Bootstrap-Kondensator eines High-Side-Treibers
#   adc_eingang          grösster Quellwiderstand bzw. kleinstes C_ext für ½ LSB Genauigkeit
#   schaltung_*          INTERAKTIVE Schaltpläne (schaltungen/grafiken.py)
#
# Spannungsteiler und Brücke gibt es schon (widerstand_rechner.py, messtechnik/rechner.py)
# -> die Seiten benutzen diese Rechner per ID, hier wird nichts kopiert.
#
# Die Grenzfrequenz allein rechnet schon "rc_filter" (bauteile/rechner/kondensator_rechner.py).
#
# Rechnung: schaltungen/netzwerk_mathe.py, dioden_mathe.py, verstaerker_mathe.py, rc_mathe.py,
#           opv_mathe.py, netzteil_mathe.py, filter_mathe.py, mess_mathe.py, schnittstellen_mathe.py (ohne GUI)
# Pt100, NTC, Brücke und DMS selbst rechnet messtechnik/rechner.py ("pt100", "ntc", "bruecke", "dms"),
# die Gate-Ladung allein "mosfet_gate" (bauteile/rechner/transistor_rechner.py) - hier nur die Schaltungen drumherum.
# Die Resonanzfrequenz allein rechnet schon "lc_resonanz" (bauteile/rechner/spule_rechner.py).
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py (_MODULE) -> erstellen(master, "stromteiler")
# =============================================================================

import math

from bauteile.rechner import normreihen                                          # -> bauteile/rechner/normreihen.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt             # -> bauteile/rechner/basis.py
from schaltungen import dioden_mathe as dm                                       # -> schaltungen/dioden_mathe.py
from schaltungen import filter_mathe as fm                                       # -> schaltungen/filter_mathe.py
from schaltungen import mess_mathe as mm                                         # -> schaltungen/mess_mathe.py
from schaltungen import schnittstellen_mathe as sm                               # -> schaltungen/schnittstellen_mathe.py
from schaltungen import netzteil_mathe as ntm                                    # -> schaltungen/netzteil_mathe.py
from schaltungen import netzwerk_mathe as nm                                     # -> schaltungen/netzwerk_mathe.py
from schaltungen import opv_mathe as om                                          # -> schaltungen/opv_mathe.py
from schaltungen import rc_mathe as rm                                           # -> schaltungen/rc_mathe.py
from schaltungen import verstaerker_mathe as vm                                  # -> schaltungen/verstaerker_mathe.py
from schaltungen.grafiken_filter import (LcFilterSchaltung, SallenKeySchaltung,  # -> schaltungen/grafiken_filter.py
                                         SchwingkreisSchaltung)
from schaltungen.grafiken_mess import (DmsKetteSchaltung, NtcTeilerSchaltung,    # -> schaltungen/grafiken_mess.py
                                       PtLeitungSchaltung)
from schaltungen.grafiken_schnittstellen import (AdcEingangSchaltung, GateTreiberSchaltung,  # -> grafiken_schnittstellen.py
                                                 HBrueckeSchaltung, OptokopplerSchaltung, PegelwandlerSchaltung)
from schaltungen.grafiken_netzteil import (LinearreglerSchaltung, QuelleSchaltung,  # -> schaltungen/grafiken_netzteil.py
                                           SchaltreglerSchaltung, StrombegrenzungSchaltung,
                                           StromquelleOpvSchaltung, VirtuelleMasseSchaltung)
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
        c = normreihen.naechste_werte(c_min, "E6")[1]                  # nächst GRÖSSERER: C ist ein Mindestwert
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
            r2 = normreihen.naechste_werte(r2_genau, "E24")[2]          # nächster Normwert (Verhältnis)
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
        r1_norm = normreihen.naechste_werte(e["r1"], "E24")[2]          # nächster Normwert
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
# 17) INNENWIDERSTAND
# =============================================================================
def _innenwiderstand(w):
    if w["U0"] is None:
        raise RechnerFehler("Leerlaufspannung U0 eingeben (Messung ohne Last)")
    zeilen = []
    r_i = w["Ri"]
    if w["Ulast"] is not None:
        if w["RL"] is None and w["I"] is None:
            raise RechnerFehler("Zur Spannung unter Last auch R_L oder den Laststrom eingeben")
        e = _fehler_umwandeln(ntm.innenwiderstand, w["U0"], w["Ulast"], w["RL"], w["I"])
        r_i = e["r_i"]
        zeilen += [f"I = {'U_last / R_L' if w['I'] is None else 'gemessen'} = {fmt(e['i'], 'strom')}",
                   f"R_i = (U0 − U_last) / I = {fmt(r_i, 'widerstand')}   ·   Kurzschlussstrom U0 / R_i = "
                   f"{fmt(e['i_kurz'], 'strom')}"]
    if r_i is None:
        raise RechnerFehler("R_i eingeben – oder U_last mit R_L (bzw. I) messen, dann wird R_i berechnet")
    if r_i <= 0:
        raise RechnerFehler("R_i muss grösser als 0 sein")
    zeilen.append(f"Leistungsanpassung: P_max = U0² / (4 · R_i) = {fmt(w['U0'] ** 2 / (4 * r_i), 'leistung')} bei R_L = R_i")
    if w["RL"] is not None and w["Ulast"] is None:
        e = _fehler_umwandeln(ntm.quelle, "Spannungsquelle", w["U0"], r_i, w["RL"])
        zeilen.append(f"An R_L = {fmt(w['RL'], 'widerstand')}: U_K = {fmt(e['u_k'], 'spannung')}, I = "
                      f"{fmt(e['i'], 'strom')}, P = {fmt(e['p_l'], 'leistung')}, η = {e['eta'] * 100:.1f} %")
    return zeilen


def innenwiderstand(master):
    return FormelRechner(
        master, "Innenwiderstand einer Quelle", "Aus zwei Messungen (Leerlauf + Last) – oder Last an bekannter Quelle",
        felder=[("U0", "Leerlaufspannung U0", "spannung", {"platzhalter": "z.B. 12.6"}),
                ("Ulast", "U unter Last (opt.)", "spannung", {"platzhalter": "z.B. 12.0"}),
                ("RL", "Last R_L", "widerstand", {"platzhalter": "z.B. 10"}),
                ("I", "Laststrom (opt.)", "strom", {"platzhalter": "statt R_L"}),
                ("Ri", "R_i (opt.)", "widerstand", {"platzhalter": "falls bekannt"})],
        berechnen=_innenwiderstand, formel="R_i = (U0 − U_last) / I     U_K = U0 · R_L / (R_i + R_L)")


# =============================================================================
# 18) NETZTEIL AUSLEGEN (rückwärts)
# =============================================================================
def _netzteil_auslegen(w):
    if w["Ua"] is None or w["I"] is None:
        raise RechnerFehler("Gewünschte Ausgangsspannung (nach dem Regler) und Laststrom eingeben")
    u_drop = 2.0 if w["Ud"] is None else w["Ud"]
    e = _fehler_umwandeln(ntm.netzteil_auslegen, w["Ua"] + u_drop, w["I"], w["dU"], w["C"])
    c_norm = normreihen.naechste_werte(e["c"], "E6")[1]                # nächst GRÖSSERER: C ist ein Mindestwert
    zeilen = [f"Im Wellental nötig: U_aus + Dropout = {fmt(w['Ua'] + u_drop, 'spannung')}   ·   "
              f"Welligkeit ΔU = {fmt(e['delta_u'], 'spannung')}",
              f"Elko: C = I / (2 · f · ΔU) = {fmt(e['c'], 'kapazitaet')}" +
              (f"   →  E6: {fmt(c_norm, 'kapazitaet')}" if w["C"] is None else ""),
              f"Spitze bei Netz −10 %: Û = U_Tal + ΔU + 2 · 0.7 V = {fmt(e['u_spitze_min'], 'spannung')}",
              f"Trafo: U_sek = Û / (√2 · 0.9) = {fmt(e['u_sek'], 'spannung')} (eff)   ·   I_sek ≈ 1.8 · I = "
              f"{fmt(e['i_sek_eff'], 'strom')}   ·   S ≈ {fmt(e['s_trafo'], 'leistung').replace('W', 'VA')}",
              f"Elko-Spannung (Netz +10 %, Leerlauf +10 %): ≥ {fmt(e['u_elko_max'], 'spannung')} → nächste Reihe "
              f"(16 / 25 / 35 / 50 / 63 V)",
              f"Regler-Eingang maximal ≈ {fmt(e['u_elko_max'], 'spannung')} → Verlust im Regler beachten"]
    return zeilen


def netzteil_auslegen(master):
    return FormelRechner(
        master, "Netzteil auslegen (Trafo, Elko)", "Vom Ausgang rückwärts: Welche Trafospannung und welcher Elko?",
        felder=[("Ua", "Ausgang nach dem Regler", "spannung", {"platzhalter": "z.B. 5"}),
                ("I", "Laststrom", "strom", {"einheit": "A", "platzhalter": "z.B. 1"}),
                ("Ud", "Dropout des Reglers", "spannung", {"platzhalter": "78xx: 2, LDO: 0.3"}),
                ("dU", "Welligkeit ΔU (opt.)", "spannung", {"platzhalter": "10 % des Tals"}),
                ("C", "Ladeelko (opt.)", "kapazitaet", {"einheit": "mF", "platzhalter": "statt ΔU"})],
        berechnen=_netzteil_auslegen, formel="ΔU = I / (2 · f · C)     U_sek = (U_aus + U_D + ΔU + 1.4 V) / (√2 · 0.9)")


# =============================================================================
# 19) LINEARREGLER
# =============================================================================
def _linearregler(w):
    if None in (w["Ue"], w["Ua"], w["I"]):
        raise RechnerFehler("Eingangsspannung (Spitze am Elko), Ausgangsspannung und Laststrom eingeben")
    du = 0.0 if w["dU"] is None else w["dU"]
    u_drop = 2.0 if w["Ud"] is None else w["Ud"]
    r_th = 50.0 if w["Rth"] is None else w["Rth"]
    e = _fehler_umwandeln(ntm.linearregler, w["Ue"], du, w["Ua"], w["I"], u_drop, r_th)
    zeilen = [f"Wellental {fmt(e['u_tal'], 'spannung')} – nötig U_aus + Dropout = {fmt(w['Ua'] + u_drop, 'spannung')}"
              + ("   ✓" if e["regelt"] else "   ❌ Dropout: Welligkeit kommt durch"),
              f"P = (U_ein,mittel − U_aus) · I = ({fmt(e['u_mittel'], 'spannung')} − {fmt(w['Ua'], 'spannung')}) · "
              f"{fmt(w['I'], 'strom')} = {fmt(e['p'], 'leistung')}   ·   η = {e['eta'] * 100:.0f} %",
              f"T_j = 25 °C + P · R_th = 25 °C + {fmt(e['p'], 'leistung')} · {r_th:g} K/W = {e['t_j']:.0f} °C"]
    if e["t_j"] > 125:
        zeilen.append(f"⚠ Über 125 °C: R_th gesamt ≤ (125 − 25) / P = {100 / e['p']:.1f} K/W nötig → Kühlkörper "
                      "(Rechner „Kühlkörper“) oder Schaltregler")
    return zeilen


def linearregler(master):
    return FormelRechner(
        master, "Linearregler (78xx / LDO / LM317)", "Reicht die Spannung im Wellental? Wie heiss wird der Regler?",
        felder=[("Ue", "Eingang: Spitze am Elko", "spannung", {"platzhalter": "z.B. 11.5"}),
                ("dU", "Welligkeit ΔU (opt.)", "spannung", {"platzhalter": "0"}),
                ("Ua", "Ausgang U_aus", "spannung", {"platzhalter": "z.B. 5"}),
                ("I", "Laststrom", "strom", {"einheit": "mA"}),
                ("Ud", "Dropout (opt.)", "spannung", {"platzhalter": "2 (78xx)"}),
                ("Rth", "R_th J→Luft K/W (opt.)", "zahl", {"platzhalter": "50 (TO-220 frei)"})],
        berechnen=_linearregler, formel="P = (U_ein − U_aus) · I     T_j = T_a + P · R_th     η = U_aus / U_ein")


# =============================================================================
# 20) LM317
# =============================================================================
def _lm317(w):
    r1 = 240.0 if w["R1"] is None else w["R1"]
    if r1 <= 0:
        raise RechnerFehler("R1 muss grösser als 0 sein")
    zeilen = [f"Mindestlast durch R1: 1.25 V / R1 = {fmt(1.25 / r1, 'strom')} (LM317 braucht ≥ 3.5 … 10 mA)"]
    if w["R2"] is not None:
        u_a = _fehler_umwandeln(ntm.lm317_spannung, r1, w["R2"])
        zeilen.insert(0, f"U_aus = 1.25 V · (1 + R2 / R1) + 50 µA · R2 = {fmt(u_a, 'spannung')}")
        return zeilen
    if w["Ua"] is None:
        raise RechnerFehler("R2 eingeben – oder die gewünschte Ausgangsspannung, dann wird R2 berechnet")
    r2 = _fehler_umwandeln(ntm.lm317_r2, w["Ua"], r1)
    naechster = normreihen.naechste_werte(r2, "E24")[2]                 # (unten, oben, nächster)
    zeilen.insert(0, f"R2 = (U_aus − 1.25 V) / (1.25 V / R1 + 50 µA) = {fmt(r2, 'widerstand')}")
    zeilen.insert(1, f"E24: {fmt(naechster, 'widerstand')} → U_aus = {fmt(ntm.lm317_spannung(r1, naechster), 'spannung')}"
                     f"   (genauer: Poti oder zwei Widerstände in Reihe)")
    return zeilen


def lm317(master):
    return FormelRechner(
        master, "LM317 einstellen", "Ausgangsspannung aus R1/R2 – oder R2 für eine gewünschte Spannung",
        felder=[("R1", "R1 (OUT → ADJ)", "widerstand", {"platzhalter": "240"}),
                ("R2", "R2 (ADJ → GND)", "widerstand", {"platzhalter": "leer = berechnen"}),
                ("Ua", "gewünschte U_aus (opt.)", "spannung", {"platzhalter": "z.B. 12"})],
        berechnen=_lm317, formel="U_aus = 1.25 V · (1 + R2 / R1) + I_ADJ · R2     I_ADJ ≈ 50 µA")


# =============================================================================
# 21) STROMBEGRENZUNG
# =============================================================================
def _strombegrenzung(w):
    if w["Imax"] is None:
        raise RechnerFehler("Gewünschten Maximalstrom eingeben")
    if w["Imax"] <= 0:
        raise RechnerFehler("Maximalstrom muss grösser als 0 sein")
    r_s = ntm.U_BE_BEGRENZUNG / w["Imax"]
    r_norm = normreihen.naechste_werte(r_s, "E24")[2]                  # nächster Normwert, I_max wird neu gerechnet
    i_echt = ntm.U_BE_BEGRENZUNG / r_norm
    zeilen = [f"R_S = 0.6 V / I_max = {fmt(r_s, 'widerstand')}   →  E24: {fmt(r_norm, 'widerstand')} "
              f"(I_max ≈ {fmt(i_echt, 'strom')})",
              f"Leistung im Shunt bei I_max: 0.6 V · I_max = {fmt(0.6 * i_echt, 'leistung')}",
              "U_BE streut und sinkt mit −2 mV/K: I_max ist nur auf ≈ ±20 % genau"]
    if w["Ue"] is not None:
        zeilen.append(f"Verlust im Längstransistor bei Kurzschluss ≈ (U_e − 0.6 V) · I_max = "
                      f"{fmt((w['Ue'] - 0.6) * i_echt, 'leistung')} → Kühlkörper oder Foldback-Begrenzung")
    return zeilen


def strombegrenzung(master):
    return FormelRechner(
        master, "Strombegrenzung mit Shunt + Transistor", "Längsregler kurzschlussfest machen",
        felder=[("Imax", "Maximalstrom I_max", "strom", {"einheit": "mA", "platzhalter": "z.B. 500"}),
                ("Ue", "Eingang U_e (opt.)", "spannung", {"platzhalter": "für den Kurzschlussverlust"})],
        berechnen=_strombegrenzung, formel="R_S = 0.6 V / I_max     P_T1,Kurzschluss ≈ U_e · I_max")


# =============================================================================
# 22) GEREGELTE STROMQUELLE
# =============================================================================
def _stromquelle_opv(w):
    if w["I"] is None or w["Ub"] is None:
        raise RechnerFehler("Gewünschten Strom und U_B eingeben")
    if w["I"] <= 0:
        raise RechnerFehler("Strom muss grösser als 0 sein")
    if w["Rs"] is None and w["Us"] is None:
        raise RechnerFehler("Shunt R_S oder Sollspannung U_soll eingeben (die andere wird berechnet)")
    r_s = w["Rs"] if w["Rs"] is not None else w["Us"] / w["I"]
    u_s = w["I"] * r_s
    e = _fehler_umwandeln(ntm.stromquelle_opv, u_s, r_s, w["Ub"], w["RL"] or 0.0)
    zeilen = [f"U_soll = I · R_S = {fmt(u_s, 'spannung')} bei R_S = {fmt(r_s, 'widerstand')}   ·   "
              f"Shunt-Leistung {fmt(w['I'] ** 2 * r_s, 'leistung')}",
              f"Regelt bis R_Last ≤ U_B / I − R_S = {fmt(e['r_last_max'], 'widerstand')}",
              f"MOSFET-Verlust: max. {fmt(e['p_mos_max'], 'leistung')} (Last kurzgeschlossen)"]
    if w["RL"] is not None:
        zeilen.append(f"Mit R_L = {fmt(w['RL'], 'widerstand')}: I = {fmt(e['i'], 'strom')}, MOSFET {fmt(e['p_mos'], 'leistung')}"
                      + ("" if e["regelt"] else "  ⚠ Last zu gross – Strom erreicht den Sollwert nicht"))
    if u_s < 0.05:
        zeilen.append("⚠ U_soll < 50 mV: Offset des OPV (mV) wird ein grosser Fehler → OPV mit kleinem Offset")
    return zeilen


def stromquelle_opv(master):
    return FormelRechner(
        master, "Geregelte Stromquelle (OPV + MOSFET)", "Low-Side-Stromsenke: I = U_soll / R_S",
        felder=[("I", "Strom I", "strom", {"einheit": "mA", "platzhalter": "z.B. 100"}),
                ("Rs", "Shunt R_S (opt.)", "widerstand", {"platzhalter": "z.B. 1"}),
                ("Us", "U_soll (opt.)", "spannung", {"einheit": "mV", "platzhalter": "statt R_S"}),
                ("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 12"}),
                ("RL", "Last R_L (opt.)", "widerstand", {"platzhalter": "optional"})],
        berechnen=_stromquelle_opv, formel="I = U_soll / R_S     R_L,max = U_B / I − R_S")


# =============================================================================
# 23) SCHALTREGLER
# =============================================================================
def _schaltregler(w):
    if None in (w["Ue"], w["Ua"], w["Ia"], w["f"]):
        raise RechnerFehler("U_e, U_a, Ausgangsstrom und Schaltfrequenz eingeben")
    l = w["L"]
    if l is None:
        # L so wählen, dass ΔI = 30 % des Spulenstroms
        probe = _fehler_umwandeln(ntm.schaltregler, w["art"], w["Ue"], w["Ua"], w["Ia"], w["f"], 1e-6)
        l = probe["l_30"]
    e = _fehler_umwandeln(ntm.schaltregler, w["art"], w["Ue"], w["Ua"], w["Ia"], w["f"], l, w["C"])
    buck = w["art"] == ntm.SCHALTREGLER_ARTEN[0]
    zeilen = [f"D = {'U_a / U_e' if buck else '1 − U_e / U_a'} = {e['d'] * 100:.1f} %   ·   "
              f"Spulenstrom Ø {fmt(e['i_l'], 'strom')}" + ("" if buck else " = I_a / (1 − D)")]
    if w["L"] is None:
        zeilen.append(f"L für ΔI = 30 %: {fmt(l, 'induktivitaet')}  →  nächster Normwert darüber")
    zeilen += [f"ΔI = {'(U_e − U_a) · D' if buck else 'U_e · D'} / (f · L) = {fmt(e['delta_i'], 'strom')}   ·   "
               f"Spitzenstrom {fmt(e['i_spitze'], 'strom')} (Sättigungsstrom der Spule ≥ diesem Wert)"]
    if e["delta_u"] is not None:
        zeilen.append(f"Ausgangswelligkeit ΔU ≈ {'ΔI / (8 · f · C)' if buck else 'I_a · D / (f · C)'} = "
                      f"{fmt(e['delta_u'], 'spannung')} (ohne ESR)")
    if not e["ccm"]:
        zeilen.append("⚠ Lückbetrieb: ΔI / 2 > Ø-Strom – D stellt sich anders ein, grössere Spule für Dauerbetrieb")
    return zeilen


def schaltregler(master):
    return FormelRechner(
        master, "Schaltregler Buck / Boost", "Idealer Wandler im Dauerbetrieb – leeres L wird für 30 % Rippel berechnet",
        felder=[("art", "Wandler", "auswahl", {"werte": ntm.SCHALTREGLER_ARTEN}),
                ("Ue", "Eingang U_e", "spannung", {"platzhalter": "z.B. 12"}),
                ("Ua", "Ausgang U_a", "spannung", {"platzhalter": "z.B. 5"}),
                ("Ia", "Ausgangsstrom I_a", "strom", {"einheit": "A", "platzhalter": "z.B. 1"}),
                ("f", "Schaltfrequenz f", "frequenz", {"einheit": "kHz", "platzhalter": "z.B. 100"}),
                ("L", "Spule L (opt.)", "induktivitaet", {"einheit": "µH", "platzhalter": "leer = berechnen"}),
                ("C", "Ausgangs-C (opt.)", "kapazitaet", {"einheit": "µF", "platzhalter": "optional"})],
        berechnen=_schaltregler, formel="Buck: U_a = D · U_e     Boost: U_a = U_e / (1 − D)     ΔI = U_L · t / L")


# =============================================================================
# FILTER 2. ORDNUNG
# =============================================================================
def _filter_bei_f(art, f0, q, w, zeilen):
    """Gemeinsam: Dämpfung und Ausgangsspannung bei einer Frequenz f (falls eingegeben)."""
    if w["f"] is None:
        return
    g = _fehler_umwandeln(fm.frequenzgang, art, f0, q, w["f"])
    zeilen.append(f"Bei f = {fmt(w['f'], 'frequenz')}: |H| = {g['betrag']:.4g} = {g['db']:.1f} dB   ·   "
                  f"φ = {g['phase']:+.0f}°" + (f"   ·   Ua = {fmt(g['betrag'] * w['Ue'], 'spannung')}"
                                               if w.get("Ue") is not None else ""))


def _lc_filter(w):
    if None in (w["L"], w["C"], w["R"]):
        raise RechnerFehler("L, C und den Lastwiderstand R_L eingeben")
    e = _fehler_umwandeln(fm.lc_tiefpass, w["L"], w["C"], w["R"])
    k = fm.kennwerte("Tiefpass", e["f0"], e["q"])
    zeilen = [f"f0 = 1 / (2π · √(L · C)) = {fmt(e['f0'], 'frequenz')}",
              f"Z0 = √(L / C) = {fmt(e['z0'], 'widerstand')}   ·   Q = R_L / Z0 = {e['q']:.3g}  → {k['charakter']}",
              f"−3 dB bei {fmt(k['f_3db'], 'frequenz')}   ·   darüber −40 dB pro Dekade"]
    if k["f_max"]:
        zeilen.append(f"⚠ Überhöhung {20 * math.log10(k['ueberhoehung']):.1f} dB (×{k['ueberhoehung']:.2f}) bei "
                      f"{fmt(k['f_max'], 'frequenz')} – für Q = 0.707 bräuchte es R_L = {fmt(0.7071 * e['z0'], 'widerstand')}")
    _filter_bei_f("Tiefpass", e["f0"], e["q"], w, zeilen)
    return zeilen


def lc_filter(master):
    return FormelRechner(
        master, "LC-Tiefpass mit Last", "Grenzfrequenz, Güte und Überhöhung – die Last bestimmt die Dämpfung",
        felder=[("L", "Induktivität L", "induktivitaet", {"einheit": "mH"}),
                ("C", "Kapazität C", "kapazitaet", {"einheit": "µF"}),
                ("R", "Lastwiderstand R_L", "widerstand", {"einheit": "Ω"}),
                ("f", "Frequenz f (opt.)", "frequenz", {"platzhalter": "optional"})],
        berechnen=_lc_filter, formel="f0 = 1 / (2π√(LC))     Q = R_L · √(C/L)     |H| = 1 / √((1 − x²)² + (x/Q)²)")


def _schwingkreis_filter(w):
    if None in (w["R"], w["L"], w["C"]):
        raise RechnerFehler("R, L und C eingeben")
    e = _fehler_umwandeln(fm.rlc_reihe, w["R"], w["L"], w["C"])
    k = fm.kennwerte(w["art"], e["f0"], e["q"])
    zeilen = [f"f0 = 1 / (2π · √(L · C)) = {fmt(e['f0'], 'frequenz')}   ·   Z0 = √(L / C) = {fmt(e['z0'], 'widerstand')}",
              f"Q = Z0 / R = {e['q']:.3g}   ·   Bandbreite B = f0 / Q = {fmt(k['bandbreite'], 'frequenz')}",
              f"−3-dB-Frequenzen: {fmt(k['f_unten'], 'frequenz')} und {fmt(k['f_oben'], 'frequenz')}"]
    if w["art"] == "Bandpass":
        zeilen.append("Bei f0 heben sich X_L und X_C auf: Der Kreis wirkt wie R allein → Ua = Ue")
    else:
        zeilen.append("Bei f0 ist die Reihenschaltung L + C ein Kurzschluss → Ua = 0 (ideal, ohne Spulenwiderstand)")
    _filter_bei_f(w["art"], e["f0"], e["q"], w, zeilen)
    return zeilen


def schwingkreis_filter(master):
    return FormelRechner(
        master, "Schwingkreis als Bandpass / Bandsperre", "RLC-Reihenkreis: Resonanz, Güte und Bandbreite",
        felder=[("art", "Ausgang", "auswahl", {"werte": ["Bandpass", "Bandsperre"]}),
                ("R", "Widerstand R", "widerstand", {"einheit": "Ω"}),
                ("L", "Induktivität L", "induktivitaet", {"einheit": "mH"}),
                ("C", "Kapazität C", "kapazitaet", {"einheit": "µF"}),
                ("f", "Frequenz f (opt.)", "frequenz", {"platzhalter": "optional"})],
        berechnen=_schwingkreis_filter, formel="f0 = 1 / (2π√(LC))     Q = √(L/C) / R     B = f0 / Q")


def _sallen_key(w):
    if w["f0"] is None:
        raise RechnerFehler("Grenzfrequenz f0 eingeben")
    q = fm.CHARAKTERISTIKEN[w["typ"]]
    tiefpass = w["art"] == "Tiefpass"
    if tiefpass and w["R"] is None:
        raise RechnerFehler("Beim Tiefpass den Widerstand R (= R1 = R2) vorgeben, z.B. 10 kΩ")
    if not tiefpass and w["C"] is None:
        raise RechnerFehler("Beim Hochpass die Kapazität C (= C1 = C2) vorgeben, z.B. 10 nF")
    e = _fehler_umwandeln(fm.sallen_key_auslegen, w["art"], w["f0"], q, w["R"], w["C"])
    i, n = e["ideal"], e["norm"]
    w0 = f"ω0 = 2π · {fmt(w['f0'], 'frequenz')}"
    if tiefpass:
        zeilen = [f"R1 = R2 = {fmt(n['r1'], 'widerstand')}   ·   {w0}   ·   Q = {q:.3f}",
                  f"C1 = 2Q / (ω0 · R) = {fmt(i['c1'], 'kapazitaet')} → Normwert {fmt(n['c1'], 'kapazitaet')}",
                  f"C2 = 1 / (2Q · ω0 · R) = {fmt(i['c2'], 'kapazitaet')} → Normwert {fmt(n['c2'], 'kapazitaet')}"]
    else:
        zeilen = [f"C1 = C2 = {fmt(n['c1'], 'kapazitaet')}   ·   {w0}   ·   Q = {q:.3f}",
                  f"R1 = 1 / (2Q · ω0 · C) = {fmt(i['r1'], 'widerstand')} → Normwert {fmt(n['r1'], 'widerstand')}",
                  f"R2 = 2Q / (ω0 · C) = {fmt(i['r2'], 'widerstand')} → Normwert {fmt(n['r2'], 'widerstand')}"]
    zeilen.append(f"Mit Normwerten: f0 = {fmt(e['f0_ist'], 'frequenz')} ({(e['f0_ist'] / w['f0'] - 1) * 100:+.1f} %), "
                  f"Q = {e['q_ist']:.3f}")
    if (n["c1"] if tiefpass else n["r1"]) != (i["c1"] if tiefpass else i["r1"]) and abs(e["q_ist"] / q - 1) > 0.05:
        zeilen.append("Hinweis: Q weicht > 5 % ab – Kondensatoren aus E24 oder zwei parallel schalten")
    return zeilen


def sallen_key(master):
    return FormelRechner(
        master, "Sallen-Key-Filter auslegen", "Aktiver Tief- oder Hochpass 2. Ordnung mit OPV als Spannungsfolger",
        felder=[("art", "Filter", "auswahl", {"werte": ["Tiefpass", "Hochpass"]}),
                ("typ", "Charakteristik", "auswahl", {"werte": list(fm.CHARAKTERISTIKEN), "standard":
                                                      "Butterworth (Q = 0.707)"}),
                ("f0", "Grenzfrequenz f0", "frequenz", {"platzhalter": "z.B. 1k"}),
                ("R", "R1 = R2 (Tiefpass)", "widerstand", {"einheit": "kΩ", "platzhalter": "z.B. 10"}),
                ("C", "C1 = C2 (Hochpass)", "kapazitaet", {"einheit": "nF", "platzhalter": "z.B. 10"})],
        berechnen=_sallen_key, formel="TP: C1 = 2Q / (ω0·R), C2 = 1 / (2Q·ω0·R)     HP: R1 = 1 / (2Q·ω0·C), R2 = 2Q / (ω0·C)")


# =============================================================================
# SENSOR-MESSSCHALTUNGEN
# =============================================================================
RHO_CU = 0.0178                                   # Ω·mm²/m, Kupfer bei 20 °C


def _pt_leitung(w):
    for name in ("l", "a"):
        if w[name] is None:
            raise RechnerFehler("Leitungslänge (einfach) und Querschnitt eingeben")
    if w["a"] <= 0 or w["l"] < 0:
        raise RechnerFehler("Länge ≥ 0 und Querschnitt > 0 eingeben")
    r_l = RHO_CU * w["l"] / w["a"]
    t = w["T"] if w["T"] is not None else 25.0
    r0 = 1000.0 if w["typ"].startswith("Pt1000") else 100.0
    zeilen = [f"R_L je Ader = ρ · l / A = 0.0178 Ω·mm²/m · {w['l']:g} m / {w['a']:g} mm² = {fmt(r_l, 'widerstand')}"]
    for art in mm.PT_ARTEN:
        e = _fehler_umwandeln(mm.pt_leitung, art, t, r0, r_l, 0.0, 1e-9)
        fehler = f"{e['fehler_leitung'] + 0.0:+.2f}".replace("-", "−").replace("−0.00", "+0.00")
        zeilen.append(f"  {art}: Fehler {fehler} K" + ("   (gleich lange Adern)" if art == "3-Leiter" else ""))
    zeilen.append(f"{w['typ'].split()[0]}: {r0 * 0.00385:g} Ω/K – beim Pt1000 ist derselbe Leitungsfehler 10× kleiner")
    return zeilen


def pt_leitung(master):
    return FormelRechner(
        master, "Pt100/Pt1000: Leitungsfehler", "Wie viel Kelvin kostet die Zuleitung in 2-, 3- und 4-Leiter-Schaltung?",
        felder=[("typ", "Sensor", "auswahl", {"werte": ["Pt100", "Pt1000"]}),
                ("l", "Leitungslänge (einfach) in m", "zahl", {"platzhalter": "z.B. 20"}),
                ("a", "Querschnitt in mm²", "zahl", {"platzhalter": "z.B. 0.25"}),
                ("T", "Temperatur (opt.)", "temperatur", {"platzhalter": "25"})],
        berechnen=_pt_leitung, formel="R_L = ρ · l / A     2-Leiter: Fehler = 2·R_L / (0.385 Ω/K)  (Pt100)")


def _ntc_teiler(w):
    for name in ("R25", "B", "T1", "T2"):
        if w[name] is None:
            raise RechnerFehler("R25, B-Wert und den Temperaturbereich T1 … T2 eingeben")
    r_fix = _fehler_umwandeln(mm.ntc_linear_r, w["R25"], w["B"], w["T1"], w["T2"])
    norm = normreihen.naechste_werte(r_fix, "E24")[2]
    u_b = w["Ub"] if w["Ub"] is not None else 3.3
    zeilen = [f"R_fix = (R1·R2 + R2·R3 − 2·R1·R3) / (R1 + R3 − 2·R2) = {fmt(r_fix, 'widerstand')} → E24: "
              f"{fmt(norm, 'widerstand')}"]
    for t in (w["T1"], (w["T1"] + w["T2"]) / 2, w["T2"]):
        e = _fehler_umwandeln(mm.ntc_teiler, t, w["R25"], w["B"], norm, u_b, True, 12)
        zeilen.append(f"  {t:g} °C: R_NTC = {fmt(e['r_ntc'], 'widerstand')}, U = {fmt(e['u_aus'], 'spannung')}, "
                      f"{abs(e['steigung']) * 1e3:.1f} mV/K, {e['stufen_pro_k']:.1f} Stufen/K (12 Bit)")
    zeilen.append("NTC unten (gegen GND), R_fix oben an U_B – U_ref des ADC = U_B (ratiometrisch)")
    return zeilen


def ntc_teiler(master):
    return FormelRechner(
        master, "NTC-Spannungsteiler auslegen", "Festwiderstand, der den Teiler im Messbereich am besten linearisiert",
        felder=[("R25", "NTC R25", "widerstand", {"einheit": "kΩ", "platzhalter": "z.B. 10"}),
                ("B", "B-Wert", "zahl", {"platzhalter": "z.B. 3950"}),
                ("T1", "Bereich von T1", "temperatur", {"platzhalter": "z.B. 0"}),
                ("T2", "bis T2", "temperatur", {"platzhalter": "z.B. 100"}),
                ("Ub", "Versorgung U_B (opt.)", "spannung", {"platzhalter": "3.3"})],
        berechnen=_ntc_teiler, formel="R_fix = (R1R2 + R2R3 − 2R1R3) / (R1 + R3 − 2R2),  R1/R2/R3 bei T1, Mitte, T2")


def _dms_verstaerker(w):
    for name in ("kw", "Ue", "Ua"):
        if w[name] is None:
            raise RechnerFehler("Nennkennwert (mV/V), Speisespannung und gewünschte Ausgangsspanne eingeben")
    if w["kw"] <= 0 or w["Ue"] <= 0 or w["Ua"] <= 0:
        raise RechnerFehler("Alle Werte müssen grösser als 0 sein")
    u_d = w["kw"] * 1e-3 * w["Ue"]
    g = w["Ua"] / u_d
    r_intern = mm.INAMPS[w["ina"]]
    if g <= 1:
        raise RechnerFehler(f"Signal {fmt(u_d, 'spannung')} braucht keine Verstärkung > 1")
    r_g = mm.inamp_verstaerkung(g=g, r_intern=r_intern)
    norm = normreihen.naechste_werte(r_g, "E24")[1]               # nächst grösserer -> G etwas kleiner, keine Übersteuerung
    g_ist = 1 + r_intern / norm
    zeilen = [f"Brückensignal bei Nennlast: U_d = {w['kw']:g} mV/V · {fmt(w['Ue'], 'spannung')} = {fmt(u_d, 'spannung')}",
              f"G = U_a / U_d = {fmt(w['Ua'], 'spannung')} / {fmt(u_d, 'spannung')} = {g:.4g}",
              f"R_G = {fmt(r_intern, 'widerstand')} / (G − 1) = {fmt(r_g, 'widerstand')} → E24 (nächst grösser) "
              f"{fmt(norm, 'widerstand')} → G = {g_ist:.4g}, U_a = {fmt(g_ist * u_d, 'spannung')}",
              "REF: 0 V nur für Zug/Last in eine Richtung, sonst Mitte des ADC-Bereichs (z.B. U_B/2 über Puffer)",
              f"Gleichtaktspannung U_e/2 = {fmt(w['Ue'] / 2, 'spannung')} muss im Eingangsbereich des Verstärkers liegen"]
    return zeilen


def dms_verstaerker(master):
    return FormelRechner(
        master, "DMS-Brücke: Instrumentenverstärker auslegen", "Wägezelle mit Nennkennwert in mV/V auf den ADC-Bereich",
        felder=[("kw", "Nennkennwert (mV/V)", "zahl", {"platzhalter": "z.B. 2"}),
                ("Ue", "Brückenspeisung U_e", "spannung", {"platzhalter": "z.B. 5"}),
                ("Ua", "gewünschte Ausgangsspanne", "spannung", {"platzhalter": "z.B. 2"}),
                ("ina", "Instrumentenverstärker", "auswahl", {"werte": list(mm.INAMPS)})],
        berechnen=_dms_verstaerker, formel="U_d = Kennwert · U_e     G = U_a / U_d     R_G = R_intern / (G − 1)")


# =============================================================================
# SCHNITTSTELLEN UND LEISTUNG
# =============================================================================
def _pegelteiler(w):
    for name in ("Uh", "Uz", "R1"):
        if w[name] is None:
            raise RechnerFehler("Hohe Spannung, Zielspannung und R1 eingeben")
    if not 0 < w["Uz"] < w["Uh"]:
        raise RechnerFehler("Die Zielspannung muss zwischen 0 und der hohen Spannung liegen")
    r2 = w["R1"] * w["Uz"] / (w["Uh"] - w["Uz"])
    norm = normreihen.naechste_werte(r2, "E24")[2]
    e = _fehler_umwandeln(sm.pegel_teiler, w["Uh"], w["R1"], norm, w["C"] or 10e-12)
    return [f"R2 = R1 · U_Ziel / (U_hoch − U_Ziel) = {fmt(r2, 'widerstand')} → E24: {fmt(norm, 'widerstand')}",
            f"U = {fmt(e['u_aus'], 'spannung')}   ·   Querstrom {fmt(e['i'], 'strom')}",
            f"t_r = 2.2 · (R1 ∥ R2) · C = {fmt(e['t_r'], 'zeit')} → bis ca. {fmt(e['f_max'], 'frequenz')}",
            "Nur in eine Richtung (hoch -> niedrig). Für I²C/bidirektional: MOSFET-Pegelwandler"]


def pegelteiler(master):
    return FormelRechner(
        master, "Pegelanpassung mit Spannungsteiler", "z.B. 5-V-Ausgang an 3.3-V-Eingang",
        felder=[("Uh", "hohe Spannung (Ausgang)", "spannung", {"platzhalter": "z.B. 5"}),
                ("Uz", "Zielspannung (Eingang)", "spannung", {"platzhalter": "z.B. 3.3"}),
                ("R1", "R1 (oben)", "widerstand", {"einheit": "kΩ", "platzhalter": "z.B. 10"}),
                ("C", "Eingangskapazität (opt.)", "kapazitaet", {"einheit": "pF", "platzhalter": "10"})],
        berechnen=_pegelteiler, formel="R2 = R1 · U_Ziel / (U_hoch − U_Ziel)     t_r = 2.2 · (R1∥R2) · C")


def _optokoppler(w):
    for name in ("Ue", "If", "ctr", "Ub"):
        if w[name] is None:
            raise RechnerFehler("U_e, LED-Strom, CTR und Ausgangsspannung eingeben")
    u_f = w["Uf"] if w["Uf"] is not None else 1.2
    e = _fehler_umwandeln(sm.optokoppler_auslegen, w["Ue"], u_f, w["If"], w["ctr"] / 100, w["Ub"])
    norm_rv = normreihen.naechste_werte(e["r_v"], "E24")[2]
    norm_rl = normreihen.naechste_werte(e["r_l_min"], "E24")[1]
    return [f"R_V = (U_e − U_F) / I_F = ({fmt(w['Ue'], 'spannung')} − {u_f:g} V) / {fmt(w['If'], 'strom')} = "
            f"{fmt(e['r_v'], 'widerstand')} → E24 {fmt(norm_rv, 'widerstand')}, P = {fmt(e['p_rv'], 'leistung')}",
            f"CTR mit Alterung: {w['ctr']:g} % · 0.5 = {e['ctr_eff'] * 100:g} % → I_C = {fmt(e['i_c'], 'strom')}",
            f"Pull-up R_L ≥ (U_B − 0.3 V) / I_C = {fmt(e['r_l_min'], 'widerstand')} → z.B. {fmt(norm_rl, 'widerstand')} "
            "(grösser = sicherer gesättigt, aber langsamer)",
            "Grosse R_L machen den Optokoppler langsam (Schaltzeiten einige 10 µs) – für schnelle Signale Typen mit "
            "Logik-Ausgang verwenden"]


def optokoppler(master):
    return FormelRechner(
        master, "Optokoppler auslegen", "Vorwiderstand und Pull-up für ein sicheres LOW am Ausgang",
        felder=[("Ue", "Eingangsspannung U_e", "spannung", {"platzhalter": "z.B. 24"}),
                ("Uf", "LED-Flussspannung (opt.)", "spannung", {"platzhalter": "1.2"}),
                ("If", "LED-Strom I_F", "strom", {"einheit": "mA", "platzhalter": "z.B. 5"}),
                ("ctr", "CTR min. in %", "zahl", {"platzhalter": "z.B. 50"}),
                ("Ub", "Versorgung Ausgang U_B", "spannung", {"platzhalter": "z.B. 3.3"})],
        berechnen=_optokoppler, formel="R_V = (U_e − U_F) / I_F     R_L ≥ (U_B − U_CE,sat) / (CTR · 0.5 · I_F)")


def _h_bruecke(w):
    for name in ("Ub", "I", "Rds"):
        if w[name] is None:
            raise RechnerFehler("U_B, Motorstrom und R_DS(on) eingeben")
    f = w["f"] if w["f"] is not None else 20e3
    t_sw = w["tsw"] if w["tsw"] is not None else 100e-9
    e = _fehler_umwandeln(sm.h_verluste, w["Ub"], w["I"], w["Rds"], f, t_sw)
    return [f"Leitverluste: I² · 2 · R_DS = {fmt(w['I'], 'strom')}² · 2 · {fmt(w['Rds'], 'widerstand')} = "
            f"{fmt(e['p_leit'], 'leistung')} (je leitender Schalter die Hälfte)",
            f"Schaltverluste ≈ U_B · I · t_sw · f = {fmt(e['p_schalt'], 'leistung')}  (t_sw = {fmt(t_sw, 'zeit')}, "
            f"f = {fmt(f, 'frequenz')})",
            f"Summe ≈ {fmt(e['p_gesamt'], 'leistung')} → Kühlung danach auslegen",
            f"Totzeit im Treiber > Ausschaltzeit der MOSFETs (typ. 100 ns … 1 µs), sonst Brückenkurzschluss"]


def h_bruecke(master):
    return FormelRechner(
        master, "H-Brücke: Verluste", "Wie warm werden die vier Schalter?",
        felder=[("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 24"}),
                ("I", "Motorstrom", "strom", {"platzhalter": "z.B. 5"}),
                ("Rds", "R_DS(on) je Schalter", "widerstand", {"einheit": "mΩ", "platzhalter": "z.B. 20"}),
                ("f", "PWM-Frequenz (opt.)", "frequenz", {"platzhalter": "20 kHz"}),
                ("tsw", "Schaltzeit t_sw (opt.)", "zeit", {"einheit": "ns", "platzhalter": "100"})],
        berechnen=_h_bruecke, formel="P_L = I² · 2 · R_DS     P_S ≈ U_B · I · t_sw · f")


def _gate_schaltzeit(w):
    for name in ("Udr", "Rg", "Qgd", "Upl"):
        if w[name] is None:
            raise RechnerFehler("Treiberspannung, R_G, Q_gd und Plateauspannung eingeben")
    if w["Udr"] <= w["Upl"]:
        raise RechnerFehler(f"U_Tr = {fmt(w['Udr'], 'spannung')} liegt nicht über dem Plateau – der MOSFET schaltet "
                            "nicht durch (Logic-Level-Typ oder höhere Treiberspannung)")
    if w["Rg"] <= 0 or w["Qgd"] <= 0:
        raise RechnerFehler("R_G und Q_gd müssen grösser als 0 sein")
    i_g = (w["Udr"] - w["Upl"]) / w["Rg"]
    t = w["Qgd"] / i_g
    zeilen = [f"Gate-Strom im Plateau I_G = (U_Tr − U_pl) / R_G = {fmt(i_g, 'strom')}",
              f"Plateaudauer t = Q_gd / I_G = {fmt(t, 'zeit')} (in dieser Zeit fällt U_DS)"]
    if None not in (w["Uds"], w["Id"], w["f"]):
        p = w["Uds"] * w["Id"] * t * w["f"]
        zeilen.append(f"Schaltverlust ≈ U_DS · I_D · t · f (Ein + Aus je ½) = {fmt(p, 'leistung')}")
    return zeilen


def gate_schaltzeit(master):
    return FormelRechner(
        master, "MOSFET: Schaltzeit und Schaltverlust", "Wie lange dauert das Miller-Plateau?",
        felder=[("Udr", "Treiberspannung U_Tr", "spannung", {"platzhalter": "z.B. 12"}),
                ("Rg", "R_G (inkl. Treiber)", "widerstand", {"einheit": "Ω", "platzhalter": "z.B. 10"}),
                ("Qgd", "Q_gd (Datenblatt)", "ladung", {"einheit": "nC", "platzhalter": "z.B. 25"}),
                ("Upl", "Plateauspannung U_pl", "spannung", {"platzhalter": "z.B. 4.5"}),
                ("Uds", "U_DS (opt.)", "spannung", {"platzhalter": "optional"}),
                ("Id", "I_D (opt.)", "strom", {"platzhalter": "optional"}),
                ("f", "Schaltfrequenz (opt.)", "frequenz", {"platzhalter": "optional"})],
        berechnen=_gate_schaltzeit, formel="t = Q_gd · R_G / (U_Tr − U_pl)     P ≈ U_DS · I_D · t · f")


def _bootstrap(w):
    if w["Qg"] is None or w["Udd"] is None:
        raise RechnerFehler("Gate-Ladung und Treiberversorgung eingeben")
    t_ein = w["ton"] if w["ton"] is not None else 1e-3
    du = w["du"] if w["du"] is not None else 0.5
    e = _fehler_umwandeln(sm.bootstrap, w["Qg"], w["Udd"], 10e-6, t_ein, du)
    norm = normreihen.naechste_werte(e["c_empf"], "E12")[1]
    return [f"Q = Q_g + I_leck · t_ein = {fmt(w['Qg'], 'ladung')} + 10 µA · {fmt(t_ein, 'zeit')} = {fmt(e['q'], 'ladung')}",
            f"C ≥ Q / ΔU = {fmt(e['c_min'], 'kapazitaet')}  → mit Faktor 2: {fmt(e['c_empf'], 'kapazitaet')} → "
            f"{fmt(norm, 'kapazitaet')} (Keramik X7R, niedriger ESR)",
            f"Spannung am Bootstrap-C ≈ U_DD − U_Diode = {fmt(e['u_boot'], 'spannung')}",
            "Der Low-Side-Schalter muss regelmässig einschalten, damit der Kondensator nachladen kann (kein 100 % Tastgrad)"]


def bootstrap(master):
    return FormelRechner(
        master, "Bootstrap-Kondensator", "High-Side-Treiber: Welcher Kondensator versorgt das Gate?",
        felder=[("Qg", "Gate-Ladung Q_g", "ladung", {"einheit": "nC", "platzhalter": "z.B. 70"}),
                ("Udd", "Treiberversorgung U_DD", "spannung", {"platzhalter": "z.B. 12"}),
                ("ton", "längste Einschaltzeit (opt.)", "zeit", {"einheit": "ms", "platzhalter": "1 ms"}),
                ("du", "zulässiger Spannungseinbruch (opt.)", "spannung", {"platzhalter": "0.5 V"})],
        berechnen=_bootstrap, formel="C ≥ 2 · (Q_g + I_leck · t_ein) / ΔU")


def _adc_eingang(w):
    for name in ("ts", "cs", "N"):
        if w[name] is None:
            raise RechnerFehler("Abtastzeit, Abtastkondensator und Auflösung (Bit) eingeben")
    if w["N"] != int(w["N"]) or not 4 <= w["N"] <= 24:
        raise RechnerFehler("Auflösung: ganze Zahl 4 … 24 Bit")
    r_sw = w["rsw"] if w["rsw"] is not None else 1e3
    e = _fehler_umwandeln(sm.adc_abtastung, 1.0, 0.0, 0.0, r_sw, w["cs"], w["ts"], int(w["N"]), 1.0)
    n = int(w["N"])
    return [f"ln(2^(N+1)) = {math.log(2 ** (n + 1)):.2f} Zeitkonstanten für ½ LSB",
            f"Ohne C_ext: R_Quelle ≤ t_s / (C_S · ln 2^(N+1)) − R_sw = {fmt(e['r_max'], 'widerstand')}",
            f"Mit C_ext am Pin: C_ext ≥ (2^(N+1) − 1) · C_S = {fmt(e['c_ext_min'], 'kapazitaet')}",
            "Mit C_ext muss die Quelle das C zwischen zwei Abtastungen nachladen – das begrenzt die Abtastrate "
            "(Grafik „ADC-Eingang“)"]


def adc_eingang(master):
    return FormelRechner(
        master, "ADC-Eingang: Quellwiderstand und C_ext", "Wird der Abtastkondensator auf ½ LSB genau geladen?",
        felder=[("ts", "Abtastzeit t_s", "zeit", {"einheit": "µs", "platzhalter": "z.B. 1"}),
                ("cs", "Abtastkondensator C_S", "kapazitaet", {"einheit": "pF", "platzhalter": "z.B. 10"}),
                ("N", "Auflösung N (Bit)", "zahl", {"platzhalter": "z.B. 12"}),
                ("rsw", "Schalterwiderstand R_sw (opt.)", "widerstand", {"einheit": "kΩ", "platzhalter": "1 kΩ"})],
        berechnen=_adc_eingang, formel="R ≤ t_s / (C_S · ln 2^(N+1)) − R_sw     C_ext ≥ (2^(N+1) − 1) · C_S")


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
    "innenwiderstand": innenwiderstand,
    "netzteil_auslegen": netzteil_auslegen,
    "linearregler": linearregler,
    "lm317": lm317,
    "strombegrenzung": strombegrenzung,
    "stromquelle_opv": stromquelle_opv,
    "schaltregler": schaltregler,
    "schaltung_quelle": QuelleSchaltung,
    "schaltung_linearregler": LinearreglerSchaltung,
    "schaltung_strombegrenzung": StrombegrenzungSchaltung,
    "schaltung_stromquelle_opv": StromquelleOpvSchaltung,
    "schaltung_virtuelle_masse": VirtuelleMasseSchaltung,
    "schaltung_schaltregler": SchaltreglerSchaltung,
    "lc_filter": lc_filter,
    "schwingkreis_filter": schwingkreis_filter,
    "sallen_key": sallen_key,
    "schaltung_lc_filter": LcFilterSchaltung,
    "schaltung_sallen_key": SallenKeySchaltung,
    "schaltung_schwingkreis": SchwingkreisSchaltung,
    "pt_leitung": pt_leitung,
    "ntc_teiler": ntc_teiler,
    "dms_verstaerker": dms_verstaerker,
    "pegelteiler": pegelteiler,
    "optokoppler": optokoppler,
    "h_bruecke": h_bruecke,
    "gate_schaltzeit": gate_schaltzeit,
    "bootstrap": bootstrap,
    "adc_eingang": adc_eingang,
    "schaltung_pt_leitung": PtLeitungSchaltung,
    "schaltung_ntc_teiler": NtcTeilerSchaltung,
    "schaltung_dms_kette": DmsKetteSchaltung,
    "schaltung_pegelwandler": PegelwandlerSchaltung,
    "schaltung_optokoppler": OptokopplerSchaltung,
    "schaltung_h_bruecke": HBrueckeSchaltung,
    "schaltung_gate_treiber": GateTreiberSchaltung,
    "schaltung_adc_eingang": AdcEingangSchaltung,
}
