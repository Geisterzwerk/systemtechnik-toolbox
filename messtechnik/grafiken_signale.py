# =============================================================================
# messtechnik/grafiken_signale.py
# -----------------------------------------------------------------------------
# INTERAKTIVE GRAFIKEN DER MESSTECHNIK-GRUNDLAGEN - als SchaltungsModell, also OHNE tkinter:
# dieselbe Klasse läuft im Fenster (schaltung_karte.py) und im Web (svg_canvas.py).
#
#   FourierSynthese   Rechteck, Dreieck, Sägezahn aus Sinusschwingungen aufbauen + Spektrum
#   MesskettePt100    Messkette Temperatur -> Pt100 -> Brücke -> Messumformer 4…20 mA -> Anzeiger
#   Messreihe         Messwerte mit systematischer und zufälliger Abweichung, Histogramm (Glockenkurve)
#
# Rechnung: messtechnik/signal_mathe.py, messtechnik/grundlagen_mathe.py
# Zeichenwerkzeug: bauteile/grafiken/schaltplan.py (Schaltplan p, Raster-Einheiten)
#
# WER RUFT DAS AUF?  messtechnik/rechner.py (RECHNER, als GrafikVerweis), Wissensseiten in
#                    messtechnik/inhalte/01_grundlagen/ ("grafiken": [...])
# =============================================================================

import math

import config                                                                # -> config.py
from bauteile.einheiten import formatieren as fmt                            # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import (BLAU, GRUEN, MESSPUNKT, ORANGE,    # -> bauteile/grafiken/schaltplan.py
                                          ROT, SPANNUNG, STROM, WARN, SchaltungsModell)
from bauteile.grafiken.skala import schoene_grenze                           # -> bauteile/grafiken/skala.py
from messtechnik import grundlagen_mathe as gm                               # -> messtechnik/grundlagen_mathe.py
from messtechnik import signal_mathe as sm                                   # -> messtechnik/signal_mathe.py

# Farben der einzelnen Sinus-Glieder (kehren nach 6 wieder)
GLIED_FARBEN = [ORANGE, GRUEN, ROT, "#A855F7", "#14B8A6", "#EC4899"]


def _u(wert):
    return fmt(wert, "spannung", 3)


