# =============================================================================
# uebungen/schemas.py
# -----------------------------------------------------------------------------
# SCHEMA ZU JEDER ÜBUNG: kleiner Schaltplan mit den GEGEBENEN Werten - das Gesuchte steht als "?" darin.
# Gezeichnet mit demselben Code wie die interaktiven Schaltpläne (bauteile/grafiken/schaltplan.py) auf ein
# SvgCanvas (bauteile/grafiken/svg_canvas.py) - KEIN tkinter, läuft auch im Web.
#
#   schema_svg(a, dunkel=False, breite=440)   -> SVG-Text oder "" (Aufgabenart ohne Schema)
#   schema_paar(a, breite=440)                -> {"hell": svg, "dunkel": svg}  (für die Webseite)
#   a = Aufgabe aus uebungen/aufgaben.py (aufgabe() oder vorschau()) - braucht "art", "gegeben", "gesucht"
#
# NEUE AUFGABENART MIT SCHEMA: unten eine Funktion  _name(p, g, ges)  schreiben und in SCHEMAS eintragen.
#   p    Schaltplan (Raster-Einheiten, siehe Beispiel in schaltplan.py)
#   g    gegebene Werte als Text: {"U": "12 V", "R": "4.7 kΩ"}
#   ges  Zeichen der gesuchten Grösse, z.B. "I" -> wird mit "?" beschriftet
# Farben wie im Unterricht: Strom ROT, Spannung BLAU (Strom- und Spannungspfeile von schaltplan.py).
#
# WER RUFT DAS AUF?  web/ueben/views.py (Aufgabe, Übungsblatt, Vorschau), pruefung/rechner_faelle.py
# =============================================================================

from bauteile.grafiken.schaltplan import ORANGE, Schaltplan              # -> bauteile/grafiken/schaltplan.py
from bauteile.grafiken.svg_canvas import SvgCanvas                      # -> bauteile/grafiken/svg_canvas.py

GESUCHT = "?"


def iec_gatter(p, x, y, zeichen, eingaenge, invertiert=False, hoehe=None, namen=(), ausgang=""):
    """Gatter nach IEC 60617 (Rechteck mit &, ≥1, =1, 1), Mitte (x, y), Eingänge links, Ausgang rechts.
    namen: Beschriftung der Eingänge (z.B. ["A = 1", "B = 0"]), ausgang: Text rechts. Kreis = invertiert."""
    h = hoehe or max(1.4, 0.7 * eingaenge + 0.4)
    a, b = p.p(x - 0.8, y - h / 2), p.p(x + 0.8, y + h / 2)
    p.c.create_rectangle(*a, *b, outline=p.linie, fill=p.bg, width=p.dick)
    p.text(x, y - h / 2 + 0.35, zeichen, "center", fett=True)
    for i in range(eingaenge):
        ye = y - h / 2 + h * (i + 1) / (eingaenge + 1)
        p.leitung((x - 1.8, ye), (x - 0.8, ye))
        if i < len(namen):
            p.text(x - 1.9, ye, namen[i], "e", fett=True)
    x_aus = x + 0.8
    if invertiert:
        r = 0.16
        (ax, ay), (bx, by) = p.p(x + 0.8, y - r), p.p(x + 0.8 + 2 * r, y + r)
        p.c.create_oval(ax, ay, bx, by, outline=p.linie, width=p.dick, fill=p.bg)
        x_aus += 2 * r
    p.leitung((x_aus, y), (x + 1.9, y))
    if ausgang:
        p.text(x + 2.0, y, ausgang, "w", fett=True, farbe=ORANGE)


def kasten_baustein(p, x0, y0, x1, y1, titel, links=(), rechts=(), unten=()):
    """Baustein als Kasten (MUX, Decoder, Flipflop ...): Anschlüsse mit Namen innen und Werten aussen.
    links/rechts: [(Pin-Name, Text aussen)], gleichmässig verteilt; unten: [(x, Pin-Name, Text)]."""
    p.kasten(x0, y0, x1, y1, "")
    p.text((x0 + x1) / 2, y0 + 0.35, titel, "center", fett=True)
    for liste, seite in ((links, "links"), (rechts, "rechts")):
        for i, (pin, aussen) in enumerate(liste):
            y = y0 + 0.5 + (y1 - y0 - 0.5) * (i + 1) / (len(liste) + 1)
            if seite == "links":
                p.leitung((x0 - 0.9, y), (x0, y))
                p.text(x0 + 0.12, y, pin, "w", klein=True)
                if aussen:
                    p.text(x0 - 1.0, y, aussen, "e", fett=True)
            else:
                p.leitung((x1, y), (x1 + 0.9, y))
                p.text(x1 - 0.12, y, pin, "e", klein=True)
                if aussen:
                    p.text(x1 + 1.0, y, aussen, "w", fett=True, farbe=ORANGE if aussen.endswith(GESUCHT) else None)
    for x, pin, aussen in unten:
        p.leitung((x, y1), (x, y1 + 0.7))
        p.text(x, y1 - 0.12, pin, "s", klein=True)
        if aussen:
            p.text(x, y1 + 0.8, aussen, "n", fett=True)


