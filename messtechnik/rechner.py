# =============================================================================
# messtechnik/rechner.py
# -----------------------------------------------------------------------------
# Alle RECHNER des Bereichs "Messtechnik".
# Registriert in bauteile/rechner/__init__.py (gleiches System wie bei den Bauteilen).
#
#   statistik            Mittelwert, Standardabweichung, Messunsicherheit (Student-t)
#   dmm_genauigkeit      ±(% vom Messwert + Digits)
#   fehlerfortpflanzung  Produkt/Quotient bzw. Summe/Differenz, Worst Case und statistisch
#   signalform           Effektivwert, Gleichrichtwert, Crestfaktor, Anzeige ohne True RMS
#   messbereich          Vorwiderstand / Shunt für ein Messwerk
#   belastung_u          Belastungsfehler bei Spannungsmessung (Innenwiderstand Messgerät)
#   buerde_i             Einfluss des Strommessers (Bürdenspannung)
#   oszi                 Bandbreite, Anstiegszeit, Amplitudenfehler, Abtastrate
#   pt100                Pt100/Pt1000 <-> Temperatur (Callendar-Van Dusen) + 2-Leiter-Fehler
#   ntc                  NTC <-> Temperatur (B-Wert-Gleichung)
#   thermoelement        Thermospannung <-> Temperatur (lineare Näherung)
#   bruecke              Wheatstone-Brücke: Ausgangsspannung / Abgleichwert
#   dms                  Dehnungsmessstreifen in Viertel-/Halb-/Vollbrücke
#   adc                  Auflösung, LSB, Code, Signal-Rausch-Abstand, Abtastrate
#   mid                  Magnetisch-induktive Durchflussmessung
#   abtastung            INTERAKTIV: Abtasttheorem / Aliasing (messtechnik/grafiken.py)
# =============================================================================

import math

from bauteile import einheiten                                                   # -> bauteile/einheiten.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, anzahl_gegeben, fmt   # -> bauteile/rechner/basis.py
from messtechnik.grafiken import AbtastGrafik                                   # -> messtechnik/grafiken.py

# ---- Zusätzliche Einheiten nur für diesen Bereich (bauteile/einheiten.py bleibt unverändert) ----
einheiten.EINHEITEN.setdefault("volumenstrom", {
    "stufen": [("l/h", 1 / 3.6e6), ("l/min", 1 / 60000), ("m³/h", 1 / 3600), ("m³/s", 1)],
    "standard": "m³/h", "vorsatz": False})
einheiten.EINHEITEN.setdefault("geschwindigkeit", {"stufen": [("m/s", 1)], "standard": "m/s", "vorsatz": False})


def _std(wert, standard):
    return standard if wert is None else wert


# =============================================================================
# 1) STATISTIK / MESSUNSICHERHEIT
# =============================================================================
# Student-t-Faktoren (zweiseitig) für Freiheitsgrad f = n − 1
_T95 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23,
        15: 2.13, 20: 2.09, 30: 2.04, 60: 2.00}
_T99 = {1: 63.66, 2: 9.92, 3: 5.84, 4: 4.60, 5: 4.03, 6: 3.71, 7: 3.50, 8: 3.36, 9: 3.25, 10: 3.17,
        15: 2.95, 20: 2.85, 30: 2.75, 60: 2.66}


def _t_faktor(tabelle, f, unendlich):
    if f > max(tabelle):
        return unendlich
    return tabelle[max(k for k in tabelle if k <= f)]       # konservativ: nächst kleinerer Freiheitsgrad


def _statistik(w):
    werte = w["liste"]
    if not werte or len(werte) < 2:
        raise RechnerFehler("Mindestens zwei Messwerte eingeben, getrennt mit Leerzeichen: 4.98 5.02 5.01")
    n = len(werte)
    mittel = sum(werte) / n
    s = math.sqrt(sum((x - mittel) ** 2 for x in werte) / (n - 1))
    s_mittel = s / math.sqrt(n)
    niveau = w["niveau"]
    if niveau.startswith("95"):
        t = _t_faktor(_T95, n - 1, 1.96)
    elif niveau.startswith("99"):
        t = _t_faktor(_T99, n - 1, 2.58)
    else:
        t = 1.0
    u = t * s_mittel
    return [f"n = {n} Werte   Min {min(werte):.6g}   Max {max(werte):.6g}   Spanne {max(werte) - min(werte):.4g}",
            f"Mittelwert x̄ = {mittel:.6g}",
            f"Standardabweichung s = {s:.4g}   (Streuung EINES Messwerts)",
            f"Standardabweichung des Mittelwerts s/√n = {s_mittel:.4g}",
            f"Ergebnis ({niveau.split(' (')[0]}):  x = {mittel:.6g} ± {u:.3g}   (t = {t:g})",
            f"Relativ: ± {abs(u / mittel) * 100:.3g} %" if mittel else "Relativer Fehler: nicht definiert (Mittelwert 0)",
            "Nur zufällige Fehler! Systematische (Kalibrierung, Belastung) kommen noch dazu."]


