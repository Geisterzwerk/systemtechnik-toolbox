# =============================================================================
# bauteile/rechner/dioden_rechner.py
# -----------------------------------------------------------------------------
# Alle RECHNER für die Seite "Diode".
#
# Unten im Dictionary RECHNER steht: ID -> Funktion, die die Rechner-Karte baut.
# Die ID wird in bauteile/inhalte/02_dioden/diode.py unter "rechner" benutzt.
#
#   dioden_kennlinie    INTERAKTIV: Kennlinien mit U_Z- und Temperatur-Regler (grafiken/dioden_kennlinie.py)
#   z_diode             Vorwiderstand für Z-Dioden-Stabilisierung, beide Worst Cases
#   gleichrichter       Einweg / Mittelpunkt / Brücke: U_DC, Brummen, Ladeelko, Dioden-Auswahl
#   durchlassspannung   U_F bei anderem Strom / anderer Temperatur, Verlustleistung
#
# Ebenfalls auf der Dioden-Seite (aus anderen Dateien, per ID):
#   led_vorwiderstand   -> rechner/widerstand_rechner.py
#   freilauf            -> rechner/relais_rechner.py
#
# Die eigentliche Mathe steht in dioden_mathe.py (ohne GUI, einzeln testbar).
#
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py -> erstellen(master, "z_diode")
# =============================================================================

from bauteile.grafiken.dioden_kennlinie import DiodenKennlinie         # -> grafiken/dioden_kennlinie.py
from bauteile.rechner import dioden_mathe as dm                        # -> rechner/dioden_mathe.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt   # -> rechner/basis.py


def _fehler_umwandeln(funktion, *args, **kwargs):
    """ValueError aus dioden_mathe.py als verständliche Meldung im Ergebnisfeld zeigen."""
    try:
        return funktion(*args, **kwargs)
    except ValueError as fehler:
        raise RechnerFehler(str(fehler)) from None


# =============================================================================
# 1) Z-DIODE
# =============================================================================
def _z_diode(w):
    if None in (w["Uemin"], w["Uz"], w["Ilmax"]):
        raise RechnerFehler("U_E,min, U_Z und I_L,max eingeben")
    u_e_max = w["Uemax"] if w["Uemax"] is not None else w["Uemin"]
    i_z_min = w["Izmin"] if w["Izmin"] is not None else 5e-3
    e = _fehler_umwandeln(dm.z_diode_vorwiderstand, w["Uemin"], u_e_max, w["Uz"], w["Ilmax"], i_z_min,
                          p_tot=w["Ptot"], i_l_min=w["Ilmin"] or 0.0)
    zeilen = [
        f"R_V ≤ (U_E,min − U_Z) / (I_L,max + I_Z,min) = {fmt(e['r_max'], 'widerstand')}",
        f"→ E12 (abgerundet): R_V = {fmt(e['r_v'], 'widerstand')}   (I_Z im Fall 1: {fmt(e['i_z_bei_min'], 'strom')})",
        f"Leerlauf-Fall (U_E,max, I_L,min): I_Z = {fmt(e['i_z_max'], 'strom')}, P_Z = {fmt(e['p_z'], 'leistung')}",
        f"Leistung R_V: {fmt(e['p_rv'], 'leistung')}  → Widerstand mit ≥ {fmt(2 * e['p_rv'], 'leistung')} wählen",
    ]
    if w["Ptot"] is None:
        zeilen.append("P_tot eingeben, dann wird geprüft, ob die Z-Diode das aushält")
    elif e["ok"]:
        zeilen.append(f"✅ Z-Diode hält das aus (P_tot = {fmt(w['Ptot'], 'leistung')}); "
                      f"R_V darf zwischen {fmt(e['r_min'], 'widerstand')} und {fmt(e['r_max'], 'widerstand')} liegen")
    else:
        zeilen.append(f"❌ P_Z > P_tot – R_V müsste ≥ {fmt(e['r_min'], 'widerstand')} sein, "
                      f"darf aber höchstens {fmt(e['r_max'], 'widerstand')} → stärkere Z-Diode oder Längsregler")
    return zeilen


def z_diode(master):
    return FormelRechner(
        master, "Z-Diode: Stabilisierung", "Vorwiderstand für beide schlimmsten Fälle bestimmen",
        felder=[("Uemin", "U_E min", "spannung", {"platzhalter": "z.B. 11"}),
                ("Uemax", "U_E max", "spannung", {"platzhalter": "z.B. 14"}),
                ("Uz", "Z-Spannung U_Z", "spannung", {"platzhalter": "z.B. 5.1"}),
                ("Ilmax", "Laststrom max", "strom", {"einheit": "mA", "platzhalter": "z.B. 20"}),
                ("Ilmin", "Laststrom min", "strom", {"einheit": "mA", "platzhalter": "leer = 0 (Leerlauf)"}),
                ("Izmin", "I_Z min", "strom", {"einheit": "mA", "platzhalter": "leer = 5"}),
                ("Ptot", "P_tot Z-Diode", "leistung", {"platzhalter": "z.B. 0.5"})],
        berechnen=_z_diode,
        formel="R_V,max = (U_E,min − U_Z) / (I_L,max + I_Z,min)     P_Z = U_Z · ((U_E,max − U_Z) / R_V − I_L,min)")


