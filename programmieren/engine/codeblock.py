# =============================================================================
# programmieren/engine/codeblock.py
# -----------------------------------------------------------------------------
# GUI-Baustein: Code-Kasten wie in einer IDE (Zeilennummern, Farben, Kopieren).
#
# RESPONSIVE: Der Kasten ist so breit wie die Seite. Ist eine Code-Zeile zu
#             lang, erscheint automatisch ein horizontaler Scrollbalken
#             (und verschwindet wieder, wenn das Fenster breit genug ist).
#
# WER BENUTZT DAS?  engine/seite.py      BENUTZT SELBST: engine/syntax.py
# =============================================================================

import tkinter as tk

import customtkinter as ctk

import config                                  # -> config.py
from programmieren.engine import syntax        # -> engine/syntax.py

SPRACH_FARBE = {"Python": "#3776AB", "C++": "#00599C", "C#": "#68217A", "Bash": "#2F7D32"}


class CodeBlock(ctk.CTkFrame):

    def __init__(self, master, code, sprache):
        modus = ctk.get_appearance_mode()
        self.farben = config.CODE_FARBEN[modus]
        self.code = code.strip("\n")

        super().__init__(master, corner_radius=10, fg_color=self.farben["hintergrund"],
                         border_width=1, border_color=config.FARBEN["rahmen"])
        self.grid_columnconfigure(0, weight=1)

        # ---- Kopfzeile: Sprach-Schild + Kopieren-Button ----
        kopf = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        kopf.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))
        kopf.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(kopf, text=f" {sprache} ", font=(config.SCHRIFT, 11, "bold"),
                     fg_color=SPRACH_FARBE.get(sprache, "#555"), text_color="white",
                     corner_radius=6, height=22).grid(row=0, column=0, sticky="w")
        self.kopier_button = ctk.CTkButton(kopf, text="📋 Kopieren", width=96, height=24,
                                           font=config.FONT_KLEIN, command=self._kopieren,
                                           fg_color="transparent", border_width=1,
                                           border_color=config.FARBEN["rahmen"],
                                           text_color=config.FARBEN["text_leise"],
                                           hover_color=config.FARBEN["rahmen"])
        self.kopier_button.grid(row=0, column=2, sticky="e")

        # ---- Code-Feld (width=10 -> fordert keine feste Breite, wächst mit der Seite) ----
        zeilen = self.code.split("\n")
        self.text = tk.Text(self, wrap="none", borderwidth=0, highlightthickness=0,
                            bg=self.farben["hintergrund"], fg=self.farben["text"],
                            font=config.FONT_CODE, height=len(zeilen), width=10, padx=10, pady=8,
                            insertbackground=self.farben["text"], cursor="xterm")
        self.text.grid(row=1, column=0, sticky="ew", padx=4, pady=(4, 6))

        # ---- Horizontaler Scrollbalken: nur sichtbar, wenn nötig ----
        self.xscroll = ctk.CTkScrollbar(self, orientation="horizontal", command=self.text.xview, height=12)
        self._xscroll_sichtbar = False
        self.text.configure(xscrollcommand=self._xscroll_update)

        self._farben_definieren()
        self._code_einfuegen(zeilen, sprache)
        self.text.bind("<Key>", self._nur_lesen)

    def _xscroll_update(self, erst, letzt):
        self.xscroll.set(erst, letzt)
        noetig = float(erst) > 0.0 or float(letzt) < 1.0
        if noetig and not self._xscroll_sichtbar:
            self.xscroll.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 6))
        elif not noetig and self._xscroll_sichtbar:
            self.xscroll.grid_remove()
        self._xscroll_sichtbar = noetig

    def _farben_definieren(self):
        f = self.farben
        for tag in ("keyword", "typ", "string", "kommentar", "zahl", "funktion"):
            self.text.tag_configure(tag, foreground=f[tag])
        self.text.tag_configure("zeilennr", foreground=f["zeilennr"])
        self.text.tag_configure("kommentar", font=(config.SCHRIFT_CODE, 12, "italic"))
        # Gefährliche Befehle (rm -rf, chmod 777 ...): rot hinterlegt, liegt über allen anderen Farben
        self.text.tag_configure("gefahr", foreground=f["gefahr"], background=f["gefahr_bg"],
                                font=(config.SCHRIFT_CODE, 12, "bold"))

    def _code_einfuegen(self, zeilen, sprache):
        breite = len(str(len(zeilen)))
        for nr in range(1, len(zeilen) + 1):
            self.text.insert("end", f"{nr:>{breite}}  ", "zeilennr")
            self.text.insert("end", zeilen[nr - 1] + ("\n" if nr < len(zeilen) else ""))

        # Einfärben -> engine/syntax.py zerlegen()
        zeile, spalte = 1, breite + 2
        for text, tag in syntax.zerlegen(self.code, sprache):
            for i, teil in enumerate(text.split("\n")):
                if i > 0:
                    zeile += 1
                    spalte = breite + 2
                if tag and teil:
                    self.text.tag_add(tag, f"{zeile}.{spalte}", f"{zeile}.{spalte + len(teil)}")
                spalte += len(teil)

        # Gefährliche Stellen markieren -> engine/syntax.py gefahr_stellen() (nur Bash)
        if sprache == "Bash":
            for nr, inhalt in enumerate(zeilen, start=1):
                for start, ende in syntax.gefahr_stellen(inhalt):
                    self.text.tag_add("gefahr", f"{nr}.{breite + 2 + start}", f"{nr}.{breite + 2 + ende}")
            self.text.tag_raise("gefahr")

    def _nur_lesen(self, event):
        if event.state & 0x4 and event.keysym.lower() in ("c", "a"):    # Ctrl+C / Ctrl+A erlaubt
            return None
        return "break"

    def _kopieren(self):
        self.clipboard_clear()
        self.clipboard_append(self.code)
        self.kopier_button.configure(text="✅ Kopiert")
        self.after(1500, lambda: self.kopier_button.winfo_exists() and
                   self.kopier_button.configure(text="📋 Kopieren"))
