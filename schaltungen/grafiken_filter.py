# =============================================================================
# schaltungen/grafiken_filter.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE der Filter 2. Ordnung.
# Spannung = blau, Strom = rot, Messpunkte = orange.
#
#   LcFilterSchaltung      LC-Tiefpass mit Last (passiv)
#   SchwingkreisSchaltung  RLC-Reihenschwingkreis als Bandpass oder Bandsperre (passiv, gleiche Zeichnung)
#   SallenKeySchaltung     aktiver Tief- und Hochpass nach Sallen-Key (OPV als Spannungsfolger)
#
# Beide zeigen rechts oben den Betragsgang (Bode, ±2 Dekaden um f0) und darunter wahlweise
# Sinus bei f (Eingang gestrichelt, Ausgang blau) oder die Sprungantwort (Überschwingen bei hohem Q).
#
# Rechnung: schaltungen/filter_mathe.py
# Der RC-Filter 1. Ordnung steht in schaltungen/grafiken_rc.py (RcFilterSchaltung) - nicht kopiert.
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_lc_filter")
# =============================================================================

import math

from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, WARN              # -> bauteile/grafiken/schaltplan.py
from schaltungen import filter_mathe as fm                               # -> schaltungen/filter_mathe.py
from schaltungen.grafiken import _r, _u                                  # -> schaltungen/grafiken.py
from schaltungen.grafiken_dioden import _MitDiagramm                     # -> schaltungen/grafiken_dioden.py
from schaltungen.grafiken_rc import LOG_C, LOG_F, LOG_R, _f, _punkt, _t  # -> schaltungen/grafiken_rc.py

LOG_L = {"einheit": "mH", "log": True, "grenzen": (1e-9, 100.0)}
U_E = ("ue", "Eingang û_e", "spannung", 0.01, 20.0, 1.0, {"einheit": "V", "grenzen": (1e-4, 1000)})
SPRUNG = [("sprung", "Sprungantwort statt Sinus")]
DB_MARKEN = [(20.0, "+20 dB"), (0.0, "0 dB"), (-3.0, "−3 dB"), (-20.0, "−20 dB"), (-40.0, "−40 dB"), (-60.0, "−60 dB")]
DB_UNTEN = -85.0                                   # 2 Dekaden · 40 dB = −80 dB am Rand


def _l(wert):
    return fmt(wert, "induktivitaet", 3)


def _c(wert):
    return fmt(wert, "kapazitaet", 3)


