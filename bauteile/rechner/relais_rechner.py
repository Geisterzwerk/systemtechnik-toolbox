# =============================================================================
# bauteile/rechner/relais_rechner.py
# -----------------------------------------------------------------------------
# Alle RECHNER für die Seite "Relais".
#
# Unten im Dictionary RECHNER steht: ID -> Funktion, die die Rechner-Karte baut.
# Die ID wird in bauteile/inhalte/04_schalten/relais.py unter "rechner" benutzt.
#
#   relais_ansteuerung   Relais mit NPN vom µC schalten: Spulenstrom, R_B, Freilaufdiode
#   relais_temperatur    Zieht das Relais auch mit heisser Spule noch an?
#   freilauf             Diode vs. Diode + Z-Diode: Spannung am Transistor, Abfallzeit
#                        (auch auf den Seiten Diode und MOSFET benutzt)
#   kontakt_last         Einschaltstrom der Last (Lampe, Motor, Netzteil ...) abschätzen
#
# Die eigentliche Mathe steht in relais_mathe.py (ohne GUI, einzeln testbar).
#
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py -> erstellen(master, "relais_ansteuerung")
# =============================================================================

from bauteile.rechner import relais_mathe as rm                        # -> rechner/relais_mathe.py
from bauteile.rechner import transistor_mathe as tm                    # -> rechner/transistor_mathe.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt   # -> rechner/basis.py


def _fehler_umwandeln(funktion, *args, **kwargs):
    """ValueError aus relais_mathe.py als verständliche Meldung im Ergebnisfeld zeigen."""
    try:
        return funktion(*args, **kwargs)
    except ValueError as fehler:
        raise RechnerFehler(str(fehler)) from None


# =============================================================================
# 1) ANSTEUERUNG MIT TRANSISTOR
# =============================================================================
def _ansteuerung(w):
    if None in (w["Ub"], w["Rsp"], w["Us"], w["B"]):
        raise RechnerFehler("U_B, Spulenwiderstand, Steuerspannung und B min eingeben")
    ue = w["ue"] or tm.UE_STANDARD
    e = _fehler_umwandeln(rm.ansteuerung, w["Ub"], w["Rsp"], w["Us"], w["B"], ue)
    zeilen = [
        f"Spulenstrom I = {fmt(e['i_c'], 'strom')}   ·   an der Spule {fmt(e['u_spule'], 'spannung')}, "
        f"P = {fmt(e['p_spule'], 'leistung')}",
        f"I_B = ü · I / B = {fmt(e['i_b'], 'strom')}   (ü = {ue:g})",
        f"R_B = {fmt(e['r_b'], 'widerstand')}  → E12: {fmt(e['r_b_norm'], 'widerstand')}  "
        f"(I_B = {fmt(e['i_b_echt'], 'strom')})",
        f"Freilaufdiode antiparallel zur Spule: z.B. {e['diode']} (I_F ≥ {fmt(e['i_c'], 'strom')}, U_R ≥ "
        f"{fmt(w['Ub'], 'spannung')})",
        f"Transistor: I_C,max ≥ {fmt(1.5 * e['i_c'], 'strom')} und U_CE0 ≥ {fmt(2 * w['Ub'], 'spannung')} wählen",
    ]
    if e["i_c"] > 0.1:
        zeilen.append("BC547 reicht nicht (I_C,max 100 mA) → z.B. BC337 (800 mA) oder Logic-Level-MOSFET")
    if e["i_b_echt"] > 10e-3:
        zeilen.append("⚠ Basisstrom > 10 mA – zu viel für die meisten µC-Pins → Darlington, ULN2003 oder MOSFET")
    return zeilen


def relais_ansteuerung(master):
    return FormelRechner(
        master, "Relais mit Transistor ansteuern", "NPN als Low-Side-Schalter, Freilaufdiode nicht vergessen",
        felder=[("Ub", "Spulenspannung U_B", "spannung", {"platzhalter": "z.B. 5, 12, 24"}),
                ("Rsp", "Spulenwiderstand", "widerstand", {"platzhalter": "Datenblatt, z.B. 70"}),
                ("Us", "Steuerspannung (µC)", "spannung", {"platzhalter": "z.B. 3.3"}),
                ("B", "B min Transistor", "zahl", {"platzhalter": "z.B. 100"}),
                ("ue", "Übersteuerung ü", "zahl", {"platzhalter": "2 … 5 (leer = 3)"})],
        berechnen=_ansteuerung, formel="I = (U_B − 0.2 V) / R_Spule     R_B = (U_St − 0.7 V) / (ü · I / B_min)")


