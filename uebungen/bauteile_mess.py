# =============================================================================
# uebungen/bauteile_mess.py
# -----------------------------------------------------------------------------
# ÜBUNGEN BAUTEILE und MESSTECHNIK (Stufen 1–4).
#   Bauteile:    Farbcode (Bild mit Ringen), SMD-Code, Normwerte, Kondensator (Q, W, Reihe, X_C), Spule (X_L),
#                Leitungswiderstand, Temperaturkoeffizient, Transformator, Diode
#   Messtechnik: relative Abweichung, Effektivwert, Oszilloskop ablesen, Multimeter-Fehlergrenze,
#                Genauigkeitsklasse, Pt100, 4…20 mA, Shunt und Vorwiderstand, Standardabweichung, AD-Wandler, DMS
#
# Gerechnet wird mit den Funktionen und Formeln der Rechner: Farbcode/SMD (bauteile/rechner/widerstand_rechner.py),
# Normreihen (normreihen.py), Pt100 nach IEC 60751 (messtechnik/rechner.py), Messreihe (grundlagen_mathe.py),
# Multimeter "± (p · |Anzeige| + n · Auflösung)", ADC "Code = abgerundet U / LSB", Messbereich
# "Rs = Ri · Iv / (I − Iv)", "Rv = U / Iv − Ri" - genau wie in den Rechnern der Messtechnik.
# Materialwerte (ρ, α) stehen IMMER in der Aufgabe.
#
# WER RUFT DAS AUF?  uebungen/aufgaben.py (lädt alle Übungs-Module)
# =============================================================================

import math

from bauteile.rechner import normreihen                                     # -> bauteile/rechner/normreihen.py
from bauteile.rechner.widerstand_rechner import (FARB_HEX, MULTI, TOLERANZ, ZIFFER, smd_entschluesseln,  # -> Farbcode/SMD
                                                 wert_zu_farben)
from messtechnik import grundlagen_mathe as gm                               # -> messtechnik/grundlagen_mathe.py
from messtechnik.rechner import pt_temperatur, pt_widerstand                 # -> messtechnik/rechner.py (IEC 60751)
from uebungen.kern import _e12, _f, art                                      # -> uebungen/kern.py
from uebungen.schemas import GESUCHT, ORANGE, SCHEMAS                        # -> uebungen/schemas.py

B, M = "Bauteile", "Messtechnik"
_R, _U, _I, _C, _L = "widerstand", "spannung", "strom", "kapazitaet", "induktivitaet"


# =============================================================================
# BAUTEILE
# =============================================================================
def _farbcode(z, ringe):
    if ringe == 4:
        wert = _e12(z, 1, 6)                                         # 10 Ω … 820 kΩ
        tol = z.choice(["Gold", "Silber"])
    else:
        wert = float(f"{z.choice(normreihen.E96) * 10 ** z.randint(1, 4):.12g}")
        tol = "Braun"
    farben, gerundet = wert_zu_farben(wert, ringe, tol)
    ziffern = 2 if ringe == 4 else 3
    zahl = "".join(str(ZIFFER[f]) for f in farben[:ziffern])
    return ("Ein Widerstand hat die Farbringe wie im Bild (von links gelesen, Toleranzring rechts). Welchen "
            "Widerstandswert hat er?",
            [("Farben", " – ".join(farben), None)], ("R", _R, "Nennwert"), gerundet,
            [f"Die ersten {ziffern} Ringe sind Ziffern: {' '.join(farben[:ziffern])} = {zahl}",
             f"Ring {ziffern + 1} ist der Multiplikator: {farben[ziffern]} = × 10^{MULTI[farben[ziffern]]}",
             f"R = {zahl} · 10^{MULTI[farben[ziffern]]} Ω = {_f(gerundet, _R)}, Toleranz {farben[-1]} = ±{TOLERANZ[farben[-1]]:g} %",
             "Merkhilfe Ziffern: Schwarz 0, Braun 1, Rot 2, Orange 3, Gelb 4, Grün 5, Blau 6, Violett 7, Grau 8, Weiss 9"])


def _farbcode_4(z):
    return _farbcode(z, 4)


def _farbcode_5(z):
    return _farbcode(z, 5)


def _smd(z):
    art_code = z.choice(["3", "3", "4", "R"])
    if art_code == "3":
        wert = _e12(z, 1, 6)
        exp = math.floor(math.log10(wert)) - 1
        code = f"{int(round(wert / 10 ** exp)):02d}{exp}"
    elif art_code == "4":                                            # 4-stellig erst ab 100 Ω (z.B. 1000 = 100 Ω)
        wert = float(f"{z.choice(normreihen.E96) * 10 ** z.randint(2, 4):.12g}")
        exp = math.floor(math.log10(wert)) - 2
        code = f"{int(round(wert / 10 ** exp)):03d}{exp}"
    else:
        code = z.choice(["4R7", "2R2", "R47", "1R0", "8R2"])
    wert = smd_entschluesseln(code)[0]                               # (Wert, Erklärung)
    return (f"Auf einem SMD-Widerstand steht der Aufdruck {code}. Welchen Wert hat er?",
            [("Code", code, None)], ("R", _R, "Widerstandswert"), wert,
            ["3 Ziffern: zwei Ziffern + Anzahl Nullen (472 = 47 · 10² = 4.7 kΩ)",
             "4 Ziffern: drei Ziffern + Anzahl Nullen (1002 = 100 · 10² = 10 kΩ)",
             "R steht für das Komma: 4R7 = 4.7 Ω, R47 = 0.47 Ω",
             f"{code} = {_f(wert, _R)}"])


