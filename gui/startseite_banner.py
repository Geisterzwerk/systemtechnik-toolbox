# =============================================================================
# gui/startseite_banner.py
# -----------------------------------------------------------------------------
# ANIMIERTES BANNER oben auf der Startseite:
#
#   ┌─────────────────────────────────────────────────────────────────────────┐
#   │ ─┤R├──●──┤|├──▷|──●── ●→ ●→   (Leiterbahnen mit Bauteilen + Strompunkten)  │
#   │                    ⚡ Systemtechnik HF Toolbox                            │
#   │          Verstehen · Berechnen · Simulieren · Messen · Programmieren       │
#   │  ┌ Oszilloskop ┐   ┌ Terminal ────────┐   ┌ Code ───────────┐            │
#   │  │ ∿∿∿ ⎍⎍⎍     │   │ $ sudo apt update│   │ def teiler(...) │            │
#   │  └─────────────┘   └──────────────────┘   └─────────────────┘            │
#   │ ──●──┤R├──⏚                                                              │
#   └─────────────────────────────────────────────────────────────────────────┘
#
#   - Statisches (Hintergrund, Bahnen, Bauteile, Titel, Rahmen) wird nur bei Grössenänderung gezeichnet.
#   - Bewegtes (Strompunkte, Kurven, Terminal- und Codezeilen) alle 70 ms neu (Tag "dyn").
#   - Pausiert, solange die Startseite nicht sichtbar ist; endet, wenn das Banner zerstört wird.
#   - Schmales Fenster: nur das Oszilloskop bleibt (Terminal und Code fallen weg).
#   - Eigene Namen beginnen mit bn_ (keine Kollision mit tkinter).
#
# WER RUFT DAS AUF?  gui/startseite_gui.py
# =============================================================================

import math
import time
import tkinter.font as tkfont

import customtkinter as ctk

import config                                                          # -> config.py
from core.layout import ResponsiveCanvas                               # -> core/layout.py

FRAME_MS = 70
TERMINAL = [                                       # (Art, Text)  Art: "befehl" wird getippt, "aus" erscheint
    ("befehl", "sudo apt update"),
    ("aus", "Holen:1 http://archive.ubuntu.com noble InRelease"),
    ("aus", "Paketlisten werden gelesen … Fertig"),
    ("befehl", "systemctl status nginx"),
    ("ok", "● nginx.service – A high performance web server"),
    ("ok", "   Active: active (running)"),
    ("befehl", "df -h /"),
    ("aus", "/dev/sda2   50G   12G   36G  25% /"),
    ("befehl", "ping -c 1 192.168.1.1"),
    ("aus", "64 bytes from 192.168.1.1: time=0.4 ms"),
    ("befehl", "uptime"),
    ("aus", " 10:42 up 23 days, load average: 0.08"),
]
CODE = [
    "# Spannungsteiler berechnen",
    "def teiler(u, r1, r2):",
    "    return u * r2 / (r1 + r2)",
    "",
    "u_aus = teiler(12.0, 10e3, 4.7e3)",
    'print(f"U = {u_aus:.2f} V")',
    ">>> U = 3.84 V",
]
SCHLUESSELWOERTER = ("def", "return", "print", "import", "for", "in", "if")


def _farbe(paar):
    return paar[1] if ctk.get_appearance_mode() == "Dark" else paar[0]


def _mischen(a, b, anteil):
    def rgb(f):
        f = f.lstrip("#")
        return [int(f[i:i + 2], 16) for i in (0, 2, 4)]
    x, y = rgb(a), rgb(b)
    return "#" + "".join(f"{round(p + (q - p) * anteil):02x}" for p, q in zip(x, y))