class _Filter2Basis(_MitDiagramm):
    """Gemeinsam: aus art, f0, Q werden Frequenzgang, Kennwerte, Sprungantwort und Diagramme."""
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.4, 10)
    SEITENVERHAELTNIS = 0.5
    SCHALTER = SPRUNG

    def _f2_rechnen(self, e, art, w):
        e["art"] = art
        e.update(fm.kennwerte(art, e["f0"], e["q"]))
        e.update(fm.frequenzgang(art, e["f0"], e["q"], w["f"]))
        e["u_a"] = e["betrag"] * w["ue"]
        phi = math.radians(e["phase"])
        e["kurve_ein"] = [(k / 200, w["ue"] * math.sin(4 * math.pi * k / 200)) for k in range(201)]
        e["kurve_aus"] = [(k / 200, e["u_a"] * math.sin(4 * math.pi * k / 200 + phi)) for k in range(201)]
        e["sprung"] = fm.sprungantwort(art, e["f0"], e["q"])
        return e

    def _f2_diagramme(self, p, w, e):
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.2, 22.8
        spitze = max(y for _t, y in fm.bode_kurve(e["art"], e["q"]))
        oben = max(5.0, spitze + 4.0)
        p.diagramm(gx0, 1.0, gx1, 4.4, [(fm.bode_kurve(e["art"], e["q"]), SPANNUNG, None, False)], DB_UNTEN, oben,
                   "|H| in dB über f (log)", [m for m in DB_MARKEN if m[0] <= oben], zeit_text="")
        p.text((gx0 + gx1) / 2, 4.65, "f0/100   ·   f0/10   ·   f0   ·   10·f0   ·   100·f0", "n", klein=True,
               farbe=p.leise)
        _punkt(p, gx0, 1.0, gx1, 4.4, fm.bode_position(w["f"], e["f0"]), max(e["db"], DB_UNTEN), DB_UNTEN, oben)
        if w.get("sprung"):
            s = e["sprung"]
            ein = [(0.0, 0.0), (0.0, w["ue"]), (1.0, w["ue"])]
            aus = [(t, y * w["ue"]) for t, y in s["kurve"]]
            werte = [y for _t, y in aus]
            lo, hi = min(0.0, min(werte)), max(w["ue"], max(werte))
            rand = 0.1 * (hi - lo)
            p.diagramm(gx0, 5.8, gx1, 9.4, [(ein, p.leise, 1, True), (aus, SPANNUNG, None, False)], lo - rand,
                       hi + rand, "Sprung am Eingang (gestrichelt)  ·  u_a (blau)", einheit="spannung",
                       t_ende=s["dauer"])
        else:
            g = max(w["ue"], e["u_a"]) * 1.15
            p.diagramm(gx0, 5.8, gx1, 9.4, [(e["kurve_ein"], p.leise, 1, True), (e["kurve_aus"], SPANNUNG, None, False)],
                       -g, g, "u_e (gestrichelt)  ·  u_a (blau)  ·  2 Perioden", einheit="spannung",
                       t_ende=2 / w["f"])

    def _f2_info(self, w, e, kopf):
        zeilen = [kopf,
                  f"Bei f = {_f(w['f'])}:  |H| = {e['betrag']:.3g} ({e['db']:.1f} dB)   ·   û_a = {_u(e['u_a'])}   ·   "
                  f"φ = {e['phase']:+.0f}°"]
        if e["art"] in ("Tiefpass", "Hochpass"):
            teil = f"−3 dB bei {_f(e['f_3db'])}"
            if e["f_max"]:
                teil += (f"   ·   Überhöhung {20 * math.log10(e['ueberhoehung']):.1f} dB bei {_f(e['f_max'])}")
            zeilen.append(teil + f"   ·   {e['charakter']}")
        else:
            zeilen.append(f"Bandbreite B = f0 / Q = {_f(e['bandbreite'])}   ·   −3 dB bei {_f(e['f_unten'])} und "
                          f"{_f(e['f_oben'])}")
        s = e["sprung"]
        if w.get("sprung") and s["ueberschwingen"] is not None:
            zeilen.append(f"Sprungantwort: Überschwingen {s['ueberschwingen']:.1f} %"
                          + (f", eingeschwungen (±2 %) nach {_t(s['einschwingzeit'])}" if s["einschwingzeit"] else ""))
        farbe = WARN if e["q"] > 2 else OK
        if e["q"] > 2:
            zeilen.append(f"⚠ Hohe Güte Q = {e['q']:.2g}: starke Resonanz – bei f0 kann û_a ein Vielfaches von û_e sein")
        return zeilen, farbe


