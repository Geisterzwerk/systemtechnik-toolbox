# =============================================================================
# bauteile/grafiken/trafo_modell.py
# -----------------------------------------------------------------------------
# TRAFO-ANIMATION OHNE FENSTER: Rechnen und Zeichnen (kein tkinter).
#
#          ┌──────── Eisenkern ────────┐
#   (~)────┤██  → → Φ → →          ██├────(💡)
#   U1     │██                       ██│     Last
#    │     │██  ← ← Φ ← ←          ██│      │
#   ───────┘   Primär N1    Sekundär N2 └───────
#
#   ① U1 (Primär)      ② Φ (Magnetfeld)      ③ U2 (Sekundär)    <- 3 "Oszilloskope"
#   Jedes Oszilloskop hat seine EIGENE Skala (bauteile/grafiken/skala.py): Endwerte mit Einheit links,
#   Momentanwert oben rechts. So sind auch kleine Sekundärspannungen (z.B. 5 V) gut zu sehen.
#
# WAS MAN SIEHT:
#   - Punkte auf den Leitungen = Strom (Richtung + Geschwindigkeit)
#   - Pfeile im Kern = Magnetfeld Φ (Richtung + Stärke), wechselt ständig die Richtung
#   - Lampe leuchtet je nach U2
#   - Unten: U2 ist dort am grössten, wo sich Φ am SCHNELLSTEN ändert
#   - DC: nur ein kurzer Impuls beim Umschalten, danach U2 = 0 → Trafo braucht Wechselspannung
#
#   m = TrafoModell()
#   m.setzen({"U1": 230, "N1": 500, "N2": 50}, "∿ Wechselspannung (AC)")
#   geo = m.statisch(c, w, h)       Kern, Spulen, Leitungen, Rahmen der Oszilloskope (einmal)
#   m.dynamisch(c, geo, t)          bewegte Teile zum Zeitpunkt t (jedes Bild)
#   m.weiter(t, dt)                 Strom-Punkte um dt weiterschieben
#   m.info()                        -> (zeilen, warnung)
#
# Gezeichnet wird auf "irgendein Canvas": im Fenster tk.Canvas, im Web SvgCanvas (bauteile/grafiken/svg_canvas.py).
#
# WER RUFT DAS AUF?  bauteile/grafiken/trafo_animation.py (Fenster), web/wiki/grafiken.py (Webversion)
# =============================================================================

import math

import config                                                   # -> config.py
from bauteile.grafiken.schaltplan import farbe_waehlen, ist_dunkel   # -> grafiken/schaltplan.py
from bauteile.grafiken.skala import schoene_grenze, wert_text   # -> bauteile/grafiken/skala.py

F_ANIM = 0.4            # Animationsfrequenz in Hz (stark verlangsamt, echt 50 Hz)
U_SKALA = 400.0         # Bezugsspannung für Strom-Punkte und Lampe (nicht mehr für die Kurven)
SAETTIGUNG = 1.6        # Fluss bei DC nach dem Einschalten (relativ zum Nennfluss, Kern gesättigt)
WURZEL2 = math.sqrt(2)
NOMINAL_V_PRO_WDG = 230 / 500   # "Normaler" Fluss (für die Sättigungs-Anzeige, vereinfacht)
TAU_DC = 0.5            # Abklingzeit des Impulses beim Umschalten auf DC (Animationszeit)

GRUEN = "#22C55E"       # Primärseite
ORANGE = "#F59E0B"      # Sekundärseite
BLAU = "#3B82F6"        # Magnetfeld
ROT = "#EF4444"

AC, DC = "∿ Wechselspannung (AC)", "═ Gleichspannung (DC)"


