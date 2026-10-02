# =============================================================================
# digitaltechnik/rechner.py
# -----------------------------------------------------------------------------
# RECHNER des Bereichs Digitaltechnik + Registrierung der interaktiven Werkzeuge.
#
#   zahlensystem          Zahl in Dez / Bin / Hex / Okt / BCD / Gray umrechnen
#   zweierkomplement      Bitmuster einer negativen Zahl (mit Rechenweg) oder Muster als signed lesen
#   binaer_addieren       a + b mit n Bit: Ergebnis, Carry und Overflow
#   bitmaske              Register-Operation (AND / OR / AND NOT / XOR / NOT / Schieben)
#   logikpegel            Passt ein Ausgang zu einem Eingang? Störabstände
#   werkzeug_*            INTERAKTIVE Werkzeuge (digitaltechnik/grafiken.py)
#
# AD-Wandler und Abtastung gibt es schon im Bereich Messtechnik ("adc", "abtastung").
# Rechnung: digitaltechnik/zahlen_mathe.py, digitaltechnik/pegel_mathe.py (ohne GUI, testbar)
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py (_MODULE) -> erstellen(master, "zahlensystem")
# =============================================================================

from bauteile.rechner.basis import FormelRechner, RechnerFehler               # -> bauteile/rechner/basis.py
from digitaltechnik import pegel_mathe as pm                                  # -> digitaltechnik/pegel_mathe.py
from digitaltechnik import zahlen_mathe as zm                                 # -> digitaltechnik/zahlen_mathe.py
from digitaltechnik.grafiken import (BitmaskenKarte, LogikpegelKarte,         # -> digitaltechnik/grafiken.py
                                     ZahlensystemKarte, ZweierkomplementKarte)

BITBREITEN = ["8", "16", "32", "4"]


def _fehler_umwandeln(funktion, *args):
    try:
        return funktion(*args)
    except ValueError as fehler:
        raise RechnerFehler(str(fehler)) from None


def _zahl(text, basis_name="automatisch (Präfix)"):
    basis = zm.BASEN.get(basis_name)
    return _fehler_umwandeln(zm.einlesen, text, basis)


# =============================================================================
# 1) ZAHLENSYSTEME
# =============================================================================
EINGABE_BASEN = ["automatisch (Präfix)"] + list(zm.BASEN)


def _zahlensystem(w):
    if w["zahl"] is None:
        raise RechnerFehler("Zahl eingeben, z.B. 200, 0xC8, 0b11001000 oder 1100 1000 mit Basis Binär")
    wert = _zahl(w["zahl"], w["basis"])
    bits = int(w["bits"])
    e = _fehler_umwandeln(zm.darstellungen, wert, bits)
    zeilen = [f"Dezimal {e['dez']}" + (f"   (Muster unsigned {e['unsigned']})" if wert < 0 else
                                        f"   (als signed {e['signed']})"),
              f"Binär   {e['bin']}",
              f"Hex     0x{e['hex']}   ·   Oktal 0o{e['okt']}"]
    if e["bcd"]:
        zeilen.append(f"BCD     {e['bcd']}   ·   Gray {e['gray']}")
    if e["ascii"]:
        zeilen.append(f"ASCII   '{e['ascii']}'")
    zeilen.append(f"Braucht mindestens {zm.bits_noetig(wert)} Bit" + (" (mit Vorzeichen)" if wert < 0 else ""))
    return zeilen


def zahlensystem(master):
    return FormelRechner(
        master, "Zahlensysteme umrechnen", "Präfix 0b / 0x / 0o wird erkannt, Leerzeichen zum Gruppieren erlaubt",
        felder=[("zahl", "Zahl", "text", {"platzhalter": "z.B. 0xC8"}),
                ("basis", "Eingabe ist", "auswahl", {"werte": EINGABE_BASEN}),
                ("bits", "Bitbreite", "auswahl", {"werte": BITBREITEN})],
        berechnen=_zahlensystem, formel="Wert = Σ Ziffer · Basis^Stelle     1 Hex-Ziffer = 4 Bit, 1 Oktalziffer = 3 Bit")


# =============================================================================
# 2) ZWEIERKOMPLEMENT
# =============================================================================
ZK_ARTEN = ["Zahl → Bitmuster", "Bitmuster → Zahl (signed)"]


