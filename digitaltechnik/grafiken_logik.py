# =============================================================================
# digitaltechnik/grafiken_logik.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE der Logik:
#
#   GatterKarte     Gatter wählen, Eingänge anklicken -> Ausgang, IEC- und ANSI-Symbol, Wahrheitstabelle
#   AusdruckKarte   boolescher Ausdruck -> Wahrheitstabelle, Minterme, kanonische und minimale DNF/KNF
#   KVKarte         KV-Diagramm (2 … 4 Variablen) anklicken: 0 → 1 → X (don't care), Blöcke + minimale Form
#
#   wahrheitstabelle_text()   Tabelle als Text (ab 16 Zeilen in Blöcken nebeneinander)
#
# Rechnung: digitaltechnik/logik_mathe.py
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_gatter")
# Eigene Namen beginnen mit dg_ (keine Kollision mit tkinter).
# =============================================================================

import math

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile.grafiken.schaltplan import OK, WARN                      # -> bauteile/grafiken/schaltplan.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel             # -> core/layout.py
from digitaltechnik import logik_mathe as lm                           # -> digitaltechnik/logik_mathe.py
from digitaltechnik.grafiken import _erklaerung, _ergebnis_label, _farbe   # -> digitaltechnik/grafiken.py

EINS, NULL_FARBE = "#22C55E", "#6B7280"
GRUPPEN_FARBEN = ["#EF4444", "#3B82F6", "#F59E0B", "#A855F7", "#14B8A6", "#EC4899", "#84CC16", "#F97316"]
IEC_ZEICHEN = {"AND": "&", "NAND": "&", "OR": "≥1", "NOR": "≥1", "XOR": "=1", "XNOR": "=1", "NOT": "1"}


def wahrheitstabelle_text(namen, zeilen, markiert=None):
    """
    Nr │ A B C │ Y        bei mehr als 16 Zeilen in Blöcken zu 16 nebeneinander.
    'markiert' = Zeilennummer, die mit ◀ gekennzeichnet wird.
    """
    kopf = f"Nr │ {' '.join(f'{n:>{len(n)}}' for n in namen)} │ Y "
    zeilentexte = []
    for k, (bits, aus) in enumerate(zeilen):
        werte = " ".join(f"{b:>{len(n)}}" for b, n in zip(bits, namen))
        zeilentexte.append(f"{k:>2} │ {werte} │ {aus}" + (" ◀" if k == markiert else "  "))
    breite = max(len(kopf), max(len(z) for z in zeilentexte))
    bloecke = [zeilentexte[i:i + 16] for i in range(0, len(zeilentexte), 16)]
    ausgabe = ["    ".join(kopf.ljust(breite) for _ in bloecke)]
    for r in range(len(bloecke[0])):
        ausgabe.append("    ".join(b[r].ljust(breite) for b in bloecke if r < len(b)))
    return "\n".join(ausgabe)


