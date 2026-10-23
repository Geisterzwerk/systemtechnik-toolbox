# =============================================================================
# core/widgets.py
# -----------------------------------------------------------------------------
# Wiederverwendbare GUI-Bausteine für ALLE Seiten der Toolbox.
# (Alles rund um "mit der Fenstergrösse mitgehen" steht in core/layout.py)
#
# INHALT:
#   Tooltip             Hinweistext, wenn die Maus über einem Button ist
#   FormatText          Text mit ## Überschrift, - Punkt, **fett**, `code`
#                       Höhe passt sich automatisch an -> nie abgeschnitten
#   karte()             Kasten mit Rahmen (Spalte 0 wächst mit)
#   info_box()          Farbige Box für Tipps / Warnungen
# =============================================================================

import math
import re
import tkinter as tk

import customtkinter as ctk

import config                                               # -> config.py
from core.layout import Responsive                          # -> core/layout.py


# =============================================================================
# TOOLTIP
# =============================================================================
class Tooltip:
    """Tooltip(mein_button, "Widerstand") - erscheint nach 400 ms. Lange Texte brechen um.
    text darf auch eine Funktion sein (wird beim Anzeigen gefragt, leerer Text = kein Tooltip)."""

    VERZOEGERUNG_MS = 400

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.fenster = None
        self._timer = None
        widget.bind("<Enter>", self._planen, add="+")
        widget.bind("<Leave>", self._verstecken, add="+")
        widget.bind("<ButtonPress>", self._verstecken, add="+")

    def _planen(self, event=None):
        self._timer = self.widget.after(self.VERZOEGERUNG_MS, self._anzeigen)

    def _anzeigen(self):
        self._timer = None
        if self.fenster is not None or not self.widget.winfo_exists():
            return
        text = self.text() if callable(self.text) else self.text       # Text kann sich ändern (Funktion)
        if not text:
            return
        self.fenster = tk.Toplevel(self.widget)
        self.fenster.wm_overrideredirect(True)
        tk.Label(self.fenster, text=text, bg="#2B2F36", fg="white", justify="left", wraplength=420,
                 padx=10, pady=6, font=config.FONT_KLEIN).pack()
        # rechts neben dem Widget - passt es nicht mehr auf den Bildschirm, dann links davon
        self.fenster.update_idletasks()
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 8
        if x + self.fenster.winfo_reqwidth() > self.widget.winfo_screenwidth():
            x = max(0, self.widget.winfo_rootx() - self.fenster.winfo_reqwidth() - 8)
        y = min(self.widget.winfo_rooty() + 6, self.widget.winfo_screenheight() - self.fenster.winfo_reqheight() - 40)
        self.fenster.wm_geometry(f"+{x}+{max(0, y)}")

    def _verstecken(self, event=None):
        if self._timer is not None:
            self.widget.after_cancel(self._timer)
            self._timer = None
        if self.fenster is not None:
            self.fenster.destroy()
            self.fenster = None


