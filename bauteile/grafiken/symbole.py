# =============================================================================
# bauteile/grafiken/symbole.py
# -----------------------------------------------------------------------------
# SCHALTZEICHEN, direkt auf dem Canvas gezeichnet (passen sich an Grösse und
# Dark/Light Mode an - anders als PNG-Bilder).
#
# AUFBAU: Ein Eintrag in SYMBOLE ist eine LISTE von Varianten. Jede Variante
# zeichnet genau EIN Symbol in eine eigene Zelle. Die Beschriftung ist KEIN
# Canvas-Text, sondern ein echtes Label UNTER der Zelle (bricht um, kann das
# Symbol nie überlagern) -> bauteile/grafiken/symbol_reihe.py
#
#   ┌──────────┐ ┌──────────┐ ┌──────────┐
#   │  ─[▭]─   │ │  ─╱╲╱─   │ │   …      │   <- je eine Zelle, gleiche Grösse
#   └──────────┘ └──────────┘ └──────────┘
#    IEC / EN     ANSI (USA)                 <- Beschriftung darunter
#
# REGELN für alle Zeichenfunktionen  zeichnen(c, w, h, farbe):
#   - Grundeinheit u = _einheit(w, h); alle Masse sind Vielfache von u
#     -> alle Symbole gleich gross, Mittellinie immer bei h/2
#   - Anschlüsse links und rechts gleich lang (bis ±ANSCHLUSS · u)
#   - Anschluss-Bezeichnungen (A, K, B, C, E ...) nur an den ENDEN der
#     Anschlussleitungen - nie im Symbol
#
# Benutzt von:  bauteile/engine/seite.py (Steckbrief oben auf der Seite)
# NEUES SYMBOL? Zeichenfunktion schreiben und unten in SYMBOLE eintragen.
# =============================================================================

from collections import namedtuple

import config    # -> config.py

# Eine Variante: Zeichenfunktion, Beschriftung darunter, Form der Zelle
#   seitenverhaeltnis  Höhe = Breite · seitenverhaeltnis
#   min_breite         schmaler wird die Zelle nicht (sonst rutscht sie in die nächste Zeile)
Variante = namedtuple("Variante", "zeichnen text seitenverhaeltnis min_breite", defaults=(0.6, 150))

ANSCHLUSS = 4.2          # Anschlussleitungen reichen bis ±4.2 u von der Mitte


def _einheit(w, h):
    """Grundeinheit: Symbole sind ca. 10 u breit und 6 u hoch."""
    return min(w / 10.4, h / 6.2)


def _strich(u):
    return max(2, round(u / 5))


def _pin(c, x, y, text, farbe, u, anker="center"):
    """Anschluss-Bezeichnung (A, K, B, C ...) - klein und fett."""
    c.create_text(x, y, text=text, fill=farbe, anchor=anker,
                  font=(config.SCHRIFT, max(8, round(u * 0.6)), "bold"))


def _anschluesse(c, cx, my, links, rechts, farbe, s, u):
    """Gleich lange Leitungen links und rechts bis ±ANSCHLUSS · u."""
    c.create_line(cx - ANSCHLUSS * u, my, links, my, fill=farbe, width=s)
    c.create_line(rechts, my, cx + ANSCHLUSS * u, my, fill=farbe, width=s)


# =============================================================================
# WIDERSTAND
# =============================================================================
def widerstand_iec(c, w, h, farbe):
    u, cx, my = _einheit(w, h), w / 2, h / 2
    s = _strich(u)
    _anschluesse(c, cx, my, cx - 1.8 * u, cx + 1.8 * u, farbe, s, u)
    c.create_rectangle(cx - 1.8 * u, my - 0.65 * u, cx + 1.8 * u, my + 0.65 * u, outline=farbe, width=s)


