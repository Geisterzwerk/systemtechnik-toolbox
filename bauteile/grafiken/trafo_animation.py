# =============================================================================
# bauteile/grafiken/trafo_animation.py
# -----------------------------------------------------------------------------
# TRAFO-ANIMATION: zeigt Schritt für Schritt, wie ein Transformator funktioniert.
#
#          ┌──────── Eisenkern ────────┐
#   (~)────┤██  → → Φ → →          ██├────(💡)
#   U1     │██                       ██│     Last
#    │     │██  ← ← Φ ← ←          ██│      │
#   ───────┘   Primär N1    Sekundär N2 └───────
#
#   ① U1 (Primär)      ② Φ (Magnetfeld)      ③ U2 (Sekundär)    <- 3 "Oszilloskope"
#   Regler: U1, N1, N2      Umschalter: AC / DC      ⏸ Pause
#
# WAS MAN SIEHT:
#   - Punkte auf den Leitungen = Strom (Richtung + Geschwindigkeit)
#   - Pfeile im Kern = Magnetfeld Φ (Richtung + Stärke), wechselt ständig die Richtung
#   - Lampe leuchtet je nach U2
#   - Unten: U2 ist dort am grössten, wo sich Φ am SCHNELLSTEN ändert
#   - DC: nur ein kurzer Impuls beim Umschalten, danach U2 = 0 → Trafo braucht Wechselspannung
#
# TECHNIK:
#   - Statische Teile (Kern, Spulen, Leitungen) werden nur bei Grössenänderung
#     oder neuer Windungszahl gezeichnet (Tag "statisch").
#   - Bewegte Teile werden alle 40 ms gelöscht und neu gezeichnet (Tag "dyn").
#   - Die Animation stoppt von selbst, wenn die Seite verlassen wird, und
#     pausiert, solange sie nicht sichtbar ist (spart Rechenzeit).
#   - Alle eigenen Namen beginnen mit ta_ (keine Kollision mit tkinter!).
# =============================================================================

import math
import time

import customtkinter as ctk

import config                                                   # -> config.py
from bauteile.rechner.basis import WertRegler                   # -> bauteile/rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel      # -> core/layout.py

F_ANIM = 0.4            # Animationsfrequenz in Hz (stark verlangsamt, echt 50 Hz)
FRAME_MS = 40           # 25 Bilder pro Sekunde
U_SKALA = 400.0         # Spannung, die in den Kurven dem vollen Ausschlag entspricht
NOMINAL_V_PRO_WDG = 230 / 500   # "Normaler" Fluss (für die Sättigungs-Anzeige, vereinfacht)
TAU_DC = 0.5            # Abklingzeit des Impulses beim Umschalten auf DC (Animationszeit)

GRUEN = "#22C55E"       # Primärseite
ORANGE = "#F59E0B"      # Sekundärseite
BLAU = "#3B82F6"        # Magnetfeld
ROT = "#EF4444"


def _modus_farbe(paar):
    return paar[1] if ctk.get_appearance_mode() == "Dark" else paar[0]


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