# =============================================================================
# WERTE-ANZEIGE: Ergebnisse als Tabelle  (Rechner, Schaltungen, Kurven, Trafo)
# =============================================================================
class WerteAnzeige(ctk.CTkFrame, Responsive):
    """
    Zeigt Ergebniszeilen übersichtlich an:

        Querstrom I2   600 µA
        P(R1)          3.6 mW
        τ              100 ms     = R · C
        Nach 5τ = 500 ms ist der Vorgang … (erklärender Satz)
        ⚠ Warnung

    Der erste Wert ist das Hauptergebnis (grösser, farbig). Das Zerlegen macht core/werte_text.py.
        anzeige.zeigen(["I = 12 mA", "P = 144 mW"], farbe=config.FARBEN["akzent"])
        anzeige.fehler("Division durch 0 …")
        anzeige.leeren()
    Ändert sich nur der Text (Regler wird gezogen), werden die vorhandenen Zeilen nur umbeschriftet.
    """

    WARN = ("#B45309", "#F59E0B")

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.grid_columnconfigure(2, weight=1)
        self.wa_zeilen = []           # [(art, [widgets])]
        self.wa_text = None
        self.responsive_starten()     # -> anpassen(): Zeilenumbruch nach der Breite (core/layout.py)

    def leeren(self):
        self.zeigen([])

    def fehler(self, text):
        self.zeigen([f"⚠ {text}"])

    def zeigen(self, zeilen, farbe=None):
        if isinstance(zeilen, str):
            zeilen = zeilen.split("\n")
        schluessel = (tuple(zeilen), str(farbe))
        if schluessel == self.wa_text:
            return
        self.wa_text = schluessel
        from core.werte_text import zerlegen                         # -> core/werte_text.py
        teile = zerlegen(zeilen)
        farbe = farbe or config.FARBEN["akzent"]
        arten = [t[0] if t[0] != "warnung" else "text" for t in teile]
        if arten != [a for a, _ in self.wa_zeilen]:                  # Aufbau anders -> neu bauen
            for _art, widgets in self.wa_zeilen:
                for w in widgets:
                    w.destroy()
            self.wa_zeilen = [(art, self._wa_zeile(nummer, art)) for nummer, art in enumerate(arten)]
            self.neu_berechnen()                                      # Umbruch für die neuen Zeilen
        erster_wert = True
        nur_text = not any(a == "wert" for a in arten)
        for (art, name, wert, notiz), (_a, widgets) in zip(teile, self.wa_zeilen):
            if art == "wert":
                n, w, z = widgets
                self._wa_setzen(n, text=name)
                self._wa_setzen(w, text=wert, text_color=farbe if erster_wert else config.FARBEN["text"],
                                font=(config.SCHRIFT_CODE, 15 if erster_wert else 13, "bold"))
                self._wa_setzen(z, text=notiz)
                erster_wert = False
            else:
                (t,) = widgets
                self._wa_setzen(t, text=name, text_color=self.WARN if art == "warnung" else
                                (farbe if nur_text else config.FARBEN["text_leise"]),
                                font=(config.SCHRIFT_CODE, 13, "bold") if nur_text else (config.SCHRIFT_CODE, 12))

    # Zellen sind einfache tk.Label (nicht CTkLabel): Beim Ziehen eines Reglers ändern sich die Werte
    # viele Male pro Sekunde - ein CTkLabel zeichnet dabei jedes Mal seine eigene Fläche neu (zu langsam).
    # Farben: Paare (hell, dunkel) werden selbst gewählt, beim Umschalten -> modus_gewechselt().

    def _wa_setzen(self, widget, **optionen):
        """Nur ändern, was sich wirklich geändert hat (text, text_color als Paar, font)."""
        alt = getattr(widget, "wa_stand", {})
        neu = {k: v for k, v in optionen.items() if alt.get(k) != v}
        if neu:
            widget.wa_stand = {**alt, **neu}
            self._wa_anwenden(widget, neu)

    @staticmethod
    def _wa_anwenden(widget, optionen):
        i = 1 if ctk.get_appearance_mode() == "Dark" else 0
        tk_opt = {}
        for k, v in optionen.items():
            if k == "text_color":
                tk_opt["fg"] = v[i] if isinstance(v, (tuple, list)) else v
            else:
                tk_opt[k] = v
        widget.configure(**tk_opt)

    def modus_gewechselt(self):
        """Dark/Light umgeschaltet (core/layout.py): Hintergrund und Schriftfarben neu setzen."""
        hintergrund = self._wa_hintergrund()
        for _art, widgets in self.wa_zeilen:
            for w in widgets:
                w.configure(bg=hintergrund)
                self._wa_anwenden(w, {"text_color": w.wa_stand.get("text_color", config.FARBEN["text"])})

    def _wa_hintergrund(self):
        """Farbe der Fläche dahinter (die Anzeige selbst ist durchsichtig)."""
        i = 1 if ctk.get_appearance_mode() == "Dark" else 0
        farbe = self.master.cget("fg_color") if hasattr(self.master, "cget") else "transparent"
        stufe = self.master
        while farbe == "transparent" and stufe is not None:              # bis zur ersten farbigen Fläche
            stufe = stufe.master
            try:
                farbe = stufe.cget("fg_color")
            except Exception:
                farbe = config.FARBEN["flaeche"]
        return farbe[i] if isinstance(farbe, (tuple, list)) else farbe

    def anpassen(self, breite):
        """Breite bekannt -> Zeilenumbruch der Text- und Notizzeilen setzen (tk.Label: echte Pixel)."""
        for art, widgets in self.wa_zeilen:
            ziel = widgets[0] if art != "wert" else widgets[2]
            ziel.configure(wraplength=max(120, breite - (ziel.winfo_x() if art == "wert" else 0) - 10))

    def _wa_zeile(self, nummer, art):
        import tkinter as tk
        bg = self._wa_hintergrund()
        def label(**kw):
            l = tk.Label(self, text="", bg=bg, anchor="w", justify="left", borderwidth=0, padx=0, pady=1, **kw)
            l.wa_stand = {}
            return l
        if art == "wert":
            name = label(font=(config.SCHRIFT_CODE, 12))
            self._wa_setzen(name, text_color=config.FARBEN["text_leise"])
            name.grid(row=nummer, column=0, sticky="nw", padx=(0, 14))
            wert = label()
            wert.grid(row=nummer, column=1, sticky="nw", padx=(0, 12))
            notiz = label(font=config.FONT_KLEIN, wraplength=360)
            self._wa_setzen(notiz, text_color=config.FARBEN["text_leise"])
            notiz.grid(row=nummer, column=2, sticky="ew")
            return [name, wert, notiz]
        text = label(font=(config.SCHRIFT_CODE, 12), wraplength=600)
        text.grid(row=nummer, column=0, columnspan=3, sticky="ew", pady=(3, 1))
        return [text]