# =============================================================================
# GATTER-SIMULATOR
# =============================================================================
class GatterKarte(Karte):

    def __init__(self, master):
        super().__init__(master, titel="🔲 Logikgatter (interaktiv)",
                         untertitel="Gatter wählen, Eingänge anklicken – links das IEC-Symbol (DIN EN 60617), rechts ANSI")
        b = self.body
        self.dg_e = [0, 1, 0]
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        self.dg_name = ctk.CTkSegmentedButton(oben, values=lm.GATTER_NAMEN, command=lambda _v: self._dg_neu())
        self.dg_name.set("AND")
        self.dg_name.grid(row=0, column=0, padx=(0, 12), pady=2)
        self.dg_anzahl = ctk.CTkSegmentedButton(oben, values=["2 Eingänge", "3 Eingänge"], command=lambda _v: self._dg_neu())
        self.dg_anzahl.set("2 Eingänge")
        self.dg_anzahl.grid(row=0, column=1, pady=2)
        knoepfe = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        knoepfe.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.dg_knoepfe = []
        for i, name in enumerate("ABC"):
            k = ctk.CTkButton(knoepfe, text="", width=86, height=30, font=(config.SCHRIFT_CODE, 13, "bold"),
                              command=lambda i=i: self._dg_klick(i))
            k.grid(row=0, column=i, padx=(0, 8))
            self.dg_knoepfe.append(k)
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.32, max_hoehe=280)
        self.dg_canvas.grid(row=2, column=0, sticky="ew", pady=(8, 4))
        self.dg_tabelle = ctk.CTkLabel(b, text="", font=(config.SCHRIFT_CODE, 13), justify="left", anchor="w")
        self.dg_tabelle.grid(row=3, column=0, sticky="w")
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  AND ist nur 1, wenn ALLE Eingänge 1 sind; OR, wenn MINDESTENS EINER 1 "
                       "ist; XOR, wenn eine UNGERADE Anzahl 1 ist (bei zwei Eingängen: wenn sie verschieden sind). "
                       "NAND, NOR, XNOR sind die negierten Versionen – der Kreis am Ausgang bedeutet „negiert“. "
                       "IEC-Symbole sind Rechtecke mit Zeichen (& für UND, ≥1 für ODER, =1 für XOR), ANSI-Symbole "
                       "haben eigene Formen (in US-Datenblättern üblich). NAND und NOR allein reichen, um JEDE "
                       "Logikfunktion zu bauen.").grid(row=5, column=0, sticky="ew", pady=(8, 0))
        self._dg_neu()

    def _dg_n(self):
        return 1 if self.dg_name.get() == "NOT" else int(self.dg_anzahl.get()[0])

    def _dg_klick(self, i):
        self.dg_e[i] = 1 - self.dg_e[i]
        self._dg_neu()

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        name, n = self.dg_name.get(), self._dg_n()
        for i, k in enumerate(self.dg_knoepfe):
            if i < n:
                k.grid()
                k.configure(text=f"{'ABC'[i]} = {self.dg_e[i]}",
                            fg_color=config.FARBEN["akzent"] if self.dg_e[i] else config.FARBEN["rahmen"],
                            text_color=("#FFFFFF", "#FFFFFF") if self.dg_e[i] else config.FARBEN["text"])
            else:
                k.grid_remove()
        eingaenge = self.dg_e[:n]
        aus = lm.gatter(name, eingaenge)
        zeilen = lm.gatter_tabelle(name, n)
        jetzt = int("".join(map(str, eingaenge)), 2)
        self.dg_tabelle.configure(text=wahrheitstabelle_text(list("ABC"[:n]), zeilen, jetzt))
        einsen = sum(1 for _, a in zeilen if a)
        self.dg_ergebnis.configure(text=f"Y = {lm.als_text(self._dg_baum(name, n))} = {aus}   ·   "
                                        f"{einsen} von {len(zeilen)} Zeilen ergeben 1",
                                   text_color=OK if aus else config.FARBEN["akzent"])
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    @staticmethod
    def _dg_baum(name, n):
        if name == "NOT":
            return ("not", ("var", "A"))
        art = {"AND": "and", "OR": "or", "XOR": "xor", "NAND": "and", "NOR": "or", "XNOR": "xor"}[name]
        baum = ("var", "A")
        for v in "BC"[:n - 1]:
            baum = (art, baum, ("var", v))
        return ("not", baum) if name in ("NAND", "NOR", "XNOR") else baum

    def _dg_zeichnen(self, c, w, h):
        if not hasattr(self, "dg_ergebnis"):
            return
        name, n = self.dg_name.get(), self._dg_n()
        e = self.dg_e[:n]
        aus = lm.gatter(name, e)
        text, leise = _farbe(config.FARBEN["text"]), _farbe(config.FARBEN["text_leise"])
        dick = max(2, int(h / 90))
        schrift = (config.SCHRIFT, max(9, int(h / 16)), "bold")
        klein = (config.SCHRIFT, max(8, int(h / 20)))
        for x_mitte, art in ((w * 0.25, "IEC"), (w * 0.72, "ANSI")):
            gb, gh = min(w * 0.13, h * 0.5), h * 0.56
            x0, x1 = x_mitte - gb / 2, x_mitte + gb / 2
            y0, y1 = h * 0.24, h * 0.24 + gh
            c.create_text(x_mitte, h * 0.1, text=art, fill=leise, font=klein)
            ys = [y0 + gh * (i + 1) / (n + 1) for i in range(n)]
            negiert = name in ("NAND", "NOR", "XNOR", "NOT")
            r_kreis = max(4, gh * 0.07)
            if art == "IEC":
                c.create_rectangle(x0, y0, x1, y1, outline=text, width=dick)
                c.create_text(x_mitte, y0 + gh * 0.2, text=IEC_ZEICHEN[name], fill=text, font=schrift)
                ende = x1
            else:
                ende = self._dg_ansi(c, name, x0, y0, x1, y1, text, dick)
            for i, y in enumerate(ys):
                links = x0 - gb * 0.6
                rand = x0 + (self._dg_ansi_rand(name, x0, y0, x1, y1, y) - x0 if art == "ANSI" else 0)
                if art == "ANSI" and name in ("XOR", "XNOR"):
                    rand -= gb * 0.12                         # Leitung endet an der vorderen Zusatzkurve
                farbe = EINS if e[i] else NULL_FARBE
                c.create_line(links, y, rand, y, fill=farbe, width=dick)
                c.create_text(links - 6, y, text=f"{'ABC'[i]}={e[i]}", anchor="e", fill=farbe, font=klein)
            ym = (y0 + y1) / 2
            if negiert:
                c.create_oval(ende, ym - r_kreis, ende + 2 * r_kreis, ym + r_kreis, outline=text, width=dick)
                ende += 2 * r_kreis
            farbe = EINS if aus else NULL_FARBE
            c.create_line(ende, ym, ende + gb * 0.5, ym, fill=farbe, width=dick)
            c.create_oval(ende + gb * 0.5, ym - r_kreis * 1.6, ende + gb * 0.5 + 3.2 * r_kreis, ym + r_kreis * 1.6,
                          fill=farbe, outline="")
            c.create_text(ende + gb * 0.5 + 3.2 * r_kreis + 6, ym, text=f"Y={aus}", anchor="w", fill=farbe, font=klein)

    @staticmethod
    def _dg_ansi_rand(name, x0, y0, x1, y1, y):
        """x-Koordinate der hinteren Kante des ANSI-Symbols auf Höhe y (OR/XOR sind hinten gewölbt)."""
        if name in ("OR", "NOR", "XOR", "XNOR"):
            t = (y - y0) / (y1 - y0)
            return x0 + (x1 - x0) * 0.18 * math.sin(math.pi * t)
        return x0

    def _dg_ansi(self, c, name, x0, y0, x1, y1, farbe, dick):
        """Zeichnet das ANSI-Symbol, gibt die x-Koordinate des Ausgangs zurück."""
        ym, b, h = (y0 + y1) / 2, x1 - x0, y1 - y0
        if name == "NOT":
            c.create_polygon(x0, y0 + h * 0.15, x0, y1 - h * 0.15, x1 - b * 0.15, ym, outline=farbe, fill="", width=dick)
            return x1 - b * 0.15
        if name in ("AND", "NAND"):
            punkte = [x0, y0, x0 + b * 0.45, y0]
            for k in range(1, 20):
                winkel = -math.pi / 2 + math.pi * k / 20
                punkte += [x0 + b * 0.45 + b * 0.55 * math.cos(winkel), ym + h / 2 * math.sin(winkel)]
            punkte += [x0 + b * 0.45, y1, x0, y1]
            c.create_polygon(*punkte, outline=farbe, fill="", width=dick)
            return x1
        # OR / NOR / XOR / XNOR: hinten gewölbt, vorne spitz
        punkte = []
        for k in range(21):                                   # obere Kurve zur Spitze
            u = k / 20
            punkte += [x0 + b * u, y0 + (ym - y0) * u ** 2.2]
        for k in range(21):                                   # untere Kurve zurück
            u = 1 - k / 20
            punkte += [x0 + b * u, y1 - (y1 - ym) * u ** 2.2]
        for k in range(21):                                   # hintere Wölbung
            t = 1 - k / 20
            punkte += [self._dg_ansi_rand(name, x0, y0, x1, y1, y0 + h * t), y0 + h * t]
        c.create_polygon(*punkte, outline=farbe, fill="", width=dick)
        if name in ("XOR", "XNOR"):                          # zweite Wölbung davor
            linie = []
            for k in range(21):
                t = k / 20
                linie += [self._dg_ansi_rand(name, x0, y0, x1, y1, y0 + h * t) - b * 0.12, y0 + h * t]
            c.create_line(*linie, fill=farbe, width=dick)
        return x1


