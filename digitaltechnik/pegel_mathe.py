# =============================================================================
# digitaltechnik/pegel_mathe.py
# -----------------------------------------------------------------------------
# LOGIKPEGEL: Datenblattwerte typischer Logikfamilien und Kompatibilitätsprüfung.
# KEIN tkinter - einzeln testbar:
#
#   python -c "from digitaltechnik.pegel_mathe import *; print(kompatibel('ESP32 (3.3 V)', '74HC (5 V, Werte bei 4.5 V)'))"
#
# BEGRIFFE (Datenblatt, garantierte Grenzwerte, nicht typisch!):
#   U_OH,min  Ausgang HIGH liefert mindestens        U_IH,min  Eingang erkennt sicher HIGH ab
#   U_OL,max  Ausgang LOW liefert höchstens          U_IL,max  Eingang erkennt sicher LOW bis
#   Störabstand HIGH  S_H = U_OH,min − U_IH,min      Störabstand LOW  S_L = U_IL,max − U_OL,max
#   U_E,max   höchste erlaubte Eingangsspannung (sonst Schutzdioden leiten / Zerstörung)
#
# Quellen: Datenblätter TI/Nexperia (74LS, 74HC bei 4.5 V, 74HCT, 74LVC), Espressif ESP32,
#          Microchip ATmega328P, JEDEC JESD8-7 (1.8 V). Ausgangswerte bei üblichen Lastströmen (4 … 8 mA).
# WER RUFT DAS AUF?  digitaltechnik/grafiken.py, digitaltechnik/rechner.py
# =============================================================================

FAMILIEN = {
    #                         U_B   U_OH   U_OL  U_IH   U_IL  U_E,max
    "74LS (TTL, 5 V)":       (5.0, 2.7,  0.5,  2.0,  0.8,  5.5),
    "74HC (5 V, Werte bei 4.5 V)": (5.0, 3.84, 0.33, 3.15, 1.35, 5.5),
    "74HCT (5 V, TTL-Eingang)": (5.0, 3.84, 0.33, 2.0, 0.8, 5.5),
    "ATmega328P / Uno (5 V)": (5.0, 4.2, 0.9,  3.0,  1.5,  5.5),
    "74LVC (3.3 V, 5-V-tolerant)": (3.3, 2.4, 0.4, 2.0, 0.8, 5.5),
    "ESP32 (3.3 V)":         (3.3, 2.64, 0.33, 2.475, 0.825, 3.6),
    "LVCMOS 1.8 V":          (1.8, 1.35, 0.45, 1.17, 0.63, 2.1),
}
SCHLUESSEL = ("u_b", "u_oh", "u_ol", "u_ih", "u_il", "u_e_max")


def familie(name):
    if name not in FAMILIEN:
        raise ValueError(f"Unbekannte Logikfamilie: {name}")
    return dict(zip(SCHLUESSEL, FAMILIEN[name]))


def kompatibel(sender, empfaenger):
    """
    Kann ein Ausgang der Familie 'sender' einen Eingang der Familie 'empfaenger' sicher ansteuern?
      HIGH ok:   U_OH,min(Sender) ≥ U_IH,min(Empfänger)   ->  Störabstand S_H ≥ 0
      LOW ok:    U_OL,max(Sender) ≤ U_IL,max(Empfänger)   ->  Störabstand S_L ≥ 0
      Spannung:  U_B(Sender) ≤ U_E,max(Empfänger)          ->  sonst Pegelwandler nötig
    """
    s, e = familie(sender), familie(empfaenger)
    s_h = s["u_oh"] - e["u_ih"]
    s_l = e["u_il"] - s["u_ol"]
    ueber = s["u_b"] > e["u_e_max"] + 1e-9
    ok = s_h >= 0 and s_l >= 0 and not ueber
    if ueber:
        rat = ("Pegelwandler nötig: Ausgang zu hoch für den Eingang (Schutzdioden leiten) – z.B. Spannungsteiler "
               "(langsame Signale), 74LVC-Puffer, TXS0108 oder MOSFET-Pegelwandler (I²C)")
    elif s_h < 0:
        rat = ("HIGH wird nicht sicher erkannt: Empfänger mit TTL-Eingang (74HCT) nehmen oder Pegelwandler "
               "(z.B. 74AHCT125 von 3.3 V auf 5 V)")
    elif s_l < 0:
        rat = "LOW wird nicht sicher erkannt: Ausgang mit kleinerem U_OL oder Pegelwandler"
    elif min(s_h, s_l) < 0.3:
        rat = "Funktioniert, aber mit kleinem Störabstand – kurze Leitungen, gemeinsame Masse"
    else:
        rat = "Direkt verbindbar"
    return {"sender": s, "empfaenger": e, "s_h": s_h, "s_l": s_l, "ueberspannung": ueber, "ok": ok, "rat": rat}


def zustand(u, empfaenger):
    """Wie deutet ein Eingang die Spannung u?  -> 'LOW', 'HIGH', 'undefiniert', 'zu hoch', 'negativ'"""
    e = familie(empfaenger)
    if u < -0.5:
        return "negativ"
    if u > e["u_e_max"]:
        return "zu hoch"
    if u <= e["u_il"]:
        return "LOW"
    if u >= e["u_ih"]:
        return "HIGH"
    return "undefiniert"