def _normwert(z):
    while True:
        wert = float(f"{z.uniform(1, 9.9) * 10 ** z.randint(2, 4):.3g}")
        if not normreihen.ist_normwert(wert, "E12"):
            break
    unten, oben, _n = normreihen.naechste_werte(wert, "E12")
    return (f"Die Rechnung ergibt einen Widerstand von {_f(wert, _R)}. Welchen E12-Normwert wählst du, wenn der "
            "Widerstand MINDESTENS so gross sein muss (z.B. ein Vorwiderstand, der den Strom begrenzt)?",
            [("R_berechnet", wert, _R)], ("R_Norm", _R, "nächstgrösserer E12-Wert"), oben,
            ["E12-Reihe: 1.0 1.2 1.5 1.8 2.2 2.7 3.3 3.9 4.7 5.6 6.8 8.2 (× 10ⁿ)",
             f"{_f(wert, _R)} liegt zwischen {_f(unten, _R)} und {_f(oben, _R)}",
             f"Mindestens so gross -> nach oben: {_f(oben, _R)}"])


def _ladung(z):
    c, u = _e12(z, -7, -3), z.choice([5.0, 12.0, 24.0, 48.0])
    q = c * u
    return ("Ein Kondensator wird auf die Spannung U geladen. Welche Ladung trägt er?",
            [("C", c, _C), ("U", u, _U)], ("Q", "ladung", "gespeicherte Ladung"), q,
            ["Q = C · U", f"Q = {_f(c, _C)} · {_f(u, _U)} = {_f(q, 'ladung')}"])


def _energie_c(z):
    c, u = _e12(z, -6, -2), z.choice([12.0, 24.0, 50.0, 400.0])
    w = 0.5 * c * u * u
    return ("Wie viel Energie ist in einem geladenen Kondensator gespeichert?",
            [("C", c, _C), ("U", u, _U)], ("W", "energie", "gespeicherte Energie"), w,
            ["W = ½ · C · U²", f"W = 0.5 · {_f(c, _C)} · ({_f(u, _U)})² = {_f(w, 'energie')}",
             "Die Energie wächst mit U² – doppelte Spannung, vierfache Energie (Vorsicht bei grossen Elkos!)."])


def _c_reihe(z):
    c1, c2 = _e12(z, -9, -5), _e12(z, -9, -5)
    cg = c1 * c2 / (c1 + c2)
    return ("Zwei Kondensatoren sind in REIHE geschaltet. Wie gross ist die Gesamtkapazität?",
            [("C1", c1, _C), ("C2", c2, _C)], ("C_ges", _C, "Gesamtkapazität"), cg,
            ["Bei Kondensatoren ist es umgekehrt wie bei Widerständen: in Reihe wird die Kapazität KLEINER.",
             "C_ges = C1 · C2 / (C1 + C2)", f"C_ges = {_f(cg, _C)}  (kleiner als der kleinste Einzelwert)"])


def _xc(z):
    c, f = _e12(z, -9, -5), z.choice([50.0, 1e3, 10e3, 100e3])
    x = 1 / (2 * math.pi * f * c)
    return ("Wie gross ist der Blindwiderstand eines Kondensators bei der Frequenz f?",
            [("C", c, _C), ("f", f, "frequenz")], ("X_C", _R, "kapazitiver Blindwiderstand"), x,
            ["X_C = 1 / (2π · f · C)", f"X_C = 1 / (2π · {_f(f, 'frequenz')} · {_f(c, _C)}) = {_f(x, _R)}",
             "Je höher die Frequenz, desto KLEINER X_C – Kondensatoren lassen hohe Frequenzen durch."])


def _xl(z):
    l, f = _e12(z, -6, -1), z.choice([50.0, 1e3, 10e3, 100e3])
    x = 2 * math.pi * f * l
    return ("Wie gross ist der Blindwiderstand einer Spule bei der Frequenz f?",
            [("L", l, _L), ("f", f, "frequenz")], ("X_L", _R, "induktiver Blindwiderstand"), x,
            ["X_L = 2π · f · L", f"X_L = 2π · {_f(f, 'frequenz')} · {_f(l, _L)} = {_f(x, _R)}",
             "Je höher die Frequenz, desto GRÖSSER X_L – Spulen sperren hohe Frequenzen."])


def _leitung(z):
    l, a = z.choice([10.0, 20.0, 25.0, 50.0, 100.0]), z.choice([0.75, 1.5, 2.5, 4.0])
    rho = 0.0175
    r = rho * 2 * l / a
    return (f"Eine Kupferleitung ist {l:g} m lang (Hin- UND Rückleiter, also {2 * l:g} m Draht) und hat den "
            f"Querschnitt {a:g} mm². Wie gross ist ihr Widerstand? (ρ Kupfer = 0.0175 Ω·mm²/m)",
            [("l (einfach)", l, "laenge"), ("A", a * 1e-6, "flaeche")], ("R", _R, "Widerstand der Leitung"), r,
            ["R = ρ · l / A, mit l = Länge des ganzen Stromwegs (hin und zurück)",
             f"R = 0.0175 Ω·mm²/m · {2 * l:g} m / {a:g} mm² = {_f(r, _R)}",
             "Doppelter Querschnitt = halber Widerstand; doppelte Länge = doppelter Widerstand."])


