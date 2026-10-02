# =============================================================================
# digitaltechnik/schaltnetze_mathe.py
# -----------------------------------------------------------------------------
# REINE FUNKTIONEN für Schaltnetze - KEIN tkinter. Einzeln testbar, z.B.:
#
#   python -c "from digitaltechnik.schaltnetze_mathe import *; print(ripple(0b0110, 0b0011, 4))"
#
#   halbaddierer(), volladdierer()   eine Stelle: Summe und Übertrag
#   ripple()                         n-Bit-Addierer/Subtrahierer aus Volladdierern, Stufe für Stufe
#   laufzeit()                       Worst-Case-Laufzeit der Übertragskette
#   mux(), demux()                   Datenweg mit Auswahleingängen
#   mux_funktion()                   Logikfunktion mit einem MUX bauen (Shannon-Zerlegung)
#   decoder(), prioritaets_encoder() 3:8-Decoder (74HC138), 8:3-Prioritäts-Encoder (74HC148)
#   siebensegment()                  Hex-Ziffer -> Segmente a … g (gemeinsame Kathode / Anode)
#   adressdecoder()                  Adressbereiche der Decoder-Ausgänge (Chip-Select)
#   open_drain_pullup()              Pull-up an Open-Drain-Leitung (I²C): R_min aus I_OL, R_max aus t_r
#   buskonflikt()                    Kurzschlussstrom, wenn zwei Push-Pull-Ausgänge gegeneinander treiben
#
# WER RUFT DAS AUF?  digitaltechnik/grafiken_schaltnetze.py, digitaltechnik/rechner.py
# =============================================================================

import math

from digitaltechnik import logik_mathe as lm                           # -> digitaltechnik/logik_mathe.py

T_R_FAKTOR = math.log(0.7 / 0.3)          # I²C: Anstieg von 0.3 · U_B auf 0.7 · U_B dauert 0.847 · R · C
R_ON_HC = 50.0                            # Ω, typischer Ausgangswiderstand 74HC bei 5 V (≈ 4 mA bei 0.2 V)

# Segmente a … g, Bit 0 = a  (a oben, b rechts oben, c rechts unten, d unten, e links unten, f links oben, g Mitte)
SEGMENTE = {0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg", 6: "acdefg", 7: "abc",
            8: "abcdefg", 9: "abcdfg", 10: "abcefg", 11: "cdefg", 12: "adef", 13: "bcdeg", 14: "adefg", 15: "aefg"}


def _bits_pruefen(bits):
    if bits < 1 or bits > 32:
        raise ValueError("Bitbreite zwischen 1 und 32")


# =============================================================================
# ADDIERER
# =============================================================================
def halbaddierer(a, b):
    """S = A ⊕ B,  C = A · B"""
    return a ^ b, a & b


def volladdierer(a, b, c_ein):
    """S = A ⊕ B ⊕ C_ein,  C_aus = A·B + C_ein·(A ⊕ B)   (aus zwei Halbaddierern + OR)"""
    s1, c1 = halbaddierer(a, b)
    s, c2 = halbaddierer(s1, c_ein)
    return s, c1 | c2


def ripple(a, b, bits, subtrahieren=False, c_ein=0):
    """
    Ripple-Carry-Addierer: n Volladdierer, der Übertrag läuft von Stelle 0 (LSB) zur höchsten Stelle.
    Subtrahieren: B wird bitweise invertiert (XOR mit 1) und C_ein = 1  ->  A + ¬B + 1 = A − B.
    Rückgabe: Stufen [(a_i, b_i (nach XOR), c_ein_i, s_i, c_aus_i), …] ab LSB, Summe, C, V
      V (Overflow) = Übertrag in die höchste Stelle XOR Übertrag aus der höchsten Stelle
      Bei der Subtraktion bedeutet C = 0 "Borgen" (A < B unsigned).
    """
    _bits_pruefen(bits)
    maske = 2 ** bits - 1
    if not (0 <= a <= maske and 0 <= b <= maske):
        raise ValueError(f"A und B müssen in {bits} Bit passen (0 … {maske})")
    c = 1 if subtrahieren else c_ein
    stufen, summe = [], 0
    for i in range(bits):
        ai, bi = (a >> i) & 1, ((b >> i) & 1) ^ (1 if subtrahieren else 0)
        s, c_aus = volladdierer(ai, bi, c)
        stufen.append((ai, bi, c, s, c_aus))
        summe |= s << i
        c = c_aus
    v = stufen[-1][2] ^ stufen[-1][4]
    return {"stufen": stufen, "summe": summe, "carry": c, "overflow": v,
            "signed": summe - 2 ** bits if summe >> (bits - 1) else summe}