def statistik(master):
    return FormelRechner(
        master, "Messreihe auswerten", "Werte mit Leerzeichen oder ; trennen (Dezimalpunkt verwenden)",
        felder=[("liste", "Messwerte", "zahl", {"liste": True, "platzhalter": "4.98 5.02 5.01 4.99"}),
                ("niveau", "Vertrauensniveau", "auswahl",
                 {"werte": ["95 % (üblich)", "68 % (1 σ)", "99 %"], "standard": "95 % (üblich)"})],
        berechnen=_statistik, formel="x̄ = Σx/n     s = √(Σ(x−x̄)²/(n−1))     u = t · s/√n")


def _dmm(w):
    x, p, d, res = w["x"], w["p"], w["d"], w["res"]
    if None in (x, p, res):
        raise RechnerFehler("Anzeigewert, %-Angabe und Auflösung (Wert der letzten Stelle) eingeben")
    d = _std(d, 0)
    fehler = abs(x) * p + d * res
    zeilen = [f"Fehlergrenze = {abs(x):g} · {p * 100:g} % + {d:g} · {res:g} = ± {fehler:.4g}",
              f"Wahrer Wert liegt zwischen {x - fehler:.6g} und {x + fehler:.6g}",
              f"Relativ: ± {fehler / abs(x) * 100:.3g} %" if x else "Anzeige 0 → nur Digit-Anteil zählt"]
    if w["bereich"] is not None and w["bereich"] > 0 and abs(x) < 0.1 * w["bereich"]:
        zeilen.append("⚠ Wert nutzt < 10 % des Messbereichs → kleineren Bereich wählen, dann wird der Digit-Anteil kleiner")
    return zeilen


def dmm_genauigkeit(master):
    return FormelRechner(
        master, "Genauigkeit Multimeter", "Datenblatt-Angabe z.B. ±(0.5 % + 2 Digits)",
        felder=[("x", "Anzeigewert", "zahl", {"platzhalter": "z.B. 12.34"}),
                ("p", "% vom Messwert", "prozent", {"platzhalter": "z.B. 0.5"}),
                ("d", "Digits", "zahl", {"platzhalter": "z.B. 2"}),
                ("res", "Auflösung (1 Digit)", "zahl", {"platzhalter": "z.B. 0.01"}),
                ("bereich", "Messbereich (opt.)", "zahl", {"platzhalter": "z.B. 40"})],
        berechnen=_dmm, formel="Fehler = ± (p · |Anzeige| + n · Auflösung)")


def _fehlerfort(w):
    x, y, dx, dy = w["x"], w["y"], w["dx"], w["dy"]
    if None in (x, y, dx, dy):
        raise RechnerFehler("Beide Werte und ihre (absoluten) Unsicherheiten eingeben")
    if w["art"].startswith("Produkt"):
        if x == 0 or y == 0:
            raise RechnerFehler("Werte dürfen bei Produkt/Quotient nicht 0 sein")
        rx, ry = abs(dx / x), abs(dy / y)
        return [f"Relative Unsicherheiten: {rx * 100:.3g} % und {ry * 100:.3g} %",
                f"Worst Case:   ± {(rx + ry) * 100:.3g} %   (Beträge addieren)",
                f"Statistisch:  ± {math.hypot(rx, ry) * 100:.3g} %   (quadratisch addieren)",
                f"x · y = {x * y:.6g} ± {abs(x * y) * math.hypot(rx, ry):.3g}   ·   "
                f"x / y = {x / y:.6g} ± {abs(x / y) * math.hypot(rx, ry):.3g}  (statistisch)"]
    d_worst, d_stat = abs(dx) + abs(dy), math.hypot(dx, dy)
    zeilen = [f"Absolut: Worst Case ± {d_worst:.4g}   ·   statistisch ± {d_stat:.4g}",
              f"Summe     x + y = {x + y:.6g} ± {d_stat:.3g}" +
              (f"  → relativ ± {d_stat / abs(x + y) * 100:.3g} %" if x + y else "")]
    if x - y:
        rel = d_stat / abs(x - y) * 100
        zeilen.append(f"Differenz x − y = {x - y:.6g} ± {d_stat:.3g}  → relativ ± {rel:.3g} %")
        if rel > 5 * max(abs(dx / x) if x else 0, abs(dy / y) if y else 0) * 100:
            zeilen.append("⚠ Differenz zweier fast gleicher Werte: der relative Fehler explodiert!")
    return zeilen


