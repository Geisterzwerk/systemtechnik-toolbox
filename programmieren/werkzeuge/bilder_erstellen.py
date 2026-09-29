# =============================================================================
# programmieren/werkzeuge/bilder_erstellen.py
# -----------------------------------------------------------------------------
# Erzeugt ALLE Bilder für das Programmier-Wiki (Flussdiagramme, Diagramme).
# Speichert sie nach:  images/programmieren/
#
# Braucht man nur, wenn man ein Bild ändern oder neu erstellen will:
#     python programmieren/werkzeuge/bilder_erstellen.py
# (benötigt: pip install matplotlib)
#
# Die Bilder werden mit matplotlib GEZEICHNET (nicht KI-generiert), damit
# sie fachlich exakt stimmen.
# =============================================================================

import os

import matplotlib

matplotlib.use("Agg")                       # ohne Fenster zeichnen
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

# Zielordner: <Projekt>/images/programmieren
BASIS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIEL = os.path.join(BASIS, "images", "programmieren")
os.makedirs(ZIEL, exist_ok=True)

# ---- Farben (passend zum Dark-Design der Toolbox) ----
BG = "#23262D"
TEXT = "#E6E8EC"
LEISE = "#9AA1AD"
BLAU = "#3B82F6"
GRUEN = "#22C55E"
ORANGE = "#F59E0B"
LILA = "#A855F7"
ROT = "#EF4444"
GRAU = "#4B5263"
plt.rcParams["font.family"] = "DejaVu Sans"


# =============================================================================
# Zeichen-Hilfsfunktionen
# =============================================================================
def leinwand(breite, hoehe):
    """Neue Zeichenfläche. Koordinaten = 'Einheiten' (1 Einheit ≈ 60 px)."""
    fig, ax = plt.subplots(figsize=(breite, hoehe), dpi=120)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, breite)
    ax.set_ylim(0, hoehe)
    ax.axis("off")
    return fig, ax


