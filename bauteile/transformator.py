# =============================================================================
# bauteile/transformator.py
# -----------------------------------------------------------------------------
# Seite TRANSFORMATOR: Animation (skaliert mit!) + Rechner + Erklärung.
# WER RUFT DAS AUF?  gui/bauteile_gui.py -> bereich.eintrag_hinzufuegen("Transformator", ...)
#
# RESPONSIVE: Die Zeichnung benutzt RELATIVE Koordinaten (z.B. 0.25 * breite)
#             -> passt bei jeder Fenstergrösse (core/layout.py ResponsiveCanvas).
# ANIMATION:  Elemente werden über TAGS bewegt ("strom", "magnet", "spannung"),
#             damit sie auch nach dem Neuzeichnen (Fenstergrösse) weiterlaufen.
#             Stoppt automatisch, wenn man die Seite verlässt.
# =============================================================================

import math

import customtkinter as ctk

import config                                                            # -> config.py
from core.layout import Karte, ResponsiveCanvas, Stapel, WrapLabel, seiten_kopf   # -> core/layout.py
from core.widgets import FormatText                                      # -> core/widgets.py

INFOTEXT = """
## Was zeigt die Animation?
- **Primärspule (links):** Wechselstrom erzeugt ein sich änderndes Magnetfeld
- **Eisenkern (Mitte):** leitet das Magnetfeld zur Sekundärspule
- **Sekundärspule (rechts):** das sich ändernde Magnetfeld induziert eine Spannung
## Formeln (idealer Trafo)
- `U1 / U2 = N1 / N2`   (Spannung verhält sich wie die Windungszahl)
- `I1 / I2 = N2 / N1`   (Strom verhält sich umgekehrt)
- Funktioniert NUR mit Wechselspannung (Gleichspannung -> kein sich änderndes Feld)
## Aufgaben
- Spannung hoch- oder heruntersetzen
- Galvanische Trennung (Sicherheit)
"""


def _zeichnen(c, w, h):
    """Zeichnet den Trafo in relativen Koordinaten (w = Breite, h = Höhe in Pixel)."""
    schrift = (config.SCHRIFT, max(8, int(h / 26)))
    # Eisenkern
    c.create_rectangle(0.24 * w, 0.38 * h, 0.76 * w, 0.62 * h, fill="#7A7F87", outline="")
    c.create_text(0.5 * w, 0.30 * h, text="Eisenkern (Magnetfeld Φ)", fill="#9AA1AD", font=schrift)
    # Spulen (je 10 Windungen)
    for k in range(10):
        x1 = 0.16 * w + k * 0.012 * w
        c.create_oval(x1, 0.25 * h, x1 + 0.018 * w, 0.75 * h, outline="#22C55E", width=2)
        x2 = 0.70 * w + k * 0.012 * w
        c.create_oval(x2, 0.25 * h, x2 + 0.018 * w, 0.75 * h, outline="#F59E0B", width=2)
    c.create_text(0.22 * w, 0.86 * h, text="Primärspule N1", fill="#22C55E", font=schrift)
    c.create_text(0.78 * w, 0.86 * h, text="Sekundärspule N2", fill="#F59E0B", font=schrift)
    # Linien für die Animation (über TAGS ansprechbar)
    for k in range(5):
        y = 0.40 * h + k * 0.05 * h
        c.create_line(0.03 * w, y, 0.14 * w, y, fill="#EF4444", width=2, tags="strom")
        c.create_line(0.26 * w, y, 0.74 * w, y, fill="#3B82F6", dash=(6, 4), width=2, tags="magnet")
        c.create_line(0.86 * w, y, 0.97 * w, y, fill="#A855F7", width=2, tags="spannung")


def create(parent):
    s = Stapel(parent)
    seiten_kopf(s, "Transformator", "Animation, Rechner und Grundlagen")

    # =========================================================================
    # ANIMATION
    # =========================================================================
    anim = s.add(Karte(parent))
    canvas = ResponsiveCanvas(anim.body, _zeichnen, seitenverhaeltnis=0.4)   # -> core/layout.py
    canvas.grid(row=0, column=0, sticky="ew")

    schritt = [0]
    hintergrund = config.FARBEN["flaeche"][1 if ctk.get_appearance_mode() == "Dark" else 0]

    def animieren():
        if not canvas.winfo_exists():
            return                                   # Seite verlassen -> Animation stoppt
        schritt[0] += 1
        canvas.move("strom", 0, math.sin(schritt[0] * 0.3) * 1.5)       # Wechselstrom
        canvas.itemconfigure("magnet", dashoffset=schritt[0] * 2)
        canvas.itemconfigure("spannung", fill="#A855F7" if schritt[0] % 4 < 2 else hintergrund)
        canvas.after(100, animieren)

    animieren()

    # =========================================================================
    # RECHNER
    # =========================================================================
    rechner = s.add(Karte(parent, titel="Rechner: U2 = U1 · N2 / N1"))
    rechner.body.grid_columnconfigure(0, weight=0)
    rechner.body.grid_columnconfigure(2, weight=1)
    felder = {}
    for zeile, (name, hinweis) in enumerate((("U1", "Primärspannung (V)"), ("N1", "Windungen primär"),
                                             ("N2", "Windungen sekundär"))):
        ctk.CTkLabel(rechner.body, text=name, width=40, anchor="w").grid(row=zeile, column=0, sticky="w", pady=4)
        felder[name] = ctk.CTkEntry(rechner.body, placeholder_text=hinweis, width=200)
        felder[name].grid(row=zeile, column=1, sticky="w", pady=4)
    ergebnis = WrapLabel(rechner.body, text="", font=config.FONT_SEKTION, text_color=config.FARBEN["akzent"])

    def berechnen():
        try:
            u1, n1, n2 = (float(felder[k].get().replace(",", ".")) for k in ("U1", "N1", "N2"))
            ergebnis.configure(text=f"U2 = {u1 * n2 / n1:.4g} V    (ü = N1/N2 = {n1 / n2:.4g})")
        except ValueError:
            ergebnis.configure(text="Bitte alle drei Werte eingeben")
        except ZeroDivisionError:
            ergebnis.configure(text="Windungszahl darf nicht 0 sein")

    ctk.CTkButton(rechner.body, text="Berechnen", command=berechnen).grid(
        row=3, column=0, columnspan=2, sticky="w", pady=(10, 4))
    ergebnis.grid(row=4, column=0, columnspan=3, sticky="ew")

    # =========================================================================
    # INFOTEXT
    # =========================================================================
    info = s.add(Karte(parent))
    text = FormatText(info.body)
    text.setze_text(INFOTEXT)
    text.grid(row=0, column=0, sticky="ew")
