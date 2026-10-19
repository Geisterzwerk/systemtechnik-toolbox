# =============================================================================
# bauteile/grafiken/widerstand_bild.py
# -----------------------------------------------------------------------------
# WIDERSTAND MIT FARBRINGEN zeichnen - auf irgendein Canvas (tk.Canvas im Fenster, SvgCanvas im Web).
# KEIN tkinter in dieser Datei.
#
#   widerstand_zeichnen(c, w, h, ["Gelb", "Violett", "Rot", "Gold"])
#   None in der Liste = Ring noch nicht gewählt (gestrichelt)
#
# WER RUFT DAS AUF?  bauteile/grafiken/farbcode_karten.py (Fenster), web/rechner/ (Webversion)
# =============================================================================

import config                                                       # -> config.py
from bauteile.rechner.widerstand_rechner import FARB_HEX            # -> rechner/widerstand_rechner.py


def widerstand_zeichnen(c, w, h, farben):
    """Zeichnet einen Widerstand mit Farbringen. farben = Liste (None = noch nicht gewählt)."""
    mitte = h / 2
    c.create_line(0.03 * w, mitte, 0.97 * w, mitte, fill="#9AA1AD", width=max(2, h / 40))      # Anschlussdrähte
    x1, x2, y1, y2 = 0.2 * w, 0.8 * w, 0.22 * h, 0.78 * h
    koerper = "#E8D3A8"                                                                       # typische Farbe (beige)
    c.create_oval(x1 - 0.03 * w, y1 - 0.04 * h, x1 + 0.07 * w, y2 + 0.04 * h, fill=koerper, outline="")
    c.create_oval(x2 - 0.07 * w, y1 - 0.04 * h, x2 + 0.03 * w, y2 + 0.04 * h, fill=koerper, outline="")
    c.create_rectangle(x1 + 0.02 * w, y1, x2 - 0.02 * w, y2, fill=koerper, outline="")

    n = len(farben)
    breite = 0.035 * w
    # Ziffern + Multiplikator links gruppiert, Toleranz (und TK) rechts mit Abstand
    links = n - (2 if n == 6 else 1)
    positionen = [0.27 * w + i * 0.085 * w for i in range(links)]
    positionen += [0.70 * w] if n != 6 else [0.66 * w, 0.73 * w]
    for x, farbe in zip(positionen, farben):
        if farbe:
            c.create_rectangle(x - breite / 2, y1 - 0.02 * h, x + breite / 2, y2 + 0.02 * h,
                               fill=FARB_HEX[farbe], outline="#555555" if farbe in ("Weiss", "Gelb", "Silber") else "")
        else:
            c.create_rectangle(x - breite / 2, y1, x + breite / 2, y2, outline="#777777", dash=(3, 3))
    c.create_text(0.5 * w, 0.93 * h, text="Lesen von links nach rechts →   (Toleranzring rechts)",
                  fill="#9AA1AD", font=(config.SCHRIFT, max(8, int(h / 14))))
