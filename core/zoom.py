# =============================================================================
# core/zoom.py
# -----------------------------------------------------------------------------
# ZOOM für die ganze App (wie im Browser): 50 % … 200 % in Stufen (config.ZOOM_STUFEN).
#
#   Ctrl + Mausrad        grösser / kleiner
#   Ctrl + Plus / Minus   grösser / kleiner   (auch Ziffernblock)
#   Ctrl + 0              zurück auf 100 %
#   ZoomRegler            [−] 100 % [+] auf der Startseite (Klick auf die Zahl = 100 %)
#
# WIE?  Zwei Dinge zusammen:
#   1. ctk.set_widget_scaling(f)   -> alle customtkinter-Knöpfe, -Felder, -Texte
#   2. tk scaling (Grundwert · f)  -> alles mit normalen tk-Schriften: Beschriftungen in Grafiken und
#                                     Schaltplänen, Fliesstext, Tabellen
#   Danach werden alle Grafiken neu gezeichnet (core/layout.py modus_gewechselt - derselbe Weg wie Dark/Light).
# Die Stufe wird in benutzerdaten.json gemerkt (Einstellung "zoom").
#
# WER RUFT DAS AUF?  main.py (App._tastenkuerzel), gui/startseite_gui.py (ZoomRegler)
# =============================================================================

import customtkinter as ctk

import config                                                          # -> config.py
from core import benutzerdaten, layout                                 # -> core/benutzerdaten.py, core/layout.py


class Zoom:
    def __init__(self, app):
        self.app = app
        self.grund = float(app.tk.call("tk", "scaling"))                  # tk scaling bei 100 %
        gemerkt = benutzerdaten.einstellung("zoom", 100)
        self.prozent = gemerkt if gemerkt in config.ZOOM_STUFEN else 100
        self.anzeige = None
        self.anzeige_timer = None
        self.beobachter = []                                              # Funktionen: werden nach jeder Änderung gerufen
        if self.prozent != 100:
            self._anwenden(neu_zeichnen=False)                            # beim Start: noch nichts gezeichnet

    # ---- Bedienung ----------------------------------------------------------
    def groesser(self, _event=None):
        return self._schritt(+1)

    def kleiner(self, _event=None):
        return self._schritt(-1)

    def zuruecksetzen(self, _event=None):
        self.setzen(100)
        return "break"

    def mausrad(self, event):
        """Ctrl + Mausrad: nach oben = grösser."""
        return self._schritt(+1 if event.delta > 0 else -1)

    def _schritt(self, richtung):
        stufen = config.ZOOM_STUFEN
        i = stufen.index(self.prozent) + richtung
        if 0 <= i < len(stufen):
            self.setzen(stufen[i])
        else:
            self._anzeigen()                                              # am Ende: nur Anzeige
        return "break"

    def setzen(self, prozent):
        if prozent not in config.ZOOM_STUFEN or prozent == self.prozent:
            self._anzeigen()
            return
        self.prozent = prozent
        self._anwenden()
        benutzerdaten.einstellung_setzen("zoom", prozent)
        self._anzeigen()
        for funktion in self.beobachter:
            funktion(prozent)

    def _anwenden(self, neu_zeichnen=True):
        faktor = self.prozent / 100
        if neu_zeichnen:
            self.app.configure(cursor="watch")                            # dauert bei vielen offenen Seiten 1-3 s
            self.app.update_idletasks()
        ctk.set_widget_scaling(faktor)
        self.app.tk.call("tk", "scaling", self.grund * faktor)
        if neu_zeichnen:
            self.app.update_idletasks()
            layout.modus_gewechselt(self.app)                             # Grafiken mit neuen Schriftgrössen zeichnen
            self.app.configure(cursor="")

    # ---- kurze Anzeige oben rechts ("🔍 125 %") -----------------------------
    def _anzeigen(self):
        if self.anzeige is None or not self.anzeige.winfo_exists():
            self.anzeige = ctk.CTkButton(self.app, text="", height=30, corner_radius=15, font=(config.SCHRIFT, 13, "bold"),
                                         fg_color=config.FARBEN["akzent"], hover_color=config.FARBEN["akzent_hover"],
                                         text_color="white", command=lambda: self.setzen(100))
        self.anzeige.configure(text=f"🔍 {self.prozent} %   (Klick = 100 %)")
        self.anzeige.place(relx=1.0, x=-24, y=56, anchor="ne")
        self.anzeige.lift()
        if self.anzeige_timer is not None:
            self.app.after_cancel(self.anzeige_timer)
        self.anzeige_timer = self.app.after(1800, self._verstecken)

    def _verstecken(self):
        self.anzeige_timer = None
        if self.anzeige is not None and self.anzeige.winfo_exists():
            self.anzeige.place_forget()


class ZoomRegler(ctk.CTkFrame):
    """[−]  100 %  [+]  für die Startseite. Klick auf die Zahl = 100 %."""

    def __init__(self, master, zoom):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.zoom = zoom
        stil = dict(width=30, height=28, fg_color="transparent", border_width=1, border_color=config.FARBEN["rahmen"],
                    text_color=config.FARBEN["text"], hover_color=config.FARBEN["rahmen"])
        ctk.CTkLabel(self, text="Zoom", font=config.FONT_TEXT).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkButton(self, text="−", command=zoom.kleiner, **stil).grid(row=0, column=1)
        self.zr_zahl = ctk.CTkButton(self, text="", width=64, height=28, fg_color="transparent",
                                     text_color=config.FARBEN["text"], hover_color=config.FARBEN["rahmen"],
                                     command=zoom.zuruecksetzen)
        self.zr_zahl.grid(row=0, column=2, padx=4)
        ctk.CTkButton(self, text="+", command=zoom.groesser, **stil).grid(row=0, column=3)
        self._zr_text(zoom.prozent)
        zoom.beobachter.append(self._zr_text)

    def _zr_text(self, prozent):
        if self.zr_zahl.winfo_exists():
            self.zr_zahl.configure(text=f"{prozent} %")