def fehlerfortpflanzung(master):
    return FormelRechner(
        master, "Fehlerfortpflanzung", "Wie genau ist ein berechnetes Ergebnis (z.B. P = U · I)?",
        felder=[("art", "Rechenart", "auswahl",
                 {"werte": ["Produkt / Quotient (P = U·I, R = U/I)", "Summe / Differenz (U1 ± U2)"]}),
                ("x", "Wert 1", "zahl"), ("dx", "Unsicherheit 1 (±)", "zahl"),
                ("y", "Wert 2", "zahl"), ("dy", "Unsicherheit 2 (±)", "zahl")],
        berechnen=_fehlerfort,
        formel="Produkt/Quotient: relative Fehler addieren   ·   Summe/Differenz: absolute Fehler addieren")


# =============================================================================
# 2) SIGNALKENNGRÖSSEN
# =============================================================================
SIGNALE = ["Sinus", "Rechteck symmetrisch (±Û)", "Dreieck symmetrisch (±Û)", "PWM / Rechteck 0 … Û",
           "Sinus einweg-gleichgerichtet", "Sinus vollweg-gleichgerichtet"]


def _kennwerte(art, u, d):
    """(Effektivwert, arithm. Mittelwert, Gleichrichtwert)"""
    if art == SIGNALE[0]:
        return u / math.sqrt(2), 0.0, 2 * u / math.pi
    if art == SIGNALE[1]:
        return u, 0.0, u
    if art == SIGNALE[2]:
        return u / math.sqrt(3), 0.0, u / 2
    if art == SIGNALE[3]:
        return u * math.sqrt(d), u * d, u * d
    if art == SIGNALE[4]:
        return u / 2, u / math.pi, u / math.pi
    return u / math.sqrt(2), 2 * u / math.pi, 2 * u / math.pi


def _signalform(w):
    u, art = w["u"], w["art"]
    if u is None:
        raise RechnerFehler("Scheitelwert Û eingeben")
    d = _std(w["d"], 0.5)
    if not 0 < d <= 1:
        raise RechnerFehler("Tastgrad zwischen 1 und 100 %")
    eff, mittel, gl = _kennwerte(art, u, d)
    anzeige_mittelwert = 1.1107 * gl                       # Sinus-kalibriertes Gleichrichtwert-Messgerät
    fehler = (anzeige_mittelwert / eff - 1) * 100 if eff else 0
    if abs(fehler) < 0.05:
        fehler = 0.0                                        # keine "-0.0 %" anzeigen
    return [f"Effektivwert (RMS)   U_eff = {fmt(eff, 'spannung')}",
            f"Arithm. Mittelwert   Ū = {fmt(mittel, 'spannung')}   (das zeigt der DC-Bereich)",
            f"Gleichrichtwert      |Ū| = {fmt(gl, 'spannung')}",
            f"Crestfaktor Û/U_eff = {u / eff:.3f}   ·   Formfaktor U_eff/|Ū| = {eff / gl:.3f}",
            f"Multimeter OHNE True RMS (AC) zeigt ≈ {fmt(anzeige_mittelwert, 'spannung')}  "
            f"→ Fehler {fehler:+.1f} %" + ("  ✅ stimmt hier (Formfaktor wie Sinus)" if abs(fehler) < 0.5 else "  ⚠ → True RMS nötig")]


def signalform(master):
    return FormelRechner(
        master, "Effektivwert & Co.", "Kenngrössen verschiedener Signalformen",
        felder=[("art", "Signalform", "auswahl", {"werte": SIGNALE}),
                ("u", "Scheitelwert Û", "spannung", {"platzhalter": "z.B. 10"}),
                ("d", "Tastgrad (nur PWM)", "prozent", {"platzhalter": "50"})],
        berechnen=_signalform, formel="Sinus: U_eff = Û/√2 ≈ 0.707·Û     Crestfaktor = Û/U_eff")


# =============================================================================
# 3) MULTIMETER
# =============================================================================
def _messbereich(w):
    ri, iv = w["Ri"], w["Iv"]
    if ri is None or iv is None:
        raise RechnerFehler("Innenwiderstand Ri und Vollausschlag-Strom des Messwerks eingeben")
    zeilen = [f"Messwerk allein: Vollausschlag bei U = Ri · Iv = {fmt(ri * iv, 'spannung')}",
              f"Kennwert: {1 / iv:,.0f} Ω/V".replace(",", "'")]
    if w["U"] is not None:
        rv = w["U"] / iv - ri
        if rv < 0:
            raise RechnerFehler("Neuer Spannungsbereich ist kleiner als der des Messwerks")
        zeilen.append(f"Spannungsbereich {fmt(w['U'], 'spannung')}: Vorwiderstand Rv = U/Iv − Ri = {fmt(rv, 'widerstand')}")
    if w["I"] is not None:
        if w["I"] <= iv:
            raise RechnerFehler("Neuer Strombereich muss grösser als der Vollausschlag sein")
        rs = ri * iv / (w["I"] - iv)
        zeilen.append(f"Strombereich {fmt(w['I'], 'strom')}: Shunt Rs = Ri · Iv / (I − Iv) = {fmt(rs, 'widerstand')}")
    if w["U"] is None and w["I"] is None:
        zeilen.append("Neuen Spannungs- oder Strombereich eingeben")
    return zeilen