def _mischen(farbe_a, farbe_b, anteil):
    """Mischt zwei Hex-Farben (anteil 0 = a, 1 = b). Akzeptiert #RGB und #RRGGBB."""
    def rgb(farbe):
        f = farbe.lstrip("#")
        if len(f) == 3:
            f = "".join(z * 2 for z in f)
        if len(f) != 6:
            return [35, 38, 45]                  # unbekanntes Format -> dunkles Grau
        return [int(f[i:i + 2], 16) for i in (0, 2, 4)]
    a, b = rgb(farbe_a), rgb(farbe_b)
    return "#" + "".join(f"{round(x + (y - x) * anteil):02x}" for x, y in zip(a, b))


class _Pfad:
    """Linienzug, auf dem man Positionen 0..1 abfragen kann (für die Strom-Punkte)."""

    def __init__(self, punkte):
        self.punkte = punkte
        self.laengen = [math.dist(a, b) for a, b in zip(punkte, punkte[1:])]
        self.gesamt = sum(self.laengen) or 1

    def position(self, anteil):
        rest = (anteil % 1.0) * self.gesamt
        for (a, b), laenge in zip(zip(self.punkte, self.punkte[1:]), self.laengen):
            if rest <= laenge and laenge > 0:
                f = rest / laenge
                return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            rest -= laenge
        return self.punkte[-1]


