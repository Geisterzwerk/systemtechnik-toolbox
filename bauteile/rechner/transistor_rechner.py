# =============================================================================
# bauteile/rechner/transistor_rechner.py
# -----------------------------------------------------------------------------
# ZUSATZ-RECHNER für die Seite "Bipolartransistor" (ergänzen halbleiter_rechner.py).
#
# Unten im Dictionary RECHNER steht: ID -> Funktion, die die Rechner-Karte baut.
# Die IDs werden in bauteile/inhalte/03_transistoren/bipolartransistor.py unter "rechner" benutzt.
#
#   basiswiderstand       R_B für NPN- ODER PNP-Schalter, mit Übersteuerung und E12-Normwert
#   arbeitspunkt          Schalter-Zustand prüfen: gesperrt, aktiv oder gesättigt?
#   verlustleistung       Durchlass- und Schaltverluste (auch mit PWM-Tastgrad)
#
# Simulator ("transistor_simulator") und Kühlkörper ("kuehlkoerper") stehen in halbleiter_rechner.py.
#
# Die eigentliche Mathe steht in transistor_mathe.py (ohne GUI, einzeln testbar).
# Hier werden nur Eingaben gelesen, Funktionen aufgerufen und Ergebnisse formatiert.
#
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py -> erstellen(master, "basiswiderstand")
# =============================================================================

from bauteile.rechner import transistor_mathe as tm                      # -> rechner/transistor_mathe.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt     # -> rechner/basis.py

TYP_NPN = "NPN (Low-Side)"
TYP_PNP = "PNP (High-Side)"


def _fehler_umwandeln(funktion, *args, **kwargs):
    """ValueError aus transistor_mathe.py als verständliche Meldung im Ergebnisfeld zeigen."""
    try:
        return funktion(*args, **kwargs)
    except ValueError as fehler:
        raise RechnerFehler(str(fehler)) from None


# =============================================================================
# 1) BASISWIDERSTAND (Transistor als Schalter)
# =============================================================================
def _basiswiderstand(w):
    npn = w["typ"] == TYP_NPN
    if w["Ub"] is None or w["B"] is None:
        raise RechnerFehler("U_B und B min eingeben")
    if w["Rl"] is None and w["Il"] is None:
        raise RechnerFehler("Lastwiderstand ODER Laststrom eingeben")
    if npn and w["Us"] is None:
        raise RechnerFehler("Steuerspannung (HIGH-Pegel) eingeben, z.B. 3.3 oder 5")
    u_steuer = w["Us"] if w["Us"] is not None else 0.0         # PNP: LOW-Pegel, leer = 0 V
    ue = w["ue"] or tm.UE_STANDARD

    e = _fehler_umwandeln(tm.schalter_dimensionieren, w["Ub"], u_steuer, w["B"], ue,
                          r_last=w["Rl"] if w["Il"] is None else None, i_last=w["Il"],
                          typ="NPN" if npn else "PNP")
    zeilen = [
        f"I_C = {fmt(e['i_c'], 'strom')}",
        f"I_B = ü · I_C / B = {fmt(e['i_b'], 'strom')}   (ü = {ue:g})",
        f"R_B = {fmt(e['u_rb'], 'spannung')} / I_B = {fmt(e['r_b'], 'widerstand')}",
        f"→ E12 (abgerundet): {fmt(e['r_b_norm'], 'widerstand')}   "
        f"→ I_B = {fmt(e['i_b_echt'], 'strom')}, ü = {e['ue_echt']:.1f}",
        f"P Transistor ≈ {fmt(e['p_t'], 'leistung')}   ·   P an R_B = {fmt(e['p_rb'], 'leistung')}",
    ]
    # ---- Hinweise ----
    if e["i_b_echt"] > 10e-3:
        zeilen.append("⚠ Basisstrom > 10 mA – viele µC-Pins schaffen das nicht → Darlington oder MOSFET")
    if e["i_c"] > 0.5:
        zeilen.append("⚠ Ab ca. 0.5 A besser einen Logic-Level-MOSFET verwenden (kaum Steuerstrom)")
    if not npn:
        zeilen.append("PNP ausschalten: Basis muss auf U_B – ist U_B grösser als die Steuerspannung, "
                      "braucht es einen NPN davor (Pegelwandler)")
    return zeilen


def basiswiderstand(master):
    return FormelRechner(
        master, "Basiswiderstand (Schalter)", "Transistor sicher in die Sättigung bringen – mit Übersteuerung",
        felder=[("typ", "Transistor", "auswahl", {"werte": [TYP_NPN, TYP_PNP]}),
                ("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 12"}),
                ("Rl", "Lastwiderstand", "widerstand", {"platzhalter": "z.B. 120"}),
                ("Il", "… oder Laststrom", "strom", {"einheit": "mA", "platzhalter": "statt R, z.B. 30"}),
                ("Us", "Steuerspannung", "spannung", {"platzhalter": "NPN: 3.3 · PNP: 0"}),
                ("B", "B min (hFE)", "zahl", {"platzhalter": "Datenblatt, z.B. 110"}),
                ("ue", "Übersteuerung ü", "zahl", {"platzhalter": "2 … 5 (leer = 3)"})],
        berechnen=_basiswiderstand,
        formel="I_C = (U_B − 0.2 V) / R_L     I_B = ü · I_C / B_min     R_B = (U_St − 0.7 V) / I_B")