def _zweierkomplement(w):
    if w["eingabe"] is None:
        raise RechnerFehler("Zahl (z.B. -5) oder Bitmuster (z.B. 1111 1011 / 0xFB) eingeben")
    bits = int(w["bits"])
    tief, hoch = zm.bereich(bits)
    if w["art"] == ZK_ARTEN[0]:
        wert = _zahl(w["eingabe"])                                    # dezimal oder mit Präfix
        z = _fehler_umwandeln(zm.zweierkomplement, wert, bits)
        zeilen = [f"{wert} mit {bits} Bit (Bereich {tief} … {hoch}):  {z['bin']}  = 0x{z['hex']}"]
        if wert < 0:
            zeilen += [f"1. Betrag {-wert} binär:     {z['betrag']}",
                       f"2. alle Bits invertieren: {z['invertiert']}",
                       f"3. +1:                    {z['plus_eins']}",
                       f"Kontrolle: 2^{bits} + ({wert}) = {z['muster']}"]
        return zeilen
    t = w["eingabe"].strip().lower()
    muster = _zahl(w["eingabe"], "automatisch (Präfix)" if t.startswith(("0x", "0b", "0o")) else "Binär")
    if muster < 0 or muster >= 2 ** bits:
        raise RechnerFehler(f"Das Muster passt nicht in {bits} Bit")
    signed = zm.als_vorzeichen(muster, bits)
    if signed < 0:
        deutung = f"signed:   {signed}   (MSB = 1 → negativ:  {muster} − 2^{bits} = {signed})"
    else:
        deutung = f"signed:   {signed}   (MSB = 0 → positiv, gleich wie unsigned)"
    return [f"Muster {zm.binaer(muster, bits)} (0x{muster:0{-(-bits // 4)}X})", f"unsigned: {muster}", deutung]


def zweierkomplement(master):
    return FormelRechner(
        master, "Zweierkomplement", "Negative Zahlen als Bitmuster – oder ein Muster als Zahl mit Vorzeichen lesen",
        felder=[("art", "Richtung", "auswahl", {"werte": ZK_ARTEN}),
                ("eingabe", "Zahl / Bitmuster", "text", {"platzhalter": "z.B. -5 oder 1111 1011"}),
                ("bits", "Bitbreite", "auswahl", {"werte": BITBREITEN})],
        berechnen=_zweierkomplement, formel="−x = invertieren + 1 = 2^n − x     Bereich −2^(n−1) … 2^(n−1) − 1")


# =============================================================================
# 3) BINÄR ADDIEREN
# =============================================================================
def _binaer_addieren(w):
    if w["a"] is None or w["b"] is None:
        raise RechnerFehler("a und b eingeben (dezimal, 0x… oder 0b…)")
    bits = int(w["bits"])
    a, b = _zahl(w["a"]), _zahl(w["b"])
    e = _fehler_umwandeln(zm.addieren, a, b, bits)
    sa, sb = zm.als_vorzeichen(e["muster_a"], bits), zm.als_vorzeichen(e["muster_b"], bits)
    return [f"  {e['bin_a']}   ({e['muster_a']} / signed {sa})",
            f"+ {e['bin_b']}   ({e['muster_b']} / signed {sb})",
            f"= {e['bin_summe']}   unsigned {e['unsigned']}, signed {e['signed']}",
            f"C = {int(e['carry'])}: unsigned " + (f"Überlauf (richtig {e['muster_a'] + e['muster_b']})" if e["carry"] else "korrekt"),
            f"V = {int(e['overflow'])}: signed " + (f"Überlauf (richtig {sa + sb})" if e["overflow"] else "korrekt")]


def binaer_addieren(master):
    return FormelRechner(
        master, "Binär addieren mit Flags", "Was rechnet das Addierwerk – und wann ist es falsch?",
        felder=[("a", "a", "text", {"platzhalter": "z.B. 100"}),
                ("b", "b", "text", {"platzhalter": "z.B. 50"}),
                ("bits", "Bitbreite", "auswahl", {"werte": BITBREITEN})],
        berechnen=_binaer_addieren, formel="C = Übertrag aus dem MSB (unsigned)     V = Vorzeichenfehler (signed)")