# =============================================================================
# 2) SPULE WARM
# =============================================================================
def _temperatur(w):
    if None in (w["Un"], w["R20"], w["T"]):
        raise RechnerFehler("Nennspannung, Spulenwiderstand und Temperatur eingeben")
    e = _fehler_umwandeln(rm.spule_warm, w["Un"], w["R20"], w["T"], w["an"] * 100 if w["an"] else 75.0, w["U"])
    zeilen = [
        f"Spulenwiderstand warm: {fmt(e['r_t'], 'widerstand')}  (kalt {fmt(w['R20'], 'widerstand')})",
        f"Strom: {fmt(e['i_20'], 'strom')} kalt → {fmt(e['i_t'], 'strom')} warm",
        f"Ansprechspannung: {fmt(e['u_an_20'], 'spannung')} bei 20 °C → {fmt(e['u_an_t'], 'spannung')} "
        f"bei {fmt(w['T'], 'temperatur')}",
    ]
    if e["ok"]:
        zeilen.append(f"✅ {fmt(e['u_spule'], 'spannung')} an der Spule reichen (Reserve {(e['reserve'] - 1) * 100:.0f} %)")
    else:
        zeilen.append(f"❌ Nur {fmt(e['u_spule'], 'spannung')} an der Spule – das Relais zieht warm nicht mehr sicher an!")
    return zeilen


def relais_temperatur(master):
    return FormelRechner(
        master, "Heisse Spule: zieht es noch an?", "Kupfer: +0.39 % Widerstand pro Kelvin",
        felder=[("Un", "Nennspannung U_N", "spannung", {"platzhalter": "z.B. 24"}),
                ("R20", "Spulenwiderstand 20 °C", "widerstand", {"platzhalter": "Datenblatt"}),
                ("T", "Spulentemperatur", "temperatur", {"platzhalter": "z.B. 85 (Schaltschrank)"}),
                ("an", "Ansprechspannung", "prozent", {"platzhalter": "leer = 75 % von U_N"}),
                ("U", "Spannung an Spule", "spannung", {"platzhalter": "leer = U_N (z.B. U_N − 10 %)"})],
        berechnen=_temperatur, formel="R_T = R_20 · (1 + 0.00393 · (T − 20 °C))     U_an,T = U_an,20 · R_T / R_20")


# =============================================================================
# 3) FREILAUF / ABSCHALTEN
# =============================================================================
def _freilauf(w):
    if w["Ub"] is None or w["Rsp"] is None:
        raise RechnerFehler("U_B und Spulenwiderstand eingeben")
    e = _fehler_umwandeln(rm.abschalten, w["Ub"], w["Rsp"], w["L"], w["Uz"])
    zeilen = [f"Spulenstrom vor dem Abschalten: {fmt(e['i'], 'strom')}"]
    if e["energie"] is not None:
        zeilen.append(f"Gespeicherte Energie ½ · L · I² = {fmt(e['energie'], 'energie')}   ·   τ = L / R = {fmt(e['tau'], 'zeit')}")
    zeilen.append("Ohne Schutz: Spannung steigt, bis etwas durchschlägt (oft > 100 V) → Transistor kaputt")
    zeile = f"Nur Diode: U_CE,max ≈ {fmt(e['u_ce_diode'], 'spannung')}"
    if e["t_diode"] is not None:
        zeile += f", Strom = 0 nach ≈ {fmt(e['t_diode'], 'zeit')}"
    zeilen.append(zeile)
    if e["u_ce_z"] is not None:
        zeile = f"Diode + Z-Diode {fmt(w['Uz'], 'spannung')}: U_CE,max ≈ {fmt(e['u_ce_z'], 'spannung')}"
        if e["t_z"] is not None:
            zeile += f", Strom = 0 nach ≈ {fmt(e['t_z'], 'zeit')}"
        zeilen.append(zeile)
        zeilen.append(f"→ Abschalten ca. {e['faktor']:.1f}× schneller (weniger Kontakt-Kleben, sauberes Öffnen)")
        if w["Uce0"] is not None and e["u_ce_z"] > w["Uce0"]:
            zeilen.append(f"❌ Über U_CE0 = {fmt(w['Uce0'], 'spannung')} – Transistor schlägt durch! "
                          "Kleinere Z-Diode oder Transistor mit höherer U_CE0")
        elif w["Uce0"] is not None and e["u_ce_z"] > w["Uce0"] * 0.8:
            zeilen.append(f"⚠ Weniger als 20 % Reserve zu U_CE0 = {fmt(w['Uce0'], 'spannung')} – kleinere Z-Diode wählen")
    elif w["L"] is None:
        zeilen.append("Induktivität L (falls bekannt) und U_Z eingeben für den Zeitvergleich")
    return zeilen