def _temperatur_r(z):
    r20, t = _e12(z, 1, 3), z.choice([-20, 0, 60, 80, 100, 150])
    alpha = 0.0039
    r = r20 * (1 + alpha * (t - 20))
    return (f"Eine Kupferwicklung hat bei 20 °C den Widerstand R20. Wie gross ist der Widerstand bei {t} °C? "
            "(α Kupfer = 0.0039 1/K, lineare Näherung)",
            [("R20", r20, _R), ("ϑ", float(t), "temperatur")], ("R", _R, f"Widerstand bei {t} °C"), r,
            ["R = R20 · (1 + α · Δϑ),  Δϑ = ϑ − 20 °C", f"Δϑ = {t - 20} K",
             f"R = {_f(r20, _R)} · (1 + 0.0039 · {t - 20}) = {_f(r, _R)}",
             "Kupfer wird mit steigender Temperatur hochohmiger (Kaltleiter-Verhalten, PTC)."])


def _trafo(z):
    n1, n2 = z.choice([200, 500, 1000, 1150, 2300]), z.choice([50, 60, 100, 115, 230])
    u1 = 230.0
    u2 = u1 * n2 / n1
    return ("Ein idealer Transformator hat die Windungszahlen N1 (primär) und N2 (sekundär). Welche Spannung liefert "
            "er sekundär?", [("U1", u1, _U), ("N1", float(n1), "zahl"), ("N2", float(n2), "zahl")],
            ("U2", _U, "Sekundärspannung"), u2,
            ["Idealer Trafo: U1 / U2 = N1 / N2  ->  U2 = U1 · N2 / N1",
             f"U2 = 230 V · {n2} / {n1} = {_f(u2, _U)}",
             "Die Ströme verhalten sich umgekehrt: I2 / I1 = N1 / N2 (Leistung bleibt gleich)."])


def _trafo_strom(z):
    u1, u2 = 230.0, z.choice([6.0, 12.0, 24.0, 48.0])
    i2 = z.choice([0.5, 1.0, 2.0, 5.0])
    i1 = i2 * u2 / u1
    return ("Ein idealer Transformator setzt 230 V auf U2 herunter und liefert sekundär den Strom I2. Welcher Strom "
            "fliesst primär?", [("U1", u1, _U), ("U2", u2, _U), ("I2", i2, _I)], ("I1", _I, "Primärstrom"), i1,
            ["Idealer Trafo: Leistung primär = Leistung sekundär: U1 · I1 = U2 · I2",
             f"I1 = I2 · U2 / U1 = {_f(i2, _I)} · {_f(u2, _U)} / 230 V = {_f(i1, _I)}",
             "In Wirklichkeit etwas mehr (Verluste, Magnetisierungsstrom)."])


def _diode_verlust(z):
    uf, i = z.choice([0.7, 0.45, 1.0]), z.choice([0.5, 1.0, 2.0, 3.0])
    p = uf * i
    art_d = {0.7: "Silizium-Diode", 0.45: "Schottky-Diode", 1.0: "Silizium-Diode bei hohem Strom"}[uf]
    return (f"Durch eine {art_d} fliesst der Strom I, die Flussspannung beträgt UF. Welche Leistung wird in der "
            "Diode in Wärme umgesetzt?", [("UF", uf, _U), ("I", i, _I)], ("P", "leistung", "Verlustleistung"), p,
            ["P = UF · I", f"P = {_f(uf, _U)} · {_f(i, _I)} = {_f(p, 'leistung')}",
             "Darum nimmt man bei grossen Strömen gerne Schottky-Dioden (kleineres UF)."])


# =============================================================================
# MESSTECHNIK
# =============================================================================
def _rel_abweichung(z):
    richtig = z.choice([5.0, 10.0, 12.0, 24.0, 100.0])
    mess = float(f"{richtig * (1 + z.choice([-1, 1]) * z.uniform(0.005, 0.05)):.4g}")
    f = (mess - richtig) / richtig
    return ("Ein Messgerät zeigt den Messwert an, der richtige Wert (Referenz) ist bekannt. Wie gross ist die relative "
            "Abweichung (mit Vorzeichen)?", [("Messwert", mess, _U), ("richtiger Wert", richtig, _U)],
            ("f", "prozent", "relative Abweichung"), f,
            ["Absolute Abweichung: F = Messwert − richtiger Wert = " + f"{_f(mess - richtig, _U)}",
             "Relative Abweichung: f = F / richtiger Wert", f"f = {f * 100:+.3g} %",
             "Plus = das Gerät zeigt zu viel an, minus = zu wenig."])


def _effektivwert(z):
    u_hat = z.choice([10.0, 14.1, 24.0, 100.0, 325.0])
    ueff = u_hat / math.sqrt(2)
    return ("Eine sinusförmige Spannung hat den Scheitelwert Û. Wie gross ist ihr Effektivwert?",
            [("Û", u_hat, _U)], ("U_eff", _U, "Effektivwert"), ueff,
            ["Nur für SINUS: U_eff = Û / √2 ≈ 0.707 · Û", f"U_eff = {_f(u_hat, _U)} / 1.414 = {_f(ueff, _U)}",
             "Beispiel Netz: Û ≈ 325 V -> 230 V effektiv."])


def _uss(z):
    uss = z.choice([2.0, 5.0, 10.0, 20.0, 650.0])
    ueff = uss / (2 * math.sqrt(2))
    return ("Am Oszilloskop wird bei einem Sinus die Spitze-Spitze-Spannung U_ss abgelesen. Welchen Effektivwert zeigt "
            "ein True-RMS-Multimeter?", [("U_ss", uss, _U)], ("U_eff", _U, "Effektivwert"), ueff,
            ["Û = U_ss / 2", f"U_eff = Û / √2 = U_ss / (2 · √2) = {_f(uss, _U)} / 2.828 = {_f(ueff, _U)}"])


