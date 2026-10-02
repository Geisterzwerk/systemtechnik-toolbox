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
#   wahrheitstabelle      Ausdruck -> Wahrheitstabelle, Minterme, kanonische und minimale DNF/KNF
#   ausdruck_vergleichen  Sind zwei Ausdrücke gleich (z.B. De Morgan prüfen)? Sonst Gegenbeispiel
#   kv_minimieren         Minterme (+ don't cares) -> minimale DNF und KNF (Quine-McCluskey)
#   addierer_laufzeit     Ripple-Carry: Worst-Case-Laufzeit und höchste Taktfrequenz
#   mux_funktion          Logikfunktion mit einem Multiplexer bauen (Dateneingänge D0 … Dn)
#   siebensegment         Hex-Ziffer -> Segmente a … g und Pegel (gemeinsame Kathode / Anode)
#   adressdecoder         Adressbereiche der Decoder-Ausgänge (Chip-Select)
#   open_drain_pullup     Pull-up für Open-Drain/I²C: R_min, R_max, Anstiegszeit
#   zaehler_entwurf       synchroner Zähler für eine Zustandsfolge: minimierte D- bzw. JK-Gleichungen
#   fmax_schaltwerk       höchste Taktfrequenz eines synchronen Schaltwerks (Setup/Hold)
#   frequenzteiler        Teiler durch m: Flipflops, Ausgangsfrequenz
#   uart_timing           Bitzeit, Rahmenzeit, Zeichen pro Sekunde, Toleranz eines UART-Formats (z.B. 8N1)
#   uart_baudrate         Baudraten-Teiler eines µC: tatsächliche Baudrate und Fehler in %
#   spi_uebertragung      SPI: Modus (CPOL/CPHA), Dauer und Datenrate
#   i2c_uebertragung      I²C: Takte, Dauer und Nutzdatenrate einer Übertragung
#   speicher_organisation Kapazität und Adressbereich aus Adress- und Datenbits
#   speicher_erweitern    Wie viele Speicherchips für grössere Tiefe / Wortbreite?
#   werkzeug_*            INTERAKTIVE Werkzeuge (digitaltechnik/grafiken.py)
#
# AD-Wandler und Abtastung gibt es schon im Bereich Messtechnik ("adc", "abtastung").
# Rechnung: digitaltechnik/zahlen_mathe.py, pegel_mathe.py, logik_mathe.py, schaltnetze_mathe.py,
#           schaltwerke_mathe.py, busse_mathe.py (ohne GUI, testbar)
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py (_MODULE) -> erstellen(master, "zahlensystem")
# =============================================================================

from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt          # -> bauteile/rechner/basis.py
from digitaltechnik import busse_mathe as bm                                  # -> digitaltechnik/busse_mathe.py
from digitaltechnik import logik_mathe as lm                                  # -> digitaltechnik/logik_mathe.py
from digitaltechnik import pegel_mathe as pm                                  # -> digitaltechnik/pegel_mathe.py
from digitaltechnik import schaltnetze_mathe as sm                            # -> digitaltechnik/schaltnetze_mathe.py
from digitaltechnik import schaltwerke_mathe as swm                           # -> digitaltechnik/schaltwerke_mathe.py
from digitaltechnik import zahlen_mathe as zm                                 # -> digitaltechnik/zahlen_mathe.py
from digitaltechnik.grafiken import (BitmaskenKarte, LogikpegelKarte,         # -> digitaltechnik/grafiken.py
                                     ZahlensystemKarte, ZweierkomplementKarte)
from digitaltechnik.grafiken_schaltnetze import (AddiererKarte, AusgangKarte,    # -> digitaltechnik/grafiken_schaltnetze.py
                                                 DecoderKarte, MuxKarte)
from digitaltechnik.grafiken_schaltwerke import (FlipflopKarte, SchieberegisterKarte,  # -> digitaltechnik/grafiken_schaltwerke.py
                                                 ZaehlerKarte)
from digitaltechnik.grafiken_busse import (I2cKarte, SpeicherKarte, SpiKarte,  # -> digitaltechnik/grafiken_busse.py
                                           UartKarte)
from digitaltechnik.grafiken_logik import (AusdruckKarte, GatterKarte, KVKarte,  # -> digitaltechnik/grafiken_logik.py
                                           wahrheitstabelle_text)

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
# 6) WAHRHEITSTABELLE
# =============================================================================
def _wahrheitstabelle(w):
    e = _fehler_umwandeln(lm.analysieren, w["ausdruck"])
    if not e["namen"]:
        return [f"Y = {e['text']} ist konstant {e['tabelle'][0][1]}"]
    zeilen = [f"Gelesen als: Y = {e['text']}", ""]
    zeilen += wahrheitstabelle_text(e["namen"], e["tabelle"]).split("\n")
    zeilen += ["", f"Minterme: Σm({', '.join(map(str, e['minterme']))})   ·   "
                   f"Maxterme: Πm({', '.join(map(str, e['maxterme']))})",
               f"DNF minimal: Y = {e['min_dnf']}",
               f"KNF minimal: Y = {e['min_knf']}"]
    if len(e["minterme"]) <= 8:
        zeilen.append(f"DNF kanonisch: {e['dnf']}")
    return zeilen