# =============================================================================
# 2) GLEICHRICHTER
# =============================================================================
def _gleichrichter(w):
    if w["Ueff"] is None:
        raise RechnerFehler("Trafospannung U_eff eingeben")
    u_f = w["Uf"] if w["Uf"] is not None else dm.U_F_SI
    e = _fehler_umwandeln(dm.gleichrichter, w["Ueff"], w["art"], u_f=u_f, i_last=w["I"], c=w["C"],
                          u_brumm_soll=w["Ubr"], f_netz=w["f"] or 50.0)
    zeilen = [f"Û = U_eff · √2 = {fmt(e['u_spitze'], 'spannung')}   ·   U_DC (Leerlauf) ≈ {fmt(e['u_dc'], 'spannung')}",
              f"Brummfrequenz {fmt(e['f_brumm'], 'frequenz')}   ·   {e['dioden']} Diode(n)"]
    if w["I"] is None:
        zeilen.append("Laststrom eingeben für Brummspannung, Ladeelko und Dioden-Strom")
    else:
        if e["u_brumm"] is not None:
            zeilen.append(f"Brummspannung U_Br,ss ≈ {fmt(e['u_brumm'], 'spannung')}  → "
                          f"U_min ≈ {fmt(e['u_dc'] - e['u_brumm'], 'spannung')}")
        if e["c_noetig"] is not None:
            zeilen.append(f"Nötiger Ladeelko C ≥ {fmt(e['c_noetig'], 'kapazitaet')}")
        zeilen.append(f"Pro Diode: I_F(AV) = {fmt(e['i_diode'], 'strom')}  ·  Verlust alle Dioden ≈ "
                      f"{fmt(e['p_dioden'], 'leistung')}")
    zeilen.append(f"Sperrspannung pro Diode U_RRM ≥ {fmt(e['u_sperr'], 'spannung')} + Reserve "
                  f"(→ {fmt(1.5 * e['u_sperr'], 'spannung')})")
    zeilen.append(f"Elko-Spannung ≥ {fmt(e['u_spitze'] * 1.1 * 1.2, 'spannung')} (Netz +10 %, Trafo im Leerlauf höher)")
    return zeilen


def gleichrichter(master):
    return FormelRechner(
        master, "Gleichrichter + Ladeelko", "Welche Spannung kommt heraus – und welche Dioden braucht es?",
        felder=[("art", "Schaltung", "auswahl", {"werte": list(dm.SCHALTUNGEN), "standard": "Brücke (B2 Graetz)"}),
                ("Ueff", "Trafo U_eff", "spannung", {"platzhalter": "z.B. 12 (M2: pro Hälfte)"}),
                ("I", "Laststrom", "strom", {"einheit": "mA", "platzhalter": "z.B. 500"}),
                ("C", "Ladeelko (opt.)", "kapazitaet", {"platzhalter": "z.B. 2200"}),
                ("Ubr", "… oder Brumm soll", "spannung", {"platzhalter": "z.B. 1 → C wird berechnet"}),
                ("Uf", "Diodenspannung U_F", "spannung", {"platzhalter": "leer = 0.7"}),
                ("f", "Netzfrequenz", "frequenz", {"platzhalter": "leer = 50"})],
        berechnen=_gleichrichter,
        formel="Û = U_eff · √2     U_DC ≈ Û − n · U_F     U_Br,ss ≈ I / (f_Br · C)")


# =============================================================================
# 3) DURCHLASSSPANNUNG BEI STROM / TEMPERATUR
# =============================================================================
def _durchlassspannung(w):
    if w["Uf1"] is None or w["I1"] is None:
        raise RechnerFehler("U_F und I_F aus dem Datenblatt eingeben")
    t = w["T"] if w["T"] is not None else 25.0
    n = w["n"] or 1.8
    e = _fehler_umwandeln(dm.durchlassspannung, w["Uf1"], w["I1"], w["I2"], t, n)
    zeilen = [f"U_F = {fmt(e['u_f2'], 'spannung')} bei {fmt(e['i_2'], 'strom')} und {fmt(t, 'temperatur')}"]
    if w["I2"] is not None:
        zeilen.append(f"Anteil Strom: {e['du_strom'] * 1000:+.0f} mV   (n · U_T · ln(I2/I1))")
    if t != 25.0:
        zeilen.append(f"Anteil Temperatur: {e['du_temp'] * 1000:+.0f} mV   (−2 mV/K)")
    zeilen.append(f"Verlustleistung P = U_F · I_F = {fmt(e['p'], 'leistung')}")
    zeilen.append("Grosse Ströme: Bahnwiderstand kommt dazu → echte U_F eher grösser (Datenblatt-Kurve!)")
    return zeilen


def durchlassspannung(master):
    return FormelRechner(
        master, "Durchlassspannung & Verlust", "U_F hängt von Strom und Temperatur ab",
        felder=[("Uf1", "U_F (Datenblatt)", "spannung", {"platzhalter": "z.B. 0.7"}),
                ("I1", "… bei I_F", "strom", {"einheit": "mA", "platzhalter": "z.B. 10"}),
                ("I2", "neuer Strom (opt.)", "strom", {"einheit": "mA", "platzhalter": "z.B. 100"}),
                ("T", "Temperatur (opt.)", "temperatur", {"platzhalter": "leer = 25"}),
                ("n", "Emissionskoeff. n", "zahl", {"platzhalter": "leer = 1.8 (Si)"})],
        berechnen=_durchlassspannung,
        formel="ΔU_F = n · U_T · ln(I2 / I1) − 2 mV/K · (T − 25 °C)     U_T = k · T / q ≈ 26 mV")


RECHNER = {
    "dioden_kennlinie": DiodenKennlinie,
    "z_diode": z_diode,
    "gleichrichter": gleichrichter,
    "durchlassspannung": durchlassspannung,
}
