# =============================================================================
# digitaltechnik/grafiken_schaltwerke.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE der Schaltwerke (mit Speicher und Takt) - MODELLE OHNE FENSTER (Desktop-App UND Web):
#
#   FlipflopKarte          RS-Latch, D-Latch, D-, JK-, T-Flipflop: Eingänge als FOLGE je Takt eintippen
#                          (z.B. D = 0110 1001) -> Zeitdiagramm, Endzustand
#   ZaehlerKarte           asynchroner und synchroner Zähler (auf/ab, modulo m), Zwischenzustände sichtbar
#   SchieberegisterKarte   seriell (SIPO), Ringzähler, Johnson-Zähler - Folge der Eingänge bzw. Anzahl Takte
#
#   zeitdiagramm()         zeichnet digitale Signale untereinander (Treppenkurven), auch mit feiner Zeitachse
#
# Warum Folgen statt "Takt-Knopf"? Ein Modell hat keinen gespeicherten Zustand (die Webseite merkt sich nichts
# zwischen zwei Aufrufen). Mit einer Folge sieht man ausserdem den ganzen Verlauf auf einmal und kann ihn ändern.
#
# Rechnung: digitaltechnik/schaltwerke_mathe.py
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_flipflop")
# =============================================================================

import re

import config                                                            # -> config.py
from bauteile.grafiken.schaltplan import OK, WARN, SchaltungsModell      # -> bauteile/grafiken/schaltplan.py
from digitaltechnik import schaltwerke_mathe as swm                      # -> digitaltechnik/schaltwerke_mathe.py
from digitaltechnik.grafiken import bitreihe, farben                     # -> digitaltechnik/grafiken.py

EINS, NULL_FARBE, ORANGE, ROT, BLAU = "#22C55E", "#6B7280", "#F59E0B", "#EF4444", "#3B82F6"
SIGNAL_FARBEN = {"CLK": "#A855F7", "C": "#A855F7", "Q": EINS}
MAX_SCHRITTE = 16


def folge(text, name, laenge=None):
    """'0110 1001' -> [0, 1, 1, 0, 1, 0, 0, 1]  (nur 0/1, Leerzeichen und Kommas egal, höchstens MAX_SCHRITTE)."""
    t = re.sub(r"[\s,;_']", "", str(text or ""))
    if t and set(t) - {"0", "1"}:
        raise ValueError(f"{name}: nur 0 und 1 eintippen (je Takt ein Zeichen), z.B. 0110 1001")
    werte = [int(z) for z in t][:MAX_SCHRITTE]
    if laenge is not None:                                          # kürzere Folge: letzter Wert bleibt stehen
        werte = (werte + [werte[-1] if werte else 0] * laenge)[:laenge]
    return werte


def zeitdiagramm(c, x0, x1, y0, y1, signale, schrift, leise, markierungen=()):
    """
    signale: [(name, [werte …], farbe), …] – alle Listen gleich lang, ein Wert je Zeitschritt
             (0/1, None = unbestimmt X, "Z" = hochohmig).
    markierungen: [(schritt, farbe), …] senkrechte Hilfslinien (z.B. Taktflanken, Glitches).
    """
    if not signale or not signale[0][1]:
        return
    n = len(signale[0][1])
    zeile = (y1 - y0) / len(signale)
    dx = (x1 - x0) / n
    for schritt, farbe in markierungen:
        c.create_line(x0 + schritt * dx, y0, x0 + schritt * dx, y1, fill=farbe, dash=(2, 3))
    for k, (name, werte, farbe) in enumerate(signale):
        oben, unten = y0 + k * zeile + zeile * 0.18, y0 + (k + 1) * zeile - zeile * 0.18
        c.create_text(x0 - 6, (oben + unten) / 2, text=name, anchor="e", fill=farbe, font=schrift)
        c.create_line(x0, unten, x1, unten, fill=leise, dash=(1, 4))
        punkte = []
        for i, w in enumerate(werte):
            y = unten if not w else oben
            if w == "Z":                                           # hochohmig (Leitung frei): Mitte
                y = (oben + unten) / 2
            elif w is None:                                        # unbestimmt: Mitte, Kasten rot gestrichelt
                c.create_rectangle(x0 + i * dx, oben, x0 + (i + 1) * dx, unten, outline=ROT, dash=(2, 2))
                y = (oben + unten) / 2
            punkte += [x0 + i * dx, y, x0 + (i + 1) * dx, y]
        c.create_line(*punkte, fill=farbe, width=2)


