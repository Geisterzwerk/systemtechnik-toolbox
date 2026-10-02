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


def _bipolar(c, cx, cy, r, farbe, s, h, pnp=False):
    """
    Ein Bipolartransistor mit Kreis, Mitte (cx, cy), Kreisradius r.
      NPN: Kollektor oben, Emitter unten, Pfeil zeigt vom Balken WEG  (nach aussen)
      PNP: Emitter oben, Kollektor unten, Pfeil zeigt zum Balken HIN  (nach innen)
    Merksatz: "NPN - Nicht Pfeil Nach innen"
    """
    balken_x = cx - 0.35 * r                          # senkrechter Basis-Balken
    bein_x = cx + 0.45 * r                            # hier gehen C und E senkrecht weg
    ende = 1.35 * r                                   # Länge der Anschlüsse ab Mitte
    c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=farbe, width=s)
    c.create_line(balken_x, cy - 0.55 * r, balken_x, cy + 0.55 * r, fill=farbe, width=s * 2)
    c.create_line(cx - ende, cy, balken_x, cy, fill=farbe, width=s)                        # Basis
    for richtung in (-1, 1):                                                               # -1 oben, 1 unten
        c.create_line(balken_x, cy + richtung * 0.25 * r, bein_x, cy + richtung * 0.65 * r, fill=farbe, width=s)
        c.create_line(bein_x, cy + richtung * 0.65 * r, bein_x, cy + richtung * ende, fill=farbe, width=s)

    # Pfeil auf dem Emitter-Bein (Punkte entlang der Schräge: 0 = Balken, 1 = Bein)
    richtung = -1 if pnp else 1
    def punkt(t):
        return (balken_x + (bein_x - balken_x) * t, cy + richtung * (0.25 + 0.40 * t) * r)
    von, nach = (punkt(0.85), punkt(0.35)) if pnp else (punkt(0.35), punkt(0.85))
    spitze = max(6, 0.3 * r)
    c.create_line(*von, *nach, fill=farbe, width=s, arrow="last", arrowshape=(spitze, spitze * 1.2, spitze * 0.45))

    schrift = (config.SCHRIFT, max(8, int(h / 12)), "bold")
    c.create_text(cx - ende, cy - 0.12 * h, text="B", fill=farbe, font=schrift, anchor="w")
    oben, unten = ("E", "C") if pnp else ("C", "E")
    c.create_text(bein_x + 0.25 * r, cy - 1.1 * r, text=oben, fill=farbe, font=schrift, anchor="w")
    c.create_text(bein_x + 0.25 * r, cy + 1.1 * r, text=unten, fill=farbe, font=schrift, anchor="w")


def _transistor_radius(w, h, anteil):
    return min(0.24 * h, anteil * w)


def npn(c, w, h, farbe):
    """NPN-Transistor allein."""
    _bipolar(c, 0.5 * w, 0.42 * h, _transistor_radius(w, h, 0.2), farbe, max(2, int(h / 40)), h)
    _beschriftung(c, 0.5 * w, 0.9 * h, "NPN (Pfeil nach aussen)", farbe, h)


def pnp(c, w, h, farbe):
    """PNP-Transistor allein."""
    _bipolar(c, 0.5 * w, 0.42 * h, _transistor_radius(w, h, 0.2), farbe, max(2, int(h / 40)), h, pnp=True)
    _beschriftung(c, 0.5 * w, 0.9 * h, "PNP (Pfeil nach innen)", farbe, h)


def npn_pnp(c, w, h, farbe):
    """NPN (links) und PNP (rechts) nebeneinander - für den Steckbrief der Transistor-Seite."""
    s = max(2, int(h / 40))
    r = _transistor_radius(w, h, 0.1)
    _bipolar(c, 0.25 * w, 0.42 * h, r, farbe, s, h)
    _beschriftung(c, 0.25 * w, 0.9 * h, "NPN (Pfeil nach aussen)", farbe, h)
    _bipolar(c, 0.72 * w, 0.42 * h, r, farbe, s, h, pnp=True)
    _beschriftung(c, 0.72 * w, 0.9 * h, "PNP (Pfeil nach innen)", farbe, h)


