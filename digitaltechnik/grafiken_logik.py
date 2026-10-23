# =============================================================================
# digitaltechnik/grafiken_logik.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE der Logik - MODELLE OHNE FENSTER (Desktop-App UND Web):
#
#   GatterKarte     Gatter wählen, Eingänge schalten -> Ausgang, IEC- und ANSI-Symbol, Wahrheitstabelle
#   AusdruckKarte   boolescher Ausdruck -> Wahrheitstabelle, Minterme, kanonische und minimale DNF/KNF
#   KVKarte         KV-Diagramm (2 … 4 Variablen): Einsen und don't cares als Minterm-Nummern ODER als
#                   Ausdruck eingeben -> Blöcke + minimale Form
#
# Rechnung: digitaltechnik/logik_mathe.py (Parser, Wahrheitstabelle, Quine-McCluskey, KV-Aufbau)
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_gatter")
# =============================================================================

import math
import re

import config                                                            # -> config.py
from bauteile.grafiken.schaltplan import OK, SchaltungsModell            # -> bauteile/grafiken/schaltplan.py
from digitaltechnik import logik_mathe as lm                             # -> digitaltechnik/logik_mathe.py
from digitaltechnik.grafiken import farben                               # -> digitaltechnik/grafiken.py

EINS, NULL_FARBE = "#22C55E", "#6B7280"
GRUPPEN_FARBEN = ["#EF4444", "#3B82F6", "#F59E0B", "#A855F7", "#14B8A6", "#EC4899", "#84CC16", "#F97316"]
IEC_ZEICHEN = {"AND": "&", "NAND": "&", "OR": "≥1", "NOR": "≥1", "XOR": "=1", "XNOR": "=1", "NOT": "1"}


