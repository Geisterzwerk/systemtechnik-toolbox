# =============================================================================
# schaltungen/grafiken_dioden.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE der Dioden- und Schutzschaltungen.
# Spannung = blau, Strom = rot, Messpunkte = orange. Wo es um die Kurvenform geht
# (Begrenzer, Gleichrichter, TVS), steht rechts ein Zeitdiagramm Eingang ↔ Ausgang.
#
#   BegrenzerSchaltung     Diodenbegrenzung einseitig / zweiseitig / mit Z-Dioden
#   EingangsschutzSchaltung  Serienwiderstand + Klemmdioden vor einem µC-Pin
#   VerpolSchaltung        ohne / Si-Diode / Schottky / P-MOSFET, Batterie verpolt
#   FreilaufSchaltung      Relais am Transistor: ohne / mit Freilaufdiode / Diode + Z
#   GleichrichterSchaltung Einweg / Brücke / Mittelpunkt mit Ladeelko und Welligkeit
#   ZStabiSchaltung        Z-Dioden-Stabilisierung mit Last
#   TvsSchaltung           Spannungsspitze mit TVS-Diode begrenzen
#
# Rechnung: schaltungen/dioden_mathe.py, Freilauf: bauteile/rechner/schaltvorgaenge_mathe.py
# Grundgerüst: bauteile/grafiken/schaltplan.py -> SchaltungsKarte
#
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_gleichrichter")
# =============================================================================

import config                                                            # -> config.py
from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import (OK, SPANNUNG, STROM, WARN,     # -> bauteile/grafiken/schaltplan.py
                                          SchaltungsKarte)
from bauteile.rechner import schaltvorgaenge_mathe as sv                 # -> bauteile/rechner/schaltvorgaenge_mathe.py
from schaltungen import dioden_mathe as dm                               # -> schaltungen/dioden_mathe.py
from schaltungen.grafiken import _i, _r, _u                              # -> schaltungen/grafiken.py

FEHLER = ("#B91C1C", "#EF4444")
MIN_BREITE_DIAGRAMM = 600       # darunter nur der Schaltplan, ohne Zeitdiagramm


def _p(wert):
    return fmt(wert, "leistung", 3)


class _MitDiagramm(SchaltungsKarte):
    """Schaltplan links + Zeitdiagramm rechts; bei schmaler Fläche nur der Schaltplan."""
    RASTER_SCHMAL = (12, 8.8)

    def sk_raster(self, breite):
        self.mit_diagramm = breite >= MIN_BREITE_DIAGRAMM
        return self.RASTER if self.mit_diagramm else self.RASTER_SCHMAL


