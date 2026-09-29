"""
responsive.py  –  Layout-Bausteine, die mit jeder Fenstergrösse mitgehen
=========================================================================
Alle Seiten benutzen diese Bausteine -> überall gleiches Verhalten.

    SidebarLayout    Sidebar links (fix) + Inhalt rechts (füllt alles)
    ScrollPage       Scrollbare Seite, füllt die Breite (max. Breite, zentriert)
    Card             Kasten mit Titel/Untertitel
    ResponsiveGrid   Karten nebeneinander -> bei wenig Platz untereinander
    WrapLabel        Label mit automatischem Zeilenumbruch
    InfoText         Wiki-Text (## Titel, - Liste, **fett**, `code`), Höhe automatisch
    CodeBlock        Code mit "Kopieren"-Button
    ResponsiveCanvas Zeichenfläche, skaliert mit (relativ zeichnen: 0.25*w)
    form_row         Beschriftung + Eingabefeld (+ Einheit) in einer Zeile

GRUNDREGEL: Damit etwas mitwächst, braucht es IMMER beides:
    parent.grid_columnconfigure(0, weight=1)    # Eltern gibt Platz her
    widget.grid(row=0, column=0, sticky="nsew") # Kind nimmt Platz an
C#/WPF-Vergleich: weight ~ Width="*",  sticky ~ HorizontalAlignment="Stretch"
"""
import re
import tkinter as tk
import customtkinter as ctk

PAD = 12
CARD_COLOR = ("gray92", "gray17")
BORDER_COLOR = ("gray78", "gray25")
TEXT_COLOR = ("gray10", "gray90")
MUTED_COLOR = ("gray40", "gray60")
ACCENT_COLOR = ("#1f6aa5", "#6ea8fe")
CODE_BG = ("gray85", "gray22")
FONT = "Segoe UI"
MONO = "Consolas"


def _pick(pair):
    """("hell","dunkel") -> passende Farbe für normale tk-Widgets."""
    if isinstance(pair, (tuple, list)):
        return pair[1] if ctk.get_appearance_mode() == "Dark" else pair[0]
    return pair


class SidebarLayout(ctk.CTkFrame):
    """Sidebar links + Inhalt rechts.
        layout = SidebarLayout(tab); layout.grid(row=0, column=0, sticky="nsew")
        layout.add_sidebar_button("Wi", lambda: layout.show(widerstand.create))
    """
    def __init__(self, master, sidebar_width=64, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=sidebar_width, corner_radius=10)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(PAD, PAD // 2), pady=PAD)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=(PAD // 2, PAD), pady=PAD)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self._buttons = []
        self._pages = {}              # "dioden" -> (button, create_func)
        self.content.layout = self    # Seiten finden so das Layout (für "Siehe auch")

    def register(self, key, btn, create_func):
        self._pages[key] = (btn, create_func)

    def goto(self, key):
        if key in self._pages:
            btn, func = self._pages[key]
            self.activate(btn, lambda: self.show(func))

    def add_sidebar_button(self, text, command, image=None):
        btn = ctk.CTkButton(self.sidebar, text=text, image=image, width=42, height=42)
        btn.configure(command=lambda: self.activate(btn, command))
        btn.grid(row=len(self._buttons), column=0, pady=(PAD if not self._buttons else 6, 0))
        self._buttons.append(btn)
        return btn

    def activate(self, btn, command):
        for b in self._buttons:
            b.configure(fg_color=("gray75", "gray30"))
        btn.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        command()

    def show(self, create_func):
        for w in self.content.winfo_children():
            w.destroy()
        create_func(self.content)


CONTENT_WIDTH = 900     # feste Inhaltsbreite wie im Programmieren-Tab


class ScrollPage(ctk.CTkScrollableFrame):
    """Scrollbare Wiki-Seite mit FESTER Inhaltsbreite (linksbündig).
    Nichts reagiert auf die Fenstergrösse -> nichts verzieht sich, nichts hängt.
    Ist das Fenster schmaler, wird einfach gescrollt/abgeschnitten wie im Programmieren-Tab.

        page = ScrollPage(parent, title="Widerstand", subtitle="...")
        page.add(Card(page.body, title="Ohm"))
    Breadcrumb: setzt die Navigation automatisch über parent.breadcrumb.
    """
    def __init__(self, master, title=None, subtitle=None, width=CONTENT_WIDTH, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=0, column=0, sticky="nw", padx=(20, 10), pady=(10, 20))
        self.body.grid_columnconfigure(0, weight=1)
        # unsichtbarer Abstandshalter: body ist IMMER genau so breit
        ctk.CTkFrame(self.body, width=width, height=0, fg_color="transparent") \
            .grid(row=999, column=0, sticky="w")

        self._row = 0
        crumb = getattr(master, "breadcrumb", None)
        if crumb:
            self.add(ctk.CTkLabel(self.body, text="▤  " + crumb, anchor="w", text_color=MUTED_COLOR,
                                  font=(FONT, 11)), pady=(0, 4))
        if title:
            self.add(ctk.CTkLabel(self.body, text=title, anchor="w", font=(FONT, 24, "bold")), pady=(0, 2))
        if subtitle:
            self.add(ctk.CTkLabel(self.body, text=subtitle, anchor="w", justify="left", wraplength=width,
                                  text_color=MUTED_COLOR, font=(FONT, 13)), pady=(0, PAD + 4))

    def add(self, widget, pady=(0, PAD + 4)):
        widget.grid(row=self._row, column=0, sticky="ew", pady=pady)
        self._row += 1
        return widget


class Card(ctk.CTkFrame):
    """Kasten mit Titel/Untertitel. Inhalt in card.body."""
    def __init__(self, master, title=None, subtitle=None, **kw):
        kw.setdefault("fg_color", CARD_COLOR)
        kw.setdefault("border_color", BORDER_COLOR)
        kw.setdefault("border_width", 1)
        kw.setdefault("corner_radius", 10)
        super().__init__(master, **kw)
        self.grid_columnconfigure(0, weight=1)
        row = 0
        if title:
            ctk.CTkLabel(self, text=title, anchor="w", font=(FONT, 17, "bold")) \
                .grid(row=row, column=0, sticky="ew", padx=PAD + 4, pady=(PAD + 2, 0)); row += 1
        if subtitle:
            WrapLabel(self, text=subtitle, text_color=MUTED_COLOR, font=(FONT, 12)) \
                .grid(row=row, column=0, sticky="ew", padx=PAD + 4, pady=(2, 0)); row += 1
        self.grid_rowconfigure(row, weight=1)
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=row, column=0, sticky="nsew", padx=PAD + 4, pady=(PAD - 4, PAD + 4))
        self.body.grid_columnconfigure(0, weight=1)