def _oszi_frequenz(z):
    kaestchen = z.choice([2.0, 2.5, 4.0, 5.0, 8.0])
    zeitbasis = z.choice([10e-6, 50e-6, 0.1e-3, 0.5e-3, 1e-3, 2e-3])
    t = kaestchen * zeitbasis
    f = 1 / t
    return ("Auf dem Oszilloskop ist eine ganze Periode des Signals so viele Kästchen (DIV) breit. Wie gross ist die "
            "Frequenz?", [("Periode", kaestchen, "zahl"), ("Zeitbasis (pro DIV)", zeitbasis, "zeit")],
            ("f", "frequenz", "Signalfrequenz"), f,
            [f"T = Kästchen · Zeitbasis = {kaestchen:g} · {_f(zeitbasis, 'zeit')} = {_f(t, 'zeit')}",
             f"f = 1 / T = {_f(f, 'frequenz')}"])


def _oszi_spannung(z):
    div, vdiv = z.choice([3.0, 4.0, 5.0, 6.4]), z.choice([0.1, 0.2, 0.5, 1.0, 2.0])
    tastkopf = z.choice([1, 10])
    uss = div * vdiv * tastkopf
    return (f"Ein Sinus ist am Oszilloskop {div:g} Kästchen hoch (Spitze-Spitze). Eingestellt ist die Ablenkung "
            f"V/DIV, verwendet wird ein Tastkopf {tastkopf}:1 – das Oszilloskop ist aber auf 1:1 eingestellt. "
            "Wie gross ist die WIRKLICHE Spitze-Spitze-Spannung am Messpunkt?",
            [("Höhe", div, "zahl"), ("V/DIV", vdiv, _U), ("Tastkopf", float(tastkopf), "zahl")],
            ("U_ss", _U, "wirkliche Spitze-Spitze-Spannung"), uss,
            [f"Am Eingang des Oszilloskops: {div:g} · {_f(vdiv, _U)} = {_f(div * vdiv, _U)}",
             f"Der Tastkopf {tastkopf}:1 teilt die Spannung durch {tastkopf} – also mal {tastkopf} rechnen: {_f(uss, _U)}",
             "Tipp: Tastkopf-Faktor im Kanalmenü einstellen, dann stimmt die Anzeige direkt."])


def _dmm(z):
    anzeige = z.choice([4.873, 12.05, 0.987, 230.4, 1.500])
    p, d = z.choice([0.005, 0.008, 0.01]), z.choice([2, 3, 5])
    aufl = {4.873: 0.001, 12.05: 0.01, 0.987: 0.001, 230.4: 0.1, 1.500: 0.001}[anzeige]
    fehler = abs(anzeige) * p + d * aufl
    return (f"Ein Multimeter zeigt {anzeige} V. Im Datenblatt steht für diesen Bereich: ± ({p * 100:g} % vom Messwert "
            f"+ {d} Digit); die letzte Stelle hat den Wert {aufl:g} V. Wie gross ist die Fehlergrenze (Betrag)?",
            [("Anzeige", anzeige, _U)], ("± F", _U, "Fehlergrenze"), fehler,
            [f"Prozent-Anteil: {p * 100:g} % · {anzeige} V = {_f(abs(anzeige) * p, _U)}",
             f"Digit-Anteil: {d} · {aufl:g} V = {_f(d * aufl, _U)}",
             f"Fehlergrenze = ± {_f(fehler, _U)}  ->  wahrer Wert zwischen {anzeige - fehler:.4g} V und {anzeige + fehler:.4g} V"])


def _klasse(z):
    k = z.choice([0.5, 1.0, 1.5, 2.5])
    endwert = z.choice([10.0, 30.0, 100.0, 300.0])
    anzeige = float(f"{endwert * z.choice([0.2, 0.25, 0.5, 0.8, 1.0]):.3g}")
    f_rel = k / 100 * endwert / anzeige
    return (f"Ein Zeigerinstrument der Genauigkeitsklasse {k:g} hat den Messbereich 0 … {endwert:g} V und zeigt "
            f"{anzeige:g} V. Wie gross ist die Fehlergrenze in Prozent VOM MESSWERT?",
            [("Klasse", k, "zahl"), ("Endwert", endwert, _U), ("Anzeige", anzeige, _U)],
            ("f", "prozent", "relative Fehlergrenze bezogen auf den Messwert"), f_rel,
            [f"Klasse {k:g}: höchstens ±{k:g} % vom ENDWERT = ± {_f(k / 100 * endwert, _U)} – überall im Bereich",
             f"Bezogen auf die Anzeige: {_f(k / 100 * endwert, _U)} / {anzeige:g} V = {f_rel * 100:.3g} %",
             "Darum den Messbereich so wählen, dass der Zeiger möglichst weit ausschlägt."])


def _pt100(z):
    t = z.choice([0, 25, 50, 100, 150, 200, 250, -20])
    r = pt_widerstand(t, 100.0)
    return (f"Welchen Widerstand hat ein Pt100 bei {t} °C? (Kennlinie nach IEC 60751, "
            "A = 3.9083·10⁻³ 1/K, B = −5.775·10⁻⁷ 1/K², für T ≥ 0 °C: R = R0 · (1 + A·T + B·T²))",
            [("T", float(t), "temperatur"), ("R0", 100.0, _R)], ("R", _R, f"Widerstand bei {t} °C"), r,
            [f"R = 100 Ω · (1 + A · {t} + B · {t}²) = {_f(r, _R)}" if t >= 0 else
             "Unter 0 °C kommt ein dritter Term C·(T − 100)·T³ dazu (C = −4.183·10⁻¹² 1/K⁴)",
             f"R({t} °C) = {_f(r, _R)}",
             "Faustregel: rund 0.385 Ω pro Kelvin (zwischen 0 und 100 °C im Mittel)."])