# =============================================================================
# 2) ARBEITSPUNKT PRÜFEN
# =============================================================================
ZUSTAND_TEXT = {
    "gesperrt": "⭘ GESPERRT – Schalter offen, kein Strom",
    "aktiv": "⚠ AKTIV – nur halb offen, Transistor wird heiss → R_B verkleinern!",
    "gesättigt": "✅ GESÄTTIGT – voll durchgeschaltet",
}


def _arbeitspunkt(w):
    if None in (w["Ub"], w["Rl"], w["Us"], w["Rb"], w["B"]):
        raise RechnerFehler("Alle fünf Werte eingeben")
    if w["Ub"] <= tm.U_CE_SAT:
        raise RechnerFehler(f"U_B muss grösser als U_CE,sat = {tm.U_CE_SAT:g} V sein")
    a = _fehler_umwandeln(tm.arbeitspunkt, w["Ub"], w["Rl"], w["Us"], w["Rb"], w["B"])
    zeilen = [ZUSTAND_TEXT[a["zustand"]],
              f"I_B = {fmt(a['i_b'], 'strom')}   ·   I_C = {fmt(a['i_c'], 'strom')}  "
              f"(Last erlaubt max. {fmt(a['i_c_max'], 'strom')})",
              f"U_CE = {fmt(a['u_ce'], 'spannung')}   ·   P_T = {fmt(a['p_t'], 'leistung')}"]
    if a["zustand"] == "gesättigt":
        zeilen.append(f"Übersteuerungsfaktor ü = B · I_B / I_C = {a['ue']:.1f}"
                      + ("   (knapp – mit B min nachrechnen!)" if a["ue"] < 1.5 else ""))
    elif a["zustand"] == "aktiv":
        zeilen.append(f"Es fehlt Basisstrom: nur {a['ue'] * 100:.0f} % des nötigen Stroms")
    return zeilen


def arbeitspunkt(master):
    return FormelRechner(
        master, "Arbeitspunkt prüfen", "NPN-Schalter: gesperrt, aktiv oder gesättigt?",
        felder=[("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 12"}),
                ("Rl", "Lastwiderstand", "widerstand", {"platzhalter": "z.B. 120"}),
                ("Us", "Steuerspannung", "spannung", {"platzhalter": "z.B. 5"}),
                ("Rb", "Basiswiderstand", "widerstand", {"einheit": "kΩ", "platzhalter": "z.B. 4.7"}),
                ("B", "Stromverstärkung B", "zahl", {"platzhalter": "z.B. 100"})],
        berechnen=_arbeitspunkt, formel="I_B = (U_St − 0.7 V) / R_B     gesättigt, wenn B · I_B ≥ (U_B − 0.2 V) / R_L")


# =============================================================================
# 3) VERLUSTLEISTUNG
# =============================================================================
def _verlustleistung(w):
    if w["Uce"] is None or w["Ic"] is None:
        raise RechnerFehler("U_CE und I_C eingeben")
    tastgrad = w["D"] if w["D"] is not None else 1.0
    nur_teil = (w["f"] is None) != (w["t"] is None)
    v = _fehler_umwandeln(tm.verlustleistung, w["Uce"], w["Ic"], w["Ib"] or 0.0, tastgrad=tastgrad,
                          f=w["f"], t_schalt=w["t"], u_sperr=w["Ub"])
    zeilen = [f"Durchlassverlust P_D = {fmt(v['p_durchlass'], 'leistung')}"
              + (f"   (Tastgrad {tastgrad * 100:g} %)" if tastgrad < 1 else "")]
    if v["p_schalt"] is not None:
        zeilen.append(f"Schaltverlust P_S ≈ {fmt(v['p_schalt'], 'leistung')}")
        if w["Ub"] is None:
            zeilen.append("⚠ Ohne U_B wurde mit U_CE gerechnet – Schaltverlust viel zu klein!")
    elif nur_teil:
        zeilen.append("Für Schaltverluste f UND Schaltzeit eingeben")
    zeilen.append(f"GESAMT P_V = {fmt(v['p_gesamt'], 'leistung')}  → mit P_tot im Datenblatt vergleichen")
    if v["p_gesamt"] > 0.5:
        zeilen.append("⚠ Über 0.5 W: TO-92 ist überfordert → Kühlkörper-Rechner benutzen (gleiche Seite)")
    return zeilen


def verlustleistung(master):
    return FormelRechner(
        master, "Verlustleistung", "Wie viel Wärme entsteht im Transistor?",
        felder=[("Uce", "U_CE (leitend)", "spannung", {"platzhalter": "gesättigt ≈ 0.2"}),
                ("Ic", "Kollektorstrom I_C", "strom", {"einheit": "mA"}),
                ("Ib", "Basisstrom (opt.)", "strom", {"einheit": "mA", "platzhalter": "optional"}),
                ("D", "Tastgrad PWM (opt.)", "prozent", {"platzhalter": "leer = 100"}),
                ("f", "Schaltfrequenz (opt.)", "frequenz", {"einheit": "kHz", "platzhalter": "optional"}),
                ("t", "t_r + t_f (opt.)", "zeit", {"einheit": "ns", "platzhalter": "Datenblatt"}),
                ("Ub", "Sperrspannung U_B", "spannung", {"platzhalter": "für Schaltverlust"})],
        berechnen=_verlustleistung,
        formel="P_D = (U_CE · I_C + U_BE · I_B) · D     P_S ≈ ½ · U_B · I_C · (t_r + t_f) · f")


RECHNER = {
    "basiswiderstand": basiswiderstand,
    "arbeitspunkt": arbeitspunkt,
    "verlustleistung": verlustleistung,
}