class Banner(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.bn_geo = None
        self.bn_schriften = {}                                       # Grösse -> tkfont.Font (zum Messen)
        self.bn_start = time.monotonic()
        self.bn_canvas = ResponsiveCanvas(self, self._bn_statisch, seitenverhaeltnis=0.36, max_hoehe=330)
        self.bn_canvas.grid(row=0, column=0, sticky="ew")
        self._bn_schleife()

    # =========================================================================
    # FARBEN
    # =========================================================================
    def _bn_farben(self):
        dunkel = ctk.get_appearance_mode() == "Dark"
        return {
            "oben": "#0F1B33" if dunkel else "#DCE8FB",
            "unten": "#1B1D22" if dunkel else "#F2F4F7",
            "bahn": "#2E4A7A" if dunkel else "#9DB7E3",
            "punkt": "#60A5FA" if dunkel else "#1F6FEB",
            "titel": "#F1F5FB" if dunkel else "#0F1B33",
            "leise": "#9AA9C2" if dunkel else "#4A5B78",
            "schirm": "#0A0F18", "raster": "#1E2B3F", "gruen": "#4ADE80", "gelb": "#FACC15", "blau": "#60A5FA",
            "rand": "#3B4A63" if dunkel else "#8EA3C4", "weiss": "#E6EDF7", "lila": "#C084FC",
            "string": "#A3E635", "zahl": "#FB923C", "kommentar": "#64748B", "konsole": "#94A3B8",
        }

    # =========================================================================
    # STATISCH (bei Grössenänderung)
    # =========================================================================
    def _bn_statisch(self, c, w, h):
        f = self._bn_farben()
        streifen = 24                                                   # Farbverlauf von oben nach unten
        for i in range(streifen):
            c.create_rectangle(0, h * i / streifen, w, h * (i + 1) / streifen + 1, outline="",
                               fill=_mischen(f["oben"], f["unten"], i / (streifen - 1)))
        dick = max(2, round(h / 160))
        g = max(9, int(h / 15))
        bahnen = []
        for y_rel, phase in ((0.09, 0.0), (0.95, 0.5)):                 # Leiterbahn oben und unten
            y = h * y_rel
            c.create_line(0, y, w, y, fill=f["bahn"], width=dick)
            bahnen.append(((0, y), (w, y)))
            schritt = max(150, w / 6)
            x = schritt * (0.35 + phase)
            k = 0
            while x < w - 40:
                self._bn_bauteil(c, x, y, ("R", "C", "D", "knoten", "L")[k % 5], f, dick, h)
                x += schritt
                k += 1
        for x_rel in (0.04, 0.96):                                      # senkrechte Bahnen an den Rändern
            x = w * x_rel
            c.create_line(x, h * 0.09, x, h * 0.95, fill=f["bahn"], width=dick)
            c.create_oval(x - dick * 2, h * 0.09 - dick * 2, x + dick * 2, h * 0.09 + dick * 2, fill=f["bahn"], outline="")
            c.create_oval(x - dick * 2, h * 0.95 - dick * 2, x + dick * 2, h * 0.95 + dick * 2, fill=f["bahn"], outline="")
        c.create_text(w / 2, h * 0.205, text=f"⚡ {config.APP_TITEL}", fill=f["titel"],
                      font=(config.SCHRIFT, max(14, int(g * 1.6)), "bold"))
        c.create_text(w / 2, h * 0.345, text="Verstehen · Berechnen · Simulieren · Messen · Programmieren",
                      fill=f["leise"], font=(config.SCHRIFT, max(9, int(g * 0.95))))
        schirme = []
        if w >= 300:
            # breit: drei Bildschirme nebeneinander, schmal: nur das Oszilloskop in der Mitte
            arten = (("Oszilloskop", f["gelb"]), ("Terminal", f["gruen"]), ("Python", f["lila"]))
            if w < 560:
                arten = arten[:1]
            n = len(arten)
            rand, abstand = (w * 0.07, w * 0.025) if n == 3 else (w * 0.18, 0)
            breite = (w - 2 * rand - (n - 1) * abstand) / n
            y0, y1 = h * 0.43, h * 0.87
            for i, (titel, akzent) in enumerate(arten):
                x0 = rand + i * (breite + abstand)
                c.create_rectangle(x0 + 3, y0 + 4, x0 + breite + 3, y1 + 4, fill=_mischen(f["unten"], "#000000", 0.35),
                                   outline="")                          # Schatten
                c.create_rectangle(x0, y0, x0 + breite, y1, fill=f["schirm"], outline=f["rand"], width=2)
                kopf = (y1 - y0) * 0.14
                c.create_rectangle(x0, y0, x0 + breite, y0 + kopf, fill="#151D2B", outline=f["rand"], width=2)
                for j, punkt in enumerate(("#F87171", "#FBBF24", "#4ADE80")):
                    r = kopf * 0.18
                    cx = x0 + kopf * 0.45 + j * kopf * 0.55
                    c.create_oval(cx - r, y0 + kopf / 2 - r, cx + r, y0 + kopf / 2 + r, fill=punkt, outline="")
                c.create_text(x0 + breite - 8, y0 + kopf / 2, text=titel, anchor="e", fill=akzent,
                              font=(config.SCHRIFT, max(7, int(kopf * 0.42)), "bold"))
                schirme.append((x0, y0 + kopf, x0 + breite, y1))
            ox0, oy0, ox1, oy1 = schirme[0]                             # Raster des Oszilloskops
            for k in range(1, 8):
                x = ox0 + (ox1 - ox0) * k / 8
                c.create_line(x, oy0, x, oy1, fill=f["raster"])
            for k in range(1, 4):
                y = oy0 + (oy1 - oy0) * k / 4
                c.create_line(ox0, y, ox1, y, fill=f["raster"])
        self.bn_geo = {"c": c, "w": w, "h": h, "bahnen": bahnen, "schirme": schirme, "f": f, "dick": dick,
                       "schrift": max(7, int(h / 30))}
        self._bn_dynamisch()

    def _bn_bauteil(self, c, x, y, art, f, dick, h):
        """Kleines Schaltzeichen auf der Bahn (Hintergrundfarbe deckt die Bahn ab)."""
        s = h * 0.035
        bg = _mischen(f["oben"], f["unten"], 0.0 if y < h / 2 else 1.0)
        if art == "R":
            c.create_rectangle(x - 2.2 * s, y - 0.8 * s, x + 2.2 * s, y + 0.8 * s, fill=bg, outline=f["bahn"], width=dick)
        elif art == "C":
            c.create_rectangle(x - 0.6 * s, y - 1.5 * s, x + 0.6 * s, y + 1.5 * s, fill=bg, outline="")
            for dx in (-0.6 * s, 0.6 * s):
                c.create_line(x + dx, y - 1.5 * s, x + dx, y + 1.5 * s, fill=f["bahn"], width=dick + 1)
        elif art == "D":
            c.create_polygon(x - s, y - s, x - s, y + s, x + s, y, fill=bg, outline=f["bahn"], width=dick)
            c.create_line(x + s, y - s, x + s, y + s, fill=f["bahn"], width=dick)
        elif art == "L":
            c.create_rectangle(x - 2.4 * s, y - 1.1 * s, x + 2.4 * s, y + 0.2 * s, fill=bg, outline="")
            for k in range(4):
                x0 = x - 2.4 * s + k * 1.2 * s
                c.create_arc(x0, y - 0.6 * s, x0 + 1.2 * s, y + 0.6 * s, start=0, extent=180, style="arc",
                             outline=f["bahn"], width=dick)
        else:
            c.create_oval(x - 0.5 * s, y - 0.5 * s, x + 0.5 * s, y + 0.5 * s, fill=f["bahn"], outline="")

    def _bn_messen(self, text, groesse, fett=False):
        """Breite eines Textes in Pixel in der Code-Schrift (für farbige Wörter nebeneinander)."""
        schluessel = (groesse, fett)
        if schluessel not in self.bn_schriften:
            self.bn_schriften[schluessel] = tkfont.Font(family=config.SCHRIFT_CODE, size=groesse,
                                                        weight="bold" if fett else "normal")
        return self.bn_schriften[schluessel].measure(text)

    # =========================================================================
    # BEWEGT (alle 70 ms)
    # =========================================================================
    def _bn_dynamisch(self):
        g = self.bn_geo
        if g is None:
            return
        c, f, w = g["c"], g["f"], g["w"]
        c.delete("dyn")
        t = time.monotonic() - self.bn_start
        r = g["dick"] * 1.6
        for k, ((x0, y), (x1, _)) in enumerate(g["bahnen"]):          # Strompunkte
            richtung = 1 if k == 0 else -1
            for n in range(7):
                anteil = ((t * 0.06 * richtung + n / 7) % 1.0)
                x = x0 + (x1 - x0) * anteil
                c.create_oval(x - r, y - r, x + r, y + r, fill=f["punkt"], outline="", tags="dyn")
        if not g["schirme"]:
            return
        self._bn_oszi(c, g["schirme"][0], t, f)
        if len(g["schirme"]) == 3:
            self._bn_terminal(c, g["schirme"][1], t, f, g["schrift"])
            self._bn_code(c, g["schirme"][2], t, f, g["schrift"])

    def _bn_oszi(self, c, schirm, t, f):
        x0, y0, x1, y1 = schirm
        mitte_a, mitte_b, amp = y0 + (y1 - y0) * 0.3, y0 + (y1 - y0) * 0.72, (y1 - y0) * 0.16
        sinus, rechteck = [], []
        for k in range(61):
            x = x0 + 4 + (x1 - x0 - 8) * k / 60
            phase = k / 60 * 4 * math.pi - t * 2.2
            sinus += [x, mitte_a - amp * math.sin(phase)]
            rechteck += [x, mitte_b - amp * (1 if math.sin(phase * 0.5) >= 0 else -1)]
        c.create_line(*sinus, fill=f["gelb"], width=2, tags="dyn")
        c.create_line(*rechteck, fill=f["blau"], width=2, tags="dyn")

    def _bn_terminal(self, c, schirm, t, f, schrift):
        """Befehle werden getippt (20 Zeichen/s), Ausgaben erscheinen auf einmal; danach von vorn."""
        x0, y0, x1, y1 = schirm
        zeilen, zeit = [], t % 34.0
        for art, text in TERMINAL:
            if art == "befehl":
                dauer = 0.6 + len(text) / 20
                if zeit < dauer:
                    getippt = text[:max(0, int((zeit - 0.6) * 20))]
                    zeilen.append(("befehl", getippt + ("▌" if int(t * 3) % 2 == 0 else " ")))
                    break
                zeilen.append(("befehl", text))
                zeit -= dauer
            else:
                if zeit < 0.35:
                    break
                zeilen.append((art, text))
                zeit -= 0.35
        else:
            zeilen.append(("befehl", "▌" if int(t * 3) % 2 == 0 else ""))
        zeilenhoehe = schrift * 1.7
        platz = max(1, int((y1 - y0 - 8) // zeilenhoehe))
        breite_zeichen = max(8, int((x1 - x0 - 12) / (schrift * 0.62)))
        for k, (art, text) in enumerate(zeilen[-platz:]):
            y = y0 + 6 + (k + 0.5) * zeilenhoehe
            if art == "befehl":
                c.create_text(x0 + 6, y, text="$ ", anchor="w", fill=f["gruen"],
                              font=(config.SCHRIFT_CODE, schrift, "bold"), tags="dyn")
                c.create_text(x0 + 6 + self._bn_messen("$ ", schrift, True), y, text=text[:breite_zeichen - 2],
                              anchor="w", fill=f["weiss"], font=(config.SCHRIFT_CODE, schrift), tags="dyn")
            else:
                c.create_text(x0 + 6, y, text=text[:breite_zeichen], anchor="w",
                              fill=f["gruen"] if art == "ok" else f["konsole"], font=(config.SCHRIFT_CODE, schrift),
                              tags="dyn")

    def _bn_code(self, c, schirm, t, f, schrift):
        """Python-Code wird Zeichen für Zeichen getippt, mit einfacher Syntaxfarbe."""
        x0, y0, x1, y1 = schirm
        zeit = t % 22.0
        zeichen = int(zeit * 14)
        zeilenhoehe = schrift * 1.7
        breite_zeichen = max(8, int((x1 - x0 - 30) / (schrift * 0.62)))
        platz = max(1, int((y1 - y0 - 8) // zeilenhoehe))
        sichtbar, rest = [], zeichen
        for zeile in CODE:
            if rest <= 0:
                break
            sichtbar.append(zeile[:rest])
            rest -= len(zeile) + 1
        if sichtbar and int(t * 3) % 2 == 0:
            sichtbar[-1] += "▌"
        for k, zeile in enumerate(sichtbar[-platz:]):
            y = y0 + 6 + (k + 0.5) * zeilenhoehe
            c.create_text(x0 + 6, y, text=str(k + 1), anchor="w", fill=f["kommentar"],
                          font=(config.SCHRIFT_CODE, schrift), tags="dyn")
            x = x0 + 24
            for wort, farbe in self._bn_farbig(zeile[:breite_zeichen], f):
                if x + self._bn_messen(wort, schrift) > x1 - 6:            # nicht über den Bildschirmrand
                    break
                c.create_text(x, y, text=wort, anchor="w", fill=farbe, font=(config.SCHRIFT_CODE, schrift), tags="dyn")
                x += self._bn_messen(wort, schrift)

    @staticmethod
    def _bn_farbig(zeile, f):
        """Zeile in (Text, Farbe)-Stücke zerlegen: Kommentar, Ausgabe, Strings, Zahlen, Schlüsselwörter."""
        if zeile.lstrip().startswith("#"):
            return [(zeile, f["kommentar"])]
        if zeile.startswith(">>>"):
            return [(zeile, f["gruen"])]
        stuecke, wort, im_string = [], "", False
        for zeichen in zeile:
            if zeichen in "\"'":
                if im_string:
                    stuecke.append((wort + zeichen, f["string"]))
                    wort, im_string = "", False
                    continue
                if wort:
                    stuecke.append((wort, None))
                wort, im_string = zeichen, True
                continue
            if not im_string and not (zeichen.isalnum() or zeichen in "_."):
                if wort:
                    stuecke.append((wort, None))
                stuecke.append((zeichen, None))
                wort = ""
                continue
            wort += zeichen
        if wort:
            stuecke.append((wort, f["string"] if im_string else None))
        farbig = []
        for text, farbe in stuecke:
            if farbe is None:
                if text in SCHLUESSELWOERTER:
                    farbe = f["lila"]
                elif text[:1].isdigit():
                    farbe = f["zahl"]
                else:
                    farbe = f["weiss"]
            farbig.append((text, farbe))
        return farbig

    # =========================================================================
    # SCHLEIFE
    # =========================================================================
    def _bn_schleife(self):
        if not self.bn_canvas.winfo_exists():
            return
        if self.bn_canvas.winfo_ismapped():
            self._bn_dynamisch()
            self.after(FRAME_MS, self._bn_schleife)
        else:
            self.after(400, self._bn_schleife)                            # unsichtbar -> selten nachsehen