# =============================================================================
# AUSDRUCK -> WAHRHEITSTABELLE
# =============================================================================
class AusdruckKarte(Karte):
    SYMBOLE = ["¬", "·", "+", "⊕", "(", ")"]

    def __init__(self, master, start="A·B + ¬A·C"):
        super().__init__(master, titel="🧾 Ausdruck → Wahrheitstabelle und Normalformen (interaktiv)",
                         untertitel="Ausdruck eintippen + Enter. Schreibweisen: ¬A !A /A A'   A·B A*B AB   A+B   A⊕B")
        b = self.body
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="ew")
        oben.grid_columnconfigure(0, weight=1)
        self.dg_feld = ctk.CTkEntry(oben, font=(config.SCHRIFT_CODE, 15))
        self.dg_feld.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.dg_feld.insert(0, start)
        self.dg_feld.bind("<Return>", lambda _e: self._dg_neu())
        symbole = ctk.CTkFrame(oben, fg_color="transparent", corner_radius=0)
        symbole.grid(row=0, column=1)
        for i, z in enumerate(self.SYMBOLE):
            ctk.CTkButton(symbole, text=z, width=34, height=30, font=(config.SCHRIFT_CODE, 15, "bold"),
                          command=lambda z=z: self._dg_einfuegen(z)).grid(row=0, column=i, padx=1)
        ctk.CTkButton(oben, text="Auswerten", width=100, command=self._dg_neu).grid(row=0, column=2, padx=(8, 0))
        self.dg_tabelle = ctk.CTkLabel(b, text="", font=(config.SCHRIFT_CODE, 13), justify="left", anchor="w")
        self.dg_tabelle.grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Jede Zeile der Wahrheitstabelle ist eine Belegung der Eingänge; die "
                       "Zeilennummer ist die Binärzahl der Eingänge (= Minterm-Nummer). DNF: für jede 1-Zeile ein "
                       "UND-Term (Minterm), alle ODER-verknüpft. KNF: für jede 0-Zeile eine ODER-Klausel (Maxterm), "
                       "alle UND-verknüpft. Die kanonischen Formen sind eindeutig, aber lang – die minimalen Formen "
                       "(Quine-McCluskey, wie das KV-Diagramm) brauchen am wenigsten Gatter.").grid(
            row=3, column=0, sticky="ew", pady=(8, 0))
        self._dg_neu()

    def _dg_einfuegen(self, zeichen):
        self.dg_feld.insert("insert", zeichen)
        self.dg_feld.focus_set()

    def _dg_neu(self):
        try:
            e = lm.analysieren(self.dg_feld.get())
        except ValueError as fehler:
            self.dg_tabelle.configure(text="")
            self.dg_ergebnis.configure(text=f"⚠ {fehler}", text_color=WARN)
            return
        self.dg_tabelle.configure(text=wahrheitstabelle_text(e["namen"], e["tabelle"]) if e["namen"] else "")
        kurz = lambda text: text if len(text) <= 160 else text[:157] + " …"
        zeilen = [f"Gelesen als:   Y = {e['text']}",
                  f"Minterme:      Σm({', '.join(map(str, e['minterme']))})" if e["namen"] else "konstant",
                  f"DNF kanonisch: {kurz(e['dnf'])}",
                  f"KNF kanonisch: {kurz(e['knf'])}",
                  f"DNF minimal:   {e['min_dnf']}",
                  f"KNF minimal:   {e['min_knf']}"]
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])