def _kreis(p, x_q=1.5, x_r=6.0, y_o=1.0, y_u=5.0):
    """Grundkreis: Leitungen oben und unten von der Quelle (links) zum Bauteil (rechts)."""
    p.leitung((x_q, y_o + 0.6), (x_q, y_o), (x_r, y_o))
    p.leitung((x_q, y_u - 0.6), (x_q, y_u), (x_r, y_u))


# ---- Grundlagen ------------------------------------------------------------------
def _ohm_strom(p, g, ges):
    _kreis(p)
    p.quelle(1.5, 1.6, 4.4, "U", g["U"])
    p.widerstand(6, 1, 6, 5, "R", g["R"])
    p.strom(2.6, 1, 4.6, 1, f"I = {GESUCHT}")


def _ohm_spannung(p, g, ges):
    _kreis(p)
    p.quelle(1.5, 1.6, 4.4)
    p.widerstand(6, 1, 6, 5, "R", g["R"], seite="links")
    p.strom(2.6, 1, 4.6, 1, f"I = {g['I']}")
    p.leitung((6, 1), (7.2, 1), farbe=p.leise, dick=1)
    p.leitung((6, 5), (7.2, 5), farbe=p.leise, dick=1)
    p.spannung(7.2, 1.1, 4.9, f"U = {GESUCHT}")


def _ohm_widerstand(p, g, ges):
    _kreis(p)
    p.quelle(1.5, 1.6, 4.4, "U", g["U"])
    p.widerstand(6, 1, 6, 5, "R", GESUCHT)
    p.strom(2.6, 1, 4.6, 1, f"I = {g['I']}")


def _leistung_ui(p, g, ges):
    _kreis(p)
    p.quelle(1.5, 1.6, 4.4, "U", g["U"])
    p.widerstand(6, 1, 6, 5, "Verbraucher", f"P = {GESUCHT}")
    p.strom(2.6, 1, 4.6, 1, f"I = {g['I']}")


def _leistung_r(p, g, ges):
    _kreis(p)
    p.quelle(1.5, 1.6, 4.4)
    p.widerstand(6, 1, 6, 5, "R", g["R"], seite="links")
    p.strom(2.6, 1, 4.6, 1, f"I = {g['I']}")
    p.text(6.5, 3, f"P = {GESUCHT}", "w", farbe=ORANGE, fett=True)
    p.text(6.5, 3.55, "(Wärme)", "w", klein=True, farbe=p.leise)


# ---- Widerstandsnetzwerke -------------------------------------------------------
def _reihe(p, g, ges):
    y = 2.2
    p.anschluss(0.8, y, "A", seite="links")
    p.widerstand(0.8, y, 3.6, y, "R1", g["R1"])
    p.widerstand(3.6, y, 6.4, y, "R2", g["R2"])
    p.widerstand(6.4, y, 9.2, y, "R3", g["R3"])
    p.anschluss(9.2, y, "B")
    p.leitung((0.8, y + 0.9), (0.8, y + 1.2), (9.2, y + 1.2), (9.2, y + 0.9), farbe=p.leise, dick=1)
    p.text(5.0, y + 1.75, f"R_ges zwischen A und B = {GESUCHT}", "center", farbe=ORANGE, fett=True)


def _parallel(p, g, ges):
    p.anschluss(1.6, 1, "A", seite="links")
    p.anschluss(1.6, 5, "B", seite="links")
    p.leitung((1.6, 1), (7.2, 1))
    p.leitung((1.6, 5), (7.2, 5))
    p.knoten(4.4, 1)
    p.knoten(4.4, 5)
    p.widerstand(4.4, 1, 4.4, 5, "R1", g["R1"])
    p.widerstand(7.2, 1, 7.2, 5, "R2", g["R2"])
    p.text(1.2, 3, "R_ges", "w", farbe=ORANGE, fett=True)
    p.text(1.2, 3.5, f"= {GESUCHT}", "w", farbe=ORANGE, fett=True)


def _teiler_grund(p, g, x_r=5.0, x_a=7.5):
    p.quelle(1.5, 1.6, 6.4, "Ue", g["Ue"])
    p.leitung((1.5, 1.6), (1.5, 1), (x_r, 1))
    p.leitung((1.5, 6.4), (1.5, 7), (x_a, 7))
    p.widerstand(x_r, 1, x_r, 4, "R1", g["R1"])
    p.widerstand(x_r, 4, x_r, 7, "R2", g["R2"])
    p.leitung((x_r, 4), (x_a, 4))
    p.knoten(x_r, 4)
    p.knoten(x_r, 7)


def _teiler(p, g, ges):
    _teiler_grund(p, g)
    p.anschluss(7.5, 4)
    p.anschluss(7.5, 7)
    p.spannung(8.2, 4.1, 6.9, f"Ua = {GESUCHT}")


