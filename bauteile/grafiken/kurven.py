# =============================================================================
# bauteile/grafiken/kurven.py
# -----------------------------------------------------------------------------
# INTERAKTIVE KURVE: Laden/Entladen (RC) bzw. Ein-/Ausschalten (RL).
#
#   ┌───────────────────────────────────────────────┐
#   │ R [10  ][kΩ]  C [100][µF]  U0 [5][V]  [Laden|Entladen]
#   │  U │         ●───────────────                 │
#   │    │     ╱   ┊                                │
#   │    │   ╱     ┊   63 %  86 %  95 %             │
#   │    │ ╱       ┊                                │
#   │    └────────τ────2τ────3τ────4τ────5τ── t      │
#   │  Zeit t: ──────●────────  [ 1 ][s ▾]  (Regler + Zahlenfeld, 0 … 5τ)
#   │  t = 1.00 s (1.0 τ)  →  u = 3.16 V (63.2 %)   │
#   └───────────────────────────────────────────────┘
#
#   modus="RC"  Kondensatorspannung u_C(t)   (bauteile/rechner/kondensator_rechner.py)
#   modus="RL"  Spulenstrom i_L(t)           (bauteile/rechner/spule_rechner.py)
#
# Die Kurve zeichnet sich bei jeder Fenstergrösse neu (core/layout.py ResponsiveCanvas).
# Beim Verschieben des Reglers wird NUR die Markierung neu gezeichnet (schnell).
# =============================================================================

import math

import customtkinter as ctk

import config                                                   # -> config.py
from bauteile.einheiten import formatieren as fmt               # -> bauteile/einheiten.py
from bauteile.rechner.basis import EinheitenEingabe, WertRegler # -> rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel      # -> core/layout.py

PUNKTE = 120          # Stützpunkte der Kurve
T_MAX = 5.0           # Kurve bis 5 τ


def _farbe(paar):
    return paar[1] if ctk.get_appearance_mode() == "Dark" else paar[0]