def widerstand_ansi(c, w, h, farbe):
    u, cx, my = _einheit(w, h), w / 2, h / 2
    s = _strich(u)
    _anschluesse(c, cx, my, cx - 1.8 * u, cx + 1.8 * u, farbe, s, u)
    punkte = [cx - 1.8 * u, my]
    for i in range(6):
        punkte += [cx - 1.8 * u + (i + 0.5) * 0.6 * u, my + (-0.7 if i % 2 == 0 else 0.7) * u]
    punkte += [cx + 1.8 * u, my]
    c.create_line(*punkte, fill=farbe, width=s)


# =============================================================================
# KONDENSATOR
# =============================================================================
def kondensator_ungepolt(c, w, h, farbe):
    u, cx, my = _einheit(w, h), w / 2, h / 2
    s = _strich(u)
    _anschluesse(c, cx, my, cx - 0.4 * u, cx + 0.4 * u, farbe, s, u)
    for x in (cx - 0.4 * u, cx + 0.4 * u):                              # zwei gleiche Platten
        c.create_line(x, my - 1.3 * u, x, my + 1.3 * u, fill=farbe, width=s * 2)


def kondensator_gepolt(c, w, h, farbe):
    """Elko nach EN 60617: Plus-Platte offen (Rechteck), Minus-Platte gefüllt, + daneben."""
    u, cx, my = _einheit(w, h), w / 2, h / 2
    s = _strich(u)
    d = 0.35 * u                                                         # Plattendicke
    _anschluesse(c, cx, my, cx - 0.45 * u - d, cx + 0.45 * u + d, farbe, s, u)
    c.create_rectangle(cx - 0.45 * u - d, my - 1.3 * u, cx - 0.45 * u, my + 1.3 * u,
                       outline=farbe, width=s)                           # + Platte (offen)
    c.create_rectangle(cx + 0.45 * u, my - 1.3 * u, cx + 0.45 * u + d, my + 1.3 * u,
                       outline=farbe, fill=farbe, width=s)               # − Platte (gefüllt)
    # Pluszeichen oberhalb links der Plus-Platte - berührt weder Platte noch Leitung
    c.create_text(cx - 1.55 * u, my - 1.05 * u, text="+", fill=farbe,
                  font=(config.SCHRIFT, max(10, round(u * 1.0)), "bold"))


# =============================================================================
# SPULE
# =============================================================================
def _boegen(c, cx, my, farbe, s, u, r):
    """4 Halbkreise (Wicklung) von cx−4r bis cx+4r."""
    for i in range(4):
        x = cx - 4 * r + i * 2 * r
        c.create_arc(x, my - r, x + 2 * r, my + r, start=0, extent=180, style="arc", outline=farbe, width=s)


def spule_en(c, w, h, farbe):
    u, cx, my = _einheit(w, h), w / 2, h / 2
    s, r = _strich(u), 0.55 * u
    _anschluesse(c, cx, my, cx - 4 * r, cx + 4 * r, farbe, s, u)
    _boegen(c, cx, my, farbe, s, u, r)


def spule_kern(c, w, h, farbe):
    """Mit Eisen-/Ferritkern: Strich parallel zur Wicklung, mit deutlichem Abstand."""
    u, cx, my = _einheit(w, h), w / 2, h / 2
    s, r = _strich(u), 0.55 * u
    _anschluesse(c, cx, my, cx - 4 * r, cx + 4 * r, farbe, s, u)
    _boegen(c, cx, my, farbe, s, u, r)
    y = my - r - 0.55 * u
    c.create_line(cx - 4 * r, y, cx + 4 * r, y, fill=farbe, width=s * 2)


def spule_din(c, w, h, farbe):
    """Alte DIN-Darstellung: gefülltes Rechteck (historisch, in alten Plänen)."""
    u, cx, my = _einheit(w, h), w / 2, h / 2
    s = _strich(u)
    _anschluesse(c, cx, my, cx - 1.8 * u, cx + 1.8 * u, farbe, s, u)
    c.create_rectangle(cx - 1.8 * u, my - 0.5 * u, cx + 1.8 * u, my + 0.5 * u, outline=farbe, fill=farbe, width=s)