# =============================================================================
# PASSIV: LC-TIEFPASS, RLC-BANDPASS, RLC-BANDSPERRE
# =============================================================================
class LcFilterSchaltung(_Filter2Basis):
    TITEL = "🔌 LC-Tiefpass (interaktiv)"
    UNTERTITEL = "Spule und Kondensator: −40 dB pro Dekade – die Last R_L bestimmt die Güte Q und damit die Überhöhung"
    VARIANTEN = []
    REGLER = [("l", "Induktivität L", "induktivitaet", 1e-6, 1.0, 1e-3, LOG_L),
              ("c", "Kapazität C", "kapazitaet", 1e-9, 100e-6, 1e-6, LOG_C),
              ("r", "Last R_L", "widerstand", 1.0, 100e3, 33.0, {"einheit": "Ω", "log": True,
                                                                                 "grenzen": (0.01, 100e6)}),
              ("f", "Signalfrequenz f", "frequenz", 10.0, 1e6, 5e3, LOG_F),
              U_E]
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Spule und Kondensator haben gegenläufige Blindwiderstände (X_L = 2π·f·L steigt, "
        "X_C = 1/(2π·f·C) sinkt). Bei f0 = 1 / (2π·√(L·C)) sind beide gleich gross (Resonanz). LC-TIEFPASS: Über f0 "
        "fällt der Ausgang mit 40 dB pro Dekade – doppelt so steil wie ein RC-Glied. Die Last R bestimmt die Güte "
        "Q = R · √(C/L): Ohne genügend Last schwingt das Filter bei f0 auf (Überhöhung, Nachschwingen bei einem "
        "Sprung). BANDPASS: Ausgang am R – nur Frequenzen um f0 kommen durch, Bandbreite B = f0 / Q. BANDSPERRE: "
        "Ausgang an L+C – genau f0 wird unterdrückt (z.B. 50-Hz-Brumm). Modell: ideale Bauteile, Quelle ohne "
        "Innenwiderstand.")

    def sk_rechnen(self, w, v):
        if v is None:
            e = fm.lc_tiefpass(w["l"], w["c"], w["r"])
            art = "Tiefpass"
        else:
            e = fm.rlc_reihe(w["r"], w["l"], w["c"])
            art = "Bandpass" if v == "RLC-Bandpass" else "Bandsperre"
        e["x_l"] = 2 * math.pi * w["f"] * w["l"]
        e["x_c"] = 1 / (2 * math.pi * w["f"] * w["c"])
        return self._f2_rechnen(e, art, w)

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_a, y_o, y_u = 1.8, 11.0, 2.4, 8.6
        p.wechselquelle(x_q, y_o + 1.8, y_u - 1.8, "u_e", f"û = {_u(w['ue'])}")
        p.leitung((x_q, y_o + 1.8), (x_q, y_o))
        p.leitung((x_q, y_u - 1.8), (x_q, y_u), (x_a, y_u))
        if v is None:
            x_k, x_r = 6.4, 8.8
            p.spule(x_q, y_o, x_k, y_o, "L", _l(w["l"]))
            p.kondensator(x_k, y_o, y_u, "C", _c(w["c"]), seite="links")
            p.widerstand(x_r, y_o, x_r, y_u, "R_L", _r(w["r"]), seite="links")
            for x in (x_k, x_r):
                p.knoten(x, y_o)
                p.knoten(x, y_u)
            p.leitung((x_k, y_o), (x_a, y_o))
        elif v == "RLC-Bandpass":
            x_k = 8.6
            p.spule(x_q, y_o, 4.8, y_o, "L", _l(w["l"]), laenge=1.4)
            p.kondensator_waagrecht(4.8, 7.4, y_o, "C", _c(w["c"]))
            p.leitung((7.4, y_o), (x_a, y_o))
            p.widerstand(x_k, y_o, x_k, y_u, "R", _r(w["r"]), seite="links")
            p.knoten(x_k, y_o)
            p.knoten(x_k, y_u)
        else:
            x_k, y_m = 6.6, (y_o + y_u) / 2
            p.widerstand(x_q, y_o, x_k, y_o, "R", _r(w["r"]))
            p.spule(x_k, y_o, x_k, y_m, "L", _l(w["l"]), seite="links", laenge=1.4)
            p.kondensator(x_k, y_m, y_u, "C", _c(w["c"]), seite="links")
            p.knoten(x_k, y_o)
            p.knoten(x_k, y_u)
            p.leitung((x_k, y_o), (x_a, y_o))
        p.anschluss(x_a, y_o)
        p.anschluss(x_a, y_u)
        p.spannung(x_a, y_o + 0.5, y_u - 0.5, f"û_a = {_u(e['u_a'])}")
        p.messpunkt(x_a - 0.9, y_o, "M1", seite="rechts")
        p.text(x_q - 0.6, y_u + 0.85, f"f0 = {_f(e['f0'])}   ·   Q = {e['q']:.3g}", "w", fett=True)
        self._f2_diagramme(p, w, e)

    def sk_info(self, w, e, v):
        kopf = (f"f0 = 1 / (2π·√(L·C)) = {_f(e['f0'])}   ·   Z0 = √(L/C) = {_r(e['z0'])}   ·   Q = "
                + ("R_L / Z0" if v is None else "Z0 / R") + f" = {e['q']:.3g}   ·   "
                f"bei f: X_L = {_r(e['x_l'])}, X_C = {_r(e['x_c'])}")
        return self._f2_info(w, e, kopf)


