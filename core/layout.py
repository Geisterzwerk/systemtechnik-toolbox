# =============================================================================
# core/layout.py
# -----------------------------------------------------------------------------
# RESPONSIVE LAYOUT für die GANZE Toolbox.
# Alles, was mit der Fenstergrösse mitgehen soll, kommt aus DIESER Datei.
#
# BAUSTEINE
#   ScrollSeite      Scrollbarer Inhaltsbereich. Füllt die Breite, auf sehr
#                    breiten Bildschirmen wird der Inhalt zentriert (max. Breite
#                    einstellbar in config.INHALT_MAX_BREITE).
#   Stapel           Legt Widgets einfach untereinander (row 0, 1, 2, ...).
#   seiten_kopf()    Titel + Untertitel einer Seite.
#   Karte            Kasten mit Titel/Untertitel, Inhalt kommt in karte.body
#   ResponsiveGrid   Karten nebeneinander -> bei schmalem Fenster untereinander
#   WrapLabel        Text, der automatisch umbricht (nie abgeschnitten)
#   ResponsiveBild   Bild, das mit der Breite mitskaliert
#   ResponsiveCanvas Zeichenfläche, die mitskaliert (z.B. Trafo-Animation)
#   Tabelle          Tabelle, deren Spalten mitwachsen und Text umbrechen
#
# DIE GRUNDREGEL (gilt für jedes Layout in tkinter)
#   Damit etwas mitwächst, braucht es IMMER zwei Dinge:
#     1. Eltern-Container gibt Platz her:   parent.grid_columnconfigure(0, weight=1)
#     2. Kind nimmt den Platz an:           widget.grid(..., sticky="ew")
#   C#-Vergleich: weight ~ Width="*" im WPF-Grid, sticky ~ HorizontalAlignment="Stretch"
#
# WARUM EINE "ZENTRALE"?
#   Beim Ziehen am Fenster feuert tkinter pro Widget hunderte <Configure>-
#   Ereignisse. Würde jedes Widget sofort neu rechnen, hängt das Programm
#   (genau das ist vorher passiert). Deshalb melden sich die Widgets nur bei
#   der Zentrale, und diese rechnet 60 ms später EINMAL alles gebündelt neu.
#   Zusätzlich reagieren alle Bausteine nur auf Änderungen der BREITE, nie
#   auf die Höhe -> keine Endlosschleifen mehr.
# =============================================================================

import math
import time
import tkinter as tk

import customtkinter as ctk

import config                          # -> config.py (Farben, Schriften, Breiten)
from core import bilder                # -> core/bilder.py (Bilder finden/laden)


# =============================================================================
# ZENTRALE: sammelt Grössenänderungen und arbeitet sie gebündelt ab
# =============================================================================
class _Zentrale:
    def __init__(self):
        self._wartend = {}        # id(widget) -> widget
        self._timer = None

    def melden(self, widget):
        self._wartend[id(widget)] = widget
        if self._timer is None:
            try:
                # after() am HAUPTFENSTER planen (nicht am Widget), damit der
                # Timer nicht verloren geht, wenn das Widget zerstört wird.
                self._timer = widget._root().after(config.RESIZE_VERZOEGERUNG_MS, self._abarbeiten)
            except tk.TclError:
                self._timer = None

    def _abarbeiten(self):
        self._timer = None
        liste = list(self._wartend.values())
        self._wartend.clear()
        for widget in liste:
            try:
                if widget.winfo_exists():
                    widget._r_ausfuehren()
            except tk.TclError:
                pass                                   # Widget gerade zerstört -> egal
            except Exception as fehler:                # Fehler in EINEM Widget darf nicht alles stoppen
                print(f"[layout] {type(widget).__name__}: {fehler}")


_ZENTRALE = _Zentrale()


