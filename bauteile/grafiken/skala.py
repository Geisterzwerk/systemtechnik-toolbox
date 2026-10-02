# =============================================================================
# bauteile/grafiken/skala.py
# -----------------------------------------------------------------------------
# SKALEN FÜR DIAGRAMME - damit in jeder Grafik die Grössen mit Einheit stehen
# und auch KLEINE Werte (mV, µA) die Kurve gut ausfüllen.
#
#   schoene_grenze(wert)        -> runder Skalenendwert ≥ |wert|, z.B. 0.0137 -> 0.015, 326 -> 400
#   wert_text(wert, typ)        -> "325 V", "−12 mA", "4.7 µs" (Einheiten-Typ wie bei fmt)
#   achse_y(c, x, y_oben, y_unten, v_min, v_max, typ, schrift, farbe, rechts=False)
#                               -> schreibt v_max, 0 (falls dazwischen) und v_min an eine senkrechte Achse
#
# WER RUFT DAS AUF?  bauteile/grafiken/schaltplan.py (diagramm), trafo_animation.py, kurven.py,
#                    halbleiter_grafiken.py, schalter_simulator.py, messtechnik/grafiken.py ...
# =============================================================================

import math

from bauteile.rechner.basis import fmt                                 # -> bauteile/rechner/basis.py

STUFEN = (1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0)     # fein genug, dass die Kurve ≥ 80 % füllt


def schoene_grenze(wert, minimum=1e-12):
    """Kleinster 'runder' Wert aus STUFEN · 10^n, der mindestens |wert| ist (nie 0)."""
    wert = abs(wert)
    if wert < minimum:
        return 1.0
    zehner = 10 ** math.floor(math.log10(wert))
    for stufe in STUFEN:
        if stufe * zehner >= wert * (1 - 1e-9):
            return float(f"{stufe * zehner:.6g}")                  # 5e-06 statt 4.9999999e-06
    return float(f"{10 * zehner:.6g}")


def wert_text(wert, typ, stellen=3):
    """Zahl mit passender Einheit (mV, µA …); Minus als echtes Minuszeichen."""
    if abs(wert) < 1e-15:
        return "0"
    text = fmt(abs(wert), typ, stellen)
    return ("−" if wert < 0 else "") + text


def achse_y(c, x, y_oben, y_unten, v_min, v_max, typ, schrift, farbe, rechts=False):
    """Beschriftet eine senkrechte Achse mit Endwerten und der Null (Text links bzw. rechts von x)."""
    anker = "w" if rechts else "e"
    dx = 4 if rechts else -4
    marken = [(v_max, y_oben), (v_min, y_unten)]
    if v_min < 0 < v_max:
        marken.append((0.0, y_unten + (y_oben - y_unten) * (0 - v_min) / (v_max - v_min)))
    for wert, y in marken:
        c.create_text(x + dx, y, text=wert_text(wert, typ), anchor=anker, fill=farbe, font=schrift)
