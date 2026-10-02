# =============================================================================
# digitaltechnik/logik_mathe.py
# -----------------------------------------------------------------------------
# REINE LOGIK-FUNKTIONEN - KEIN tkinter. Einzeln testbar, z.B.:
#
#   python -c "from digitaltechnik.logik_mathe import *; print(analysieren('A·B + /A·C'))"
#
#   GATTER / gatter()       AND, OR, NOT, NAND, NOR, XOR, XNOR mit beliebig vielen Eingängen
#   parsen()                Text -> Ausdrucksbaum (siehe SCHREIBWEISEN)
#   auswerten()             Baum mit Belegung {A: 1, B: 0} ausrechnen
#   analysieren()           Wahrheitstabelle, Minterme, kanonische DNF/KNF, minimale DNF/KNF
#   minimieren()            Quine-McCluskey (+ Petrick) mit don't cares -> minimale Summe von Produkten
#   kv_aufbau()             Zeilen/Spalten eines KV-Diagramms (2 … 4 Variablen, Gray-Reihenfolge)
#   vergleichen()           sind zwei Ausdrücke gleich? (sonst ein Gegenbeispiel)
#
# SCHREIBWEISEN (alles gemischt erlaubt):
#   NICHT  ¬A  !A  ~A  /A  A'  NOT A  NICHT A
#   UND    A·B  A*B  A&B  A∧B  A AND B  A UND B  AB (nebeneinander)  A(B+C)
#   ODER   A+B  A|B  A∨B  A OR B  A ODER B
#   XOR    A⊕B  A^B  A XOR B          NAND / NOR / XNOR als Wörter
#   Variablen: ein Buchstabe, optional mit Ziffern (A, B, X1, X2). "AB" heisst A·B.
#   Rangfolge: NICHT  vor  UND  vor  XOR  vor  ODER  – Klammern setzen, wenn unsicher.
#
# WER RUFT DAS AUF?  digitaltechnik/grafiken_logik.py, digitaltechnik/rechner.py
# =============================================================================

import itertools
import re

MAX_VARIABLEN = 6
GATTER_NAMEN = ["AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR"]
NICHT, UND, ODER = "¬", "·", " + "


# =============================================================================
# GATTER
# =============================================================================
def gatter(name, eingaenge):
    """Ausgang eines Gatters für eine Liste von 0/1-Eingängen (NOT: genau 1 Eingang)."""
    e = [1 if x else 0 for x in eingaenge]
    if name == "NOT":
        if len(e) != 1:
            raise ValueError("NOT hat genau einen Eingang")
        return 1 - e[0]
    if len(e) < 2:
        raise ValueError(f"{name} braucht mindestens zwei Eingänge")
    und, oder, ungerade = int(all(e)), int(any(e)), sum(e) % 2
    werte = {"AND": und, "OR": oder, "NAND": 1 - und, "NOR": 1 - oder, "XOR": ungerade, "XNOR": 1 - ungerade}
    if name not in werte:
        raise ValueError(f"Unbekanntes Gatter: {name}")
    return werte[name]


def gatter_tabelle(name, anzahl):
    """[(eingänge-tupel, ausgang), ...] in Zählreihenfolge (00, 01, 10, 11 …)."""
    anzahl = 1 if name == "NOT" else anzahl
    return [(bits, gatter(name, bits)) for bits in itertools.product((0, 1), repeat=anzahl)]


# =============================================================================
# PARSER
# =============================================================================
_WOERTER = {"AND": "&", "UND": "&", "OR": "|", "ODER": "|", "NOT": "!", "NICHT": "!", "XOR": "^",
            "NAND": "NAND", "NOR": "NOR", "XNOR": "XNOR"}
_ZEICHEN = {"¬": "!", "!": "!", "~": "!", "/": "!", "·": "&", "*": "&", "&": "&", "∧": "&", "⋅": "&", "•": "&",
            "+": "|", "|": "|", "∨": "|", "^": "^", "⊕": "^", "'": "'", "’": "'", "(": "(", ")": ")"}


def _tokens(text):
    if text is None or not text.strip():
        raise ValueError("Ausdruck eingeben, z.B.  A·B + ¬A·C")
    tokens, i = [], 0
    while i < len(text):
        z = text[i]
        if z.isspace():
            i += 1
        elif z in "01":
            tokens.append(("const", int(z)))
            i += 1
        elif z in _ZEICHEN:
            tokens.append(("op", _ZEICHEN[z]))
            i += 1
        elif z.isalpha():
            wort = re.match(r"[A-Za-zÄÖÜäöü]+", text[i:]).group(0)
            if wort.upper() in _WOERTER:
                tokens.append(("op", _WOERTER[wort.upper()]))
                i += len(wort)
                continue
            # kein Schlüsselwort: Buchstabe für Buchstabe als Variable, Ziffern direkt dahinter gehören dazu
            name = re.match(r"[A-Za-zÄÖÜäöü][0-9_]*", text[i:]).group(0).rstrip("_")
            tokens.append(("var", name.upper()))
            i += len(name)
        else:
            raise ValueError(f"Zeichen „{z}“ an Stelle {i + 1} ist nicht erlaubt")
    return tokens


