"""
wiki_nav.py  –  Navigation wie im Programmieren-Tab
====================================================
    [⇤] [⌂] [◀]  [ Suchen ...                              ]
    ┌──────────────────┐ ┌──────────────────────────────────┐
    │ ▤ Passive   ▾    │ │ ▤ Passive › Widerstand            │
    │    Widerstand    │ │ Widerstand                        │
    │    Kondensator   │ │ Untertitel                        │
    │ ▤ Halbleiter ▸   │ │ [Karten ...]                      │
    └──────────────────┘ └──────────────────────────────────┘

Wiederverwendbar für jeden Tab (Bauteile, Schaltungen, Formeln ...):

    SECTIONS = [
        ("Passive Bauteile", "resistor.png", [
            ("widerstand", "Widerstand", widerstand.create, "ohm farbcode leistung"),
        ]),
    ]
    WikiNav(parent, SECTIONS, start="widerstand")

Jeder Eintrag: (key, Anzeigename, create-Funktion, Suchbegriffe)
Seiten können mit parent.layout.goto("dioden") springen (für "Siehe auch").
"""
import os
import customtkinter as ctk
from PIL import Image

FONT = "Segoe UI"
ACCENT = ("#3b82f6", "#3b82f6")
HOVER = ("gray80", "gray25")
MUTED = ("gray40", "gray60")
SIDEBAR_BG = ("gray90", "gray12")
IMAGES = os.path.join(os.path.dirname(__file__), "..", "images")


def _icon(name, size=18):
    if not name:
        return None
    pfad = os.path.join(IMAGES, name)
    return ctk.CTkImage(Image.open(pfad), size=(size, size)) if os.path.exists(pfad) else None


class WikiNav(ctk.CTkFrame):
    def __init__(self, master, sections, start=None, sidebar_width=240):
        super().__init__(master, fg_color="transparent")
        self.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sections = sections
        self.sidebar_width = sidebar_width
        self.pages = {}            # key -> (section_name, label, create_func, keywords)
        self.item_buttons = {}     # key -> button
        self.section_open = {}     # section -> bool
        self.history = []
        self.current = None
        self._sidebar_visible = True

        for sec_name, _icon_name, items in sections:
            self.section_open[sec_name] = True
            for key, label, func, kw in items:
                self.pages[key] = (sec_name, label, func, kw)

        self._build_toolbar()
        self._build_sidebar()

        # Inhaltsbereich
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(8, 0))
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.layout = self            # für "Siehe auch"

        first = start or next(iter(self.pages))
        self.goto(first, remember=False)

    # ------------------------------------------------------------------ Toolbar
    def _build_toolbar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 0))
        bar.grid_columnconfigure(3, weight=1)       # nur die Suche wächst

        def tb(col, text, cmd, accent=False):
            b = ctk.CTkButton(bar, text=text, width=40, height=36, command=cmd, font=(FONT, 15),
                              fg_color=ACCENT if accent else ("gray85", "gray20"),
                              hover_color=("#2563eb", "#2563eb") if accent else HOVER,
                              text_color=("gray10", "gray90"))
            b.grid(row=0, column=col, padx=(0, 8))
            return b

        tb(0, "⇤", self.toggle_sidebar, accent=True)
        tb(1, "⌂", lambda: self.goto(next(iter(self.pages))))
        tb(2, "◀", self.back)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._render_sidebar())
        ctk.CTkEntry(bar, textvariable=self.search_var, height=36,
                     placeholder_text="🔍  Suchen ... z.B. Farbcode, Z-Diode, Gleichrichter, Sättigung") \
            .grid(row=0, column=3, sticky="ew")

    # ------------------------------------------------------------------ Sidebar
    def _build_sidebar(self):
        self.sidebar = ctk.CTkScrollableFrame(self, width=self.sidebar_width, fg_color=SIDEBAR_BG,
                                              corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="ns", pady=(8, 0))
        self.sidebar.grid_columnconfigure(0, weight=1)
        self._render_sidebar()

    def _render_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()
        self.item_buttons.clear()
        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        row = 0
        for sec_name, icon_name, items in self.sections:
            if query:
                items = [it for it in items
                         if query in it[1].lower() or query in it[3].lower()]
                if not items:
                    continue
            offen = self.section_open[sec_name] or bool(query)

            head = ctk.CTkButton(self.sidebar, text=f"  {sec_name}   {'▾' if offen else '▸'}",
                                 image=_icon(icon_name), compound="left", anchor="w", height=34,
                                 font=(FONT, 13, "bold"), fg_color="transparent", hover_color=HOVER,
                                 text_color=("gray10", "gray95"),
                                 command=lambda s=sec_name: self._toggle_section(s))
            head.grid(row=row, column=0, sticky="ew", padx=4, pady=(8 if row else 2, 2))
            row += 1
            if not offen:
                continue
            for key, label, _f, _kw in items:
                aktiv = key == self.current
                b = ctk.CTkButton(self.sidebar, text=label, anchor="w", height=28, font=(FONT, 12),
                                  fg_color=ACCENT if aktiv else "transparent",
                                  hover_color=ACCENT if aktiv else HOVER,
                                  text_color=("white", "white") if aktiv else ("gray15", "gray85"),
                                  command=lambda k=key: self.goto(k))
                b.grid(row=row, column=0, sticky="ew", padx=(6, 4), pady=1)
                self.item_buttons[key] = b
                row += 1

    def _toggle_section(self, sec):
        self.section_open[sec] = not self.section_open[sec]
        self._render_sidebar()

    def toggle_sidebar(self):
        if self._sidebar_visible:
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
        self._sidebar_visible = not self._sidebar_visible

    # ------------------------------------------------------------------ Navigation
    def goto(self, key, remember=True):
        if key not in self.pages or key == self.current:
            return
        if remember and self.current:
            self.history.append(self.current)
        self.current = key
        sec, label, func, _kw = self.pages[key]
        self.section_open[sec] = True
        self._render_sidebar()

        for w in self.content.winfo_children():
            w.destroy()
        self.content.breadcrumb = f"{sec}  ›  {label}"
        func(self.content)

    def back(self):
        if self.history:
            self.goto(self.history.pop(), remember=False)
