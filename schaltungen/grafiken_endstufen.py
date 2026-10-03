# =============================================================================
# schaltungen/grafiken_endstufen.py
# -----------------------------------------------------------------------------
# INTERAKTIVE SCHALTPLÄNE der Endstufen.
# Spannung = blau, Strom = rot, Messpunkte = orange.
#
#   DarlingtonSchaltung   Einzeltransistor gegen Darlington als Schalter: Basisstrom, Sättigung, Verlustleistung
#   GegentaktSchaltung    Komplementär-Gegentaktstufe Klasse B und AB: Übernahmeverzerrung, Kennlinie, THD, η
#
# Symbole: Schaltplan.npn() / Schaltplan.pnp() in bauteile/grafiken/schaltplan.py
# Rechnung: schaltungen/endstufen_mathe.py
# WER RUFT DAS AUF?  schaltungen/rechner.py (Registrierung, z.B. "schaltung_gegentakt")
# =============================================================================

from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import OK, SPANNUNG, STROM, WARN       # -> bauteile/grafiken/schaltplan.py
from schaltungen import endstufen_mathe as em                            # -> schaltungen/endstufen_mathe.py
from schaltungen.grafiken import _i, _r, _u                              # -> schaltungen/grafiken.py
from schaltungen.grafiken_dioden import FEHLER, _MitDiagramm             # -> schaltungen/grafiken_dioden.py
from schaltungen.grafiken_rc import LOG_R, _punkt                        # -> schaltungen/grafiken_rc.py

LOG_RK = {"einheit": "Ω", "log": True, "grenzen": (0.1, 10e6)}


def _p(wert):
    return fmt(wert, "leistung", 3)