def speichern(fig, name):
    pfad = os.path.join(ZIEL, name)
    fig.savefig(pfad, facecolor=BG, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("gespeichert:", pfad)


def box(ax, x, y, b, h, text, farbe=BLAU, textfarbe="white", groesse=12, rund=0.15, fett=True):
    """Abgerundetes Rechteck mit Text; (x, y) = Mittelpunkt."""
    ax.add_patch(FancyBboxPatch((x - b / 2, y - h / 2), b, h, boxstyle=f"round,pad=0,rounding_size={rund}",
                                facecolor=farbe, edgecolor="none"))
    ax.text(x, y, text, ha="center", va="center", color=textfarbe, fontsize=groesse,
            fontweight="bold" if fett else "normal", linespacing=1.4)


def raute(ax, x, y, b, h, text, farbe=ORANGE):
    """Entscheidungs-Raute (Flussdiagramm)."""
    ax.add_patch(Polygon([(x, y + h / 2), (x + b / 2, y), (x, y - h / 2), (x - b / 2, y)],
                         facecolor=farbe, edgecolor="none"))
    ax.text(x, y, text, ha="center", va="center", color="#1B1D22", fontsize=11, fontweight="bold")


def pfeil(ax, punkte, text=None, text_pos=None, farbe=LEISE):
    """Pfeil entlang mehrerer Punkte [(x1,y1), (x2,y2), ...]. Spitze am letzten Punkt."""
    for (x1, y1), (x2, y2) in zip(punkte[:-2], punkte[1:-1]):
        ax.plot([x1, x2], [y1, y2], color=farbe, lw=2, solid_capstyle="round")
    ax.add_patch(FancyArrowPatch(punkte[-2], punkte[-1], arrowstyle="-|>", mutation_scale=18,
                                 color=farbe, lw=2))
    if text:
        tx, ty = text_pos
        ax.text(tx, ty, text, color=farbe, fontsize=11, fontweight="bold", ha="center", va="center")


def titel(ax, x, y, text, groesse=15):
    ax.text(x, y, text, color=TEXT, fontsize=groesse, fontweight="bold", ha="center", va="center")


# =============================================================================
# Bilder
# =============================================================================
def bild_programmablauf():
    fig, ax = leinwand(12, 5.2)
    zeilen = [("C++", 4.2, [("Quellcode\n.cpp", GRAU), ("Compiler\n(g++)", BLAU), ("Maschinencode\n.exe", GRUEN), ("CPU", LILA)]),
              ("C#", 2.6, [("Quellcode\n.cs", GRAU), ("Compiler\n(dotnet)", BLAU), ("Zwischencode\nIL", ORANGE), (".NET JIT\n→ CPU", LILA)]),
              ("Python", 1.0, [("Quellcode\n.py", GRAU), ("Interpreter\n(python)", BLAU), ("führt Zeile für\nZeile aus", ORANGE), ("CPU", LILA)])]
    for sprache, y, schritte in zeilen:
        ax.text(0.55, y, sprache, color=TEXT, fontsize=14, fontweight="bold", va="center", ha="center")
        for i, (text, farbe) in enumerate(schritte):
            x = 2.4 + i * 2.8
            box(ax, x, y, 2.3, 1.0, text, farbe=farbe, groesse=10.5)
            if i < len(schritte) - 1:
                pfeil(ax, [(x + 1.2, y), (x + 1.6, y)])
    speichern(fig, "programmablauf.png")


def bild_variable_speicher():
    fig, ax = leinwand(11, 4.2)
    titel(ax, 5.5, 3.8, "Arbeitsspeicher (RAM)")
    variablen = [("0x1000", "alter", "int", "25", BLAU), ("0x1004", "spannung", "double", "24.5", GRUEN),
                 ("0x100C", "aktiv", "bool", "true", ORANGE), ("0x100D", "zeichen", "char", "'A'", LILA)]
    for i, (adr, name, typ, wert, farbe) in enumerate(variablen):
        x = 1.5 + i * 2.7
        box(ax, x, 2.2, 2.3, 1.3, wert, farbe=farbe, groesse=17)
        ax.text(x, 3.15, f"{name}", color=TEXT, fontsize=12, fontweight="bold", ha="center")
        ax.text(x, 1.25, f"Typ: {typ}", color=LEISE, fontsize=10.5, ha="center")
        ax.text(x, 0.8, f"Adresse: {adr}", color=LEISE, fontsize=10.5, ha="center", family="monospace")
    speichern(fig, "variable_speicher.png")


def bild_datentypen_bits():
    typen = [("bool", 8, ORANGE), ("char (C++)", 8, LILA), ("byte / uint8_t", 8, GRAU), ("short", 16, BLAU),
             ("char (C#)", 16, LILA), ("int / float", 32, BLAU), ("long (C#) / long long", 64, BLAU),
             ("double", 64, GRUEN), ("decimal (C#)", 128, ORANGE)]
    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=120)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    namen = [t[0] for t in typen][::-1]
    bits = [t[1] for t in typen][::-1]
    farben = [t[2] for t in typen][::-1]
    ax.grid(False)                          # keine Gitterlinien
    balken = ax.barh(namen, bits, color=farben, height=0.62, edgecolor="none")
    for b, wert in zip(balken, bits):
        ax.text(b.get_width() + 1.5, b.get_y() + b.get_height() / 2, f"{wert} Bit = {wert // 8} Byte",
                va="center", color=TEXT, fontsize=11)
    ax.set_xlim(0, 150)
    ax.set_xlabel("Bit", color=LEISE, fontsize=11)
    ax.tick_params(colors=TEXT, labelsize=11)
    for seite in ("top", "right"):
        ax.spines[seite].set_visible(False)
    for seite in ("left", "bottom"):
        ax.spines[seite].set_color(GRAU)
    ax.set_title("Speichergrösse der Datentypen", color=TEXT, fontsize=15, fontweight="bold", pad=12)
    speichern(fig, "datentypen_bits.png")