class KurvenKarte(Karte):

    # Texte und Einheiten je Modus
    MODI = {
        "RC": {"titel": "📈 Kondensator laden & entladen (interaktiv)",
               "unter": "Werte ändern, Enter drücken – dann am Regler die Zeit verschieben",
               "bauteil": ("C", "kapazitaet", "µF", "100"), "r_start": ("10", "kΩ"), "achse": "u_C", "groesse": "spannung",
               "schalter": ["Laden", "Entladen"]},
        "RL": {"titel": "📈 Spule ein- & ausschalten (interaktiv)",
               "unter": "Strom durch die Spule nach dem Einschalten bzw. Ausschalten (mit Freilaufdiode)",
               "bauteil": ("L", "induktivitaet", "mH", "100"), "r_start": ("100", "Ω"), "achse": "i_L", "groesse": "strom",
               "schalter": ["Einschalten", "Ausschalten"]},
    }

    def __init__(self, master, modus="RC"):
        self.ku_modus = modus
        info = self.MODI[modus]
        super().__init__(master, titel=info["titel"], untertitel=info["unter"])
        b = self.body
        # Startwerte VOR dem Canvas setzen (der Canvas kann sofort zeichnen wollen)
        self.ku_tau, self.ku_end, self.ku_R, self.ku_U = 1.0, 1.0, 1.0, 1.0
        self.ku_groesse = (0, 0)
        self.ku_regler = None

        # ---- Eingaben ----
        eingaben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        eingaben.grid(row=0, column=0, sticky="w")
        name, typ, einheit, start = info["bauteil"]
        r_wert, r_einheit = info["r_start"]
        self.ku_r = self._feld(eingaben, 0, "R", "widerstand", r_einheit, r_wert)
        self.ku_x = self._feld(eingaben, 1, name, typ, einheit, start)
        self.ku_u = self._feld(eingaben, 2, "U0", "spannung", "V", "5")
        self.ku_art = ctk.CTkSegmentedButton(b, values=info["schalter"], command=lambda _v: self.ku_neu())
        self.ku_art.set(info["schalter"][0])
        self.ku_art.grid(row=1, column=0, sticky="w", pady=(8, 4))

        # ---- Kurve (wächst mit der Breite) ----
        self.ku_canvas = ResponsiveCanvas(b, self._zeichnen, seitenverhaeltnis=0.45, max_hoehe=360)
        self.ku_canvas.grid(row=2, column=0, sticky="ew", pady=(4, 4))

        # ---- Zeit-Regler: echte Zeit (s, ms, µs), Bereich 0 … 5τ ----
        # Slider + Zahlenfeld + Einheit -> bauteile/rechner/basis.py WertRegler
        self.ku_regler = WertRegler(b, "Zeit t", "zeit", 0, T_MAX * self.ku_tau, self.ku_tau,
                                    schritte=500, bei_aenderung=self._marker, text_breite=60)
        self.ku_regler.grid(row=3, column=0, sticky="ew")

        self.ku_anzeige = WrapLabel(b, text="", font=(config.SCHRIFT_CODE, 13, "bold"),
                                    text_color=config.FARBEN["akzent"])
        self.ku_anzeige.grid(row=4, column=0, sticky="ew", pady=(6, 0))

        self.ku_neu()

    def _feld(self, rahmen, spalte, text, typ, einheit, start):
        ctk.CTkLabel(rahmen, text=text, anchor="w").grid(row=0, column=spalte * 2, padx=(0 if spalte == 0 else 12, 4))
        feld = EinheitenEingabe(rahmen, typ, "", einheit, breite=70)
        feld.ee_feld.insert(0, start)
        feld.grid(row=0, column=spalte * 2 + 1)
        feld.bei_enter(self.ku_neu)
        return feld

    # -------------------------------------------------------------------------
    def ku_neu(self):
        """Werte lesen, τ berechnen, Kurve neu zeichnen."""
        try:
            R, X, U = self.ku_r.wert(), self.ku_x.wert(), self.ku_u.wert()
            if not R or not X or not U or R <= 0 or X <= 0:
                raise ValueError("R, " + ("C" if self.ku_modus == "RC" else "L") + " und U0 > 0 eingeben")
        except ValueError as fehler:
            self.ku_anzeige.configure(text=f"⚠ {fehler}", text_color=("#B45309", "#F59E0B"))
            return
        self.ku_R = R
        tau_alt = self.ku_tau
        if self.ku_modus == "RC":
            self.ku_tau = R * X
            self.ku_end = U                          # Endspannung
        else:
            self.ku_tau = X / R
            self.ku_end = U / R                      # Endstrom
        self.ku_U = U
        # Zeit-Regler auf 0 … 5τ einstellen, an derselben Stelle (gleiches Vielfaches von τ) bleiben
        n_tau = self.ku_regler.wert() / tau_alt if tau_alt > 0 else 1.0
        self.ku_regler.bereich_setzen(0, T_MAX * self.ku_tau, n_tau * self.ku_tau)
        breite, hoehe = self.ku_groesse
        if breite > 1:
            self.ku_canvas.delete("all")
            self._zeichnen(self.ku_canvas, breite, hoehe)
        else:
            self._marker()

    def _steigend(self):
        return self.ku_art.get() == self.MODI[self.ku_modus]["schalter"][0]

    def _wert(self, n_tau):
        """Relativer Wert 0..1 nach n_tau Zeitkonstanten."""
        return 1 - math.exp(-n_tau) if self._steigend() else math.exp(-n_tau)

    # -------------------------------------------------------------------------
    def _koord(self):
        w, h = self.ku_groesse
        links, rechts, oben, unten = 0.10 * w, 0.96 * w, 0.08 * h, 0.82 * h
        return links, rechts, oben, unten

    def _zeichnen(self, c, w, h):
        """Achsen, Hilfslinien bei τ, 2τ ... und die Kurve (wird bei Grössenänderung aufgerufen)."""
        self.ku_groesse = (w, h)
        links, rechts, oben, unten = self._koord()
        text = _farbe(config.FARBEN["text_leise"])
        linie = _farbe(config.FARBEN["rahmen"])
        schrift = (config.SCHRIFT, max(8, int(h / 26)))

        def x(n):
            return links + (rechts - links) * n / T_MAX

        def y(v):
            return unten - (unten - oben) * v

        # Raster + Beschriftung Zeitachse
        for n in range(0, 6):
            c.create_line(x(n), oben, x(n), unten, fill=linie, dash=(2, 4))
            c.create_text(x(n), unten + 0.06 * h, text="0" if n == 0 else f"{n}τ", fill=text, font=schrift)
            if n:
                c.create_text(x(n), unten + 0.13 * h, text=fmt(n * self.ku_tau, "zeit", 3), fill=text,
                              font=(config.SCHRIFT, max(7, int(h / 32))))
        for anteil in (0, 0.5, 1):
            c.create_line(links, y(anteil), rechts, y(anteil), fill=linie, dash=(2, 4))
            c.create_text(links - 0.01 * w, y(anteil), anchor="e", fill=text, font=schrift,
                          text=fmt(anteil * self.ku_end, self.MODI[self.ku_modus]["groesse"], 3))
        # Achsen
        c.create_line(links, unten, rechts, unten, fill=text, width=2, arrow="last")
        c.create_line(links, unten, links, oben - 0.03 * h, fill=text, width=2, arrow="last")
        c.create_text(links + 0.01 * w, oben - 0.035 * h, anchor="w", fill=text, font=schrift,
                      text=self.MODI[self.ku_modus]["achse"])

        # Prozentmarken bei 1τ … 5τ
        for n in range(1, 6):
            v = self._wert(n)
            c.create_oval(x(n) - 3, y(v) - 3, x(n) + 3, y(v) + 3, fill=text, outline="")
            c.create_text(x(n) + 4, y(v) + (12 if self._steigend() else -12), anchor="w", fill=text,
                          font=(config.SCHRIFT, max(7, int(h / 32))), text=f"{v * 100:.1f} %")

        # Kurve
        punkte = []
        for i in range(PUNKTE + 1):
            n = T_MAX * i / PUNKTE
            punkte += [x(n), y(self._wert(n))]
        c.create_line(*punkte, fill="#3B82F6", width=3, smooth=True)

        # Tangente im Startpunkt: schneidet den Endwert genau bei 1τ (klassischer Merksatz)
        if self._steigend():
            c.create_line(x(0), y(0), x(1), y(1), fill="#9AA1AD", dash=(6, 4))
        else:
            c.create_line(x(0), y(1), x(1), y(0), fill="#9AA1AD", dash=(6, 4))
        self._marker()

    def _marker(self):
        """Nur die Markierung (senkrechte Linie + Punkt) neu zeichnen und Werte anzeigen."""
        w, h = self.ku_groesse
        if w <= 1 or self.ku_regler is None:
            return
        c = self.ku_canvas
        c.delete("marker")
        links, rechts, oben, unten = self._koord()
        n = self.ku_regler.wert() / self.ku_tau             # Zeit in Vielfachen von τ
        v = self._wert(n)
        px = links + (rechts - links) * n / T_MAX
        py = unten - (unten - oben) * v
        c.create_line(px, oben, px, unten, fill="#F59E0B", width=2, tags="marker")
        c.create_oval(px - 7, py - 7, px + 7, py + 7, fill="#F59E0B", outline="white", width=2, tags="marker")

        t = n * self.ku_tau
        groesse = self.MODI[self.ku_modus]["groesse"]
        zeilen = [f"t = {fmt(t, 'zeit')}  ({n:.2f} τ)   →   "
                  f"{self.MODI[self.ku_modus]['achse']} = {fmt(v * self.ku_end, groesse)}  ({v * 100:.1f} %)"]
        if self.ku_modus == "RC":
            # Strom durch R: beim Laden (U0-u)/R, beim Entladen u/R (entgegengesetzt)
            i = self.ku_U * (1 - v if self._steigend() else v) / self.ku_R
            zeilen.append(f"Strom durch R: {fmt(i, 'strom')}   ·   τ = R·C = {fmt(self.ku_tau, 'zeit')}")
        else:
            u_l = self.ku_U * (1 - v) if self._steigend() else None
            zeilen.append(f"Spannung an L: {fmt(u_l, 'spannung')}   ·   τ = L/R = {fmt(self.ku_tau, 'zeit')}"
                          if u_l is not None else
                          f"Freilaufdiode hält den Strom am Fliessen   ·   τ = L/R = {fmt(self.ku_tau, 'zeit')}")
        self.ku_anzeige.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
