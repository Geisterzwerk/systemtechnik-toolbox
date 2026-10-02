# =============================================================================
# digitaltechnik/grafiken_schaltwerke.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE der Schaltwerke (mit Speicher und Takt):
#
#   FlipflopKarte          RS-Latch, D-Latch, D-, JK-, T-Flipflop: Eingänge setzen, Takt geben, Zeitdiagramm
#   ZaehlerKarte           asynchroner und synchroner Zähler (auf/ab, modulo m), Zwischenzustände sichtbar
#   SchieberegisterKarte   seriell (SIPO), Ringzähler, Johnson-Zähler – Takt für Takt
#
#   zeitdiagramm()         zeichnet digitale Signale untereinander (Treppenkurven), auch mit feiner Zeitachse
#
# Rechnung: digitaltechnik/schaltwerke_mathe.py
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_flipflop")
# Eigene Namen beginnen mit dg_ (keine Kollision mit tkinter).
# =============================================================================

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile.grafiken.schaltplan import OK, WARN                      # -> bauteile/grafiken/schaltplan.py
from bauteile.rechner.basis import WertRegler                          # -> bauteile/rechner/basis.py
from core.layout import Karte, ResponsiveCanvas                        # -> core/layout.py
from digitaltechnik import schaltwerke_mathe as swm                    # -> digitaltechnik/schaltwerke_mathe.py
from digitaltechnik.grafiken import BitLeiste, _erklaerung, _ergebnis_label, _farbe   # -> digitaltechnik/grafiken.py

EINS, NULL_FARBE, ORANGE, ROT, BLAU = "#22C55E", "#6B7280", "#F59E0B", "#EF4444", "#3B82F6"
SIGNAL_FARBEN = {"CLK": "#A855F7", "C": "#A855F7", "Q": EINS}


def zeitdiagramm(c, x0, x1, y0, y1, signale, schrift, leise, markierungen=()):
    """
    signale: [(name, [werte …], farbe), …] – alle Listen gleich lang, ein Wert je Zeitschritt
             (0/1, None = unbestimmt X, "Z" = hochohmig).
    markierungen: [(schritt, farbe), …] senkrechte Hilfslinien (z.B. Taktflanken, Glitches).
    """
    if not signale or not signale[0][1]:
        return
    n = len(signale[0][1])
    zeile = (y1 - y0) / len(signale)
    dx = (x1 - x0) / n
    for schritt, farbe in markierungen:
        c.create_line(x0 + schritt * dx, y0, x0 + schritt * dx, y1, fill=farbe, dash=(2, 3))
    for k, (name, werte, farbe) in enumerate(signale):
        oben, unten = y0 + k * zeile + zeile * 0.18, y0 + (k + 1) * zeile - zeile * 0.18
        c.create_text(x0 - 6, (oben + unten) / 2, text=name, anchor="e", fill=farbe, font=schrift)
        c.create_line(x0, unten, x1, unten, fill=leise, dash=(1, 4))
        punkte = []
        for i, w in enumerate(werte):
            y = unten if not w else oben
            if w == "Z":                                           # hochohmig (Leitung frei): Mitte
                y = (oben + unten) / 2
            elif w is None:                                        # unbestimmt: Mitte, gestrichelt dargestellt
                c.create_rectangle(x0 + i * dx, oben, x0 + (i + 1) * dx, unten, outline=ROT, dash=(2, 2))
                y = (oben + unten) / 2
            punkte += [x0 + i * dx, y, x0 + (i + 1) * dx, y]
        c.create_line(*punkte, fill=farbe, width=2)


def _knopf_stil(knopf, name, wert):
    knopf.configure(text=f"{name} = {wert}", fg_color=config.FARBEN["akzent"] if wert else config.FARBEN["rahmen"],
                    text_color=("#FFFFFF", "#FFFFFF") if wert else config.FARBEN["text"])