class TrafoAnimation(Karte):

    def __init__(self, master):
        super().__init__(master, titel="🎬 So funktioniert ein Transformator",
                         untertitel="Regler bewegen und beobachten, was mit Magnetfeld, U2 und Lampe passiert")
        b = self.body

        # ---- Zustand (VOR dem Canvas setzen - der Canvas kann sofort zeichnen) ----
        self.ta_U1, self.ta_N1, self.ta_N2 = 230.0, 500.0, 50.0
        self.ta_dc = False
        self.ta_laeuft = True
        self.ta_zeit = 0.0                 # Animationszeit in s
        self.ta_wechsel = (-1e9, False)    # (Zeitpunkt des letzten AC/DC-Wechsels, vorher DC?)
        self.ta_s1 = 0.0                   # Position der Strom-Punkte primär (0..1)
        self.ta_s2 = 0.0                   # ... sekundär
        self.ta_geo = None                 # Geometrie, gesetzt in _ta_statisch
        self.ta_letzt = time.monotonic()

        # ---- Zeichenfläche ----
        self.ta_canvas = ResponsiveCanvas(b, self._ta_statisch, seitenverhaeltnis=0.62, max_hoehe=560)
        self.ta_canvas.grid(row=0, column=0, sticky="ew")

        # ---- Regler ----
        regler = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        regler.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        regler.grid_columnconfigure(1, weight=1)
        regler.grid_columnconfigure(0, weight=1)
        # Slider + Zahlenfeld + Einheit -> bauteile/rechner/basis.py WertRegler
        self.ta_regler = {
            "U1": WertRegler(regler, "Primärspannung U1", "spannung", 0, 400, self.ta_U1, einheit="V",
                             grenzen=(0, 1000), schritte=400, bei_aenderung=self._ta_regler_geaendert, text_breite=170),
            "N1": WertRegler(regler, "Windungen primär N1", "zahl", 10, 1000, self.ta_N1, grenzen=(1, 100000),
                             ganzzahl=True, bei_aenderung=self._ta_regler_geaendert, text_breite=170),
            "N2": WertRegler(regler, "Windungen sekundär N2", "zahl", 10, 1000, self.ta_N2, grenzen=(1, 100000),
                             ganzzahl=True, bei_aenderung=self._ta_regler_geaendert, text_breite=170),
        }
        for zeile, eintrag in enumerate(self.ta_regler.values()):
            eintrag.grid(row=zeile, column=0, sticky="ew")

        knoepfe = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        knoepfe.grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.ta_art = ctk.CTkSegmentedButton(knoepfe, values=["∿ Wechselspannung (AC)", "═ Gleichspannung (DC)"],
                                             command=lambda _v: self._ta_art_geaendert())
        self.ta_art.set("∿ Wechselspannung (AC)")
        self.ta_art.grid(row=0, column=0)
        self.ta_pause = ctk.CTkButton(knoepfe, text="⏸ Pause", width=90, command=self._ta_pause_umschalten)
        self.ta_pause.grid(row=0, column=1, padx=(10, 0))

        # ---- Ergebnis + Legende ----
        self.ta_info = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"), text_color=config.FARBEN["akzent"])
        self.ta_info.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        WrapLabel(b, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"], text=(
            "① Die Wechselspannung U1 treibt einen Strom durch die Primärspule (Punkte = Strom).   "
            "② Dieser Strom erzeugt im Eisenkern ein Magnetfeld Φ (blaue Pfeile), das ständig die Richtung wechselt.   "
            "③ Der Kern leitet das Feld durch die Sekundärspule.   "
            "④ Weil sich das Feld dort ständig ändert, wird eine Spannung U2 induziert → die Lampe leuchtet.   "
            f"Animation stark verlangsamt (echt: 50 Hz = 50 Schwingungen pro Sekunde).")).grid(
            row=4, column=0, sticky="ew", pady=(6, 0))

        self._ta_regler_geaendert()
        self._ta_schleife()

    # =========================================================================
    # BEDIENUNG
    # =========================================================================
    def _ta_regler_geaendert(self):
        alt_n = (round(self.ta_N1), round(self.ta_N2))
        self.ta_U1 = self.ta_regler["U1"].wert()
        self.ta_N1 = max(1.0, self.ta_regler["N1"].wert())
        self.ta_N2 = max(1.0, self.ta_regler["N2"].wert())
        if alt_n != (round(self.ta_N1), round(self.ta_N2)):
            self._ta_neu_zeichnen()               # Anzahl gezeichneter Windungen ändert sich
        self._ta_info_setzen()

    def _ta_art_geaendert(self):
        neu_dc = self.ta_art.get().startswith("═")
        if neu_dc != self.ta_dc:
            self.ta_wechsel = (self.ta_zeit, self.ta_dc)
            self.ta_dc = neu_dc
            self._ta_neu_zeichnen()               # Quellen-Symbol ~ / =
        self._ta_info_setzen()

    def _ta_pause_umschalten(self):
        self.ta_laeuft = not self.ta_laeuft
        self.ta_pause.configure(text="⏸ Pause" if self.ta_laeuft else "▶ Weiter")

    def _ta_info_setzen(self):
        u2 = self.ta_U1 * self.ta_N2 / self.ta_N1
        ue = self.ta_N1 / self.ta_N2
        zeilen = [("Bei AC wäre: " if self.ta_dc else "") + f"U2 = U1 · N2 / N1 = {self.ta_U1:.0f} V · {self.ta_N2:.0f} / {self.ta_N1:.0f} = {u2:.1f} V"
                  f"      ü = {ue:.2f}  ({'Abwärts' if ue > 1 else 'Aufwärts' if ue < 1 else '1:1'})"]
        if self.ta_dc:
            zeilen.append("⚠ Gleichspannung: Φ ändert sich nicht mehr → U2 = 0. Primärstrom wird nur noch vom "
                          "Drahtwiderstand begrenzt → sehr hoher Strom, echter Trafo würde durchbrennen!")
        elif self._ta_fluss() > 1.5:
            zeilen.append("⚠ Zu wenig Windungen für diese Spannung: Kern geht in Sättigung → hoher Strom, Trafo wird heiss")
        self.ta_info.configure(text="\n".join(zeilen),
                               text_color=("#B45309", "#F59E0B") if len(zeilen) > 1 else config.FARBEN["akzent"])

    def _ta_fluss(self):
        """Relative Flussamplitude (1 = normal). Φ ~ U1 / N1 (bei gleicher Frequenz)."""
        return (self.ta_U1 / self.ta_N1) / NOMINAL_V_PRO_WDG

    # =========================================================================
    # SIGNALE (normiert, für Kurven und Animation)
    # =========================================================================
    def _ta_signale(self, t):
        """(u1, phi, u2) zum Zeitpunkt t, normiert auf −1..+1 (u2 kann darüber hinaus -> wird abgeschnitten)."""
        a1 = self.ta_U1 / U_SKALA
        a2 = self.ta_U1 * self.ta_N2 / self.ta_N1 / U_SKALA
        aphi = min(self._ta_fluss() * 0.6, 1.0)
        t_w, vorher_dc = self.ta_wechsel
        dc = self.ta_dc if t >= t_w else vorher_dc
        w = 2 * math.pi * F_ANIM
        if not dc:
            return a1 * math.sin(w * t), -aphi * math.cos(w * t), a2 * math.sin(w * t)
        # DC: Fluss baut sich einmal auf (bis Sättigung), U2 nur als kurzer Impuls
        dt = t - t_w if t >= t_w else 1e9
        abkling = math.exp(-dt / TAU_DC)
        return a1, 1.0 - abkling, a2 * abkling

    # =========================================================================
    # ZEICHNEN - statisch
    # =========================================================================
    def _ta_neu_zeichnen(self):
        if self.ta_geo:
            w, h = self.ta_geo["w"], self.ta_geo["h"]
            self.ta_canvas.delete("all")
            self._ta_statisch(self.ta_canvas, w, h)

    def _ta_statisch(self, c, w, h):
        """Kern, Spulen, Leitungen, Quelle, Lampe, Kurven-Rahmen. Aufruf bei Grössenänderung."""
        bg = _modus_farbe(config.FARBEN["flaeche"])
        text = _modus_farbe(config.FARBEN["text"])
        leise = _modus_farbe(config.FARBEN["text_leise"])
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
        for xm, n, farbe in ((xl, self.ta_N1, GRUEN), (xr, self.ta_N2, ORANGE)):
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
        c.create_text(xs, ys, text="═" if self.ta_dc else "~", fill=GRUEN, font=(config.SCHRIFT, int(r * 1.1), "bold"))
        c.create_text(xs - r - 0.01 * w, ys, anchor="e", text="U1", fill=GRUEN, font=schrift)

        # ---- Sekundärkreis: Lampe rechts ----
        xla, yla = 0.90 * w, ys
        ecke_rechts = xr + 0.85 * d
        c.create_line(ecke_rechts, yt, xla, yt, xla, yla - r, fill=ORANGE, width=2)
        c.create_line(ecke_rechts, yb, xla, yb, xla, yla + r, fill=ORANGE, width=2)
        c.create_text(xla + r + 0.01 * w, yla, anchor="w", text="Last", fill=ORANGE, font=schrift)

        # ---- Beschriftung der Spulen ----
        c.create_text(xl, y1 + 0.035 * h, text=f"Primär  N1 = {self.ta_N1:.0f}", fill=GRUEN, font=schrift)
        c.create_text(xr, y1 + 0.035 * h, text=f"Sekundär  N2 = {self.ta_N2:.0f}", fill=ORANGE, font=schrift)

        # ---- Rahmen der drei Kurven ----
        kurven = []
        for k, (titel, farbe) in enumerate((("① U1 (primär)", GRUEN), ("② Φ Magnetfeld", BLAU),
                                            ("③ U2 (sekundär)", ORANGE))):
            px0 = w * (0.02 + k * 0.33)
            px1 = px0 + 0.30 * w
            py0, py1 = 0.66 * h, 0.97 * h
            c.create_rectangle(px0, py0, px1, py1, outline=_modus_farbe(config.FARBEN["rahmen"]))
            c.create_line(px0, (py0 + py1) / 2, px1, (py0 + py1) / 2, fill=_modus_farbe(config.FARBEN["rahmen"]),
                          dash=(2, 3))
            c.create_text(px0 + 4, py0 - 0.02 * h, anchor="w", text=titel, fill=farbe, font=schrift)
            kurven.append((px0, px1, py0, py1, farbe))
        c.create_text(w * 0.98, 0.62 * h, anchor="e", fill=leise, font=klein,
                      text="Zeit →  (rechts = jetzt)")

        # ---- Geometrie merken (für die bewegten Teile) ----
        self.ta_geo = {
            "w": w, "h": h, "xl": xl, "xr": xr, "yc0": y0 + d / 2, "yc1": y1 - d / 2, "d": d,
            "lampe": (xla, yla, r), "kurven": kurven,
            "pfad1": _Pfad([(xs, ys - r), (xs, yt), (ecke_links, yt), (ecke_links, yb), (xs, yb), (xs, ys + r)]),
            "pfad2": _Pfad([(ecke_rechts, yb), (ecke_rechts, yt), (xla, yt), (xla, yla - r),
                            (xla, yla + r), (xla, yb), (ecke_rechts, yb)]),
            "text": text, "canvas": c,     # Zeichenfläche merken (self.ta_canvas existiert evtl. noch nicht)
        }
        self._ta_dynamisch()

    # =========================================================================
    # ZEICHNEN - bewegt (alle 40 ms)
    # =========================================================================
    def _ta_dynamisch(self):
        g = self.ta_geo
        if g is None:
            return
        c = g["canvas"]
        c.delete("dyn")
        u1, phi, u2 = self._ta_signale(self.ta_zeit)

        # ---- Magnetfeld: Pfeile im Kern (oben →, unten ← bei positivem Φ) ----
        laenge = 0.06 * g["w"] * min(abs(phi), 1.0)
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
                          font=(config.SCHRIFT, max(10, int(g["h"] / 16 * (0.4 + 0.6 * min(abs(phi), 1)))), "bold"))
        if self._ta_fluss() > 1.5 and not self.ta_dc:
            c.create_text(0.5 * g["w"], g["yc1"] - 0.06 * g["h"], text="Sättigung!", fill=ROT, tags="dyn",
                          font=(config.SCHRIFT, max(8, int(g["h"] / 30)), "bold"))

        # ---- Strom-Punkte auf den Leitungen ----
        radius = max(2.5, g["h"] / 110)
        for pfad, pos, farbe in ((g["pfad1"], self.ta_s1, GRUEN), (g["pfad2"], self.ta_s2, ORANGE)):
            for k in range(10):
                x, y = pfad.position(pos + k / 10)
                c.create_oval(x - radius, y - radius, x + radius, y + radius, fill=farbe, outline="", tags="dyn")

        # ---- Lampe: Helligkeit nach U2 (AC: Effektivwert, DC: aktueller Impuls) ----
        xla, yla, r = g["lampe"]
        u2_eff = self.ta_U1 * self.ta_N2 / self.ta_N1
        hell = min(1.0, (abs(u2) * U_SKALA if self.ta_dc else u2_eff) / 230)
        bg = _modus_farbe(config.FARBEN["flaeche"])
        if hell > 0.05:
            glow = r * (1.3 + 1.2 * hell)
            c.create_oval(xla - glow, yla - glow, xla + glow, yla + glow, outline="", tags="dyn",
                          fill=_mischen(bg, "#FFD54A", 0.35 * hell))
        c.create_oval(xla - r, yla - r, xla + r, yla + r, outline=ORANGE, width=2, tags="dyn",
                      fill=_mischen(bg, "#FFE066", hell))
        k = r * 0.6
        c.create_line(xla - k, yla - k, xla + k, yla + k, fill=ORANGE, width=2, tags="dyn")
        c.create_line(xla - k, yla + k, xla + k, yla - k, fill=ORANGE, width=2, tags="dyn")

        # ---- Drei "Oszilloskope": die letzten 2.5 Perioden ----
        fenster = 2.5 / F_ANIM
        for idx, (px0, px1, py0, py1, farbe) in enumerate(g["kurven"]):
            mitte, amp = (py0 + py1) / 2, (py1 - py0) * 0.42
            punkte = []
            for i in range(61):
                t = self.ta_zeit - fenster * (1 - i / 60)
                wert = max(-1.15, min(1.15, self._ta_signale(t)[idx]))
                punkte += [px0 + (px1 - px0) * i / 60, mitte - amp * wert]
            c.create_line(*punkte, fill=farbe, width=2, tags="dyn")
            aktuell = max(-1.15, min(1.15, (u1, phi, u2)[idx]))
            c.create_oval(px1 - 4, mitte - amp * aktuell - 4, px1 + 4, mitte - amp * aktuell + 4,
                          fill=farbe, outline="", tags="dyn")

    # =========================================================================
    # ANIMATIONS-SCHLEIFE
    # =========================================================================
    def _ta_schleife(self):
        if not hasattr(self, "ta_canvas") or not self.ta_canvas.winfo_exists():
            return                                          # Seite verlassen -> Ende
        jetzt = time.monotonic()
        dt = min(0.1, jetzt - self.ta_letzt)                # nach Pausen keine grossen Sprünge
        self.ta_letzt = jetzt
        if not self.ta_canvas.winfo_ismapped():
            self.after(300, self._ta_schleife)              # unsichtbar -> nur selten nachsehen
            return
        if self.ta_laeuft:
            self.ta_zeit += dt
            u1, _phi, u2 = self._ta_signale(self.ta_zeit)
            # Stromgeschwindigkeit: AC ~ Momentanwert; DC primär: konstant hoher Strom
            i1 = 0.9 if self.ta_dc and self.ta_U1 > 0 else u1
            self.ta_s1 = (self.ta_s1 + i1 * dt * 0.35) % 1.0
            self.ta_s2 = (self.ta_s2 + max(-1.5, min(1.5, u2)) * dt * 0.35) % 1.0
            self._ta_dynamisch()
        self.after(FRAME_MS, self._ta_schleife)
