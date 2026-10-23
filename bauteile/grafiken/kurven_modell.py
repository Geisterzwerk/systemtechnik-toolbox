# =============================================================================
# bauteile/grafiken/kurven_modell.py
# -----------------------------------------------------------------------------
# LERNANSICHT SCHALTVORGANG als MODELL OHNE FENSTER (läuft in der Desktop-App UND im Web):
#   RcKurve   Kondensator laden / entladen: u_C(t) und i_C(t)
#   RlKurve   Spule ein- / ausschalten:     i_L(t) und u_L(t), Ausschalten ohne Diode, mit Freilaufdiode
#             oder mit Diode + Z-Diode
#
#   ┌──────────────────────────────────────────────────────────┐
#   │ [ Laden | Entladen ]                                      │
#   │  u_E │ ──────┐________   <- Schalter / Eingangsspannung    │
#   │  u_C │      ╱‾‾‾‾‾‾‾‾‾   <- Diagramm 1 (eigene Achse)      │
#   │  i_C │      ‾╲________   <- Diagramm 2 (eigene Achse)      │
#   │       0    1τ   2τ   3τ   4τ   5τ   <- mit echter Zeit     │
#   │  R ═══●═══  C ═══●═══  U_q …  Zeitpunkt ═══●═══ (% der Achse) │
#   └──────────────────────────────────────────────────────────┘
#
# Die Rechnung steht in bauteile/rechner/schaltvorgaenge_mathe.py (sv.rc, sv.rl_ein, sv.rl_aus …).
# Der Zeit-Regler gilt in % der gezeigten Zeitachse (RC: 0 … 5τ, also 20 % = 1τ) - so passt er immer,
# egal wie gross τ ist. Die echte Zeit steht unter der Grafik.
#
# WER RUFT DAS AUF?  bauteile/rechner/kondensator_rechner.py (rc_ladekurve), spule_rechner.py (rl_kurve)
#                    über GrafikVerweis -> Desktop: SchaltungsKarte, Web: web/wiki/grafiken.py
# =============================================================================

import math

import config                                                            # -> config.py
from bauteile.einheiten import formatieren as fmt                        # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import SchaltungsModell, farbe_waehlen  # -> grafiken/schaltplan.py
from bauteile.rechner import schaltvorgaenge_mathe as sv                 # -> rechner/schaltvorgaenge_mathe.py

PUNKTE = 240             # Stützpunkte pro Kurve
VOR_NULL = 0.12          # so viel (Anteil der Zeitachse) wird VOR dem Schalten gezeigt
BLAU, GRUEN, ORANGE, VIOLETT = "#3B82F6", "#22C55E", "#F59E0B", "#A78BFA"
WARN_ROT = ("#B91C1C", "#EF4444")

# Knöpfe der Spule -> Ausschaltpfad in schaltvorgaenge_mathe.py
RL_KNOEPFE = {"Einschalten": None, "Aus: ohne Diode": sv.AUSSCHALTEN[0],
              "Aus: Freilaufdiode": sv.AUSSCHALTEN[1], "Aus: Diode + Z-Diode": sv.AUSSCHALTEN[2]}

ZEIT_REGLER = ("t", "Zeitpunkt (Anteil der Zeitachse)", "prozent", 0.0, 1.0, 0.2, {"schritte": 200})