# =============================================================================
# FLIPFLOPS
# =============================================================================
class FlipflopKarte(Karte):
    EINGAENGE = {"RS-Latch": ["S", "R"], "D-Latch": ["D", "C"], "D-Flipflop": ["D"], "JK-Flipflop": ["J", "K"],
                 "T-Flipflop": ["T"]}
    LAENGE = 24                                    # so viele Zeitschritte zeigt das Diagramm

    def __init__(self, master):
        super().__init__(master, titel="⏱️ Flipflops und Latches (interaktiv)",
                         untertitel="Eingänge setzen, dann „Takt ↑“ – das Zeitdiagramm zeichnet alles mit")
        b = self.body
        self.dg_e, self.dg_q, self.dg_verlauf, self.dg_hinweis = {}, 0, [], ""
        self.dg_art = ctk.CTkSegmentedButton(b, values=swm.FLIPFLOP_ARTEN, command=lambda _v: self._dg_art_neu())
        self.dg_art.set("D-Flipflop")
        self.dg_art.grid(row=0, column=0, sticky="w")
        self.dg_knoepfe_rahmen = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        self.dg_knoepfe_rahmen.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.4, max_hoehe=340)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Ein Flipflop speichert ein Bit. Das RS-LATCH reagiert sofort: S setzt, "
                       "R setzt zurück, S = R = 1 ist verboten. Das D-LATCH ist pegelgesteuert: Solange C = 1, folgt Q "
                       "dem Eingang D (transparent), bei C = 0 hält es den Wert. FLIPFLOPS sind flankengesteuert "
                       "(Dreieck am Takteingang): Sie übernehmen nur im Moment der steigenden Flanke – dazwischen "
                       "dürfen sich die Eingänge ändern, ohne dass etwas passiert. Das D-Flipflop speichert D, das JK "
                       "kann zusätzlich toggeln (J = K = 1), das T-Flipflop toggelt bei T = 1 – zwei T-Flipflops "
                       "hintereinander teilen die Frequenz durch 4.").grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self._dg_art_neu()

    def _dg_art(self):
        return self.dg_art.get()

    def _dg_flanke(self):
        return self._dg_art() in ("D-Flipflop", "JK-Flipflop", "T-Flipflop")

    def _dg_art_neu(self):
        for kind in self.dg_knoepfe_rahmen.winfo_children():
            kind.destroy()
        self.dg_e = {name: 0 for name in self.EINGAENGE[self._dg_art()]}
        self.dg_knoepfe = {}
        for i, name in enumerate(self.EINGAENGE[self._dg_art()]):
            k = ctk.CTkButton(self.dg_knoepfe_rahmen, text="", width=86, height=30, font=(config.SCHRIFT_CODE, 13, "bold"),
                              command=lambda name=name: self._dg_eingang(name))
            k.grid(row=0, column=i, padx=(0, 8))
            self.dg_knoepfe[name] = k
        spalte = len(self.dg_knoepfe)
        if self._dg_flanke():
            ctk.CTkButton(self.dg_knoepfe_rahmen, text="Takt ↑", width=90, height=30, fg_color="#7C3AED",
                          hover_color="#6D28D9", command=self._dg_takt).grid(row=0, column=spalte, padx=(12, 8))
            spalte += 1
        ctk.CTkButton(self.dg_knoepfe_rahmen, text="Neu", width=60, height=30, fg_color="transparent", border_width=1,
                      text_color=config.FARBEN["text"], command=self._dg_art_neu).grid(row=0, column=spalte, padx=(8, 0))
        self.dg_q, self.dg_verlauf, self.dg_hinweis = 0, [], "Startzustand Q = 0"
        self._dg_aufzeichnen(0)
        self._dg_neu()

    def _dg_aufzeichnen(self, clk):
        self.dg_verlauf.append({"clk": clk, **self.dg_e, "q": self.dg_q,
                                "verboten": self._dg_art() == "RS-Latch" and self.dg_e.get("S") and self.dg_e.get("R")})
        self.dg_verlauf = self.dg_verlauf[-self.LAENGE:]

    def _dg_eingang(self, name):
        self.dg_e[name] ^= 1
        if not self._dg_flanke():                       # Latches reagieren sofort auf den Pegel
            self.dg_q, self.dg_hinweis = swm.naechster_zustand(self._dg_art(), self.dg_q, self.dg_e)
        else:
            self.dg_hinweis = f"{name} = {self.dg_e[name]} – ohne Taktflanke ändert sich Q nicht"
        self._dg_aufzeichnen(0)
        self._dg_neu()

    def _dg_takt(self):
        self.dg_q, self.dg_hinweis = swm.naechster_zustand(self._dg_art(), self.dg_q, self.dg_e)
        self.dg_hinweis = "↑ Flanke: " + self.dg_hinweis
        self._dg_aufzeichnen(1)
        self._dg_aufzeichnen(1)
        self._dg_aufzeichnen(0)
        self._dg_neu()

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        for name, k in self.dg_knoepfe.items():
            _knopf_stil(k, name, self.dg_e[name])
        art = self._dg_art()
        tabelle = "   ".join(f"{e} → {q}" for e, q in swm.flipflop_tabelle(art))
        verboten = self.dg_verlauf and self.dg_verlauf[-1]["verboten"]
        zeilen = [f"Q = {self.dg_q}   ¬Q = {1 - self.dg_q if not verboten else 0}   ·   {self.dg_hinweis}",
                  f"{swm.KENN_GLEICHUNG[art]}",
                  tabelle]
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=WARN if verboten else config.FARBEN["akzent"])
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    def _dg_zeichnen(self, c, w, h):
        if not hasattr(self, "dg_ergebnis") or not self.dg_verlauf:
            return
        art = self._dg_art()
        text, leise = _farbe(config.FARBEN["text"]), _farbe(config.FARBEN["text_leise"])
        g = max(8, int(min(w / 2.4, h) / 16))
        schrift, fett = (config.SCHRIFT, g), (config.SCHRIFT, g, "bold")
        dick = max(2, int(h / 120))
        # ---- Symbol (IEC) ----
        x0, x1 = w * 0.08, w * 0.22
        y0, y1 = h * 0.14, h * 0.86
        c.create_rectangle(x0, y0, x1, y1, outline=text, width=dick)
        namen = self.EINGAENGE[art] + (["C1"] if self._dg_flanke() else [])
        for i, name in enumerate(namen):
            y = y0 + (y1 - y0) * (i + 1) / (len(namen) + 1)
            wert = self.dg_e.get(name, self.dg_verlauf[-1]["clk"])
            c.create_line(x0 - w * 0.04, y, x0, y, fill=EINS if wert else NULL_FARBE, width=dick)
            c.create_text(x0 + 6, y, text=("1" + name if name in "DJKT" and self._dg_flanke() else name),
                          anchor="w", fill=text, font=schrift)
            if name == "C1":                               # Dreieck = flankengesteuert
                c.create_polygon(x0, y - h * 0.035, x0 + w * 0.012, y, x0, y + h * 0.035, outline=text, fill="", width=dick)
        for i, (name, wert) in enumerate((("Q", self.dg_q), ("¬Q", 1 - self.dg_q))):
            y = y0 + (y1 - y0) * (i + 1) / 3
            c.create_line(x1, y, x1 + w * 0.04, y, fill=EINS if wert else NULL_FARBE, width=dick)
            r = max(5, h * 0.035)
            c.create_oval(x1 + w * 0.04, y - r, x1 + w * 0.04 + 2 * r, y + r, fill=EINS if wert else NULL_FARBE, outline="")
            c.create_text(x1 - 6, y, text=name, anchor="e", fill=text, font=fett)
        c.create_text((x0 + x1) / 2, y0 - 4, text=art, anchor="s", fill=leise, font=schrift)
        # ---- Zeitdiagramm ----
        signale = []
        if self._dg_flanke():
            signale.append(("CLK", [v["clk"] for v in self.dg_verlauf], SIGNAL_FARBEN["CLK"]))
        for name in self.EINGAENGE[art]:
            signale.append((name, [v[name] for v in self.dg_verlauf], SIGNAL_FARBEN.get(name, BLAU)))
        signale.append(("Q", [None if v["verboten"] else v["q"] for v in self.dg_verlauf], EINS))
        flanken = [(i, "#7C3AED") for i in range(1, len(self.dg_verlauf))
                   if self.dg_verlauf[i]["clk"] and not self.dg_verlauf[i - 1]["clk"]]
        zx0 = w * 0.38
        zx1 = zx0 + (w * 0.96 - zx0) * len(self.dg_verlauf) / self.LAENGE
        zeitdiagramm(c, zx0, zx1, h * 0.08, h * 0.95, signale, schrift, leise, flanken)


