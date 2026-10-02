# =============================================================================
# digitaltechnik/zahlen_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für Zahlensysteme, Codes, Zweierkomplement und Bitmasken.
# KEIN tkinter - einzeln testbar, z.B.:
#
#   python -c "from digitaltechnik.zahlen_mathe import *; print(darstellungen(200, 8))"
#
#   einlesen()            Text wie "0xFF", "1010 1100", "-42" -> ganze Zahl
#   darstellungen()       Dezimal, Binär, Hex, Oktal, BCD, Gray, ASCII einer Zahl
#   zweierkomplement()    Bitmuster einer (negativen) Zahl mit n Bit + Rechenweg
#   als_vorzeichen()      Bitmuster als vorzeichenbehaftete Zahl lesen
#   addieren()            a + b mit n Bit: Ergebnis, Carry (C) und Overflow (V)
#   bitoperation()        AND / OR / XOR / NOT / Schieben mit einer Maske
#
# WER RUFT DAS AUF?  digitaltechnik/grafiken.py, digitaltechnik/rechner.py
# =============================================================================

BASEN = {"Dezimal": 10, "Binär": 2, "Hexadezimal": 16, "Oktal": 8}
PRAEFIX = {"0b": 2, "0x": 16, "0o": 8}
ZIFFERN = "0123456789ABCDEF"
OPERATIONEN = ["AND (Bits prüfen)", "OR (Bits setzen)", "AND NOT (Bits löschen)", "XOR (Bits umschalten)",
               "NOT (alle invertieren)", "<< (links schieben)", ">> (rechts schieben)"]


def _bits_pruefen(bits):
    if not isinstance(bits, int) or bits < 1 or bits > 64:
        raise ValueError("Bitbreite zwischen 1 und 64 wählen")


# =============================================================================
# EINLESEN
# =============================================================================
def einlesen(text, basis=None):
    """
    Liest eine ganze Zahl aus Text. Leerzeichen, _ und ' dürfen zum Gruppieren benutzt werden.
      basis=None: Präfix entscheidet (0b…, 0x…, 0o…), sonst dezimal
      basis=2/8/10/16: so lesen (ein passendes Präfix ist trotzdem erlaubt)
    """
    if text is None or not str(text).strip():
        raise ValueError("Zahl eingeben")
    t = str(text).strip().replace(" ", "").replace("_", "").replace("'", "")
    negativ = t.startswith("-")
    if negativ or t.startswith("+"):
        t = t[1:]
    praefix = t[:2].lower()
    if praefix in PRAEFIX:
        if basis is not None and basis != PRAEFIX[praefix]:
            raise ValueError(f"Präfix {praefix} passt nicht zur gewählten Basis {basis}")
        basis, t = PRAEFIX[praefix], t[2:]
    basis = basis or 10
    if not t:
        raise ValueError("Nach dem Präfix fehlen die Ziffern")
    erlaubt = ZIFFERN[:basis]
    falsch = sorted({z for z in t.upper() if z not in erlaubt})
    if falsch:
        raise ValueError(f"Ziffer(n) {', '.join(falsch)} gibt es in Basis {basis} nicht (erlaubt: {erlaubt})")
    wert = int(t, basis)
    return -wert if negativ else wert


# =============================================================================
# DARSTELLUNGEN
# =============================================================================
def gruppiert(text, gruppe=4):
    """'10101100' -> '1010 1100' (von rechts in Gruppen)"""
    teile = []
    while text:
        teile.insert(0, text[-gruppe:])
        text = text[:-gruppe]
    return " ".join(teile)


def binaer(wert, bits):
    """Bitmuster (vorzeichenlos, wert ≥ 0) mit genau 'bits' Stellen, in 4er-Gruppen."""
    return gruppiert(format(wert, f"0{bits}b"))


def bits_noetig(wert):
    """Wie viele Bit braucht die Zahl? (vorzeichenlos bzw. mit Vorzeichen im Zweierkomplement)"""
    if wert >= 0:
        return max(wert.bit_length(), 1)
    return (-wert - 1).bit_length() + 1


def bcd(wert):
    """Jede Dezimalziffer als 4-Bit-Gruppe (8421-BCD): 59 -> 0101 1001"""
    if wert < 0:
        raise ValueError("BCD hier nur für Zahlen ≥ 0")
    return " ".join(format(int(z), "04b") for z in str(wert))


def gray(wert):
    """Gray-Code: benachbarte Zahlen unterscheiden sich in genau einem Bit:  g = n XOR (n >> 1)"""
    if wert < 0:
        raise ValueError("Gray-Code nur für Zahlen ≥ 0")
    return wert ^ (wert >> 1)