def messbereich(master):
    return FormelRechner(
        master, "Messbereichserweiterung", "Vorwiderstand (Spannung) bzw. Shunt (Strom) für ein Messwerk",
        felder=[("Ri", "Messwerk Ri", "widerstand"), ("Iv", "Vollausschlag Iv", "strom", {"einheit": "µA"}),
                ("U", "Neuer U-Bereich", "spannung", {"platzhalter": "optional"}),
                ("I", "Neuer I-Bereich", "strom", {"platzhalter": "optional"})],
        berechnen=_messbereich, formel="Rv = U / Iv − Ri     Rs = Ri · Iv / (I − Iv)")


def _belastung_u(w):
    uq, rq = w["Uq"], w["Rq"]
    if uq is None or rq is None:
        raise RechnerFehler("Quellenspannung und Innenwiderstand der Quelle eingeben")
    ri = _std(w["Ri"], 10e6)
    anzeige = uq * ri / (rq + ri)
    fehler = (anzeige / uq - 1) * 100
    zeilen = [f"Anzeige = Uq · Ri / (Rq + Ri) = {fmt(anzeige, 'spannung')}",
              f"Belastungsfehler: {fehler:+.3g} %   (Messgerät Ri = {fmt(ri, 'widerstand')})"]
    if abs(fehler) > 1:
        zeilen.append("⚠ Quelle zu hochohmig für dieses Messgerät → Impedanzwandler (OPV) oder Messgerät mit höherem Ri")
    zeilen.append("Faustregel: Ri des Messgeräts ≥ 100 × Innenwiderstand der Quelle → Fehler < 1 %")
    return zeilen


def belastung_u(master):
    return FormelRechner(
        master, "Belastungsfehler Spannungsmessung", "Das Messgerät bildet mit der Quelle einen Spannungsteiler",
        felder=[("Uq", "Leerlaufspannung Uq", "spannung"),
                ("Rq", "Innenwiderstand Quelle", "widerstand", {"einheit": "kΩ"}),
                ("Ri", "Ri Messgerät", "widerstand", {"einheit": "MΩ", "platzhalter": "10"})],
        berechnen=_belastung_u, formel="U_Anzeige = Uq · Ri / (Rq + Ri)")


def _buerde_i(w):
    u, r = w["U"], w["R"]
    if u is None or r is None:
        raise RechnerFehler("Spannung und Widerstand des Stromkreises eingeben")
    if w["Rm"] is not None:
        rm = w["Rm"]
    elif w["Ub"] is not None and w["Iv"] is not None:
        rm = w["Ub"] / w["Iv"]
    else:
        raise RechnerFehler("Widerstand des Strommessers ODER Bürdenspannung + Bereichsendwert eingeben")
    i_ohne, i_mit = u / r, u / (r + rm)
    return [f"Strom ohne Messgerät: {fmt(i_ohne, 'strom')}",
            f"Strom mit Messgerät ({fmt(rm, 'widerstand')}): {fmt(i_mit, 'strom')}",
            f"Messfehler: {(i_mit / i_ohne - 1) * 100:+.3g} %   ·   Spannungsfall am Messgerät {fmt(i_mit * rm, 'spannung')}",
            "Bei kleinen Spannungen (z.B. 3.3-V-Schaltungen) kann diese Bürdenspannung die Schaltung stören!"]


def buerde_i(master):
    return FormelRechner(
        master, "Einfluss des Strommessers", "Der Strommesser liegt in Reihe und bremst den Strom etwas",
        felder=[("U", "Spannung im Kreis", "spannung"), ("R", "Widerstand im Kreis", "widerstand"),
                ("Rm", "Ri Strommesser", "widerstand", {"platzhalter": "oder unten"}),
                ("Ub", "Bürdenspannung", "spannung", {"einheit": "mV", "platzhalter": "z.B. 200"}),
                ("Iv", "… beim Bereichsendwert", "strom", {"einheit": "mA", "platzhalter": "z.B. 200"})],
        berechnen=_buerde_i, formel="R_Messgerät = Bürdenspannung / Bereichsendwert")