class _KurvenModell(SchaltungsModell):
    """Gemeinsamer Teil: Achsen berechnen, drei Streifen zeichnen, Markierung beim Zeitpunkt."""

    SEITENVERHAELTNIS = 0.78
    MAX_HOEHE = 560
    RASTER = (12, 8)
    # Knöpfe unter den Reglern: Zeitpunkt direkt auf n · τ setzen (schaltung_karte.py -> sk_knopf)
    KNOEPFE = [(f"{n}τ", f"tau{n}") for n in range(1, 6)]
    HILFE = ("- **R**, **C** (bzw. **L**) und die Quellenspannung einstellen – die Zeitachse passt sich τ an.\n"
             "- **Zeitpunkt**: Regler ziehen oder mit den Knöpfen **1τ … 5τ** direkt hinspringen.\n"
             "- Oben zwischen den Vorgängen umschalten (z.B. Laden / Entladen).")

    def sk_knopf(self, aktion, w, e, v):
        """Knopf "nτ": Zeitpunkt-Regler auf t = n · τ (als Anteil der Zeitachse, höchstens das Ende)."""
        n = int(aktion[3:])
        return {"t": min(n * e["tau"], e["t_ende"]) / e["t_ende"]}

    def _modell(self, w, v):
        raise NotImplementedError

    def sk_rechnen(self, w, v):
        m = self._modell(w, v)
        t0, t1 = -VOR_NULL * m["t_ende"], m["t_ende"]
        zeiten = [t0 + (t1 - t0) * i / PUNKTE for i in range(PUNKTE + 1)]
        werte = [m["f"](t) for t in zeiten]
        bereiche, extreme = [], []
        for spalte in (0, 1):                                   # Wertebereich je Diagramm, 0 immer sichtbar
            vs = [x[spalte] for x in werte]
            extreme.append((min(vs), max(vs)))
            lo, hi = min(0.0, min(vs)), max(0.0, max(vs))
            if hi - lo < 1e-15:
                hi = lo + 1.0
            rand = 0.12 * (hi - lo)
            bereiche.append((lo - (rand if lo < 0 else 0), hi + rand))
        eingang = [m["eingang"](t) for t in zeiten]
        lo, hi = min(0.0, min(eingang)), max(0.0, max(eingang))
        bereiche.append((lo, hi if hi > lo else lo + 1.0))
        t = min(max(w["t"], 0.0), 1.0) * m["t_ende"]            # Zeitpunkt in Sekunden
        a, b = m["f"](t)
        return {**m, "zeiten": zeiten, "werte": werte, "bereiche": bereiche, "extreme": extreme,
                "t": t, "a": a, "b": b}

    # ---- Geometrie (Pixel) ---------------------------------------------------
    @staticmethod
    def _geo(p):
        w, h = p.breite, p.hoehe
        return w, h, 0.13 * w, 0.93 * w, {"eingang": (0.04 * h, 0.13 * h), 0: (0.21 * h, 0.50 * h),
                                          1: (0.58 * h, 0.86 * h)}

    def _x(self, p, e, t):
        _, _, links, rechts, _ = self._geo(p)
        t0, t1 = -VOR_NULL * e["t_ende"], e["t_ende"]
        return links + (rechts - links) * (t - t0) / (t1 - t0)

    def _y(self, p, e, wert, band):
        oben, unten = self._geo(p)[4][band]
        lo, hi = e["bereiche"][2 if band == "eingang" else band]
        return unten - (unten - oben) * (wert - lo) / (hi - lo)

    def sk_zeichnen(self, p, w, e, v):
        c = p.c
        _, h, links, rechts, baender = self._geo(p)
        text = farbe_waehlen(config.FARBEN["text_leise"], p.dunkel)
        linie = farbe_waehlen(config.FARBEN["rahmen"], p.dunkel)
        klein = (config.SCHRIFT, max(7, int(h / 48)))
        fett = (config.SCHRIFT, max(9, int(h / 34)), "bold")
        x, y = (lambda t: self._x(p, e, t)), (lambda wert, band: self._y(p, e, wert, band))

        # ---- Senkrechte Hilfslinien: Schaltzeitpunkt, 1τ … 5τ, ggf. "i = 0" ----
        oben_alles, unten_alles = baender["eingang"][0], baender[1][1]
        c.create_line(x(0), oben_alles, x(0), unten_alles, fill=text, dash=(4, 3))
        c.create_text(x(0), unten_alles + 0.03 * h, text="t = 0\nSchalten", fill=text, font=klein, justify="center")
        n_max = int(e["t_ende"] / e["tau"] + 1e-9)
        for n in range(1, min(n_max, 5) + 1):
            xn = x(n * e["tau"])
            c.create_line(xn, baender[0][0], xn, unten_alles, fill=linie, dash=(2, 4))
            c.create_text(xn, unten_alles + 0.03 * h, text=f"{n}τ\n{fmt(n * e['tau'], 'zeit', 3)}",
                          fill=text, font=klein, justify="center")
        if n_max < 2:                                           # z.B. Z-Diode: Strom ist schon vor 1τ null
            for k in range(1, 5):
                t = k * e["t_ende"] / 4
                c.create_line(x(t), baender[0][0], x(t), unten_alles, fill=linie, dash=(2, 4))
                c.create_text(x(t), unten_alles + 0.03 * h, text="\n" + fmt(t, "zeit", 3), fill=text, font=klein,
                              justify="center")
        if e["t_null"] is not None and e["t_null"] <= e["t_ende"]:
            xn = x(e["t_null"])
            c.create_line(xn, baender[0][0], xn, unten_alles, fill=ORANGE, dash=(6, 3))
            c.create_text(xn + 4, baender[0][0] + 0.02 * h, anchor="w",
                          text=f"i = 0 nach {fmt(e['t_null'], 'zeit', 3)}", fill=ORANGE, font=klein)

        # ---- Streifen 1: Eingang / Schalter ----
        o, u = baender["eingang"]
        c.create_line(links, u, rechts, u, fill=linie)
        c.create_line(*[k for t in e["zeiten"] for k in (x(t), y(e["eingang"](t), "eingang"))], fill=VIOLETT, width=2)
        c.create_text(links - 6, (o + u) / 2, anchor="e", text=e["eingang_name"], fill=VIOLETT, font=fett)
        c.create_text(rechts, o - 0.005 * h, anchor="ne", text=e["eingang_text"], fill=text, font=klein)

        # ---- Streifen 2 und 3: Diagramme mit eigener Achse ----
        for band in (0, 1):
            o, u = baender[band]
            lo, hi = e["bereiche"][band]
            name, typ, farbe = e["namen"][band], e["typen"][band], e["farben"][band]
            c.create_line(links, o, links, u, fill=text, width=2)
            y0 = y(0, band)
            c.create_line(links, y0, rechts, y0, fill=text, width=1)
            dmin, dmax = e["extreme"][band]
            span = (hi - lo) or 1.0
            for wert in sorted({0.0, dmin, dmax}):
                if wert != 0.0 and abs(wert) < 0.12 * span:      # zu nah an 0 -> Beschriftungen würden überlappen
                    continue
                c.create_line(links - 3, y(wert, band), links, y(wert, band), fill=text)
                c.create_text(links - 5, y(wert, band), anchor="e", text=fmt(wert, typ, 3), fill=text, font=klein)
            c.create_text(0.01 * p.breite, o - 0.012 * h, anchor="sw", text=name, fill=farbe, font=fett)
            c.create_line(*[k for t, val in zip(e["zeiten"], e["werte"]) for k in (x(t), y(val[band], band))],
                          fill=farbe, width=3)
        c.create_text(rechts, baender[1][0] - 0.005 * h, anchor="se", text=e["vorzeichen"], fill=text, font=klein)

        # ---- Prozentmarken bei 1τ … 5τ (Diagramm 1) ----
        if e["prozent"]:
            for n in range(1, min(n_max, 5) + 1):
                t = n * e["tau"]
                xn, yn = x(t), y(e["f"](t)[0], 0)
                anteil = 1 - math.exp(-n) if e["prozent"] == "laden" else math.exp(-n)
                c.create_oval(xn - 3, yn - 3, xn + 3, yn + 3, fill=e["farben"][0], outline="")
                nahe_rand = xn > links + 0.8 * (rechts - links)
                c.create_text(xn - 5 if nahe_rand else xn + 5, yn + (12 if e["prozent"] == "laden" else -12),
                              anchor="e" if nahe_rand else "w", fill=text, font=klein, text=f"{anteil * 100:.1f} %")

        # ---- Markierung beim gewählten Zeitpunkt ----
        xm = x(e["t"])
        c.create_line(xm, baender["eingang"][0], xm, baender[1][1], fill=ORANGE, width=2)
        for band, wert in ((0, e["a"]), (1, e["b"])):
            ym = y(wert, band)
            c.create_oval(xm - 6, ym - 6, xm + 6, ym + 6, fill=ORANGE, outline="white", width=2)
            # Wert ÜBER dem Diagramm neben dem Namen -> überdeckt nie Kurve oder Prozentmarken
            c.create_text(links, baender[band][0] - 0.012 * h, anchor="sw",
                          text=f"= {fmt(wert, e['typen'][band], 4)}", fill=ORANGE, font=fett)


