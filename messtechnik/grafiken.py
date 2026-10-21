# =============================================================================
# messtechnik/grafiken.py
# -----------------------------------------------------------------------------
# INTERAKTIVE GRAFIK: Abtasttheorem und Aliasing - MODELL OHNE FENSTER (Desktop-App UND Web).
#
#   blau    = echtes Signal (Sinus mit Frequenz f)
#   Punkte  = Abtastwerte (alle 1/fs Sekunden)
#   orange  = was der AD-Wandler "sieht" (die Rekonstruktion aus den Punkten)
#
# Ist fs > 2·f, passt die orange Kurve zum echten Signal. Sonst entsteht eine
# FALSCHE, tiefere Frequenz (Alias) – genau das verhindert ein Anti-Aliasing-Filter.
#
# Die Alias-Frequenz rechnet schaltungen/rc_mathe.py alias_frequenz() (mit Vorzeichen).
# WER RUFT DAS AUF?  messtechnik/rechner.py ("abtastung") über GrafikVerweis
# =============================================================================

import math

import config                                                            # -> config.py
from bauteile.einheiten import formatieren                               # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import SchaltungsModell, farbe_waehlen  # -> bauteile/grafiken/schaltplan.py
from schaltungen.rc_mathe import alias_frequenz                          # -> schaltungen/rc_mathe.py

BLAU, ORANGE, GRUEN, ROT = "#3B82F6", "#F59E0B", "#22C55E", "#EF4444"
MAX_PUNKTE = 4000                        # Kurve höchstens so fein (sehr hohe Frequenzen -> sonst riesig)
MAX_ABTASTWERTE = 400                    # Abtastpunkte höchstens so viele zeichnen


class AbtastGrafik(SchaltungsModell):
    TITEL = "📉 Abtasttheorem & Aliasing (interaktiv)"
    UNTERTITEL = "Signalfrequenz erhöhen: ab fs/2 sieht der Wandler eine falsche Frequenz"
    REGLER = [("f", "Signalfrequenz f", "frequenz", 1.0, 45.0, 3.0, {"einheit": "Hz", "grenzen": (0.1, 200), "schritte": 88}),
              ("fs", "Abtastrate fs", "frequenz", 4.0, 60.0, 20.0, {"einheit": "Hz", "grenzen": (1, 400), "schritte": 112})]
    SEITENVERHAELTNIS = 0.42
    MAX_HOEHE = 340
    ERKLAERUNG = ("Was zeigt die Grafik?  Der AD-Wandler kennt nur die grünen Abtastwerte. Liegt die Signalfrequenz "
                  "unter der halben Abtastrate (Nyquist-Frequenz fs/2), lässt sich das Signal eindeutig rekonstruieren. "
                  "Darüber passen die Punkte auch zu einer tieferen Frequenz – der Wandler sieht dann ein falsches "
                  "Signal (Alias). Darum steht vor jedem AD-Wandler ein Tiefpass (Anti-Aliasing-Filter).")

    def sk_rechnen(self, w, v):
        f, fs = w["f"], w["fs"]
        if f <= 0 or fs <= 0:
            raise ValueError("Frequenzen müssen grösser als 0 sein")
        dauer = 1.0 if fs <= MAX_ABTASTWERTE else MAX_ABTASTWERTE / fs     # sonst nur ein Ausschnitt
        return {"f": f, "fs": fs, "fa": alias_frequenz(f, fs), "dauer": dauer}

    def sk_info(self, w, e, v):
        f, fs, fa = e["f"], e["fs"], abs(e["fa"])
        zeilen = [f"Nyquist-Frequenz fs/2 = {formatieren(fs / 2, 'frequenz')}   ·   Signal f = {formatieren(f, 'frequenz')}"]
        if f < fs / 2 - 1e-9:
            zeilen.append(f"✅ f < fs/2 → korrekt erfasst ({fs / f:.1f} Abtastwerte pro Periode)")
            return zeilen, config.FARBEN["akzent"]
        if abs(f - fs / 2) < 1e-9:
            zeilen.append("⚠ Genau fs/2: je nach Phase sieht man die volle Amplitude – oder nur Nullen")
            return zeilen, ("#B45309", ORANGE)
        zeilen.append(f"❌ ALIASING: Der Wandler sieht {formatieren(fa, 'frequenz')} statt {formatieren(f, 'frequenz')}!")
        return zeilen, ("#B91C1C", ROT)

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        f, fs, fa, dauer = e["f"], e["fs"], e["fa"], e["dauer"]
        text = farbe_waehlen(config.FARBEN["text_leise"], p.dunkel)
        linie = farbe_waehlen(config.FARBEN["rahmen"], p.dunkel)
        schrift = (config.SCHRIFT, max(8, int(h / 24)))
        links, rechts, oben, unten = 0.07 * wb, 0.98 * wb, 0.10 * h, 0.86 * h

        def x(t):
            return links + (rechts - links) * t / dauer

        def y(wert):
            return (oben + unten) / 2 - (unten - oben) / 2 * 0.9 * wert

        c.create_line(links, y(0), rechts, y(0), fill=linie)
        for k in range(1, 10):
            c.create_line(x(dauer * k / 10), oben, x(dauer * k / 10), unten, fill=linie, dash=(2, 4))
        for k in range(0, 11, 2):
            c.create_text(x(dauer * k / 10), unten + 0.07 * h, text="0" if k == 0 else formatieren(dauer * k / 10, "zeit", 3),
                          fill=text, font=schrift, anchor="w" if k == 0 else "e" if k == 10 else "center")
        for wert, beschriftung in ((1, "+û"), (0, "0"), (-1, "−û")):    # Amplitude (Scheitelwert û)
            c.create_text(links - 4, y(wert), text=beschriftung, anchor="e", fill=text, font=schrift)

        schritte = min(MAX_PUNKTE, max(200, int(f * dauer * 40)))         # echtes Signal
        c.create_line(*[k for i in range(schritte + 1)
                        for k in (x(dauer * i / schritte), y(math.sin(2 * math.pi * f * dauer * i / schritte)))],
                      fill=BLAU, width=2)
        c.create_line(*[k for i in range(401)                              # Rekonstruktion
                        for k in (x(dauer * i / 400), y(math.sin(2 * math.pi * fa * dauer * i / 400)))],
                      fill=ORANGE, width=3, dash=(8, 4))
        for k in range(int(dauer * fs) + 1):                                # Abtastpunkte
            t = k / fs
            px, py = x(t), y(math.sin(2 * math.pi * f * t))
            c.create_line(px, y(0), px, py, fill=GRUEN)
            c.create_oval(px - 4, py - 4, px + 4, py + 4, fill=GRUEN, outline="")
        c.create_text(links + 4, oben - 0.05 * h, anchor="w", fill=BLAU, font=schrift, text="— echtes Signal")
        c.create_text(links + 0.2 * wb, oben - 0.05 * h, anchor="w", fill=GRUEN, font=schrift, text="● Abtastwerte")
        c.create_text(links + 0.4 * wb, oben - 0.05 * h, anchor="w", fill=ORANGE, font=schrift,
                      text="- - was der Wandler sieht")