def _pt100_zurueck(z):
    r = float(f"{z.uniform(100.5, 190):.2f}")
    t = pt_temperatur(r, 100.0)
    return ("Ein Pt100 hat den gemessenen Widerstand R. Welche Temperatur hat er? (IEC 60751, T ≥ 0 °C: "
            "R = R0 · (1 + A·T + B·T²), A = 3.9083·10⁻³, B = −5.775·10⁻⁷)",
            [("R", r, _R), ("R0", 100.0, _R)], ("T", "temperatur", "Temperatur"), t,
            ["Quadratische Gleichung nach T auflösen: T = (−A + √(A² − 4·B·(1 − R/R0))) / (2·B)",
             f"T = {_f(t, 'temperatur')}",
             f"Grob geschätzt mit 0.385 Ω/K: ({r:g} − 100) / 0.385 = {(r - 100) / 0.385:.1f} °C – fast gleich."])


def _messkette(z):
    oben = z.choice([100.0, 250.0, 10.0, 16.0])
    einheit = {100.0: "°C", 250.0: "°C", 10.0: "bar", 16.0: "bar"}[oben]
    i = float(f"{z.uniform(4.5, 19.5):.2f}") * 1e-3
    wert = (i - 0.004) / 0.016 * oben
    return (f"Ein Messumformer gibt 4 … 20 mA für den Bereich 0 … {oben:g} {einheit} aus. Gemessen werden {i * 1e3:.2f} mA. "
            f"Welcher Messwert (in {einheit}) ist das?", [("I", i, _I)], ("Messwert", "zahl", f"in {einheit}"), wert,
            ["Linear: 4 mA = Anfang, 20 mA = Ende, die Spanne ist 16 mA",
             f"Messwert = (I − 4 mA) / 16 mA · {oben:g} {einheit}",
             f"= ({i * 1e3:.2f} − 4) / 16 · {oben:g} = {wert:.4g} {einheit}",
             "0 mA heisst nicht 'Wert 0', sondern Kabelbruch – darum der lebende Nullpunkt bei 4 mA."])


def _shunt(z):
    ri, iv = z.choice([100.0, 500.0, 1000.0, 2000.0]), z.choice([50e-6, 100e-6, 1e-3])
    i = z.choice([10e-3, 100e-3, 1.0])
    rs = ri * iv / (i - iv)
    return ("Ein Messwerk (Innenwiderstand Ri, Vollausschlag Iv) soll den grösseren Strombereich I bekommen. "
            "Wie gross muss der Parallelwiderstand (Shunt) sein?",
            [("Ri", ri, _R), ("Iv", iv, _I), ("I", i, _I)], ("Rs", _R, "Shunt"), rs,
            ["Durch das Messwerk darf nur Iv fliessen, der Rest I − Iv muss durch den Shunt.",
             "Beide haben dieselbe Spannung Ri · Iv:  Rs = Ri · Iv / (I − Iv)",
             f"Rs = {_f(ri, _R)} · {_f(iv, _I)} / ({_f(i, _I)} − {_f(iv, _I)}) = {_f(rs, _R)}"])


def _vorwiderstand(z):
    while True:                                                      # U deutlich grösser als Ri · Iv
        ri, iv = z.choice([100.0, 500.0, 1000.0, 2000.0]), z.choice([50e-6, 100e-6, 1e-3])
        u = z.choice([1.0, 10.0, 30.0, 100.0])
        if u > 2 * ri * iv:
            break
    rv = u / iv - ri
    return ("Ein Messwerk (Innenwiderstand Ri, Vollausschlag Iv) soll als Spannungsmesser für den Bereich U dienen. "
            "Wie gross muss der Vorwiderstand sein?",
            [("Ri", ri, _R), ("Iv", iv, _I), ("U", u, _U)], ("Rv", _R, "Vorwiderstand"), rv,
            ["Bei Vollausschlag fliesst Iv durch Rv UND Ri:  U = Iv · (Rv + Ri)",
             "Rv = U / Iv − Ri", f"Rv = {_f(u, _U)} / {_f(iv, _I)} − {_f(ri, _R)} = {_f(rv, _R)}"])


def _streuung(z):
    werte = [round(5.0 + z.gauss(0, 0.02), 3) for _ in range(z.randint(5, 7))]
    e = gm.auswerten(werte)
    return ("Eine Spannung wurde mehrmals gemessen (Werte in V). Wie gross ist die empirische Standardabweichung s?",
            [(f"U{k + 1}", w, _U) for k, w in enumerate(werte)], ("s", _U, "Standardabweichung"), e["s"],
            [f"Mittelwert: x̄ = Summe / n = {e['mittel']:.5g} V",
             "s = √( Σ (xᵢ − x̄)² / (n − 1) )   – durch n − 1, nicht durch n!",
             f"s = {_f(e['s'], _U)}",
             f"Unsicherheit des Mittelwerts: s / √n = {_f(e['s_mittel'], _U)}"])


def _adc_lsb(z):
    n, uref = z.choice([8, 10, 12, 16]), z.choice([2.5, 3.3, 5.0])
    lsb = uref / 2 ** n
    return (f"Ein {n}-Bit-AD-Wandler hat die Referenzspannung Uref. Wie gross ist 1 LSB (kleinste Stufe)?",
            [("n", float(n), "zahl"), ("Uref", uref, _U)], ("LSB", _U, "Spannung einer Stufe"), lsb,
            ["LSB = Uref / 2ⁿ", f"LSB = {_f(uref, _U)} / {2 ** n} = {_f(lsb, _U)}"])


