# =============================================================================
# programmieren/werkzeuge/bilder_hell.py   <-  von Hand starten:  py programmieren/werkzeuge/bilder_hell.py
# -----------------------------------------------------------------------------
# Macht aus den dunklen Bildern in images/programmieren/ eine HELLE Variante  <name>_hell.png
# für den Light Mode. Die App zeigt dann automatisch die passende Variante (core/layout.py
# ResponsiveBild -> CTkImage mit light_image und dark_image) - auch beim Umschalten.
#
# WIE? Die Bilder stammen aus bilder_erstellen.py und benutzen nur wenige feste Farben (PALETTE).
# Jeder Pixel ist eine dieser Farben oder eine Mischung aus ZWEI davon (Kantenglättung).
# Für jede vorkommende Farbe wird die passende Mischung gesucht und dann mit den HELLEN
# Farben (HELL) gleich gemischt. So bleiben die Kanten glatt.
#
# Nur Pillow nötig (kein matplotlib). Wird NICHT in die EXE gepackt (Ordner "werkzeuge").
# WER RUFT DAS AUF?  niemand - nur von Hand, nachdem bilder_erstellen.py neue Bilder gemacht hat
# =============================================================================

import itertools
import os

from PIL import Image

BASIS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDNER = os.path.join(BASIS, "images", "programmieren")

# dunkle Farbe (aus bilder_erstellen.py)  ->  helle Farbe (passend zu config.FARBEN im Light Mode)
HELL = {
    "#23262D": "#FFFFFF",      # Hintergrund
    "#2F3440": "#EEF1F5",      # Flächen / Kästen
    "#E6E8EC": "#1D2939",      # Text
    "#9AA1AD": "#667085",      # leiser Text, Pfeile
    "#4B5263": "#4B5263",      # graue Kästen (weisse Schrift darauf bleibt lesbar)
    "#1B1D22": "#1B1D22",      # dunkle Schrift auf Orange
    "#FFFFFF": "#FFFFFF",      # weisse Schrift in farbigen Kästen
    "#3B82F6": "#2563EB",      # Farben eine Spur kräftiger -> besser lesbar auf Weiss
    "#22C55E": "#16A34A",
    "#F59E0B": "#D97706",
    "#A855F7": "#9333EA",
    "#EF4444": "#DC2626",
}


def _rgb(hexwert):
    return tuple(int(hexwert[i:i + 2], 16) for i in (1, 3, 5))


PALETTE = [(_rgb(d), _rgb(h)) for d, h in HELL.items()]
_NAMEN = list(HELL)
BUNT = {"#3B82F6", "#22C55E", "#F59E0B", "#A855F7", "#EF4444", "#4B5263"}


def _erlaubt(a, b):
    """Nur Farben mischen, die im Bild wirklich nebeneinander liegen können (sonst falsche dunkle Punkte):
    dunkle Schrift nur auf Orange, weisse Schrift nur auf farbigen Kästen."""
    for x, y in ((a, b), (b, a)):
        if x == "#1B1D22":
            return y == "#F59E0B"
        if x == "#FFFFFF":
            return y in BUNT
    return True


PAARE = [(i, j) for i, j in itertools.combinations(range(len(PALETTE)), 2) if _erlaubt(_NAMEN[i], _NAMEN[j])]


def _farbe_umrechnen(pixel):
    """Pixel -> beste Mischung a + t·(b − a) aus zwei Palettenfarben -> dieselbe Mischung in hell."""
    bester = None
    for i in range(len(PALETTE)):                                  # reine Farbe
        a = PALETTE[i][0]
        d = sum((p - q) ** 2 for p, q in zip(pixel, a))
        if bester is None or d < bester[0]:
            bester = (d, i, i, 0.0)
    for i, j in PAARE:                                             # Mischung aus zwei Farben
        a, b = PALETTE[i][0], PALETTE[j][0]
        ab = [q - p for p, q in zip(a, b)]
        laenge = sum(x * x for x in ab)
        if laenge == 0:
            continue
        t = max(0.0, min(1.0, sum((p - q) * x for p, q, x in zip(pixel, a, ab)) / laenge))
        d = sum((p - (q + t * x)) ** 2 for p, q, x in zip(pixel, a, ab))
        if d < bester[0]:
            bester = (d, i, j, t)
    _, i, j, t = bester
    ha, hb = PALETTE[i][1], PALETTE[j][1]
    return tuple(round(p + t * (q - p)) for p, q in zip(ha, hb))


def hell_machen(pfad):
    bild = Image.open(pfad).convert("RGBA")
    alpha = bild.getchannel("A")
    rgb = bild.convert("RGB")
    tabelle = {farbe: _farbe_umrechnen(farbe) for _anzahl, farbe in rgb.getcolors(maxcolors=10_000_000)}
    neu = Image.new("RGB", rgb.size)
    daten = rgb.get_flattened_data() if hasattr(rgb, "get_flattened_data") else rgb.getdata()
    neu.putdata([tabelle[p] for p in daten])
    neu.putalpha(alpha)
    ziel = pfad[:-4] + "_hell.png"
    neu.save(ziel, optimize=True)
    return ziel


def main():
    for name in sorted(os.listdir(ORDNER)):
        if name.lower().endswith(".png") and not name.endswith("_hell.png"):
            print("gespeichert:", hell_machen(os.path.join(ORDNER, name)))


if __name__ == "__main__":
    main()