# =============================================================================
# AKTIV: SALLEN-KEY
# =============================================================================
class SallenKeySchaltung(_Filter2Basis):
    RASTER_SCHMAL = (13.4, 10)
    TITEL = "🔌 Aktives Filter 2. Ordnung: Sallen-Key (interaktiv)"
    UNTERTITEL = "Ohne Spule: OPV als Spannungsfolger, zwei R und zwei C – Q über das Verhältnis der Bauteile einstellen"
    VARIANTEN = ["Tiefpass", "Hochpass"]
    # Butterworth um 1 kHz mit Normwerten (Tiefpass: gleiche R, Hochpass: gleiche C)
    STARTWERTE = {"Tiefpass": {"r1": 10e3, "r2": 10e3, "c1": 22e-9, "c2": 12e-9},
                  "Hochpass": {"r1": 11e3, "r2": 22e3, "c1": 10e-9, "c2": 10e-9}}
    REGLER = [("r1", "R1", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("r2", "R2", "widerstand", 1e3, 1e6, 10e3, LOG_R),
              ("c1", "C1 (Rückkopplung)", "kapazitaet", 100e-12, 10e-6, 22e-9, LOG_C),
              ("c2", "C2", "kapazitaet", 100e-12, 10e-6, 12e-9, LOG_C),
              ("f", "Signalfrequenz f", "frequenz", 1.0, 1e6, 1e3, LOG_F),
              U_E]
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Zwei RC-Glieder hintereinander ergeben 40 dB pro Dekade. Der Trick des Sallen-Key-"
        "Filters: Das erste Bauteil (beim Tiefpass C1, beim Hochpass R1) führt nicht nach Masse, sondern zum Ausgang "
        "des OPV. Diese Mitkopplung hebt den Bereich um f0 an und macht die Kennlinie eckiger – so lässt sich die "
        "Güte Q einstellen. Q = 0.707 (Butterworth) ist maximal flach, Q = 0.577 (Bessel) schwingt kaum über, "
        "grösseres Q wird steiler, aber mit Überhöhung. Tiefpass mit R1 = R2: Q = ½·√(C1/C2). Hochpass mit "
        "C1 = C2: Q = ½·√(R2/R1). Mit dem Schalter oben die Sprungantwort ansehen: Das Überschwingen wächst mit Q.")

    def sk_rechnen(self, w, v):
        e = fm.sallen_key(v, w["r1"], w["r2"], w["c1"], w["c2"])
        return self._f2_rechnen(e, v, w)

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_m, x_b, x_o, x_k, x_a = 2.4, 4.8, 7.4, 9.8, 11.5, 12.2
        y_s, y_r, y_u = 6.0, 2.4, 9.2
        pins = p.opv(x_o, y_s + 0.5, plus_oben=True)
        p.wechselquelle(x_q, y_s + 0.8, y_u - 0.6, "u_e", f"û = {_u(w['ue'])}")
        p.leitung((x_q, y_s + 0.8), (x_q, y_s))
        p.leitung((x_q, y_u - 0.6), (x_q, y_u), (x_a, y_u))
        if v == "Tiefpass":
            p.widerstand(x_q, y_s, x_m, y_s, "R1", _r(w["r1"]), seite="unten")
            p.widerstand(x_m, y_s, x_b, y_s, "R2", _r(w["r2"]), seite="oben")
            p.kondensator(x_m, y_s, y_r, "C1", _c(w["c1"]), seite="rechts")
            p.kondensator(x_b, y_s, y_u, "C2", _c(w["c2"]), seite="links")
        else:
            p.kondensator_waagrecht(x_q, x_m, y_s, "C1", _c(w["c1"]))
            p.kondensator_waagrecht(x_m, x_b, y_s, "C2", _c(w["c2"]))
            p.widerstand(x_m, y_s, x_m, y_r, "R1", _r(w["r1"]), seite="rechts")
            p.widerstand(x_b, y_s, x_b, y_u, "R2", _r(w["r2"]), seite="links")
        p.knoten(x_m, y_s)
        p.knoten(x_b, y_s)
        p.knoten(x_b, y_u)
        p.leitung((x_b, y_s), pins["plus"])
        p.leitung((x_m, y_r), (x_k, y_r), (x_k, pins["aus"][1]))          # Mitkopplung zum Ausgang
        p.leitung(pins["aus"], (x_a, pins["aus"][1]))
        p.knoten(x_k, pins["aus"][1])
        y_g = 8.1                                                          # Gegenkopplung: Spannungsfolger
        p.leitung(pins["minus"], (pins["minus"][0] - 0.3, pins["minus"][1]), (pins["minus"][0] - 0.3, y_g),
                  (x_k, y_g), (x_k, pins["aus"][1]))
        p.knoten(x_k, y_g)
        p.anschluss(x_a, pins["aus"][1], "u_a")
        p.anschluss(x_a, y_u)
        p.masse(3.6, y_u)
        p.messpunkt(x_k, y_r, "M1", seite="rechts")
        p.text(0.6, 1.4, f"f0 = {_f(e['f0'])}   ·   Q = {e['q']:.3g}   ·   û_a = {_u(e['u_a'])}", "w", fett=True)
        self._f2_diagramme(p, w, e)

    def sk_info(self, w, e, v):
        if v == "Tiefpass":
            formel = "Q = √(R1R2C1C2) / (C2·(R1+R2))"
        else:
            formel = "Q = √(R1R2C1C2) / (R1·(C1+C2))"
        kopf = f"f0 = 1 / (2π·√(R1·R2·C1·C2)) = {_f(e['f0'])}   ·   {formel} = {e['q']:.3g}"
        return self._f2_info(w, e, kopf)


class SchwingkreisSchaltung(LcFilterSchaltung):
    TITEL = "🔌 Schwingkreis als Bandpass und Bandsperre (interaktiv)"
    UNTERTITEL = "RLC in Reihe: Ausgang am R lässt nur f0 durch, Ausgang an L + C sperrt genau f0"
    VARIANTEN = ["RLC-Bandpass", "RLC-Bandsperre"]
    REGLER = [regler if regler[0] != "r" else ("r", "Reihen-R", "widerstand", 1.0, 10e3, 10.0,
                                                 {"einheit": "Ω", "log": True, "grenzen": (0.01, 100e6)})
              for regler in LcFilterSchaltung.REGLER]