class RcKurve(_KurvenModell):
    TITEL = "📈 Kondensator laden & entladen – Spannung und Strom (interaktiv)"
    UNTERTITEL = "Werte und Vorgang wählen, dann den Zeitpunkt verschieben"
    VARIANTEN = ["Laden", "Entladen"]
    STARTWERTE = {"Laden": {"u0": 0.0}, "Entladen": {"u0": 5.0}}       # Entladen beginnt beim vollen Kondensator
    REGLER = [("r", "R", "widerstand", 100.0, 1e6, 10e3, {"einheit": "kΩ", "log": True, "grenzen": (1.0, 100e6)}),
              ("c", "C", "kapazitaet", 1e-9, 1e-3, 10e-6, {"einheit": "µF", "log": True, "grenzen": (1e-12, 10.0)}),
              ("uq", "U_q (Quelle)", "spannung", 0.5, 30.0, 5.0, {"einheit": "V", "grenzen": (0.01, 1000)}),
              ("u0", "U_C0 (Start)", "spannung", 0.0, 30.0, 0.0, {"einheit": "V", "grenzen": (-1000, 1000)}),
              ZEIT_REGLER]
    ERKLAERUNG = ("Was zeigt die Grafik?  Direkt nach dem Schalten liegt die ganze Spannungsdifferenz am Widerstand – "
                  "der Strom ist am grössten. Je weiter sich der Kondensator auflädt, desto kleiner wird die Differenz "
                  "und damit der Strom: Spannung und Strom nähern sich exponentiell ihrem Endwert. Nach 1τ ist 63 % der "
                  "Änderung geschafft, nach 5τ über 99 % (τ = R · C ist eine ZEIT, 5τ also nicht automatisch 5 s). "
                  "Vorzeichen: i_C > 0 heisst, Strom fliesst in den Kondensator (laden), i_C < 0 heraus (entladen).")

    def _modell(self, w, v):
        laden = v != "Entladen"
        u_start, u_ende = w["u0"], (w["uq"] if laden else 0.0)
        tau = w["r"] * w["c"]
        return {"tau": tau, "t_ende": 5 * tau, "t_null": None,
                "eingang": lambda t: u_start if t < 0 else u_ende,
                "eingang_name": "u_E", "eingang_text": "Eingang (Schalter)",
                "f": lambda t: sv.rc(t, w["r"], w["c"], u_start, u_ende),
                "namen": ("u_C", "i_C"), "typen": ("spannung", "strom"), "farben": (BLAU, GRUEN),
                "prozent": "laden" if u_ende > u_start else ("entladen" if u_ende < u_start else None),
                "vorzeichen": "i_C > 0: lädt  ·  i_C < 0: entlädt"}

    def sk_info(self, w, e, v):
        n = e["t"] / e["tau"]
        zeilen = [f"t = {fmt(e['t'], 'zeit')} ({n:.2f} τ)   →   u_C = {fmt(e['a'], 'spannung')}   ·   "
                  f"i_C = {fmt(e['b'], 'strom')}"
                  + (f"   ·   Ladezustand {e['a'] / w['uq'] * 100:.1f} % von U_q" if w["uq"] > 0 else ""),
                  f"τ = R · C = {fmt(e['tau'], 'zeit')}  →  nach 5τ = {fmt(5 * e['tau'], 'zeit')} ist der Vorgang zu "
                  "99.3 % abgeschlossen (5τ ist eine Zeit, nicht 5 s)"]
        return zeilen, config.FARBEN["akzent"]