# =============================================================================
# DARLINGTON
# =============================================================================
class DarlingtonSchaltung(_MitDiagramm):
    TITEL = "🔌 Darlington gegen Einzeltransistor als Schalter (interaktiv)"
    UNTERTITEL = "Riesige Stromverstärkung – aber der Darlington sättigt nie ganz und wird bei grossem Strom warm"
    VARIANTEN = ["Einzeltransistor", "Darlington"]
    REGLER = [("ub", "Versorgung U_B", "spannung", 5.0, 30.0, 12.0, {"einheit": "V", "grenzen": (0.5, 200)}),
              ("rl", "Last R_L", "widerstand", 1.0, 1e3, 6.0, LOG_RK),
              ("ust", "Steuerspannung (µC-Pin)", "spannung", 1.8, 5.0, 3.3, {"einheit": "V", "grenzen": (0.5, 30)}),
              ("rb", "Basiswiderstand R_B", "widerstand", 100.0, 100e3, 1e3, LOG_R),
              ("b1", "β von T1", "zahl", 20.0, 500.0, 100.0, {"grenzen": (1, 2000)}),
              ("b2", "β von T2 (Darlington)", "zahl", 10.0, 300.0, 50.0, {"grenzen": (1, 2000)})]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.0, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Ein µC-Pin liefert nur wenige mA. Ein einzelner Transistor mit β = 100 schaltet "
        "damit höchstens einige 100 mA – für 2 A reicht der Basisstrom nicht, der Transistor sättigt nicht und "
        "verheizt U_CE · I_C. Beim DARLINGTON steuert der erste Transistor die Basis des zweiten: β ≈ β1 · β2, "
        "schon 2 mA Basisstrom reichen für Ampere. Der Preis: U_BE ≈ 1.4 V, und der Ausgangstransistor kann nicht "
        "sättigen, weil seine Basis über T1 versorgt wird: U_CE ≥ U_CE,sat + U_BE ≈ 0.9 V. Bei 2 A sind das 1.8 W "
        "Verlust (Einzeltransistor gesättigt: 0.4 W, MOSFET mit 50 mΩ: 0.2 W). Diagramm: Verlustleistung über dem "
        "Laststrom für beide Varianten.")

    def _zustand(self, art, w, i_last):
        e = em.darlington(art, w["ust"], w["rb"], i_last, w["b1"], w["b2"])
        if e["gesaettigt"]:
            return e, i_last * e["u_ce"]
        i_c = e["i_c_moeglich"]
        u_ce = max(w["ub"] - i_c * w["ub"] / i_last, 0.0)              # R_L = U_B / I_Last
        return e, i_c * u_ce

    def sk_rechnen(self, w, v):
        i_last = w["ub"] / w["rl"]
        e, p = self._zustand(v, w, i_last)
        if not e["gesaettigt"]:
            e["u_ce"] = w["ub"] - e["i_c"] * w["rl"]
        e["p"] = p
        e["i_last"] = i_last
        e["i_achse"] = 2 * i_last
        e["kurven"] = {}
        for art in self.VARIANTEN:
            kurve = []
            for k in range(1, 61):
                i = e["i_achse"] * k / 60
                kurve.append((k / 60, self._zustand(art, w, i)[1]))
            e["kurven"][art] = kurve
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_t, y_t, y_r, y_g = 8.4, 6.2, 1.0, 8.8
        p.versorgung(x_t, y_r, f"U_B = {_u(w['ub'])}")
        p.widerstand(x_t, y_r, x_t, 3.4, "R_L", _r(w["rl"]), seite="rechts", farbe=STROM)
        p.quelle(1.2, 5.4, 8.0, "µC", _u(w["ust"]))
        p.leitung((1.2, 8.0), (1.2, y_g), (x_t, y_g))
        p.masse(4.8, y_g)
        if v == "Einzeltransistor":
            p.leitung((x_t, 3.4), (x_t, y_t - 1), farbe=STROM)
            p.npn(x_t, y_t, "T1")
            p.leitung((1.2, 5.4), (1.2, y_t))
            p.widerstand(1.2, y_t, x_t - 0.9, y_t, "R_B", _r(w["rb"]))
            p.leitung((x_t, y_t + 1), (x_t, y_g))
        else:
            x1, y1 = 6.4, 5.0
            p.leitung((x_t, 3.4), (x_t, y_t - 1), farbe=STROM)
            p.leitung((x1, y1 - 1), (x1, 3.8), (x_t, 3.8))
            p.knoten(x_t, 3.8)
            p.npn(x1, y1, "T1", seite="links")
            p.npn(x_t, y_t, "T2")
            p.leitung((x1, y1 + 1), (x1, y_t), (x_t - 0.9, y_t))
            p.leitung((1.2, 5.4), (1.2, y1))
            p.widerstand(1.2, y1, x1 - 0.9, y1, "R_B", _r(w["rb"]))
            p.leitung((x_t, y_t + 1), (x_t, y_g))
        p.knoten(x_t, y_g)
        p.text(x_t + 0.4, 4.6, f"U_CE = {_u(e['u_ce'])}", "w", fett=True,
               farbe=SPANNUNG if e["gesaettigt"] else FEHLER[1])
        p.text(x_t - 0.4, 2.2, f"I = {_i(e['i_c'])}", "e", klein=True, farbe=STROM)
        p.text(3.8, 7.2 if v == "Einzeltransistor" else 5.8, f"I_B = {_i(e['i_b'])}", "center", klein=True,
               farbe=STROM)
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.6, 22.8
        top = max(y for kurve in e["kurven"].values() for _t, y in kurve) * 1.1 or 1.0
        kurven = [(kurve, STROM if art == v else p.leise, None if art == v else 1, art != v)
                  for art, kurve in e["kurven"].items()]
        p.diagramm(gx0, 1.4, gx1, 8.6, kurven, 0.0, top, "Verlustleistung im Transistor (rot = gewählt)",
                   zeit_text=f"Laststrom (0 … {_i(e['i_achse'])})", einheit="leistung")
        _punkt(p, gx0, 1.4, gx1, 8.6, 0.5, e["p"], 0.0, top, farbe=SPANNUNG)

    def sk_info(self, w, e, v):
        zeilen = [f"I_Last = U_B / R_L = {_i(e['i_last'])}   ·   I_B = (U_St − {e['u_bes']:.1f} V) / R_B = "
                  f"{_i(e['i_b'])}   ·   β = {e['beta']:.0f}   ·   β · I_B = {_i(e['i_c_moeglich'])}"]
        if e["gesaettigt"]:
            zeilen.append(f"✓ Gesättigt: U_CE ≈ {_u(e['u_ce'])} → Verlust {_p(e['p'])}"
                          + ("   (Darlington: U_CE nie unter ≈ 0.9 V)" if v == "Darlington" else ""))
            return zeilen, OK if e["p"] < 1.0 else WARN
        zeilen.append(f"❌ Nicht gesättigt: nur {_i(e['i_c'])} statt {_i(e['i_last'])}, U_CE = {_u(e['u_ce'])} → "
                      f"Verlust {_p(e['p'])} – Basisstrom zu klein")
        return zeilen, WARN


