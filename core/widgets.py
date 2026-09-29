# =============================================================================
# core/widgets.py
# -----------------------------------------------------------------------------
# Wiederverwendbare GUI-Bausteine für ALLE Seiten der Toolbox.
# (Alles rund um "mit der Fenstergrösse mitgehen" steht in core/layout.py)
#
# INHALT:
#   Tooltip             Hinweistext, wenn die Maus über einem Button ist
#   SeitenBereich       Ein ganzer Bereich: Icon-Leiste links + Scroll-Inhalt rechts
#                       (benutzt von Bauteile, Schaltungen, Formeln, Messwerte)
#   FormatText          Text mit ## Überschrift, - Punkt, **fett**, `code`
#                       Höhe passt sich automatisch an -> nie abgeschnitten
#   karte()             Kasten mit Rahmen (Spalte 0 wächst mit)
#   info_box()          Farbige Box für Tipps / Warnungen
#   platzhalter_seite() Seite für Bereiche "im Aufbau"
# =============================================================================

import math
import re
import tkinter as tk

import customtkinter as ctk

import config                                               # -> config.py
from core.layout import Responsive, ScrollSeite, Stapel, seiten_kopf   # -> core/layout.py


# =============================================================================
# TOOLTIP
# =============================================================================
class Tooltip:
    """Tooltip(mein_button, "Widerstand") - erscheint nach 400 ms."""

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
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 8
        y = self.widget.winfo_rooty() + 6
        self.fenster = tk.Toplevel(self.widget)
        self.fenster.wm_overrideredirect(True)
        self.fenster.wm_geometry(f"+{x}+{y}")
        tk.Label(self.fenster, text=self.text, bg="#2B2F36", fg="white",
                 padx=8, pady=4, font=config.FONT_KLEIN).pack()

    def _verstecken(self, event=None):
        if self._timer is not None:
            self.widget.after_cancel(self._timer)
            self._timer = None
        if self.fenster is not None:
            self.fenster.destroy()
            self.fenster = None


# =============================================================================
# SEITEN-BEREICH  (Icon-Leiste links + scrollbarer Inhalt rechts)
# =============================================================================
class SeitenBereich(ctk.CTkFrame):
    """
    Baut einen kompletten Bereich (z.B. "Bauteile"):

        ┌────┬──────────────────────────────────┐
        │ ⬅  │                                  │
        │ Wi │   Seite (scrollbar, wächst mit)  │
        │ Ko │                                  │
        └────┴──────────────────────────────────┘

        bereich = SeitenBereich(tab, app)
        bereich.eintrag_hinzufuegen("Widerstand", widerstand.create, icon="resistor.png")
        bereich.seite_zeigen("Widerstand")

    Jede Seite ist eine Funktion  create(parent) . 'parent' ist bereits die
    scrollbare, mitwachsende Seite (Spalte 0 hat weight=1) - die Seite muss
    sich um Scrollen und Breite NICHT mehr kümmern.
    """

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.FARBEN["hintergrund"], corner_radius=0)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")

        # Spalte 0 = Leiste (feste Breite), Spalte 1 = Inhalt (bekommt den ganzen Rest)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # ---- Icon-Leiste links ----
        self.leiste = ctk.CTkFrame(self, width=64, corner_radius=0, fg_color=config.FARBEN["sidebar"])
        self.leiste.grid(row=0, column=0, sticky="ns")
        zurueck = ctk.CTkButton(self.leiste, text="⬅", width=44, height=44, command=app.show_startseite,
                                fg_color="transparent", border_width=1,
                                border_color=config.FARBEN["rahmen"], text_color=config.FARBEN["text"])
        zurueck.grid(row=0, column=0, padx=10, pady=(10, 16))
        Tooltip(zurueck, "Zur Startseite")

        # ---- Inhalt rechts -> core/layout.py ScrollSeite ----
        self.scroll = ScrollSeite(self)
        self.scroll.grid(row=0, column=1, sticky="nsew")

        self._seiten = {}          # name -> create-Funktion
        self._buttons = {}         # name -> Button

    def eintrag_hinzufuegen(self, name, create_funktion, icon=None, text_kurz=None):
        from core.bilder import icon_laden          # -> core/bilder.py
        bild = icon_laden(icon) if icon else None
        text = "" if bild else (text_kurz or name[:2])
        button = ctk.CTkButton(self.leiste, image=bild, text=text, width=44, height=44,
                               command=lambda: self.seite_zeigen(name))
        button.grid(row=len(self._buttons) + 1, column=0, padx=10, pady=4)
        Tooltip(button, name)
        self._seiten[name] = create_funktion
        self._buttons[name] = button

    def seite_zeigen(self, name):
        for n, b in self._buttons.items():
            b.configure(fg_color=config.FARBEN["akzent"] if n == name else ("#8A94A6", "#3A3F4A"))
        body = self.scroll.neue_seite()             # alte Seite weg, neue leere Seite
        # -> Sprung in die create()-Funktion, z.B. bauteile/widerstand.py
        self._seiten[name](body)


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
        modus = ctk.get_appearance_mode()
        farben = config.TEXT_FARBEN[modus]
        hell, dunkel = config.FARBEN.get(hintergrund, config.FARBEN["flaeche"])

        super().__init__(master, wrap="word", height=1, width=10, borderwidth=0, highlightthickness=0,
                         bg=dunkel if modus == "Dark" else hell, fg=farben["text"], font=config.FONT_TEXT,
                         padx=4, pady=2, cursor="arrow", **kwargs)

        s = config.SCHRIFT
        self.tag_configure("h2", font=(s, 15, "bold"), foreground=farben["ueberschrift"],
                           spacing1=10, spacing3=4)
        self.tag_configure("fett", font=(s, 13, "bold"))
        self.tag_configure("code", font=config.FONT_CODE, background=farben["code_bg"])
        self.tag_configure("punkt", lmargin1=8, lmargin2=26, spacing1=2)
        self.tag_configure("absatz", spacing1=2, spacing3=6)

        # Höhe einer "Zeile" in Pixel (tk.Text misst height in Zeilen der Grundschrift)
        self._zeilenhoehe = max(1, int(self.tk.call("font", "metrics", config.FONT_TEXT, "-linespace")))
        self.responsive_starten()              # -> core/layout.py

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


# =============================================================================
# PLATZHALTER-SEITE
# =============================================================================
def platzhalter_seite(parent, titel, text="Diese Seite ist noch im Aufbau. 🚧"):
    """Einheitliche Seite für Bereiche, die noch leer sind."""
    seiten_kopf(Stapel(parent), titel, text)