# =============================================================================
# GATTER-SIMULATOR
# =============================================================================
class GatterKarte(SchaltungsModell):
    TITEL = "🔲 Logikgatter (interaktiv)"
    UNTERTITEL = "Gatter wählen, Eingänge schalten – links das IEC-Symbol (DIN EN 60617), rechts ANSI"
    VARIANTEN = list(lm.GATTER_NAMEN)
    SCHALTER = [("a", "A = 1"), ("b", "B = 1"), ("c", "C = 1")]
    AUSWAHL = [("anzahl", "Eingänge", ["2 Eingänge", "3 Eingänge"], "2 Eingänge")]
    SEITENVERHAELTNIS = 0.32
    MAX_HOEHE = 280
    ERKLAERUNG = ("Was zeigt das Werkzeug?  AND ist nur 1, wenn ALLE Eingänge 1 sind; OR, wenn MINDESTENS EINER 1 ist; "
                  "XOR, wenn eine UNGERADE Anzahl 1 ist (bei zwei Eingängen: wenn sie verschieden sind). NAND, NOR, XNOR "
                  "sind die negierten Versionen – der Kreis am Ausgang bedeutet „negiert“. IEC-Symbole sind Rechtecke "
                  "mit Zeichen (& für UND, ≥1 für ODER, =1 für XOR), ANSI-Symbole haben eigene Formen (in US-Datenblättern "
                  "üblich). NAND und NOR allein reichen, um JEDE Logikfunktion zu bauen.")

    @staticmethod
    def _baum(name, n):
        if name == "NOT":
            return ("not", ("var", "A"))
        art = {"AND": "and", "OR": "or", "XOR": "xor", "NAND": "and", "NOR": "or", "XNOR": "xor"}[name]
        baum = ("var", "A")
        for v in "BC"[:n - 1]:
            baum = (art, baum, ("var", v))
        return ("not", baum) if name in ("NAND", "NOR", "XNOR") else baum

    def sk_rechnen(self, w, v):
        name = v if v in lm.GATTER_NAMEN else "AND"
        n = 1 if name == "NOT" else int(w["anzahl"][0])
        e = [int(bool(w[k])) for k in "abc"[:n]]
        return {"name": name, "n": n, "e": e, "aus": lm.gatter(name, e), "zeilen": lm.gatter_tabelle(name, n)}

    def sk_info(self, w, e, v):
        einsen = sum(1 for _, a in e["zeilen"] if a)
        jetzt = int("".join(map(str, e["e"])), 2)
        tabelle = lm.wahrheitstabelle_text(list("ABC"[:e["n"]]), e["zeilen"], jetzt).split("\n")
        return ([f"Y = {lm.als_text(self._baum(e['name'], e['n']))} = {e['aus']}   ·   "
                 f"{einsen} von {len(e['zeilen'])} Zeilen ergeben 1", ""] + tabelle,
                OK if e["aus"] else config.FARBEN["akzent"])

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        name, n, ein, aus = e["name"], e["n"], e["e"], e["aus"]
        text, leise, _, _ = farben(p)
        dick = max(2, int(h / 90))
        schrift = (config.SCHRIFT, max(9, int(h / 16)), "bold")
        klein = (config.SCHRIFT, max(8, int(h / 20)))
        for x_mitte, art in ((wb * 0.25, "IEC"), (wb * 0.72, "ANSI")):
            gb, gh = min(wb * 0.13, h * 0.5), h * 0.56
            x0, x1 = x_mitte - gb / 2, x_mitte + gb / 2
            y0, y1 = h * 0.24, h * 0.24 + gh
            c.create_text(x_mitte, h * 0.1, text=art, fill=leise, font=klein)
            ys = [y0 + gh * (i + 1) / (n + 1) for i in range(n)]
            negiert = name in ("NAND", "NOR", "XNOR", "NOT")
            r_kreis = max(4, gh * 0.07)
            if art == "IEC":
                c.create_rectangle(x0, y0, x1, y1, outline=text, width=dick)
                c.create_text(x_mitte, y0 + gh * 0.2, text=IEC_ZEICHEN[name], fill=text, font=schrift)
                ende = x1
            else:
                ende = self._ansi(c, name, x0, y0, x1, y1, text, dick)
            for i, y in enumerate(ys):
                links = x0 - gb * 0.6
                rand = x0 + (self._ansi_rand(name, x0, y0, x1, y1, y) - x0 if art == "ANSI" else 0)
                if art == "ANSI" and name in ("XOR", "XNOR"):
                    rand -= gb * 0.12                         # Leitung endet an der vorderen Zusatzkurve
                farbe = EINS if ein[i] else NULL_FARBE
                c.create_line(links, y, rand, y, fill=farbe, width=dick)
                c.create_text(links - 6, y, text=f"{'ABC'[i]}={ein[i]}", anchor="e", fill=farbe, font=klein)
            ym = (y0 + y1) / 2
            if negiert:
                c.create_oval(ende, ym - r_kreis, ende + 2 * r_kreis, ym + r_kreis, outline=text, width=dick)
                ende += 2 * r_kreis
            farbe = EINS if aus else NULL_FARBE
            c.create_line(ende, ym, ende + gb * 0.5, ym, fill=farbe, width=dick)
            c.create_oval(ende + gb * 0.5, ym - r_kreis * 1.6, ende + gb * 0.5 + 3.2 * r_kreis, ym + r_kreis * 1.6,
                          fill=farbe, outline="")
            c.create_text(ende + gb * 0.5 + 3.2 * r_kreis + 6, ym, text=f"Y={aus}", anchor="w", fill=farbe, font=klein)

    @staticmethod
    def _ansi_rand(name, x0, y0, x1, y1, y):
        """x-Koordinate der hinteren Kante des ANSI-Symbols auf Höhe y (OR/XOR sind hinten gewölbt)."""
        if name in ("OR", "NOR", "XOR", "XNOR"):
            return x0 + (x1 - x0) * 0.18 * math.sin(math.pi * (y - y0) / (y1 - y0))
        return x0

    def _ansi(self, c, name, x0, y0, x1, y1, farbe, dick):
        """Zeichnet das ANSI-Symbol, gibt die x-Koordinate des Ausgangs zurück."""
        ym, b, h = (y0 + y1) / 2, x1 - x0, y1 - y0
        if name == "NOT":
            c.create_polygon(x0, y0 + h * 0.15, x0, y1 - h * 0.15, x1 - b * 0.15, ym, outline=farbe, fill="", width=dick)
            return x1 - b * 0.15
        if name in ("AND", "NAND"):
            punkte = [x0, y0, x0 + b * 0.45, y0]
            for k in range(1, 20):
                winkel = -math.pi / 2 + math.pi * k / 20
                punkte += [x0 + b * 0.45 + b * 0.55 * math.cos(winkel), ym + h / 2 * math.sin(winkel)]
            punkte += [x0 + b * 0.45, y1, x0, y1]
            c.create_polygon(*punkte, outline=farbe, fill="", width=dick)
            return x1
        punkte = []                                            # OR / NOR / XOR / XNOR: hinten gewölbt, vorne spitz
        for k in range(21):
            u = k / 20
            punkte += [x0 + b * u, y0 + (ym - y0) * u ** 2.2]
        for k in range(21):
            u = 1 - k / 20
            punkte += [x0 + b * u, y1 - (y1 - ym) * u ** 2.2]
        for k in range(21):
            t = 1 - k / 20
            punkte += [self._ansi_rand(name, x0, y0, x1, y1, y0 + h * t), y0 + h * t]
        c.create_polygon(*punkte, outline=farbe, fill="", width=dick)
        if name in ("XOR", "XNOR"):                          # zweite Wölbung davor
            c.create_line(*[q for k in range(21) for q in
                            (self._ansi_rand(name, x0, y0, x1, y1, y0 + h * k / 20) - b * 0.12, y0 + h * k / 20)],
                          fill=farbe, width=dick)
        return x1


