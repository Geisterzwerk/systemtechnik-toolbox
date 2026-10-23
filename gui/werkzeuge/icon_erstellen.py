# =============================================================================
# gui/werkzeuge/icon_erstellen.py   <-  EINMAL von Hand starten:  py gui/werkzeuge/icon_erstellen.py
# -----------------------------------------------------------------------------
# Zeichnet das SystemLab-Logo mit Pillow und speichert es als
#   images/systemlab.png   (256 x 256, z.B. für die Webseite oder eine Anleitung)
#   images/systemlab.ico   (16, 24, 32, 48, 64, 128, 256 px - Fenster-Icon und EXE-Icon)
#
# Das Logo: blaues Quadrat mit runden Ecken, darauf ein Oszilloskop-Raster,
# eine weisse Sinuskurve und ein oranger Messpunkt (wie die Messpunkte M1, M2 in den Schaltungen).
#
# Wird NICHT in die EXE gepackt (Ordner "werkzeuge" ist in SystemLab.spec ausgeschlossen).
# WER RUFT DAS AUF?  niemand - nur von Hand, wenn sich das Logo ändern soll
# =============================================================================

import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config                                                          # -> config.py

GROESSE = 1024          # gross zeichnen, dann verkleinern -> glatte Kanten
BLAU_OBEN, BLAU_UNTEN = (59, 130, 246), (15, 27, 51)
RASTER = (255, 255, 255, 38)
WEISS = (255, 255, 255, 255)
ORANGE = (245, 158, 11, 255)


def logo_zeichnen(n=GROESSE):
    bild = Image.new("RGBA", (n, n), (0, 0, 0, 0))

    # ---- Hintergrund: senkrechter Farbverlauf, dann mit runder Maske ausschneiden ----
    verlauf = Image.new("RGBA", (n, n))
    zeichner = ImageDraw.Draw(verlauf)
    for y in range(n):
        a = y / (n - 1)
        farbe = tuple(round(o + (u - o) * a) for o, u in zip(BLAU_OBEN, BLAU_UNTEN)) + (255,)
        zeichner.line([(0, y), (n, y)], fill=farbe)
    maske = Image.new("L", (n, n), 0)
    ImageDraw.Draw(maske).rounded_rectangle([0, 0, n - 1, n - 1], radius=int(n * 0.22), fill=255)
    bild.paste(verlauf, (0, 0), maske)

    d = ImageDraw.Draw(bild)
    rand = n * 0.16
    # ---- Oszilloskop-Raster ----
    for k in range(1, 4):
        x = rand + (n - 2 * rand) * k / 4
        d.line([(x, rand), (x, n - rand)], fill=RASTER, width=max(2, n // 170))
        y = rand + (n - 2 * rand) * k / 4
        d.line([(rand, y), (n - rand, y)], fill=RASTER, width=max(2, n // 170))

    # ---- Sinuskurve (eine volle Periode) ----
    # Dicke Linien mit Pillow fransen aus -> stattdessen viele dicht gesetzte Kreise ("Stempel")
    punkte = []
    for i in range(1601):
        x = rand + (n - 2 * rand) * i / 1600
        y = n / 2 - (n * 0.24) * math.sin(2 * math.pi * i / 1600)
        punkte.append((x, y))
    r = n * 0.035
    for x, y in punkte:
        d.ellipse([x - r, y - r, x + r, y + r], fill=WEISS)

    # ---- Messpunkt auf dem Scheitel ----
    x, y = punkte[400]
    r = n * 0.075
    d.ellipse([x - r, y - r, x + r, y + r], fill=ORANGE, outline=WEISS, width=int(n * 0.022))
    return bild


def main():
    gross = logo_zeichnen()
    png = gross.resize((256, 256), Image.LANCZOS)
    os.makedirs(os.path.dirname(config.APP_LOGO), exist_ok=True)
    png.save(config.APP_LOGO)
    png.save(config.APP_ICON, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("gespeichert:", config.APP_LOGO)
    print("gespeichert:", config.APP_ICON)


if __name__ == "__main__":
    main()