class TrafoModell:
    TITEL = "🎬 So funktioniert ein Transformator"
    UNTERTITEL = "Regler bewegen und beobachten, was mit Magnetfeld, U2 und Lampe passiert"
    ERKLAERUNG = ("① Die Wechselspannung U1 treibt einen Strom durch die Primärspule (Punkte = Strom).   "
                  "② Dieser Strom erzeugt im Eisenkern ein Magnetfeld Φ (blaue Pfeile), das ständig die Richtung "
                  "wechselt.   ③ Der Kern leitet das Feld durch die Sekundärspule.   "
                  "④ Weil sich das Feld dort ständig ändert, wird eine Spannung U2 induziert → die Lampe leuchtet.   "
                  "Oszilloskope: Zeit läuft nach rechts (rechts = jetzt), jedes mit eigener Skala; Φ in % vom "
                  "Nennfluss.   Animation stark verlangsamt (echt: 50 Hz = 50 Schwingungen pro Sekunde).")
    VARIANTEN = [AC, DC]
    SCHALTER = []
    STARTWERTE = {}
    # wie SchaltungsModell: (schluessel, text, typ, von, bis, start, {optionen}) -> WertRegler im Fenster, Slider im Web
    REGLER = [("U1", "Primärspannung U1", "spannung", 0.0, 400.0, 230.0, {"einheit": "V", "grenzen": (0, 1000),
                                                                          "schritte": 400}),
              ("N1", "Windungen primär N1", "zahl", 10.0, 1000.0, 500.0, {"grenzen": (1, 100000), "ganzzahl": True}),
              ("N2", "Windungen sekundär N2", "zahl", 10.0, 1000.0, 50.0, {"grenzen": (1, 100000), "ganzzahl": True})]
    SEITENVERHAELTNIS = 0.62
    MAX_HOEHE = 560
    PERIODE = 1 / F_ANIM            # eine Schwingung der Animation in s
    UMSCHALT_VARIANTE = DC          # Web: DC als "Umschalten von AC auf DC" zeigen (Impuls, danach 0)
    UMSCHALT_DAUER = 4.0            # s: 1 s AC, Umschalten, Impuls, Ruhe - dann von vorne

    def __init__(self):
        self.U1, self.N1, self.N2 = 230.0, 500.0, 50.0
        self.dc = False
        self.wechsel = (-1e9, False)    # (Zeitpunkt des letzten AC/DC-Wechsels, vorher DC?)
        self.s1 = 0.0                   # Position der Strom-Punkte primär (0..1)
        self.s2 = 0.0                   # ... sekundär

    @classmethod
    def startwerte(cls, variante=None):
        return {r[0]: r[5] for r in cls.REGLER}

    def setzen(self, werte, variante=None, zeit=0.0):
        """Reglerwerte übernehmen; Variante AC/DC wechseln (merkt sich den Zeitpunkt für den DC-Impuls)."""
        self.U1 = werte.get("U1", self.U1)
        self.N1 = max(1.0, werte.get("N1", self.N1))
        self.N2 = max(1.0, werte.get("N2", self.N2))
        if variante is not None:
            neu_dc = variante == DC
            if neu_dc != self.dc:
                self.wechsel = (zeit, self.dc)
                self.dc = neu_dc

    # =========================================================================
    # RECHNEN
    # =========================================================================
    def fluss(self):
        """Relative Flussamplitude (1 = normal). Φ ~ U1 / N1 (bei gleicher Frequenz)."""
        return (self.U1 / self.N1) / NOMINAL_V_PRO_WDG

    def signale(self, t):
        """
        (u1 in V, phi relativ zum Nennfluss, u2 in V) zum Zeitpunkt t - echte Momentanwerte.
        U1 und U2 sind Effektivwerte -> Scheitelwert û = √2 · U.
        """
        u1_dach = WURZEL2 * self.U1
        u2_dach = WURZEL2 * self.U1 * self.N2 / self.N1
        t_w, vorher_dc = self.wechsel
        dc = self.dc if t >= t_w else vorher_dc
        w = 2 * math.pi * F_ANIM
        if not dc:
            return u1_dach * math.sin(w * t), -self.fluss() * math.cos(w * t), u2_dach * math.sin(w * t)
        # DC: Fluss baut sich einmal auf (bis Sättigung), U2 nur als kurzer Impuls
        dt = t - t_w if t >= t_w else 1e9
        abkling = math.exp(-dt / TAU_DC)
        return self.U1, SAETTIGUNG * (1.0 - abkling), u2_dach * abkling

    def skalen(self):
        """Skalenendwerte der drei Oszilloskope: (U1 in V, Φ relativ, U2 in V)."""
        u1 = WURZEL2 * self.U1                         # auch bei DC: die AC-Kurve davor bleibt sichtbar
        u2 = WURZEL2 * self.U1 * self.N2 / self.N1
        return (schoene_grenze(max(u1, 1e-3)), schoene_grenze(max(self.fluss(), SAETTIGUNG if self.dc else 0.1)),
                schoene_grenze(max(u2, 1e-3)))

    @staticmethod
    def wert_text(idx, wert):
        if idx == 1:
            return f"{wert * 100:+.0f} %".replace("-", "−")
        return ("+" if wert > 0 else "") + wert_text(wert, "spannung")

    def info(self):
        """(zeilen, warnung) - Ergebnistext unter der Animation."""
        u2 = self.U1 * self.N2 / self.N1
        ue = self.N1 / self.N2
        zeilen = [("Bei AC wäre: " if self.dc else "") + f"U2 = U1 · N2 / N1 = {self.U1:.0f} V · {self.N2:.0f} / "
                  f"{self.N1:.0f} = {u2:.1f} V      ü = {ue:.2f}  "
                  f"({'Abwärts' if ue > 1 else 'Aufwärts' if ue < 1 else '1:1'})"]
        if self.dc:
            zeilen.append("⚠ Gleichspannung: Φ ändert sich nicht mehr → U2 = 0. Primärstrom wird nur noch vom "
                          "Drahtwiderstand begrenzt → sehr hoher Strom, echter Trafo würde durchbrennen!")
        elif self.fluss() > 1.5:
            zeilen.append("⚠ Zu wenig Windungen für diese Spannung: Kern geht in Sättigung → hoher Strom, Trafo wird heiss")
        return zeilen, len(zeilen) > 1

    def weiter(self, t, dt):
        """Strom-Punkte um dt weiterschieben (Geschwindigkeit ~ Momentanwert der Spannung)."""
        u1, _phi, u2 = self.signale(t)
        u1, u2 = u1 / (WURZEL2 * U_SKALA), u2 / (WURZEL2 * U_SKALA)
        # Stromgeschwindigkeit: AC ~ Momentanwert; DC primär: konstant hoher Strom
        i1 = 0.9 if self.dc and self.U1 > 0 and t >= self.wechsel[0] else u1
        self.s1 = (self.s1 + i1 * dt * 0.35) % 1.0
        self.s2 = (self.s2 + max(-1.5, min(1.5, u2)) * dt * 0.35) % 1.0

    # =========================================================================
    # ZEICHNEN - statisch (einmal pro Grösse / Einstellung)
    # =========================================================================
    def statisch(self, c, w, h):
        """Kern, Spulen, Leitungen, Quelle, Lampe, Kurven-Rahmen. Rückgabe: Geometrie für dynamisch()."""
        dunkel = ist_dunkel(c)
        bg = farbe_waehlen(config.FARBEN["flaeche"], dunkel)
        text = farbe_waehlen(config.FARBEN["text"], dunkel)
        leise = farbe_waehlen(config.FARBEN["text_leise"], dunkel)
        rahmen = farbe_waehlen(config.FARBEN["rahmen"], dunkel)
        schrift = (config.SCHRIFT, max(8, int(h / 34)))
        klein = (config.SCHRIFT, max(7, int(h / 40)))

        # ---- Eisenkern (geschlossener Rahmen) ----
        x0, x1, y0, y1 = 0.30 * w, 0.70 * w, 0.07 * h, 0.52 * h
        d = min(0.05 * w, 0.075 * h)                                   # Schenkeldicke
        c.create_rectangle(x0, y0, x1, y1, fill="#6B7280", outline="")
        c.create_rectangle(x0 + d, y0 + d, x1 - d, y1 - d, fill=bg, outline="")
        c.create_text(0.5 * w, y0 - 0.025 * h, text="Eisenkern (leitet das Magnetfeld Φ)", fill=leise, font=klein)
        xl, xr = x0 + d / 2, x1 - d / 2                                # Mitte linker / rechter Schenkel
        yt, yb = y0 + 0.07 * h, y1 - 0.07 * h                          # Bereich der Wicklungen

        # ---- Wicklungen: Anzahl Striche ~ Windungszahl ----
        for xm, n, farbe in ((xl, self.N1, GRUEN), (xr, self.N2, ORANGE)):
            striche = max(2, min(16, round(n / 60)))
            for i in range(striche):
                y = yt + (yb - yt) * (i + 0.5) / striche
                c.create_line(xm - 0.85 * d, y + 0.012 * h, xm + 0.85 * d, y - 0.012 * h, fill=farbe, width=3,
                              capstyle="round")

        # ---- Primärkreis: Quelle links ----
        xs, ys, r = 0.10 * w, (y0 + y1) / 2, min(0.045 * h, 0.035 * w)
        ecke_links = xl - 0.85 * d
        c.create_line(ecke_links, yt, xs, yt, xs, ys - r, fill=GRUEN, width=2)
        c.create_line(ecke_links, yb, xs, yb, xs, ys + r, fill=GRUEN, width=2)
        c.create_oval(xs - r, ys - r, xs + r, ys + r, outline=GRUEN, width=2, fill=bg)
        c.create_text(xs, ys, text="═" if self.dc else "~", fill=GRUEN, font=(config.SCHRIFT, int(r * 1.1), "bold"))
        c.create_text(xs - r - 0.01 * w, ys, anchor="e", text="U1", fill=GRUEN, font=schrift)

        # ---- Sekundärkreis: Lampe rechts ----
        xla, yla = 0.90 * w, ys
        ecke_rechts = xr + 0.85 * d
        c.create_line(ecke_rechts, yt, xla, yt, xla, yla - r, fill=ORANGE, width=2)
        c.create_line(ecke_rechts, yb, xla, yb, xla, yla + r, fill=ORANGE, width=2)
        c.create_text(xla + r + 0.01 * w, yla, anchor="w", text="Last", fill=ORANGE, font=schrift)

        # ---- Beschriftung der Spulen ----
        c.create_text(xl, y1 + 0.035 * h, text=f"Primär  N1 = {self.N1:.0f}", fill=GRUEN, font=schrift)
        c.create_text(xr, y1 + 0.035 * h, text=f"Sekundär  N2 = {self.N2:.0f}", fill=ORANGE, font=schrift)

        # ---- Rahmen der drei Kurven (jede mit eigener Skala) ----
        kurven = []
        u2 = self.U1 * self.N2 / self.N1
        art = " ═" if self.dc else " ~"
        titel_liste = ((f"① U1 = {wert_text(self.U1, 'spannung')}{art}", GRUEN), ("② Magnetfeld Φ", BLAU),
                       ("③ U2 → 0 V (nur Impuls)" if self.dc else f"③ U2 = {wert_text(u2, 'spannung')} ~", ORANGE))
        for k, ((titel, farbe), skala) in enumerate(zip(titel_liste, self.skalen())):
            px0 = w * (0.02 + k * 0.33)
            px1 = px0 + 0.30 * w
            py0, py1 = 0.66 * h, 0.97 * h
            mitte, amp = (py0 + py1) / 2, (py1 - py0) * 0.42
            c.create_rectangle(px0, py0, px1, py1, outline=rahmen)
            c.create_line(px0, mitte, px1, mitte, fill=rahmen, dash=(2, 3))
            c.create_text(px0 + 4, py0 - 0.02 * h, anchor="w", text=titel, fill=farbe, font=schrift)
            for wert, y in ((skala, mitte - amp), (-skala, mitte + amp)):      # Skala: Endwerte mit Einheit
                c.create_line(px0, y, px0 + 5, y, fill=leise)
                c.create_text(px0 + 7, y, anchor="w", fill=leise, font=klein, text=self.wert_text(k, wert))
            c.create_text(px1 - 3, py1 - 3, anchor="se", fill=leise, font=klein, text="t →")
            kurven.append((px0, px1, py0, py1, farbe, skala))

        # ---- Geometrie (für die bewegten Teile) ----
        return {
            "w": w, "h": h, "xl": xl, "xr": xr, "yc0": y0 + d / 2, "yc1": y1 - d / 2, "d": d,
            "lampe": (xla, yla, r), "kurven": kurven, "bg": bg, "text": text, "klein": klein,
            "pfad1": _Pfad([(xs, ys - r), (xs, yt), (ecke_links, yt), (ecke_links, yb), (xs, yb), (xs, ys + r)]),
            "pfad2": _Pfad([(ecke_rechts, yb), (ecke_rechts, yt), (xla, yt), (xla, yla - r),
                            (xla, yla + r), (xla, yb), (ecke_rechts, yb)]),
        }

    # =========================================================================
    # ZEICHNEN - bewegt (jedes Bild)
    # =========================================================================
    def dynamisch(self, c, g, t):
        """Bewegte Teile zum Zeitpunkt t. Alle mit tags="dyn" (das Fenster löscht nur diese)."""
        u1, phi, u2 = self.signale(t)
        phi_bild = phi * 0.6                                    # Pfeillänge: Nennfluss = 60 % der vollen Länge

        # ---- Magnetfeld: Pfeile im Kern (oben →, unten ← bei positivem Φ) ----
        laenge = 0.06 * g["w"] * min(abs(phi_bild), 1.0)
        if laenge > 2:
            richtung = 1 if phi > 0 else -1
            breite = max(2, int(g["d"] * 0.25))
            for x in (0.42, 0.58):
                xm = x * g["w"]
                c.create_line(xm - richtung * laenge / 2, g["yc0"], xm + richtung * laenge / 2, g["yc0"],
                              fill=BLAU, width=breite, arrow="last", arrowshape=(10, 12, 5), tags="dyn")
                c.create_line(xm + richtung * laenge / 2, g["yc1"], xm - richtung * laenge / 2, g["yc1"],
                              fill=BLAU, width=breite, arrow="last", arrowshape=(10, 12, 5), tags="dyn")
            c.create_text(0.5 * g["w"], (g["yc0"] + g["yc1"]) / 2, text="Φ", fill=BLAU, tags="dyn",
                          font=(config.SCHRIFT, max(10, int(g["h"] / 16 * (0.4 + 0.6 * min(abs(phi_bild), 1)))), "bold"))
        if self.fluss() > 1.5 and not self.dc:
            c.create_text(0.5 * g["w"], g["yc1"] - 0.06 * g["h"], text="Sättigung!", fill=ROT, tags="dyn",
                          font=(config.SCHRIFT, max(8, int(g["h"] / 30)), "bold"))

        # ---- Strom-Punkte auf den Leitungen ----
        radius = max(2.5, g["h"] / 110)
        for pfad, pos, farbe in ((g["pfad1"], self.s1, GRUEN), (g["pfad2"], self.s2, ORANGE)):
            for k in range(10):
                x, y = pfad.position(pos + k / 10)
                c.create_oval(x - radius, y - radius, x + radius, y + radius, fill=farbe, outline="", tags="dyn")

        # ---- Lampe: Helligkeit nach U2 (AC: Effektivwert, DC: aktueller Impuls) ----
        xla, yla, r = g["lampe"]
        u2_eff = self.U1 * self.N2 / self.N1
        hell = min(1.0, (abs(u2) / WURZEL2 if self.dc else u2_eff) / 230)
        if hell > 0.05:
            glow = r * (1.3 + 1.2 * hell)
            c.create_oval(xla - glow, yla - glow, xla + glow, yla + glow, outline="", tags="dyn",
                          fill=_mischen(g["bg"], "#FFD54A", 0.35 * hell))
        c.create_oval(xla - r, yla - r, xla + r, yla + r, outline=ORANGE, width=2, tags="dyn",
                      fill=_mischen(g["bg"], "#FFE066", hell))
        k = r * 0.6
        c.create_line(xla - k, yla - k, xla + k, yla + k, fill=ORANGE, width=2, tags="dyn")
        c.create_line(xla - k, yla + k, xla + k, yla - k, fill=ORANGE, width=2, tags="dyn")

        # ---- Drei "Oszilloskope": die letzten 2.5 Perioden ----
        fenster = 2.5 / F_ANIM
        for idx, (px0, px1, py0, py1, farbe, skala) in enumerate(g["kurven"]):
            mitte, amp = (py0 + py1) / 2, (py1 - py0) * 0.42
            punkte = []
            for i in range(61):
                tk = t - fenster * (1 - i / 60)
                wert = max(-1.15, min(1.15, self.signale(tk)[idx] / skala))
                punkte += [px0 + (px1 - px0) * i / 60, mitte - amp * wert]
            c.create_line(*punkte, fill=farbe, width=2, tags="dyn")
            momentan = (u1, phi, u2)[idx]
            aktuell = max(-1.15, min(1.15, momentan / skala))
            c.create_oval(px1 - 4, mitte - amp * aktuell - 4, px1 + 4, mitte - amp * aktuell + 4,
                          fill=farbe, outline="", tags="dyn")
            if px1 - px0 < 180:                                  # schmal: Titel zeigt den Wert, Platz fehlt
                continue
            c.create_text(px1 - 6, py0 + 3, anchor="ne", fill=farbe, font=g["klein"], tags="dyn",   # Momentanwert
                          text=("Φ" if idx == 1 else f"u{1 if idx == 0 else 2}") + " = " + self.wert_text(idx, momentan))
