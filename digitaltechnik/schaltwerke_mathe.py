# =============================================================================
# digitaltechnik/schaltwerke_mathe.py
# -----------------------------------------------------------------------------
# REINE FUNKTIONEN für Schaltwerke (mit Speicher) - KEIN tkinter. Einzeln testbar, z.B.:
#
#   python -c "from digitaltechnik.schaltwerke_mathe import *; print(zaehler_entwurf([0, 1, 2, 3, 4], 'D'))"
#
#   naechster_zustand()   Flipflop: Q nach dem Takt (RS, D, JK, T) bzw. Latch bei aktivem Takt
#   KENN_GLEICHUNG        charakteristische Gleichungen
#   zaehler_folge()       Zustände eines Zählers (auf/ab, modulo m)
#   ripple_uebergang()    Zwischenzustände eines asynchronen Zählers beim Weiterschalten
#   schieberegister()     Zustände eines Schieberegisters (seriell rein, Ring, Johnson)
#   zaehler_entwurf()     synchroner Zähler mit D- oder JK-Flipflops: minimierte Ansteuergleichungen
#   fmax_synchron()       höchste Taktfrequenz: 1 / (t_pd + t_Logik + t_setup + t_skew)
#   frequenzteiler()      wie viele Flipflops für einen Teiler, welche Ausgangsfrequenz
#
# WER RUFT DAS AUF?  digitaltechnik/grafiken_schaltwerke.py, digitaltechnik/rechner.py
# =============================================================================

import math

from digitaltechnik import logik_mathe as lm                           # -> digitaltechnik/logik_mathe.py

FLIPFLOP_ARTEN = ["RS-Latch", "D-Latch", "D-Flipflop", "JK-Flipflop", "T-Flipflop"]
KENN_GLEICHUNG = {"RS-Latch": "Q⁺ = S + ¬R·Q   (S·R = 0 verboten)", "D-Latch": "Q = D, solange C = 1",
                  "D-Flipflop": "Q⁺ = D", "JK-Flipflop": "Q⁺ = J·¬Q + ¬K·Q", "T-Flipflop": "Q⁺ = T ⊕ Q"}
# Ansteuertabelle JK: (Q, Q⁺) -> (J, K)   X = egal
JK_ANSTEUERUNG = {(0, 0): ("0", "X"), (0, 1): ("1", "X"), (1, 0): ("X", "1"), (1, 1): ("X", "0")}


# =============================================================================
# FLIPFLOPS
# =============================================================================
def naechster_zustand(art, q, e):
    """
    Neuer Zustand Q nach dem Ereignis.
      RS-Latch:    sofort (kein Takt), e = {S, R}; S = R = 1 ist verboten (beide Ausgänge 0, danach unbestimmt)
      D-Latch:     e = {D, C}: transparent, solange C = 1, sonst speichern
      D/JK/T-FF:   wird nur bei der steigenden Taktflanke aufgerufen
    Rückgabe: (Q, Hinweis)
    """
    if art == "RS-Latch":
        s, r = e["S"], e["R"]
        if s and r:
            return q, "verboten: S = R = 1"
        return (1 if s else 0 if r else q), ("setzen" if s else "rücksetzen" if r else "speichern")
    if art == "D-Latch":
        return (e["D"], "transparent: Q folgt D") if e["C"] else (q, "speichern (C = 0)")
    if art == "D-Flipflop":
        return e["D"], f"D = {e['D']} übernommen"
    if art == "JK-Flipflop":
        j, k = e["J"], e["K"]
        if j and k:
            return 1 - q, "toggeln (J = K = 1)"
        if j:
            return 1, "setzen"
        if k:
            return 0, "rücksetzen"
        return q, "speichern"
    if art == "T-Flipflop":
        return (1 - q, "toggeln") if e["T"] else (q, "speichern")
    raise ValueError(f"Unbekanntes Flipflop: {art}")


def flipflop_tabelle(art):
    """Wahrheitstabelle als Liste (Eingänge-Text, Q⁺-Text)."""
    if art == "RS-Latch":
        return [("S=0 R=0", "Q (speichern)"), ("S=0 R=1", "0"), ("S=1 R=0", "1"), ("S=1 R=1", "verboten")]
    if art == "D-Latch":
        return [("C=0", "Q (speichern)"), ("C=1 D=0", "0"), ("C=1 D=1", "1")]
    if art == "D-Flipflop":
        return [("↑ D=0", "0"), ("↑ D=1", "1"), ("kein ↑", "Q")]
    if art == "JK-Flipflop":
        return [("↑ J=0 K=0", "Q"), ("↑ J=0 K=1", "0"), ("↑ J=1 K=0", "1"), ("↑ J=1 K=1", "¬Q")]
    if art == "T-Flipflop":
        return [("↑ T=0", "Q"), ("↑ T=1", "¬Q")]
    raise ValueError(f"Unbekanntes Flipflop: {art}")