# =============================================================================
# LOGIK-TASTATUR: Tastenleiste für logische Ausdrücke (DNF/KNF, KV, Wahrheitstabelle)
# =============================================================================
class LogikTastatur(ctk.CTkFrame):
    """
    [A][B][C][D]  [¬][·][+][⊕]  [(][)]  [⌫]
    Ein Klick fügt das Zeichen an der Cursor-Stelle im Eingabefeld ein (wie ein kleiner Taschenrechner).
        LogikTastatur(master, eingabefeld, bei_aenderung=None, variablen="ABCD")
    bei_aenderung: Funktion ohne Argumente, wird nach jedem Klick aufgerufen (z.B. neu rechnen)
    Die Zeichen versteht digitaltechnik/logik_mathe.py (¬ · + ⊕ - auch ! * / ^ gehen beim Tippen).
    """

    ZEICHEN = [("¬", "NICHT (vor die Variable)"), ("·", "UND"), ("+", "ODER"), ("⊕", "XOR"),
               ("(", "Klammer auf"), (")", "Klammer zu")]

    def __init__(self, master, feld, bei_aenderung=None, variablen="ABCD"):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.lt_feld = feld
        self.lt_funktion = bei_aenderung
        tasten = [(v, f"Variable {v}") for v in variablen] + [None] + self.ZEICHEN + [None] + [("⌫", "Zeichen löschen")]
        spalte = 0
        for taste in tasten:
            if taste is None:                                          # kleine Lücke zwischen den Gruppen
                ctk.CTkFrame(self, width=8, height=1, fg_color="transparent").grid(row=0, column=spalte)
                spalte += 1
                continue
            zeichen, tipp = taste
            knopf = ctk.CTkButton(self, text=zeichen, width=32, height=28, font=(config.SCHRIFT_CODE, 14, "bold"),
                                  fg_color=config.FARBEN["hintergrund"], text_color=config.FARBEN["text"],
                                  hover_color=config.FARBEN["rahmen"], border_width=1,
                                  border_color=config.FARBEN["rahmen"],
                                  command=lambda z=zeichen: self._lt_taste(z))
            knopf.grid(row=0, column=spalte, padx=1)
            Tooltip(knopf, tipp)
            spalte += 1

    def _lt_taste(self, zeichen):
        feld = self.lt_feld
        if zeichen == "⌫":
            stelle = feld.index("insert")
            if stelle > 0:
                feld.delete(stelle - 1)
        else:
            text = f" {zeichen} " if zeichen in "+⊕" else zeichen        # A + B liest sich besser als A+B
            feld.insert("insert", text)
        feld.focus_set()
        if self.lt_funktion:
            self.lt_funktion()


# =============================================================================
# KARTE & INFO-BOX
# =============================================================================
def karte(master, **kwargs):
    """Kasten mit abgerundeten Ecken und Rahmen. Spalte 0 wächst mit."""
    kasten = ctk.CTkFrame(master, corner_radius=10, border_width=1,
                          fg_color=kwargs.pop("fg_color", config.FARBEN["flaeche"]),
                          border_color=config.FARBEN["rahmen"], **kwargs)
    kasten.grid_columnconfigure(0, weight=1)
    return kasten