def _adc_code(z):
    n, uref = z.choice([8, 10, 12]), z.choice([3.3, 5.0])
    u = float(f"{z.uniform(0.1, uref * 0.95):.3g}")
    lsb = uref / 2 ** n
    code = min(2 ** n - 1, int(u / lsb))
    return {"text": f"Ein {n}-Bit-AD-Wandler (Uref = {uref:g} V) misst {u:g} V. Welchen Code (dezimal) liefert er? "
                    "(Code = U / LSB, abgerundet)",
            "antwort": "text", "loesung": str(code), "vergleich": "basis10",
            "gegeben": [("n", f"{n} Bit"), ("Uref", f"{uref:g} V"), ("U", f"{u:g} V")],
            "gesucht": {"zeichen": "Code", "text": "dezimal"},
            "weg": [f"LSB = {uref:g} V / {2 ** n} = {_f(lsb, _U)}",
                    f"Code = {u:g} V / {_f(lsb, _U)} = {u / lsb:.2f}  ->  abgerundet {code}",
                    f"Binär: {code:0{n}b}, Hex: 0x{code:X}"]}


def _dms(z):
    ue, k = z.choice([5.0, 10.0]), 2.0
    eps = z.choice([100e-6, 250e-6, 500e-6, 1e-3])
    ud = ue * k * eps / 4
    return ("Ein Dehnungsmessstreifen (k = 2) sitzt in einer Viertelbrücke, die mit Ue gespeist wird. Das Bauteil wird "
            "um ε gedehnt. Wie gross ist die Brückenspannung? (Näherung für kleine Dehnungen)",
            [("Ue", ue, _U), ("ε", eps * 1e6, "zahl")], ("U_d", _U, "Brückenspannung"), ud,
            ["ε ist in µm/m angegeben (1000 µm/m = 0.1 % Dehnung)",
             "Viertelbrücke: U_d ≈ Ue · k · ε / 4",
             f"U_d ≈ {_f(ue, _U)} · 2 · {eps:g} / 4 = {_f(ud, _U)}",
             "Nur Millivolt – darum folgt immer ein Messverstärker."])


# =============================================================================
# SCHEMAS (kleine Bilder)
# =============================================================================
def _s_widerstand_farben(p, farben):
    """Widerstand mit Farbringen (Farben aus dem Rechner: FARB_HEX)."""
    x0, x1, y = 2.2, 7.8, 2.2
    p.leitung((0.6, y), (x0, y))
    p.leitung((x1, y), (9.4, y))
    a, b = p.p(x0, y - 0.75), p.p(x1, y + 0.75)
    p.c.create_rectangle(*a, *b, outline=p.linie, fill="#D9C7A3", width=p.dick)
    for i, farbe in enumerate(farben):
        x = x0 + 0.7 + i * 0.9 if i < len(farben) - 1 else x1 - 0.8
        a, b = p.p(x, y - 0.75), p.p(x + 0.45, y + 0.75)
        p.c.create_rectangle(*a, *b, outline="", fill=FARB_HEX.get(farbe, "#888888"))
    p.text(5, y + 2.0, f"R = {GESUCHT}", "center", fett=True, farbe=ORANGE)


def _s_farbcode(p, g, ges):
    _s_widerstand_farben(p, g["Farben"].split(" – "))


def _s_kreis_bauteil(p, g, ges, bauteil, name, wert, frage):
    p.wechselquelle(1.5, 1.6, 4.4, "", g.get("f", ""))
    p.leitung((1.5, 1.6), (1.5, 1), (6, 1))
    p.leitung((1.5, 4.4), (1.5, 5), (6, 5))
    if bauteil == "C":
        p.kondensator(6, 1, 5, name, wert)
    else:
        p.spule(6, 1, 6, 5, name, wert)
    p.text(3.8, 5.7, frage, "center", fett=True, farbe=ORANGE)


def _s_xc(p, g, ges):
    _s_kreis_bauteil(p, g, ges, "C", "C", g["C"], f"X_C = {GESUCHT}")


def _s_xl(p, g, ges):
    _s_kreis_bauteil(p, g, ges, "L", "L", g["L"], f"X_L = {GESUCHT}")


def _s_smd(p, g, ges):
    a, b = p.p(3.2, 1.2), p.p(6.8, 3.2)
    p.c.create_rectangle(*a, *b, outline=p.linie, fill="#1F2937", width=p.dick)
    for x0, x1 in ((2.6, 3.2), (6.8, 7.4)):                          # Lötkappen
        a, b = p.p(x0, 1.2), p.p(x1, 3.2)
        p.c.create_rectangle(*a, *b, outline=p.linie, fill="#C0C0C0", width=p.dick)
    x, y = p.p(5, 2.2)
    p.c.create_text(x, y, text=g["Code"], fill="#FFFFFF", font=p.fett, anchor="center")
    p.text(5, 4.2, f"R = {GESUCHT}", "center", fett=True, farbe=ORANGE)


def _s_c_quelle(p, g, ges, frage):
    p.quelle(1.5, 1.6, 4.4, "U", g["U"])
    p.leitung((1.5, 1.6), (1.5, 1), (5, 1))
    p.leitung((1.5, 4.4), (1.5, 5), (5, 5))
    p.kondensator(5, 1, 5, "C", g["C"])
    p.text(3.2, 5.7, frage, "center", fett=True, farbe=ORANGE)


def _s_ladung(p, g, ges):
    _s_c_quelle(p, g, ges, f"Q = {GESUCHT}")