class ResponsiveGrid(ctk.CTkFrame):
    """Karten in festen Spalten (Standard 2). KEINE Resize-Events -> kein Hängen.
    Spalten sind gleich gewichtet, aber nicht erzwungen gleich breit."""
    def __init__(self, master, min_col_width=340, max_cols=2, gap=PAD, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.cols, self.gap, self._n = max_cols, gap, 0
        for c in range(max_cols):
            self.grid_columnconfigure(c, weight=1, uniform="col")

    def add(self, widget):
        r, c = divmod(self._n, self.cols)
        half = self.gap // 2
        widget.grid(row=r, column=c, sticky="nsew",
                    padx=(0 if c == 0 else half, 0 if c == self.cols - 1 else half), pady=(0, self.gap))
        self._n += 1
        return widget


class WrapLabel(ctk.CTkLabel):
    """Label mit festem Umbruch (wraplength). Keine Events -> stabil."""
    def __init__(self, master, wraplength=460, **kw):
        kw.setdefault("anchor", "w")
        kw.setdefault("justify", "left")
        super().__init__(master, wraplength=wraplength, **kw)


class InfoText(tk.Text):
    """Wiki-Text, Höhe passt sich an -> nie abgeschnitten.
    Syntax:  # Titel   ## Zwischentitel   - Liste   **fett**   `code`"""
    _INLINE = re.compile(r"(\*\*.+?\*\*|`.+?`)")

    def __init__(self, master, markdown="", font_size=13, **kw):
        super().__init__(master, wrap="word", height=1, width=1, borderwidth=0,
                         highlightthickness=0, relief="flat", cursor="arrow", padx=2, pady=2, **kw)
        s = font_size
        self.configure(bg=_pick(CARD_COLOR), fg=_pick(TEXT_COLOR), font=(FONT, s))
        self.tag_configure("h1", font=(FONT, s + 7, "bold"), foreground=_pick(ACCENT_COLOR), spacing1=6, spacing3=6)
        self.tag_configure("h2", font=(FONT, s + 4, "bold"), foreground=_pick(ACCENT_COLOR), spacing1=10, spacing3=4)
        self.tag_configure("bold", font=(FONT, s, "bold"))
        self.tag_configure("code", font=(MONO, s - 1), background=_pick(CODE_BG))
        self.tag_configure("bullet", lmargin1=10, lmargin2=26, spacing1=2)
        self.tag_configure("p", spacing1=2, spacing3=2)
        self.set_markdown(markdown)
        self._last_w = 0
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        if event.width != self._last_w:          # Höhenänderung ignorieren -> keine Schleife
            self._last_w = event.width
            self.after_idle(self._fit_height)

    def set_markdown(self, md):
        self.configure(state="normal")
        self.delete("1.0", "end")
        lines = [l.strip() for l in md.strip("\n").splitlines()]
        for n, line in enumerate(lines):
            end = "\n" if n < len(lines) - 1 else ""
            if line.startswith("## "):
                self.insert("end", line[3:] + end, "h2")
            elif line.startswith("# "):
                self.insert("end", line[2:] + end, "h1")
            elif line.startswith("- "):
                self.insert("end", "•  ", "bullet"); self._inline(line[2:], "bullet"); self.insert("end", end, "bullet")
            else:
                self._inline(line, "p"); self.insert("end", end, "p")
        self.configure(state="disabled")
        self.after_idle(self._fit_height)

    def _inline(self, text, base):
        for part in self._INLINE.split(text):
            if part.startswith("**") and part.endswith("**"):
                self.insert("end", part[2:-2], (base, "bold"))
            elif part.startswith("`") and part.endswith("`"):
                self.insert("end", part[1:-1], (base, "code"))
            elif part:
                self.insert("end", part, base)

    def _fit_height(self):
        try:
            n = self.count("1.0", "end", "displaylines")
        except tk.TclError:
            return
        n = n[0] if isinstance(n, tuple) else (n or 1)
        if n and int(self.cget("height")) != n:
            self.configure(height=n)


class CodeBlock(ctk.CTkFrame):
    """Code-Ausschnitt mit Kopieren-Button."""
    def __init__(self, master, code, language="Python", **kw):
        super().__init__(master, fg_color=CODE_BG, corner_radius=8, **kw)
        self.code = code.strip("\n")
        self.grid_columnconfigure(0, weight=1)
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 0))
        head.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(head, text=language, text_color=MUTED_COLOR, font=(FONT, 11)).grid(row=0, column=0, sticky="w")
        self._btn = ctk.CTkButton(head, text="Kopieren", width=80, height=24, font=(FONT, 11), command=self._copy)
        self._btn.grid(row=0, column=1, sticky="e")
        txt = tk.Text(self, wrap="none", height=self.code.count("\n") + 1, width=1, borderwidth=0,
                      highlightthickness=0, bg=_pick(CODE_BG), fg=_pick(TEXT_COLOR), font=(MONO, 12), padx=10, pady=8)
        txt.insert("1.0", self.code)
        txt.configure(state="disabled")
        txt.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 4))
        self._bar = ctk.CTkScrollbar(self, orientation="horizontal", command=txt.xview, height=12)
        self._bar_on = False
        txt.configure(xscrollcommand=self._scroll)

    def _scroll(self, a, b):
        self._bar.set(a, b)
        need = not (float(a) <= 0 and float(b) >= 1)
        if need != self._bar_on:
            self._bar.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 4)) if need else self._bar.grid_remove()
            self._bar_on = need

    def _copy(self):
        self.clipboard_clear(); self.clipboard_append(self.code)
        self._btn.configure(text="✔ Kopiert")
        self.after(1200, lambda: self._btn.configure(text="Kopieren"))