# =============================================================================
# KV-DIAGRAMM
# =============================================================================
class KVKarte(Karte):
    ANZAHLEN = ["2 Variablen", "3 Variablen", "4 Variablen"]

    def __init__(self, master):
        super().__init__(master, titel="🗺️ KV-Diagramm (interaktiv)",
                         untertitel="Felder anklicken: 0 → 1 → X (don't care) → 0. Die Blöcke zeigen die minimale Form")
        b = self.body
        self.dg_werte = {}
        self.dg_geo = None
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="ew")
        self.dg_anzahl = ctk.CTkSegmentedButton(oben, values=self.ANZAHLEN, command=lambda _v: self._dg_anzahl_neu())
        self.dg_anzahl.set(self.ANZAHLEN[2])
        self.dg_anzahl.grid(row=0, column=0, padx=(0, 12), pady=2)
        self.dg_feld = ctk.CTkEntry(oben, width=230, font=(config.SCHRIFT_CODE, 13),
                                    placeholder_text="oder Ausdruck, z.B. A·B + C·¬D")
        self.dg_feld.grid(row=0, column=1, pady=2)
        self.dg_feld.bind("<Return>", lambda _e: self._dg_aus_ausdruck())
        ctk.CTkButton(oben, text="übernehmen", width=100, command=self._dg_aus_ausdruck).grid(row=0, column=2, padx=6)
        ctk.CTkButton(oben, text="leeren", width=70, fg_color="transparent", border_width=1,
                      text_color=config.FARBEN["text"], command=self._dg_leeren).grid(row=0, column=3)
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.55, max_hoehe=420)
        self.dg_canvas.grid(row=1, column=0, sticky="ew", pady=(8, 4))
        self.dg_canvas.bind("<Button-1>", self._dg_klick)
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Das KV-Diagramm ist die Wahrheitstabelle als Rechteck, so angeordnet, "
                       "dass benachbarte Felder sich in genau EINER Variable unterscheiden (Gray-Code an den Rändern) – "
                       "auch über den Rand hinweg (oben ↔ unten, links ↔ rechts). Zusammenhängende Blöcke aus 1, 2, 4 "
                       "oder 8 Einsen ergeben je einen UND-Term; Variablen, die sich im Block ändern, fallen weg. "
                       "Möglichst grosse und möglichst wenige Blöcke = minimale DNF. X-Felder (don't care) dürfen "
                       "mitbenutzt werden, müssen aber nicht. Die kleine Zahl in jedem Feld ist die Minterm-Nummer.").grid(
            row=3, column=0, sticky="ew", pady=(8, 0))
        for m in (0, 1, 2, 3, 8, 10):                       # Startbeispiel
            self.dg_werte[m] = "1"
        self._dg_neu()

    def _dg_n(self):
        return int(self.dg_anzahl.get()[0])

    def _dg_namen(self):
        return list("ABCD"[:self._dg_n()])

    def _dg_anzahl_neu(self):
        self.dg_werte = {m: v for m, v in self.dg_werte.items() if m < 2 ** self._dg_n()}
        self._dg_neu()

    def _dg_leeren(self):
        self.dg_werte = {}
        self._dg_neu()

    def _dg_aus_ausdruck(self):
        try:
            baum = lm.parsen(self.dg_feld.get())
            namen = lm.variablen(baum)
            if len(namen) > 4:
                raise ValueError("Für das KV-Diagramm höchstens 4 Variablen")
            n = max(len(namen), 2)
            # Variablen des Ausdrucks auf A, B, C, D abbilden (in ihrer Reihenfolge)
            kv_namen = list("ABCD"[:n])
            abbild = dict(zip(namen, kv_namen))
            umbenannt = self._umbenennen(baum, abbild)
            zeilen = lm.tabelle(umbenannt, kv_namen)
        except ValueError as fehler:
            self.dg_ergebnis.configure(text=f"⚠ {fehler}", text_color=WARN)
            return
        self.dg_anzahl.set(self.ANZAHLEN[n - 2])
        self.dg_werte = {k: "1" for k, (_, aus) in enumerate(zeilen) if aus}
        self._dg_neu(hinweis=", ".join(f"{a} → {b}" for a, b in abbild.items() if a != b))

    def _umbenennen(self, baum, abbild):
        if baum[0] == "var":
            return ("var", abbild[baum[1]])
        return (baum[0],) + tuple(self._umbenennen(k, abbild) if isinstance(k, tuple) else k for k in baum[1:])

    def _dg_klick(self, ereignis):
        if not self.dg_geo:
            return
        x0, y0, zb, zh, zeilen, spalten = self.dg_geo
        s, r = int((ereignis.x - x0) // zb), int((ereignis.y - y0) // zh)
        if 0 <= r < zeilen and 0 <= s < spalten:
            m = lm.kv_aufbau(self._dg_n())[2](r, s)
            self.dg_werte[m] = {"0": "1", "1": "X", "X": "0"}[self.dg_werte.get(m, "0")]
            self._dg_neu()

    def _dg_minterme(self):
        n = self._dg_n()
        eins = [m for m in range(2 ** n) if self.dg_werte.get(m) == "1"]
        dc = [m for m in range(2 ** n) if self.dg_werte.get(m) == "X"]
        return eins, dc

    def _dg_neu(self, hinweis=""):
        if not hasattr(self, "dg_ergebnis"):
            return
        n, namen = self._dg_n(), self._dg_namen()
        eins, dc = self._dg_minterme()
        f = lm.minimal_formen(eins, namen, dc)
        self.dg_terme = f["terme"]
        zeilen = [f"Σm({', '.join(map(str, eins))})" + (f" + d({', '.join(map(str, dc))})" if dc else ""),
                  f"Y = {f['min_dnf']}   (minimale DNF, {len(f['terme'])} Block/Blöcke)",
                  f"Y = {f['min_knf']}   (minimale KNF, aus den Nullen)"]
        for i, t in enumerate(f["terme"]):
            if t != "-" * n:
                zeilen.append(f"  Block {i + 1}: {lm.produkt(t, namen)}   ({2 ** t.count('-')} Felder)")
        if hinweis:
            zeilen.append(f"Variablen umbenannt: {hinweis}")
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    def _dg_zeichnen(self, c, w, h):
        if not hasattr(self, "dg_terme"):
            return
        n, namen = self._dg_n(), self._dg_namen()
        z_codes, s_codes, zelle = lm.kv_aufbau(n)
        z_namen, s_namen = "".join(namen[:len(z_codes[0])]), "".join(namen[len(z_codes[0]):])
        text, leise = _farbe(config.FARBEN["text"]), _farbe(config.FARBEN["text_leise"])
        rahmen = _farbe(config.FARBEN["rahmen"])
        zellen = min((w * 0.62) / len(s_codes), (h * 0.78) / len(z_codes))
        x0 = w * 0.08 + zellen * 0.9
        y0 = h * 0.16
        self.dg_geo = (x0, y0, zellen, zellen, len(z_codes), len(s_codes))
        gross = (config.SCHRIFT_CODE, max(10, int(zellen / 3)), "bold")
        klein = (config.SCHRIFT, max(7, int(zellen / 7)))
        mittel = (config.SCHRIFT_CODE, max(8, int(zellen / 5)))
        # Achsen: Variablennamen und Gray-Codes
        c.create_text(x0 - 6, y0 - 6, text=f"{z_namen} \\ {s_namen}", anchor="se", fill=text, font=mittel)
        for s, code in enumerate(s_codes):
            c.create_text(x0 + (s + 0.5) * zellen, y0 - 6, text=code, anchor="s", fill=leise, font=mittel)
        for r, code in enumerate(z_codes):
            c.create_text(x0 - 6, y0 + (r + 0.5) * zellen, text=code, anchor="e", fill=leise, font=mittel)
        # Felder (nur Rahmen; Texte erst nach den Blöcken, damit sie obenauf liegen)
        for r in range(len(z_codes)):
            for s in range(len(s_codes)):
                a, b = x0 + s * zellen, y0 + r * zellen
                c.create_rectangle(a, b, a + zellen, b + zellen, outline=rahmen, width=1)
        # Blöcke (je Gruppe eine Farbe, leicht eingerückt; über den Rand -> mehrere Teilrechtecke)
        for i, t in enumerate(self.dg_terme):
            farbe = GRUPPEN_FARBEN[i % len(GRUPPEN_FARBEN)]
            rand = 4 + 3 * (i % 4)
            zs, ss = lm.kv_gruppe(t, n)
            for z_stueck in lm.zusammenhaengend(zs, len(z_codes)):
                for s_stueck in lm.zusammenhaengend(ss, len(s_codes)):
                    a = x0 + s_stueck[0] * zellen + rand
                    b = y0 + z_stueck[0] * zellen + rand
                    c.create_rectangle(a, b, x0 + (s_stueck[-1] + 1) * zellen - rand,
                                       y0 + (z_stueck[-1] + 1) * zellen - rand, outline=farbe, width=3)
        for r in range(len(z_codes)):
            for s in range(len(s_codes)):
                m = zelle(r, s)
                a, b = x0 + s * zellen, y0 + r * zellen
                wert = self.dg_werte.get(m, "0")
                farbe = {"1": text, "X": "#F59E0B", "0": leise}[wert]
                c.create_text(a + zellen / 2, b + zellen / 2, text=wert, fill=farbe, font=gross)
                c.create_text(a + zellen - 4, b + zellen - 3, text=str(m), anchor="se", fill=leise, font=klein)
        # Legende rechts
        lx = x0 + len(s_codes) * zellen + 20
        for i, t in enumerate(self.dg_terme[:8]):
            if t == "-" * n:
                continue
            farbe = GRUPPEN_FARBEN[i % len(GRUPPEN_FARBEN)]
            y = y0 + i * zellen * 0.45 + 8
            c.create_rectangle(lx, y - 6, lx + 14, y + 6, outline=farbe, width=3)
            c.create_text(lx + 22, y, text=lm.produkt(t, namen), anchor="w", fill=text, font=mittel)
