# =============================================================================
# schaltungen/filter_mathe.py
# -----------------------------------------------------------------------------
# REINE RECHENFUNKTIONEN für Filter 2. ORDNUNG - KEIN tkinter. Einzeln testbar, z.B.:
#
#   python -c "from schaltungen.filter_mathe import *; print(sallen_key_auslegen('Tiefpass', 1e3, 0.707, r=10e3))"
#
# Jedes Filter 2. Ordnung hat dieselbe Form (x = f / f0, Güte Q):
#   Nenner  N = 1 − x² + j · x / Q
#   Tiefpass  H = 1 / N          Hochpass  H = −x² / N
#   Bandpass  H = (j · x / Q) / N    Bandsperre  H = (1 − x²) / N
#
#   frequenzgang()        |H|, dB und Phase bei f
#   bode_kurve()          Betragsgang in dB über ±2 Dekaden um f0 (für das Diagramm)
#   kennwerte()           Überhöhung, −3-dB-Frequenz(en), Bandbreite, Charakter (Bessel/Butterworth …)
#   sprungantwort()       Antwort auf einen Spannungssprung (zeigt das Überschwingen bei hohem Q)
#   lc_tiefpass()         L in Reihe, C parallel zur Last R_L:  f0 = 1 / (2π√(LC)),  Q = R_L · √(C / L)
#   rlc_reihe()           Reihenschwingkreis, Ausgang an R (Bandpass) oder an L+C (Bandsperre): Q = √(L/C) / R
#   sallen_key()          f0 und Q aus R1, R2, C1, C2 (Einsverstärker)
#   sallen_key_auslegen() Bauteile für gewünschtes f0 und Q (gleiche R bzw. gleiche C), mit Normwerten
#
# WER RUFT DAS AUF?  schaltungen/grafiken_filter.py, schaltungen/rechner.py
# =============================================================================

import cmath
import math

from bauteile.rechner import normreihen                                # -> bauteile/rechner/normreihen.py

ARTEN = ["Tiefpass", "Hochpass", "Bandpass", "Bandsperre"]
# Güte Q der bekannten Filtercharakteristiken (2. Ordnung)
CHARAKTERISTIKEN = {"kritisch gedämpft (Q = 0.5)": 0.5, "Bessel (Q = 0.577)": 1 / math.sqrt(3),
                    "Butterworth (Q = 0.707)": 1 / math.sqrt(2), "Tschebyscheff 1 dB (Q = 0.956)": 0.9565}


def _positiv(**werte):
    for name, wert in werte.items():
        if wert is None or wert <= 0:
            raise ValueError(f"{name} muss grösser als 0 sein")


def _h(art, x, q):
    if art not in ARTEN:
        raise ValueError(f"Unbekannte Filterart: {art}")
    nenner = complex(1 - x * x, x / q)
    zaehler = {"Tiefpass": 1, "Hochpass": -x * x, "Bandpass": complex(0, x / q), "Bandsperre": 1 - x * x}[art]
    return zaehler / nenner


def frequenzgang(art, f0, q, f):
    """|H|, Dämpfung in dB (−∞ wird auf −200 dB begrenzt) und Phase in Grad bei der Frequenz f."""
    _positiv(f0=f0, Q=q, f=f)
    h = _h(art, f / f0, q)
    betrag = abs(h)
    return {"betrag": betrag, "db": 20 * math.log10(betrag) if betrag > 1e-10 else -200.0,
            "phase": math.degrees(cmath.phase(h)) if betrag > 1e-12 else 0.0}


def bode_kurve(art, q, dekaden=2, punkte=161):
    """Betragsgang in dB: x-Achse 0 … 1 = f0 / 10^dekaden … f0 · 10^dekaden (logarithmisch, Mitte = f0)."""
    kurve = []
    for k in range(punkte):
        t = k / (punkte - 1)
        betrag = abs(_h(art, 10 ** (dekaden * (2 * t - 1)), q))
        kurve.append((t, 20 * math.log10(max(betrag, 1e-10))))
    return kurve