# =============================================================================
# BEGRENZER
# =============================================================================
class BegrenzerSchaltung(_MitDiagramm):
    TITEL = "🔌 Diodenbegrenzung (interaktiv)"
    UNTERTITEL = "Ab der Durchlass- bzw. Z-Spannung leitet die Diode und schneidet das Signal ab"
    VARIANTEN = ["einseitig", "zweiseitig", "Z-Dioden"]
    REGLER = [("u", "Scheitelwert Û", "spannung", 0.2, 20.0, 5.0, {"einheit": "V", "grenzen": (0.01, 1000)}),
              ("rv", "Vorwiderstand R_V", "widerstand", 100.0, 100e3, 1e3, {"einheit": "kΩ", "log": True,
                                                                            "grenzen": (1.0, 10e6)}),
              ("uz", "Z-Spannung U_Z", "spannung", 2.0, 15.0, 3.3, {"einheit": "V", "grenzen": (1.0, 200)})]
    RASTER = (20, 8.8)
    SEITENVERHAELTNIS = 0.55
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Solange die Spannung am Ausgang kleiner als die Durchlassspannung (≈ 0.7 V) bzw. "
        "U_Z + 0.7 V ist, sperren die Dioden – der Ausgang folgt dem Eingang. Darüber leiten sie, und der Rest der "
        "Spannung fällt am Vorwiderstand ab: Das Signal wird oben (und mit zwei Dioden auch unten) abgeschnitten. "
        "R_V begrenzt dabei den Diodenstrom. Anwendung: Schutz von Eingängen, Pegelbegrenzung, Rechteck aus Sinus.")

    def _art(self, v):
        return {"einseitig": "einseitig", "zweiseitig": "zweiseitig", "Z-Dioden": "z"}[v]

    def sk_rechnen(self, w, v):
        return dm.begrenzer(self._art(v), w["u"], w["rv"], u_z=w["uz"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_d, x_a, y_o, y_u = 2.1, 6.6, 9.8, 1.7, 8.0
        p.wechselquelle(x_q, y_o + 0.8, y_u - 0.8, "u_e", f"Û = {_u(w['u'])}")
        p.leitung((x_q, y_o + 0.8), (x_q, y_o))
        p.widerstand(x_q, y_o, x_d, y_o, "R_V", _r(w["rv"]))
        p.leitung((x_q, y_u - 0.8), (x_q, y_u), (x_a, y_u))
        p.leitung((x_d, y_o), (x_a, y_o))
        p.knoten(x_d, y_o)
        p.knoten(x_d, y_u)
        p.masse(4.0, y_u)
        if v == "einseitig":
            p.diode(x_d, y_o, x_d, y_u, "D1", "0.7 V")
        elif v == "zweiseitig":
            xl, xr, ya, yb = x_d - 0.7, x_d + 0.7, y_o + 1.0, y_u - 1.0
            p.leitung((x_d, y_o), (x_d, ya))
            p.leitung((xl, ya), (xr, ya))
            p.leitung((xl, yb), (xr, yb))
            p.leitung((x_d, yb), (x_d, y_u))
            p.diode(xl, ya, xl, yb)                                        # leitet bei positiver Spannung
            p.diode(xr, yb, xr, ya)                                        # leitet bei negativer Spannung
            p.text(xr + 0.45, (ya + yb) / 2, "D1, D2", "w", fett=True)
            p.text(xr + 0.45, (ya + yb) / 2 + 0.42, "antiparallel", "w", klein=True, farbe=p.leise)
        else:
            ym = (y_o + y_u) / 2
            p.diode(x_d, ym - 0.1, x_d, y_o + 0.5, art="z")                # Kathode oben
            p.diode(x_d, ym + 0.1, x_d, y_u - 0.5, art="z")                # Kathode unten
            p.leitung((x_d, ym - 0.1), (x_d, ym + 0.1))
            p.text(x_d + 0.55, ym, f"2 × Z {_u(w['uz'])}", "w", fett=True)
        p.anschluss(x_a, y_o)
        p.anschluss(x_a, y_u)
        p.spannung(x_a + 0.5, y_o, y_u, "u_a")
        p.messpunkt(x_d, y_o, "M1", seite="links")
        if getattr(self, "mit_diagramm", True):
            grenze = max(w["u"], e["oben"]) * 1.15
            marken = [(e["oben"], f"{e['oben']:+.2g} V")]
            if e["unten"] > -1e9:
                marken.append((e["unten"], f"{e['unten']:+.2g} V"))
            p.diagramm(12.4, 1.4, 19.6, 7.4, [(e["kurve_ein"], p.leise, 1, True), (e["kurve_aus"], SPANNUNG, None, False)],
                       -grenze, grenze, "u_e (gestrichelt)  ·  u_a (blau)", marken)

    def sk_info(self, w, e, v):
        unten = "–" if e["unten"] < -1e9 else _u(e["unten"])
        zeilen = [f"Begrenzung oben bei {_u(e['oben'])}, unten bei {unten}",
                  f"Diodenstrom Spitze = (Û − U_Begrenzung) / R_V = {_i(e['i_spitze'])}   ·   "
                  f"P(R_V) Spitze = {_p(e['p_rv_spitze'])}"]
        if not e["begrenzt"]:
            zeilen.append("Û liegt unter der Begrenzung – die Dioden leiten nie, u_a = u_e")
            return zeilen, config.FARBEN["akzent"]
        if e["i_spitze"] > 0.1:
            zeilen.append("⚠ Mehr als 100 mA Diodenstrom – R_V vergrössern (Kleinsignaldiode 1N4148: max. 200 mA)")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# EINGANGSSCHUTZ
# =============================================================================
class EingangsschutzSchaltung(SchaltungsKarte):
    TITEL = "🔌 Eingangsschutz eines Mikrocontrollers (interaktiv)"
    UNTERTITEL = "Serienwiderstand + Klemmdioden: Was passiert bei Überspannung am Pin?"
    VARIANTEN = ["interne ESD-Dioden", "externe Schottky (BAT54S)"]
    REGLER = [("ue", "Spannung am Eingang", "spannung", -30.0, 30.0, 12.0, {"einheit": "V", "grenzen": (-1000, 1000)}),
              ("r", "Serienwiderstand R", "widerstand", 100.0, 100e3, 10e3, {"einheit": "kΩ", "log": True,
                                                                              "grenzen": (1.0, 10e6)}),
              ("udd", "Versorgung U_DD", "spannung", 1.8, 5.5, 3.3, {"einheit": "V", "grenzen": (0.5, 15)})]
    RASTER = (16, 8.8)
    SEITENVERHAELTNIS = 0.55
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Jeder CMOS-Eingang hat Schutzdioden zu U_DD und GND. Liegt am Eingang mehr als "
        "U_DD + U_F (oder weniger als −U_F), leiten sie und halten den Pin fest. Den Strom begrenzt NUR der "
        "Serienwiderstand: I_inj = (U_ein − U_Pin) / R. Die internen Dioden vertragen meist nur 1 … 5 mA "
        "(Datenblatt: „injection current“). Achtung: Der Strom fliesst in die Versorgung U_DD – verbraucht die "
        "Schaltung gerade weniger, steigt U_DD an. Externe Schottky-Dioden leiten früher (≈ 0.3 V) und entlasten den Chip.")

    def sk_rechnen(self, w, v):
        u_f = 0.7 if v == self.VARIANTEN[0] else 0.3
        return dict(dm.eingangsschutz(w["ue"], w["r"], w["udd"], u_f), u_f=u_f)

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_k, y_s, y_o, y_u = 1.6, 7.6, 4.6, 1.5, 7.8
        art = "normal" if v == self.VARIANTEN[0] else "schottky"
        p.quelle(x_q, y_s, y_u, "U_ein", _u(w["ue"]), plus_oben=w["ue"] >= 0)
        p.widerstand(x_q, y_s, x_k, y_s, "R", _r(w["r"]))
        p.leitung((x_k, y_s), (10.2, y_s))
        p.knoten(x_k, y_s)
        p.versorgung(x_k, y_o, f"U_DD = {_u(w['udd'])}")
        p.diode(x_k, y_s, x_k, y_o, art=art)                              # Pin -> U_DD
        p.diode(x_k, y_u, x_k, y_s, art=art)                              # GND -> Pin
        p.leitung((x_q, y_u), (x_k, y_u))
        p.knoten(x_k, y_u)
        p.masse(4.6, y_u)
        p.text(x_k - 0.45, (y_s + y_o) / 2, "D1", "e", fett=True)
        p.text(x_k - 0.45, (y_s + y_u) / 2, "D2", "e", fett=True)
        if e["weg"] == "U_DD":
            p.strom(x_k + 0.55, y_s - 0.6, x_k + 0.55, y_o + 0.6, "", farbe=STROM)
        elif e["weg"] == "GND":
            p.strom(x_k + 0.55, y_u - 0.6, x_k + 0.55, y_s + 0.6, "", farbe=STROM)
        p.kasten(10.2, 2.4, 15.2, 7.0, "µC")
        p.text(10.45, y_s, "Pin", "w", klein=True)
        p.text(12.7, y_s + 0.9, f"U_Pin = {_u(e['u_pin'])}", "center", fett=True, farbe=SPANNUNG)
        if e["weg"]:
            p.text(12.7, y_s + 1.5, f"I_inj = {_i(abs(e['i_inj']))}", "center", fett=True, farbe=STROM)
        p.messpunkt(x_k, y_s, "M1", seite="links")

    def sk_info(self, w, e, v):
        zeilen = [f"U_Pin = {_u(e['u_pin'])}   ·   am Widerstand {_u(e['u_r'])}   ·   P(R) = {_p(e['p_r'])}"]
        if e["weg"] is None:
            zeilen.append("Dioden sperren – der Eingang arbeitet normal, kein Injektionsstrom")
            return zeilen, OK
        richtung = "in die Versorgung U_DD" if e["weg"] == "U_DD" else "aus GND (Pin unter 0 V)"
        zeilen.append(f"Injektionsstrom {_i(abs(e['i_inj']))} {richtung}")
        if abs(e["i_inj"]) > 1e-3:
            zeilen.append("⚠ Mehr als 1 mA – viele µC erlauben nur ±1 … 5 mA (Datenblatt!) → R vergrössern")
            return zeilen, WARN
        if e["weg"] == "U_DD":
            zeilen.append("Hinweis: Dieser Strom speist U_DD – im Standby kann die Versorgung dadurch ansteigen")
        return zeilen, OK


# =============================================================================
# VERPOLSCHUTZ
# =============================================================================
class VerpolSchaltung(SchaltungsKarte):
    TITEL = "🔌 Verpolschutz (interaktiv)"
    UNTERTITEL = "Diode oder P-MOSFET in der Plusleitung – Spannungsfall, Wärme und Verhalten bei Verpolung"
    VARIANTEN = dm.VERPOL_ARTEN
    SCHALTER = [("verpolt", "Batterie verpolt")]
    REGLER = [("ub", "Batterie U_B", "spannung", 3.0, 48.0, 12.0, {"einheit": "V", "grenzen": (0.5, 200)}),
              ("i", "Laststrom (Nenn)", "strom", 0.01, 10.0, 1.0, {"einheit": "A", "log": True, "grenzen": (1e-4, 100)}),
              ("rds", "R_DS(on) P-MOSFET", "widerstand", 1e-3, 0.2, 0.02, {"einheit": "mΩ", "log": True,
                                                                         "grenzen": (1e-4, 10)})]
    RASTER = (15.8, 8.8)
    SEITENVERHAELTNIS = 0.56
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Eine Diode in der Plusleitung sperrt bei Verpolung – kostet aber im Betrieb immer "
        "U_F (Si ≈ 0.7 V, Schottky ≈ 0.4 V) und damit P = U_F · I an Wärme. Der P-MOSFET liegt „verkehrt herum“ "
        "in der Leitung: Beim Einschalten leitet zuerst seine Body-Diode, dann zieht das Gate (an GND) den Kanal auf. "
        "Übrig bleibt nur I · R_DS(on) – oft nur Millivolt. Bei Verpolung ist U_GS ≥ 0, der MOSFET sperrt, und die "
        "Body-Diode sperrt ebenfalls. Ohne Schutz liegt die Batterie verkehrt an der Elektronik.")

    def sk_rechnen(self, w, v):
        return dm.verpolschutz(v, w["ub"], w["i"], w["verpolt"], w["rds"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_e, x_l, y_o, y_u = 2.0, 6.8, 11.2, 1.6, 7.8
        p.quelle(x_q, y_o + 0.8, y_u - 0.8, "Batterie", _u(w["ub"]), plus_oben=not w["verpolt"])
        p.leitung((x_q, y_o + 0.8), (x_q, y_o), (x_e - 1.2, y_o))
        p.leitung((x_e + 1.2, y_o), (x_l, y_o))
        p.leitung((x_q, y_u - 0.8), (x_q, y_u), (x_l, y_u))
        p.masse(4.0, y_u)
        if v == "ohne Schutz":
            p.leitung((x_e - 1.2, y_o), (x_e + 1.2, y_o))
        elif v == "P-MOSFET":
            p.leitung((x_e - 1.2, y_o), (x_e - 1.0, y_o))
            p.leitung((x_e + 1.0, y_o), (x_e + 1.2, y_o))
            p.pmosfet(x_e, y_o, "", gate_unten=y_u - y_o)
            p.knoten(x_e, y_u)
        else:
            p.diode(x_e - 1.2, y_o, x_e + 1.2, y_o, "D", art="normal" if v == "Si-Diode" else "schottky")
        p.widerstand(x_l, y_o, x_l, y_u, "Last", _r(e["r_last"]))
        p.spannung(x_l + 1.7, y_o, y_u, f"U_Last = {_u(e['u_last'])}")
        p.leitung((x_l, y_o), (x_l + 1.7, y_o), farbe=p.leise, dick=1)
        p.leitung((x_l, y_u), (x_l + 1.7, y_u), farbe=p.leise, dick=1)
        if abs(e["i"]) > 0:
            if e["i"] > 0:
                p.strom(8.6, y_o, 9.9, y_o, f"I = {_i(e['i'])}")
            else:
                p.strom(9.9, y_o, 8.6, y_o, f"I = {_i(-e['i'])}")
        x_t = x_e + 0.35 if v == "P-MOSFET" else x_e
        anker = "w" if v == "P-MOSFET" else "center"
        if e["zerstoert"]:
            p.text(x_e, 4.4, "Elektronik verpolt!", "center", fett=True, farbe=FEHLER[1])
        elif e["gesperrt"]:
            p.text(x_t, 3.3, "sperrt – kein Strom", anker, fett=True, farbe=OK[1])
        elif v != "ohne Schutz":
            p.text(x_t, 3.3, f"ΔU = {_u(e['u_element'])}", anker, fett=True, farbe=SPANNUNG)
            p.text(x_t, 3.9, f"P = {_p(e['p_element'])}", anker, fett=True, farbe=STROM)

    def sk_info(self, w, e, v):
        if e["zerstoert"]:
            return [f"Ohne Schutz liegen {_u(e['u_last'])} an der Elektronik – Elkos, ICs und Dioden werden zerstört."], FEHLER
        if e["gesperrt"]:
            return [f"{v} sperrt: Die Last bekommt 0 V, es fliesst kein Strom.",
                    f"Das Bauteil muss {_u(w['ub'])} in Sperrrichtung aushalten (U_RRM bzw. U_DS)."], OK
        zeilen = [f"U_Last = {_u(e['u_last'])}   ·   Spannungsfall {_u(e['u_element'])}   ·   "
                  f"Verlust {_p(e['p_element'])}   ·   {e['wirkungsgrad'] * 100:.1f} % kommen an"]
        farbe = OK
        if e["gate_warnung"]:
            zeilen.append("⚠ " + e["gate_warnung"])
            farbe = WARN
        if v in ("Si-Diode", "Schottky") and e["p_element"] > 1:
            zeilen.append("⚠ Mehr als 1 W in der Diode – Kühlung nötig oder P-MOSFET verwenden")
            farbe = WARN
        return zeilen, farbe


# =============================================================================
# FREILAUF
# =============================================================================
class FreilaufSchaltung(SchaltungsKarte):
    TITEL = "🔌 Freilaufdiode am Relais (interaktiv)"
    UNTERTITEL = "Transistor schaltet die Spule ab – wohin mit dem Strom?"
    VARIANTEN = ["ohne Freilaufdiode", "Freilaufdiode", "Diode + Z-Diode"]
    REGLER = [("ub", "Versorgung U_B", "spannung", 5.0, 48.0, 24.0, {"einheit": "V", "grenzen": (1, 400)}),
              ("rs", "Spulenwiderstand", "widerstand", 10.0, 10e3, 1e3, {"einheit": "Ω", "log": True,
                                                                         "grenzen": (0.1, 1e6)}),
              ("l", "Induktivität L", "induktivitaet", 1e-3, 10.0, 0.5, {"einheit": "H", "log": True,
                                                                       "grenzen": (1e-6, 100)}),
              ("uz", "Z-Spannung U_Z", "spannung", 5.0, 60.0, 24.0, {"einheit": "V", "grenzen": (1, 400)})]
    RASTER = (14.6, 9.2)
    SEITENVERHAELTNIS = 0.6
    R_AUS = 10e3                      # Modell für "ohne Diode" (wie in der RC/RL-Lernansicht)
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Der Strom in einer Spule kann nicht springen. Schaltet der Transistor ab, erzeugt "
        "die Spule so viel Spannung, wie nötig ist, um den Strom weiterzutreiben – ohne Freilaufpfad Hunderte Volt "
        "am Kollektor, der Transistor schlägt durch. Die Freilaufdiode bietet dem Strom einen Weg im Kreis: "
        "U_CE steigt nur auf U_B + 0.7 V, aber der Strom klingt langsam ab (Relais fällt verzögert ab). Mit "
        "Z-Diode in Reihe wird die Gegenspannung grösser – der Strom ist viel schneller weg, U_CE bleibt trotzdem "
        "begrenzt (U_B + U_Z + 0.7 V). Modell ohne Diode: Sperrender Transistor/Streukapazität als 10 kΩ.")

    def _art(self, v):
        return sv.AUSSCHALTEN[self.VARIANTEN.index(v)]

    def sk_rechnen(self, w, v):
        if w["rs"] <= 0:
            raise ValueError("Spulenwiderstand muss grösser als 0 sein")
        return sv.rl_aus_kennwerte(w["ub"], w["rs"], w["l"], self._art(v), self.R_AUS, w["uz"])

    def sk_zeichnen(self, p, w, e, v):
        x, x_f, y_o, y_k, y_t = 6.0, 8.8, 1.2, 4.8, 6.4
        p.versorgung(x, y_o, f"+U_B = {_u(w['ub'])}")
        p.widerstand(x, y_o, x, y_k, "K1 (Spule)", f"{_r(w['rs'])} · {fmt(w['l'], 'induktivitaet', 3)}",
                     seite="links", laenge=1.8)
        p.leitung((x, y_k), (x, y_t - 1.0))
        p.npn(x, y_t, "T1")
        p.masse(x, y_t + 1.0)
        p.leitung((x - 0.9, y_t), (x - 1.4, y_t))
        p.widerstand(x - 1.4, y_t, 1.6, y_t, "R_B", "")
        p.anschluss(1.6, y_t, "")
        p.text(1.6, y_t + 0.5, "U_St", "n", klein=True)
        if v != "ohne Freilaufdiode":
            y_a, y_b = y_o + 0.4, y_k
            p.knoten(x, y_a)
            p.knoten(x, y_b)
            p.leitung((x, y_a), (x_f, y_a))
            p.leitung((x, y_b), (x_f, y_b))
            if v == "Freilaufdiode":
                p.diode(x_f, y_b, x_f, y_a, "D", "z.B. 1N4148")              # Anode unten, Kathode oben
            else:
                ym = (y_a + y_b) / 2
                p.diode(x_f, y_b, x_f, ym + 0.05, "D")
                p.diode(x_f, y_a, x_f, ym - 0.05, "Z", _u(w["uz"]), art="z")   # Kathode unten
                p.leitung((x_f, ym - 0.05), (x_f, ym + 0.05))
            p.strom(x_f + 2.6, y_b - 0.4, x_f + 2.6, y_a + 0.4, "", farbe=STROM)
            p.text(x_f + 2.8, (y_a + y_b) / 2, "Freilauf-", "sw", klein=True, farbe=STROM)
            p.text(x_f + 2.8, (y_a + y_b) / 2, "strom", "nw", klein=True, farbe=STROM)
        p.messpunkt(x, y_k, "M1", seite="links")
        farbe = FEHLER[1] if e["u_schalter"] > 100 else SPANNUNG
        p.text(x + 0.35, y_k + 0.42, f"U_CE,max ≈ {_u(e['u_schalter'])}", "w", fett=True, farbe=farbe)

    def sk_info(self, w, e, v):
        zeilen = [f"Strom vor dem Abschalten {_i(e['i0'])}   ·   Energie ½ · L · I² = {fmt(e['energie'], 'energie', 3)}",
                  f"Spannung am Transistor beim Abschalten: U_CE,max ≈ {_u(e['u_schalter'])}"]
        if e["t_null"] is None:
            zeilen.append(f"Strom klingt mit τ = {fmt(e['tau'], 'zeit', 3)} ab – aber nur, weil irgendetwas durchschlägt")
            zeilen.append("❌ Ohne Freilaufpfad wird der Transistor zerstört (oder der Kontakt brennt ab)")
            return zeilen, FEHLER
        zeilen.append(f"Strom ist nach ≈ {fmt(e['t_null'], 'zeit', 3)} null (Relais fällt etwas früher ab)")
        return zeilen, OK


# =============================================================================
# GLEICHRICHTER
# =============================================================================
class GleichrichterSchaltung(_MitDiagramm):
    TITEL = "🔌 Gleichrichter mit Ladeelko (interaktiv)"
    UNTERTITEL = "Einweg, Brücke oder Mittelpunkt – Welligkeit, Brummfrequenz und Sperrspannung"
    VARIANTEN = dm.GLEICHRICHTER
    REGLER = [("u2", "Trafo U2 (eff)", "spannung", 3.0, 30.0, 12.0, {"einheit": "V", "grenzen": (1, 400)}),
              ("i", "Laststrom", "strom", 0.01, 5.0, 0.5, {"einheit": "mA", "log": True, "grenzen": (1e-4, 50)}),
              ("c", "Ladeelko C", "kapazitaet", 100e-6, 22e-3, 2.2e-3, {"einheit": "µF", "log": True,
                                                                     "grenzen": (1e-6, 1)})]
    RASTER = (22.4, 9.4)
    RASTER_SCHMAL = (12.6, 9.4)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Die Dioden lassen nur eine Stromrichtung zum Elko durch. Der Elko lädt sich auf den "
        "Spitzenwert Û minus die Diodenspannungen auf und versorgt die Last, solange die Trafospannung darunter "
        "liegt – die Spannung sinkt dabei um ΔU ≈ I / (f_Brumm · C) ab (Sägezahn). Nachgeladen wird nur in kurzen "
        "Momenten nahe der Spitze, darum sind die Diodenströme dort ein Vielfaches des Laststroms. Brücke und "
        "Mittelpunkt nutzen beide Halbwellen (100 Hz Brumm) und brauchen nur den halben Elko wie die Einweg-"
        "Schaltung (50 Hz). Bei Einweg und Mittelpunkt muss jede Diode 2 · Û sperren.")

    def sk_rechnen(self, w, v):
        e = dm.gleichrichter(v, w["u2"], w["i"], w["c"])
        quelle, aus, ripple, u_min, i_laden = dm.gleichrichter_kurve(v, w["u2"], w["i"], w["c"])
        e.update(kurve_ein=quelle, kurve_aus=aus, ripple_sim=ripple, u_min_sim=u_min, i_laden=i_laden)
        return e

    def sk_zeichnen(self, p, w, e, v):
        y_o, y_u, x_c, x_l = 1.4, 8.2, 7.4, 9.6
        x_t = 1.4
        p.trafo(x_t, 2.4, 6.6 if v != "Mittelpunkt" else 7.2, name="Trafo")
        p.text(x_t - 0.7, 4.5, "230 V~", "e", klein=True, farbe=p.leise)
        xs = x_t + 0.55                                              # Sekundärseite
        if v == "Einweg":
            p.leitung((xs, 2.4), (xs, y_o))
            p.diode(xs, y_o, 5.4, y_o, "D1")
            p.leitung((5.4, y_o), (x_l, y_o))
            p.leitung((xs, 6.6), (xs, y_u), (x_l, y_u))
        elif v == "Brücke":
            xa, xb, ym = 3.6, 5.6, 4.8
            p.leitung((xs, 3.2), (3.0, 3.2), (3.0, ym), (xa, ym))
            p.leitung((xs, 5.8), (4.6, 5.8), (4.6, ym), (xb, ym))
            p.leitung((xs, 2.4), (xs, 3.2))
            p.leitung((xs, 6.6), (xs, 5.8))
            p.diode(xa, ym, xa, y_o, "D1", seite="links")
            p.diode(xb, ym, xb, y_o, "D2")
            p.diode(xa, y_u, xa, ym, "D3", seite="links")
            p.diode(xb, y_u, xb, ym, "D4")
            for xx in (xa, xb):
                p.knoten(xx, ym)
            p.leitung((xa, y_o), (x_l, y_o))
            p.leitung((xa, y_u), (x_l, y_u))
            p.knoten(xb, y_o)
            p.knoten(xb, y_u)
        else:
            y_m = 4.8
            p.leitung((xs, 2.4), (xs, y_o))
            p.diode(xs, y_o, 4.6, y_o, "D1")
            p.leitung((4.6, y_o), (x_l, y_o))
            p.leitung((xs, 7.2), (2.6, 7.2))
            p.diode(2.6, 7.2, 5.0, 7.2, "D2", seite="unten")
            p.leitung((5.0, 7.2), (5.6, 7.2), (5.6, y_o))
            p.knoten(5.6, y_o)
            p.leitung((xs, y_m), (6.3, y_m), (6.3, y_u))
            p.knoten(xs, y_m)
            p.leitung((6.3, y_u), (x_l, y_u))
            p.text(xs + 0.15, y_m - 0.3, "M", "sw", klein=True, farbe=p.leise)
        p.kondensator(x_c, y_o, y_u, "C", fmt(w["c"], "kapazitaet", 3), seite="rechts")
        p.knoten(x_c, y_o)
        p.knoten(x_c, y_u)
        p.widerstand(x_l, y_o, x_l, y_u, "Last", _i(w["i"]))
        p.spannung(x_l + 1.9, y_o, y_u, "U_DC")
        p.leitung((x_l, y_o), (x_l + 1.9, y_o), farbe=p.leise, dick=1)
        p.leitung((x_l, y_u), (x_l + 1.9, y_u), farbe=p.leise, dick=1)
        p.masse(x_c, y_u)
        if getattr(self, "mit_diagramm", True):
            g = e["u_spitze"] * 1.12
            p.diagramm(13.6, 1.6, 21.8, 7.8, [(e["kurve_ein"], p.leise, 1, True), (e["kurve_aus"], SPANNUNG, None, False)],
                       -g, g, "u2 (gestrichelt)  ·  U_DC am Elko (blau)  ·  2 Netzperioden",
                       [(e["u_dc"], _u(e["u_dc"])), (e["u_min_sim"], _u(e["u_min_sim"]))])

    def sk_info(self, w, e, v):
        zeilen = [f"Û = {_u(e['u_spitze'])}   ·   U_DC (Spitze) = {_u(e['u_dc'])}   ·   Brumm {fmt(e['f_brumm'], 'frequenz', 3)}",
                  f"Welligkeit ΔU ≈ I / (f_Brumm · C) = {_u(e['ripple'])}   (Simulation: {_u(e['ripple_sim'])}, "
                  f"Formel = sichere Seite)   ·   "
                  f"Minimum {_u(e['u_min_sim'])}",
                  f"Je Diode: Sperrspannung ≥ {_u(e['u_sperr'])}, Mittelwert {_i(e['i_diode'])}"
                  + (f", beim Nachladen ≈ {_i(e['i_laden'])}" if e["i_laden"] else "")]
        if e["ripple_sim"] > 0.2 * e["u_dc"]:
            zeilen.append("⚠ Welligkeit über 20 % – Elko vergrössern (oder Brücke statt Einweg)")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# Z-DIODEN-STABILISIERUNG