def wahrheitstabelle(master):
    return FormelRechner(
        master, "Wahrheitstabelle und Normalformen", "Schreibweisen: ¬A !A /A A'  ·  A·B A*B AB  ·  A+B  ·  A⊕B",
        felder=[("ausdruck", "Ausdruck Y =", "text", {"platzhalter": "z.B. A·B + /A·C"})],
        berechnen=_wahrheitstabelle, formel="DNF = ODER der Minterme (1-Zeilen)     KNF = UND der Maxterme (0-Zeilen)")


# =============================================================================
# 7) AUSDRÜCKE VERGLEICHEN
# =============================================================================
def _ausdruck_vergleichen(w):
    if w["a"] is None or w["b"] is None:
        raise RechnerFehler("Beide Ausdrücke eingeben, z.B. ¬(A·B) und ¬A + ¬B")
    gleich, info = _fehler_umwandeln(lm.vergleichen, w["a"], w["b"])
    links, rechts = lm.als_text(lm.parsen(w["a"])), lm.als_text(lm.parsen(w["b"]))
    if gleich:
        return [f"{links}  =  {rechts}", f"✓ Gleichwertig – für alle {2 ** len(info['namen'])} Belegungen geprüft"]
    belegung = ", ".join(f"{n} = {v}" for n, v in info["belegung"].items())
    return [f"{links}  ≠  {rechts}",
            f"❌ Gegenbeispiel: {belegung}  →  links {info['a']}, rechts {info['b']}"]


def ausdruck_vergleichen(master):
    return FormelRechner(
        master, "Zwei Ausdrücke vergleichen", "Umformung prüfen (z.B. De Morgan) – alle Belegungen werden durchprobiert",
        felder=[("a", "Ausdruck 1", "text", {"platzhalter": "z.B. ¬(A·B)"}),
                ("b", "Ausdruck 2", "text", {"platzhalter": "z.B. ¬A + ¬B"})],
        berechnen=_ausdruck_vergleichen, formel="De Morgan: ¬(A·B) = ¬A + ¬B     ¬(A + B) = ¬A·¬B")


# =============================================================================
# 8) MINIMIEREN AUS MINTERMEN
# =============================================================================
def _kv_minimieren(w):
    n = int(w["n"])
    namen = list("ABCDEF"[:n])

    def liste(text):
        if text is None:
            return []
        werte = [_zahl(t) for t in text.replace(",", " ").replace(";", " ").split()]
        falsch = [m for m in werte if not 0 <= m < 2 ** n]
        if falsch:
            raise RechnerFehler(f"Minterm(e) {', '.join(map(str, falsch))} gibt es mit {n} Variablen nicht "
                                f"(0 … {2 ** n - 1})")
        return werte
    if w["m"] is None:
        raise RechnerFehler("Minterme eingeben (Nummern der 1-Zeilen), z.B. 0 1 2 3 8 10")
    eins, dc = liste(w["m"]), liste(w["d"])
    doppelt = sorted(set(eins) & set(dc))
    if doppelt:
        raise RechnerFehler(f"Minterm(e) {', '.join(map(str, doppelt))} sind gleichzeitig 1 und don't care")
    f = lm.minimal_formen(eins, namen, dc)
    zeilen = [f"Y = Σm({', '.join(map(str, sorted(eins)))})" + (f" + d({', '.join(map(str, sorted(dc)))})" if dc else ""),
              f"DNF minimal: Y = {f['min_dnf']}",
              f"KNF minimal: Y = {f['min_knf']}"]
    for t in f["terme"]:
        if t != "-" * n:
            zeilen.append(f"  {lm.produkt(t, namen):<16} deckt {2 ** t.count('-')} Felder  (Muster {t})")
    return zeilen


def kv_minimieren(master):
    return FormelRechner(
        master, "Minimieren aus Mintermen (KV / Quine-McCluskey)", "Nummern der 1-Zeilen und der don't-care-Zeilen",
        felder=[("n", "Anzahl Variablen", "auswahl", {"werte": ["4", "3", "2", "5", "6"]}),
                ("m", "Minterme (1)", "text", {"platzhalter": "z.B. 0 1 2 3 8 10"}),
                ("d", "don't care (X, opt.)", "text", {"platzhalter": "z.B. 5 7"})],
        berechnen=_kv_minimieren, formel="Blöcke aus 2^k Feldern -> k Variablen fallen weg")


# =============================================================================
# 9) ADDIERER-LAUFZEIT
# =============================================================================
def _addierer_laufzeit(w):
    if w["n"] is None or w["tc"] is None:
        raise RechnerFehler("Bitbreite und Laufzeit pro Stufe (Übertrag) eingeben")
    n = w["n"]
    if n != int(n) or not 1 <= n <= 64:
        raise RechnerFehler("Bitbreite als ganze Zahl von 1 bis 64")
    e = _fehler_umwandeln(sm.laufzeit, int(n), w["tc"], w["ts"])
    return [f"Übertrag durch alle Stufen: n · t_C = {int(n)} · {fmt(w['tc'], 'zeit')} = {fmt(e['t_carry_ges'], 'zeit')}",
            f"höchstes Summenbit: (n − 1) · t_C + t_S = {fmt(e['t_summe_ges'], 'zeit')}",
            f"Ergebnis sicher nach {fmt(e['t_ges'], 'zeit')}  →  f_max ≈ {fmt(e['f_max'], 'frequenz')}",
            "Schneller: Carry-Lookahead (Überträge parallel berechnen) – Laufzeit wächst nur noch mit log2(n)"]