# =============================================================================
# TRANSFORMATOR (eine breitere Zelle mit Bezugslinien)
# =============================================================================
def transformator(c, w, h, farbe):
    """
    Zwei Wicklungen (senkrecht), Eisenkern als Doppelstrich, Wicklungsanfang als Punkt.
    Beschriftungen OBEN links/rechts und UNTEN in der Mitte, je mit kurzer Bezugslinie.
    """
    u = min(w / 13, h / 8.4)
    cx, my = w / 2, h * 0.5
    s, r = _strich(u), 0.5 * u
    hoehe = 8 * r                                                        # 4 Bögen übereinander
    oben, unten = my - hoehe / 2, my + hoehe / 2
    xl, xr = cx - 1.2 * u, cx + 1.2 * u                                  # Wicklungsachsen
    for x, seite in ((xl, -1), (xr, 1)):
        for i in range(4):
            y = oben + i * 2 * r
            c.create_arc(x - r, y, x + r, y + 2 * r, start=270 if seite == -1 else 90, extent=180,
                         style="arc", outline=farbe, width=s)
        aussen = x + seite * 2.6 * u
        c.create_line(x, oben, aussen, oben, fill=farbe, width=s)        # Anschlüsse waagrecht nach aussen
        c.create_line(x, unten, aussen, unten, fill=farbe, width=s)
        punkt = x + seite * 0.9 * u                                      # Wicklungsanfang (Punkt)
        c.create_oval(punkt - 0.22 * u, oben + 0.3 * u, punkt + 0.22 * u, oben + 0.74 * u, fill=farbe, outline="")
    for dx in (-0.22 * u, 0.22 * u):
        c.create_line(cx + dx, oben - 0.2 * u, cx + dx, unten + 0.2 * u, fill=farbe, width=s)   # Kern

    leise = farbe
    schrift = (config.SCHRIFT, max(8, round(u * 0.4)))
    # Beschriftung aussen neben der jeweiligen Wicklung, Bezugslinie schräg zur Wicklung
    y_text = oben - 1.1 * u
    c.create_text(xl - 1.5 * u, y_text, text="Primär N1", fill=leise, font=schrift, anchor="e")
    c.create_line(xl - 1.45 * u, y_text + 0.3 * u, xl - 0.45 * u, oben + 0.3 * u, fill=leise, width=1)
    c.create_text(xr + 1.5 * u, y_text, text="Sekundär N2", fill=leise, font=schrift, anchor="w")
    c.create_line(xr + 1.45 * u, y_text + 0.3 * u, xr + 0.45 * u, oben + 0.3 * u, fill=leise, width=1)
    y_kern = unten + 1.35 * u
    c.create_text(cx, y_kern, text="Kern", fill=leise, font=schrift)
    c.create_line(cx, y_kern - 0.45 * u, cx, unten + 0.3 * u, fill=leise, width=1)


# =============================================================================
# DIODEN & LED
# =============================================================================
def _diodenkoerper(c, cx, my, g, farbe, s, strich="normal"):
    """Dreieck (Anode links) + Kathodenstrich rechts. Gibt (x Anode, x Kathode) zurück."""
    a, k = cx - g * 0.8, cx + g * 0.8
    c.create_polygon(a, my - g, a, my + g, k, my, outline=farbe, fill="", width=s)
    c.create_line(k, my - g, k, my + g, fill=farbe, width=s)
    if strich == "z":                                   # Z-Diode: abgeknickte Enden
        c.create_line(k, my - g, k - g * 0.4, my - g * 1.2, fill=farbe, width=s)
        c.create_line(k, my + g, k + g * 0.4, my + g * 1.2, fill=farbe, width=s)
    elif strich == "schottky":                          # Schottky: S-förmige Enden
        c.create_line(k, my - g, k + g * 0.35, my - g, k + g * 0.35, my - g * 0.65, fill=farbe, width=s)
        c.create_line(k, my + g, k - g * 0.35, my + g, k - g * 0.35, my + g * 0.65, fill=farbe, width=s)
    return a, k