def _teiler_belastet(p, g, ges):
    _teiler_grund(p, g)
    p.knoten(7.5, 4)
    p.knoten(7.5, 7)
    p.widerstand(7.5, 4, 7.5, 7, "RL", g["RL"])
    p.leitung((7.5, 4), (9.6, 4), farbe=p.leise, dick=1)
    p.leitung((7.5, 7), (9.6, 7), farbe=p.leise, dick=1)
    p.spannung(9.6, 4.1, 6.9, f"Ua = {GESUCHT}")


# ---- RC-Glied ---------------------------------------------------------------------
def _rc_tau(p, g, ges):
    p.anschluss(1, 1.5)
    p.widerstand(1, 1.5, 4.6, 1.5, "R", g["R"])
    p.leitung((4.6, 1.5), (6, 1.5))
    p.kondensator(6, 1.5, 4.5, "C", g["C"])
    p.leitung((1, 4.5), (6, 4.5))
    p.anschluss(1, 4.5)
    p.text(3.5, 5.4, f"τ = {GESUCHT}", "center", farbe=ORANGE, fett=True)


def _rc_laden(p, g, ges):
    o, u = 1.6, 5.6                                                  # oben Platz für Name + Wert von R
    p.quelle(1.5, o + 0.6, u - 0.6, "Ue", g["Ue"])
    p.leitung((1.5, o + 0.6), (1.5, o), (2.2, o))
    p.schalter(2.2, o, 3.4, o, False, "t = 0")
    p.leitung((3.4, o), (4.0, o))
    p.widerstand(4.0, o, 6.8, o, "R", g["R"])
    p.kondensator(6.8, o, u, "C", g["C"], seite="links")
    p.leitung((1.5, u - 0.6), (1.5, u), (6.8, u))
    p.leitung((6.8, o), (8.0, o), farbe=p.leise, dick=1)
    p.leitung((6.8, u), (8.0, u), farbe=p.leise, dick=1)
    p.spannung(8.0, o + 0.1, u - 0.1, f"uC = {GESUCHT}")
    p.text(4.6, u + 0.7, f"Kondensator am Anfang leer · gesucht nach t = {g['t']}", "center", klein=True, farbe=p.leise)


# ---- Dioden & LED -------------------------------------------------------------------
def _led_vorwiderstand(p, g, ges):
    o, u = 1.6, 5.6                                                  # oben Platz für Name + Wert von RV
    p.quelle(1.5, o + 0.6, u - 0.6, "UB", g["UB"])
    p.leitung((1.5, o + 0.6), (1.5, o), (2.6, o))
    p.widerstand(2.6, o, 5.6, o, "RV", GESUCHT)
    p.leitung((5.6, o), (7, o))
    p.diode(7, o, 7, u, "LED", f"UF = {g['UF']}", seite="links")
    p.leitung((1.5, u - 0.6), (1.5, u), (7, u))
    for dy in (-0.35, 0.15):                                         # Lichtpfeile: die LED leuchtet
        a, b = p.p(7.5, 3.5 + dy), p.p(8.1, 3.0 + dy)
        p.c.create_line(*a, *b, fill=ORANGE, width=p.dick, arrow="last",
                        arrowshape=(p.u * 0.2, p.u * 0.24, p.u * 0.09))
    p.strom(5.4, u, 3.4, u, f"IF = {g['IF']}", seite="unten")


# art -> (Spalten, Zeilen, Zeichenfunktion)
SCHEMAS = {
    "ohm_strom": (8.0, 6.0, _ohm_strom),
    "ohm_spannung": (9.0, 6.0, _ohm_spannung),
    "ohm_widerstand": (8.0, 6.0, _ohm_widerstand),
    "leistung_ui": (9.0, 6.0, _leistung_ui),
    "leistung_r": (8.5, 6.0, _leistung_r),
    "reihe": (10.0, 4.6, _reihe),
    "parallel": (9.0, 6.0, _parallel),
    "teiler": (10.0, 8.0, _teiler),
    "teiler_belastet": (11.0, 8.0, _teiler_belastet),
    "rc_tau": (8.5, 6.0, _rc_tau),
    "rc_laden": (9.6, 6.8, _rc_laden),
    "led_vorwiderstand": (9.0, 7.0, _led_vorwiderstand),
}


def schema_svg(a, dunkel=False, breite=440):
    """Schema zur Aufgabe als SVG-Text (Hintergrund wie die Karte). "" = für diese Art gibt es keins."""
    if a.get("art") not in SCHEMAS:
        return ""
    spalten, zeilen, zeichnen = SCHEMAS[a["art"]]
    rand = 0.7                                                       # wie Schaltplan(): Platz links und rechts
    hoehe = round(breite * zeilen / (spalten + 2 * rand))
    c = SvgCanvas(breite, hoehe, dunkel)
    zeichnen(Schaltplan(c, breite, hoehe, spalten, zeilen, rand), dict(a["gegeben"]), a["gesucht"]["zeichen"])
    return c.svg()


def schema_paar(a, breite=440):
    """Hell UND dunkel - die Webseite zeigt per CSS das passende (.nur-hell / .nur-dunkel)."""
    hell = schema_svg(a, False, breite)
    return {"hell": hell, "dunkel": schema_svg(a, True, breite)} if hell else None