# =============================================================================
# FLIPFLOPS
# =============================================================================
class FlipflopKarte(SchaltungsModell):
    TITEL = "⏱️ Flipflops und Latches (interaktiv)"
    UNTERTITEL = "Eingänge als Folge eintippen (ein Zeichen je Takt) – das Zeitdiagramm zeigt, was passiert"
    EINGAENGE = {"RS-Latch": ["S", "R"], "D-Latch": ["D", "C"], "D-Flipflop": ["D"], "JK-Flipflop": ["J", "K"],
                 "T-Flipflop": ["T"]}
    VARIANTEN = ["D-Flipflop", "JK-Flipflop", "T-Flipflop", "D-Latch", "RS-Latch"]
    TEXTFELDER = [("e1", "1. Eingang (D, J, T, S)", "0110 1001", {"max": 24, "platzhalter": "z.B. 0110 1001"}),
                  ("e2", "2. Eingang (K, C, R)", "0011 0011", {"max": 24, "platzhalter": "z.B. 0011 0011"})]
    STARTWERTE = {"D-Flipflop": {"e1": "0110 1001"}, "T-Flipflop": {"e1": "1101 0011"},
                  "JK-Flipflop": {"e1": "1010 1100", "e2": "0110 1010"}, "D-Latch": {"e1": "0110 1001", "e2": "1100 0110"},
                  "RS-Latch": {"e1": "1000 0011", "e2": "0010 0011"}}
    SEITENVERHAELTNIS = 0.4
    MAX_HOEHE = 340
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Ein Flipflop speichert ein Bit. Das RS-LATCH reagiert sofort: S setzt, R setzt "
                  "zurück, S = R = 1 ist verboten. Das D-LATCH ist pegelgesteuert: Solange C = 1, folgt Q dem Eingang D "
                  "(transparent), bei C = 0 hält es den Wert. FLIPFLOPS sind flankengesteuert (Dreieck am Takteingang): "
                  "Sie übernehmen nur im Moment der steigenden Flanke – dazwischen dürfen sich die Eingänge ändern, ohne "
                  "dass etwas passiert. Das D-Flipflop speichert D, das JK kann zusätzlich toggeln (J = K = 1), das "
                  "T-Flipflop toggelt bei T = 1 – zwei T-Flipflops hintereinander teilen die Frequenz durch 4. "
                  "Startzustand Q = 0.")

    def sk_rechnen(self, w, v):
        art = v if v in self.EINGAENGE else "D-Flipflop"
        namen = self.EINGAENGE[art]
        erste = folge(w["e1"], namen[0])
        n = max(len(erste), 1)
        folgen = {namen[0]: folge(w["e1"], namen[0], n)}
        if len(namen) > 1:
            folgen[namen[1]] = folge(w["e2"], namen[1], n)
        flanke = art in ("D-Flipflop", "JK-Flipflop", "T-Flipflop")
        q, verlauf, hinweis = 0, [], "Startzustand Q = 0"
        for k in range(n):
            e = {name: folgen[name][k] for name in namen}
            verboten = art == "RS-Latch" and e.get("S") and e.get("R")
            if flanke:                                                  # Eingänge anlegen, dann Flanke
                verlauf.append({"clk": 0, **e, "q": q, "verboten": False})
                q, hinweis = swm.naechster_zustand(art, q, e)
                verlauf += [{"clk": 1, **e, "q": q, "verboten": False}] * 2
            else:                                                       # Latch reagiert sofort auf den Pegel
                q, hinweis = swm.naechster_zustand(art, q, e)
                verlauf += [{"clk": 0, **e, "q": q, "verboten": bool(verboten)}] * 2
        return {"art": art, "namen": namen, "flanke": flanke, "q": q, "verlauf": verlauf, "hinweis": hinweis,
                "schritte": n, "folge_q": [s["q"] for s in verlauf[(2 if flanke else 1)::3 if flanke else 2]]}

    def sk_info(self, w, e, v):
        art = e["art"]
        verboten = e["verlauf"] and e["verlauf"][-1]["verboten"]
        tabelle = "   ".join(f"{a} → {q}" for a, q in swm.flipflop_tabelle(art))
        return ([f"Nach {e['schritte']} {'Takten' if e['flanke'] else 'Schritten'}: Q = {e['q']}   ·   letzter Schritt: {e['hinweis']}",
                 f"Q nach jedem {'Takt' if e['flanke'] else 'Schritt'}: {' '.join(map(str, e['folge_q']))}",
                 swm.KENN_GLEICHUNG[art], tabelle],
                WARN if verboten else config.FARBEN["akzent"])

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        art, verlauf, flanke = e["art"], e["verlauf"], e["flanke"]
        text, leise, _, _ = farben(p)
        g = max(8, int(min(wb / 2.4, h) / 16))
        schrift, fett = (config.SCHRIFT, g), (config.SCHRIFT, g, "bold")
        dick = max(2, int(h / 120))
        x0, x1, y0, y1 = wb * 0.08, wb * 0.22, h * 0.14, h * 0.86          # Symbol (IEC)
        c.create_rectangle(x0, y0, x1, y1, outline=text, width=dick)
        namen = e["namen"] + (["C1"] if flanke else [])
        letzt = verlauf[-1]
        for i, name in enumerate(namen):
            y = y0 + (y1 - y0) * (i + 1) / (len(namen) + 1)
            wert = letzt.get(name, letzt["clk"])
            c.create_line(x0 - wb * 0.04, y, x0, y, fill=EINS if wert else NULL_FARBE, width=dick)
            c.create_text(x0 + 6, y, text=("1" + name if name in "DJKT" and flanke else name), anchor="w", fill=text,
                          font=schrift)
            if name == "C1":                                                  # Dreieck = flankengesteuert
                c.create_polygon(x0, y - h * 0.035, x0 + wb * 0.012, y, x0, y + h * 0.035, outline=text, fill="", width=dick)
        for i, (name, wert) in enumerate((("Q", e["q"]), ("¬Q", 1 - e["q"]))):
            y = y0 + (y1 - y0) * (i + 1) / 3
            c.create_line(x1, y, x1 + wb * 0.04, y, fill=EINS if wert else NULL_FARBE, width=dick)
            r = max(5, h * 0.035)
            c.create_oval(x1 + wb * 0.04, y - r, x1 + wb * 0.04 + 2 * r, y + r, fill=EINS if wert else NULL_FARBE, outline="")
            c.create_text(x1 - 6, y, text=name, anchor="e", fill=text, font=fett)
        c.create_text((x0 + x1) / 2, y0 - 4, text=art, anchor="s", fill=leise, font=schrift)
        signale = [("CLK", [s["clk"] for s in verlauf], SIGNAL_FARBEN["CLK"])] if flanke else []
        for name in e["namen"]:
            signale.append((name, [s[name] for s in verlauf], SIGNAL_FARBEN.get(name, BLAU)))
        signale.append(("Q", [None if s["verboten"] else s["q"] for s in verlauf], EINS))
        flanken = [(i, "#7C3AED") for i in range(1, len(verlauf)) if verlauf[i]["clk"] and not verlauf[i - 1]["clk"]]
        zeitdiagramm(c, wb * 0.38, wb * 0.96, h * 0.08, h * 0.95, signale, schrift, leise, flanken)