class RlKurve(_KurvenModell):
    TITEL = "📈 Spule ein- & ausschalten – Strom und Spannung (interaktiv)"
    UNTERTITEL = "Ausschalten mit und ohne Freilaufdiode vergleichen"
    VARIANTEN = list(RL_KNOEPFE)
    REGLER = [("r", "R_Spule", "widerstand", 1.0, 1e3, 100.0, {"einheit": "Ω", "log": True, "grenzen": (0.01, 1e6)}),
              ("l", "L", "induktivitaet", 1e-3, 10.0, 0.1, {"einheit": "mH", "log": True, "grenzen": (1e-9, 1000)}),
              ("u", "U", "spannung", 1.0, 48.0, 10.0, {"einheit": "V", "grenzen": (0.01, 1000)}),
              ("raus", "R_aus (ohne Diode)", "widerstand", 100.0, 1e6, 10e3,
               {"einheit": "kΩ", "log": True, "grenzen": (1.0, 1e9)}),
              ("uz", "U_Z (Z-Diode)", "spannung", 3.0, 100.0, 24.0, {"einheit": "V", "grenzen": (0.5, 1000)}),
              ZEIT_REGLER]
    ERKLAERUNG = ("Was zeigt die Grafik?  Die Spule wehrt sich gegen jede Stromänderung: u_L = L · di/dt. Beim "
                  "Einschalten liegt deshalb zuerst die ganze Spannung an der Spule und der Strom steigt erst langsam "
                  "an. Beim Ausschalten kann der Strom nicht springen – die Spulenspannung kehrt ihre Polarität um, "
                  "damit er weiterfliessen kann. Ohne Freilaufpfad wird diese Spannung riesig (Strom × Widerstand des "
                  "Ausschaltpfads) und zerstört den Schalter. Mit Freilaufdiode bleibt sie klein, der Strom klingt aber "
                  "langsam ab; mit Z-Diode schneller.")

    def _modell(self, w, v):
        art = RL_KNOEPFE.get(v)
        tau_ein = w["l"] / w["r"]
        if art is None:                                         # Einschalten
            return {"tau": tau_ein, "t_ende": 5 * tau_ein, "t_null": None, "tau_ein": tau_ein, "art": None,
                    "eingang": lambda t: 0.0 if t < 0 else w["u"],
                    "eingang_name": "u_E", "eingang_text": "Schalter: AUS → EIN",
                    "f": lambda t: sv.rl_ein(t, w["r"], w["l"], w["u"]),
                    "namen": ("i_L", "u_L"), "typen": ("strom", "spannung"), "farben": (GRUEN, BLAU),
                    "prozent": "laden", "vorzeichen": "u_L > 0: bremst den steigenden Strom"}
        k = sv.rl_aus_kennwerte(w["u"], w["r"], w["l"], art, w["raus"], w["uz"])
        t_ende = 5 * k["tau"] if k["t_null"] is None else min(5 * k["tau"], 1.4 * k["t_null"])
        return {"tau": k["tau"], "t_ende": t_ende, "t_null": k["t_null"], "tau_ein": tau_ein, "k": k, "art": art,
                "eingang": lambda t: w["u"] if t < 0 else 0.0,
                "eingang_name": "u_E", "eingang_text": "Schalter: EIN → AUS",
                "f": lambda t: sv.rl_aus(t, k["r_kreis"], w["l"], k["i0"], k["u_gegen"]),
                "namen": ("i_L", "u_L"), "typen": ("strom", "spannung"), "farben": (GRUEN, BLAU),
                "prozent": "entladen" if k["u_gegen"] == 0 else None,
                "vorzeichen": "u_L < 0: Polarität kehrt um, treibt den Strom weiter"}

    def sk_info(self, w, e, v):
        n = e["t"] / e["tau"]
        zeilen = [f"t = {fmt(e['t'], 'zeit')} ({n:.2f} τ)   →   i_L = {fmt(e['a'], 'strom')}   ·   "
                  f"u_L = {fmt(e['b'], 'spannung')}   ·   Energie ½·L·i² = {fmt(0.5 * w['l'] * e['a'] ** 2, 'energie')}"]
        if e["art"] is None:
            zeilen.append(f"Einschaltpfad: R = R_Spule = {fmt(w['r'], 'widerstand')}  →  τ_ein = L / R = "
                          f"{fmt(e['tau'], 'zeit')}  ·  Endstrom U / R = {fmt(w['u'] / w['r'], 'strom')}")
            return zeilen, config.FARBEN["akzent"]
        k = e["k"]
        pfad = {sv.AUSSCHALTEN[0]: f"R_Spule + R_aus = {fmt(k['r_kreis'], 'widerstand')}",
                sv.AUSSCHALTEN[1]: f"R_Spule = {fmt(k['r_kreis'], 'widerstand')} + Diode 0.7 V",
                sv.AUSSCHALTEN[2]: f"R_Spule = {fmt(k['r_kreis'], 'widerstand')} + Diode + Z-Diode "
                                   f"({fmt(k['u_gegen'], 'spannung')})"}[e["art"]]
        zeilen.append(f"Ausschaltpfad: {pfad}  →  τ_aus = {fmt(k['tau'], 'zeit')}   (τ_ein = {fmt(e['tau_ein'], 'zeit')})")
        zeilen.append(f"Spannung am Schalter beim Abschalten ≈ {fmt(k['u_schalter'], 'spannung')}   ·   "
                      f"gespeicherte Energie vorher {fmt(k['energie'], 'energie')}")
        if k["u_schalter"] > 100:
            zeilen.append("⚠ Diese Spannungsspitze zerstört Transistoren und lässt Kontakte abbrennen → Freilaufpfad nötig")
            return zeilen, WARN_ROT
        return zeilen, config.FARBEN["akzent"]