def info_box(master, titel, eintraege, art="tipp"):
    """Farbige Box: art="tipp" (blau) oder art="warnung" (orange)."""
    box = ctk.CTkFrame(master, corner_radius=10, fg_color=config.FARBEN[art])
    box.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(box, text=titel, font=config.FONT_SEKTION, anchor="w",
                 text_color=config.FARBEN["text"]).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
    text = FormatText(box, hintergrund=art)
    text.setze_text("\n".join(f"- {e}" for e in eintraege))
    text.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
    return box


# =============================================================================
# FORMAT-TEXT  (mini "Markdown")
# =============================================================================
class FormatText(tk.Text, Responsive):
    """
    Text-Feld (nur lesen) mit einfachen Formatierungen:
        ## Überschrift   - Punkt   **fett**   `code`

    Die Höhe wird in PIXELN gemessen (inkl. grösserer Überschriften und
    Abständen) und dann gesetzt -> es wird nie etwas abgeschnitten.
    Berechnet wird nur, wenn sich die BREITE ändert (-> core/layout.py).
    """

    _MUSTER = re.compile(r"(\*\*.+?\*\*|`.+?`)")

    def __init__(self, master, hintergrund="flaeche", **kwargs):
        self._ft_hintergrund = hintergrund
        super().__init__(master, wrap="word", height=1, width=10, borderwidth=0, highlightthickness=0,
                         font=config.FONT_TEXT, padx=4, pady=2, cursor="arrow", **kwargs)

        s = config.SCHRIFT
        self.tag_configure("h2", font=(s, 15, "bold"), spacing1=10, spacing3=4)
        self.tag_configure("fett", font=(s, 13, "bold"))
        self.tag_configure("code", font=config.FONT_CODE)
        self.tag_configure("punkt", lmargin1=8, lmargin2=26, spacing1=2)
        self.tag_configure("absatz", spacing1=2, spacing3=6)
        self.modus_gewechselt()                # Farben passend zum aktuellen Modus

        # Höhe einer "Zeile" in Pixel (tk.Text misst height in Zeilen der Grundschrift)
        self._zeilenhoehe = max(1, int(self.tk.call("font", "metrics", config.FONT_TEXT, "-linespace")))
        self.responsive_starten()              # -> core/layout.py

    def modus_gewechselt(self):
        """Farben für Dark/Light setzen (beim Erstellen und nach jedem Umschalten, core/layout.py)."""
        modus = ctk.get_appearance_mode()
        farben = config.TEXT_FARBEN[modus]
        hell, dunkel = config.FARBEN.get(self._ft_hintergrund, config.FARBEN["flaeche"])
        self.configure(bg=dunkel if modus == "Dark" else hell, fg=farben["text"])
        self.tag_configure("h2", foreground=farben["ueberschrift"])
        self.tag_configure("code", background=farben["code_bg"])

    def setze_text(self, text):
        self.configure(state="normal")
        self.delete("1.0", "end")
        for zeile in text.strip("\n").split("\n"):
            zeile = zeile.strip()
            if zeile.startswith("## "):
                self.insert("end", zeile[3:] + "\n", "h2")
            elif zeile.startswith("- "):
                self._inline("•  " + zeile[2:], "punkt")
                self.insert("end", "\n")
            else:
                self._inline(zeile, "absatz")
                self.insert("end", "\n")
        self.delete("end-1c", "end")
        self.configure(state="disabled")
        # Vorläufige Höhe (Anzahl Zeilen), die genaue kommt, sobald die Breite bekannt ist
        self.configure(height=int(self.index("end-1c").split(".")[0]))
        self.neu_berechnen()

    def _inline(self, zeile, grund_tag):
        for teil in self._MUSTER.split(zeile):
            if not teil:
                continue
            if teil.startswith("**") and teil.endswith("**"):
                self.insert("end", teil[2:-2], (grund_tag, "fett"))
            elif teil.startswith("`") and teil.endswith("`"):
                self.insert("end", teil[1:-1], (grund_tag, "code"))
            else:
                self.insert("end", teil, grund_tag)

    def anpassen(self, breite):
        """Wird von core/layout.py aufgerufen, wenn sich die Breite geändert hat."""
        if breite < 60 or not self.winfo_ismapped():
            return          # versteckt / zu schmal -> nicht rechnen (sonst tausende Zeilen)
        try:
            pixel = int(self.tk.call(self._w, "count", "-update", "-ypixels", "1.0", "end"))
        except (tk.TclError, ValueError):
            return
        zeilen = max(1, math.ceil(pixel / self._zeilenhoehe))
        if zeilen != int(self.cget("height")):
            self.configure(height=zeilen)