# =============================================================================
# 4) OSZILLOSKOP
# =============================================================================
def _oszi(w):
    b = w["B"]
    if b is None:
        raise RechnerFehler("Bandbreite des Oszilloskops eingeben")
    tr_o = 0.35 / b
    zeilen = [f"Eigene Anstiegszeit: tr ≈ 0.35 / B = {fmt(tr_o, 'zeit')}",
              f"Empfohlene Abtastrate: ≥ 2.5 … 5 × B = {fmt(2.5 * b, 'frequenz')} … {fmt(5 * b, 'frequenz')}  (Samples/s)"]
    if w["f"] is not None:
        amp = 1 / math.sqrt(1 + (w["f"] / b) ** 2)
        zeilen.append(f"Sinus mit {fmt(w['f'], 'frequenz')}: Amplitude wird ≈ {(1 - amp) * 100:.1f} % zu klein angezeigt")
        if w["f"] > b / 3:
            zeilen.append(f"⚠ Faustregel: B ≥ 3 … 5 × Signalfrequenz → mindestens {fmt(3 * w['f'], 'frequenz')}")
    if w["tr"] is not None:
        tr_m = math.hypot(w["tr"], tr_o)
        zeilen.append(f"Signal-Anstiegszeit {fmt(w['tr'], 'zeit')} wird angezeigt als ≈ {fmt(tr_m, 'zeit')} "
                      f"({(tr_m / w['tr'] - 1) * 100:+.0f} %)")
    return zeilen


def oszi(master):
    return FormelRechner(
        master, "Oszilloskop: reicht die Bandbreite?", "Bandbreite von Oszilloskop UND Tastkopf beachten",
        felder=[("B", "Bandbreite B", "frequenz", {"einheit": "MHz"}),
                ("f", "Signalfrequenz (opt.)", "frequenz", {"einheit": "MHz", "platzhalter": "optional"}),
                ("tr", "Anstiegszeit Signal (opt.)", "zeit", {"einheit": "ns", "platzhalter": "optional"})],
        berechnen=_oszi, formel="tr ≈ 0.35 / B     tr,gemessen ≈ √(tr,Signal² + tr,Oszi²)")


# =============================================================================
# 5) TEMPERATURSENSOREN
# =============================================================================
_A, _B, _C = 3.9083e-3, -5.775e-7, -4.183e-12          # IEC 60751
PT_BEREICH = (-200.0, 850.0)                           # °C, für diesen Bereich gilt die Norm


def pt_widerstand(t, r0):
    if t >= 0:
        return r0 * (1 + _A * t + _B * t * t)
    return r0 * (1 + _A * t + _B * t * t + _C * (t - 100) * t ** 3)


def pt_temperatur(r, r0):
    if r >= r0:                                          # quadratische Gleichung (T ≥ 0 °C)
        return (-_A + math.sqrt(_A * _A - 4 * _B * (1 - r / r0))) / (2 * _B)
    t = (r / r0 - 1) / _A                                # Newton-Verfahren für T < 0 °C
    for _ in range(20):
        f = pt_widerstand(t, r0) - r
        ableitung = r0 * (_A + 2 * _B * t + _C * (4 * t ** 3 - 300 * t * t))
        t -= f / ableitung
    return t


def _pt100(w):
    r0 = 1000.0 if w["typ"].startswith("Pt1000") else 100.0
    if (w["T"] is None) == (w["R"] is None):
        raise RechnerFehler("Entweder Temperatur ODER Widerstand eingeben")
    t_min, t_max = PT_BEREICH
    if w["T"] is not None:
        if not t_min <= w["T"] <= t_max:
            raise RechnerFehler(f"Pt-Sensoren sind nach IEC 60751 nur für {t_min:g} … {t_max:g} °C definiert")
        t, r = w["T"], pt_widerstand(w["T"], r0)
        zeilen = [f"R({t:g} °C) = {fmt(r, 'widerstand', 5)}"]
    else:
        r_min, r_max = pt_widerstand(t_min, r0), pt_widerstand(t_max, r0)
        if not r_min <= w["R"] <= r_max:
            raise RechnerFehler(f"R ausserhalb {fmt(r_min, 'widerstand')} … {fmt(r_max, 'widerstand')} "
                                f"(= {t_min:g} … {t_max:g} °C) – Sensor defekt oder Pt100/Pt1000 verwechselt?")
        r, t = w["R"], pt_temperatur(w["R"], r0)
        zeilen = [f"T = {t:.2f} °C  bei R = {fmt(r, 'widerstand', 5)}"]
    empf = r0 * 0.00385
    zeilen.append(f"Empfindlichkeit ≈ {empf:g} Ω/K   (Pt100: 0.385 Ω/K)")
    if w["Rl"] is not None:
        fehler_k = 2 * w["Rl"] / empf
        zeilen.append(f"2-Leiter-Schaltung mit {fmt(w['Rl'], 'widerstand')} je Ader: "
                      f"+{fehler_k:.2f} K zu viel → 3- oder 4-Leiter-Schaltung verwenden")
    return zeilen