def freilauf(master):
    return FormelRechner(
        master, "Freilaufdiode & Abschalten", "Nur Diode oder Diode + Z-Diode? Spannung vs. Abfallzeit",
        felder=[("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 24"}),
                ("Rsp", "Spulenwiderstand", "widerstand", {"platzhalter": "z.B. 1k"}),
                ("L", "Induktivität (opt.)", "induktivitaet", {"platzhalter": "z.B. 2 H (messen)", "einheit": "H"}),
                ("Uz", "Z-Diode U_Z (opt.)", "spannung", {"platzhalter": "z.B. 24"}),
                ("Uce0", "U_CE0 Transistor (opt.)", "spannung", {"platzhalter": "z.B. 45"})],
        berechnen=_freilauf, formel="U_CE,max ≈ U_B + U_Z + 0.7 V     t_0 = τ · ln(1 + I · R / U_Gegen)     τ = L / R")


# =============================================================================
# 4) KONTAKTBELASTUNG
# =============================================================================
def _kontakt(w):
    if w["I"] is None:
        raise RechnerFehler("Nennstrom der Last eingeben")
    e = _fehler_umwandeln(rm.kontakt_last, w["U"], w["I"], w["art"], w["Irel"])
    zeilen = [f"Einschaltstrom ≈ {e['faktor']} × {fmt(w['I'], 'strom')} = {fmt(e['i_ein'], 'strom')}",
              f"({e['text']})"]
    if e["p"] is not None:
        zeilen.append(f"Leistung der Last ≈ {fmt(e['p'], 'leistung')}")
    if e["reserve"] is not None:
        if e["reserve"] < 1:
            zeilen.append("❌ Laststrom grösser als Relais-Nennstrom → grösseres Relais oder Schütz")
        elif e["i_ein"] > w["Irel"] * 4:
            zeilen.append("⚠ Einschaltstrom weit über Relais-Nennstrom → Relais mit Inrush-Angabe (z.B. TV-8, "
                          "„80 A inrush“), Schütz oder Einschaltstrom-Begrenzer (NTC)")
        else:
            zeilen.append(f"✅ Nennstrom ok (Reserve {e['reserve']:.1f}×) – Einschaltstrom trotzdem im Datenblatt prüfen")
    if w["netz"] == "DC" and w["U"] is not None and w["U"] > 30:
        zeilen.append("⚠ DC über 30 V: Lichtbogen erlischt nicht von selbst → DC-Lastgrenzkurve im Datenblatt prüfen, "
                      "oft nur < 1 A schaltbar!")
    return zeilen


def kontakt_last(master):
    return FormelRechner(
        master, "Kontaktbelastung", "Nicht der Nennstrom killt Kontakte, sondern Einschaltstrom und DC-Lichtbogen",
        felder=[("art", "Lastart", "auswahl", {"werte": list(rm.LASTARTEN)}),
                ("netz", "Spannungsart", "auswahl", {"werte": ["AC", "DC"]}),
                ("U", "Lastspannung", "spannung", {"platzhalter": "z.B. 230"}),
                ("I", "Nennstrom Last", "strom", {"platzhalter": "z.B. 0.5"}),
                ("Irel", "Relais-Nennstrom (opt.)", "strom", {"platzhalter": "z.B. 10"})],
        berechnen=_kontakt, formel="I_Ein ≈ Faktor · I_Nenn   (Glühlampe ≈ 12, Motor ≈ 6, Netzteil ≈ 30)")


RECHNER = {
    "relais_ansteuerung": relais_ansteuerung,
    "relais_temperatur": relais_temperatur,
    "freilauf": freilauf,
    "kontakt_last": kontakt_last,
}