class Responsive:
    """
    Mixin (Zusatz-Klasse) für Widgets, die auf die BREITE reagieren.
    Eine Klasse, die das benutzt, muss nur die Methode  anpassen(breite)  haben
    und im Konstruktor  self.responsive_starten()  aufrufen.
    breite = echte Pixel (inkl. Windows-Skalierung)
    """

    def responsive_starten(self):
        self._r_breite = 0            # zuletzt verarbeitete Breite
        self._r_neu = 0               # zuletzt gemeldete Breite
        self._r_verlauf = []          # letzte Breiten (für Schwingungs-Schutz)
        self._r_zeiten = []           # Zeitpunkte der letzten Anpassungen (Rate-Limit)
        self._r_gewarnt = False
        # tk.Misc.bind -> direkt am äusseren Rahmen, auch bei CustomTkinter-Widgets
        tk.Misc.bind(self, "<Configure>", self._r_configure, "+")
        tk.Misc.bind(self, "<Map>", lambda e: self.neu_berechnen(), "+")   # sichtbar geworden

    def _r_configure(self, event):
        if event.width > 1 and event.width != self._r_breite:   # NUR Breite zählt
            self._r_neu = event.width
            _ZENTRALE.melden(self)

    def neu_berechnen(self):
        """Erzwingt eine Neuberechnung (z.B. nachdem sich der Inhalt geändert hat)."""
        self._r_breite = 0
        try:
            breite = self.winfo_width()
        except tk.TclError:
            return
        if breite > 1:
            self._r_neu = breite
            _ZENTRALE.melden(self)

    def _r_ausfuehren(self):
        neu = self._r_neu
        if neu == self._r_breite:
            return
        # --- SCHUTZ 1: Hin-und-her-Schwingen erkennen (A -> B -> A -> B ...) ---
        # Passiert, wenn eine Anpassung die eigene Breite wieder verändert.
        # Dann bleiben wir einfach beim aktuellen Zustand stehen.
        verlauf = self._r_verlauf
        if len(verlauf) >= 2 and abs(neu - verlauf[-2]) <= 3:
            self._r_breite = neu
            self._r_verlauf = (verlauf + [neu])[-4:]
            return
        # --- SCHUTZ 2: max. 8 Anpassungen pro Sekunde pro Widget ---
        jetzt = time.monotonic()
        zeiten = [t for t in self._r_zeiten if jetzt - t < 1.0]
        if len(zeiten) >= 8:
            self._r_breite = neu
            if not self._r_gewarnt:
                self._r_gewarnt = True
                print(f"[layout] {type(self).__name__} passt sich zu oft an -> gebremst")
            return
        zeiten.append(jetzt)
        self._r_zeiten = zeiten
        self._r_verlauf = (verlauf + [neu])[-4:]
        self._r_breite = neu
        self.anpassen(neu)

    def anpassen(self, breite):          # wird von der Unterklasse überschrieben
        pass

    def _skalierung(self):
        """Windows-Anzeigeskalierung (z.B. 1.25 bei 125 %)."""
        try:
            return self._get_widget_scaling()
        except AttributeError:
            return 1.0


# =============================================================================
# SCROLL-SEITE
# =============================================================================
class ScrollSeite(ctk.CTkScrollableFrame):
    """
    Scrollbarer Inhaltsbereich. EIN Objekt pro Bereich, die Seiten werden darin
    ausgetauscht:
        body = scroll.neue_seite()     # alte Seite weg, neue leere Seite
        ... Widgets in body einfügen (Spalte 0 hat weight=1) ...

    - Inhalt füllt immer die volle Breite
    - Ist das Fenster breiter als config.INHALT_MAX_BREITE, wird der Inhalt
      zentriert (lange Textzeilen sind schlecht lesbar)
    """

    def __init__(self, master, max_breite=None, **kwargs):
        kwargs.setdefault("fg_color", config.FARBEN["hintergrund"])
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)
        self.max_breite = config.INHALT_MAX_BREITE if max_breite is None else max_breite
        self.grid_columnconfigure(0, weight=1)
        self.body = None
        self._breite = 0
        self._rand = None
        tk.Misc.bind(self, "<Configure>", self._bei_groessenaenderung, "+")
        self.neue_seite()

    def neue_seite(self):
        """Alte Seite löschen, neue leere Seite anlegen und nach oben scrollen."""
        if self.body is not None:
            self.body.destroy()
        self.body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.body.grid_columnconfigure(0, weight=1)
        self._rand = None
        self._rand_setzen()
        try:
            self._parent_canvas.yview_moveto(0)
        except (AttributeError, tk.TclError):
            pass
        return self.body

    # ACHTUNG Name: NICHT "_configure" nennen! Das ist eine interne Methode von
    # tkinter (wird bei jedem .configure() benutzt) -> würde alles kaputt machen.
    def _bei_groessenaenderung(self, event):
        if event.width != self._breite:
            self._breite = event.width
            self._rand_setzen()

    def _rand_setzen(self):
        skalierung = self._get_widget_scaling()
        breite = self._breite / skalierung if self._breite > 1 else 0
        rand = config.SEITEN_RAND
        if self.max_breite and breite > self.max_breite + 2 * rand:
            rand = int((breite - self.max_breite) / 2)       # zentrieren
        if rand != self._rand:
            self._rand = rand
            # padx wird von CustomTkinter automatisch skaliert -> unskalierte Werte
            self.body.grid(row=0, column=0, sticky="ew", padx=rand, pady=(4, config.SEITEN_RAND))