# =============================================================================
# GEGENTAKT-ENDSTUFE
# =============================================================================
class GegentaktSchaltung(_MitDiagramm):
    TITEL = "🔌 Gegentakt-Endstufe Klasse B und AB (interaktiv)"
    UNTERTITEL = "NPN für die positive, PNP für die negative Halbwelle – und was in der Mitte passiert"
    VARIANTEN = em.KLASSEN
    REGLER = [("ub", "Versorgung ±U_B", "spannung", 5.0, 30.0, 12.0, {"einheit": "V", "grenzen": (1.0, 100)}),
              ("uh", "Eingang û", "spannung", 0.2, 15.0, 2.0, {"einheit": "V", "grenzen": (0.0, 100)}),
              ("rl", "Last R_L (Lautsprecher)", "widerstand", 2.0, 32.0, 8.0, LOG_RK),
              ("ubias", "Vorspannung U_bias (AB)", "spannung", 0.0, 1.6, 1.3, {"einheit": "V", "grenzen": (0.0, 3.0)})]
    RASTER = (23.2, 10)
    RASTER_SCHMAL = (12.0, 10)
    SEITENVERHAELTNIS = 0.5
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Zwei Emitterfolger arbeiten im Gegentakt: Der NPN liefert die positive Halbwelle "
        "aus +U_B, der PNP die negative aus −U_B. KLASSE B: Ohne Vorspannung leitet ein Transistor erst, wenn der "
        "Eingang 0.65 V überschreitet – um den Nulldurchgang entsteht eine Lücke (Übernahmeverzerrung), die man bei "
        "leiser Musik deutlich hört (hoher Klirrfaktor bei kleinen Signalen). KLASSE AB: Zwei Dioden zwischen den "
        "Basen (U_bias ≈ 1.3 V) halten beide Transistoren knapp leitend – die Lücke verschwindet, dafür fliesst ein "
        "kleiner Ruhestrom. Der Wirkungsgrad bleibt hoch (max. π/4 = 78.5 % bei Vollaussteuerung). Oben: Signal über "
        "der Zeit, unten: Übertragungskennlinie u_a(u_e).")

    def sk_rechnen(self, w, v):
        e = em.gegentakt(v, w["ub"], w["uh"], w["rl"], w["ubias"])
        e["leistung"] = em.endstufe_leistung(w["ub"], w["rl"], max(e["u_hat_aus"], 1e-9))
        return e

    def sk_zeichnen(self, p, w, e, v):
        x_t, x_b, x_a, y_n, y_p, y_m, y_o, y_u = 7.4, 5.0, 10.2, 3.0, 7.0, 5.0, 1.0, 9.0
        p.versorgung(x_t, y_o, f"+U_B = {_u(w['ub'])}")
        p.text(x_t + 0.4, y_u + 0.45, f"−U_B = −{_u(w['ub'])}", "w", klein=True, farbe=p.leise)
        p.npn(x_t, y_n, "T1 (NPN)")
        p.pnp(x_t, y_p, "T2 (PNP)")
        p.leitung((x_t, y_n - 1), (x_t, y_o))
        p.leitung((x_t, y_p + 1), (x_t, y_u))
        p.leitung((x_t, y_n + 1), (x_t, y_p - 1))
        p.knoten(x_t, y_m)
        p.leitung((x_t, y_m), (x_a, y_m))
        p.widerstand(x_a, y_m, x_a, 8.2, "R_L", _r(w["rl"]), seite="rechts")
        p.masse(x_a, 8.2)
        p.leitung((x_t - 0.9, y_n), (x_b, y_n))
        p.leitung((x_t - 0.9, y_p), (x_b, y_p))
        if v == "Klasse AB":
            p.widerstand(x_b, y_o, x_b, y_n, "", "", laenge=1.0)
            p.leitung((x_b, y_o), (x_t, y_o))
            p.diode(x_b, 3.4, x_b, 4.6, "", "", groesse=0.28)
            p.diode(x_b, 5.4, x_b, 6.6, "", "", groesse=0.28)
            p.leitung((x_b, y_n), (x_b, 3.4))
            p.leitung((x_b, 4.6), (x_b, 5.4))
            p.leitung((x_b, 6.6), (x_b, y_p))
            p.widerstand(x_b, y_p, x_b, y_u, "", "", laenge=1.0)
            p.leitung((x_b, y_u), (x_t, y_u))
            p.text(x_b - 0.45, 3.9, f"U_bias = {_u(w['ubias'])}", "e", klein=True, farbe=SPANNUNG)
        else:
            p.leitung((x_b, y_n), (x_b, y_p))
        p.knoten(x_b, y_n)
        p.knoten(x_b, y_p)
        p.knoten(x_b, y_m)
        p.leitung((x_b, y_m), (2.4, y_m))
        p.wechselquelle(2.4, y_m, 8.2, "u_e", f"û = {_u(w['uh'])}")
        p.masse(2.4, 8.2)
        p.messpunkt(x_a, y_m, "M1", seite="rechts")
        if not getattr(self, "mit_diagramm", True):
            return
        gx0, gx1 = 14.0, 22.8
        g = max(w["uh"], 0.1) * 1.15
        p.diagramm(gx0, 1.0, gx1, 4.6, [(e["ein"], p.leise, 1, True), (e["aus"], SPANNUNG, None, False)], -g, g,
                   "u_e (gestrichelt) und u_a (blau)", einheit="spannung", zeit_text="t (2 Perioden)")
        p.diagramm(gx0, 6.0, gx1, 9.4, [(e["kennlinie"], STROM, None, False)], -g, g,
                   "Kennlinie u_a über u_e", einheit="spannung",
                   zeit_text=f"u_e (−{_u(w['uh'] * 1.1)} … +{_u(w['uh'] * 1.1)})")

    def sk_info(self, w, e, v):
        l = e["leistung"]
        zeilen = [f"Klirrfaktor THD = {e['thd'] * 100:.2f} %   ·   û_a = {_u(e['u_hat_aus'])}   ·   "
                  f"P_aus = {_p(e['p_aus'])} an {_r(w['rl'])}",
                  f"Aufgenommen ≈ {_p(e['p_auf'])}   ·   η = {e['eta'] * 100:.0f} %   ·   Verlust in den Transistoren "
                  f"{_p(e['p_verlust'])} (höchstens {_p(l['p_v_max'])} bei û = 2·U_B/π)"]
        farbe = OK
        if v == "Klasse B" and e["thd"] > 0.01:
            zeilen.append(f"⚠ Übernahmeverzerrung: ±0.65 V Lücke um den Nulldurchgang → {e['thd'] * 100:.1f} % "
                          "Klirrfaktor (bei kleinen Signalen besonders schlimm)")
            farbe = WARN
        if e["begrenzt"]:
            zeilen.append(f"⚠ Ausgang begrenzt bei ±{_u(w['ub'] - 1)} – Eingang verkleinern oder U_B erhöhen")
            farbe = WARN
        return zeilen, farbe