# =============================================================================
# FOURIER-SYNTHESE
# =============================================================================
class FourierSynthese(SchaltungsModell):
    TITEL = "〰 Signalformen aus Sinus zusammensetzen (interaktiv)"
    UNTERTITEL = "Fourier-Synthese: Grundschwingung + Oberschwingungen = Rechteck, Dreieck oder Sägezahn"
    VARIANTEN = sm.FORMEN
    SCHALTER = [("einzeln", "einzelne Sinus zeigen")]
    REGLER = [("n", "Anzahl Sinus-Glieder", "zahl", 1.0, 25.0, 3.0, {"ganzzahl": True, "grenzen": (1, 100)}),
              ("u", "Scheitelwert Û", "spannung", 0.01, 100.0, 1.0, {"einheit": "V", "log": True,
                                                                      "grenzen": (1e-3, 1000)}),
              ("f", "Grundfrequenz f", "frequenz", 1.0, 100e3, 50.0, {"einheit": "Hz", "log": True,
                                                                       "grenzen": (0.01, 1e9)})]
    RASTER = (24, 15)
    SEITENVERHAELTNIS = 0.62
    MAX_HOEHE = 520
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Oben die Summe der Sinus-Glieder (blau) und die ideale Kurvenform (gestrichelt), "
        "mit „einzelne Sinus zeigen“ auch jedes Glied für sich. Unten das Spektrum: Jeder Balken ist ein Glied, "
        "seine Höhe die Amplitude, seine Lage die Frequenz (k · f). RECHTECK: nur ungerade Oberschwingungen "
        "(3f, 5f, 7f …), Amplitude 1/k – an den Sprüngen bleibt immer ein Überschwinger von rund 9 % der "
        "Sprunghöhe (Gibbs-Phänomen). DREIECK: ebenfalls nur ungerade, aber Amplitude 1/k² – schon wenige Glieder "
        "genügen. SÄGEZAHN: alle Oberschwingungen (2f, 3f, 4f …), Amplitude 1/k. Je steiler eine Flanke, desto "
        "mehr hohe Frequenzen braucht das Signal – darum braucht ein Oszilloskop genug Bandbreite.")

    def sk_rechnen(self, w, v):
        n = int(round(w["n"]))
        glieder = [(k, a * w["u"]) for k, a in sm.glieder(v, n)]
        # Spitze der Summe über eine Periode (für die Skala und den Gibbs-Hinweis)
        werte = [sum(a * math.sin(k * 2 * math.pi * i / 600) for k, a in glieder) for i in range(600)]
        return {"n": n, "glieder": glieder, "spitze": max(abs(x) for x in werte)}

    def sk_zeichnen(self, p, w, e, v):
        u, f = w["u"], w["f"]
        grenze = schoene_grenze(max(e["spitze"], u) * 1.05)
        # ---- oben: Zeitverlauf über 2 Perioden ----
        schritte = 400
        def kurve(funktion):
            return [(i / schritte, funktion(4 * math.pi * i / schritte)) for i in range(schritte + 1)]
        kurven = [(kurve(lambda x: u * sm.ideal(v, x)), p.leise, 1, True)]
        if w.get("einzeln"):
            for nummer, (k, a) in enumerate(e["glieder"][:6]):
                kurven.append((kurve(lambda x, k=k, a=a: a * math.sin(k * x)), GLIED_FARBEN[nummer], 1, False))
        kurven.append((kurve(lambda x: sum(a * math.sin(k * x) for k, a in e["glieder"])), SPANNUNG,
                       p.dick + 1, False))
        p.diagramm(2.4, 1.2, 23.4, 8.6, kurven, -grenze, grenze,
                   titel=f"{v} aus {e['n']} Sinus-{'Glied' if e['n'] == 1 else 'Gliedern'}  (gestrichelt: ideal)",
                   einheit="spannung", t_ende=2 / f)
        # ---- unten: Spektrum ----
        self._spektrum(p, e, f, u)

    def _spektrum(self, p, e, f, u):
        x0, x1, y0, y1 = 2.4, 23.4, 10.6, 13.6
        k_max = max(k for k, _a in e["glieder"])
        anzahl = max(k_max, 5)
        breite = (x1 - x0) / anzahl
        (a, b), (c, d) = p.p(x0, y0), p.p(x1, y1)
        p.c.create_line(a, d, c, d, fill=p.leise, width=1)
        p.text((x0 + x1) / 2, y0 - 0.45, "Spektrum: Amplitude jedes Sinus-Glieds über der Frequenz",
               "center", klein=True, farbe=p.leise)
        p.text(x0 - 0.12, y0, _u(u * 4 / math.pi if u else 0), "e", klein=True, farbe=p.leise)
        bezug = 4 / math.pi * u                                 # grösste mögliche Amplitude (Rechteck k=1)
        beschriften = anzahl <= 13
        for k, amp in e["glieder"]:
            xm = x0 + (k - 0.5) * breite
            hoehe = abs(amp) / bezug * (y1 - y0) if bezug else 0
            (px0, py0), (px1, py1) = p.p(xm - breite * 0.3, y1 - hoehe), p.p(xm + breite * 0.3, y1)
            p.c.create_rectangle(px0, py0, px1, py1, fill=SPANNUNG, outline="")
            if beschriften or k == 1:
                p.text(xm, y1 + 0.42, f"{k}f", "center", klein=True, farbe=p.leise)
        p.text(x1, y1 + 0.95, f"f = {fmt(f, 'frequenz', 3)}  →  Frequenz", "e", klein=True, farbe=p.leise)

    def sk_info(self, w, e, v):
        f = w["f"]
        teile = [f"{k}f = {fmt(k * f, 'frequenz', 3)}: {_u(abs(a))}" for k, a in e["glieder"][:5]]
        zeilen = [f"{v} mit Û = {_u(w['u'])}, f = {fmt(f, 'frequenz', 3)}  ·  Glieder: " + "  ·  ".join(teile)
                  + ("  …" if len(e["glieder"]) > 5 else "")]
        if v == "Rechteck":
            zeilen.append(f"Spitze der Summe: {_u(e['spitze'])} = {e['spitze'] / w['u']:.3f} · Û  "
                          "(Gibbs-Phänomen: der Überschwinger an den Sprüngen bleibt bei ≈ 9 % der Sprunghöhe)")
        elif v == "Dreieck":
            zeilen.append("Amplituden fallen mit 1/k² – nach 3 Gliedern ist die Form schon fast perfekt")
        else:
            zeilen.append("Alle Oberschwingungen kommen vor (gerade und ungerade), Amplitude 1/k")
        return zeilen, config.FARBEN["akzent"]