# =============================================================================
# AUSDRUCK -> WAHRHEITSTABELLE
# =============================================================================
class AusdruckKarte(SchaltungsModell):
    TITEL = "🧾 Ausdruck → Wahrheitstabelle und Normalformen (interaktiv)"
    UNTERTITEL = "Schreibweisen: ¬A !A /A A'   A·B A*B AB   A+B   A⊕B   Klammern ( )"
    TEXTFELDER = [("ausdruck", "Ausdruck Y =", "A·B + ¬A·C", {"max": 120, "platzhalter": "z.B. A*B + !A*C", "tastatur": "logik"})]
    SEITENVERHAELTNIS = 0.42
    MAX_HOEHE = 460
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Jede Zeile der Wahrheitstabelle ist eine Belegung der Eingänge; die "
                  "Zeilennummer ist die Binärzahl der Eingänge (= Minterm-Nummer). DNF: für jede 1-Zeile ein UND-Term "
                  "(Minterm), alle ODER-verknüpft. KNF: für jede 0-Zeile eine ODER-Klausel (Maxterm), alle UND-verknüpft. "
                  "Die kanonischen Formen sind eindeutig, aber lang – die minimalen Formen (Quine-McCluskey, wie das "
                  "KV-Diagramm) brauchen am wenigsten Gatter.")

    def sk_rechnen(self, w, v):
        return lm.analysieren(w["ausdruck"])                             # ValueError mit Erklärung

    def sk_info(self, w, e, v):
        kurz = lambda text: text if len(text) <= 160 else text[:157] + " …"          # noqa: E731
        return ([f"Gelesen als:   Y = {e['text']}",
                 f"Minterme:      Σm({', '.join(map(str, e['minterme']))})" if e["namen"] else "konstant",
                 f"DNF kanonisch: {kurz(e['dnf'])}", f"KNF kanonisch: {kurz(e['knf'])}",
                 f"DNF minimal:   {e['min_dnf']}", f"KNF minimal:   {e['min_knf']}"],
                config.FARBEN["akzent"])

    def sk_zeichnen(self, p, w, e, v):
        """Wahrheitstabelle als Raster: Spalten = Variablen + Y, Zeilen = Belegungen (bis 32 Zeilen in 2 Blöcken)."""
        c, wb, h = p.c, p.breite, p.hoehe
        text, leise, linie, akzent = farben(p)
        namen, zeilen = e["namen"], e["tabelle"]
        if not namen:
            c.create_text(wb / 2, h / 2, text=f"Y = {e['text']} ist konstant", fill=text,
                          font=(config.SCHRIFT, max(10, int(h / 14)), "bold"))
            return
        if len(zeilen) > 32:
            c.create_text(wb / 2, h / 2, text=f"{len(zeilen)} Zeilen – zu viele für das Bild (Formeln unten)",
                          fill=leise, font=(config.SCHRIFT, max(9, int(h / 18))))
            return
        bloecke = 1 if len(zeilen) <= 16 else 2
        pro_block = math.ceil(len(zeilen) / bloecke)
        spalten = len(namen) + 2                                         # Nr., Variablen, Y
        zh = min(h * 0.86 / (pro_block + 1), 26)
        zb = min(wb * 0.9 / (bloecke * spalten + (bloecke - 1)), 54)
        schrift = (config.SCHRIFT_CODE, max(8, int(zh * 0.55)))
        fett = (config.SCHRIFT_CODE, max(8, int(zh * 0.55)), "bold")
        for blk in range(bloecke):
            x0 = wb * 0.05 + blk * (spalten + 1) * zb
            y0 = h * 0.04
            for i, kopf in enumerate(["Nr."] + namen + ["Y"]):
                c.create_text(x0 + (i + 0.5) * zb, y0 + zh / 2, text=kopf, fill=text, font=fett)
            c.create_line(x0, y0 + zh, x0 + spalten * zb, y0 + zh, fill=linie)
            for k in range(blk * pro_block, min(len(zeilen), (blk + 1) * pro_block)):
                bel, y = zeilen[k]
                yy = y0 + (k - blk * pro_block + 1.5) * zh
                if y:
                    c.create_rectangle(x0, yy - zh / 2, x0 + spalten * zb, yy + zh / 2, fill=akzent, outline="")
                farbe = "#FFFFFF" if y else text
                c.create_text(x0 + 0.5 * zb, yy, text=str(k), fill="#FFFFFF" if y else leise, font=schrift)
                for i, bit in enumerate(bel):
                    c.create_text(x0 + (i + 1.5) * zb, yy, text=str(bit), fill=farbe, font=schrift)
                c.create_text(x0 + (spalten - 0.5) * zb, yy, text=str(y), fill=farbe, font=fett)


