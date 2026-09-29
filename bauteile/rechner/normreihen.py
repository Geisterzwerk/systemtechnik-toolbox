# =============================================================================
# bauteile/rechner/normreihen.py
# -----------------------------------------------------------------------------
# E-REIHEN (Normwerte nach IEC 60063) und Hilfsfunktionen.
# Benutzt von: Widerstands-, Kondensator- und Spulen-Rechnern.
#
#   naechste_werte(4600, "E24")  -> (4300.0, 4700.0, 4700.0)   (unten, oben, nächster)
# =============================================================================

import math

# Werte pro Dekade (zwischen 1 und 10)
E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
E12 = E24[::2]          # 1.0 1.2 1.5 1.8 2.2 2.7 3.3 3.9 4.7 5.6 6.8 8.2
E6 = E24[::4]           # 1.0 1.5 2.2 3.3 4.7 6.8

E96 = [v / 100 for v in (
    100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143,
    147, 150, 154, 158, 162, 165, 169, 174, 178, 182, 187, 191, 196, 200, 205, 210,
    215, 221, 226, 232, 237, 243, 249, 255, 261, 267, 274, 280, 287, 294, 301, 309,
    316, 324, 332, 340, 348, 357, 365, 374, 383, 392, 402, 412, 422, 432, 442, 453,
    464, 475, 487, 499, 511, 523, 536, 549, 562, 576, 590, 604, 619, 634, 649, 665,
    681, 698, 715, 732, 750, 768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976)]
E48 = E96[::2]

REIHEN = {"E6": E6, "E12": E12, "E24": E24, "E48": E48, "E96": E96}
TOLERANZ = {"E6": "±20 %", "E12": "±10 %", "E24": "±5 %", "E48": "±2 %", "E96": "±1 %"}


def naechste_werte(wert, reihe="E24"):
    """Gibt (nächst kleinerer, nächst grösserer, nächster) Normwert zurück."""
    if wert <= 0:
        raise ValueError("Wert muss grösser als 0 sein")
    werte = REIHEN[reihe]
    dekade = math.floor(math.log10(wert))
    kandidaten = sorted(round(v * 10 ** d, 12) for d in (dekade - 1, dekade, dekade + 1) for v in werte)
    unten = max(k for k in kandidaten if k <= wert * (1 + 1e-9))
    oben = min(k for k in kandidaten if k >= wert * (1 - 1e-9))
    # "nächster" im logarithmischen Sinn (so sind die Reihen aufgebaut)
    naechster = unten if abs(math.log(wert / unten)) <= abs(math.log(oben / wert)) else oben
    return unten, oben, naechster


def ist_normwert(wert, reihe="E24"):
    u, o, _ = naechste_werte(wert, reihe)
    return math.isclose(u, wert, rel_tol=1e-6) or math.isclose(o, wert, rel_tol=1e-6)