# =============================================================================
class ZStabiSchaltung(SchaltungsKarte):
    TITEL = "🔌 Z-Dioden-Stabilisierung (interaktiv)"
    UNTERTITEL = "Eingangsspannung oder Last ändern – wann hört die Stabilisierung auf?"
    SCHALTER = [("leer", "Last abgeklemmt")]
    REGLER = [("ue", "Eingang Ue", "spannung", 0.0, 30.0, 12.0, {"einheit": "V", "grenzen": (0, 400)}),
              ("rv", "Vorwiderstand R_V", "widerstand", 10.0, 10e3, 220.0, {"einheit": "Ω", "log": True,
                                                                            "grenzen": (1.0, 1e6)}),
              ("rl", "Last R_L", "widerstand", 10.0, 100e3, 1e3, {"einheit": "Ω", "log": True, "grenzen": (1.0, 1e8)}),
              ("uz", "Z-Spannung U_Z", "spannung", 2.7, 24.0, 5.1, {"einheit": "V", "grenzen": (1.0, 200)})]
    RASTER = (14.8, 8.6)
    SEITENVERHAELTNIS = 0.6
    R_Z = 5.0                        # Ω, differentieller Widerstand (typisch 5 … 30 Ω, Datenblatt)
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Die Z-Diode leitet in Sperrrichtung erst ab U_Z und hält dann ihre Spannung fast "
        "konstant. Der Vorwiderstand nimmt die Differenz Ue − U_Z auf; sein Strom teilt sich auf Z-Diode und Last. "
        "Steigt die Last (kleineres R_L), bleibt weniger Strom für die Z-Diode – fällt er unter ca. 1 mA, "
        "stabilisiert sie nicht mehr und Ua bricht ein. Ohne Last fliesst der ganze Strom durch die Z-Diode – "
        "das ist ihr Worst Case für die Leistung. Modell: U_Z + r_z · I_Z mit r_z = 5 Ω.")

    def sk_rechnen(self, w, v):
        return dm.z_arbeitspunkt(w["ue"], w["rv"], w["uz"], None if w["leer"] else w["rl"], self.R_Z)

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_z, x_l, y_o, y_u = 1.6, 6.6, 10.8, 1.4, 7.8
        p.quelle(x_q, y_o + 0.8, y_u - 0.8, "Ue", _u(w["ue"]))
        p.leitung((x_q, y_o + 0.8), (x_q, y_o), (2.6, y_o))
        p.widerstand(2.6, y_o, x_z, y_o, "R_V", _r(w["rv"]))
        p.leitung((x_z, y_o), (x_l, y_o))
        p.leitung((x_q, y_u - 0.8), (x_q, y_u), (x_l, y_u))
        p.knoten(x_z, y_o)
        p.knoten(x_z, y_u)
        p.masse(4.0, y_u)
        p.diode(x_z, y_u, x_z, y_o, "Z", _u(w["uz"]), art="z", seite="rechts")    # Kathode oben
        p.strom(x_z, y_o + 0.25, x_z, y_o + 1.25, f"I_Z = {_i(e['i_z'])}", seite="links")
        if w["leer"]:
            p.anschluss(x_l, y_o)
            p.anschluss(x_l, y_u)
            p.spannung(x_l + 0.5, y_o, y_u, f"Ua = {_u(e['u_a'])}")
        else:
            p.widerstand(x_l, y_o, x_l, y_u, "R_L", _r(w["rl"]))
            p.strom(8.6, y_o, 10.0, y_o, f"I_L = {_i(e['i_l'])}")
            p.spannung(x_l + 1.7, y_o, y_u, f"Ua = {_u(e['u_a'])}")
            p.leitung((x_l, y_o), (x_l + 1.7, y_o), farbe=p.leise, dick=1)
            p.leitung((x_l, y_u), (x_l + 1.7, y_u), farbe=p.leise, dick=1)
        p.messpunkt(x_z, y_o, "M1", seite="rechts")

    def sk_info(self, w, e, v):
        zeilen = [f"Ua = {_u(e['u_a'])}   ·   I(R_V) = {_i(e['i_rv'])} = I_Z {_i(e['i_z'])} + I_L {_i(e['i_l'])}",
                  f"P(Z-Diode) = {_p(e['p_z'])}   ·   P(R_V) = {_p(e['p_rv'])}"]
        if not e["leitet"]:
            zeilen.append("⚠ Z-Diode sperrt: Ue zu klein oder Last zu gross – Ua ist nur ein belasteter Spannungsteiler")
            return zeilen, WARN
        if not e["stabil"]:
            zeilen.append("⚠ I_Z < 1 mA: im Knick der Kennlinie, Ua ist nicht mehr stabil → R_V verkleinern")
            return zeilen, WARN
        if e["p_z"] > 0.5:
            zeilen.append("⚠ Über 0.5 W – eine übliche Z-Diode (500 mW) wird überlastet")
            return zeilen, WARN
        return zeilen, OK