def pt100(master):
    return FormelRechner(
        master, "Pt100 / Pt1000", "Widerstand ↔ Temperatur nach IEC 60751 (Callendar-Van Dusen)",
        felder=[("typ", "Sensor", "auswahl", {"werte": ["Pt100 (100 Ω bei 0 °C)", "Pt1000 (1000 Ω bei 0 °C)"]}),
                ("T", "Temperatur", "temperatur", {"platzhalter": "oder R"}),
                ("R", "… oder Widerstand", "widerstand", {"platzhalter": "oder T"}),
                ("Rl", "Leitungswiderstand je Ader (opt.)", "widerstand", {"platzhalter": "optional"})],
        berechnen=_pt100, formel="R(T) = R0 · (1 + A·T + B·T²)  für T ≥ 0 °C,  A = 3.9083·10⁻³, B = −5.775·10⁻⁷")


def _ntc(w):
    r25, b = w["R25"], w["B"]
    if r25 is None or b is None:
        raise RechnerFehler("R25 und B-Wert eingeben")
    t25 = 298.15
    if r25 <= 0 or b <= 0:
        raise RechnerFehler("R25 und B-Wert müssen grösser als 0 sein")
    if (w["T"] is None) == (w["R"] is None):
        raise RechnerFehler("Entweder Temperatur ODER Widerstand eingeben")
    if w["T"] is not None:
        if w["T"] <= -273.15:
            raise RechnerFehler("Temperatur muss über dem absoluten Nullpunkt (−273.15 °C) liegen")
        tk = w["T"] + 273.15
        r = r25 * math.exp(b * (1 / tk - 1 / t25))
        zeilen = [f"R({w['T']:g} °C) = {fmt(r, 'widerstand')}"]
    else:
        r = w["R"]
        if r <= 0:
            raise RechnerFehler("Widerstand muss grösser als 0 sein")
        nenner = 1 / t25 + math.log(r / r25) / b          # = 1 / T in 1/K
        if nenner <= 0:
            raise RechnerFehler("Widerstand passt nicht zu R25/B (ergäbe keine gültige Temperatur)")
        tk = 1 / nenner
        zeilen = [f"T = {tk - 273.15:.2f} °C  bei R = {fmt(r, 'widerstand')}"]
    zeilen.append(f"Empfindlichkeit: {-b / tk ** 2 * 100:.2f} %/K  (sehr gross, aber stark nichtlinear)")
    zeilen.append("B-Wert-Gleichung ist eine Näherung – ausserhalb ca. 0 … 100 °C mehrere K Abweichung möglich")
    return zeilen


def ntc(master):
    return FormelRechner(
        master, "NTC (Heissleiter)", "Widerstand ↔ Temperatur mit dem B-Wert aus dem Datenblatt",
        felder=[("R25", "R bei 25 °C", "widerstand", {"einheit": "kΩ", "platzhalter": "z.B. 10"}),
                ("B", "B-Wert", "zahl", {"platzhalter": "z.B. 3950 (K)"}),
                ("T", "Temperatur", "temperatur", {"platzhalter": "oder R"}),
                ("R", "… oder Widerstand", "widerstand", {"einheit": "kΩ", "platzhalter": "oder T"})],
        berechnen=_ntc, formel="R(T) = R25 · e^(B · (1/T − 1/T25)),  T in Kelvin")


THERMO = {"Typ K (NiCr-Ni)": 41e-6, "Typ J (Fe-CuNi)": 52e-6, "Typ T (Cu-CuNi)": 43e-6,
          "Typ N (NiCrSi-NiSi)": 27e-6, "Typ S (PtRh10-Pt)": 6.5e-6}


def _thermo(w):
    s = THERMO[w["typ"]]
    t_v = _std(w["Tv"], 25.0)
    if w["U"] is not None:
        t = t_v + w["U"] / s
        zeilen = [f"Messstelle ≈ {t:.1f} °C  (Vergleichsstelle {t_v:g} °C + {fmt(w['U'], 'spannung')} / {s * 1e6:g} µV/K)"]
    elif w["T"] is not None:
        u = (w["T"] - t_v) * s
        zeilen = [f"Thermospannung ≈ {fmt(u, 'spannung')}  bei {w['T']:g} °C (Vergleichsstelle {t_v:g} °C)"]
    else:
        raise RechnerFehler("Thermospannung ODER Temperatur der Messstelle eingeben")
    zeilen.append("Lineare Näherung! Genaue Werte: Grundwerttabellen nach IEC 60584")
    zeilen.append("Das Thermoelement misst nur die DIFFERENZ zur Vergleichsstelle (Klemmenstelle)")
    return zeilen