def bild_zahlensysteme():
    fig, ax = leinwand(12, 4.6)
    titel(ax, 6, 4.25, "1 Byte = 8 Bit   →   Beispiel: 200 = 0b1100_1000 = 0xC8")
    bits = [1, 1, 0, 0, 1, 0, 0, 0]
    for i, bit in enumerate(bits):
        x = 1.4 + i * 1.3
        nr = 7 - i
        box(ax, x, 2.4, 1.1, 1.1, str(bit), farbe=BLAU if bit else GRAU, groesse=20)
        ax.text(x, 3.3, f"Bit {nr}", color=LEISE, fontsize=10, ha="center")
        ax.text(x, 1.5, f"2^{nr} = {2 ** nr}", color=TEXT if bit else LEISE, fontsize=10, ha="center")
    # Nibble-Klammern
    for start, text in ((0, "Nibble 1100 = C"), (4, "Nibble 1000 = 8")):
        x1, x2 = 1.4 + start * 1.3 - 0.5, 1.4 + (start + 3) * 1.3 + 0.5
        ax.plot([x1, x1, x2, x2], [1.15, 1.0, 1.0, 1.15], color=ORANGE, lw=2)
        ax.text((x1 + x2) / 2, 0.65, text, color=ORANGE, fontsize=11.5, fontweight="bold", ha="center")
    ax.text(0.35, 3.3, "MSB", color=ROT, fontsize=10, fontweight="bold", ha="center")
    ax.text(11.7, 3.3, "LSB", color=ROT, fontsize=10, fontweight="bold", ha="center")
    ax.text(6, 0.15, "128 + 64 + 8 = 200", color=GRUEN, fontsize=12, fontweight="bold", ha="center")
    speichern(fig, "zahlensysteme.png")


def bild_if_else():
    fig, ax = leinwand(11, 7.2)
    box(ax, 5.5, 6.7, 2.4, 0.7, "Start", farbe=GRAU)
    pfeil(ax, [(5.5, 6.35), (5.5, 5.85)])
    raute(ax, 5.5, 5.2, 3.6, 1.3, "Temp ≥ 80 ?")
    pfeil(ax, [(7.3, 5.2), (9.2, 5.2), (9.2, 1.2)], "ja", (8.1, 5.45), GRUEN)
    box(ax, 9.2, 0.85, 2.6, 0.7, "ALARM", farbe=ROT)
    pfeil(ax, [(5.5, 4.55), (5.5, 3.85)], "nein", (5.95, 4.2), ROT)
    raute(ax, 5.5, 3.2, 3.6, 1.3, "Temp ≥ 60 ?")
    pfeil(ax, [(7.3, 3.2), (8.0, 3.2), (8.0, 2.05)], "ja", (7.65, 3.45), GRUEN)
    box(ax, 8.0, 1.7, 2.2, 0.7, "Warnung", farbe=ORANGE, textfarbe="#1B1D22")
    pfeil(ax, [(3.7, 3.2), (2.2, 3.2), (2.2, 2.05)], "nein (else)", (2.9, 3.45), ROT)
    box(ax, 2.2, 1.7, 2.2, 0.7, "OK", farbe=GRUEN)
    ax.text(5.5, 0.2, "Es wird immer genau EIN Block ausgeführt, der erste zutreffende", color=LEISE,
            fontsize=11, ha="center")
    speichern(fig, "if_else.png")


