# =============================================================================
# bauteile/grafiken/kurven.py
# -----------------------------------------------------------------------------
# LERNANSICHT SCHALTVORGANG: Kondensator laden/entladen (RC) bzw.
# Spule ein-/ausschalten (RL) - Spannung UND Strom gleichzeitig.
#
#   ┌──────────────────────────────────────────────────────────┐
#   │ R [10][kΩ]  C [10][µF]  U_q [5][V]  U_C0 [0][V]           │
#   │ [ Laden | Entladen ]                                      │
#   │  u_E │ ──────┐________   <- Schalter / Eingangsspannung    │
#   │  u_C │      ╱‾‾‾‾‾‾‾‾‾   <- Diagramm 1 (eigene Achse)      │
#   │  i_C │      ‾╲________   <- Diagramm 2 (eigene Achse)      │
#   │       0    1τ   2τ   3τ   4τ   5τ   <- mit echter Zeit     │
#   │  Zeit t: ──────●──────  [ 50 ][ms ▾]                      │
#   └──────────────────────────────────────────────────────────┘
#
#   modus="RC"  oben u_C(t), unten i_C(t)        (bauteile/rechner/kondensator_rechner.py)
#   modus="RL"  oben i_L(t), unten u_L(t)        (bauteile/rechner/spule_rechner.py)
#               Ausschalten wahlweise ohne Freilaufdiode (Strom über R_aus),
#               mit Freilaufdiode oder mit Diode + Z-Diode.
#
# Die Rechnung steht in bauteile/rechner/schaltvorgaenge_mathe.py.
# Beim Verschieben des Zeit-Reglers wird NUR die Markierung neu gezeichnet.
# Eigene Namen beginnen mit ku_ (keine Kollision mit tkinter).
# =============================================================================

import customtkinter as ctk

import config                                                   # -> config.py
from bauteile.einheiten import formatieren as fmt               # -> bauteile/einheiten.py
from bauteile.rechner import schaltvorgaenge_mathe as sv        # -> rechner/schaltvorgaenge_mathe.py
from bauteile.rechner.basis import EinheitenEingabe, WertRegler # -> rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel      # -> core/layout.py

PUNKTE = 240             # Stützpunkte pro Kurve
VOR_NULL = 0.12          # so viel (Anteil der Zeitachse) wird VOR dem Schalten gezeigt
BLAU = "#3B82F6"
GRUEN = "#22C55E"
ORANGE = "#F59E0B"
VIOLETT = "#A78BFA"

# Knöpfe der Spule -> Ausschaltpfad in schaltvorgaenge_mathe.py
RL_KNOEPFE = {"Einschalten": None, "Aus: ohne Diode": sv.AUSSCHALTEN[0],
              "Aus: Freilaufdiode": sv.AUSSCHALTEN[1], "Aus: Diode + Z-Diode": sv.AUSSCHALTEN[2]}

ERKLAERUNG = {
    "RC": ("Was zeigt die Grafik?  Direkt nach dem Schalten liegt die ganze Spannungsdifferenz am Widerstand – der "
           "Strom ist am grössten. Je weiter sich der Kondensator auflädt, desto kleiner wird die Differenz und damit "
           "der Strom: Spannung und Strom nähern sich exponentiell ihrem Endwert. Nach 1τ ist 63 % der Änderung "
           "geschafft, nach 5τ über 99 % (τ = R · C ist eine ZEIT, 5τ also nicht automatisch 5 s). Vorzeichen: "
           "i_C > 0 heisst, Strom fliesst in den Kondensator (laden), i_C < 0 heraus (entladen)."),
    "RL": ("Was zeigt die Grafik?  Die Spule wehrt sich gegen jede Stromänderung: u_L = L · di/dt. Beim Einschalten "
           "liegt deshalb zuerst die ganze Spannung an der Spule und der Strom steigt erst langsam an. Beim Ausschalten "
           "kann der Strom nicht springen – die Spulenspannung kehrt ihre Polarität um, damit er weiterfliessen kann. "
           "Ohne Freilaufpfad wird diese Spannung riesig (Strom × Widerstand des Ausschaltpfads) und zerstört den "
           "Schalter. Mit Freilaufdiode bleibt sie klein, der Strom klingt aber langsam ab; mit Z-Diode schneller."),
}