# =============================================================================
# MESSKETTE PT100 -> 4 … 20 mA
# =============================================================================
class MesskettePt100(SchaltungsModell):
    TITEL = "🔗 Messkette Temperatur → 4…20 mA (interaktiv)"
    UNTERTITEL = "Aufnehmer, Messumformer, Ausgeber: Welcher Wert steht an welcher Stelle der Kette?"
    SCHALTER = [("linear", "Messumformer linearisiert die Pt100-Kennlinie")]
    REGLER = [("t", "Temperatur am Messort", "temperatur", 0.0, 250.0, 125.0, {"grenzen": (0, 250)})]
    RASTER = (24, 12.5)
    SEITENVERHAELTNIS = 0.52
    MAX_HOEHE = 440
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Eine Messkette nach DIN 1319: Der AUFNEHMER (Pt100) setzt die Temperatur in einen "
        "Widerstand um, die Messbrücke den Widerstand in eine kleine Spannung, der MESSUMFORMER diese in das "
        "Einheitssignal 4 … 20 mA, und der AUSGEBER (Anzeiger) zeigt wieder °C an. Brücke und Messumformer brauchen "
        "HILFSENERGIE. Der Pt100 ist leicht gekrümmt (quadratische Kennlinie nach IEC 60751): Ohne Linearisierung "
        "zeigt die lineare Skala in der Mitte bis zu rund 2.4 K zu viel – eine systematische Messabweichung. "
        "Echte Messumformer linearisieren deshalb. Beispielwerte nach dem Artikel „Messeinrichtung“ (Wikipedia), "
        "Brücke vereinfacht als linear im Widerstand.")

    def sk_rechnen(self, w, v):
        return gm.kette(w["t"], bool(w.get("linear")))

    def sk_zeichnen(self, p, w, e, v):
        # ---- fünf Glieder in einer Reihe ----
        y_o, y_u = 2.6, 5.8
        ym = (y_o + y_u) / 2
        kaesten = [(0.4, "Messobjekt", "Rohr / Ofen"), (5.1, "Pt100", "Aufnehmer"),
                   (9.8, "Messbrücke", "Messumformer"), (14.5, "Messumformer", "4 … 20 mA"),
                   (19.2, "Anzeiger", "Ausgeber")]
        breite = 4.0
        for x, titel, rolle in kaesten:
            p.kasten(x, y_o, x + breite, y_u, titel)
            p.text(x + breite / 2, y_o + 1.35, rolle, "center", klein=True, farbe=p.leise)
        werte = [(f"ϑ = {fmt(e['t'], 'temperatur', 4)}", ROT),
                 (f"R = {fmt(e['r'], 'widerstand', 5)}", ORANGE),
                 (f"U = {fmt(e['u'], 'spannung', 3)}", SPANNUNG),
                 (f"I = {fmt(e['i'], 'strom', 4)}", STROM)]
        for (x, _t, _r), (text, farbe) in zip(kaesten, werte):
            xa, xb = x + breite, x + breite + 0.7
            (a, b), (c, d) = p.p(xa, ym), p.p(xb, ym)
            p.c.create_line(a, b, c, d, fill=farbe, width=p.dick + 1, arrow="last",
                            arrowshape=(p.u * 0.3, p.u * 0.34, p.u * 0.13))
        # Werte im unteren Teil der Kästen (zwischen den Kästen ist zu wenig Platz)
        for (x, _t, _r), (text, farbe) in zip(kaesten, werte):
            p.text(x + breite / 2, y_u - 0.6, text, "center", fett=True, farbe=farbe)
        p.text(19.2 + breite / 2, y_u - 0.6, f"{fmt(e['anzeige'], 'temperatur', 4)}", "center", fett=True,
               farbe=GRUEN)
        # ---- Hilfsenergie ----
        for x in (9.8, 14.5):
            (a, b), (c, d) = p.p(x + breite / 2, 0.9), p.p(x + breite / 2, y_o)
            p.c.create_line(a, b, c, d, fill=p.leise, width=1, dash=(4, 3), arrow="last",
                            arrowshape=(p.u * 0.25, p.u * 0.28, p.u * 0.1))
        p.text(14.5 - 0.35, 0.75, "Hilfsenergie (z.B. 24 V DC)", "center", klein=True, farbe=p.leise)
        # ---- Skala des Anzeigers: wahrer Wert und Anzeige ----
        x0, x1, ys = 2.0, 22.0, 9.2
        p.text(x0, ys - 1.35, "Skala des Anzeigers", "w", klein=True, farbe=p.leise)
        (a, b), (c, d) = p.p(x0, ys), p.p(x1, ys)
        p.c.create_line(a, b, c, d, fill=p.linie, width=p.dick)
        for grad in range(0, 251, 50):
            xs = x0 + (x1 - x0) * grad / 250
            (a, b), (c, d) = p.p(xs, ys - 0.25), p.p(xs, ys + 0.25)
            p.c.create_line(a, b, c, d, fill=p.linie, width=1)
            p.text(xs, ys + 0.75, f"{grad} °C", "center", klein=True, farbe=p.leise)
        for wert, farbe, oben, text in ((e["t"], ROT, False, "wahr"), (e["anzeige"], GRUEN, True, "Anzeige")):
            xs = x0 + (x1 - x0) * wert / 250
            y_spitze, y_ende = (ys - 0.15, ys - 1.0) if oben else (ys + 0.15, ys + 1.0)
            (a, b), (c, d) = p.p(xs, y_ende), p.p(xs, y_spitze)
            p.c.create_line(a, b, c, d, fill=farbe, width=p.dick + 1, arrow="last",
                            arrowshape=(p.u * 0.25, p.u * 0.28, p.u * 0.12))
            p.text(xs, y_ende - 0.35 if oben else y_ende + 0.4, text, "center", klein=True, farbe=farbe)
        abw = e["abweichung"]
        farbe = WARN[1] if abs(abw) >= 0.05 else GRUEN
        p.text(12.0, 11.9, f"Abweichung der Anzeige: {abw:+.2f} K", "center", fett=True, farbe=farbe)

    def sk_info(self, w, e, v):
        zeilen = [f"ϑ = {fmt(e['t'], 'temperatur', 4)}  →  R = {fmt(e['r'], 'widerstand', 5)}  →  "
                  f"U = {fmt(e['u'], 'spannung', 3)}  →  I = {fmt(e['i'], 'strom', 4)}  →  "
                  f"Anzeige {fmt(e['anzeige'], 'temperatur', 4)}"]
        if w.get("linear"):
            zeilen.append("Linearisiert: Der Messumformer rechnet die Pt100-Kennlinie zurück – keine Abweichung "
                          "durch die Kennlinie")
            return zeilen, config.FARBEN["akzent"]
        zeilen.append(f"Ohne Linearisierung: systematische Abweichung {e['abweichung']:+.2f} K "
                      "(Pt100-Kennlinie ist gekrümmt, die Skala aber linear)")
        return zeilen, WARN if abs(e["abweichung"]) >= 0.05 else config.FARBEN["akzent"]