def darstellungen(wert, bits=None):
    """
    Alle üblichen Schreibweisen einer Zahl. Negative Zahlen brauchen eine Bitbreite (Zweierkomplement).
    Rückgabe: dict mit dez, bin, hex, okt, bcd, gray, ascii, bits, muster (vorzeichenlos), vorzeichen (gelesen als signed)
    """
    if bits is None:
        bits = max(8, -(-bits_noetig(wert) // 4) * 4)
    _bits_pruefen(bits)
    if wert < 0:
        muster = zweierkomplement(wert, bits)["muster"]
    else:
        if wert >= 2 ** bits:
            raise ValueError(f"{wert} passt nicht in {bits} Bit (max. {2 ** bits - 1})")
        muster = wert
    stellen = -(-bits // 4)
    e = {"dez": wert, "bits": bits, "muster": muster, "bin": binaer(muster, bits),
         "hex": format(muster, f"0{stellen}X"), "okt": format(muster, "o"),
         "unsigned": muster, "signed": als_vorzeichen(muster, bits)}
    e["bcd"] = bcd(wert) if wert >= 0 else None
    e["gray"] = binaer(gray(wert), bits) if wert >= 0 else None
    e["ascii"] = chr(muster) if 32 <= muster <= 126 else None
    return e


# =============================================================================
# ZWEIERKOMPLEMENT
# =============================================================================
def bereich(bits, mit_vorzeichen=True):
    """Wertebereich mit n Bit:  signed −2^(n−1) … 2^(n−1) − 1,  unsigned 0 … 2^n − 1"""
    _bits_pruefen(bits)
    if mit_vorzeichen:
        return -(2 ** (bits - 1)), 2 ** (bits - 1) - 1
    return 0, 2 ** bits - 1


def zweierkomplement(wert, bits):
    """
    Bitmuster von 'wert' im Zweierkomplement mit n Bit:
      positiv: normal binär (MSB = 0)
      negativ: |wert| binär -> alle Bits invertieren (Einerkomplement) -> +1
      gleichbedeutend: Muster = 2^n + wert
    Rückgabe: muster, Rechenweg (betrag, invertiert, plus_eins als Text)
    """
    tief, hoch = bereich(bits)
    if not tief <= wert <= hoch:
        raise ValueError(f"{wert} passt nicht in {bits} Bit mit Vorzeichen ({tief} … {hoch})")
    muster = wert % (2 ** bits)
    e = {"muster": muster, "bin": binaer(muster, bits), "hex": format(muster, f"0{-(-bits // 4)}X")}
    if wert < 0:
        betrag = -wert
        invertiert = (~betrag) & (2 ** bits - 1)
        e.update({"betrag": binaer(betrag, bits), "invertiert": binaer(invertiert, bits),
                  "plus_eins": binaer((invertiert + 1) & (2 ** bits - 1), bits)})
    return e


def als_vorzeichen(muster, bits):
    """Bitmuster als signed lesen: MSB hat die Wertigkeit −2^(n−1)."""
    _bits_pruefen(bits)
    if not 0 <= muster < 2 ** bits:
        raise ValueError(f"Muster passt nicht in {bits} Bit")
    return muster - 2 ** bits if muster >= 2 ** (bits - 1) else muster


def addieren(a, b, bits):
    """
    a + b mit n Bit (Addierwerk rechnet immer vorzeichenlos – die Deutung macht der Mensch):
      C (Carry)    = Übertrag aus dem MSB          -> Überlauf, wenn man UNSIGNED rechnet
      V (Overflow) = zwei gleiche Vorzeichen ergeben ein anderes Vorzeichen -> Überlauf bei SIGNED
    a und b dürfen signed oder unsigned eingegeben werden (Muster = Wert mod 2^n).
    """
    _bits_pruefen(bits)
    m = 2 ** bits
    for name, x in (("a", a), ("b", b)):
        if not -(m // 2) <= x < m:
            raise ValueError(f"{name} = {x} passt nicht in {bits} Bit")
    ma, mb = a % m, b % m
    roh = ma + mb
    summe = roh % m
    msb = m // 2
    v = (ma & msb) == (mb & msb) and (summe & msb) != (ma & msb)
    return {"muster_a": ma, "muster_b": mb, "summe": summe, "carry": roh >= m, "overflow": v,
            "unsigned": summe, "signed": als_vorzeichen(summe, bits),
            "bin_a": binaer(ma, bits), "bin_b": binaer(mb, bits), "bin_summe": binaer(summe, bits)}


# =============================================================================
# BITMASKEN
# =============================================================================
def maske_aus_bits(nummern):
    """[0, 3] -> 0b1001  (Bit n hat die Wertigkeit 2^n, Bit 0 = LSB)"""
    maske = 0
    for n in nummern:
        if n < 0 or n > 63:
            raise ValueError("Bitnummern von 0 bis 63")
        maske |= 1 << n
    return maske


def bitoperation(wert, maske, operation, bits=8, schritte=1):
    """
    Typische Registeroperationen (Ergebnis auf n Bit begrenzt):
      AND       wert & maske        -> prüfen: nur die Bits der Maske bleiben
      OR        wert | maske        -> setzen
      AND NOT   wert & ~maske       -> löschen
      XOR       wert ^ maske        -> umschalten
      NOT       ~wert               -> alle invertieren (Maske egal)
      << / >>   schieben um 'schritte' Stellen (× bzw. ÷ 2^schritte, logisch)
    Rückgabe: ergebnis, geaendert (welche Bits sich geändert haben), Ausdruck in C-Schreibweise
    """
    _bits_pruefen(bits)
    voll = 2 ** bits - 1
    for name, x in (("Wert", wert), ("Maske", maske)):
        if not 0 <= x <= voll:
            raise ValueError(f"{name} passt nicht in {bits} Bit (0 … {voll})")
    if operation not in OPERATIONEN:
        raise ValueError(f"Unbekannte Operation: {operation}")
    if schritte < 0 or schritte > bits:
        raise ValueError(f"Schieben um 0 … {bits} Stellen")
    nr = OPERATIONEN.index(operation)
    hx = f"0x{maske:0{-(-bits // 4)}X}"
    ergebnis, c = [
        (wert & maske, f"x & {hx}"),
        (wert | maske, f"x |= {hx}"),
        (wert & ~maske & voll, f"x &= ~{hx}"),
        (wert ^ maske, f"x ^= {hx}"),
        (~wert & voll, "x = ~x"),
        ((wert << schritte) & voll, f"x <<= {schritte}"),
        (wert >> schritte, f"x >>= {schritte}"),
    ][nr]
    return {"ergebnis": ergebnis, "geaendert": ergebnis ^ wert, "c": c, "bin": binaer(ergebnis, bits),
            "verloren": ((wert << schritte) >> bits) if nr == 5 else (wert & ((1 << schritte) - 1) if nr == 6 else 0)}