def bode_position(f, f0, dekaden=2):
    """Lage von f auf der x-Achse von bode_kurve() (0 … 1, ausserhalb abgeschnitten)."""
    return min(max((math.log10(f / f0) / dekaden + 1) / 2, 0.0), 1.0)


def _suche(funktion, a, b):
    """Nullstelle von funktion zwischen a und b (Intervallhalbierung im log. Massstab)."""
    fa = funktion(a)
    for _ in range(100):
        m = math.sqrt(a * b)
        fm = funktion(m)
        if (fm > 0) == (fa > 0):
            a, fa = m, fm
        else:
            b = m
    return math.sqrt(a * b)


def kennwerte(art, f0, q):
    """
    Tiefpass/Hochpass: Überhöhung (nur bei Q > 0.707) bei x = √(1 − 1 / (2Q²)), |H|max = Q / √(1 − 1/(4Q²)),
                       −3-dB-Grenzfrequenz (bei Butterworth genau f0).
    Bandpass/Bandsperre: Bandbreite B = f0 / Q, untere und obere −3-dB-Frequenz.
    """
    _positiv(f0=f0, Q=q)
    e = {"f0": f0, "q": q, "zeta": 1 / (2 * q)}
    grenze = 1 / math.sqrt(2)
    if art in ("Tiefpass", "Hochpass"):
        if q > grenze + 1e-9:
            x_max = math.sqrt(1 - 1 / (2 * q * q))
            e["ueberhoehung"] = q / math.sqrt(1 - 1 / (4 * q * q))
            e["f_max"] = f0 * x_max if art == "Tiefpass" else f0 / x_max
        else:
            e["ueberhoehung"], e["f_max"] = 1.0, None
        if art == "Tiefpass":
            e["f_3db"] = f0 * _suche(lambda x: abs(_h(art, x, q)) - grenze, 1e-3 if q < 50 else 1.0001, 1e3)
        else:
            e["f_3db"] = f0 * _suche(lambda x: abs(_h(art, x, q)) - grenze, 1e3, 1e-3 if q < 50 else 0.9999)
    else:
        e["bandbreite"] = f0 / q
        # |x − 1/x| = 1/Q  ->  x = (√(1 + 4Q²) ∓ 1) / (2Q)
        wurzel = math.sqrt(1 + 4 * q * q)
        e["f_unten"], e["f_oben"] = f0 * (wurzel - 1) / (2 * q), f0 * (wurzel + 1) / (2 * q)
    e["charakter"] = charakter(q)
    return e


def charakter(q):
    """Einordnung der Güte in Worten."""
    if q < 0.5 - 1e-3:
        return "überdämpft (träge, kein Überschwingen)"
    if q < 0.5 + 1e-3:
        return "kritisch gedämpft (schnellstes Einschwingen ohne Überschwingen)"
    if q < 0.577 + 0.01:
        return "Bessel-ähnlich (konstante Laufzeit, kaum Überschwingen)"
    if q < 0.707 + 0.01:
        return "Butterworth-ähnlich (maximal flacher Durchlass)"
    if q < 1.5:
        return "Tschebyscheff-ähnlich (steiler, mit Überhöhung)"
    return "stark resonant (deutliche Überhöhung, schwingt lange nach)"


def _expm2(a):
    """e^A für eine 2×2-Matrix (Taylorreihe mit Skalieren und Quadrieren) - ohne numpy."""
    norm = max(abs(a[0][0]) + abs(a[0][1]), abs(a[1][0]) + abs(a[1][1]))
    s = max(0, math.ceil(math.log2(norm / 0.5))) if norm > 0.5 else 0
    m = [[x / 2 ** s for x in zeile] for zeile in a]

    def mal(x, y):
        return [[x[0][0] * y[0][0] + x[0][1] * y[1][0], x[0][0] * y[0][1] + x[0][1] * y[1][1]],
                [x[1][0] * y[0][0] + x[1][1] * y[1][0], x[1][0] * y[0][1] + x[1][1] * y[1][1]]]
    ergebnis, term = [[1.0, 0.0], [0.0, 1.0]], [[1.0, 0.0], [0.0, 1.0]]
    for k in range(1, 16):
        term = [[x / k for x in zeile] for zeile in mal(term, m)]
        ergebnis = [[ergebnis[i][j] + term[i][j] for j in range(2)] for i in range(2)]
    for _ in range(s):
        ergebnis = mal(ergebnis, ergebnis)
    return ergebnis