def addierer_laufzeit(master):
    return FormelRechner(
        master, "Ripple-Carry-Addierer: Laufzeit", "Wie lange läuft der Übertrag durch die Kette?",
        felder=[("n", "Bitbreite n", "zahl", {"platzhalter": "z.B. 16"}),
                ("tc", "Laufzeit Übertrag pro Stufe t_C", "zeit", {"einheit": "ns", "platzhalter": "z.B. 10"}),
                ("ts", "Laufzeit Summe t_S (opt.)", "zeit", {"einheit": "ns", "platzhalter": "= t_C"})],
        berechnen=_addierer_laufzeit, formel="t ≈ n · t_C     f_max ≈ 1 / t")


# =============================================================================
# 10) LOGIKFUNKTION MIT MUX
# =============================================================================
def _mux_funktion(w):
    if w["ausdruck"] is None:
        raise RechnerFehler("Ausdruck eingeben, z.B. A·B + ¬A·C")
    k = None if w["k"] == "automatisch (n − 1)" else int(w["k"])
    e = _fehler_umwandeln(sm.mux_funktion, w["ausdruck"], k)
    k = len(e["auswahl"])
    zeilen = [f"Y = {e['text']}   →   {2 ** k}:1-MUX, Auswahl {' '.join(e['auswahl'])}"
              + (f", Rest {' '.join(e['rest'])} an die Dateneingänge" if e["rest"] else "")]
    for i, d in enumerate(e["daten"]):
        zeilen.append(f"  D{i} ({' '.join(e['auswahl'])} = {format(i, f'0{k}b')}):  {d}")
    return zeilen


def mux_funktion(master):
    return FormelRechner(
        master, "Logikfunktion mit Multiplexer", "Auswahl = erste Variablen, an D_i kommt die Restfunktion",
        felder=[("ausdruck", "Ausdruck Y =", "text", {"platzhalter": "z.B. A·B + ¬A·C"}),
                ("k", "Auswahlleitungen", "auswahl", {"werte": ["automatisch (n − 1)", "1", "2", "3", "4"]})],
        berechnen=_mux_funktion, formel="Y = Σ (Auswahl = i) · D_i     (Shannon-Zerlegung)")


# =============================================================================
# 11) 7-SEGMENT
# =============================================================================
def _siebensegment(w):
    if w["ziffer"] is None:
        raise RechnerFehler("Ziffer 0 … 9 oder A … F eingeben")
    t = w["ziffer"].strip()
    ziffer = _zahl(t if t.lower().startswith(("0x", "0b")) else t, "Hexadezimal" if len(t) == 1 else
                   "automatisch (Präfix)")
    anode = w["typ"] == "gemeinsame Anode"
    e = _fehler_umwandeln(sm.siebensegment, ziffer, anode)
    return [f"Ziffer {ziffer:X}: Segmente {' '.join(e['segmente'])} an ({len(e['segmente'])} von 7)",
            "a b c d e f g = " + " ".join(str(e["pegel"][s]) for s in "abcdefg")
            + ("   (LOW = an)" if anode else "   (HIGH = an)"),
            f"Muster g … a = {format(e['muster'], '07b')} = 0x{e['muster']:02X}"
            + ("" if anode else "   (gemeinsame Anode: invertieren)")]


def siebensegment(master):
    return FormelRechner(
        master, "7-Segment-Code", "Welche Segmente leuchten – und welcher Pegel muss an a … g?",
        felder=[("ziffer", "Ziffer (0 … F)", "text", {"platzhalter": "z.B. 7 oder b"}),
                ("typ", "Anzeige", "auswahl", {"werte": ["gemeinsame Kathode", "gemeinsame Anode"]})],
        berechnen=_siebensegment, formel="Kathode: Segment an = HIGH     Anode: Segment an = LOW")