class _Parser:
    """Rekursiver Abstieg:  oder := xor (| xor)* ;  xor := und (^ und)* ;  und := nicht ((&)? nicht)* ;
    nicht := ! nicht | atom (')* ;  atom := var | const | ( ausdruck ).  NAND/NOR/XNOR auf Stufe ODER."""

    def __init__(self, tokens):
        self.t, self.i = tokens, 0

    def _sieh(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def _nimm(self):
        self.i += 1
        return self.t[self.i - 1]

    def ausdruck(self):
        links = self._xor()
        while self._sieh() in (("op", "|"), ("op", "NAND"), ("op", "NOR"), ("op", "XNOR")):
            op = self._nimm()[1]
            rechts = self._xor()
            links = ({"|": "or", "NAND": "nand", "NOR": "nor", "XNOR": "xnor"}[op], links, rechts)
        return links

    def _xor(self):
        links = self._und()
        while self._sieh() == ("op", "^"):
            self._nimm()
            links = ("xor", links, self._und())
        return links

    def _und(self):
        links = self._nicht()
        while True:
            art, wert = self._sieh()
            if (art, wert) == ("op", "&"):
                self._nimm()
                links = ("and", links, self._nicht())
            elif art in ("var", "const") or (art, wert) in (("op", "("), ("op", "!")):    # nebeneinander = UND
                links = ("and", links, self._nicht())
            else:
                return links

    def _nicht(self):
        if self._sieh() == ("op", "!"):
            self._nimm()
            return ("not", self._nicht())
        knoten = self._atom()
        while self._sieh() == ("op", "'"):
            self._nimm()
            knoten = ("not", knoten)
        return knoten

    def _atom(self):
        art, wert = self._sieh()
        if art == "var":
            self._nimm()
            return ("var", wert)
        if art == "const":
            self._nimm()
            return ("const", wert)
        if (art, wert) == ("op", "("):
            self._nimm()
            innen = self.ausdruck()
            if self._sieh() != ("op", ")"):
                raise ValueError("Schliessende Klammer ) fehlt")
            self._nimm()
            return innen
        if art is None:
            raise ValueError("Ausdruck endet zu früh – fehlt ein Operand?")
        raise ValueError(f"Unerwartetes Zeichen „{wert}“ – fehlt ein Operand oder eine Klammer?")


def parsen(text):
    """Text -> Ausdrucksbaum aus Tupeln, z.B. ('and', ('var', 'A'), ('not', ('var', 'B')))."""
    p = _Parser(_tokens(text))
    baum = p.ausdruck()
    if p.i != len(p.t):
        raise ValueError(f"Unerwartetes „{p.t[p.i][1]}“ – fehlt ein Operator oder ist eine Klammer zu viel?")
    return baum


def variablen(baum):
    """Alle Variablen, natürlich sortiert (A, B, …, X2, X10)."""
    gefunden = set()

    def laufen(k):
        if k[0] == "var":
            gefunden.add(k[1])
        for kind in k[1:]:
            if isinstance(kind, tuple):
                laufen(kind)
    laufen(baum)
    return sorted(gefunden, key=lambda n: (re.sub(r"\d+", "", n), int(re.sub(r"\D", "", n) or 0)))


def auswerten(baum, belegung):
    art = baum[0]
    if art == "var":
        return belegung[baum[1]]
    if art == "const":
        return baum[1]
    if art == "not":
        return 1 - auswerten(baum[1], belegung)
    a, b = auswerten(baum[1], belegung), auswerten(baum[2], belegung)
    return {"and": a & b, "or": a | b, "xor": a ^ b, "nand": 1 - (a & b), "nor": 1 - (a | b), "xnor": 1 - (a ^ b)}[art]


def als_text(baum, eltern=0):
    """Baum -> Text in der Toolbox-Schreibweise (¬, ·, +, ⊕), Klammern nur wo nötig."""
    rang = {"or": 1, "nand": 1, "nor": 1, "xnor": 1, "xor": 2, "and": 3}
    art = baum[0]
    if art == "var":
        return baum[1]
    if art == "const":
        return str(baum[1])
    if art == "not":
        innen = als_text(baum[1], 4)
        return NICHT + (innen if baum[1][0] in ("var", "const", "not") else f"({als_text(baum[1])})")
    zeichen = {"and": "·", "or": " + ", "xor": " ⊕ ", "nand": " NAND ", "nor": " NOR ", "xnor": " XNOR "}[art]
    text = als_text(baum[1], rang[art]) + zeichen + als_text(baum[2], rang[art] + 0.5)
    return f"({text})" if rang[art] < eltern else text


# =============================================================================
# WAHRHEITSTABELLE, NORMALFORMEN
# =============================================================================
def tabelle(baum, namen=None):
    """[(belegung-tupel, ausgang), ...], erste Variable = höchstwertiges Bit (Zeile k = Minterm k)."""
    namen = namen or variablen(baum)
    if len(namen) > MAX_VARIABLEN:
        raise ValueError(f"Höchstens {MAX_VARIABLEN} Variablen ({len(namen)} gefunden: {', '.join(namen)})")
    zeilen = []
    for bits in itertools.product((0, 1), repeat=len(namen)):
        zeilen.append((bits, auswerten(baum, dict(zip(namen, bits)))))
    return zeilen


def produkt(muster, namen):
    """'1-0' -> 'A·¬C'   (1 = Variable, 0 = negiert, - = fällt weg)"""
    teile = [n if z == "1" else NICHT + n for z, n in zip(muster, namen) if z != "-"]
    return UND.join(teile) or "1"


def summe(muster, namen):
    """Maxterm-Klausel aus einem Null-Muster: '1-0' -> '(¬A + C)'"""
    teile = [NICHT + n if z == "1" else n for z, n in zip(muster, namen) if z != "-"]
    return "(" + ODER.join(teile) + ")" if len(teile) > 1 else (teile[0] if teile else "0")


def kanonisch(minterme, namen):
    n = len(namen)
    alle = set(range(2 ** n))
    nullen = sorted(alle - set(minterme))
    dnf = ODER.join(produkt(format(m, f"0{n}b"), namen) for m in sorted(minterme)) or "0"
    knf = "·".join(summe(format(m, f"0{n}b"), namen) for m in nullen) or "1"
    return dnf, knf


# =============================================================================
# MINIMIEREN (Quine-McCluskey + Petrick)
# =============================================================================
def _zusammenfassen(a, b):
    unterschied = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if len(unterschied) == 1 and "-" not in (a[unterschied[0]], b[unterschied[0]]):
        i = unterschied[0]
        return a[:i] + "-" + a[i + 1:]
    return None


def _deckt(muster, m, n):
    bits = format(m, f"0{n}b")
    return all(z == "-" or z == b for z, b in zip(muster, bits))


def primimplikanten(minterme, dont_care, n):
    aktuell = {format(m, f"0{n}b") for m in set(minterme) | set(dont_care)}
    primes = set()
    while aktuell:
        naechste, benutzt = set(), set()
        liste = sorted(aktuell)
        for a, b in itertools.combinations(liste, 2):
            neu = _zusammenfassen(a, b)
            if neu:
                naechste.add(neu)
                benutzt.update((a, b))
        primes |= aktuell - benutzt
        aktuell = naechste
    return sorted(primes)


def _reihenfolge(positiv):
    """Sortierschlüssel für Terme: nach Variablen der Reihe nach, positives Literal zuerst (A vor ¬A vor fehlend)."""
    rang = {str(positiv): 0, str(1 - positiv): 1, "-": 2}
    return lambda muster: tuple(rang[z] for z in muster)


def minimieren(minterme, n, dont_care=()):
    """
    Minimale Summe von Produkten (DNF) für die Minterme, don't cares dürfen mitbenutzt werden.
    Rückgabe: Liste von Mustern ('1-0' …), erst wenige Terme, dann wenige Literale.
    """
    minterme = sorted(set(minterme) - set(dont_care))
    if not minterme:
        return []
    if len(set(minterme) | set(dont_care)) == 2 ** n:
        return ["-" * n]
    primes = primimplikanten(minterme, dont_care, n)
    deckung = {p: {m for m in minterme if _deckt(p, m, n)} for p in primes}
    # Petrick: Produkt über alle Minterme der Summe ihrer Primimplikanten, ausmultipliziert mit Absorption
    loesungen = [frozenset()]
    for m in minterme:
        moeglich = [p for p in primes if m in deckung[p]]
        neu = {l | {p} for l in loesungen for p in moeglich}
        neu = sorted(neu, key=len)
        loesungen = []
        for kandidat in neu:                                   # Absorption: Obermengen weglassen
            if not any(l <= kandidat for l in loesungen):
                loesungen.append(kandidat)
        if len(loesungen) > 4000:                              # Schutz vor Explosion (kommt bei ≤ 6 Variablen kaum vor)
            loesungen = sorted(loesungen, key=len)[:4000]

    def kosten(l):
        return (len(l), sum(n - p.count("-") for p in l), sorted(l))
    return sorted(min(loesungen, key=kosten), key=_reihenfolge(1))


def analysieren(text, dont_care=()):
    """Alles zu einem Ausdruck: Variablen, Tabelle, Minterme, kanonische und minimale Formen."""
    baum = parsen(text)
    namen = variablen(baum)
    if not namen:
        wert = auswerten(baum, {})
        return {"baum": baum, "namen": [], "tabelle": [((), wert)], "minterme": [0] if wert else [],
                "dnf": str(wert), "knf": str(wert), "min_dnf": str(wert), "min_knf": str(wert), "text": als_text(baum)}
    zeilen = tabelle(baum, namen)
    minterme = [k for k, (_, aus) in enumerate(zeilen) if aus]
    n = len(namen)
    dnf, knf = kanonisch(minterme, namen)
    return {"baum": baum, "namen": namen, "tabelle": zeilen, "minterme": minterme,
            "maxterme": [k for k in range(2 ** n) if k not in minterme], "dnf": dnf, "knf": knf,
            **minimal_formen(minterme, namen, dont_care), "text": als_text(baum)}


def minimal_formen(minterme, namen, dont_care=()):
    """Minimale DNF und KNF (KNF = minimierte Nullen, mit De Morgan umgedreht)."""
    n = len(namen)
    terme = minimieren(minterme, n, dont_care)
    nullen = [k for k in range(2 ** n) if k not in minterme and k not in dont_care]
    klauseln = minimieren(nullen, n, dont_care)
    min_dnf = ODER.join(produkt(t, namen) for t in terme) if terme else "0"
    min_knf = "·".join(summe(k, namen) for k in sorted(klauseln, key=_reihenfolge(0))) if klauseln else "1"
    if terme == ["-" * n]:
        min_dnf = "1"
    if klauseln == ["-" * n]:
        min_knf = "0"
    return {"min_dnf": min_dnf, "min_knf": min_knf, "terme": terme, "klauseln": klauseln}


def vergleichen(text_a, text_b):
    """Gleichwertig? -> (True, None) oder (False, Gegenbeispiel-Belegung mit beiden Ergebnissen)."""
    a, b = parsen(text_a), parsen(text_b)
    namen = sorted(set(variablen(a)) | set(variablen(b)),
                   key=lambda n: (re.sub(r"\d+", "", n), int(re.sub(r"\D", "", n) or 0)))
    if len(namen) > MAX_VARIABLEN:
        raise ValueError(f"Höchstens {MAX_VARIABLEN} Variablen")
    for bits in itertools.product((0, 1), repeat=len(namen)):
        belegung = dict(zip(namen, bits))
        wa, wb = auswerten(a, belegung), auswerten(b, belegung)
        if wa != wb:
            return False, {"belegung": belegung, "a": wa, "b": wb, "namen": namen}
    return True, {"namen": namen}


# =============================================================================
# KV-DIAGRAMM
# =============================================================================
GRAY = {1: ["0", "1"], 2: ["00", "01", "11", "10"]}


def kv_aufbau(n):
    """
    Aufteilung der Variablen auf Zeilen und Spalten (Gray-Reihenfolge, Nachbarn unterscheiden sich in 1 Bit):
      2 Var: Zeilen A,  Spalten B       3 Var: Zeilen A,  Spalten BC       4 Var: Zeilen AB, Spalten CD
    Rückgabe: (zeilen_bits, spalten_bits, zelle(r, s) -> Minterm-Nummer)
    """
    if n not in (2, 3, 4):
        raise ValueError("KV-Diagramm hier für 2 … 4 Variablen")
    z_bits = 1 if n < 4 else 2
    s_bits = n - z_bits
    zeilen, spalten = GRAY[z_bits], GRAY[s_bits]

    def zelle(r, s):
        return int(zeilen[r] + spalten[s], 2)
    return zeilen, spalten, zelle


def kv_gruppe(muster, n):
    """Welche Zeilen- und Spaltenindizes deckt ein Implikant ab? (für das Einzeichnen der Blöcke)"""
    zeilen, spalten, zelle = kv_aufbau(n)
    z = sorted({r for r in range(len(zeilen)) for s in range(len(spalten)) if _deckt(muster, zelle(r, s), n)})
    s = sorted({s for r in range(len(zeilen)) for s in range(len(spalten)) if _deckt(muster, zelle(r, s), n)})
    return z, s


def zusammenhaengend(indizes, laenge):
    """[0, 3] bei Länge 4 -> [[3], [0]] (zwei Stücke über den Rand), [1, 2] -> [[1, 2]]"""
    if len(indizes) == laenge:
        return [list(indizes)]
    stuecke, aktuell = [], []
    for i in indizes:
        if aktuell and i != aktuell[-1] + 1:
            stuecke.append(aktuell)
            aktuell = []
        aktuell.append(i)
    if aktuell:
        stuecke.append(aktuell)
    return stuecke