# =============================================================================
# STAPEL & SEITENKOPF
# =============================================================================
class Stapel:
    """
    Legt Widgets untereinander, volle Breite:
        s = Stapel(body)
        s.add(Karte(body, titel="Rechner"))
    """

    def __init__(self, parent):
        self.parent = parent
        self.zeile = 0
        parent.grid_columnconfigure(0, weight=1)

    def add(self, widget, pady=(0, 12), sticky="ew", **grid_kwargs):
        widget.grid(row=self.zeile, column=0, sticky=sticky, pady=pady, **grid_kwargs)
        self.zeile += 1
        return widget


def seiten_kopf(stapel, titel, untertitel=None, pfad=None):
    """Pfad (klein, grau) + Titel + Untertitel oben auf einer Seite."""
    p = stapel.parent
    if pfad:
        stapel.add(WrapLabel(p, text=pfad, font=config.FONT_KLEIN,
                             text_color=config.FARBEN["text_leise"]), pady=(14, 0))
    stapel.add(WrapLabel(p, text=titel, font=config.FONT_TITEL,
                         text_color=config.FARBEN["text"]), pady=(2 if pfad else 14, 0))
    if untertitel:
        stapel.add(WrapLabel(p, text=untertitel, font=config.FONT_UNTERTITEL,
                             text_color=config.FARBEN["text_leise"]), pady=(2, 12))
    else:
        stapel.add(ctk.CTkFrame(p, height=8, fg_color="transparent"), pady=0)