def sprungantwort(art, f0, q, punkte=480):
    """
    Antwort auf einen Sprung 0 → 1 bei t = 0.
      y'' + (ω0 / Q) · y' + ω0² · y = Anregung je nach Filterart
    Gelöst EXAKT mit der Übergangsmatrix e^(A·Δt) - stabil auch bei sehr kleinem oder grossem Q.
    Die Dauer richtet sich nach dem langsamsten Vorgang (Abklingen mit ω0 / (2Q) bzw. der langsamen Polstelle).
    Rückgabe: Kurve [(t 0 … 1, y)], Dauer in s, Überschwingen in % (nur Tiefpass), Einschwingzeit (±2 %) in s
    """
    _positiv(f0=f0, Q=q)
    if art not in ARTEN:
        raise ValueError(f"Unbekannte Filterart: {art}")
    # Zustandsform (ω0 = 1): x1' = x2, x2' = −x1 − x2/Q + u, y = c1·x1 + c2·x2 + d·u, stationär x = (1, 0)
    b2 = {"Tiefpass": 0.0, "Hochpass": 1.0, "Bandpass": 0.0, "Bandsperre": 1.0}[art]
    b1 = 1 / q if art == "Bandpass" else 0.0
    b0 = 1.0 if art in ("Tiefpass", "Bandsperre") else 0.0
    c1, c2, d = b0 - b2, b1 - b2 / q, b2
    if q >= 0.5:
        langsam = 1 / (2 * q)                                  # Abklingkonstante der Hüllkurve
    else:
        langsam = (1 / q - math.sqrt(1 / (q * q) - 4)) / 2     # langsame (reelle) Polstelle
    # höchstens 30 Schwingungen zeigen (sonst sieht man bei sehr hohem Q nur noch eine Fläche)
    dauer_norm = max(4 * math.pi, 5 / langsam) if q < 0.5 else min(max(4 * math.pi, 5 / langsam), 60 * math.pi)
    unter = 4
    dt = dauer_norm / (punkte * unter)
    phi = _expm2([[0.0, dt], [-dt, -dt / q]])
    x1 = x2 = 0.0
    kurve, werte = [], []
    for k in range(punkte * unter + 1):
        y = c1 * x1 + c2 * x2 + d
        werte.append(y)
        if k % unter == 0:
            kurve.append((k / (punkte * unter), y))
        a1, a2 = x1 - 1.0, x2                                  # Abweichung vom Endzustand (1, 0)
        x1 = 1.0 + phi[0][0] * a1 + phi[0][1] * a2
        x2 = phi[1][0] * a1 + phi[1][1] * a2
    omega0 = 2 * math.pi * f0
    ueber = max(0.0, (max(werte) - 1) * 100) if art == "Tiefpass" else None
    t_ein = None
    if art in ("Tiefpass", "Bandsperre"):
        letzte = max((k for k, y in enumerate(werte) if abs(y - 1) > 0.02), default=0)
        if letzte < len(werte) - 1:
            t_ein = (letzte + 1) * dt / omega0
    return {"kurve": kurve, "dauer": dauer_norm / omega0, "ueberschwingen": ueber, "einschwingzeit": t_ein,
            "endwert": werte[-1]}