def _diode(c, w, h, farbe, art):
    u, cx, my = _einheit(w, h), w / 2, h / 2
    s, g = _strich(u), 1.0 * u
    a, k = _diodenkoerper(c, cx, my, g, farbe, s, art)
    _anschluesse(c, cx, my, a, k, farbe, s, u)
    _pin(c, cx - ANSCHLUSS * u, my - 0.75 * u, "A", farbe, u, anker="w")
    _pin(c, cx + ANSCHLUSS * u, my - 0.75 * u, "K", farbe, u, anker="e")


def diode_si(c, w, h, farbe):
    _diode(c, w, h, farbe, "normal")


def diode_schottky(c, w, h, farbe):
    _diode(c, w, h, farbe, "schottky")


def diode_z(c, w, h, farbe):
    _diode(c, w, h, farbe, "z")


def led(c, w, h, farbe):
    u, cx, my = _einheit(w, h), w / 2, h * 0.58                          # etwas tiefer: Platz für die Lichtpfeile
    s, g = _strich(u), 1.0 * u
    a, k = _diodenkoerper(c, cx, my, g, farbe, s)
    _anschluesse(c, cx, my, a, k, farbe, s, u)
    for dx in (-0.25 * u, 0.55 * u):                                     # zwei Pfeile nach aussen = Licht
        x0, y0 = cx + dx, my - g - 0.25 * u
        c.create_line(x0, y0, x0 + 0.8 * u, y0 - 0.9 * u, fill=farbe, width=max(1, s - 1),
                      arrow="last", arrowshape=(max(6, u * 0.5), max(7, u * 0.6), max(3, u * 0.22)))
    _pin(c, cx - ANSCHLUSS * u, my - 0.75 * u, "A +", farbe, u, anker="w")
    _pin(c, cx + ANSCHLUSS * u, my - 0.75 * u, "K −", farbe, u, anker="e")


# =============================================================================
# TRANSISTOREN
# =============================================================================
def _bjt(c, cx, my, g, farbe, s, u, npn=True):
    """Bipolartransistor mit Kreis. NPN: Pfeil vom Balken weg, PNP: zum Balken hin."""
    xm = cx + 0.35 * g                                                   # Kreis leicht rechts -> Basis hat Platz
    xb = xm - 0.3 * g
    c.create_oval(xm - g, my - g, xm + g, my + g, outline=farbe, width=s)
    c.create_line(xb, my - 0.55 * g, xb, my + 0.55 * g, fill=farbe, width=s + 1)
    c.create_line(xm - 1.8 * g, my, xb, my, fill=farbe, width=s)                                     # Basis
    c.create_line(xb, my - 0.25 * g, xm + 0.45 * g, my - 0.8 * g, xm + 0.45 * g, my - 1.5 * g, fill=farbe, width=s)
    pfeil = dict(fill=farbe, width=s, arrow="last", arrowshape=(max(6, g * 0.35), max(7, g * 0.42), max(3, g * 0.16)))
    if npn:
        c.create_line(xb, my + 0.25 * g, xm + 0.45 * g, my + 0.8 * g, **pfeil)
    else:
        c.create_line(xm + 0.45 * g, my + 0.8 * g, xb, my + 0.25 * g, **pfeil)
    c.create_line(xm + 0.45 * g, my + 0.8 * g, xm + 0.45 * g, my + 1.5 * g, fill=farbe, width=s)
    _pin(c, xm - 1.8 * g, my - 0.55 * u, "B", farbe, u, anker="w")
    _pin(c, xm + 0.45 * g + 0.4 * u, my - 1.35 * g, "C", farbe, u, anker="w")
    _pin(c, xm + 0.45 * g + 0.4 * u, my + 1.35 * g, "E", farbe, u, anker="w")