def bild_switch():
    fig, ax = leinwand(12, 5)
    box(ax, 6, 4.4, 3.4, 0.8, "switch (zustand)", farbe=BLAU)
    faelle = [("case 0", "AUS", GRAU), ("case 1", "STANDBY", ORANGE), ("case 2 / 3", "LÄUFT", GRUEN),
              ("default", "Unbekannt", ROT)]
    for i, (fall, text, farbe) in enumerate(faelle):
        x = 1.6 + i * 2.95
        pfeil(ax, [(6, 4.0), (6, 3.4), (x, 3.4), (x, 2.75)])
        ax.text(x, 2.95, fall, color=TEXT, fontsize=10.5, fontweight="bold", ha="center",
                bbox=dict(facecolor=BG, edgecolor="none", pad=1))
        box(ax, x, 2.0, 2.4, 0.9, text, farbe=farbe, textfarbe="#1B1D22" if farbe == ORANGE else "white")
        pfeil(ax, [(x, 1.55), (x, 1.05)])
        ax.text(x, 0.8, "break", color=LEISE, fontsize=10, ha="center", family="monospace")
    speichern(fig, "switch.png")


def bild_schleife(name, art):
    """Flussdiagramme für for / while / do-while."""
    fig, ax = leinwand(10, 7)
    box(ax, 5, 6.55, 2.2, 0.65, "Start", farbe=GRAU)
    if art == "for":
        pfeil(ax, [(5, 6.2), (5, 5.75)])
        box(ax, 5, 5.4, 3.6, 0.7, "Start:  int i = 0", farbe=LILA)
        pfeil(ax, [(5, 5.05), (5, 4.55)])
        raute(ax, 5, 3.9, 3.4, 1.3, "i < 5 ?")
        pfeil(ax, [(5, 3.25), (5, 2.65)], "ja", (5.35, 2.95), GRUEN)
        box(ax, 5, 2.3, 3.4, 0.7, "Körper: print(i)", farbe=BLAU)
        pfeil(ax, [(5, 1.95), (5, 1.45)])
        box(ax, 5, 1.1, 3.0, 0.7, "Schritt:  i++", farbe=LILA)
        pfeil(ax, [(3.5, 1.1), (1.6, 1.1), (1.6, 3.9), (3.3, 3.9)])
        pfeil(ax, [(6.7, 3.9), (8.5, 3.9), (8.5, 1.45)], "nein", (7.6, 4.15), ROT)
        box(ax, 8.5, 1.1, 1.8, 0.7, "Ende", farbe=GRAU)
    elif art == "while":
        pfeil(ax, [(5, 6.2), (5, 5.45)])
        raute(ax, 5, 4.8, 3.8, 1.3, "Bedingung\nwahr?")
        pfeil(ax, [(5, 4.15), (5, 3.35)], "ja", (5.35, 3.75), GRUEN)
        box(ax, 5, 3.0, 3.4, 0.7, "Körper ausführen", farbe=BLAU)
        pfeil(ax, [(5, 2.65), (5, 2.1), (1.6, 2.1), (1.6, 4.8), (3.1, 4.8)])
        pfeil(ax, [(6.9, 4.8), (8.5, 4.8), (8.5, 1.45)], "nein", (7.7, 5.05), ROT)
        box(ax, 8.5, 1.1, 1.8, 0.7, "Ende", farbe=GRAU)
        ax.text(5, 0.35, "Zuerst prüfen: evtl. 0 Durchläufe", color=LEISE, fontsize=11, ha="center")
    else:  # do-while
        pfeil(ax, [(5, 6.2), (5, 5.55)])
        box(ax, 5, 5.2, 3.4, 0.7, "Körper ausführen", farbe=BLAU)
        pfeil(ax, [(5, 4.85), (5, 4.1)])
        raute(ax, 5, 3.45, 3.8, 1.3, "Bedingung\nwahr?")
        pfeil(ax, [(3.1, 3.45), (1.6, 3.45), (1.6, 5.2), (3.3, 5.2)], "ja", (2.3, 3.7), GRUEN)
        pfeil(ax, [(5, 2.8), (5, 1.45)], "nein", (5.45, 2.1), ROT)
        box(ax, 5, 1.1, 1.8, 0.7, "Ende", farbe=GRAU)
        ax.text(5, 0.35, "Zuerst ausführen: mindestens 1 Durchlauf", color=LEISE, fontsize=11, ha="center")
    speichern(fig, name)