# =============================================================================
# 12) ADRESSDECODER
# =============================================================================
def _adressdecoder(w):
    if w["N"] is None or w["k"] is None:
        raise RechnerFehler("Adressbreite und Anzahl Decoder-Eingänge eingeben")
    for name in ("N", "k"):
        if w[name] != int(w[name]):
            raise RechnerFehler("Ganze Zahlen eingeben")
    bereiche, block = _fehler_umwandeln(sm.adressdecoder, int(w["N"]), int(w["k"]))
    stellen = max(4, -(-int(w["N"]) // 4))
    groesse = fmt(block, "zahl") if block < 1024 else (f"{block // 1024} Ki" if block < 2 ** 20 else f"{block // 2 ** 20} Mi")
    zeilen = [f"{2 ** int(w['k'])} Ausgänge, je ein Block von 2^({int(w['N'])} − {int(w['k'])}) = {block} Adressen ({groesse})",
              f"Decoder an A{int(w['N']) - 1} … A{int(w['N']) - int(w['k'])}, der Baustein bekommt A{int(w['N']) - int(w['k']) - 1} … A0"
              if int(w["k"]) < int(w["N"]) else "Jede Adresse hat einen eigenen Ausgang"]
    for k, von, bis in bereiche[:16]:
        zeilen.append(f"  ¬CS{k}:  0x{von:0{stellen}X} … 0x{bis:0{stellen}X}")
    if len(bereiche) > 16:
        zeilen.append(f"  … ({len(bereiche) - 16} weitere)")
    return zeilen


def adressdecoder(master):
    return FormelRechner(
        master, "Adressdecodierung (Chip-Select)", "Welcher Decoder-Ausgang ist für welchen Adressbereich zuständig?",
        felder=[("N", "Adressbits N", "zahl", {"platzhalter": "z.B. 16 (64 Ki)"}),
                ("k", "Decoder-Eingänge k", "zahl", {"platzhalter": "z.B. 3 (74HC138)"})],
        berechnen=_adressdecoder, formel="Blockgrösse = 2^(N − k)     Ausgang i: i · Block … (i + 1) · Block − 1")


# =============================================================================
# 13) PULL-UP FÜR OPEN DRAIN / I²C
# =============================================================================
I2C_MODI = {"Standard-Mode (100 kHz, t_r ≤ 1000 ns)": 1000e-9, "Fast-Mode (400 kHz, t_r ≤ 300 ns)": 300e-9,
            "Fast-Mode Plus (1 MHz, t_r ≤ 120 ns)": 120e-9}


def _open_drain_pullup(w):
    if w["Ub"] is None or w["C"] is None:
        raise RechnerFehler("Versorgung U_B und Buskapazität C eingeben")
    t_r = I2C_MODI[w["modus"]]
    i_ol = 20e-3 if "Plus" in w["modus"] else 3e-3
    e = _fehler_umwandeln(sm.open_drain_pullup, w["Ub"], w["C"], 0.4, i_ol, t_r, w["R"])
    zeilen = [f"R_min = (U_B − 0.4 V) / I_OL = ({fmt(w['Ub'], 'spannung')} − 0.4 V) / {fmt(i_ol, 'strom')} = "
              f"{fmt(e['r_min'], 'widerstand')}",
              f"R_max = t_r / (0.847 · C) = {fmt(t_r, 'zeit')} / (0.847 · {fmt(w['C'], 'kapazitaet')}) = "
              f"{fmt(e['r_max'], 'widerstand')}"]
    if not e["moeglich"]:
        zeilen.append("❌ R_max < R_min: Buskapazität zu gross für diesen Modus → langsamer Modus, Bus-Puffer "
                      "(P82B715) oder kürzere Leitungen")
    else:
        zeilen.append(f"→ Pull-up zwischen {fmt(e['r_min'], 'widerstand')} und {fmt(e['r_max'], 'widerstand')} wählen")
    if w["R"] is not None:
        zeilen.append(f"Mit R = {fmt(w['R'], 'widerstand')}: t_r = {fmt(e['t_r'], 'zeit')}, LOW-Strom "
                      f"{fmt(e['i_low'], 'strom')}" + ("  ✓" if e["r_min"] <= w["R"] <= e["r_max"] else "  ⚠ ausserhalb"))
    return zeilen


def open_drain_pullup(master):
    return FormelRechner(
        master, "Pull-up für Open Drain / I²C", "Nach der I²C-Spezifikation: U_OL ≤ 0.4 V, Anstieg 30 → 70 %",
        felder=[("Ub", "Versorgung U_B", "spannung", {"platzhalter": "z.B. 3.3"}),
                ("C", "Buskapazität C", "kapazitaet", {"einheit": "pF", "platzhalter": "z.B. 200"}),
                ("modus", "I²C-Modus", "auswahl", {"werte": list(I2C_MODI)}),
                ("R", "gewählter R (opt.)", "widerstand", {"einheit": "kΩ", "platzhalter": "optional"})],
        berechnen=_open_drain_pullup, formel="R_min = (U_B − U_OL) / I_OL     R_max = t_r / (0.847 · C_Bus)")


# =============================================================================
# 14) SYNCHRONEN ZÄHLER ENTWERFEN
# =============================================================================
def _zaehler_entwurf(w):
    if w["folge"] is None:
        raise RechnerFehler("Zustandsfolge eingeben, z.B. 0 1 2 3 4 5 6 7 8 9 oder 0 1 3 2")
    folge = [_zahl(t) for t in w["folge"].replace(",", " ").replace("→", " ").split()]
    ff = "D" if w["ff"].startswith("D") else "JK"
    e = _fehler_umwandeln(swm.zaehler_entwurf, folge, ff)
    n = e["bits"]
    zeilen = [f"{n} Flipflops ({' '.join(e['namen'])}), {len(folge)} Zustände"
              + (f", unbenutzt (don't care): {', '.join(map(str, e['frei']))}" if e["frei"] else ""),
              "Folge: " + " → ".join(format(z, f"0{n}b") for z, _ in e["tabelle"]) + f" → {format(folge[0], f'0{n}b')}"]
    zeilen += [f"  {name} = {text}" for name, text in e["gleichungen"]]
    if e["frei"]:
        for z, weg, ok in swm.freie_zustaende_pruefen(e):
            zeilen.append(f"  Start in {z}: " + " → ".join(map(str, weg)) + ("  ✓ findet zurück" if ok else "  ⚠ hängt fest"))
    return zeilen


def zaehler_entwurf(master):
    return FormelRechner(
        master, "Synchronen Zähler entwerfen", "Zustandsfolge eingeben – die Ansteuergleichungen werden minimiert",
        felder=[("folge", "Zustandsfolge", "text", {"platzhalter": "z.B. 0 1 2 3 4 5 6 7 8 9"}),
                ("ff", "Flipflop-Typ", "auswahl", {"werte": ["D-Flipflop", "JK-Flipflop"]})],
        berechnen=_zaehler_entwurf, formel="D_i = Q_i⁺     JK: 0→0 J=0 K=X, 0→1 J=1 K=X, 1→0 J=X K=1, 1→1 J=X K=0")


# =============================================================================
# 15) HÖCHSTE TAKTFREQUENZ
# =============================================================================
def _fmax_schaltwerk(w):
    if w["tpd"] is None or w["tsu"] is None:
        raise RechnerFehler("t_pd (Takt → Q) und t_setup des Flipflops eingeben")
    t_logik = w["tlog"] or 0.0
    t_skew = w["tskew"] or 0.0
    e = _fehler_umwandeln(swm.fmax_synchron, w["tpd"], w["tsu"], t_logik, t_skew, w["th"])
    zeilen = [f"T_min = t_pd + t_Logik + t_setup + t_skew = {fmt(w['tpd'], 'zeit')} + {fmt(t_logik, 'zeit')} + "
              f"{fmt(w['tsu'], 'zeit')} + {fmt(t_skew, 'zeit')} = {fmt(e['t_min'], 'zeit')}",
              f"f_max = 1 / T_min = {fmt(e['f_max'], 'frequenz')}"]
    if w["th"] is not None:
        zeilen.append(f"Hold: t_pd + t_Logik − t_hold − t_skew = {fmt(e['hold_reserve'], 'zeit')}  "
                      + ("✓ eingehalten" if e["hold_ok"] else "❌ verletzt (Signal ändert sich zu früh)"))
    return zeilen


def fmax_schaltwerk(master):
    return FormelRechner(
        master, "Höchste Taktfrequenz (synchron)", "Längster Weg von Flipflop zu Flipflop – mit Setup und Hold",
        felder=[("tpd", "t_pd (Takt → Q)", "zeit", {"einheit": "ns", "platzhalter": "z.B. 10"}),
                ("tsu", "t_setup", "zeit", {"einheit": "ns", "platzhalter": "z.B. 5"}),
                ("tlog", "t_Logik (längster Pfad, opt.)", "zeit", {"einheit": "ns", "platzhalter": "0"}),
                ("tskew", "t_skew (Taktversatz, opt.)", "zeit", {"einheit": "ns", "platzhalter": "0"}),
                ("th", "t_hold (opt.)", "zeit", {"einheit": "ns", "platzhalter": "optional"})],
        berechnen=_fmax_schaltwerk, formel="f_max = 1 / (t_pd + t_Logik + t_setup + t_skew)")


# =============================================================================
# 16) FREQUENZTEILER
# =============================================================================
def _frequenzteiler(w):
    if w["f"] is None or w["m"] is None:
        raise RechnerFehler("Eingangsfrequenz und Teiler m eingeben")
    e = _fehler_umwandeln(swm.frequenzteiler, w["f"], w["m"])
    zeilen = [f"f_aus = f / m = {fmt(w['f'], 'frequenz')} / {int(w['m'])} = {fmt(e['f_aus'], 'frequenz')}"
              f"   (Periode {fmt(e['periode'], 'zeit')})",
              f"Flipflops: ⌈log2 {int(w['m'])}⌉ = {e['ff']}"]
    if e["zweierpotenz"]:
        zeilen.append("Zweierpotenz: einfacher Binärzähler, jede Stufe halbiert, Tastgrad 50 %")
        zeilen.append("Stufen: " + ", ".join(fmt(f, "frequenz") for f in e["zwischen"][:8])
                      + (" …" if len(e["zwischen"]) > 8 else ""))
    else:
        zeilen.append(f"Modulo-{int(w['m'])}-Zähler (synchron rücksetzen); Tastgrad am höchsten Bit ≠ 50 % – "
                      "für 50 %: durch m/2 teilen und danach ein T-Flipflop (bei geradem m)")
    return zeilen


def frequenzteiler(master):
    return FormelRechner(
        master, "Frequenzteiler mit Flipflops", "Wie viele Flipflops braucht ein Teiler durch m?",
        felder=[("f", "Eingangsfrequenz f", "frequenz", {"platzhalter": "z.B. 32768"}),
                ("m", "Teiler m", "zahl", {"platzhalter": "z.B. 32768"})],
        berechnen=_frequenzteiler, formel="f_aus = f / m     Flipflops = ⌈log2 m⌉")


# =============================================================================
# 17) UART: TIMING EINES FORMATS
# =============================================================================
DATENBITS = ["8", "7", "9", "6", "5"]


def _uart_timing(w):
    if w["baud"] is None:
        raise RechnerFehler("Baudrate eingeben, z.B. 9600 oder 115200")
    datenbits, stopbits = int(w["datenbits"]), float(w["stopbits"])
    e = _fehler_umwandeln(bm.uart_timing, w["baud"], datenbits, w["paritaet"], stopbits)
    zeilen = [f"Format {bm.uart_format(datenbits, w['paritaet'], stopbits)}: 1 Start + {datenbits} Daten"
              + ("" if w["paritaet"] == "keine" else " + 1 Parität") + f" + {stopbits:g} Stopp = {e['rahmen_bits']:g} Bit",
              f"t_bit = 1 / Baudrate = 1 / {w['baud']:g} Bd = {fmt(e['t_bit'], 'zeit')}",
              f"t_Rahmen = {e['rahmen_bits']:g} · t_bit = {fmt(e['t_rahmen'], 'zeit')}   →   "
              f"max. {e['bytes_s']:.1f} Zeichen/s",
              f"Nutzdaten: {datenbits} / {e['rahmen_bits']:g} = {e['nutzanteil'] * 100:.1f} %  →  "
              f"{fmt(e['nutz_bit_s'], 'zahl')} bit/s",
              f"Taktabweichung beider Seiten zusammen höchstens ≈ 0.5 / {e['rahmen_bits'] - 0.5:g} = "
              f"{e['toleranz_gesamt'] * 100:.1f} % (praktisch je Seite ≤ 2 %)"]
    if w["n"] is not None:
        if w["n"] < 1 or w["n"] != int(w["n"]):
            raise RechnerFehler("Anzahl Zeichen: ganze Zahl ≥ 1")
        zeilen.append(f"{int(w['n'])} Zeichen ohne Pausen: {fmt(w['n'] * e['t_rahmen'], 'zeit')}")
    return zeilen


def uart_timing(master):
    return FormelRechner(
        master, "UART: Bitzeit und Datenrate", "Wie lange dauert ein Zeichen, wie viele passen in eine Sekunde?",
        felder=[("baud", "Baudrate", "zahl", {"platzhalter": "z.B. 9600"}),
                ("datenbits", "Datenbits", "auswahl", {"werte": DATENBITS}),
                ("paritaet", "Parität", "auswahl", {"werte": bm.PARITAETEN}),
                ("stopbits", "Stoppbits", "auswahl", {"werte": ["1", "2", "1.5"]}),
                ("n", "Anzahl Zeichen (opt.)", "zahl", {"platzhalter": "optional"})],
        berechnen=_uart_timing, formel="t_bit = 1 / Baudrate     Zeichen/s = Baudrate / Rahmenbits")


# =============================================================================
# 18) UART: BAUDRATEN-TEILER
# =============================================================================
BAUDQUARZE = "1.8432, 3.6864, 7.3728, 11.0592, 14.7456 MHz"
UEBERABTASTUNG = {"16-fach (normal)": 16, "8-fach (doppelte Geschwindigkeit)": 8}


def _uart_baudrate(w):
    if w["f"] is None or w["baud"] is None:
        raise RechnerFehler("Takt des µC und gewünschte Baudrate eingeben")
    k = UEBERABTASTUNG[w["ueber"]]
    e = _fehler_umwandeln(bm.baud_teiler, w["f"], w["baud"], k)
    fehler = abs(e["fehler"]) * 100
    f_text = fmt(w["f"], "frequenz", 6)
    zeilen = [f"N = f / ({k} · Baudrate) = {f_text} / ({k} · {w['baud']:g}) = {e['ideal']:.3f} "
              f"→ gerundet N = {e['teiler']}  (AVR: UBRR = N − 1 = {e['register']})",
              f"tatsächlich: {f_text} / ({k} · {e['teiler']}) = {e['ist']:.1f} Bd",
              f"Fehler = {e['fehler'] * 100:+.2f} %"]
    if fehler <= 0.5:
        zeilen[-1] += "  ✓ sehr gut"
    elif fehler <= 2:
        zeilen[-1] += "  ✓ in Ordnung (≤ 2 %)"
    elif fehler <= 4.5:
        zeilen[-1] += "  ⚠ grenzwertig – funktioniert nur, wenn die Gegenseite fast genau ist"
    else:
        zeilen[-1] += "  ❌ zu gross – Zeichen werden falsch empfangen"
    if fehler > 0.5:
        zeilen.append(f"Abhilfe: anderer Takt („Baudratenquarz“ {BAUDQUARZE} ergibt 0 %), "
                      "8-fache Überabtastung oder kleinere Baudrate")
    return zeilen


def uart_baudrate(master):
    return FormelRechner(
        master, "UART: Baudraten-Teiler und Fehler", "Trifft der µC-Takt die gewünschte Baudrate genau genug?",
        felder=[("f", "Takt f des µC", "frequenz", {"einheit": "MHz", "platzhalter": "z.B. 16"}),
                ("baud", "Baudrate", "zahl", {"platzhalter": "z.B. 115200"}),
                ("ueber", "Überabtastung", "auswahl", {"werte": list(UEBERABTASTUNG)})],
        berechnen=_uart_baudrate, formel="N = round(f / (16 · Baudrate))     Fehler = f / (16 · N · Baudrate) − 1")


# =============================================================================
# 19) SPI-ÜBERTRAGUNG
# =============================================================================
SPI_MODI = ["Modus 0", "Modus 1", "Modus 2", "Modus 3"]


def _spi_uebertragung(w):
    m = bm.spi_modus(SPI_MODI.index(w["modus"]))
    zeilen = [f"{w['modus']}: CPOL = {m['cpol']}, CPHA = {m['cpha']}  →  SCLK in Ruhe {'HIGH' if m['ruhe'] else 'LOW'}, "
              f"abtasten an der {m['abtast']}en Flanke, Daten wechseln an der {m['schiebe']}en"]
    if w["f"] is None:
        return zeilen
    n = w["n"] if w["n"] is not None else 1
    if n < 1 or n != int(n):
        raise RechnerFehler("Anzahl Bytes: ganze Zahl ≥ 1")
    e = _fehler_umwandeln(bm.spi_dauer, w["f"], int(n))
    zeilen += [f"t = {int(n)} · 8 / f_SCLK = {e['takte']} / {fmt(w['f'], 'frequenz')} = {fmt(e['dauer'], 'zeit')}"
               "  (ohne Pausen zwischen den Bytes)",
               f"Datenrate: {fmt(e['bytes_s'], 'zahl')} Byte/s je Richtung (Vollduplex)"]
    return zeilen


def spi_uebertragung(master):
    return FormelRechner(
        master, "SPI: Modus und Übertragungsdauer", "CPOL/CPHA nachschlagen und die Dauer einer Übertragung berechnen",
        felder=[("modus", "SPI-Modus", "auswahl", {"werte": SPI_MODI}),
                ("f", "Takt f_SCLK (opt.)", "frequenz", {"einheit": "MHz", "platzhalter": "z.B. 8"}),
                ("n", "Anzahl Bytes (opt.)", "zahl", {"platzhalter": "1"})],
        berechnen=_spi_uebertragung, formel="Modus = 2 · CPOL + CPHA     t = 8 · n / f_SCLK")


# =============================================================================
# 20) I²C-ÜBERTRAGUNG
# =============================================================================
def _i2c_uebertragung(w):
    if w["n"] is None:
        raise RechnerFehler("Anzahl Datenbytes eingeben")
    if w["n"] < 0 or w["n"] != int(w["n"]):
        raise RechnerFehler("Anzahl Datenbytes: ganze Zahl ≥ 0")
    f = w["f"] if w["f"] is not None else bm.I2C_MODI[w["modus"]]
    e = _fehler_umwandeln(bm.i2c_dauer, f, w["art"], int(w["n"]))
    n = int(w["n"])
    if w["art"] == "Register lesen":
        aufbau = f"S + 9 (Adresse+W+ACK) + 9 (Register+ACK) + Sr + 9 (Adresse+R+ACK) + 9 · {n} + P"
    else:
        aufbau = f"S + 9 (Adresse+R/W+ACK) + 9 · {n} (Byte+ACK) + P"
    zeilen = [f"Takte ≈ {aufbau} = {e['takte']}",
              f"t ≈ {e['takte']} / {fmt(f, 'frequenz')} = {fmt(e['dauer'], 'zeit')}  "
              "(ohne Clock Stretching und Pausen)"]
    if n:
        zeilen.append(f"Nutzdaten: {8 * n} Bit in {fmt(e['dauer'], 'zeit')} = {fmt(e['nutz_bit_s'], 'zahl')} bit/s "
                      f"({e['anteil'] * 100:.0f} % der Takte)")
    if w["f"] is not None and w["f"] > 1e6:
        zeilen.append("⚠ Über 1 MHz nur im High-speed-mode (3.4 MHz) mit besonderen Treibern")
    return zeilen


def i2c_uebertragung(master):
    return FormelRechner(
        master, "I²C: Dauer einer Übertragung", "Wie lange braucht ein Schreib- oder Lesezugriff?",
        felder=[("modus", "Modus", "auswahl", {"werte": list(bm.I2C_MODI)}),
                ("art", "Zugriff", "auswahl", {"werte": bm.I2C_ARTEN}),
                ("n", "Datenbytes", "zahl", {"platzhalter": "z.B. 2"}),
                ("f", "eigener Takt f_SCL (opt.)", "frequenz", {"einheit": "kHz", "platzhalter": "optional"})],
        berechnen=_i2c_uebertragung, formel="Takte ≈ 1 + 9 · (1 + n) + 1     t = Takte / f_SCL")


# =============================================================================
# 21) SPEICHER-ORGANISATION
# =============================================================================
def _speicher_organisation(w):
    if w["a"] is None or w["d"] is None:
        raise RechnerFehler("Adressbits und Datenbits eingeben")
    if w["a"] != int(w["a"]) or w["d"] != int(w["d"]):
        raise RechnerFehler("Ganze Zahlen eingeben")
    a, d = int(w["a"]), int(w["d"])
    o = _fehler_umwandeln(bm.speicher_organisation, a, d)
    worte_text, bits_text = bm.groesse_text(o["worte"], ""), bm.groesse_text(o["bits"])
    return [f"Wörter = 2^{a} = {o['worte']}" + (f" ({worte_text.strip()})" if o["worte"] >= 1024 else ""),
            f"Kapazität = 2^{a} · {d} Bit = {o['bits']} Bit" + (f" = {bits_text}" if o["bits"] >= 1024 else "")
            + (f" = {bm.groesse_text(int(o['bytes']), 'Byte')}" if o["bits"] % 8 == 0 else ""),
            f"Adressen 0x{0:0{o['hex_stellen']}X} … 0x{o['hoechste']:0{o['hex_stellen']}X}   "
            f"(A{a - 1} … A0, Daten D{d - 1} … D0)"]


def speicher_organisation(master):
    return FormelRechner(
        master, "Speicher: Organisation und Kapazität", "Aus Adress- und Datenbits: Wörter, Bit, Byte, Adressbereich",
        felder=[("a", "Adressbits a", "zahl", {"platzhalter": "z.B. 15 (62256)"}),
                ("d", "Datenbits d (Wortbreite)", "zahl", {"platzhalter": "z.B. 8"})],
        berechnen=_speicher_organisation, formel="Wörter = 2^a     Kapazität = 2^a · d Bit")


# =============================================================================
# 22) SPEICHER ERWEITERN
# =============================================================================
def _speicher_erweitern(w):
    for name in ("ziel", "zb", "chip", "cb"):
        if w[name] is None:
            raise RechnerFehler("Ziel (Wörter × Bit) und Chip (Wörter × Bit) eingeben, z.B. 64K × 16 aus 32K × 8")
    ziel = _fehler_umwandeln(bm.worte_einlesen, w["ziel"])
    chip = _fehler_umwandeln(bm.worte_einlesen, w["chip"])
    if w["zb"] != int(w["zb"]) or w["cb"] != int(w["cb"]):
        raise RechnerFehler("Wortbreiten als ganze Zahl eingeben")
    zb, cb = int(w["zb"]), int(w["cb"])
    e = _fehler_umwandeln(bm.speicher_erweitern, ziel, zb, chip, cb)
    zeilen = [f"Wortbreite: ⌈{zb} / {cb}⌉ = {e['nebeneinander']} Chips nebeneinander (gleiche Adresse, gleiches ¬CS)",
              f"Tiefe: {bm.groesse_text(ziel, '')} / {bm.groesse_text(chip, '')} = {e['untereinander']} Reihen "
              "untereinander (gemeinsamer Datenbus, ein Decoder wählt per ¬CS)",
              f"→ {e['chips']} Chips   ·   Adressbits gesamt: {e['adressbits']} (A{e['adressbits'] - 1} … A0), "
              f"jeder Chip bekommt A{e['adressbits_chip'] - 1} … A0"]
    if e["decoder_bits"]:
        bereich = (f"A{e['adressbits'] - 1}" if e["decoder_bits"] == 1 else
                   f"A{e['adressbits'] - 1} … A{e['adressbits_chip']}")
        zeilen.append(f"Decoder an {bereich} ({e['decoder_bits']} Bit → {2 ** e['decoder_bits']} ¬CS-Leitungen"
                      + (", bei 1 Bit reicht ein Inverter" if e["decoder_bits"] == 1 else "") + ")")
    if ziel < chip:
        zeilen.append("Hinweis: Der Chip ist grösser als nötig – ein Teil bleibt ungenutzt")
    if e["ungenutzt_bits"]:
        zeilen.append(f"Hinweis: {e['ungenutzt_bits']} Datenbit(s) je Adresse bleiben ungenutzt")
    return zeilen


def speicher_erweitern(master):
    return FormelRechner(
        master, "Speicher erweitern (Tiefe und Wortbreite)", "Aus kleinen Speicherchips einen grösseren Speicher bauen",
        felder=[("ziel", "Ziel: Wörter", "text", {"platzhalter": "z.B. 64K"}),
                ("zb", "Ziel: Wortbreite (Bit)", "zahl", {"platzhalter": "z.B. 16"}),
                ("chip", "Chip: Wörter", "text", {"platzhalter": "z.B. 32K"}),
                ("cb", "Chip: Wortbreite (Bit)", "zahl", {"platzhalter": "z.B. 8"})],
        berechnen=_speicher_erweitern,
        formel="Chips = ⌈Breite_Ziel / Breite_Chip⌉ · Wörter_Ziel / Wörter_Chip     Decoder-Bits = log2(Reihen)")


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
    "wahrheitstabelle": wahrheitstabelle,
    "ausdruck_vergleichen": ausdruck_vergleichen,
    "kv_minimieren": kv_minimieren,
    "werkzeug_gatter": GatterKarte,
    "werkzeug_ausdruck": AusdruckKarte,
    "werkzeug_kv": KVKarte,
    "addierer_laufzeit": addierer_laufzeit,
    "mux_funktion": mux_funktion,
    "siebensegment": siebensegment,
    "adressdecoder": adressdecoder,
    "open_drain_pullup": open_drain_pullup,
    "werkzeug_addierer": AddiererKarte,
    "werkzeug_mux": MuxKarte,
    "werkzeug_decoder": DecoderKarte,
    "werkzeug_ausgang": AusgangKarte,
    "zaehler_entwurf": zaehler_entwurf,
    "fmax_schaltwerk": fmax_schaltwerk,
    "frequenzteiler": frequenzteiler,
    "werkzeug_flipflop": FlipflopKarte,
    "werkzeug_zaehler": ZaehlerKarte,
    "werkzeug_schieberegister": SchieberegisterKarte,
    "uart_timing": uart_timing,
    "uart_baudrate": uart_baudrate,
    "spi_uebertragung": spi_uebertragung,
    "i2c_uebertragung": i2c_uebertragung,
    "speicher_organisation": speicher_organisation,
    "speicher_erweitern": speicher_erweitern,
    "werkzeug_uart": UartKarte,
    "werkzeug_spi": SpiKarte,
    "werkzeug_i2c": I2cKarte,
    "werkzeug_speicher": SpeicherKarte,
}