def _s_energie(p, g, ges):
    _s_c_quelle(p, g, ges, f"W = {GESUCHT}")


def _s_leitung(p, g, ges):
    p.quelle(1.2, 1.6, 4.4, "", "")
    p.leitung((1.2, 1.6), (1.2, 1), (8.4, 1))
    p.leitung((1.2, 4.4), (1.2, 5), (8.4, 5))
    p.widerstand(8.4, 1, 8.4, 5, "Last", "")
    p.text(4.8, 0.55, f"l = {g['l (einfach)']} (hin)", "center", klein=True)
    p.text(4.8, 5.45, f"l = {g['l (einfach)']} (zurück)", "center", klein=True)
    p.text(4.8, 3.0, f"Cu, A = {g['A']}", "center", klein=True, farbe=p.leise)
    p.text(4.8, 3.6, f"R_Leitung = {GESUCHT}", "center", fett=True, farbe=ORANGE)


def _s_temperatur(p, g, ges):
    p.anschluss(1.2, 2.2)
    p.widerstand(1.2, 2.2, 6.2, 2.2, "Cu-Wicklung", f"R20 = {g['R20']}")
    p.anschluss(6.2, 2.2)
    p.text(3.7, 3.4, f"ϑ = {g['ϑ']}", "center", fett=True)
    p.text(3.7, 4.1, f"R = {GESUCHT}", "center", fett=True, farbe=ORANGE)


def _s_diode(p, g, ges):
    p.anschluss(1, 2)
    p.leitung((1, 2), (2.6, 2))
    p.diode(2.6, 2, 6.2, 2, "D", "")
    p.leitung((6.2, 2), (8, 2))
    p.anschluss(8, 2)
    p.strom(1.3, 2, 2.3, 2, f"I = {g['I']}", seite="unten")
    p.text(4.4, 3.4, f"UF = {g['UF']}", "center", klein=True)
    p.text(4.4, 4.0, f"P = {GESUCHT}", "center", fett=True, farbe=ORANGE)


def _s_c_reihe(p, g, ges):
    p.anschluss(1, 2)
    p.leitung((1, 2), (3, 2))
    p.kondensator_waagrecht(3, 4.2, 2, "C1", g["C1"])
    p.leitung((4.2, 2), (5.8, 2))
    p.kondensator_waagrecht(5.8, 7, 2, "C2", g["C2"])
    p.leitung((7, 2), (9, 2))
    p.anschluss(9, 2)
    p.text(5, 3.4, f"C_ges = {GESUCHT}", "center", fett=True, farbe=ORANGE)


def _s_trafo(p, g, ges, u2_text=None, i_text=None):
    p.wechselquelle(1.2, 1.6, 4.4, "U1", g["U1"])
    p.leitung((1.2, 1.6), (1.2, 1), (3.6, 1), (3.6, 1.6))
    p.leitung((1.2, 4.4), (1.2, 5), (3.6, 5), (3.6, 4.4))
    p.trafo(4.5, 1.6, 4.4)
    p.leitung((5.4, 1.6), (5.4, 1), (7.8, 1))
    p.leitung((5.4, 4.4), (5.4, 5), (7.8, 5))
    p.widerstand(7.8, 1, 7.8, 5, "Last", i_text or "")
    p.text(4.5, 5.6, f"N1 = {g.get('N1', '')}   N2 = {g.get('N2', '')}" if "N1" in g else "", "center", klein=True)
    p.spannung(9.2, 1.1, 4.9, u2_text or f"U2 = {g.get('U2', '')}")
    p.leitung((7.8, 1), (9.2, 1), farbe=p.leise, dick=1)
    p.leitung((7.8, 5), (9.2, 5), farbe=p.leise, dick=1)


def _s_trafo_u(p, g, ges):
    _s_trafo(p, g, ges, u2_text=f"U2 = {GESUCHT}")


def _s_trafo_i(p, g, ges):
    _s_trafo(p, g, ges, i_text=f"I2 = {g['I2']}")
    p.strom(2.0, 1, 3.2, 1, f"I1 = {GESUCHT}")


def _s_shunt(p, g, ges):
    p.anschluss(1, 2.5)
    p.leitung((1, 2.5), (3, 2.5))
    p.knoten(3, 2.5)
    p.leitung((3, 2.5), (3, 1.4), (4, 1.4))
    p.leitung((3, 2.5), (3, 3.8), (4, 3.8))
    p.messgeraet(5, 1.4, "A", f"Ri = {g['Ri']}, Iv = {g['Iv']}")
    p.leitung((5.42, 1.4), (7, 1.4), (7, 2.5))
    p.widerstand(4, 3.8, 7, 3.8, "Rs", GESUCHT, seite="unten")
    p.leitung((7, 3.8), (7, 2.5))
    p.knoten(7, 2.5)
    p.leitung((7, 2.5), (9, 2.5))
    p.anschluss(9, 2.5)
    p.text(5, 0.4, f"Bereich I = {g['I']}", "center", klein=True)


def _s_vorwiderstand(p, g, ges):
    p.anschluss(1, 2.2)
    p.widerstand(1, 2.2, 4.4, 2.2, "Rv", GESUCHT)
    p.messgeraet(5.4, 2.2, "V", "")
    p.leitung((5.82, 2.2), (9, 2.2))
    p.anschluss(9, 2.2)
    p.text(5.4, 3.2, f"Ri = {g['Ri']}, Iv = {g['Iv']}", "center", klein=True)
    p.text(5, 3.9, f"Bereich U = {g['U']}", "center", klein=True)