def laufzeit(bits, t_carry, t_summe=None):
    """
    Ripple-Carry, ungünstigster Fall (Übertrag läuft durch alle Stufen):
      bis C_aus:              n · t_carry
      bis zum höchsten S:     (n − 1) · t_carry + t_summe
    f_max ≈ 1 / t_gesamt (wenn das Ergebnis jeden Takt fertig sein muss)
    """
    _bits_pruefen(bits)
    if t_carry <= 0:
        raise ValueError("Laufzeit pro Stufe muss grösser als 0 sein")
    t_summe = t_carry if t_summe is None else t_summe
    t_c, t_s = bits * t_carry, (bits - 1) * t_carry + t_summe
    gesamt = max(t_c, t_s)
    return {"t_carry_ges": t_c, "t_summe_ges": t_s, "t_ges": gesamt, "f_max": 1 / gesamt}


# =============================================================================
# MULTIPLEXER
# =============================================================================
def mux(daten, auswahl):
    """Y = D[auswahl]   (daten als Liste, auswahl als Zahl)"""
    if not 0 <= auswahl < len(daten):
        raise ValueError(f"Auswahl {auswahl} gibt es nicht (0 … {len(daten) - 1})")
    return daten[auswahl]


def demux(eingang, auswahl, ausgaenge):
    """Eingang auf Ausgang Y[auswahl], alle anderen 0."""
    if not 0 <= auswahl < ausgaenge:
        raise ValueError(f"Auswahl {auswahl} gibt es nicht (0 … {ausgaenge - 1})")
    return [eingang if k == auswahl else 0 for k in range(ausgaenge)]


def auswahl_bits(eingaenge):
    """Ein MUX mit n Dateneingängen braucht ⌈log2 n⌉ Auswahlleitungen."""
    if eingaenge < 2:
        raise ValueError("Mindestens 2 Dateneingänge")
    return math.ceil(math.log2(eingaenge))


def mux_funktion(text, k=None):
    """
    Logikfunktion mit einem 2^k:1-MUX bauen (Shannon-Zerlegung):
      die ersten k Variablen an die Auswahleingänge,
      an D_i kommt die Restfunktion der übrigen Variablen (0, 1, X, ¬X oder ein kleiner Ausdruck).
    Ohne k: k = Anzahl Variablen − 1 (der klassische Trick: n Variablen mit einem 2^(n−1):1-MUX).
    """
    e = lm.analysieren(text)
    namen = e["namen"]
    n = len(namen)
    if n < 2:
        raise ValueError("Mindestens zwei Variablen für einen MUX")
    k = n - 1 if k is None else k
    if not 1 <= k <= min(n, 4):
        raise ValueError(f"Auswahlleitungen zwischen 1 und {min(n, 4)}")
    rest = namen[k:]
    daten = []
    for i in range(2 ** k):
        teil = [m - (i << (n - k)) for m in e["minterme"] if m >> (n - k) == i]
        if not rest:
            daten.append("1" if teil else "0")
        else:
            daten.append(lm.minimal_formen(teil, rest)["min_dnf"])
    return {"namen": namen, "auswahl": namen[:k], "rest": rest, "daten": daten, "text": e["text"]}


# =============================================================================
# DECODER / ENCODER / 7-SEGMENT
# =============================================================================
def decoder(adresse, bits=3, freigabe=True, aktiv_low=True):
    """
    n:2^n-Decoder: genau der Ausgang Y[adresse] ist aktiv (74HC138: Ausgänge aktiv LOW).
    Ohne Freigabe ist kein Ausgang aktiv. Rückgabe: Liste der PEGEL an Y0 … Y(2^n − 1).
    """
    if not 0 <= adresse < 2 ** bits:
        raise ValueError(f"Adresse 0 … {2 ** bits - 1}")
    aktiv = [1 if (freigabe and k == adresse) else 0 for k in range(2 ** bits)]
    return [1 - x for x in aktiv] if aktiv_low else aktiv