def npn(c, w, h, farbe):
    u = _einheit(w, h)
    _bjt(c, w / 2, h / 2, 1.55 * u, farbe, _strich(u), u, npn=True)


def pnp(c, w, h, farbe):
    u = _einheit(w, h)
    _bjt(c, w / 2, h / 2, 1.55 * u, farbe, _strich(u), u, npn=False)


def _mos(c, cx, my, g, farbe, s, u, n_kanal=True):
    """Anreicherungs-MOSFET mit Kreis. N-Kanal: Pfeil zum Kanal hin, P-Kanal: weg."""
    xm = cx + 0.35 * g
    xk = xm - 0.2 * g                                   # Kanal (3 Striche = Anreicherungstyp)
    xg = xk - 0.3 * g                                   # Gate-Platte
    c.create_oval(xm - g, my - g, xm + g, my + g, outline=farbe, width=s)
    c.create_line(xm - 1.8 * g, my + 0.45 * g, xg, my + 0.45 * g, fill=farbe, width=s)            # Gate
    c.create_line(xg, my - 0.55 * g, xg, my + 0.55 * g, fill=farbe, width=s)
    for dy in (-0.45, 0, 0.45):
        c.create_line(xk, my + (dy - 0.17) * g, xk, my + (dy + 0.17) * g, fill=farbe, width=s + 1)
    xr = xm + 0.4 * g
    c.create_line(xk, my - 0.45 * g, xr, my - 0.45 * g, xr, my - 1.5 * g, fill=farbe, width=s)    # Drain
    c.create_line(xk, my + 0.45 * g, xr, my + 0.45 * g, xr, my + 1.5 * g, fill=farbe, width=s)    # Source
    c.create_line(xr, my, xr, my + 0.45 * g, fill=farbe, width=s)                                 # Bulk an Source
    pfeil = dict(fill=farbe, width=s, arrow="last", arrowshape=(max(6, g * 0.35), max(7, g * 0.42), max(3, g * 0.16)))
    if n_kanal:
        c.create_line(xr, my, xk, my, **pfeil)
    else:
        c.create_line(xk, my, xr, my, **pfeil)
    _pin(c, xm - 1.8 * g, my + 0.45 * g - 0.55 * u, "G", farbe, u, anker="w")
    _pin(c, xr + 0.4 * u, my - 1.35 * g, "D", farbe, u, anker="w")
    _pin(c, xr + 0.4 * u, my + 1.35 * g, "S", farbe, u, anker="w")


def mosfet_n(c, w, h, farbe):
    u = _einheit(w, h)
    _mos(c, w / 2, h / 2, 1.55 * u, farbe, _strich(u), u, n_kanal=True)


def mosfet_p(c, w, h, farbe):
    u = _einheit(w, h)
    _mos(c, w / 2, h / 2, 1.55 * u, farbe, _strich(u), u, n_kanal=False)