def _farbe(paar):
    return paar[1] if ctk.get_appearance_mode() == "Dark" else paar[0]


class KurvenKarte(Karte):

    FELDER = {
        "RC": [("r", "R", "widerstand", "kΩ", "10"), ("c", "C", "kapazitaet", "µF", "10"),
               ("uq", "U_q", "spannung", "V", "5"), ("u0", "U_C0 (Start)", "spannung", "V", "0")],
        "RL": [("r", "R_Spule", "widerstand", "Ω", "100"), ("l", "L", "induktivitaet", "mH", "100"),
               ("u", "U", "spannung", "V", "10"), ("raus", "R_aus", "widerstand", "kΩ", "10"),
               ("uz", "U_Z", "spannung", "V", "24")],
    }
    TITEL = {"RC": ("📈 Kondensator laden & entladen – Spannung und Strom (interaktiv)",
                    "Werte ändern + Enter, Vorgang wählen, dann am Zeit-Regler verschieben"),
             "RL": ("📈 Spule ein- & ausschalten – Strom und Spannung (interaktiv)",
                    "Ausschalten mit und ohne Freilaufdiode vergleichen")}

    def __init__(self, master, modus="RC"):
        self.ku_modus = modus
        super().__init__(master, titel=self.TITEL[modus][0], untertitel=self.TITEL[modus][1])
        b = self.body
        # Zustand VOR dem Canvas setzen (der Canvas kann sofort zeichnen wollen)
        self.ku_m = None                  # aktuelles Modell (Kurven, Achsen, Texte)
        self.ku_groesse = (0, 0)
        self.ku_regler = None

        # ---- Eingaben (Enter = übernehmen) ----
        eingaben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        eingaben.grid(row=0, column=0, sticky="w")
        self.ku_felder = {}
        for i, (name, text, typ, einheit, start) in enumerate(self.FELDER[modus]):
            zeile, spalte = divmod(i, 3)
            ctk.CTkLabel(eingaben, text=text, anchor="w").grid(row=zeile, column=spalte * 2, sticky="w",
                                                               padx=(0 if spalte == 0 else 14, 6), pady=2)
            feld = EinheitenEingabe(eingaben, typ, "", einheit, breite=64)
            feld.ee_feld.insert(0, start)
            feld.grid(row=zeile, column=spalte * 2 + 1, sticky="w", pady=2)
            feld.bei_enter(self.ku_neu)
            self.ku_felder[name] = feld

        knoepfe = ["Laden", "Entladen"] if modus == "RC" else list(RL_KNOEPFE)
        self.ku_art = ctk.CTkSegmentedButton(b, values=knoepfe, command=lambda _v: self._ku_art_gewechselt())
        self.ku_art.set(knoepfe[0])
        self.ku_art.grid(row=1, column=0, sticky="w", pady=(8, 4))

        # ---- Drei Streifen: Eingang, Diagramm 1, Diagramm 2 ----
        self.ku_canvas = ResponsiveCanvas(b, self._zeichnen, seitenverhaeltnis=0.78, max_hoehe=560)
        self.ku_canvas.grid(row=2, column=0, sticky="ew", pady=(4, 4))

        # ---- Zeit-Regler: echte Zeit (s, ms, µs) -> bauteile/rechner/basis.py WertRegler ----
        self.ku_regler = WertRegler(b, "Zeit t", "zeit", 0, 1.0, 0.2, schritte=500,
                                    bei_aenderung=self._marker, text_breite=60)
        self.ku_regler.grid(row=3, column=0, sticky="ew")

        self.ku_anzeige = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"),
                                    text_color=config.FARBEN["akzent"])
        self.ku_anzeige.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        WrapLabel(b, text=ERKLAERUNG[modus], font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"]).grid(
            row=5, column=0, sticky="ew", pady=(6, 0))

        self.ku_neu()

    # =========================================================================
    # MODELL: Werte lesen, Kurven-Funktionen und Texte festlegen
    # =========================================================================
    def _werte(self):
        werte = {}
        for name, text, *_ in self.FELDER[self.ku_modus]:
            wert = self.ku_felder[name].wert()                  # ValueError bei Unsinn
            if wert is None:
                raise ValueError(f"{text} eingeben")
            if name not in ("u0",) and wert <= 0:
                raise ValueError(f"{text} muss grösser als 0 sein")
            werte[name] = wert
        return werte

    def _ku_art_gewechselt(self):
        """RC: Startspannung sichtbar auf den natürlichen Startwert setzen (Laden: 0 V, Entladen: U_q)."""
        if self.ku_modus == "RC":
            try:
                uq = self.ku_felder["uq"].wert() or 0.0
            except ValueError:
                uq = 0.0
            feld = self.ku_felder["u0"]
            feld.leeren()
            feld.ee_feld.insert(0, f"{(0.0 if self.ku_art.get() == 'Laden' else uq) / feld._faktor():g}")
        self.ku_neu()

    def _modell(self, w):
        """Baut ein Dictionary mit allem, was Zeichnung und Anzeige brauchen."""
        if self.ku_modus == "RC":
            laden = self.ku_art.get() == "Laden"
            u_start, u_ende = w["u0"], (w["uq"] if laden else 0.0)
            tau = w["r"] * w["c"]
            return {
                "tau": tau, "t_ende": 5 * tau, "t_null": None,
                "eingang": lambda t: u_start if t < 0 else u_ende,
                "eingang_name": "u_E", "eingang_text": "Eingang (Schalter)",
                "f": lambda t: sv.rc(t, w["r"], w["c"], u_start, u_ende),
                "namen": ("u_C", "i_C"), "typen": ("spannung", "strom"), "farben": (BLAU, GRUEN),
                "prozent": "laden" if u_ende > u_start else ("entladen" if u_ende < u_start else None),
                "vorzeichen": "i_C > 0: lädt  ·  i_C < 0: entlädt",
                "w": w, "laden": laden,
            }
        # ---- RL ----
        art = RL_KNOEPFE[self.ku_art.get()]
        tau_ein = w["l"] / w["r"]
        if art is None:                                         # Einschalten
            return {
                "tau": tau_ein, "t_ende": 5 * tau_ein, "t_null": None, "tau_ein": tau_ein,
                "eingang": lambda t: 0.0 if t < 0 else w["u"],
                "eingang_name": "u_E", "eingang_text": "Schalter: AUS → EIN",
                "f": lambda t: sv.rl_ein(t, w["r"], w["l"], w["u"]),
                "namen": ("i_L", "u_L"), "typen": ("strom", "spannung"), "farben": (GRUEN, BLAU),
                "prozent": "laden", "vorzeichen": "u_L > 0: bremst den steigenden Strom",
                "w": w, "art": None,
            }
        k = sv.rl_aus_kennwerte(w["u"], w["r"], w["l"], art, w["raus"], w["uz"])   # -> schaltvorgaenge_mathe.py
        t_ende = 5 * k["tau"] if k["t_null"] is None else min(5 * k["tau"], 1.4 * k["t_null"])
        return {
            "tau": k["tau"], "t_ende": t_ende, "t_null": k["t_null"], "tau_ein": tau_ein, "k": k,
            "eingang": lambda t: w["u"] if t < 0 else 0.0,
            "eingang_name": "u_E", "eingang_text": "Schalter: EIN → AUS",
            "f": lambda t: sv.rl_aus(t, k["r_kreis"], w["l"], k["i0"], k["u_gegen"]),
            "namen": ("i_L", "u_L"), "typen": ("strom", "spannung"), "farben": (GRUEN, BLAU),
            "prozent": "entladen" if k["u_gegen"] == 0 else None,
            "vorzeichen": "u_L < 0: Polarität kehrt um, treibt den Strom weiter",
            "w": w, "art": art,
        }

    def ku_neu(self):
        """Werte lesen, Modell bauen, Zeitachse anpassen, alles neu zeichnen."""
        try:
            m = self._modell(self._werte())
        except ValueError as fehler:
            self.ku_m = None
            self.ku_anzeige.configure(text=f"⚠ {fehler}", text_color=("#B45309", "#F59E0B"))
            self.ku_canvas.delete("all")
            return
        # Zeit-Regler: gleicher ANTEIL der Zeitachse wie vorher (beim ersten Mal: 1τ)
        if self.ku_m is None:
            t_neu = m["tau"] if m["tau"] <= m["t_ende"] else 0.2 * m["t_ende"]
        else:
            t_neu = self.ku_regler.wert() / self.ku_m["t_ende"] * m["t_ende"]
        self.ku_m = m
        self._achsen_berechnen()
        self.ku_regler.bereich_setzen(0, m["t_ende"], t_neu)
        breite, hoehe = self.ku_groesse
        if breite > 1:
            self.ku_canvas.delete("all")
            self._zeichnen(self.ku_canvas, breite, hoehe)
        else:
            self._marker()

    def _achsen_berechnen(self):
        """Kurven vorab berechnen und Wertebereich je Diagramm bestimmen (Nullpunkt immer sichtbar)."""
        m = self.ku_m
        t0, t1 = -VOR_NULL * m["t_ende"], m["t_ende"]
        zeiten = [t0 + (t1 - t0) * i / PUNKTE for i in range(PUNKTE + 1)]
        werte = [m["f"](t) for t in zeiten]
        m["zeiten"], m["werte"] = zeiten, werte
        bereiche, extreme = [], []
        for spalte in (0, 1):
            vs = [v[spalte] for v in werte]
            extreme.append((min(vs), max(vs)))                  # für die Achsenbeschriftung
            lo, hi = min(0.0, min(vs)), max(0.0, max(vs))
            if hi - lo < 1e-15:
                hi = lo + 1.0
            rand = 0.12 * (hi - lo)
            bereiche.append((lo - (rand if lo < 0 else 0), hi + rand))
        eingang = [m["eingang"](t) for t in zeiten]
        lo, hi = min(0.0, min(eingang)), max(0.0, max(eingang))
        bereiche.append((lo, hi if hi > lo else lo + 1.0))
        m["bereiche"], m["extreme"] = bereiche, extreme

    # =========================================================================
    # ZEICHNEN
    # =========================================================================
    def _geometrie(self):
        w, h = self.ku_groesse
        links, rechts = 0.13 * w, 0.93 * w             # rechts Platz für die 5τ-Beschriftung
        baender = {"eingang": (0.04 * h, 0.13 * h), 0: (0.21 * h, 0.50 * h), 1: (0.58 * h, 0.86 * h)}
        return w, h, links, rechts, baender

    def _x(self, t):
        w, h, links, rechts, _ = self._geometrie()
        t0, t1 = -VOR_NULL * self.ku_m["t_ende"], self.ku_m["t_ende"]
        return links + (rechts - links) * (t - t0) / (t1 - t0)

    def _y(self, wert, band):
        _, _, _, _, baender = self._geometrie()
        oben, unten = baender[band]
        lo, hi = self.ku_m["bereiche"][2 if band == "eingang" else band]
        return unten - (unten - oben) * (wert - lo) / (hi - lo)

    def _zeichnen(self, c, w, h):
        self.ku_groesse = (w, h)
        m = self.ku_m
        if m is None:
            return
        _, _, links, rechts, baender = self._geometrie()
        text = _farbe(config.FARBEN["text_leise"])
        linie = _farbe(config.FARBEN["rahmen"])
        schrift = (config.SCHRIFT, max(8, int(h / 40)))
        klein = (config.SCHRIFT, max(7, int(h / 48)))
        fett = (config.SCHRIFT, max(9, int(h / 34)), "bold")

        # ---- Senkrechte Hilfslinien: Schaltzeitpunkt, 1τ … 5τ, ggf. "i = 0" ----
        oben_alles, unten_alles = baender["eingang"][0], baender[1][1]
        c.create_line(self._x(0), oben_alles, self._x(0), unten_alles, fill=text, dash=(4, 3))
        c.create_text(self._x(0), unten_alles + 0.03 * h, text="t = 0\nSchalten", fill=text, font=klein, justify="center")
        n_max = int(m["t_ende"] / m["tau"] + 1e-9)
        for n in range(1, min(n_max, 5) + 1):
            x = self._x(n * m["tau"])
            c.create_line(x, baender[0][0], x, unten_alles, fill=linie, dash=(2, 4))
            c.create_text(x, unten_alles + 0.03 * h, text=f"{n}τ\n{fmt(n * m['tau'], 'zeit', 3)}",
                          fill=text, font=klein, justify="center")
        if n_max < 2:                                   # z.B. Z-Diode: Strom ist schon vor 1τ null
            for k in range(1, 5):
                t = k * m["t_ende"] / 4
                x = self._x(t)
                c.create_line(x, baender[0][0], x, unten_alles, fill=linie, dash=(2, 4))
                c.create_text(x, unten_alles + 0.03 * h, text="\n" + fmt(t, "zeit", 3), fill=text, font=klein,
                              justify="center")
        if m["t_null"] is not None and m["t_null"] <= m["t_ende"]:
            x = self._x(m["t_null"])
            c.create_line(x, baender[0][0], x, unten_alles, fill=ORANGE, dash=(6, 3))
            c.create_text(x + 4, baender[0][0] + 0.02 * h, anchor="w", text=f"i = 0 nach {fmt(m['t_null'], 'zeit', 3)}",
                          fill=ORANGE, font=klein)

        # ---- Streifen 1: Eingang / Schalter (Rechteck) ----
        o, u = baender["eingang"]
        c.create_line(links, u, rechts, u, fill=linie)
        punkte = []
        for t in m["zeiten"]:
            punkte += [self._x(t), self._y(m["eingang"](t), "eingang")]
        c.create_line(*punkte, fill=VIOLETT, width=2)
        c.create_text(links - 6, (o + u) / 2, anchor="e", text=m["eingang_name"], fill=VIOLETT, font=fett)
        c.create_text(rechts, o - 0.005 * h, anchor="ne", text=m["eingang_text"], fill=text, font=klein)

        # ---- Streifen 2 und 3: Diagramme mit eigener Achse ----
        for band in (0, 1):
            o, u = baender[band]
            lo, hi = m["bereiche"][band]
            name, typ, farbe = m["namen"][band], m["typen"][band], m["farben"][band]
            c.create_line(links, o, links, u, fill=text, width=2)                       # y-Achse
            y0 = self._y(0, band)
            c.create_line(links, y0, rechts, y0, fill=text, width=1)                    # Nulllinie
            dmin, dmax = m["extreme"][band]
            span = (hi - lo) or 1.0
            for wert in sorted({0.0, dmin, dmax}):
                # nur beschriften, wenn nicht zu nah an einer anderen Beschriftung (sonst überlappen sie)
                if wert != 0.0 and abs(wert) < 0.12 * span:
                    continue
                y = self._y(wert, band)
                c.create_line(links - 3, y, links, y, fill=text)
                c.create_text(links - 5, y, anchor="e", text=fmt(wert, typ, 3), fill=text, font=klein)
            c.create_text(0.01 * self.ku_groesse[0], o - 0.012 * h, anchor="sw", text=name, fill=farbe, font=fett)
            punkte = []
            for t, v in zip(m["zeiten"], m["werte"]):
                punkte += [self._x(t), self._y(v[band], band)]
            c.create_line(*punkte, fill=farbe, width=3)
        c.create_text(rechts, baender[1][0] - 0.005 * h, anchor="se", text=m["vorzeichen"], fill=text, font=klein)

        # ---- Prozentmarken bei 1τ … 5τ (Diagramm 1) ----
        if m["prozent"]:
            for n in range(1, min(n_max, 5) + 1):
                t = n * m["tau"]
                v = m["f"](t)[0]
                x, y = self._x(t), self._y(v, 0)
                anteil = 1 - pow(2.718281828459045, -n) if m["prozent"] == "laden" else pow(2.718281828459045, -n)
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=m["farben"][0], outline="")
                nahe_rand = x > links + 0.8 * (rechts - links)          # dann links vom Punkt beschriften
                c.create_text(x - 5 if nahe_rand else x + 5, y + (12 if m["prozent"] == "laden" else -12),
                              anchor="e" if nahe_rand else "w", fill=text, font=klein, text=f"{anteil * 100:.1f} %")
        self._marker()

    def _marker(self):
        """Nur die Markierung (Cursor) neu zeichnen und die Werte anzeigen."""
        w, h = self.ku_groesse
        m = self.ku_m
        if m is None or self.ku_regler is None:
            return
        t = self.ku_regler.wert()
        a, b = m["f"](t)
        zeilen = self._texte(t, a, b)
        self.ku_anzeige.configure(text="\n".join(zeilen[0]), text_color=zeilen[1])
        if w <= 1:
            return
        c = self.ku_canvas
        c.delete("marker")
        _, _, links, rechts, baender = self._geometrie()
        x = self._x(t)
        c.create_line(x, baender["eingang"][0], x, baender[1][1], fill=ORANGE, width=2, tags="marker")
        fett = (config.SCHRIFT, max(9, int(h / 34)), "bold")
        for band, wert in ((0, a), (1, b)):
            y = self._y(wert, band)
            c.create_oval(x - 6, y - 6, x + 6, y + 6, fill=ORANGE, outline="white", width=2, tags="marker")
            # Wert ÜBER dem Diagramm neben dem Namen -> überdeckt nie Kurve oder Prozentmarken
            c.create_text(links, baender[band][0] - 0.012 * h, anchor="sw",
                          text=f"= {fmt(wert, m['typen'][band], 4)}",
                          fill=ORANGE, font=fett, tags="marker")

    def _texte(self, t, a, b):
        """Anzeige unter der Grafik: (Zeilen, Farbe)."""
        m, w = self.ku_m, self.ku_m["w"]
        n = t / m["tau"]
        akzent = config.FARBEN["akzent"]
        if self.ku_modus == "RC":
            zeilen = [f"t = {fmt(t, 'zeit')} ({n:.2f} τ)   →   u_C = {fmt(a, 'spannung')}   ·   i_C = {fmt(b, 'strom')}"
                      + (f"   ·   Ladezustand {a / w['uq'] * 100:.1f} % von U_q" if w["uq"] > 0 else ""),
                      f"τ = R · C = {fmt(m['tau'], 'zeit')}  →  nach 5τ = {fmt(5 * m['tau'], 'zeit')} ist der "
                      "Vorgang zu 99.3 % abgeschlossen (5τ ist eine Zeit, nicht 5 s)"]
            return zeilen, akzent
        energie = 0.5 * w["l"] * a * a
        zeilen = [f"t = {fmt(t, 'zeit')} ({n:.2f} τ)   →   i_L = {fmt(a, 'strom')}   ·   u_L = {fmt(b, 'spannung')}"
                  f"   ·   Energie ½·L·i² = {fmt(energie, 'energie')}"]
        if m["art"] is None:
            zeilen.append(f"Einschaltpfad: R = R_Spule = {fmt(w['r'], 'widerstand')}  →  τ_ein = L / R = "
                          f"{fmt(m['tau'], 'zeit')}  ·  Endstrom U / R = {fmt(w['u'] / w['r'], 'strom')}")
            return zeilen, akzent
        k = m["k"]
        pfad = {sv.AUSSCHALTEN[0]: f"R_Spule + R_aus = {fmt(k['r_kreis'], 'widerstand')}",
                sv.AUSSCHALTEN[1]: f"R_Spule = {fmt(k['r_kreis'], 'widerstand')} + Diode 0.7 V",
                sv.AUSSCHALTEN[2]: f"R_Spule = {fmt(k['r_kreis'], 'widerstand')} + Diode + Z-Diode "
                                   f"({fmt(k['u_gegen'], 'spannung')})"}[m["art"]]
        zeilen.append(f"Ausschaltpfad: {pfad}  →  τ_aus = {fmt(k['tau'], 'zeit')}   (τ_ein = {fmt(m['tau_ein'], 'zeit')})")
        zeilen.append(f"Spannung am Schalter beim Abschalten ≈ {fmt(k['u_schalter'], 'spannung')}   ·   "
                      f"gespeicherte Energie vorher {fmt(k['energie'], 'energie')}")
        farbe = akzent
        if k["u_schalter"] > 100:
            zeilen.append("⚠ Diese Spannungsspitze zerstört Transistoren und lässt Kontakte abbrennen → Freilaufpfad nötig")
            farbe = ("#B91C1C", "#EF4444")
        return zeilen, farbe
