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
#   werkzeug_*            INTERAKTIVE Werkzeuge (digitaltechnik/grafiken.py)
#
# AD-Wandler und Abtastung gibt es schon im Bereich Messtechnik ("adc", "abtastung").
# Rechnung: digitaltechnik/zahlen_mathe.py, pegel_mathe.py, logik_mathe.py, schaltnetze_mathe.py (ohne GUI)
# WER RUFT DAS AUF?  bauteile/rechner/__init__.py (_MODULE) -> erstellen(master, "zahlensystem")
# =============================================================================

from bauteile.rechner.basis import FormelRechner, RechnerFehler, fmt          # -> bauteile/rechner/basis.py
from digitaltechnik import logik_mathe as lm                                  # -> digitaltechnik/logik_mathe.py
from digitaltechnik import pegel_mathe as pm                                  # -> digitaltechnik/pegel_mathe.py
from digitaltechnik import schaltnetze_mathe as sm                            # -> digitaltechnik/schaltnetze_mathe.py
from digitaltechnik import zahlen_mathe as zm                                 # -> digitaltechnik/zahlen_mathe.py
from digitaltechnik.grafiken import (BitmaskenKarte, LogikpegelKarte,         # -> digitaltechnik/grafiken.py
                                     ZahlensystemKarte, ZweierkomplementKarte)
from digitaltechnik.grafiken_schaltnetze import (AddiererKarte, AusgangKarte,    # -> digitaltechnik/grafiken_schaltnetze.py
                                                 DecoderKarte, MuxKarte)
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
}
