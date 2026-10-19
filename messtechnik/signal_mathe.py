# =============================================================================
# messtechnik/signal_mathe.py
# -----------------------------------------------------------------------------
# SIGNALFORMEN UND FOURIER-SYNTHESE - reine Rechnung, KEIN tkinter.
#
# Jedes periodische Signal lässt sich aus Sinusschwingungen zusammensetzen:
# einer Grundschwingung (Frequenz f) und Oberschwingungen (2f, 3f, 4f …).
#
#   FORMEN                     Rechteck, Dreieck, Sägezahn (steigend) - je Scheitelwert 1
#   glieder(form, n)           die ersten n Sinus-Glieder: [(ordnung k, amplitude a_k), ...]
#                              -> Signal = Σ a_k · sin(k · ω · t)
#   summe(form, n, x)          Wert der Summe bei x = ω·t (im Bogenmass)
#   ideal(form, x)             die ideale Kurvenform bei x
#   ueberschwinger(n)          Spitze der Rechteck-Summe mit n Gliedern (Gibbs-Phänomen)
#
# Formeln (Scheitelwert h, ω = 2π · f), nachgerechnet in pruefung/rechner_faelle.py:
#   Rechteck   (4h/π)  · [sin(ωt) + sin(3ωt)/3 + sin(5ωt)/5 + …]        nur ungerade k, Amplitude ~ 1/k
#   Dreieck    (8h/π²) · [sin(ωt) − sin(3ωt)/9 + sin(5ωt)/25 − …]       nur ungerade k, Amplitude ~ 1/k²
#   Sägezahn   (2h/π)  · [sin(ωt) − sin(2ωt)/2 + sin(3ωt)/3 − …]        alle k, Amplitude ~ 1/k
# Quelle: Fourierreihe (z.B. Wikipedia „Fourierreihe“, Abschnitt Beispiele); Phase so gewählt,
# dass alle drei bei t = 0 mit 0 beginnen und ansteigen.
#
# WER RUFT DAS AUF?  messtechnik/grafiken_signale.py (FourierSynthese), pruefung/rechner_faelle.py
# =============================================================================

import math

FORMEN = ["Rechteck", "Dreieck", "Sägezahn"]


def glieder(form, n):
    """Die ersten n Sinus-Glieder (Ordnung k, Amplitude bei Scheitelwert 1). Ordnung 1 = Grundschwingung."""
    if form not in FORMEN:
        raise ValueError(f"Unbekannte Signalform: {form}")
    n = max(1, int(n))
    if form == "Rechteck":
        return [(2 * i - 1, 4 / math.pi / (2 * i - 1)) for i in range(1, n + 1)]
    if form == "Dreieck":
        return [(2 * i - 1, (-1) ** (i - 1) * 8 / math.pi ** 2 / (2 * i - 1) ** 2) for i in range(1, n + 1)]
    return [(k, (-1) ** (k + 1) * 2 / math.pi / k) for k in range(1, n + 1)]          # Sägezahn


def summe(form, n, x):
    """Summe der ersten n Glieder bei x = ω·t (Bogenmass), Scheitelwert der Idealform = 1."""
    return sum(a * math.sin(k * x) for k, a in glieder(form, n))


def ideal(form, x):
    """Ideale Kurvenform bei x = ω·t, Scheitelwert 1, Periode 2π, Beginn bei 0 (steigend)."""
    x = (x + math.pi) % (2 * math.pi) - math.pi            # auf -π … π
    if form == "Rechteck":
        return 1.0 if x > 0 else -1.0 if x < 0 else 0.0
    if form == "Dreieck":
        if abs(x) <= math.pi / 2:
            return 2 * x / math.pi
        return 2 * (math.pi - x) / math.pi if x > 0 else 2 * (-math.pi - x) / math.pi
    if form == "Sägezahn":
        return x / math.pi
    raise ValueError(f"Unbekannte Signalform: {form}")


def ueberschwinger(n, schritte=4000):
    """Höchster Wert der Rechteck-Summe mit n Gliedern zwischen 0 und π (Scheitelwert ideal = 1).
    Gibbs-Phänomen: Die Spitze bleibt auch bei sehr vielen Gliedern bei etwa 1.18 -
    das sind rund 9 % der Sprunghöhe (Sprung von −1 auf +1 = 2)."""
    return max(summe("Rechteck", n, math.pi * i / schritte) for i in range(1, schritte))