# =============================================================================
# KV-DIAGRAMM
# =============================================================================
def _nummern(text, n, name):
    """'0, 1, 2 8;10' -> {0, 1, 2, 8, 10}; nur 0 … 2^n − 1."""
    teile = [t for t in re.split(r"[\s,;]+", str(text or "").strip()) if t]
    werte = set()
    for t in teile:
        if not t.isdigit():
            raise ValueError(f"{name}: „{t}“ ist keine Minterm-Nummer (nur Zahlen, mit Komma getrennt)")
        k = int(t)
        if k >= 2 ** n:
            raise ValueError(f"{name}: {k} gibt es bei {n} Variablen nicht (0 … {2 ** n - 1})")
        werte.add(k)
    return werte


def _umbenennen(baum, abbild):
    if baum[0] == "var":
        return ("var", abbild[baum[1]])
    return (baum[0],) + tuple(_umbenennen(k, abbild) if isinstance(k, tuple) else k for k in baum[1:])


class KVKarte(SchaltungsModell):
    TITEL = "🗺️ KV-Diagramm (interaktiv)"
    UNTERTITEL = "Feld anklicken: 0 → 1 → X → 0  ·  oder Minterm-Nummern bzw. einen Ausdruck eintippen"
    HILFE = ("- **Feld im Diagramm anklicken**: 0 → 1 → X (don't care) → 0. Die Felder Einsen / don't care darunter "
             "werden automatisch mitgeführt.\n- Oder Minterm-Nummern eintippen, mit Komma getrennt (Enter übernimmt).\n"
             "- Oder einen Ausdruck eingeben – er ersetzt die Einsen. Ein Klick ins Diagramm macht daraus wieder Nummern.")
    VARIANTEN = ["4 Variablen", "3 Variablen", "2 Variablen"]
    TEXTFELDER = [("einsen", "Einsen (Minterme)", "0, 1, 2, 3, 8, 10", {"max": 80, "platzhalter": "z.B. 0, 1, 2, 3, 8, 10"}),
                  ("dc", "don't care (X)", "", {"max": 80, "platzhalter": "optional, z.B. 5, 7"}),
                  ("ausdruck", "oder Ausdruck", "", {"max": 120, "platzhalter": "z.B. A·B + C·¬D (ersetzt die Einsen)",
                                                          "tastatur": "logik"})]
    STARTWERTE = {"4 Variablen": {"einsen": "0, 1, 2, 3, 8, 10", "dc": ""},
                  "3 Variablen": {"einsen": "0, 1, 2, 5", "dc": "7"}, "2 Variablen": {"einsen": "0, 1", "dc": ""}}
    SEITENVERHAELTNIS = 0.55
    MAX_HOEHE = 420
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Das KV-Diagramm ist die Wahrheitstabelle als Rechteck, so angeordnet, dass "
                  "benachbarte Felder sich in genau EINER Variable unterscheiden (Gray-Code an den Rändern) – auch über "
                  "den Rand hinweg (oben ↔ unten, links ↔ rechts). Zusammenhängende Blöcke aus 1, 2, 4 oder 8 Einsen "
                  "ergeben je einen UND-Term; Variablen, die sich im Block ändern, fallen weg. Möglichst grosse und "
                  "möglichst wenige Blöcke = minimale DNF. X-Felder (don't care) dürfen mitbenutzt werden, müssen aber "
                  "nicht. Die kleine Zahl in jedem Feld ist die Minterm-Nummer.")

    def sk_rechnen(self, w, v):
        n = int((v or "4 Variablen")[0])
        hinweis = ""
        if w["ausdruck"].strip():                                         # Ausdruck ersetzt die Einsen
            baum = lm.parsen(w["ausdruck"])
            vars_ = lm.variablen(baum)
            if len(vars_) > 4:
                raise ValueError("Für das KV-Diagramm höchstens 4 Variablen")
            n = max(len(vars_), 2)                                        # Variablenzahl folgt dem Ausdruck
            kv_namen = list("ABCD"[:n])
            abbild = dict(zip(vars_, kv_namen))
            zeilen = lm.tabelle(_umbenennen(baum, abbild), kv_namen)
            einsen = {k for k, (_, aus) in enumerate(zeilen) if aus}
            dc = set()
            hinweis = ", ".join(f"{a} → {b}" for a, b in abbild.items() if a != b)
        else:
            einsen = _nummern(w["einsen"], n, "Einsen")
            dc = _nummern(w["dc"], n, "don't care") - einsen
        namen = list("ABCD"[:n])
        f = lm.minimal_formen(sorted(einsen), namen, sorted(dc))
        return {"n": n, "namen": namen, "einsen": sorted(einsen), "dc": sorted(dc), "f": f, "hinweis": hinweis}

    def sk_info(self, w, e, v):
        f, n = e["f"], e["n"]
        zeilen = [f"Σm({', '.join(map(str, e['einsen']))})" + (f" + d({', '.join(map(str, e['dc']))})" if e["dc"] else ""),
                  f"Y = {f['min_dnf']}   (minimale DNF, {len(f['terme'])} Block/Blöcke)",
                  f"Y = {f['min_knf']}   (minimale KNF, aus den Nullen)"]
        for i, t in enumerate(f["terme"]):
            if t != "-" * n:
                zeilen.append(f"  Block {i + 1}: {lm.produkt(t, e['namen'])}   ({2 ** t.count('-')} Felder)")
        if e["hinweis"]:
            zeilen.append(f"Variablen umbenannt: {e['hinweis']}")
        return zeilen, config.FARBEN["akzent"]

    def sk_klick(self, aktion, w, e, v):
        """KV-Feld angeklickt: 0 -> 1 -> X -> 0. Aus einem Ausdruck werden dabei Minterm-Nummern."""
        _art, m = aktion
        einsen, dc = set(e["einsen"]), set(e["dc"])
        if m in einsen:
            einsen.discard(m)
            dc.add(m)
        elif m in dc:
            dc.discard(m)
        else:
            einsen.add(m)
        liste = lambda menge: ", ".join(map(str, sorted(menge)))
        return {"__variante__": f"{e['n']} Variablen", "einsen": liste(einsen), "dc": liste(dc), "ausdruck": ""}

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        n, namen, terme = e["n"], e["namen"], e["f"]["terme"]
        werte = {m: "1" for m in e["einsen"]} | {m: "X" for m in e["dc"]}
        z_codes, s_codes, zelle = lm.kv_aufbau(n)
        z_namen, s_namen = "".join(namen[:len(z_codes[0])]), "".join(namen[len(z_codes[0]):])
        text, leise, rahmen, _ = farben(p)
        zellen = min((wb * 0.62) / len(s_codes), (h * 0.78) / len(z_codes))
        x0, y0 = wb * 0.08 + zellen * 0.9, h * 0.16
        gross = (config.SCHRIFT_CODE, max(10, int(zellen / 3)), "bold")
        klein = (config.SCHRIFT, max(7, int(zellen / 7)))
        mittel = (config.SCHRIFT_CODE, max(8, int(zellen / 5)))
        c.create_text(x0 - 6, y0 - 6, text=f"{z_namen} \\ {s_namen}", anchor="se", fill=text, font=mittel)
        for s, code in enumerate(s_codes):
            c.create_text(x0 + (s + 0.5) * zellen, y0 - 6, text=code, anchor="s", fill=leise, font=mittel)
        for r, code in enumerate(z_codes):
            c.create_text(x0 - 6, y0 + (r + 0.5) * zellen, text=code, anchor="e", fill=leise, font=mittel)
        for r in range(len(z_codes)):
            for s in range(len(s_codes)):
                a, b = x0 + s * zellen, y0 + r * zellen
                c.create_rectangle(a, b, a + zellen, b + zellen, outline=rahmen, width=1)
                p.klickbereich(a, b, a + zellen, b + zellen, ("kv", zelle(r, s)))      # Klick: 0 -> 1 -> X
        for i, t in enumerate(terme):                                      # Blöcke, über den Rand -> mehrere Teile
            farbe = GRUPPEN_FARBEN[i % len(GRUPPEN_FARBEN)]
            rand = 4 + 3 * (i % 4)
            zs, ss = lm.kv_gruppe(t, n)
            for z_stueck in lm.zusammenhaengend(zs, len(z_codes)):
                for s_stueck in lm.zusammenhaengend(ss, len(s_codes)):
                    c.create_rectangle(x0 + s_stueck[0] * zellen + rand, y0 + z_stueck[0] * zellen + rand,
                                       x0 + (s_stueck[-1] + 1) * zellen - rand, y0 + (z_stueck[-1] + 1) * zellen - rand,
                                       outline=farbe, width=3)
        for r in range(len(z_codes)):
            for s in range(len(s_codes)):
                m = zelle(r, s)
                a, b = x0 + s * zellen, y0 + r * zellen
                wert = werte.get(m, "0")
                c.create_text(a + zellen / 2, b + zellen / 2, text=wert,
                              fill={"1": text, "X": "#F59E0B", "0": leise}[wert], font=gross)
                c.create_text(a + zellen - 4, b + zellen - 3, text=str(m), anchor="se", fill=leise, font=klein)
        lx = x0 + len(s_codes) * zellen + 20                               # Legende rechts
        for i, t in enumerate(terme[:8]):
            if t == "-" * n:
                continue
            farbe = GRUPPEN_FARBEN[i % len(GRUPPEN_FARBEN)]
            y = y0 + i * zellen * 0.45 + 8
            c.create_rectangle(lx, y - 6, lx + 14, y + 6, outline=farbe, width=3)
            c.create_text(lx + 22, y, text=lm.produkt(t, namen), anchor="w", fill=text, font=mittel)