# =============================================================================
# RELAIS (eine breitere Zelle)
# =============================================================================
def relais(c, w, h, farbe):
    """Spule (A1/A2) links, Wirkverbindung gestrichelt, Wechsler (11/12/14) rechts in Ruhelage."""
    s = max(2, int(h / 40))
    m = h * 0.5
    schrift = (config.SCHRIFT, max(8, int(h / 16)), "bold")
    # --- Spule: Rechteck (EN 60617) ---
    x0, x1 = 0.16 * w, 0.32 * w
    xm = (x0 + x1) / 2
    c.create_rectangle(x0, m - 0.2 * h, x1, m + 0.2 * h, outline=farbe, width=s)
    c.create_line(xm, 0.06 * h, xm, m - 0.2 * h, fill=farbe, width=s)
    c.create_line(xm, m + 0.2 * h, xm, 0.94 * h, fill=farbe, width=s)
    c.create_text(xm - 0.03 * w, 0.1 * h, text="A1", fill=farbe, font=schrift, anchor="e")
    c.create_text(xm - 0.03 * w, 0.9 * h, text="A2", fill=farbe, font=schrift, anchor="e")
    # --- Wechsler: COM (11) unten, Öffner (12) links oben, Schliesser (14) rechts oben ---
    xc, dx = 0.68 * w, 0.07 * w
    oben = m - 0.18 * h
    c.create_line(xc, 0.94 * h, xc, m + 0.22 * h, fill=farbe, width=s)                          # 11 (COM)
    c.create_line(xc - dx, 0.06 * h, xc - dx, oben, xc - dx * 0.35, oben, fill=farbe, width=s)   # 12 (Öffner)
    c.create_line(xc + dx, 0.06 * h, xc + dx, oben, xc + dx * 0.35, oben, fill=farbe, width=s)   # 14 (Schliesser)
    c.create_line(xc, m + 0.22 * h, xc - dx * 0.55, oben - 0.02 * h, fill=farbe, width=s)        # Zunge in Ruhe
    c.create_line(x1, m, xc - dx * 0.3, m, fill=farbe, width=max(1, s - 1), dash=(6, 4))          # Wirkverbindung
    c.create_text(xc + 0.03 * w, 0.9 * h, text="11", fill=farbe, font=schrift, anchor="w")
    c.create_text(xc - dx - 0.03 * w, 0.1 * h, text="12", fill=farbe, font=schrift, anchor="e")
    c.create_text(xc + dx + 0.03 * w, 0.1 * h, text="14", fill=farbe, font=schrift, anchor="w")


# =============================================================================
# REGISTRIERUNG: Schlüssel (wie in "steckbrief": {"symbol": ...}) -> Varianten
# =============================================================================
SYMBOLE = {
    "widerstand": [
        Variante(widerstand_iec, "IEC / EN (Europa)"),
        Variante(widerstand_ansi, "ANSI (USA, oft in Datenblättern)"),
    ],
    "kondensator": [
        Variante(kondensator_ungepolt, "ungepolt (Keramik, Folie)"),
        Variante(kondensator_gepolt, "gepolt (Elko): + beachten!"),
    ],
    "spule": [
        Variante(spule_en, "Spule (EN 60617)"),
        Variante(spule_kern, "mit Eisen-/Ferritkern"),
        Variante(spule_din, "alte DIN-Form (historisch, in älteren Plänen)"),
    ],
    "transformator": [
        Variante(transformator, "Primärwicklung N1 links, Sekundärwicklung N2 rechts, Eisenkern als Doppelstrich. "
                                "● = Wicklungsanfang: Punkt-Enden haben gleichzeitig dieselbe Polarität "
                                "(U1 und U2 in Phase).", 0.72, 340),
    ],
    "diode": [
        Variante(diode_si, "Diode (Si) – Kathode = Ring am Gehäuse"),
        Variante(diode_schottky, "Schottky-Diode"),
        Variante(diode_z, "Z-Diode (in Sperrrichtung betrieben)"),
    ],
    "led": [
        Variante(led, "A (+) Anode: langes Bein  ·  K (−) Kathode: kurzes Bein, abgeflachte Gehäuseseite",
                 0.6, 220),
    ],
    "bipolartransistor": [
        Variante(npn, "NPN – Pfeil am Emitter zeigt raus"),
        Variante(pnp, "PNP – Pfeil am Emitter zeigt rein"),
    ],
    "mosfet": [
        Variante(mosfet_n, "N-Kanal – Pfeil zeigt zum Kanal (rein)"),
        Variante(mosfet_p, "P-Kanal – Pfeil zeigt vom Kanal weg (raus)"),
    ],
    "relais": [
        Variante(relais, "Spule A1/A2 · Wechsler 11 (COM), 12 (Öffner), 14 (Schliesser) · gezeichnet in Ruhelage "
                         "(Spule stromlos)", 0.5, 300),
    ],
}