# =============================================================================
# ZÄHLER
# =============================================================================
class ZaehlerKarte(SchaltungsModell):
    TITEL = "🔢 Zähler: asynchron und synchron (interaktiv)"
    UNTERTITEL = "Modulo und Richtung einstellen – beim asynchronen Zähler die Zwischenzustände beachten"
    VARIANTEN = ["asynchron (Ripple)", "synchron"]
    AUSWAHL = [("richtung", "Richtung", ["aufwärts", "abwärts"], "aufwärts")]
    REGLER = [("m", "Modulo m (Zustände)", "zahl", 2.0, 16.0, 10.0, {"ganzzahl": True})]
    UNTER = 24                                     # Zeitschritte je Taktperiode (für die Verzögerungen)
    SEITENVERHAELTNIS = 0.42
    MAX_HOEHE = 360
    ERKLAERUNG = ("Was zeigt das Werkzeug?  ASYNCHRON: Nur das erste Flipflop bekommt den Takt, jedes weitere wird vom "
                  "Ausgang des vorigen getaktet. Einfach, aber die Bits kippen nacheinander – beim Übergang 0111 → 1000 "
                  "erscheinen kurz 0110, 0100 und 0000 (rote Linien). Ein Modulo-Zähler, der beim Erreichen von m "
                  "asynchron zurückgesetzt wird, zeigt m kurz an (Glitch). SYNCHRON: Alle Flipflops hängen am selben "
                  "Takt und schalten gleichzeitig; eine Logik bestimmt, welche toggeln. Q0 hat die halbe Taktfrequenz, "
                  "jedes weitere Bit wieder die Hälfte – ein Zähler ist auch ein Frequenzteiler (höchstes Bit: f / m).")

    def sk_rechnen(self, w, v):
        m = int(round(w["m"]))
        if not 2 <= m <= 16:
            raise ValueError("Modulo m zwischen 2 und 16")
        bits = max(1, (m - 1).bit_length())
        ab = w["richtung"] == "abwärts"
        asyn = v != "synchron"
        perioden = m + 1
        reihe = swm.zaehler_folge(bits, m, ab, schritte=perioden)
        werte, glitches = [], []
        d = max(1, self.UNTER // (3 * bits))                               # Verzögerung je Stufe (asynchron)
        for p in range(perioden):
            alt, neu = (reihe[0], reihe[0]) if p == 0 else (reihe[p - 1], reihe[p])
            if p == 0:
                zwischen = [alt]
            elif asyn and not ab:
                zwischen = swm.ripple_uebergang(alt, bits, m)
            elif asyn:                                                      # abwärts: Bits kippen nacheinander
                zwischen, z = [alt], alt
                for i in range(bits):
                    z ^= 1 << i
                    zwischen.append(z)
                    if not (z >> i) & 1:
                        break
                if zwischen[-1] != neu:
                    zwischen.append(neu)
            else:
                zwischen = [alt, neu]
            for t in range(self.UNTER):
                if asyn:
                    stufe = min(t // d, len(zwischen) - 1) if t >= 1 else 0
                    werte.append(zwischen[stufe])
                    if 0 < stufe < len(zwischen) - 1 and t % d == 0:
                        glitches.append(p * self.UNTER + t)
                else:
                    werte.append(alt if t < 1 else neu)
        return {"m": m, "bits": bits, "folge": reihe[:m + 1], "werte": werte, "glitches": glitches,
                "perioden": perioden, "asyn": asyn, "ab": ab}

    def sk_info(self, w, e, v):
        m, bits = e["m"], e["bits"]
        zeilen = [f"{bits} Flipflops, {m} Zustände: " + ", ".join(map(str, e["folge"][:m])),
                  f"Frequenzen: Q0 = f/2 (bei Zweierpotenz) … höchstes Bit Q{bits - 1}: f / {m}" +
                  ("" if m == 2 ** bits else "  (Tastgrad ≠ 50 %, weil m keine Zweierpotenz ist)")]
        if e["asyn"] and not e["ab"]:
            beispiel = 2 ** (bits - 1) - 1 if 2 ** (bits - 1) < m else m - 1
            kette = swm.ripple_uebergang(beispiel, bits, m)
            zeilen.append("Übergang " + " → ".join(format(z, f"0{bits}b") for z in kette) +
                          f"   ({len(kette) - 2} falsche Zwischenwerte)")
        if e["asyn"] and m != 2 ** bits:
            zeilen.append(f"⚠ Asynchrones Rücksetzen bei {m}: Zustand {m} ist kurz sichtbar (Glitch) – "
                          "für saubere Ausgänge synchron zählen")
        return zeilen, (WARN if e["asyn"] else OK)

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        text, leise, _, _ = farben(p)
        schrift = (config.SCHRIFT, max(7, int(min(wb / 2.2, h) / 18)))
        n = len(e["werte"])
        clk = [1 if (t % self.UNTER) < self.UNTER // 2 else 0 for t in range(n)]
        signale = [("CLK", clk, SIGNAL_FARBEN["CLK"])] + [(f"Q{i}", [(z >> i) & 1 for z in e["werte"]], EINS)
                                                          for i in range(e["bits"])]
        x0, x1, y0, y1 = wb * 0.08, wb * 0.98, h * 0.12, h * 0.98
        zeitdiagramm(c, x0, x1, y0, y1, signale, schrift, leise, [(t, ROT) for t in e["glitches"]])
        dx = (x1 - x0) / n
        for p_ in range(e["perioden"]):                                      # Zählerstand je Periode oben
            z = e["werte"][p_ * self.UNTER + self.UNTER - 1]
            c.create_text(x0 + (p_ + 0.55) * self.UNTER * dx, y0 - 4, text=str(z), anchor="s", fill=text, font=schrift)


# =============================================================================
# SCHIEBEREGISTER
# =============================================================================
class SchieberegisterKarte(SchaltungsModell):
    TITEL = "➡️ Schieberegister, Ring- und Johnson-Zähler (interaktiv)"
    UNTERTITEL = "Seriell: Eingangsfolge eintippen (ein Bit je Takt). Ring/Johnson: Anzahl Takte wählen"
    VARIANTEN = ["seriell (SIPO)", "Ringzähler", "Johnson-Zähler"]
    TEXTFELDER = [("ein", "Eingang je Takt (seriell)", "1011 0010", {"max": 24, "platzhalter": "z.B. 1011 0010"})]
    REGLER = [("takte", "Anzahl Takte (Ring/Johnson)", "zahl", 1.0, 16.0, 8.0, {"ganzzahl": True})]
    SEITENVERHAELTNIS = 0.42
    MAX_HOEHE = 340
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Ein Schieberegister sind D-Flipflops in einer Kette am selben Takt: Bei jeder "
                  "Flanke übernimmt jede Stufe den Wert der vorigen. SERIELL rein, PARALLEL raus (SIPO, z.B. 74HC595) "
                  "macht aus einer Datenleitung 8 Ausgänge – so steuert ein µC viele LEDs mit 3 Pins. Der RINGZÄHLER "
                  "führt den Ausgang zurück an den Eingang: Eine einzelne 1 läuft im Kreis (n Zustände, 1-aus-n ohne "
                  "Decoder). Der JOHNSON-Zähler führt den INVERTIERTEN Ausgang zurück: 2n Zustände, und es ändert sich "
                  "pro Takt nur ein Bit.")

    def sk_rechnen(self, w, v):
        art = {"seriell (SIPO)": "seriell", "Ringzähler": "Ring", "Johnson-Zähler": "Johnson"}.get(v, "seriell")
        if art == "seriell":
            eingaben = folge(w["ein"], "Eingang")
            if not eingaben:
                raise ValueError("Eingang je Takt eintippen, z.B. 1011 0010")
        else:
            eingaben = [0] * int(round(w["takte"]))
        start = 0b0001 if art == "Ring" else 0
        verlauf = swm.schieberegister(4, eingaben, art, start)
        return {"art": art, "verlauf": verlauf, "z": verlauf[-1], "eingaben": eingaben}

    def sk_info(self, w, e, v):
        art = e["art"]
        zustaende = {"seriell": "beliebig (16 Muster)", "Ring": "4 Zustände (eine 1 läuft im Kreis)",
                     "Johnson": "8 Zustände (2 · n), pro Takt ändert sich nur ein Bit"}[art]
        rueck = {"seriell": "Q0 ← Eingang", "Ring": "Q0 ← Q3", "Johnson": "Q0 ← ¬Q3"}[art]
        return ([f"Q3 … Q0 = {format(e['z'], '04b')} nach {len(e['verlauf']) - 1} Takten   ·   {rueck}, Q(i) ← Q(i−1)",
                 f"{zustaende}",
                 "Verlauf: " + " → ".join(format(z, "04b") for z in e["verlauf"])],
                config.FARBEN["akzent"])

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        text, leise, _, _ = farben(p)
        g = max(7, int(min(wb / 2.2, h) / 16))
        bitreihe(p, wb * 0.02, h * 0.02, wb * 0.42, e["z"], 4, "Q3 … Q0")
        schritte = []                                           # je Takt 2 Zeitschritte (Takt HIGH, LOW)
        for z in e["verlauf"]:
            schritte += [z, z]
        clk = [1 if i % 2 == 0 and i > 0 else 0 for i in range(len(schritte))]
        signale = [("CLK", clk, SIGNAL_FARBEN["CLK"])] + [(f"Q{i}", [(z >> i) & 1 for z in schritte], EINS) for i in range(4)]
        if e["art"] == "seriell":
            ein = [0] + [x for x in e["eingaben"] for _ in (0, 1)][:len(schritte) - 1]
            signale.insert(1, ("Ein", ein, BLAU))
        zeitdiagramm(c, wb * 0.08, wb * 0.98, h * 0.30, h * 0.98, signale, (config.SCHRIFT, g), leise)