class ResponsiveCanvas(tk.Canvas):
    """Zeichenfläche mit FESTER Grösse. Zeichnen relativ zu w/h:
        def zeichnen(c, w, h): c.create_line(0.1*w, 0.5*h, 0.9*w, 0.5*h)
        canvas = ResponsiveCanvas(card.body, zeichnen, width=820, height=380)
    Nach Wertänderung: canvas.redraw()"""
    def __init__(self, master, draw_func, width=600, height=300, **kw):
        super().__init__(master, width=width, height=height, highlightthickness=0,
                         bg=_pick(CARD_COLOR), **kw)
        self.draw_func, self._w, self._h = draw_func, width, height
        self.after_idle(self.redraw)

    def redraw(self):
        if self.winfo_exists():
            self.delete("all")
            self.draw_func(self, self._w, self._h)


def form_row(parent, row, label, placeholder="", entry_width=200, unit_values=None):
    """Label + Entry (+ Einheit). Rückgabe: (entry, unit_menu oder None)"""
    ctk.CTkLabel(parent, text=label, anchor="w", width=90).grid(row=row, column=0, sticky="w", pady=4)
    entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=entry_width)
    entry.grid(row=row, column=1, sticky="w", pady=4)
    unit = None
    if unit_values:
        unit = ctk.CTkOptionMenu(parent, values=unit_values, width=80)
        unit.grid(row=row, column=2, sticky="w", padx=(8, 0), pady=4)
    parent.grid_columnconfigure(3, weight=1)
    return entry, unit


