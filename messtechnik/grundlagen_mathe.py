# =============================================================================
# messtechnik/grundlagen_mathe.py
# -----------------------------------------------------------------------------
# MESSKETTE UND MESSREIHE - reine Rechnung, KEIN tkinter.
#
#   kette(t, linearisiert)     Beispiel-Messkette Temperatur 0 … 250 °C (nach DIN 1319, Beispiel aus
#                              dem Wikipedia-Artikel „Messeinrichtung“):
#                                Pt100:            Temperatur 0 … 250 °C  -> Widerstand 100.0 … 194.1 Ω
#                                Messbrücke:       Widerstand             -> Spannung 0 … 60 mV
#                                Messumformer:     Spannung 0 … 60 mV     -> Strom 4 … 20 mA
#                                Anzeiger:         Strom 4 … 20 mA        -> Skala 0 … 250 °C
#                              Vereinfachung: Brücke und Messumformer sind linear im WIDERSTAND.
#                              Der Pt100 selbst ist leicht gekrümmt (quadratisch) - ohne Linearisierung
#                              zeigt die lineare Skala darum etwas zu viel an (systematische Abweichung).
#                              linearisiert=True: der Messumformer rechnet die Pt100-Kennlinie zurück.
#
#   messreihe(wahr, syst, s, n, ausreisser)
#                              n Messwerte mit systematischer Abweichung syst und Streuung s
#                              (Normalverteilung, IMMER dieselben Zufallszahlen -> Bild bleibt stabil).
#   auswerten(werte)           Mittelwert, Standardabweichung s, s/√n
#
# WER RUFT DAS AUF?  messtechnik/grafiken_signale.py (MesskettePt100, Messreihe), pruefung/rechner_faelle.py
# =============================================================================

import math
import random

from messtechnik.rechner import pt_temperatur, pt_widerstand          # -> messtechnik/rechner.py (IEC 60751)

T_MAX = 250.0                         # °C, Messbereich 0 … 250 °C
R0 = 100.0                            # Pt100
R_MAX = pt_widerstand(T_MAX, R0)      # 194.1 Ω
U_MAX = 0.060                         # V, Brückenspannung bei 250 °C
I_MIN, I_MAX = 0.004, 0.020           # A, Einheitssignal 4 … 20 mA


def kette(t, linearisiert=False):
    """Werte an jedem Glied der Kette für die Temperatur t (°C). Alle Werte in Basiseinheiten."""
    if not 0 <= t <= T_MAX:
        raise ValueError(f"Temperatur muss zwischen 0 und {T_MAX:.0f} °C liegen")
    r = pt_widerstand(t, R0)
    u = (r - R0) / (R_MAX - R0) * U_MAX                       # Messbrücke (vereinfacht linear in R)
    if linearisiert:
        anteil = pt_temperatur(R0 + u / U_MAX * (R_MAX - R0), R0) / T_MAX     # Kennlinie zurückgerechnet
    else:
        anteil = u / U_MAX
    i = I_MIN + anteil * (I_MAX - I_MIN)                       # Messumformer -> 4 … 20 mA
    anzeige = (i - I_MIN) / (I_MAX - I_MIN) * T_MAX            # Anzeiger mit linearer Skala
    return {"t": t, "r": r, "u": u, "i": i, "anzeige": anzeige, "abweichung": anzeige - t}


def messreihe(wahr, syst, s, n, ausreisser=False, saat=7):
    """n Messwerte: wahr + syst + zufällige Streuung (Standardabweichung s). Mit ausreisser=True ist
    ein Wert grob falsch (z.B. falsch abgelesen): um 8·s daneben, mindestens aber um 2 % von wahr."""
    zufall = random.Random(saat)                               # feste Saat -> jedes Mal dieselben Werte
    werte = [wahr + syst + zufall.gauss(0.0, 1.0) * s for _ in range(int(n))]
    if ausreisser and werte:
        werte[len(werte) // 3] = wahr + syst + max(8 * s, 0.02 * abs(wahr))
    return werte


def auswerten(werte):
    """{"n", "mittel", "s" (empirische Standardabweichung), "s_mittel" (s/√n)}"""
    n = len(werte)
    mittel = sum(werte) / n
    s = math.sqrt(sum((x - mittel) ** 2 for x in werte) / (n - 1)) if n > 1 else 0.0
    return {"n": n, "mittel": mittel, "s": s, "s_mittel": s / math.sqrt(n)}