def bild_funktion_blackbox():
    fig, ax = leinwand(12, 3.8)
    box(ax, 1.6, 2.35, 2.4, 0.7, "spannung = 24", farbe=GRAU, groesse=11)
    box(ax, 1.6, 1.35, 2.4, 0.7, "strom = 1.5", farbe=GRAU, groesse=11)
    ax.text(1.6, 3.2, "Parameter (Eingabe)", color=LEISE, fontsize=11, ha="center")
    pfeil(ax, [(2.85, 2.35), (4.1, 1.95)])
    pfeil(ax, [(2.85, 1.35), (4.1, 1.75)])
    box(ax, 6, 1.85, 3.6, 1.8, "leistung(u, i)\n\nreturn u * i", farbe=BLAU, groesse=13)
    ax.text(6, 3.2, "Funktion (Verarbeitung)", color=LEISE, fontsize=11, ha="center")
    pfeil(ax, [(7.85, 1.85), (9.1, 1.85)])
    box(ax, 10.4, 1.85, 2.2, 0.8, "36.0", farbe=GRUEN, groesse=15)
    ax.text(10.4, 3.2, "Rückgabewert (Ausgabe)", color=LEISE, fontsize=11, ha="center")
    speichern(fig, "funktion_blackbox.png")


def bild_array_index():
    fig, ax = leinwand(12, 3.6)
    werte = ["12.1", "12.4", "11.9", "12.0", "12.3"]
    for i, w in enumerate(werte):
        x = 1.8 + i * 2.1
        box(ax, x, 1.9, 2.0, 1.0, w, farbe=BLAU, groesse=15, rund=0.05)
        ax.text(x, 2.75, f"[{i}]", color=ORANGE, fontsize=13, fontweight="bold", ha="center", family="monospace")
        ax.text(x, 1.05, f"[{i - len(werte)}]", color=LEISE, fontsize=10.5, ha="center", family="monospace")
    ax.text(0.35, 1.9, "messwerte", color=TEXT, fontsize=11, fontweight="bold", ha="center", rotation=90, va="center")
    ax.text(6, 3.35, "Index beginnt bei 0  ·  letzter Index = Länge − 1 = 4", color=TEXT, fontsize=13,
            fontweight="bold", ha="center")
    ax.text(6, 0.45, "negative Indizes (nur Python): [-1] = letztes Element", color=LEISE, fontsize=11, ha="center")
    speichern(fig, "array_index.png")


def bild_klasse_objekt():
    fig, ax = leinwand(12, 5.4)
    # Klasse (Bauplan)
    ax.add_patch(FancyBboxPatch((0.4, 0.6), 4.2, 4.2, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor="none", edgecolor=BLAU, lw=2.5, linestyle="--"))
    box(ax, 2.5, 4.35, 4.2, 0.7, "class TemperaturSensor", farbe=BLAU, groesse=12, rund=0.1)
    ax.text(0.7, 3.5, "Attribute:", color=ORANGE, fontsize=11, fontweight="bold")
    ax.text(0.9, 2.95, "name\ngrenzwert\nwert", color=TEXT, fontsize=11, va="top", family="monospace", linespacing=1.6)
    ax.text(0.7, 1.75, "Methoden:", color=GRUEN, fontsize=11, fontweight="bold")
    ax.text(0.9, 1.35, "messen()\nist_zu_heiss()", color=TEXT, fontsize=11, va="top", family="monospace", linespacing=1.6)
    ax.text(2.5, 0.25, "BAUPLAN (Klasse)", color=BLAU, fontsize=12, fontweight="bold", ha="center")
    # Objekte
    objekte = [(8.6, 3.75, "serverraum", "\"Serverraum\"", "30", "32.5"), (8.6, 1.45, "labor", "\"Labor\"", "25", "21.0")]
    for x, y, var, name, grenz, wert in objekte:
        pfeil(ax, [(4.7, 2.7), (6.1, y)], farbe=LEISE)
        box(ax, x, y, 4.8, 1.85, "", farbe="#2F3440", rund=0.12)
        ax.text(x, y + 0.6, f"Objekt: {var}", color=GRUEN, fontsize=12, fontweight="bold", ha="center")
        ax.text(x - 2.0, y - 0.05, f"name = {name}\ngrenzwert = {grenz}\nwert = {wert}", color=TEXT,
                fontsize=10.5, va="center", family="monospace", linespacing=1.5)
    ax.text(8.6, 0.25, "OBJEKTE (Instanzen) mit eigenen Werten", color=GRUEN, fontsize=12, fontweight="bold", ha="center")
    speichern(fig, "klasse_objekt.png")


