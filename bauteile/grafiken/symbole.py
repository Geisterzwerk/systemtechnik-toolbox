# =============================================================================
# bauteile/grafiken/symbole.py
# -----------------------------------------------------------------------------
# SCHALTZEICHEN, direkt auf dem Canvas gezeichnet (passen sich an Grösse und
# Dark/Light Mode an - anders als PNG-Bilder).
#
# Jede Funktion:  zeichnen(canvas, breite, hoehe, farbe)
# Registrierung:  SYMBOLE = {"widerstand": ..., ...}
# Benutzt von:    bauteile/engine/seite.py (Steckbrief oben auf der Seite)
#
# NEUES SYMBOL? Funktion schreiben und unten in SYMBOLE eintragen.
# =============================================================================

import config    # -> config.py


def _beschriftung(c, x, y, text, farbe, h):
    c.create_text(x, y, text=text, fill=farbe, font=(config.SCHRIFT, max(8, int(h / 11))))


def widerstand(c, w, h, farbe):
    """Links IEC/EN (Europa: Rechteck), rechts ANSI (USA: Zickzack)."""
    s = max(2, int(h / 40))
    m = h * 0.45
    # --- IEC: Rechteck ---
    x0, x1 = 0.05 * w, 0.45 * w
    c.create_line(x0, m, 0.13 * w, m, fill=farbe, width=s)
    c.create_rectangle(0.13 * w, m - 0.12 * h, 0.37 * w, m + 0.12 * h, outline=farbe, width=s)
    c.create_line(0.37 * w, m, x1, m, fill=farbe, width=s)
    _beschriftung(c, 0.25 * w, 0.85 * h, "IEC / EN (Europa)", farbe, h)
    # --- ANSI: Zickzack ---
    punkte = [0.55 * w, m, 0.62 * w, m]
    for i in range(6):
        x = 0.62 * w + (i + 0.5) * 0.043 * w
        punkte += [x, m + (-0.14 if i % 2 == 0 else 0.14) * h]
    punkte += [0.88 * w, m, 0.95 * w, m]
    c.create_line(*punkte, fill=farbe, width=s)
    _beschriftung(c, 0.75 * w, 0.85 * h, "ANSI (USA, Datenblätter)", farbe, h)


def kondensator(c, w, h, farbe):
    """Links ungepolt (Keramik/Folie), rechts gepolt (Elko) mit Plus-Zeichen."""
    s = max(2, int(h / 40))
    m = h * 0.42
    platte = 0.22 * h
    # --- ungepolt: zwei gleiche Platten ---
    c.create_line(0.05 * w, m, 0.22 * w, m, fill=farbe, width=s)
    c.create_line(0.22 * w, m - platte, 0.22 * w, m + platte, fill=farbe, width=s * 2)
    c.create_line(0.28 * w, m - platte, 0.28 * w, m + platte, fill=farbe, width=s * 2)
    c.create_line(0.28 * w, m, 0.45 * w, m, fill=farbe, width=s)
    _beschriftung(c, 0.25 * w, 0.85 * h, "ungepolt (Keramik, Folie)", farbe, h)
    # --- gepolt (Elko): eine Platte gefüllt / als Rechteck, + an der Anode ---
    c.create_line(0.55 * w, m, 0.72 * w, m, fill=farbe, width=s)
    c.create_rectangle(0.72 * w - s, m - platte, 0.72 * w + s, m + platte, outline=farbe, width=s)
    c.create_rectangle(0.78 * w - s, m - platte, 0.78 * w + s, m + platte, fill=farbe, outline=farbe)
    c.create_line(0.78 * w, m, 0.95 * w, m, fill=farbe, width=s)
    c.create_text(0.69 * w, m - platte - 0.02 * h, text="+", fill=farbe, font=(config.SCHRIFT, max(10, int(h / 7)), "bold"))
    _beschriftung(c, 0.75 * w, 0.85 * h, "gepolt (Elko): + beachten!", farbe, h)


def spule(c, w, h, farbe):
    """Links nach EN 60617 (Bögen), rechts mit Eisenkern, ganz rechts alte DIN-Form."""
    s = max(2, int(h / 40))
    m = h * 0.48
    r = min(0.03 * w, 0.12 * h)
    # --- Bögen ---
    def boegen(x_start, anzahl=4):
        c.create_line(x_start - 0.05 * w, m, x_start, m, fill=farbe, width=s)
        for i in range(anzahl):
            x = x_start + i * 2 * r
            c.create_arc(x, m - r, x + 2 * r, m + r, start=0, extent=180, style="arc", outline=farbe, width=s)
        ende = x_start + anzahl * 2 * r
        c.create_line(ende, m, ende + 0.05 * w, m, fill=farbe, width=s)
        return ende
    boegen(0.06 * w)
    _beschriftung(c, 0.06 * w + 4 * r, 0.85 * h, "Spule (EN 60617)", farbe, h)
    ende = boegen(0.40 * w)
    c.create_line(0.40 * w, m - r - 0.08 * h, ende, m - r - 0.08 * h, fill=farbe, width=s)   # Kern-Strich
    _beschriftung(c, 0.40 * w + 4 * r, 0.85 * h, "mit Eisen-/Ferritkern", farbe, h)
    # --- alte DIN-Form: gefülltes Rechteck ---
    c.create_line(0.74 * w, m, 0.79 * w, m, fill=farbe, width=s)
    c.create_rectangle(0.79 * w, m - 0.08 * h, 0.91 * w, m + 0.08 * h, fill=farbe, outline=farbe)
    c.create_line(0.91 * w, m, 0.96 * w, m, fill=farbe, width=s)
    _beschriftung(c, 0.85 * w, 0.85 * h, "alt (DIN)", farbe, h)


def transformator(c, w, h, farbe):
    """Zwei Wicklungen mit Kern (Doppelstrich) und Wicklungssinn-Punkten."""
    s = max(2, int(h / 40))
    r = min(0.1 * h, 0.03 * w)
    x_l, x_r = 0.40 * w, 0.60 * w
    oben = 0.10 * h
    for x, seite in ((x_l, -1), (x_r, 1)):
        for i in range(4):
            y = oben + i * 2 * r
            start = 270 if seite == -1 else 90
            c.create_arc(x - r, y, x + r, y + 2 * r, start=start, extent=180, style="arc", outline=farbe, width=s)
        unten = oben + 8 * r
        c.create_line(x, oben, x + seite * 0.12 * w, oben, fill=farbe, width=s)
        c.create_line(x, unten, x + seite * 0.12 * w, unten, fill=farbe, width=s)
        c.create_oval(x + seite * 0.035 * w - 3, oben + 0.01 * h, x + seite * 0.035 * w + 3,
                      oben + 0.01 * h + 6, fill=farbe, outline="")                          # Wicklungssinn
    unten = oben + 8 * r
    for dx in (-0.012 * w, 0.012 * w):
        c.create_line(0.5 * w + dx, oben, 0.5 * w + dx, unten, fill=farbe, width=s)          # Kern
    _beschriftung(c, x_l - 0.12 * w, 0.88 * h, "primär N1", farbe, h)
    _beschriftung(c, x_r + 0.12 * w, 0.88 * h, "sekundär N2", farbe, h)
    _beschriftung(c, 0.5 * w, 0.88 * h, "Kern", farbe, h)


SYMBOLE = {
    "widerstand": widerstand,
    "kondensator": kondensator,
    "spule": spule,
    "transformator": transformator,
}