# ---------------------------------------------------------------------------
# Wiki-Bausteine: Tabelle, Hinweisbox, Siehe auch
# ---------------------------------------------------------------------------
HEADER_BG = ("#c9d6e8", "#2b3a52")
ROW_BG = (("gray95", "gray17"), ("gray90", "gray20"))
CALLOUT = {
    "tipp":   (("#dbeafe", "#14243d"), "💡"),
    "fehler": (("#fdecc8", "#3a2d12"), "⚠"),
    "info":   (("#e5e7eb", "#232830"), "ℹ"),
}


class Table(Card):
    """Tabelle in einer Karte. Erste Spalte fett.
        Table(page.body, "Diodentypen", ["Typ", "U_F", "Einsatz"], [["1N4007", "0.7 V", "Netzteil"], ...])
    """
    def __init__(self, master, title, header, rows, note=None, col_wrap=270, **kw):
        super().__init__(master, title=title, **kw)
        t = ctk.CTkFrame(self.body, fg_color="transparent")
        t.grid(row=0, column=0, sticky="ew")
        for c in range(len(header)):
            t.grid_columnconfigure(c, weight=1, uniform="tab")
        for c, h in enumerate(header):
            ctk.CTkLabel(t, text=h, anchor="w", fg_color=HEADER_BG, font=(FONT, 12, "bold"),
                         corner_radius=0, height=30).grid(row=0, column=c, sticky="nsew", padx=(0, 1))
        for r, row in enumerate(rows, start=1):
            for c, zelle in enumerate(row):
                ctk.CTkLabel(t, text=f" {zelle}", anchor="w", justify="left", wraplength=col_wrap,
                             fg_color=ROW_BG[r % 2], corner_radius=0, height=28,
                             font=(MONO, 12, "bold") if c == 0 else (FONT, 12)) \
                    .grid(row=r, column=c, sticky="nsew", padx=(0, 1))
        if note:
            ctk.CTkLabel(self.body, text=note, anchor="w", justify="left", wraplength=800,
                         font=(FONT, 14)).grid(row=1, column=0, sticky="w", pady=(12, 0))


class Callout(ctk.CTkFrame):
    """Farbige Box mit Titel + Aufzählung.  art = "tipp" | "fehler" | "info"
        Callout(page.body, "fehler", "Häufige Fehler", ["LED ohne Vorwiderstand", ...])
    """
    def __init__(self, master, art, title, punkte, **kw):
        farbe, icon = CALLOUT[art]
        super().__init__(master, fg_color=farbe, corner_radius=10, **kw)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=f"{icon}  {title}", anchor="w", font=(FONT, 16, "bold")) \
            .grid(row=0, column=0, sticky="w", padx=PAD + 4, pady=(PAD, 4))
        txt = InfoText(self, "\n".join("- " + p for p in punkte))
        txt.configure(bg=_pick(farbe))
        txt.grid(row=1, column=0, sticky="ew", padx=PAD + 4, pady=(0, PAD + 2))


class SeeAlso(ctk.CTkFrame):
    """Buttons zu verwandten Seiten.
        SeeAlso(page.body, parent, [("Spule", "spule"), ("Diode", "dioden")])
    parent = das an create(parent) übergebene Objekt (kennt das Layout)."""
    def __init__(self, master, parent, links, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        ctk.CTkLabel(self, text="🔗  Siehe auch", anchor="w", font=(FONT, 15, "bold")) \
            .grid(row=0, column=0, columnspan=len(links), sticky="w", pady=(0, 6))
        layout = getattr(parent, "layout", None)
        for c, (text, key) in enumerate(links):
            self.grid_columnconfigure(c, weight=1, uniform="see")
            ctk.CTkButton(self, text=f"💡 {text}", height=30,
                          command=(lambda k=key: layout.goto(k)) if layout else None) \
                .grid(row=1, column=c, sticky="ew", padx=(0 if c == 0 else 6, 0))