# =============================================================================
# ZÄHLER
# =============================================================================
class ZaehlerKarte(Karte):
    ARTEN = ["asynchron (Ripple)", "synchron"]
    UNTER = 24                                     # Zeitschritte je Taktperiode (für die Verzögerungen)

    def __init__(self, master):
        super().__init__(master, titel="🔢 Zähler: asynchron und synchron (interaktiv)",
                         untertitel="Modulo und Richtung einstellen – beim asynchronen Zähler die Zwischenzustände beachten")
        b = self.body
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        self.dg_art = ctk.CTkSegmentedButton(oben, values=self.ARTEN, command=lambda _v: self._dg_neu())
        self.dg_art.set(self.ARTEN[0])
        self.dg_art.grid(row=0, column=0, padx=(0, 12))
        self.dg_richtung = ctk.CTkSegmentedButton(oben, values=["aufwärts", "abwärts"], command=lambda _v: self._dg_neu())
        self.dg_richtung.set("aufwärts")
        self.dg_richtung.grid(row=0, column=1)
        self.dg_modulo = WertRegler(b, "Modulo m (Zustände)", "zahl", 2, 16, 10, ganzzahl=True,
                                    bei_aenderung=self._dg_neu, text_breite=150)
        self.dg_modulo.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.42, max_hoehe=360)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  ASYNCHRON: Nur das erste Flipflop bekommt den Takt, jedes weitere wird "
                       "vom Ausgang des vorigen getaktet. Einfach, aber die Bits kippen nacheinander – beim Übergang "
                       "0111 → 1000 erscheinen kurz 0110, 0100 und 0000 (rote Linien). Ein Modulo-Zähler, der beim "
                       "Erreichen von m asynchron zurückgesetzt wird, zeigt m kurz an (Glitch). SYNCHRON: Alle "
                       "Flipflops hängen am selben Takt und schalten gleichzeitig; eine Logik bestimmt, welche toggeln. "
                       "Q0 hat die halbe Taktfrequenz, jedes weitere Bit wieder die Hälfte – ein Zähler ist auch ein "
                       "Frequenzteiler (höchstes Bit: f / m).").grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self.dg_d = None
        self._dg_neu()

    def _dg_daten(self):
        m = int(round(self.dg_modulo.wert()))
        bits = max(1, (m - 1).bit_length())
        ab = self.dg_richtung.get() == "abwärts"
        asyn = self.dg_art.get() == self.ARTEN[0]
        perioden = m + 1
        folge = swm.zaehler_folge(bits, m, ab, schritte=perioden)
        werte, glitches = [], []                       # werte: Zustand je feinem Zeitschritt
        d = max(1, self.UNTER // (3 * bits))           # Verzögerung je Stufe (asynchron)
        for p in range(perioden):
            # Periode 0 zeigt den Startzustand; ab Periode 1 schaltet die steigende Flanke am Periodenanfang weiter
            alt, neu = (folge[0], folge[0]) if p == 0 else (folge[p - 1], folge[p])
            if p == 0:
                zwischen = [alt]
            elif asyn and not ab:
                zwischen = swm.ripple_uebergang(alt, bits, m)
            elif asyn:                                  # abwärts: Bits kippen ebenfalls nacheinander
                zwischen, z = [alt], alt
                for i in range(bits):
                    z ^= 1 << i
                    zwischen.append(z)
                    if not (z >> i) & 1:
                        break
                if zwischen[-1] != neu:
                    zwischen.append(neu)
            else:
                zwischen = [alt, neu]
            for t in range(self.UNTER):
                if asyn:
                    stufe = min(t // d, len(zwischen) - 1) if t >= 1 else 0
                    werte.append(zwischen[stufe])
                    if 0 < stufe < len(zwischen) - 1 and t % d == 0:
                        glitches.append(p * self.UNTER + t)
                else:
                    werte.append(alt if t < 1 else neu)
        return {"m": m, "bits": bits, "folge": folge[:m + 1], "werte": werte, "glitches": glitches,
                "perioden": perioden, "asyn": asyn, "ab": ab}

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        self.dg_d = d = self._dg_daten()
        m, bits = d["m"], d["bits"]
        uebergang = ""
        if d["asyn"] and not d["ab"]:
            beispiel = 2 ** (bits - 1) - 1 if 2 ** (bits - 1) < m else m - 1
            kette = swm.ripple_uebergang(beispiel, bits, m)
            uebergang = ("Übergang " + " → ".join(format(z, f"0{bits}b") for z in kette) +
                         f"   ({len(kette) - 2} falsche Zwischenwerte)")
        zeilen = [f"{bits} Flipflops, {m} Zustände: " + ", ".join(map(str, d["folge"][:m])) +
                  (" …" if m > 16 else ""),
                  f"Frequenzen: Q0 = f/2 (bei Zweierpotenz) … höchstes Bit Q{bits - 1}: f / {m}" +
                  ("" if m == 2 ** bits else "  (Tastgrad ≠ 50 %, weil m keine Zweierpotenz ist)")]
        if uebergang:
            zeilen.append(uebergang)
        if d["asyn"] and m != 2 ** bits:
            zeilen.append(f"⚠ Asynchrones Rücksetzen bei {m}: Zustand {m} ist kurz sichtbar (Glitch) – "
                          "für saubere Ausgänge synchron zählen")
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=WARN if d["asyn"] else OK)
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    def _dg_zeichnen(self, c, w, h):
        d = self.dg_d
        if d is None:
            return
        leise = _farbe(config.FARBEN["text_leise"])
        text = _farbe(config.FARBEN["text"])
        g = max(7, int(min(w / 2.2, h) / 18))
        schrift = (config.SCHRIFT, g)
        n = len(d["werte"])
        clk = [1 if (t % self.UNTER) < self.UNTER // 2 else 0 for t in range(n)]
        signale = [("CLK", clk, SIGNAL_FARBEN["CLK"])]
        for i in range(d["bits"]):
            signale.append((f"Q{i}", [(z >> i) & 1 for z in d["werte"]], EINS))
        x0, x1, y0, y1 = w * 0.08, w * 0.98, h * 0.12, h * 0.98
        markierungen = [(t, ROT) for t in d["glitches"]]
        zeitdiagramm(c, x0, x1, y0, y1, signale, schrift, leise, markierungen)
        dx = (x1 - x0) / n
        for p in range(d["perioden"]):                      # Zählerstand je Periode oben
            z = d["werte"][p * self.UNTER + self.UNTER - 1]
            c.create_text(x0 + (p + 0.55) * self.UNTER * dx, y0 - 4, text=str(z), anchor="s", fill=text, font=schrift)


# =============================================================================
# SCHIEBEREGISTER
# =============================================================================
class SchieberegisterKarte(Karte):
    ARTEN = ["seriell (SIPO)", "Ringzähler", "Johnson-Zähler"]

    def __init__(self, master):
        super().__init__(master, titel="➡️ Schieberegister, Ring- und Johnson-Zähler (interaktiv)",
                         untertitel="Dateneingang setzen und „Takt ↑“ drücken – jedes Bit rückt eine Stelle weiter")
        b = self.body
        self.dg_ein, self.dg_z, self.dg_verlauf = 1, 0, []
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        self.dg_art = ctk.CTkSegmentedButton(oben, values=self.ARTEN, command=lambda _v: self._dg_reset())
        self.dg_art.set(self.ARTEN[0])
        self.dg_art.grid(row=0, column=0, padx=(0, 12))
        self.dg_ein_knopf = ctk.CTkButton(oben, text="", width=110, height=30, command=self._dg_eingang)
        self.dg_ein_knopf.grid(row=0, column=1, padx=(0, 8))
        ctk.CTkButton(oben, text="Takt ↑", width=90, height=30, fg_color="#7C3AED", hover_color="#6D28D9",
                      command=self._dg_takt).grid(row=0, column=2, padx=(0, 8))
        ctk.CTkButton(oben, text="Reset", width=70, height=30, fg_color="transparent", border_width=1,
                      text_color=config.FARBEN["text"], command=self._dg_reset).grid(row=0, column=3)
        self.dg_leiste = BitLeiste(b, 4, None, titel="Q3 Q2 Q1 Q0")
        self.dg_leiste.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.34, max_hoehe=300)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Ein Schieberegister sind D-Flipflops in einer Kette am selben Takt: "
                       "Bei jeder Flanke übernimmt jede Stufe den Wert der vorigen. SERIELL rein, PARALLEL raus (SIPO, "
                       "z.B. 74HC595) macht aus einer Datenleitung 8 Ausgänge – so steuert ein µC viele LEDs mit 3 Pins. "
                       "Der RINGZÄHLER führt den Ausgang zurück an den Eingang: Eine einzelne 1 läuft im Kreis (n "
                       "Zustände, 1-aus-n ohne Decoder). Der JOHNSON-Zähler führt den INVERTIERTEN Ausgang zurück: "
                       "2n Zustände, und es ändert sich pro Takt nur ein Bit.").grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self._dg_reset()

    def _dg_art_kurz(self):
        return {"seriell (SIPO)": "seriell", "Ringzähler": "Ring", "Johnson-Zähler": "Johnson"}[self.dg_art.get()]

    def _dg_reset(self):
        self.dg_z = 0b0001 if self._dg_art_kurz() == "Ring" else 0
        self.dg_verlauf = [self.dg_z]
        self._dg_neu()

    def _dg_eingang(self):
        self.dg_ein ^= 1
        self._dg_neu()

    def _dg_takt(self):
        self.dg_z = swm.schieberegister(4, [self.dg_ein], self._dg_art_kurz(), self.dg_z)[-1]
        self.dg_verlauf = (self.dg_verlauf + [self.dg_z])[-16:]
        self._dg_neu()

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        art = self._dg_art_kurz()
        if art == "seriell":
            self.dg_ein_knopf.grid()
            _knopf_stil(self.dg_ein_knopf, "Eingang", self.dg_ein)
        else:
            self.dg_ein_knopf.grid_remove()
        self.dg_leiste.zeigen(self.dg_z)
        zustaende = {"seriell": "beliebig (16 Muster)", "Ring": "4 Zustände (eine 1 läuft im Kreis)",
                     "Johnson": "8 Zustände (2 · n), pro Takt ändert sich nur ein Bit"}[art]
        rueck = {"seriell": "Q0 ← Eingang", "Ring": "Q0 ← Q3", "Johnson": "Q0 ← ¬Q3"}[art]
        zeilen = [f"Q3 … Q0 = {format(self.dg_z, '04b')}   ·   {rueck}, Q(i) ← Q(i−1)",
                  f"{zustaende}   ·   Verlauf: " + " → ".join(format(z, "04b") for z in self.dg_verlauf[-6:])]
        if art == "Ring" and self.dg_z == 0:
            zeilen.append("⚠ Alle Stufen 0: Der Ringzähler bleibt hängen – er braucht beim Start genau eine 1 (Reset)")
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    def _dg_zeichnen(self, c, w, h):
        if not hasattr(self, "dg_ergebnis"):
            return
        leise = _farbe(config.FARBEN["text_leise"])
        g = max(7, int(min(w / 2.2, h) / 16))
        schritte = []                                   # je Takt 2 Zeitschritte (Takt HIGH, LOW)
        for z in self.dg_verlauf:
            schritte += [z, z]
        clk = [1 if i % 2 == 0 and i > 0 else 0 for i in range(len(schritte))]
        signale = [("CLK", clk, SIGNAL_FARBEN["CLK"])] + [(f"Q{i}", [(z >> i) & 1 for z in schritte], EINS)
                                                         for i in range(4)]
        x0 = w * 0.08
        x1 = x0 + (w * 0.98 - x0) * len(schritte) / 32
        zeitdiagramm(c, x0, x1, h * 0.06, h * 0.96, signale, (config.SCHRIFT, g), leise)