# =============================================================================
# MESSREIHE: systematische und zufällige Abweichung
# =============================================================================
class Messreihe(SchaltungsModell):
    WAHR = 5.0                       # V: Referenzspannung (richtiger Wert)
    TITEL = "🎯 Messreihe: systematische und zufällige Abweichung (interaktiv)"
    UNTERTITEL = "Eine Referenzspannung von genau 5.000 V wird mehrmals gemessen"
    SCHALTER = [("ausreisser", "grober Fehler (ein Wert falsch abgelesen)")]
    REGLER = [("syst", "systematische Abweichung", "spannung", -0.1, 0.1, 0.03, {"einheit": "mV",
                                                                                 "grenzen": (-1, 1)}),
              ("s", "Streuung s (zufällig)", "spannung", 0.0, 0.1, 0.02, {"einheit": "mV", "grenzen": (0, 1)}),
              ("n", "Anzahl Messungen n", "zahl", 3.0, 200.0, 30.0, {"ganzzahl": True, "grenzen": (2, 1000)})]
    RASTER = (24, 12.5)
    SEITENVERHAELTNIS = 0.52
    MAX_HOEHE = 440
    ERKLAERUNG = (
        "Was zeigt die Grafik?  Links jede einzelne Messung (Punkte) mit dem richtigen Wert 5.000 V (grün "
        "gestrichelt) und dem Mittelwert (blau). Rechts, wie oft welcher Wert vorkam (Histogramm) – bei zufälligen "
        "Abweichungen entsteht eine Glockenkurve (Normalverteilung). SYSTEMATISCHE Abweichung verschiebt alle Werte "
        "gleich – mehr Messungen helfen nicht, man muss sie kennen und korrigieren (Kalibrierung). ZUFÄLLIGE "
        "Abweichung lässt die Werte streuen – der Mittelwert vieler Messungen wird genauer (s/√n). Ein GROBER "
        "FEHLER (Ausreisser) verfälscht Mittelwert und Streuung – ihn erkennt man und lässt ihn mit Begründung weg.")

    def sk_rechnen(self, w, v):
        n = int(round(w["n"]))
        werte = gm.messreihe(self.WAHR, w["syst"], w["s"], n, bool(w.get("ausreisser")))
        return {"werte": werte, **gm.auswerten(werte)}

    def sk_zeichnen(self, p, w, e, v):
        werte, wahr, s = e["werte"], self.WAHR, e["s"]
        spanne = max(max(abs(x - wahr) for x in werte), abs(e["mittel"] - wahr) + 2 * s, 0.01) * 1.15
        y_min, y_max = wahr - spanne, wahr + spanne
        # ---- links: Messwerte über der Nummer der Messung ----
        x0, x1, y0, y1 = 3.2, 15.4, 1.2, 10.4
        n = len(werte)
        def pixel(i, wert):
            return p.p(x0 + (x1 - x0) * (i + 0.5) / n, y1 - (wert - y_min) / (y_max - y_min) * (y1 - y0))
        (a, b), (c, d) = p.p(x0, y0), p.p(x1, y1)
        p.c.create_line(a, b, a, d, fill=p.leise, width=1)
        p.c.create_line(a, d, c, d, fill=p.leise, width=1)
        for wert, farbe, gestrichelt in ((wahr, GRUEN, True), (e["mittel"], BLAU, False)):
            _, py = pixel(0, wert)
            if gestrichelt:
                p.c.create_line(a, py, c, py, fill=farbe, width=2, dash=(6, 4))
            else:
                p.c.create_line(a, py, c, py, fill=farbe, width=2)
        for wert in (y_max, wahr, y_min):
            _, py = pixel(0, wert)
            p.text(x0 - 0.12, (py - p.y0) / p.u, fmt(wert, "spannung", 4), "e", klein=True, farbe=p.leise)
        r = max(2.0, min(p.u * 0.14, 280 / max(n, 1) * p.u / 40))
        for i, wert in enumerate(werte):
            px, py = pixel(i, wert)
            grob = abs(wert - e["mittel"]) > 3 * s and s > 0 and w.get("ausreisser")
            p.c.create_oval(px - r, py - r, px + r, py + r, fill=ROT if grob else SPANNUNG, outline="")
        p.text((x0 + x1) / 2, y0 - 0.45, f"{n} Messungen (Punkte) · grün: richtiger Wert · blau: Mittelwert",
               "center", klein=True, farbe=p.leise)
        p.text(x1, y1 + 0.45, "Nummer der Messung →", "e", klein=True, farbe=p.leise)
        # ---- rechts: Histogramm (gleiche Höhenachse) ----
        hx0, hx1 = 16.6, 23.2
        klassen = 12
        zaehler = [0] * klassen
        for wert in werte:
            k = min(klassen - 1, max(0, int((wert - y_min) / (y_max - y_min) * klassen)))
            zaehler[k] += 1
        groesste = max(zaehler) or 1
        for k, anzahl in enumerate(zaehler):
            if not anzahl:
                continue
            unten = y1 - k / klassen * (y1 - y0)
            oben = y1 - (k + 1) / klassen * (y1 - y0)
            (a, b), (c, d) = p.p(hx0, oben + 0.05), p.p(hx0 + (hx1 - hx0) * anzahl / groesste, unten - 0.05)
            p.c.create_rectangle(a, b, c, d, fill=SPANNUNG, outline="")
        if s > 0:                                              # Glockenkurve mit Mittelwert und s
            punkte = []
            breite_klasse = (y_max - y_min) / klassen
            for i in range(61):
                wert = y_min + (y_max - y_min) * i / 60
                dichte = n * breite_klasse / (s * math.sqrt(2 * math.pi)) * math.exp(-0.5 * ((wert - e["mittel"]) / s) ** 2)
                punkte += list(p.p(hx0 + (hx1 - hx0) * min(dichte / groesste, 1.3), y1 - (wert - y_min) / (y_max - y_min) * (y1 - y0)))
            p.c.create_line(*punkte, fill=MESSPUNKT, width=2)
        (a, b), (c, d) = p.p(hx0, y0), p.p(hx0, y1)
        p.c.create_line(a, b, c, d, fill=p.leise, width=1)
        p.text((hx0 + hx1) / 2, y0 - 0.45, "Häufigkeit · orange: Glockenkurve", "center", klein=True,
               farbe=p.leise)
        p.text(hx1, y1 + 0.45, "Anzahl →", "e", klein=True, farbe=p.leise)

    def sk_info(self, w, e, v):
        abw = e["mittel"] - self.WAHR
        zeilen = [f"Mittelwert = {fmt(e['mittel'], 'spannung', 5)}  ·  Abweichung vom richtigen Wert = "
                  f"{fmt(abw, 'spannung', 3)} ({abw / self.WAHR * 100:+.2f} %)",
                  f"Streuung s = {fmt(e['s'], 'spannung', 3)}  ·  Unsicherheit des Mittelwerts s/√n = "
                  f"{fmt(e['s_mittel'], 'spannung', 3)}  (n = {e['n']})"]
        if w.get("ausreisser"):
            zeilen.append("⚠ Ein Wert liegt weit daneben (rot, > 3·s vom Mittelwert): grober Fehler – Ursache "
                          "suchen, Wert begründet streichen. Er verfälscht hier Mittelwert und s.")
            return zeilen, WARN
        return zeilen, config.FARBEN["akzent"]