def prioritaets_encoder(eingaenge):
    """
    Prioritäts-Encoder (aktiv HIGH gedacht): der HÖCHSTE aktive Eingang bestimmt den Code.
    Rückgabe: (code, gueltig)  – gueltig = 0, wenn kein Eingang aktiv ist (74HC148: GS-Ausgang).
    """
    for k in range(len(eingaenge) - 1, -1, -1):
        if eingaenge[k]:
            return k, 1
    return 0, 0


def siebensegment(ziffer, gemeinsame_anode=False):
    """
    Hex-Ziffer 0 … 15 -> eingeschaltete Segmente und Pegel an a … g.
      gemeinsame Kathode: Segment an = HIGH;   gemeinsame Anode: Segment an = LOW
    Rückgabe: segmente ('abcdef'), pegel {a: 1, …}, muster (Bit 0 = a, Bit 6 = g)
    """
    if not 0 <= ziffer <= 15:
        raise ValueError("Ziffer 0 … 15 (0 … F)")
    an = SEGMENTE[ziffer]
    muster = sum(1 << "abcdefg".index(s) for s in an)
    pegel = {s: (0 if s in an else 1) if gemeinsame_anode else (1 if s in an else 0) for s in "abcdefg"}
    if gemeinsame_anode:
        muster = (~muster) & 0x7F
    return {"segmente": an, "pegel": pegel, "muster": muster}


def adressdecoder(adressbits, decoder_bits):
    """
    Speicher-/IO-Adressraum mit 2^N Adressen, die obersten k Adressbits an einen k:2^k-Decoder:
      jeder Ausgang ist für einen Block von 2^(N−k) Adressen zuständig.
    Rückgabe: Liste (ausgang, von, bis), blockgroesse
    """
    if not 1 <= decoder_bits <= adressbits <= 32:
        raise ValueError("1 ≤ Decoder-Bits ≤ Adressbits ≤ 32")
    if decoder_bits > 6:
        raise ValueError("Höchstens 6 Decoder-Bits (64 Ausgänge)")
    block = 2 ** (adressbits - decoder_bits)
    return [(k, k * block, (k + 1) * block - 1) for k in range(2 ** decoder_bits)], block


# =============================================================================
# AUSGANGSTYPEN
# =============================================================================
def open_drain_pullup(u_b, c_bus, u_ol_max=0.4, i_ol=3e-3, t_r_max=None, r=None):
    """
    Open-Drain-Leitung mit Pull-up (I²C, Interrupt-Leitungen, Wired-AND):
      R_min = (U_B − U_OL,max) / I_OL        (sonst kommt der Ausgang nicht tief genug)
      t_r   = 0.847 · R · C_bus              (Anstieg 30 % -> 70 % von U_B, wie in der I²C-Spezifikation)
      R_max = t_r,max / (0.847 · C_bus)
    I²C: Standard-Mode t_r ≤ 1000 ns, Fast-Mode ≤ 300 ns, I_OL = 3 mA, U_OL ≤ 0.4 V.
    """
    if u_b <= u_ol_max:
        raise ValueError("U_B muss grösser als U_OL sein")
    if c_bus <= 0 or i_ol <= 0:
        raise ValueError("C_Bus und I_OL müssen grösser als 0 sein")
    e = {"r_min": (u_b - u_ol_max) / i_ol}
    if t_r_max is not None:
        if t_r_max <= 0:
            raise ValueError("t_r,max muss grösser als 0 sein")
        e["r_max"] = t_r_max / (T_R_FAKTOR * c_bus)
        e["moeglich"] = e["r_max"] >= e["r_min"]
    if r is not None:
        e["t_r"] = T_R_FAKTOR * r * c_bus
        e["t_10_90"] = math.log(9) * r * c_bus
        e["i_low"] = (u_b - u_ol_max) / r
    return e


def buskonflikt(u_b, r_on_high=R_ON_HC, r_on_low=R_ON_HC):
    """Zwei Push-Pull-Ausgänge, einer HIGH, einer LOW: Strom fliesst von U_B über beide Transistoren nach GND."""
    i = u_b / (r_on_high + r_on_low)
    u_mitte = u_b * r_on_low / (r_on_high + r_on_low)
    return {"i": i, "u_leitung": u_mitte, "p": u_b * i}