# =============================================================================
# TVS-SCHUTZ
# =============================================================================
class TvsSchaltung(_MitDiagramm):
    TITEL = "🔌 TVS-Diode gegen Spannungsspitzen (interaktiv)"
    UNTERTITEL = "Eine Stossspannung (1.2/50 µs) trifft die Versorgungsleitung – die TVS klemmt sie"
    VARIANTEN = ["unidirektional", "bidirektional"]
    SCHALTER = [("negativ", "negative Spitze")]
    REGLER = [("up", "Spitze U_peak", "spannung", 10.0, 2000.0, 500.0, {"einheit": "V", "log": True,
                                                                        "grenzen": (1.0, 1e5)}),
              ("rq", "Quellwiderstand R_q", "widerstand", 0.5, 100.0, 2.0, {"einheit": "Ω", "log": True,
                                                                             "grenzen": (0.01, 1e4)}),
              ("uwm", "TVS U_WM (Stand-off)", "spannung", 5.0, 60.0, 26.0, {"einheit": "V", "grenzen": (1, 600)}),
              ("ub", "Betriebsspannung U_B", "spannung", 3.0, 60.0, 24.0, {"einheit": "V", "grenzen": (0.5, 600)}),
              ("rd", "TVS r_d (differentiell)", "widerstand", 0.05, 5.0, 0.5, {"einheit": "Ω", "log": True,
                                                                               "grenzen": (1e-3, 100)})]
    RASTER = (21.4, 8.8)
    RASTER_SCHMAL = (13.0, 8.8)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Im Betrieb sperrt die TVS-Diode (U_B ≤ U_WM). Kommt eine Spitze, bricht sie ab "
        "U_BR ≈ 1.11 · U_WM durch und leitet einen grossen Strom nach GND – begrenzt nur durch den Innenwiderstand "
        "der Störquelle (Normprüfung: 2 Ω). Am Gerät bleibt die Klemmspannung U_BR + I · r_d stehen, nicht die "
        "volle Spitze. Die TVS muss die kurze Pulsleistung aushalten (Datenblatt P_PP, z.B. 600 W bei 10/1000 µs). "
        "Unidirektional: in Gegenrichtung wie eine normale Diode (≈ −0.7 V) – richtig für DC-Leitungen. "
        "Bidirektional: symmetrisch – für Signale, die positiv UND negativ werden (AC, RS-485).")

    def sk_rechnen(self, w, v):
        u = -w["up"] if w["negativ"] else w["up"]
        return dm.tvs(u, w["rq"], w["uwm"], w["rd"], v == "bidirektional", w["ub"])

    def sk_zeichnen(self, p, w, e, v):
        x_q, x_t, y_o, y_u = 1.6, 6.8, 1.6, 7.8
        p.quelle(x_q, y_o + 0.8, y_u - 0.8, "Störung", _u(-w["up"] if w["negativ"] else w["up"]),
                 plus_oben=not w["negativ"])
        p.leitung((x_q, y_o + 0.8), (x_q, y_o), (2.4, y_o))
        p.widerstand(2.4, y_o, 5.4, y_o, "R_q", _r(w["rq"]))
        p.leitung((5.4, y_o), (9.8, y_o))
        p.leitung((x_q, y_u - 0.8), (x_q, y_u), (9.8, y_u))
        p.knoten(x_t, y_o)
        p.knoten(x_t, y_u)
        p.masse(4.0, y_u)
        p.diode(x_t, y_u - 0.6, x_t, y_o + 0.6, "TVS", f"U_WM {_u(w['uwm'])}",
                art="tvs" if v == "bidirektional" else "z")
        p.leitung((x_t, y_o), (x_t, y_o + 0.6))
        p.leitung((x_t, y_u - 0.6), (x_t, y_u))
        if e["leitet"]:
            von, nach = (y_o + 0.7, y_o + 1.5) if e["i_puls"] > 0 else (y_o + 1.5, y_o + 0.7)
            p.strom(x_t - 0.55, von, x_t - 0.55, nach, f"{_i(abs(e['i_puls']))}", seite="links")
        p.kasten(9.8, 2.2, 12.4, 7.2, "Gerät")
        p.text(11.1, 4.2, "U_Klemm", "center", klein=True)
        p.text(11.1, 4.8, _u(e["u_klemm"]), "center", fett=True, farbe=SPANNUNG)
        p.messpunkt(x_t, y_o, "M1", seite="rechts")
        if getattr(self, "mit_diagramm", True):
            g = max(abs(min(u for _, u in e["kurve_ein"])), max(u for _, u in e["kurve_ein"]), e["u_br"]) * 1.1
            marken = [(e["u_klemm"], _u(e["u_klemm"]))] if e["leitet"] else []
            p.diagramm(14.4, 1.4, 21.0, 7.6, [(e["kurve_ein"], p.leise, 1, True), (e["kurve_aus"], SPANNUNG, None, False)],
                       -g if w["negativ"] else -g * 0.08, g if not w["negativ"] else g * 0.08,
                       "ohne TVS (gestrichelt)  ·  am Gerät (blau)", marken, zeit_text=f"t (0 … {e['t_ende'] * 1e6:.0f} µs)")

    def sk_info(self, w, e, v):
        zeilen = [f"U_BR ≈ 1.11 · U_WM = {_u(e['u_br'])}   ·   Klemmspannung am Gerät {_u(e['u_klemm'])}",
                  f"Pulsstrom {_i(abs(e['i_puls']))}   ·   Pulsleistung (Spitze) {_p(e['p_spitze'])}"]
        if not e["betrieb_ok"]:
            zeilen.append("❌ U_B > U_WM: Die TVS leitet schon im Normalbetrieb und wird heiss → grössere U_WM wählen")
            return zeilen, FEHLER
        if e["p_spitze"] > 600:
            zeilen.append("⚠ Über 600 W Spitzenleistung – grössere TVS (z.B. 1.5 kW) oder Vorstufe (Varistor, Gasableiter)")
            return zeilen, WARN
        return zeilen, OK