def uml_klasse(ax, x, y_oben, b, name, attribute, methoden, farbe):
    """UML-Klassenkasten: Name | Attribute | Methoden. Gibt Unterkante zurück."""
    h_name, h_zeile = 0.6, 0.36
    h_attr = max(1, len(attribute)) * h_zeile + 0.15
    h_meth = max(1, len(methoden)) * h_zeile + 0.15
    y = y_oben
    ax.add_patch(FancyBboxPatch((x - b / 2, y - h_name), b, h_name, boxstyle="square,pad=0", facecolor=farbe, edgecolor=farbe))
    ax.text(x, y - h_name / 2, name, color="white", fontsize=11.5, fontweight="bold", ha="center", va="center")
    y -= h_name
    for liste in (attribute, methoden):
        h = max(1, len(liste)) * h_zeile + 0.15
        ax.add_patch(FancyBboxPatch((x - b / 2, y - h), b, h, boxstyle="square,pad=0", facecolor="#2F3440", edgecolor=farbe, lw=1.5))
        for i, eintrag in enumerate(liste):
            ax.text(x - b / 2 + 0.15, y - 0.25 - i * h_zeile, eintrag, color=TEXT, fontsize=10, va="center", family="monospace")
        y -= h
    return y


def bild_vererbung():
    fig, ax = leinwand(12, 6.4)
    unten = uml_klasse(ax, 6, 6.2, 4.2, "Sensor", ["# name", "# einheit", "+ wert"], ["+ anzeigen()"], BLAU)
    links = uml_klasse(ax, 2.6, 3.0, 4.4, "TemperaturSensor", ["(erbt alles)"], ["+ in_fahrenheit()"], GRUEN)
    rechts = uml_klasse(ax, 9.4, 3.0, 4.4, "DruckSensor", ["- max_bar"], ["+ anzeigen()  «override»"], ORANGE)
    # Vererbungspfeile (hohle Spitze = "erbt von")
    for x in (2.6, 9.4):
        ax.plot([x, x, 6], [3.0, 3.6, 3.6], color=LEISE, lw=2)
    ax.add_patch(FancyArrowPatch((6, 3.6), (6, unten), arrowstyle="-|>,head_width=0.5,head_length=0.8",
                                 mutation_scale=15, facecolor=BG, edgecolor=LEISE, lw=2))
    ax.text(6.25, 3.25, "erbt von  ('ist ein')", color=LEISE, fontsize=10.5, va="center")
    ax.text(6, 0.25, "+ public    # protected    - private", color=LEISE, fontsize=10.5, ha="center", family="monospace")
    speichern(fig, "vererbung.png")