def _diode(c, cx, m, a, farbe, s, art="diode"):
    """
    Eine Diode waagrecht, Anode links, Kathode rechts. a = halbe Symbolgrösse.
    art: "diode" | "z" (Z-Diode) | "schottky" | "led"
    """
    links, rechts = cx - a, cx + a                     # Dreieck-Rückseite / Kathoden-Balken
    c.create_line(links - 1.2 * a, m, links, m, fill=farbe, width=s)          # Anschluss Anode
    c.create_line(rechts, m, rechts + 1.2 * a, m, fill=farbe, width=s)        # Anschluss Kathode
    c.create_polygon(links, m - a, links, m + a, rechts, m, outline=farbe, fill="", width=s)
    c.create_line(rechts, m - a, rechts, m + a, fill=farbe, width=s)          # Kathoden-Balken
    haken = 0.4 * a
    if art == "z":            # Z-Diode: Balken mit abgeknickten Enden (wie ein "Z")
        c.create_line(rechts - haken, m - a, rechts, m - a, fill=farbe, width=s)
        c.create_line(rechts, m + a, rechts + haken, m + a, fill=farbe, width=s)
    elif art == "schottky":   # Schottky: Balken mit S-förmigen Enden
        c.create_line(rechts, m - a, rechts + haken, m - a, rechts + haken, m - a + haken, fill=farbe, width=s)
        c.create_line(rechts, m + a, rechts - haken, m + a, rechts - haken, m + a - haken, fill=farbe, width=s)
    elif art == "led":        # LED: zwei Pfeile nach aussen (Licht)
        for dx in (-0.35 * a, 0.35 * a):
            x, y = cx + dx, m - 1.1 * a
            c.create_line(x, y, x + 0.6 * a, y - 0.6 * a, fill=farbe, width=max(1, s - 1),
                          arrow="last", arrowshape=(6, 7, 3))


def dioden(c, w, h, farbe):
    """Diode, Z-Diode, Schottky-Diode und LED nebeneinander (Anode links, Kathode rechts)."""
    s = max(2, int(h / 40))
    a = min(0.14 * h, 0.035 * w)
    m = h * 0.45
    for x, art, text in ((0.13, "diode", "Diode"), (0.38, "z", "Z-Diode"),
                         (0.62, "schottky", "Schottky"), (0.87, "led", "LED")):
        _diode(c, x * w, m, a, farbe, s, art)
        _beschriftung(c, x * w, 0.88 * h, text, farbe, h)
    _beschriftung(c, 0.13 * w - 1.6 * a, m - 1.6 * a, "A", farbe, h)
    _beschriftung(c, 0.13 * w + 1.6 * a, m - 1.6 * a, "K", farbe, h)


def relais(c, w, h, farbe):
    """Links die Spule (A1/A2), gestrichelt die Wirkverbindung, rechts ein Wechsler (11/12/14) in Ruhelage."""
    s = max(2, int(h / 40))
    m = h * 0.42
    schrift = (config.SCHRIFT, max(8, int(h / 12)))
    # --- Spule: Rechteck (EN 60617) ---
    x0, x1 = 0.16 * w, 0.30 * w
    xm = (x0 + x1) / 2
    c.create_rectangle(x0, m - 0.18 * h, x1, m + 0.18 * h, outline=farbe, width=s)
    c.create_line(xm, 0.05 * h, xm, m - 0.18 * h, fill=farbe, width=s)
    c.create_line(xm, m + 0.18 * h, xm, 0.78 * h, fill=farbe, width=s)
    c.create_text(xm - 0.02 * w, 0.1 * h, text="A1", fill=farbe, font=schrift, anchor="e")
    c.create_text(xm - 0.02 * w, 0.74 * h, text="A2", fill=farbe, font=schrift, anchor="e")
    _beschriftung(c, xm, 0.92 * h, "Spule", farbe, h)
    # --- Wechsler: COM (11) unten, Öffner (12) links oben, Schliesser (14) rechts oben ---
    xc = 0.66 * w
    dx = 0.06 * w
    oben = m - 0.16 * h
    c.create_line(xc, 0.78 * h, xc, m + 0.2 * h, fill=farbe, width=s)                          # 11 (COM)
    c.create_line(xc - dx, 0.05 * h, xc - dx, oben, xc - dx * 0.35, oben, fill=farbe, width=s)   # 12 (Öffner)
    c.create_line(xc + dx, 0.05 * h, xc + dx, oben, xc + dx * 0.35, oben, fill=farbe, width=s)   # 14 (Schliesser)
    c.create_line(xc, m + 0.2 * h, xc - dx * 0.55, oben - 0.02 * h, fill=farbe, width=s)        # Kontaktzunge in Ruhe
    c.create_line(x1, m, xc - dx * 0.25, m, fill=farbe, width=max(1, s - 1), dash=(6, 4))        # Wirkverbindung
    c.create_text(xc + 0.015 * w, 0.74 * h, text="11", fill=farbe, font=schrift, anchor="w")
    c.create_text(xc - dx - 0.015 * w, 0.1 * h, text="12", fill=farbe, font=schrift, anchor="e")
    c.create_text(xc + dx + 0.015 * w, 0.1 * h, text="14", fill=farbe, font=schrift, anchor="w")
    _beschriftung(c, xc, 0.92 * h, "Wechsler (in Ruhelage)", farbe, h)


SYMBOLE = {
    "widerstand": widerstand,
    "kondensator": kondensator,
    "spule": spule,
    "transformator": transformator,
    "npn": npn,
    "pnp": pnp,
    "npn_pnp": npn_pnp,
    "dioden": dioden,
    "relais": relais,
}