# =============================================================================
# ZÄHLER
# =============================================================================
def zaehler_folge(bits, modulo=None, abwaerts=False, start=0, schritte=None):
    """Zustände eines Zählers mit n Flipflops, optional modulo m (Rücksetzen bei m)."""
    if not 1 <= bits <= 16:
        raise ValueError("1 bis 16 Bit")
    m = 2 ** bits if modulo is None else modulo
    if not 2 <= m <= 2 ** bits:
        raise ValueError(f"Modulo zwischen 2 und {2 ** bits} (mit {bits} Flipflops)")
    schritte = m if schritte is None else schritte
    folge, z = [], start % m
    for _ in range(schritte + 1):
        folge.append(z)
        z = (z - 1) % m if abwaerts else (z + 1) % m
    return folge


def ripple_uebergang(alt, bits, modulo=None):
    """
    Asynchroner Aufwärtszähler (jedes Flipflop toggelt bei der fallenden Flanke des vorigen):
    beim Weiterschalten kippen die Bits NACHEINANDER von Q0 aufwärts -> kurze falsche Zwischenzustände.
    Modulo m: erreicht der Zähler m, setzt eine Logik ihn zurück (kurzer Zustand m sichtbar = Glitch).
    Rückgabe: Liste aller Zustände von alt bis zum neuen Zustand (inkl. Zwischenzustände).
    """
    zustaende, z = [alt], alt
    for i in range(bits):
        z ^= 1 << i                                    # Bit i kippt
        zustaende.append(z)
        if (z >> i) & 1:                               # 0 -> 1: keine fallende Flanke, Kette hört auf
            break
    neu = z & (2 ** bits - 1)
    if zustaende[-1] != neu:
        zustaende[-1] = neu
    if modulo is not None and neu == modulo:
        zustaende.append(0)                            # asynchrones Rücksetzen
    return zustaende


def schieberegister(bits, eingaben, art="seriell", start=0):
    """
    Zustände (Bit 0 = erste Stufe) nach jedem Takt:
      seriell:  Q0 <- Eingang, Qi <- Q(i−1)          (SISO/SIPO)
      Ring:     Q0 <- Q(n−1)   (eine 1 wandert im Kreis, n Zustände)
      Johnson:  Q0 <- ¬Q(n−1)  (2n Zustände)
    eingaben: Bits je Takt (nur für 'seriell'), bei Ring/Johnson die Anzahl Takte als len(eingaben)
    """
    if not 1 <= bits <= 16:
        raise ValueError("1 bis 16 Bit")
    voll = 2 ** bits - 1
    z, folge = start & voll, [start & voll]
    for e in eingaben:
        msb = (z >> (bits - 1)) & 1
        rein = e if art == "seriell" else (msb if art == "Ring" else 1 - msb)
        z = ((z << 1) | rein) & voll
        folge.append(z)
    return folge


# =============================================================================
# SYNCHRONEN ZÄHLER ENTWERFEN
# =============================================================================
def zaehler_entwurf(folge, ff="D", bits=None):
    """
    Synchroner Zähler für eine beliebige Zustandsfolge (z.B. 0, 1, 2, … 9 oder Gray-Folge):
      1. Zustandsfolgetabelle  Q -> Q⁺ (letzter Zustand -> erster)
      2. nicht benutzte Zustände = don't care
      3. D-Flipflop: D_i = Q⁺_i;  JK: aus der Ansteuertabelle (0→0: J=0 K=X, 0→1: J=1 K=X, 1→0: J=X K=1, 1→1: J=X K=0)
      4. jede Ansteuerfunktion minimieren (Quine-McCluskey)
    Variablen: Q(n−1) … Q0 (Q(n−1) ist das höchstwertige Bit).
    """
    if len(folge) < 2:
        raise ValueError("Mindestens zwei Zustände angeben")
    if len(set(folge)) != len(folge):
        raise ValueError("Jeder Zustand darf nur einmal vorkommen")
    if min(folge) < 0:
        raise ValueError("Zustände ≥ 0")
    n = bits or max(1, max(folge).bit_length())
    if max(folge) >= 2 ** n:
        raise ValueError(f"Zustand {max(folge)} passt nicht in {n} Bit")
    if n > 6:
        raise ValueError("Höchstens 6 Flipflops (64 Zustände)")
    if ff not in ("D", "JK"):
        raise ValueError("Flipflop-Typ D oder JK")
    namen = [f"Q{i}" for i in range(n - 1, -1, -1)]
    nachfolger = {z: folge[(k + 1) % len(folge)] for k, z in enumerate(folge)}
    frei = [z for z in range(2 ** n) if z not in nachfolger]
    gleichungen = []
    for i in range(n - 1, -1, -1):
        if ff == "D":
            einsen = [z for z, z_neu in nachfolger.items() if (z_neu >> i) & 1]
            gleichungen.append((f"D{i}", lm.minimal_formen(einsen, namen, frei)["min_dnf"]))
        else:
            j_eins, j_x, k_eins, k_x = [], list(frei), [], list(frei)
            for z, z_neu in nachfolger.items():
                j, k = JK_ANSTEUERUNG[((z >> i) & 1, (z_neu >> i) & 1)]
                (j_eins if j == "1" else j_x if j == "X" else []).append(z)
                (k_eins if k == "1" else k_x if k == "X" else []).append(z)
            gleichungen.append((f"J{i}", lm.minimal_formen(j_eins, namen, j_x)["min_dnf"]))
            gleichungen.append((f"K{i}", lm.minimal_formen(k_eins, namen, k_x)["min_dnf"]))
    tabelle = [(z, nachfolger[z]) for z in folge]
    # Fangen sich unbenutzte Zustände wieder? (D-Flipflop: Gleichungen auf die freien Zustände anwenden)
    return {"bits": n, "namen": namen, "tabelle": tabelle, "frei": frei, "gleichungen": gleichungen}