def bild_mehrere_dateien():
    fig, ax = leinwand(12, 6.2)
    box(ax, 6, 5.5, 3.2, 0.8, "main.py\nerzeugt & verbindet", farbe=GRAU, groesse=11)
    box(ax, 6, 3.6, 3.4, 1.1, "steuerung.py\nclass Steuerung", farbe=BLAU, groesse=12)
    box(ax, 1.9, 1.7, 3.0, 1.0, "sensor.py\nclass Sensor", farbe=GRUEN, groesse=12)
    box(ax, 10.1, 1.7, 3.0, 1.0, "anzeige.py\nclass Anzeige", farbe=ORANGE, textfarbe="#1B1D22", groesse=12)
    pfeil(ax, [(6, 5.1), (6, 4.2)], "Steuerung(sensor, anzeige)", (8.2, 4.65), LEISE)
    pfeil(ax, [(4.3, 3.4), (2.4, 2.25)], "sensor.messen()", (2.7, 3.05), GRUEN)
    pfeil(ax, [(7.7, 3.4), (9.6, 2.25)], "anzeige.zeigen(text)", (9.5, 3.05), ORANGE)
    ax.text(6, 0.45, "Steuerung HAT EINEN Sensor und HAT EINE Anzeige (Komposition).\n"
                     "Sensor und Anzeige kennen sich gegenseitig NICHT.",
            color=LEISE, fontsize=10.5, ha="center", va="center")
    speichern(fig, "mehrere_dateien.png")


def bild_try_catch():
    fig, ax = leinwand(11, 6.2)
    box(ax, 5.5, 5.6, 4.6, 0.8, "try:   riskanter Code", farbe=BLAU)
    pfeil(ax, [(3.9, 5.2), (2.6, 3.75)], "kein Fehler", (2.3, 4.6), GRUEN)
    pfeil(ax, [(7.1, 5.2), (8.4, 3.75)], "Fehler!", (8.8, 4.6), ROT)
    box(ax, 2.6, 3.35, 3.8, 0.8, "else:  (nur Python)", farbe=GRUEN)
    box(ax, 8.4, 3.35, 3.8, 0.8, "catch / except:\nFehler behandeln", farbe=ROT, groesse=11)
    pfeil(ax, [(2.6, 2.95), (4.6, 1.55)])
    pfeil(ax, [(8.4, 2.95), (6.4, 1.55)])
    box(ax, 5.5, 1.15, 4.6, 0.8, "finally:  läuft IMMER", farbe=LILA)
    ax.text(5.5, 0.2, "Programm läuft weiter, statt abzustürzen", color=LEISE, fontsize=11, ha="center")
    speichern(fig, "try_catch.png")


def bild_pointer():
    fig, ax = leinwand(12, 4.2)
    titel(ax, 6, 3.85, "int x = 42;      int* p = &x;")
    box(ax, 3, 2.0, 2.6, 1.2, "42", farbe=BLAU, groesse=20, rund=0.05)
    ax.text(3, 2.95, "x  (int)", color=TEXT, fontsize=12, fontweight="bold", ha="center")
    ax.text(3, 1.05, "Adresse: 0x1000", color=LEISE, fontsize=11, ha="center", family="monospace")
    box(ax, 9, 2.0, 2.6, 1.2, "0x1000", farbe=ORANGE, textfarbe="#1B1D22", groesse=16, rund=0.05)
    ax.text(9, 2.95, "p  (int*)", color=TEXT, fontsize=12, fontweight="bold", ha="center")
    ax.text(9, 1.05, "Adresse: 0x2000", color=LEISE, fontsize=11, ha="center", family="monospace")
    pfeil(ax, [(7.65, 2.0), (4.35, 2.0)], "zeigt auf", (6, 2.3), ORANGE)
    ax.text(6, 0.3, "*p  liest den Wert an der Adresse  →  42", color=GRUEN, fontsize=12, fontweight="bold", ha="center")
    speichern(fig, "pointer.png")


if __name__ == "__main__":
    bild_programmablauf()
    bild_variable_speicher()
    bild_datentypen_bits()
    bild_zahlensysteme()
    bild_if_else()
    bild_switch()
    bild_schleife("for_schleife.png", "for")
    bild_schleife("while_schleife.png", "while")
    bild_schleife("do_while.png", "do")
    bild_funktion_blackbox()
    bild_array_index()
    bild_klasse_objekt()
    bild_vererbung()
    bild_mehrere_dateien()
    bild_try_catch()
    bild_pointer()
    print("Fertig!")