def thermoelement(master):
    return FormelRechner(
        master, "Thermoelement (Näherung)", "Nur wenige µV pro Kelvin – Vergleichsstelle nicht vergessen",
        felder=[("typ", "Typ", "auswahl", {"werte": list(THERMO)}),
                ("U", "Thermospannung", "spannung", {"einheit": "mV", "platzhalter": "oder T"}),
                ("T", "… oder Temperatur Messstelle", "temperatur", {"platzhalter": "oder U"}),
                ("Tv", "Vergleichsstelle", "temperatur", {"platzhalter": "25"})],
        berechnen=_thermo, formel="U_th ≈ S · (T_Mess − T_Vergleich)")


# =============================================================================
# 6) BRÜCKE & DMS
# =============================================================================
def _bruecke(w):
    ue, r1, r2, r3, r4 = w["Ue"], w["R1"], w["R2"], w["R3"], w["R4"]
    if None in (r1, r2, r3):
        raise RechnerFehler("Mindestens R1, R2 und R3 eingeben")
    if r4 is None:
        return [f"Abgleich (Ua = 0) bei R4 = R3 · R2 / R1 = {fmt(r3 * r2 / r1, 'widerstand')}",
                "Abgleichbedingung: R1 / R2 = R3 / R4"]
    if ue is None:
        raise RechnerFehler("Für die Ausgangsspannung auch Ue eingeben")
    ua = ue * (r2 / (r1 + r2) - r4 / (r3 + r4))
    return [f"Ua = Ue · (R2/(R1+R2) − R4/(R3+R4)) = {fmt(ua, 'spannung')}",
            f"= {ua / ue * 1000:.4g} mV/V",
            "Abgeglichen (Ua ≈ 0)" if abs(ua) < 1e-9 * abs(ue) + 1e-12 else f"Abgleichwert R4 wäre {fmt(r3 * r2 / r1, 'widerstand')}"]


def bruecke(master):
    return FormelRechner(
        master, "Wheatstone-Brücke", "Links R1 (oben) / R2 (unten), rechts R3 (oben) / R4 (unten), Ua zwischen den Mitten",
        felder=[("Ue", "Speisespannung Ue", "spannung"), ("R1", "R1", "widerstand"), ("R2", "R2", "widerstand"),
                ("R3", "R3", "widerstand"), ("R4", "R4 (leer = Abgleich)", "widerstand", {"platzhalter": "optional"})],
        berechnen=_bruecke, formel="Ua = Ue · (R2/(R1+R2) − R4/(R3+R4))     Abgleich: R1/R2 = R3/R4")


def _dms(w):
    ue, eps = w["Ue"], w["eps"]
    if ue is None or eps is None:
        raise RechnerFehler("Speisespannung und Dehnung eingeben")
    k = _std(w["k"], 2.0)
    n = {"Viertelbrücke (1 aktiver DMS)": 1, "Halbbrücke (2 aktive DMS)": 2, "Vollbrücke (4 aktive DMS)": 4}[w["art"]]
    e = eps * 1e-6
    ua = ue * k * e * n / 4
    zeilen = [f"Ua ≈ Ue · k · ε · n/4 = {fmt(ua, 'spannung')}   ({ua / ue * 1000:.4g} mV/V)"]
    if w["R"] is not None:
        zeilen.append(f"Widerstandsänderung je DMS: ΔR = R · k · ε = {fmt(w['R'] * k * e, 'widerstand')}")
    zeilen.append("Sehr kleine Signale → Instrumentenverstärker nötig. Halb-/Vollbrücke kompensiert auch die Temperatur.")
    return zeilen


def dms(master):
    return FormelRechner(
        master, "Dehnungsmessstreifen (DMS)", "Dehnung in µm/m (= µε)",
        felder=[("art", "Schaltung", "auswahl", {"werte": ["Viertelbrücke (1 aktiver DMS)", "Halbbrücke (2 aktive DMS)",
                                                             "Vollbrücke (4 aktive DMS)"]}),
                ("Ue", "Speisespannung Ue", "spannung", {"platzhalter": "z.B. 5"}),
                ("eps", "Dehnung ε (µm/m)", "zahl", {"platzhalter": "z.B. 1000"}),
                ("k", "k-Faktor", "zahl", {"platzhalter": "2"}),
                ("R", "R des DMS (opt.)", "widerstand", {"platzhalter": "z.B. 350"})],
        berechnen=_dms, formel="ΔR/R = k · ε     Ua ≈ Ue · k · ε · n / 4")