# =============================================================================
# PASSIVE FILTER
# =============================================================================
def lc_tiefpass(l, c, r_last):
    """
    L in Reihe, C parallel zur Last:  H = 1 / (1 + s·L/R_L + s²·L·C)
      f0 = 1 / (2π · √(L · C))      Q = R_L · √(C / L)  = R_L / Z0      Kennwiderstand Z0 = √(L / C)
    Ohne Last (R_L → ∞) wird Q unendlich: Resonanzüberhöhung.
    """
    _positiv(L=l, C=c, R_L=r_last)
    z0 = math.sqrt(l / c)
    return {"f0": 1 / (2 * math.pi * math.sqrt(l * c)), "q": r_last / z0, "z0": z0}


def rlc_reihe(r, l, c):
    """
    Reihenschwingkreis R-L-C:  f0 = 1 / (2π√(LC)),  Q = Z0 / R = √(L/C) / R,  Bandbreite B = f0 / Q.
    Ausgang an R -> Bandpass, Ausgang an L+C -> Bandsperre (Kerbfilter).
    """
    _positiv(R=r, L=l, C=c)
    z0 = math.sqrt(l / c)
    f0 = 1 / (2 * math.pi * math.sqrt(l * c))
    return {"f0": f0, "q": z0 / r, "z0": z0, "bandbreite": f0 * r / z0}


# =============================================================================
# AKTIV: SALLEN-KEY (OPV als Spannungsfolger, Verstärkung 1)
# =============================================================================
def sallen_key(art, r1, r2, c1, c2):
    """
    Tiefpass: Ue – R1 – R2 – (+)OPV, C1 vom Mittelpunkt zum Ausgang, C2 vom (+)-Eingang nach GND
              f0 = 1 / (2π√(R1R2C1C2))     Q = √(R1R2C1C2) / (C2 · (R1 + R2))
    Hochpass: Ue – C1 – C2 – (+)OPV, R1 vom Mittelpunkt zum Ausgang, R2 vom (+)-Eingang nach GND
              f0 = 1 / (2π√(R1R2C1C2))     Q = √(R1R2C1C2) / (R1 · (C1 + C2))
    """
    _positiv(R1=r1, R2=r2, C1=c1, C2=c2)
    produkt = math.sqrt(r1 * r2 * c1 * c2)
    if art == "Tiefpass":
        q = produkt / (c2 * (r1 + r2))
    elif art == "Hochpass":
        q = produkt / (r1 * (c1 + c2))
    else:
        raise ValueError("Sallen-Key hier nur als Tief- oder Hochpass")
    return {"f0": 1 / (2 * math.pi * produkt), "q": q}


def sallen_key_auslegen(art, f0, q, r=None, c=None, reihe="E24", reihe_c="E12"):
    """
    Tiefpass mit gleichen R:  C1 = 2Q / (ω0 · R),  C2 = 1 / (2Q · ω0 · R)      (C1 / C2 = 4Q²)
    Hochpass mit gleichen C:  R1 = 1 / (2Q · ω0 · C),  R2 = 2Q / (ω0 · C)      (R2 / R1 = 4Q²)
    Danach auf Normwerte runden (R: E24, C: E12) und f0, Q mit den Normwerten nachrechnen.
    """
    _positiv(f0=f0, Q=q)
    w0 = 2 * math.pi * f0
    if art == "Tiefpass":
        _positiv(R=r)
        ideal = {"r1": r, "r2": r, "c1": 2 * q / (w0 * r), "c2": 1 / (2 * q * w0 * r)}
    elif art == "Hochpass":
        _positiv(C=c)
        ideal = {"r1": 1 / (2 * q * w0 * c), "r2": 2 * q / (w0 * c), "c1": c, "c2": c}
    else:
        raise ValueError("Sallen-Key hier nur als Tief- oder Hochpass")
    norm = {k: normreihen.naechste_werte(v, reihe if k.startswith("r") else reihe_c)[2] for k, v in ideal.items()}
    ist = sallen_key(art, norm["r1"], norm["r2"], norm["c1"], norm["c2"])
    return {"ideal": ideal, "norm": norm, "f0_ist": ist["f0"], "q_ist": ist["q"]}
