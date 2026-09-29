# =============================================================================
# bauteile/kondensator.py
# -----------------------------------------------------------------------------
# Seite KONDENSATOR: RC-Rechner (τ, 5τ, Energie, Spannung zum Zeitpunkt t) + Infotext.
# WER RUFT DAS AUF?  gui/bauteile_gui.py -> bereich.eintrag_hinzufuegen("Kondensator", ...)
# =============================================================================

import math

import customtkinter as ctk

import config                                                            # -> config.py
from core.layout import Karte, ResponsiveGrid, Stapel, WrapLabel, seiten_kopf   # -> core/layout.py
from core.widgets import FormatText                                      # -> core/widgets.py

INFOTEXT = """
## Kondensator – Grundlagen
Ein Kondensator speichert elektrische Energie im elektrischen Feld zwischen zwei Platten.
- **Kapazität:** `C = Q / U`  in Farad (F)
- **Zeitkonstante:** `τ = R · C`
- **Laden:** `u(t) = U0 · (1 − e^(−t/τ))`
- **Entladen:** `u(t) = U0 · e^(−t/τ)`
- Nach **1τ** ≈ 63 % geladen, nach **5τ** ≈ 99.3 % → gilt als voll
- **Energie:** `W = ½ · C · U²`
"""

EINHEITEN_C = {"pF": 1e-12, "nF": 1e-9, "µF": 1e-6, "mF": 1e-3, "F": 1}


def _zahl(entry):
    text = entry.get().strip().replace(",", ".")
    return float(text) if text else None


def _zeit_text(sekunden):
    """0.0047 -> '4.7 ms'"""
    for faktor, zeichen in ((1, "s"), (1e-3, "ms"), (1e-6, "µs"), (1e-9, "ns")):
        if sekunden >= faktor:
            return f"{sekunden / faktor:.4g} {zeichen}"
    return f"{sekunden:.3g} s"


def create(parent):
    s = Stapel(parent)
    seiten_kopf(s, "Kondensator", "RC-Glied: Laden, Entladen und Energie")

    grid = s.add(ResponsiveGrid(parent, min_spaltenbreite=360, max_spalten=2))

    # =========================================================================
    # EINGABE
    # =========================================================================
    ein = grid.add(Karte(grid, titel="RC-Glied", untertitel="R und C sind Pflicht, U0 und t optional"))
    ein.body.grid_columnconfigure(0, weight=0)
    ein.body.grid_columnconfigure(3, weight=1)          # Rest der Zeile = Füllplatz

    def feld(zeile, text, platzhalter):
        ctk.CTkLabel(ein.body, text=text, anchor="w", width=70).grid(row=zeile, column=0, sticky="w", pady=4)
        eingabe = ctk.CTkEntry(ein.body, placeholder_text=platzhalter, width=160)
        eingabe.grid(row=zeile, column=1, sticky="w", pady=4)
        return eingabe

    feld_r = feld(0, "R (Ω)", "z.B. 10000")
    feld_c = feld(1, "C", "z.B. 100")
    einheit_c = ctk.CTkOptionMenu(ein.body, values=list(EINHEITEN_C.keys()), width=80)
    einheit_c.set("µF")
    einheit_c.grid(row=1, column=2, sticky="w", padx=(8, 0), pady=4)
    feld_u = feld(2, "U0 (V)", "z.B. 5")
    feld_t = feld(3, "Zeit t (s)", "optional")

    # =========================================================================
    # ERGEBNIS
    # =========================================================================
    aus = grid.add(Karte(grid, titel="Ergebnis"))
    ergebnis = WrapLabel(aus.body, text="Werte eingeben und berechnen.", font=config.FONT_TEXT,
                         text_color=config.FARBEN["text_leise"])
    ergebnis.grid(row=0, column=0, sticky="ew")

    def berechnen():
        try:
            r, c, u0, t = _zahl(feld_r), _zahl(feld_c), _zahl(feld_u), _zahl(feld_t)
            if r is None or c is None:
                ergebnis.configure(text="Bitte R und C eingeben")
                return
            c = c * EINHEITEN_C[einheit_c.get()]          # z.B. 100 µF -> 0.0001 F
            tau = r * c
            zeilen = [f"τ = R · C = {_zeit_text(tau)}", f"5τ (≈ voll) = {_zeit_text(5 * tau)}"]
            if u0 is not None:
                zeilen.append(f"Energie W = ½·C·U² = {0.5 * c * u0 ** 2:.4g} J")
                if t is not None:
                    laden = u0 * (1 - math.exp(-t / tau))
                    zeilen.append(f"Laden:    u({t:g} s) = {laden:.4g} V  ({laden / u0 * 100:.1f} %)")
                    zeilen.append(f"Entladen: u({t:g} s) = {u0 * math.exp(-t / tau):.4g} V")
            ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])
        except ValueError:
            ergebnis.configure(text="Ungültige Eingabe")
        except ZeroDivisionError:
            ergebnis.configure(text="R oder C darf nicht 0 sein")

    ctk.CTkButton(ein.body, text="Berechnen", command=berechnen).grid(
        row=4, column=0, columnspan=3, sticky="w", pady=(10, 0))

    # =========================================================================
    # INFOTEXT
    # =========================================================================
    info = s.add(Karte(parent))
    text = FormatText(info.body)
    text.setze_text(INFOTEXT)
    text.grid(row=0, column=0, sticky="ew")