def freie_zustaende_pruefen(entwurf):
    """Wohin laufen die unbenutzten Zustände mit den minimierten Gleichungen? (Selbststart prüfen)"""
    n, namen = entwurf["bits"], entwurf["namen"]
    baeume = {name: lm.parsen(text) if text not in ("0", "1") else ("const", int(text))
              for name, text in entwurf["gleichungen"]}
    benutzt = {z for z, _ in entwurf["tabelle"]}

    def schritt(z):
        belegung = {f"Q{i}": (z >> i) & 1 for i in range(n)}
        neu = 0
        for i in range(n):
            q = (z >> i) & 1
            if f"D{i}" in baeume:
                bit = lm.auswerten(baeume[f"D{i}"], belegung)
            else:
                j, k = lm.auswerten(baeume[f"J{i}"], belegung), lm.auswerten(baeume[f"K{i}"], belegung)
                bit = (j & (1 - q)) | ((1 - k) & q)
            neu |= bit << i
        return neu

    ergebnis = []
    for z in entwurf["frei"]:
        weg, aktuell = [z], z
        for _ in range(2 ** n):
            aktuell = schritt(aktuell)
            weg.append(aktuell)
            if aktuell in benutzt or aktuell in weg[:-1]:
                break
        ergebnis.append((z, weg, aktuell in benutzt))
    return ergebnis


# =============================================================================
# TIMING
# =============================================================================
def fmax_synchron(t_pd, t_setup, t_logik=0.0, t_skew=0.0, t_hold=None):
    """
    Synchrones Schaltwerk: zwischen zwei Taktflanken muss das Signal vom Flipflop-Ausgang durch die Logik
    zum nächsten Flipflop-Eingang laufen und dort t_setup vor der Flanke stabil sein:
      T_min = t_pd + t_Logik + t_setup + t_skew      f_max = 1 / T_min
    Hold-Prüfung: t_pd(min) + t_Logik(min) ≥ t_hold + t_skew  (hier vereinfacht mit denselben Werten)
    """
    for name, wert in (("t_pd", t_pd), ("t_setup", t_setup), ("t_Logik", t_logik), ("t_skew", t_skew)):
        if wert < 0:
            raise ValueError(f"{name} darf nicht negativ sein")
    t = t_pd + t_logik + t_setup + t_skew
    if t <= 0:
        raise ValueError("Mindestens eine Zeit muss grösser als 0 sein")
    e = {"t_min": t, "f_max": 1 / t}
    if t_hold is not None:
        e["hold_ok"] = t_pd + t_logik >= t_hold + t_skew
        e["hold_reserve"] = t_pd + t_logik - t_hold - t_skew
    return e


def frequenzteiler(f_ein, teiler):
    """Teiler durch m: ⌈log2 m⌉ Flipflops; Zweierpotenz -> symmetrisch (50 %), sonst Tastgrad ≠ 50 % möglich."""
    if f_ein <= 0:
        raise ValueError("Eingangsfrequenz muss grösser als 0 sein")
    if teiler < 2 or teiler != int(teiler):
        raise ValueError("Teiler als ganze Zahl ≥ 2")
    teiler = int(teiler)
    ff = math.ceil(math.log2(teiler))
    zweierpotenz = 2 ** ff == teiler
    return {"f_aus": f_ein / teiler, "ff": ff, "zweierpotenz": zweierpotenz,
            "periode": teiler / f_ein, "zwischen": [f_ein / 2 ** k for k in range(1, ff + 1)] if zweierpotenz else []}