# =============================================================================
# KARTE
# =============================================================================
class Karte(ctk.CTkFrame):
    """
    Kasten mit Rahmen, optionalem Titel/Untertitel. Inhalt kommt in karte.body
    (Spalte 0 von body hat weight=1 -> Inhalt kann mitwachsen).
    """

    def __init__(self, master, titel=None, untertitel=None, **kwargs):
        kwargs.setdefault("fg_color", config.FARBEN["flaeche"])
        kwargs.setdefault("border_color", config.FARBEN["rahmen"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 10)
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        zeile = 0
        if titel:
            WrapLabel(self, text=titel, font=config.FONT_SEKTION, text_color=config.FARBEN["text"]) \
                .grid(row=zeile, column=0, sticky="ew", padx=16, pady=(14, 0))
            zeile += 1
        if untertitel:
            WrapLabel(self, text=untertitel, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"]) \
                .grid(row=zeile, column=0, sticky="ew", padx=16, pady=(2, 0))
            zeile += 1

        self.grid_rowconfigure(zeile, weight=1)
        self.body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.body.grid(row=zeile, column=0, sticky="nsew", padx=16, pady=(8 if zeile else 14, 14))
        self.body.grid_columnconfigure(0, weight=1)


# =============================================================================
# RESPONSIVE GRID
# =============================================================================
class ResponsiveGrid(ctk.CTkFrame, Responsive):
    """
    Legt Elemente nebeneinander. Wird das Fenster schmaler, rutschen sie
    automatisch untereinander (wie eine Webseite auf dem Handy).

        grid = stapel.add(ResponsiveGrid(body, min_spaltenbreite=340, max_spalten=2))
        grid.add(Karte(grid, titel="Ohm"))
        grid.add(Karte(grid, titel="Leistung"))
    """

    def __init__(self, master, min_spaltenbreite=340, max_spalten=2, abstand=12, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.min_spaltenbreite = min_spaltenbreite
        self.max_spalten = max_spalten
        self.abstand = abstand
        self._elemente = []
        self._spalten = 1
        self.responsive_starten()

    def add(self, widget):
        self._elemente.append(widget)
        self._anordnen()
        return widget

    def anpassen(self, breite):
        breite = breite / self._skalierung()
        spalten = int((breite + self.abstand) // (self.min_spaltenbreite + self.abstand))
        spalten = max(1, min(self.max_spalten, spalten, len(self._elemente) or 1))
        if spalten != self._spalten:
            self._spalten = spalten
            self._anordnen()

    def _anordnen(self):
        n = self._spalten
        for s in range(self.max_spalten):
            # uniform -> alle aktiven Spalten exakt gleich breit
            self.grid_columnconfigure(s, weight=1 if s < n else 0, uniform="spalte" if s < n else "")
        halb = self.abstand // 2
        for i, widget in enumerate(self._elemente):
            zeile, spalte = divmod(i, n)
            links = 0 if spalte == 0 else halb
            rechts = 0 if spalte == n - 1 else halb
            widget.grid(row=zeile, column=spalte, sticky="nsew", padx=(links, rechts), pady=(0, self.abstand))


# =============================================================================
# WRAP-LABEL
# =============================================================================
class WrapLabel(ctk.CTkLabel, Responsive):
    """
    Label, dessen Text automatisch an die Breite umbricht.
    WICHTIG: mit sticky="ew" in eine Spalte mit weight=1 legen.
    """

    def __init__(self, master, **kwargs):
        kwargs.setdefault("anchor", "w")
        kwargs.setdefault("justify", "left")
        kwargs.setdefault("wraplength", 300)          # Startwert, wird sofort angepasst
        self._wl = kwargs["wraplength"]
        super().__init__(master, **kwargs)
        self.responsive_starten()

    def anpassen(self, breite):
        wl = int(breite / self._skalierung()) - 12
        if wl > 40 and abs(wl - self._wl) > 8:          # erst ab 8 px Unterschied
            self._wl = wl
            self.configure(wraplength=wl)


# =============================================================================
# RESPONSIVE BILD
# =============================================================================
class ResponsiveBild(ctk.CTkLabel, Responsive):
    """
    Bild, das so breit wird wie der Platz (höchstens max_breite / Originalbreite).
    Seitenverhältnis bleibt erhalten. Fehlt das Bild -> Hinweistext statt Absturz.

    PERFORMANCE: Grosse Bilder (z.B. farbcode.png) werden beim Laden EINMAL auf
    die maximale Anzeigegrösse verkleinert. Die Breite springt in 24-px-Schritten,
    und jede Grösse wird nur einmal erzeugt (Cache). Vorher wurde bei jeder
    kleinen Breitenänderung das grosse Originalbild neu skaliert -> sehr langsam.
    """

    SCHRITT = 24

    def __init__(self, master, pfad, max_breite=None, **kwargs):
        pil = bilder.pil_laden(pfad)                       # -> core/bilder.py
        text = "" if pil else f"🖼  Bild fehlt: {pfad}"
        super().__init__(master, text=text, text_color=config.FARBEN["text_leise"], **kwargs)
        self._max = min(max_breite or 10_000, pil.width if pil else 0)
        self._pil = None
        self._cache = {}
        self._aktuell = None
        if pil:
            # einmal verkleinern (max. 2x Anzeigebreite -> scharf auch bei 200 % Skalierung)
            ziel = min(pil.width, int(self._max * 2))
            if ziel < pil.width:
                pil = pil.resize((ziel, int(pil.height * ziel / pil.width)))
            self._pil = pil
            self.responsive_starten()

    def anpassen(self, breite):
        b = int(breite / self._skalierung()) - 20            # Platz für CTkLabel-Innenabstand
        b = min(self._max, (b // self.SCHRITT) * self.SCHRITT)
        if b < 60 or b == self._aktuell:
            return
        self._aktuell = b
        if b not in self._cache:
            h = max(1, int(b * self._pil.height / self._pil.width))
            self._cache[b] = ctk.CTkImage(self._pil, self._pil, size=(b, h))
        self.configure(image=self._cache[b])


# =============================================================================
# RESPONSIVE CANVAS
# =============================================================================
class ResponsiveCanvas(tk.Canvas, Responsive):
    """
    Zeichenfläche, die mit der Breite mitwächst (Höhe = Breite * seitenverhaeltnis).
    Gezeichnet wird in RELATIVEN Koordinaten:

        def zeichnen(c, w, h):
            c.create_rectangle(0.2*w, 0.4*h, 0.8*w, 0.6*h, fill="gray", tags="kern")

    Für Animationen Elemente über TAGS ansprechen (c.move("strom", 0, 2)),
    nicht über gespeicherte IDs - beim Neuzeichnen entstehen neue IDs.
    """

    def __init__(self, master, zeichnen, seitenverhaeltnis=0.4, max_hoehe=460, **kwargs):
        hell, dunkel = config.FARBEN["flaeche"]
        super().__init__(master, width=1, height=200, highlightthickness=0,
                         bg=dunkel if ctk.get_appearance_mode() == "Dark" else hell, **kwargs)
        self.zeichnen = zeichnen
        self.verhaeltnis = seitenverhaeltnis
        self.max_hoehe = max_hoehe
        self.responsive_starten()

    def anpassen(self, breite):
        hoehe = min(int(breite * self.verhaeltnis), self.max_hoehe)
        self.configure(height=hoehe)           # nur Höhe -> löst keine neue Breite aus
        self.delete("all")
        self.zeichnen(self, breite, hoehe)


# =============================================================================
# TABELLE
# =============================================================================
class Tabelle(ctk.CTkFrame, Responsive):
    """
    Tabelle mit Kopfzeile und Zebra-Streifen. Alle Spalten gleich breit,
    Text bricht in den Zellen automatisch um.

        Tabelle(body, kopf=["Typ", "Bit"], zeilen=[["int", "32"], ["char", "8"]])
    """

    def __init__(self, master, kopf, zeilen, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.n = max([len(kopf)] + [len(z) for z in zeilen] + [1])
        for s in range(self.n):
            self.grid_columnconfigure(s, weight=1, uniform="tabelle")
        self._zellen = []
        self._wl = 150

        for s, text in enumerate(kopf):
            self._zelle(0, s, text, (config.SCHRIFT, 12, "bold"), config.FARBEN["tabelle_kopf"])
        for z, zeile in enumerate(zeilen, start=1):
            farbe = config.FARBEN["tabelle_zeile"] if z % 2 == 0 else "transparent"
            for s, text in enumerate(zeile):
                schrift = (config.SCHRIFT_CODE, 12, "bold") if s == 0 else config.FONT_KLEIN
                self._zelle(z, s, text, schrift, farbe)
        self.responsive_starten()

    def _zelle(self, zeile, spalte, text, schrift, farbe):
        label = ctk.CTkLabel(self, text=f" {text}", font=schrift, fg_color=farbe, corner_radius=0,
                             text_color=config.FARBEN["text"], anchor="w", justify="left",
                             wraplength=self._wl)
        label.grid(row=zeile, column=spalte, sticky="nsew", padx=1, pady=0)
        self._zellen.append(label)

    def anpassen(self, breite):
        wl = max(50, int(breite / self._skalierung() / self.n) - 14)
        if abs(wl - self._wl) > 3:
            self._wl = wl
            for label in self._zellen:
                label.configure(wraplength=wl)