# =============================================================================
# ANMELDEN
# =============================================================================
_LISTE_B = [
    ("farbcode_4", "Farbcode: 4 Ringe lesen", "Widerstand", 1, ("Bauteile", "widerstand"), _farbcode_4, (10, 5, _s_farbcode)),
    ("smd_code", "SMD-Code lesen", "Widerstand", 1, ("Bauteile", "widerstand"), _smd, (10, 4.8, _s_smd)),
    ("farbcode_5", "Farbcode: 5 Ringe (E96)", "Widerstand", 2, ("Bauteile", "widerstand"), _farbcode_5, (10, 5, _s_farbcode)),
    ("normwert_e12", "Normwert wählen (E12)", "Widerstand", 2, ("Bauteile", "widerstand"), _normwert, None),
    ("leitungswiderstand", "Leitungswiderstand", "Widerstand", 2, ("Bauteile", "widerstand"), _leitung, (9.8, 6.0, _s_leitung)),
    ("temperatur_widerstand", "Widerstand bei anderer Temperatur", "Widerstand", 3, ("Bauteile", "widerstand"), _temperatur_r, (7.8, 4.6, _s_temperatur)),
    ("kondensator_ladung", "Kondensator: Ladung Q", "Kondensator & Spule", 1, ("Bauteile", "kondensator"), _ladung, (7.6, 6.2, _s_ladung)),
    ("kondensator_reihe", "Kondensatoren in Reihe", "Kondensator & Spule", 2, ("Bauteile", "kondensator"), _c_reihe, (10, 4.2, _s_c_reihe)),
    ("kondensator_xc", "Blindwiderstand X_C", "Kondensator & Spule", 2, ("Bauteile", "kondensator"), _xc, (8.4, 6.4, _s_xc)),
    ("spule_xl", "Blindwiderstand X_L", "Kondensator & Spule", 2, ("Bauteile", "spule"), _xl, (8.4, 6.4, _s_xl)),
    ("kondensator_energie", "Kondensator: Energie", "Kondensator & Spule", 3, ("Bauteile", "kondensator"), _energie_c, (7.6, 6.2, _s_energie)),
    ("trafo_u2", "Transformator: Sekundärspannung", "Transformator & Diode", 2, ("Bauteile", "transformator"), _trafo, (10.4, 6.2, _s_trafo_u)),
    ("diode_verlust", "Diode: Verlustleistung", "Transformator & Diode", 2, ("Bauteile", "diode"), _diode_verlust, (9.2, 4.6, _s_diode)),
    ("trafo_i1", "Transformator: Primärstrom", "Transformator & Diode", 3, ("Bauteile", "transformator"), _trafo_strom, (10.4, 6.2, _s_trafo_i)),
]
_LISTE_M = [
    ("rel_abweichung", "Relative Messabweichung", "Grundlagen", 1, ("Messtechnik", "messabweichungen"), _rel_abweichung, None),
    ("effektivwert", "Sinus: Effektivwert aus Û", "Grundlagen", 1, ("Messtechnik", "signalkenngroessen"), _effektivwert, None),
    ("uss_ueff", "Sinus: U_ss → U_eff", "Grundlagen", 2, ("Messtechnik", "signalkenngroessen"), _uss, None),
    ("streuung", "Standardabweichung einer Messreihe", "Grundlagen", 3, ("Messtechnik", "messunsicherheit"), _streuung, None),
    ("oszi_frequenz", "Oszilloskop: Frequenz ablesen", "Messgeräte", 1, ("Messtechnik", "oszilloskop"), _oszi_frequenz, None),
    ("dmm_fehler", "Multimeter: Fehlergrenze", "Messgeräte", 2, ("Messtechnik", "multimeter"), _dmm, None),
    ("genauigkeitsklasse", "Genauigkeitsklasse", "Messgeräte", 2, ("Messtechnik", "begriffe"), _klasse, None),
    ("oszi_tastkopf", "Oszilloskop: Tastkopf 10:1", "Messgeräte", 3, ("Messtechnik", "oszilloskop"), _oszi_spannung, None),
    ("shunt", "Messbereich erweitern: Shunt", "Messgeräte", 3, ("Messtechnik", "multimeter"), _shunt, (10, 5.4, _s_shunt)),
    ("vorwiderstand_messwerk", "Messbereich erweitern: Vorwiderstand", "Messgeräte", 3, ("Messtechnik", "multimeter"), _vorwiderstand, (10, 4.6, _s_vorwiderstand)),
    ("pt100_r", "Pt100: Widerstand bei T", "Sensoren & Messkette", 2, ("Messtechnik", "temperatur"), _pt100, None),
    ("messkette_ma", "4 … 20 mA: Messwert", "Sensoren & Messkette", 2, ("Messtechnik", "messkette"), _messkette, None),
    ("pt100_t", "Pt100: Temperatur aus R", "Sensoren & Messkette", 3, ("Messtechnik", "temperatur"), _pt100_zurueck, None),
    ("dms_bruecke", "DMS in der Viertelbrücke", "Sensoren & Messkette", 4, ("Messtechnik", "bruecke_dms"), _dms, None),
    ("adc_lsb", "AD-Wandler: LSB", "Digital", 2, ("Messtechnik", "ad_wandler"), _adc_lsb, None),
    ("adc_code", "AD-Wandler: Code für eine Spannung", "Digital", 3, ("Messtechnik", "ad_wandler"), _adc_code, None),
]
for _bereich, _liste in ((B, _LISTE_B), (M, _LISTE_M)):
    for _id, _titel, _thema, _stufe, _seite, _erz, _schema in _liste:
        art(_id, _titel, _bereich, _thema, _stufe, [_seite], _erz)
        if _schema:
            SCHEMAS[_id] = _schema