# =============================================================================
# 4) BITMASKE
# =============================================================================
def _bitmaske(w):
    if w["x"] is None:
        raise RechnerFehler("Registerwert x eingeben (z.B. 0xA5)")
    bits = int(w["bits"])
    x = _zahl(w["x"])
    if w["maske"] is not None:
        maske = _zahl(w["maske"])
    elif w["nr"] is not None:
        nummern = [_zahl(t) for t in w["nr"].replace(",", " ").split()]
        maske = _fehler_umwandeln(zm.maske_aus_bits, nummern)
    else:
        maske = 0
        if w["op"] not in (zm.OPERATIONEN[4], zm.OPERATIONEN[5], zm.OPERATIONEN[6]):
            raise RechnerFehler("Maske eingeben (z.B. 0x08) oder Bitnummern (z.B. 3 oder 0 4 7)")
    schritte = 1 if w["n"] is None else _zahl(w["n"])
    e = _fehler_umwandeln(zm.bitoperation, x, maske, w["op"], bits, schritte)
    stellen = -(-bits // 4)
    zeilen = [f"x     = {zm.binaer(x, bits)}  (0x{x:0{stellen}X})",
              f"Maske = {zm.binaer(maske, bits)}  (0x{maske:0{stellen}X})",
              f"{e['c']}  →  {e['bin']}  = 0x{e['ergebnis']:0{stellen}X} = {e['ergebnis']}",
              f"geänderte Bits: {zm.binaer(e['geaendert'], bits)}"]
    if w["op"] == zm.OPERATIONEN[0]:
        zeilen.append("Ergebnis ≠ 0 → Bit(s) gesetzt" if e["ergebnis"] else "Ergebnis = 0 → Bit(s) nicht gesetzt")
    return zeilen


def bitmaske(master):
    return FormelRechner(
        master, "Bitmaske anwenden", "Registerbits setzen, löschen, umschalten, prüfen oder schieben",
        felder=[("x", "Register x", "text", {"platzhalter": "z.B. 0xA5"}),
                ("op", "Operation", "auswahl", {"werte": zm.OPERATIONEN}),
                ("maske", "Maske (opt.)", "text", {"platzhalter": "z.B. 0x08"}),
                ("nr", "oder Bitnummern", "text", {"platzhalter": "z.B. 3  oder  0 4 7"}),
                ("n", "Schieben um (opt.)", "text", {"platzhalter": "1"}),
                ("bits", "Bitbreite", "auswahl", {"werte": BITBREITEN})],
        berechnen=_bitmaske, formel="setzen x |= m     löschen x &= ~m     umschalten x ^= m     prüfen x & m")


# =============================================================================
# 5) LOGIKPEGEL
# =============================================================================
def _logikpegel(w):
    e = _fehler_umwandeln(pm.kompatibel, w["sender"], w["empf"])
    s, r = e["sender"], e["empfaenger"]
    return [f"S_H = U_OH − U_IH = {s['u_oh']:.2f} V − {r['u_ih']:.2f} V = {e['s_h']:+.2f} V   "
            f"{'✓' if e['s_h'] >= 0 else '❌'}",
            f"S_L = U_IL − U_OL = {r['u_il']:.2f} V − {s['u_ol']:.2f} V = {e['s_l']:+.2f} V   "
            f"{'✓' if e['s_l'] >= 0 else '❌'}",
            f"Ausgang bis {s['u_b']:.1f} V – Eingang verträgt {r['u_e_max']:.1f} V   "
            f"{'❌ zu hoch' if e['ueberspannung'] else '✓'}",
            ("✓ " if e["ok"] else "⚠ ") + e["rat"]]


def logikpegel(master):
    namen = list(pm.FAMILIEN)
    return FormelRechner(
        master, "Logikpegel-Kompatibilität", "Garantierte Datenblattwerte – nicht die typischen",
        felder=[("sender", "Sender (Ausgang)", "auswahl", {"werte": namen, "standard": "ESP32 (3.3 V)"}),
                ("empf", "Empfänger (Eingang)", "auswahl", {"werte": namen, "standard": "74HC (5 V, Werte bei 4.5 V)"})],
        berechnen=_logikpegel, formel="S_H = U_OH,min − U_IH,min     S_L = U_IL,max − U_OL,max")


# =============================================================================
# REGISTRIERUNG (IDs müssen sich von allen anderen unterscheiden)
# =============================================================================
RECHNER = {
    "zahlensystem": zahlensystem,
    "zweierkomplement": zweierkomplement,
    "binaer_addieren": binaer_addieren,
    "bitmaske": bitmaske,
    "logikpegel": logikpegel,
    "werkzeug_zahlensystem": ZahlensystemKarte,
    "werkzeug_zweierkomplement": ZweierkomplementKarte,
    "werkzeug_bitmaske": BitmaskenKarte,
    "werkzeug_logikpegel": LogikpegelKarte,
}