# =============================================================================
# 7) AD-WANDLER
# =============================================================================
def _adc(w):
    n, uref = w["n"], w["Uref"]
    if n is None or uref is None:
        raise RechnerFehler("Auflösung in Bit und Referenzspannung eingeben")
    if n != int(n) or not 1 <= n <= 32:
        raise RechnerFehler("Bitzahl: ganze Zahl zwischen 1 und 32")
    n = int(n)
    stufen = 2 ** n
    lsb = uref / stufen
    zeilen = [f"{stufen:,} Stufen".replace(",", "'") + f"   ·   1 LSB = Uref / 2ⁿ = {fmt(lsb, 'spannung')}",
              f"Quantisierungsfehler: ± ½ LSB = ± {fmt(lsb / 2, 'spannung')}",
              f"Idealer Signal-Rausch-Abstand: 6.02 · n + 1.76 = {6.02 * n + 1.76:.1f} dB"]
    if w["Uin"] is not None:
        code = min(stufen - 1, max(0, int(w["Uin"] / lsb)))
        zeilen.append(f"Eingang {fmt(w['Uin'], 'spannung')} → Code {code}  (0x{code:X}, binär {code:0{n}b})")
    if w["fmax"] is not None:
        zeilen.append(f"Abtasttheorem: fs > 2 · fmax = {fmt(2 * w['fmax'], 'frequenz')}  "
                      f"(praktisch 2.5 … 10 × → {fmt(2.5 * w['fmax'], 'frequenz')} … {fmt(10 * w['fmax'], 'frequenz')})")
        zeilen.append("Vor dem ADC ein Tiefpass (Anti-Aliasing-Filter), sonst erscheinen höhere Frequenzen gespiegelt!")
    return zeilen


def adc(master):
    return FormelRechner(
        master, "AD-Wandler", "Auflösung, LSB und nötige Abtastrate",
        felder=[("n", "Auflösung (Bit)", "zahl", {"platzhalter": "z.B. 12"}),
                ("Uref", "Referenzspannung", "spannung", {"platzhalter": "z.B. 3.3"}),
                ("Uin", "Eingangsspannung (opt.)", "spannung", {"platzhalter": "optional"}),
                ("fmax", "Höchste Signalfrequenz (opt.)", "frequenz", {"platzhalter": "optional"})],
        berechnen=_adc, formel="LSB = Uref / 2ⁿ     SNR_ideal = 6.02·n + 1.76 dB     fs > 2·fmax")


# =============================================================================
# 8) DURCHFLUSS (magnetisch-induktiv)
# =============================================================================
def _mid(w):
    d = w["D"]
    if d is None:
        raise RechnerFehler("Nennweite (Innendurchmesser) eingeben")
    a = math.pi * d * d / 4
    if anzahl_gegeben(w, "Q", "v") != 1:
        raise RechnerFehler("Entweder Volumenstrom ODER Fliessgeschwindigkeit eingeben")
    v = w["v"] if w["v"] is not None else w["Q"] / a
    q = v * a
    zeilen = [f"Querschnitt A = π·D²/4 = {a * 1e4:.4g} cm²",
              f"Fliessgeschwindigkeit v = {v:.3g} m/s   ·   Volumenstrom Q = {q * 3600:.4g} m³/h = {q * 60000:.4g} l/min"]
    if w["B"] is not None:
        u = w["B"] * d * v
        zeilen.append(f"Induzierte Spannung U = B · D · v ≈ {fmt(u, 'spannung')}  (idealisiert, ohne Gerätefaktor)")
    if v < 0.3:
        zeilen.append("Sehr kleine Geschwindigkeit → Messsignal klein, kleinere Nennweite prüfen")
    elif v > 10:
        zeilen.append("Sehr hohe Geschwindigkeit → Druckverlust/Verschleiss, grössere Nennweite prüfen")
    zeilen.append("Voraussetzung: leitfähiges Medium (Datenblatt: Mindestleitfähigkeit)")
    return zeilen


def mid(master):
    return FormelRechner(
        master, "Magnetisch-induktiver Durchfluss", "Umrechnung Volumenstrom ↔ Geschwindigkeit und Messspannung",
        felder=[("D", "Innendurchmesser D", "laenge", {"einheit": "mm", "platzhalter": "z.B. 50"}),
                ("Q", "Volumenstrom Q", "volumenstrom", {"platzhalter": "oder v"}),
                ("v", "… oder Geschwindigkeit v", "geschwindigkeit", {"platzhalter": "oder Q"}),
                ("B", "Flussdichte B (opt.)", "flussdichte", {"einheit": "mT", "platzhalter": "optional"})],
        berechnen=_mid, formel="Q = v · A     U = B · D · v   (Faraday'sches Induktionsgesetz)")


# =============================================================================
# REGISTRIERUNG (IDs müssen sich von denen der Bauteile unterscheiden)
# =============================================================================
RECHNER = {
    "statistik": statistik, "dmm_genauigkeit": dmm_genauigkeit, "fehlerfortpflanzung": fehlerfortpflanzung,
    "signalform": signalform, "messbereich": messbereich, "belastung_u": belastung_u, "buerde_i": buerde_i,
    "oszi": oszi, "pt100": pt100, "ntc": ntc, "thermoelement": thermoelement, "bruecke": bruecke,
    "dms": dms, "adc": adc, "mid": mid, "abtastung": AbtastGrafik,
}
