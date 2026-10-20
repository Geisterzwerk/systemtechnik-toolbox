# =============================================================================
# uebungen/digital.py
# -----------------------------------------------------------------------------
# ÜBUNGEN DIGITALTECHNIK (Stufen 1–4): Zahlensysteme und Codes, Logik und Gatter, KV-Diagramm,
# Schaltnetze (Addierer, MUX, Decoder, 7-Segment), Schaltwerke (Flipflops, Zähler, Schieberegister,
# f_max), Busse und Speicher (UART, Parität, Speichergrösse), Logikpegel.
#
# Gerechnet und geprüft wird mit DENSELBEN Funktionen wie die Rechner der Digitaltechnik
# (digitaltechnik/*_mathe.py) - nichts doppelt. Antworten meist als Text (Binär, Hex, Dezimal, Bitfolge)
# oder als Auswahl - siehe uebungen/kern.py (Erzeuger als dict).
#
# WER RUFT DAS AUF?  uebungen/aufgaben.py (lädt alle Übungs-Module)
# =============================================================================

from digitaltechnik import busse_mathe as bm, logik_mathe as lm, pegel_mathe as pm     # -> digitaltechnik/
from digitaltechnik import schaltnetze_mathe as sn, schaltwerke_mathe as sw, zahlen_mathe as zm
from uebungen.kern import _f, art                                    # -> uebungen/kern.py
from uebungen.schemas import GESUCHT, SCHEMAS, iec_gatter, kasten_baustein   # -> uebungen/schemas.py

D = "Digitaltechnik"
ZAHLEN, LOGIK, NETZE, WERKE, BUSSE = ("Zahlensysteme & Codes", "Logik & Gatter", "Schaltnetze", "Schaltwerke",
                                      "Busse, Speicher & Pegel")


def _b(wert, bits):
    """Bitmuster mit Leerzeichen alle 4 Stellen: 0101 1001"""
    return zm.binaer(wert, bits)


def _text(text, loesung, weg, gesucht, vergleich="text", **mehr):
    """Kurzform für eine Text-Aufgabe (dict, siehe uebungen/kern.py)."""
    return {"text": text, "antwort": "text", "loesung": loesung, "weg": weg, "gesucht": gesucht,
            "vergleich": vergleich, **mehr}


def _auswahl(z, text, richtig, falsch, weg, gesucht, **mehr):
    """Auswahl-Aufgabe: richtige + falsche Optionen, gemischt (gleiche Nummer -> gleiche Reihenfolge)."""
    optionen = [richtig] + [f for f in dict.fromkeys(falsch) if f != richtig]
    z.shuffle(optionen)
    return {"text": text, "antwort": "auswahl", "loesung": richtig, "optionen": optionen, "weg": weg,
            "gesucht": gesucht, **mehr}


# =============================================================================
# ZAHLENSYSTEME UND CODES
# =============================================================================
def _potenzen(wert, bits):
    """Rechenweg: welche Zweierpotenzen stecken drin?"""
    teile = [str(2 ** i) for i in range(bits - 1, -1, -1) if wert >> i & 1]
    return " + ".join(teile) if teile else "0"


def _dez_bin(z):
    w = z.randint(5, 255)
    return _text(f"Wandle die Dezimalzahl {w} in eine 8-Bit-Binärzahl um.", _b(w, 8),
                 [f"Zerlegen in Zweierpotenzen (128, 64, 32, 16, 8, 4, 2, 1): {w} = {_potenzen(w, 8)}",
                  f"Jede vorhandene Potenz ist eine 1: {_b(w, 8)}",
                  "Kontrolle: Hex = " + f"0x{w:02X} (je 4 Bit eine Hex-Ziffer)"],
                 {"zeichen": "Binär", "text": "8 Bit, z.B. 0101 1001"}, "basis2")


def _bin_dez(z):
    w = z.randint(5, 255)
    return _text(f"Welche Dezimalzahl ist die vorzeichenlose Binärzahl {_b(w, 8)}?", str(w),
                 [f"Wertigkeiten der Einsen addieren: {_potenzen(w, 8)} = {w}"],
                 {"zeichen": "Dezimal", "text": ""}, "basis10")


def _dez_hex(z):
    w = z.randint(16, 4095)
    return _text(f"Wandle die Dezimalzahl {w} in eine Hexadezimalzahl um.", f"{w:X}",
                 [f"Fortgesetzt durch 16 teilen: {w} = {w // 16} · 16 + {w % 16}  …  (Reste von unten nach oben lesen)",
                  f"Ergebnis: 0x{w:X}   (A = 10, B = 11 … F = 15)",
                  f"Kontrolle binär: {zm.gruppiert(format(w, 'b'))}"],
                 {"zeichen": "Hex", "text": "z.B. 2F oder 0x2F"}, "basis16")


def _hex_bin(z):
    w = z.randint(16, 255)
    return _text(f"Schreibe die Hexadezimalzahl 0x{w:02X} als 8-Bit-Binärzahl.", _b(w, 8),
                 [f"Jede Hex-Ziffer wird zu genau 4 Bit: {w >> 4:X} = {w >> 4:04b}, {w & 15:X} = {w & 15:04b}",
                  f"Zusammen: {_b(w, 8)}"],
                 {"zeichen": "Binär", "text": "8 Bit"}, "basis2")


def _bits_noetig(z):
    n = z.choice([5, 10, 12, 20, 26, 60, 100, 200, 300, 1000])
    bits = max((n - 1).bit_length(), 1)
    return _text(f"Ein Zähler soll {n} verschiedene Zustände unterscheiden (0 bis {n - 1}). Wie viele Bit "
                 "(Flipflops) braucht er mindestens?", str(bits),
                 [f"Mit n Bit gibt es 2ⁿ Zustände. Gesucht ist das kleinste n mit 2ⁿ ≥ {n}:",
                  f"2^{bits - 1} = {2 ** (bits - 1)} reicht nicht, 2^{bits} = {2 ** bits} reicht  ->  {bits} Bit"],
                 {"zeichen": "Anzahl Bit", "text": ""}, "basis10")


def _bcd(z):
    w = z.randint(10, 99)
    return _text(f"Schreibe die Dezimalzahl {w} im BCD-Code (8421).", zm.bcd(w),
                 ["Beim BCD-Code wird JEDE Dezimalziffer einzeln in 4 Bit umgewandelt (nicht die ganze Zahl):",
                  f"{w // 10} = {w // 10:04b},  {w % 10} = {w % 10:04b}  ->  {zm.bcd(w)}",
                  f"Zum Vergleich rein binär wäre {w} = {zm.gruppiert(format(w, 'b'))} – das ist etwas anderes!"],
                 {"zeichen": "BCD", "text": "8 Bit"}, "basis2")


def _zk_muster(z):
    w = -z.randint(1, 128)
    e = zm.zweierkomplement(w, 8)
    return _text(f"Wie lautet das 8-Bit-Muster der Zahl {w} im Zweierkomplement?", e["bin"],
                 [f"1. Betrag binär: {abs(w)} = {e['betrag']}",
                  f"2. Alle Bits invertieren (Einerkomplement): {e['invertiert']}",
                  f"3. Plus 1: {e['plus_eins']}   (= 0x{e['hex']})",
                  f"Kontrolle: 256 − {abs(w)} = {256 + w} = {e['bin']}"],
                 {"zeichen": "Bitmuster", "text": "8 Bit"}, "basis2")


def _zk_lesen(z):
    muster = z.randint(128, 255)
    w = zm.als_vorzeichen(muster, 8)
    return _text(f"Das 8-Bit-Muster {_b(muster, 8)} ist eine Zahl MIT Vorzeichen (Zweierkomplement). Welchen "
                 "Dezimalwert hat es?", str(w),
                 ["Das höchste Bit (MSB) ist 1 -> die Zahl ist negativ. Das MSB hat die Wertigkeit −128:",
                  f"Wert = −128 + {muster - 128} = {w}",
                  f"Gleich gerechnet: Muster − 256 = {muster} − 256 = {w}"],
                 {"zeichen": "Dezimal", "text": "mit Vorzeichen"}, "basis10")


def _gray(z):
    w = z.randint(1, 15)
    g = zm.gray(w)
    return _text(f"Wie lautet die Dezimalzahl {w} im 4-Bit-Gray-Code?", f"{g:04b}",
                 [f"Binär: {w} = {w:04b}",
                  f"Gray = n XOR (n >> 1) = {w:04b} XOR {w >> 1:04b} = {g:04b}",
                  "Im Gray-Code unterscheiden sich benachbarte Zahlen in genau EINEM Bit (wichtig für Drehgeber)."],
                 {"zeichen": "Gray", "text": "4 Bit"}, "basis2")


def _ueberlauf(z):
    a, b = z.randint(-128, 127), z.randint(-128, 127)
    e = zm.addieren(a, b, 8)
    richtig = "Ja, Überlauf (V = 1)" if e["overflow"] else "Nein, kein Überlauf (V = 0)"
    falsch = ["Nein, kein Überlauf (V = 0)", "Ja, Überlauf (V = 1)"]
    return _auswahl(z, f"Ein 8-Bit-Rechenwerk addiert die vorzeichenbehafteten Zahlen {a} und {b} (Zweierkomplement). "
                    "Gibt es einen Überlauf (Ergebnis ausserhalb −128 … +127)?", richtig, falsch,
                    [f"{a} = {e['bin_a']},  {b} = {e['bin_b']}",
                     f"Summe der Muster (8 Bit): {e['bin_summe']}  ->  als signed gelesen: {e['signed']}",
                     f"Mathematisch richtig wäre {a + b}. " + ("Das liegt ausserhalb −128 … +127 -> Überlauf."
                                                             if e["overflow"] else "Das passt in 8 Bit -> kein Überlauf."),
                     "Merkregel: Überlauf nur, wenn zwei Zahlen mit GLEICHEM Vorzeichen ein Ergebnis mit anderem Vorzeichen geben."],
                    {"zeichen": "Überlauf?", "text": ""})


def _bitmaske(z):
    ops = zm.OPERATIONEN[:4]
    op = z.choice(ops)
    wert, maske = z.randint(0, 255), z.choice([0x0F, 0xF0, 0x01, 0x80, 0x3C, 0x81, 0x18, 0x55])
    e = zm.bitoperation(wert, maske, op)
    kurz = op.split(" (")[0]
    return _text(f"Ein Register hat den Wert 0x{wert:02X}. Was steht nach der Operation {kurz} mit der Maske "
                 f"0x{maske:02X} im Register? ({op.split('(')[1].rstrip(')')})", f"{e['ergebnis']:02X}",
                 [f"Wert:   {_b(wert, 8)}  (0x{wert:02X})", f"Maske:  {_b(maske, 8)}  (0x{maske:02X})",
                  f"{kurz}: {_b(e['ergebnis'], 8)}  =  0x{e['ergebnis']:02X}",
                  f"In C: {e['ausdruck']}" if e.get("ausdruck") else "Bit für Bit verknüpfen."],
                 {"zeichen": "Ergebnis (Hex)", "text": "z.B. 0x3C"}, "basis16")


# =============================================================================
# LOGIK UND GATTER
# =============================================================================
GATTER_ZEICHEN = {"AND": ("&", False), "OR": ("≥1", False), "NAND": ("&", True), "NOR": ("≥1", True),
                  "XOR": ("=1", False), "XNOR": ("=1", True), "NOT": ("1", True)}


def _gatter(z):
    name = z.choice(list(GATTER_ZEICHEN))
    n = 1 if name == "NOT" else z.choice([2, 2, 3])
    e = [z.randint(0, 1) for _ in range(n)]
    y = lm.gatter(name, e)
    namen = "ABC"[:n]
    regel = {"AND": "1 nur, wenn ALLE Eingänge 1 sind", "OR": "1, wenn MINDESTENS ein Eingang 1 ist",
             "NAND": "AND und danach invertiert: 0 nur, wenn alle Eingänge 1 sind",
             "NOR": "OR und danach invertiert: 1 nur, wenn alle Eingänge 0 sind",
             "XOR": "1, wenn eine UNGERADE Anzahl Eingänge 1 ist", "XNOR": "XOR invertiert: 1 bei gerader Anzahl Einsen",
             "NOT": "dreht den Eingang um"}[name]
    return _text(f"Welchen Wert hat der Ausgang Y des {name}-Gatters?", str(y),
                 [f"{name}: {regel}", "Eingänge: " + ", ".join(f"{v} = {x}" for v, x in zip(namen, e)), f"-> Y = {y}"],
                 {"zeichen": "Y", "text": "0 oder 1"}, "basis2",
                 gegeben=[(v, str(x)) for v, x in zip(namen, e)] + [("Gatter", name)])


def _s_gatter(p, g, ges):
    name = g["Gatter"]
    zeichen, inv = GATTER_ZEICHEN[name]
    eingaenge = [k for k in "ABC" if k in g]
    iec_gatter(p, 4.2, 2.4, zeichen, len(eingaenge), inv, namen=[f"{k} = {g[k]}" for k in eingaenge],
               ausgang=f"Y = {GESUCHT}")
    p.text(4.2, 4.4, f"{name} (Schaltzeichen nach IEC)", "center", klein=True, farbe=p.leise)


AUSDRUECKE = ["A·B + C", "A + B·C", "¬A·B + A·¬C", "(A + B)·¬C", "A ⊕ B + C", "¬(A·B) + C", "A·¬B·C + ¬A·B",
              "(A + ¬B)·(B + C)", "¬(A + B)·C", "A·B + ¬B·C"]


def _ausdruck(z):
    text = z.choice(AUSDRUECKE)
    baum = lm.parsen(text)
    bel = {v: z.randint(0, 1) for v in "ABC"}
    y = lm.auswerten(baum, bel)
    return _text(f"Berechne Y = {text} für die angegebene Belegung. (¬ = NICHT, · = UND, + = ODER, ⊕ = XOR)", str(y),
                 ["Reihenfolge wie in der Mathematik: zuerst Klammern und ¬, dann · (UND), zuletzt + (ODER).",
                  "Belegung: " + ", ".join(f"{k} = {v}" for k, v in bel.items()),
                  f"Einsetzen in {text}  ->  Y = {y}"],
                 {"zeichen": "Y", "text": "0 oder 1"}, "basis2", gegeben=[(k, str(v)) for k, v in bel.items()])


def _de_morgan(z):
    a, b = z.sample(["A", "B", "C", "D"], 2)
    if z.random() < 0.5:
        frage, richtig = f"¬({a}·{b})", f"¬{a} + ¬{b}"
        falsch = [f"¬{a}·¬{b}", f"{a} + {b}", f"¬{a}·{b}"]
        regel = "Ein Strich über einem UND wird zu einem ODER der einzeln negierten Variablen."
    else:
        frage, richtig = f"¬({a} + {b})", f"¬{a}·¬{b}"
        falsch = [f"¬{a} + ¬{b}", f"{a}·{b}", f"¬{a} + {b}"]
        regel = "Ein Strich über einem ODER wird zu einem UND der einzeln negierten Variablen."
    assert lm.vergleichen(frage, richtig)[0] and not any(lm.vergleichen(frage, f)[0] for f in falsch)
    return _auswahl(z, f"Welcher Ausdruck ist gleichwertig mit {frage}? (De Morgan)", richtig, falsch,
                    ["Regel von De Morgan: ¬(A·B) = ¬A + ¬B  und  ¬(A + B) = ¬A·¬B", regel,
                     f"{frage} = {richtig}  (Kontrolle mit Wahrheitstabelle: in allen 4 Zeilen gleich)"],
                    {"zeichen": "gleichwertig", "text": ""})


def _minterme(z):
    text = z.choice(AUSDRUECKE)
    zeilen = lm.tabelle(lm.parsen(text), ["A", "B", "C"])
    m = [k for k, (_bel, y) in enumerate(zeilen) if y]
    loesung = ", ".join(str(k) for k in m) if m else "keine"
    return _text(f"Für welche Zeilen der Wahrheitstabelle ist Y = {text} gleich 1? Gib die Nummern der Minterme an "
                 "(A ist das höchstwertige Bit: Zeile 5 = A B C = 1 0 1).", loesung,
                 ["Alle 8 Belegungen von A B C durchgehen (000 = Zeile 0 … 111 = Zeile 7) und Y ausrechnen:",
                  " · ".join(f"{k}: {''.join(map(str, bel))}→{y}" for k, (bel, y) in enumerate(zeilen)),
                  f"Y = 1 in den Zeilen {loesung}  ->  Y = Σm({loesung})"],
                 {"zeichen": "Minterme", "text": "z.B. 1, 3, 5"}, "menge")


def _kv_minimal(z):
    namen = ["A", "B", "C"]
    while True:
        m = sorted(z.sample(range(8), z.randint(3, 5)))
        f = lm.minimal_formen(m, namen)
        if f["min_dnf"] not in ("0", "1") and len(f["terme"]) >= 2:
            break
    richtig = f["min_dnf"]
    falsch = []
    for k in range(8):                                               # andere Funktionen: eine Zeile mehr/weniger
        andere = sorted(set(m) ^ {k})
        if andere and len(andere) < 8:
            t = lm.minimal_formen(andere, namen)["min_dnf"]
            if t not in (richtig, "0", "1") and not lm.vergleichen(t, richtig)[0]:
                falsch.append(t)
        if len(falsch) >= 3:
            break
    tabelle = {"kopf": ["Zeile", "A", "B", "C", "Y"],
               "zeilen": [[str(k), *f"{k:03b}", "1" if k in m else "0"] for k in range(8)]}
    return _auswahl(z, "Gegeben ist die Wahrheitstabelle. Welcher Ausdruck ist die MINIMALE disjunktive Form "
                    "(KV-Diagramm: möglichst grosse Päckchen)?", richtig, falsch,
                    [f"Einsen in den Zeilen {', '.join(map(str, m))}",
                     "Im KV-Diagramm benachbarte Einsen zu möglichst grossen Päckchen (2, 4, 8) zusammenfassen – "
                     "in jedem Päckchen fällt die Variable weg, die sich ändert.",
                     f"Ergebnis: Y = {richtig}"],
                    {"zeichen": "Y", "text": "minimale Form"}, tabelle=tabelle)


# =============================================================================
# SCHALTNETZE
# =============================================================================
def _volladdierer(z):
    a, b, c = (z.randint(0, 1) for _ in range(3))
    s, cout = sn.volladdierer(a, b, c)
    return _text("Ein Volladdierer bekommt A, B und den Übertrag C_ein. Gib C_aus und S als zweistellige Binärzahl "
                 "an (C_aus zuerst, z.B. 10).", f"{cout}{s}",
                 [f"Einfach zählen: A + B + C_ein = {a} + {b} + {c} = {a + b + c}",
                  f"{a + b + c} binär = {cout}{s}  ->  C_aus = {cout}, S = {s}",
                  "Formeln: S = A ⊕ B ⊕ C_ein,  C_aus = A·B + C_ein·(A ⊕ B)"],
                 {"zeichen": "C_aus S", "text": "2 Bit"}, "basis2",
                 gegeben=[("A", str(a)), ("B", str(b)), ("C_ein", str(c))])


def _s_volladdierer(p, g, ges):
    kasten_baustein(p, 3.4, 0.6, 6.4, 4.8, "VA (Σ)",
                    links=[("A", f"A = {g['A']}"), ("B", f"B = {g['B']}"), ("Cin", f"C_ein = {g['C_ein']}")],
                    rechts=[("S", f"S = {GESUCHT}"), ("Cout", f"C_aus = {GESUCHT}")])


def _mux(z):
    daten = [z.randint(0, 1) for _ in range(4)]
    s = z.randint(0, 3)
    y = sn.mux(daten, s)
    return _text("Ein 4:1-Multiplexer hat die Dateneingänge D0 … D3 und die Auswahleingänge S1 S0. Welcher Wert "
                 "liegt am Ausgang Y?", str(y),
                 [f"S1 S0 = {s:02b} ist binär die Zahl {s} -> der MUX schaltet D{s} durch.",
                  f"D{s} = {y}  ->  Y = {y}"],
                 {"zeichen": "Y", "text": "0 oder 1"}, "basis2",
                 gegeben=[(f"D{i}", str(v)) for i, v in enumerate(daten)] + [("S1 S0", f"{s:02b}")])


def _s_mux(p, g, ges):
    kasten_baustein(p, 3.6, 0.6, 6.4, 5.4, "MUX",
                    links=[(f"D{i}", f"D{i} = {g[f'D{i}']}") for i in range(4)],
                    rechts=[("Y", f"Y = {GESUCHT}")],
                    unten=[(4.4, "S1", g["S1 S0"][0]), (5.6, "S0", g["S1 S0"][1])])


def _decoder(z):
    adr = z.randint(0, 7)
    pegel = sn.decoder(adr, 3, True, True)
    aktiv = pegel.index(0)
    richtig = f"Y{aktiv} ist LOW, alle anderen HIGH"
    falsch = [f"Y{(aktiv + 1) % 8} ist LOW, alle anderen HIGH", f"Y{aktiv} ist HIGH, alle anderen LOW",
              f"Y{7 - aktiv if 7 - aktiv != aktiv else (aktiv + 2) % 8} ist LOW, alle anderen HIGH"]
    return _auswahl(z, f"Ein 3-zu-8-Decoder (wie 74HC138, Ausgänge aktiv LOW, freigegeben) bekommt die Adresse "
                    f"A2 A1 A0 = {adr:03b}. Welche Ausgänge haben welchen Pegel?", richtig, falsch,
                    [f"A2 A1 A0 = {adr:03b} = {adr} dezimal -> Ausgang Y{adr} wird ausgewählt.",
                     "Aktiv LOW heisst: Der ausgewählte Ausgang geht auf 0, alle anderen bleiben 1.",
                     "Typische Anwendung: Chip-Select für 8 Bausteine an einem Bus."],
                    {"zeichen": "Ausgänge", "text": ""}, gegeben=[("A2 A1 A0", f"{adr:03b}")])


def _s_decoder(p, g, ges):
    adr = g["A2 A1 A0"]
    kasten_baustein(p, 3.4, 0.4, 6.4, 6.2, "3:8",
                    links=[("A0", f"A0 = {adr[2]}"), ("A1", f"A1 = {adr[1]}"), ("A2", f"A2 = {adr[0]}")],
                    rechts=[(f"Y{i}", "") for i in range(8)])
    p.text(7.6, 3.3, f"Pegel = {GESUCHT}", "w", fett=True, farbe="#F59E0B")
    p.text(4.9, 6.8, "Ausgänge aktiv LOW", "center", klein=True, farbe=p.leise)


SEGMENTE = {"a": ((0.25, 0), (0.75, 0)), "b": ((0.8, 0.05), (0.8, 0.95)), "c": ((0.8, 1.05), (0.8, 1.95)),
            "d": ((0.25, 2), (0.75, 2)), "e": ((0.2, 1.05), (0.2, 1.95)), "f": ((0.2, 0.05), (0.2, 0.95)),
            "g": ((0.25, 1), (0.75, 1))}


def _siebensegment(z):
    ziffer = z.randint(0, 9)
    e = sn.siebensegment(ziffer)
    return _text(f"Welche Segmente einer 7-Segment-Anzeige leuchten bei der Ziffer {ziffer}? Gib die Buchstaben an "
                 "(Segmente a … g wie im Bild).", e["segmente"],
                 [f"Ziffer {ziffer} zeichnen und die benötigten Striche ablesen: {', '.join(e['segmente'])}",
                  f"Bei gemeinsamer Kathode sind diese Segmente HIGH, bei gemeinsamer Anode LOW."],
                 {"zeichen": "Segmente", "text": "z.B. bcfg"}, "buchstaben", gegeben=[("Ziffer", str(ziffer))])


def _s_siebensegment(p, g, ges):
    x0, y0, s = 3.0, 0.8, 2.0                                        # Ursprung, Grösse
    for name, ((xa, ya), (xb, yb)) in SEGMENTE.items():
        p.leitung((x0 + xa * s, y0 + ya * s), (x0 + xb * s, y0 + yb * s), farbe=p.leise, dick=p.dick + 4)
        mx, my = x0 + (xa + xb) / 2 * s, y0 + (ya + yb) / 2 * s
        dx = 0.35 if name in "bc" else -0.35 if name in "ef" else 0
        dy = -0.3 if name == "a" else 0.3 if name == "d" else 0.32 if name == "g" else 0
        p.text(mx + dx, my + dy, name, "center", fett=True)
    p.text(6.6, 2.8, f"Ziffer {g['Ziffer']}", "w", fett=True)
    p.text(6.6, 3.4, f"Segmente = {GESUCHT}", "w", fett=True, farbe="#F59E0B")


def _laufzeit(z):
    bits = z.choice([4, 8, 16, 32])
    tc = z.choice([5e-9, 8e-9, 10e-9, 15e-9])
    ts = tc + z.choice([2e-9, 5e-9])
    e = sn.laufzeit(bits, tc, ts)
    return (f"Ein {bits}-Bit-Ripple-Carry-Addierer besteht aus {bits} Volladdierern. Jeder braucht t_carry bis zum "
            "Übertrag und t_summe bis zur Summe. Wie lange dauert es im ungünstigsten Fall, bis das höchste Summenbit "
            "stimmt?",
            [("n", float(bits), "zahl"), ("t_carry", tc, "zeit"), ("t_summe", ts, "zeit")],
            ("t_ges", "zeit", "Laufzeit bis zum höchsten Summenbit"), e["t_summe_ges"],
            ["Ungünstigster Fall: Der Übertrag läuft durch alle Stufen, erst dann stimmt das höchste Bit.",
             "t_ges = (n − 1) · t_carry + t_summe",
             f"t_ges = {bits - 1} · {_f(tc, 'zeit')} + {_f(ts, 'zeit')} = {_f(e['t_summe_ges'], 'zeit')}",
             f"Damit höchstens f ≈ 1 / t_ges = {_f(1 / e['t_summe_ges'], 'frequenz')} – darum gibt es Carry-Lookahead-Addierer."])


# =============================================================================
# SCHALTWERKE
# =============================================================================
def _jk(z):
    q, j, k = (z.randint(0, 1) for _ in range(3))
    q_neu, hinweis = sw.naechster_zustand("JK-Flipflop", q, {"J": j, "K": k})
    return _text("Ein JK-Flipflop (taktflankengesteuert) hat vor der Taktflanke den Zustand Q. Welchen Zustand hat "
                 "es NACH der steigenden Taktflanke?", str(q_neu),
                 ["Wahrheitstabelle JK: J=0 K=0 speichern · J=1 K=0 setzen · J=0 K=1 rücksetzen · J=1 K=1 toggeln",
                  f"J = {j}, K = {k}: {hinweis}  ->  Q⁺ = {q_neu}",
                  "Formel: Q⁺ = J·¬Q + ¬K·Q"],
                 {"zeichen": "Q⁺", "text": "0 oder 1"}, "basis2",
                 gegeben=[("Q", str(q)), ("J", str(j)), ("K", str(k))])


def _s_jk(p, g, ges):
    kasten_baustein(p, 3.6, 0.6, 6.4, 5.0, "JK-FF",
                    links=[("J", f"J = {g['J']}"), ("C", "Takt ↑"), ("K", f"K = {g['K']}")],
                    rechts=[("Q", f"Q⁺ = {GESUCHT}"), ("Q̅", "")])
    p.text(5.0, 5.6, f"vorher: Q = {g['Q']}", "center", klein=True, farbe=p.leise)


def _zaehler(z):
    start = z.randint(0, 15)
    n = z.randint(3, 12)
    folge = sw.zaehler_folge(4, start=start, schritte=n)
    ende = folge[-1]
    return _text(f"Ein 4-Bit-Binärzähler (aufwärts, zählt 0 … 15 und dann wieder 0) steht auf {_b(start, 4)}. "
                 f"Welchen Stand hat er nach {n} Taktimpulsen?", f"{ende:04b}",
                 [f"Start {start}, plus {n} = {start + n}" + (f", nach 15 geht es bei 0 weiter: ({start + n}) mod 16 = {ende}"
                                                           if start + n > 15 else ""),
                  "Folge: " + " → ".join(str(x) for x in folge),
                  f"Ergebnis: {ende} = {ende:04b}"],
                 {"zeichen": "Zählerstand", "text": "4 Bit"}, "basis2")


def _mod_zaehler(z):
    m = z.choice([5, 6, 10, 12])
    start = z.randint(0, m - 1)
    n = z.randint(5, 25)
    folge = sw.zaehler_folge(4, modulo=m, start=start, schritte=n)
    return _text(f"Ein Modulo-{m}-Zähler zählt 0, 1, … {m - 1} und springt dann auf 0. Er steht auf {start}. Welchen "
                 f"Stand (dezimal) hat er nach {n} Taktimpulsen?", str(folge[-1]),
                 [f"Nach {m} Takten ist er wieder am selben Ort: ({start} + {n}) mod {m} = {(start + n) % m}",
                  "Folge: " + " → ".join(str(x) for x in folge)],
                 {"zeichen": "Zählerstand", "text": "dezimal"}, "basis10")


def _schieberegister(z):
    start = z.randint(0, 15)
    eingaben = [z.randint(0, 1) for _ in range(z.randint(2, 4))]
    folge = sw.schieberegister(4, eingaben, "seriell", start)
    ende = folge[-1]
    return _text(f"Ein 4-Bit-Schieberegister (seriell rein, parallel raus) enthält Q3 Q2 Q1 Q0 = {start:04b}. Bei jedem "
                 f"Takt wird der serielle Eingang in Q0 übernommen und alles eine Stelle Richtung Q3 geschoben. Eingänge "
                 f"nacheinander: {' , '.join(map(str, eingaben))}. Was steht danach in Q3 Q2 Q1 Q0?", f"{ende:04b}",
                 ["Bei jedem Takt: Q3 ← Q2, Q2 ← Q1, Q1 ← Q0, Q0 ← Eingang (das alte Q3 fällt heraus)"]
                 + [f"Takt {i + 1} (Eingang {e}): {folge[i + 1]:04b}" for i, e in enumerate(eingaben)],
                 {"zeichen": "Q3 Q2 Q1 Q0", "text": "4 Bit"}, "basis2",
                 gegeben=[("Start Q3…Q0", f"{start:04b}"), ("Eingänge", ", ".join(map(str, eingaben)))])


def _s_schieberegister(p, g, ges):
    start = g["Start Q3…Q0"]
    for i in range(4):                                               # Q0 links (erste Stufe), Q3 rechts
        x = 2.4 + i * 1.9
        kasten_baustein(p, x, 1.0, x + 1.3, 2.8, "D-FF")
        p.text(x + 0.65, 3.4, f"Q{i} = {start[3 - i]}", "center", klein=True)
        if i:
            p.leitung((x - 0.6, 1.9), (x, 1.9))
    p.leitung((1.2, 1.9), (2.4, 1.9))
    p.anschluss(1.2, 1.9)
    p.text(0.8, 1.3, f"seriell: {g['Eingänge']}", "w", klein=True)
    p.leitung((2.4 + 3 * 1.9 + 1.3, 1.9), (10.4, 1.9))
    p.text(5.6, 4.2, f"danach Q3 Q2 Q1 Q0 = {GESUCHT}", "center", fett=True, farbe="#F59E0B")


def _frequenzteiler(z):
    f = z.choice([1e6, 4e6, 8e6, 16e6, 32768.0, 50e3])
    stufen = z.randint(1, 6)
    e = sw.frequenzteiler(f, 2 ** stufen)
    return (f"Ein Takt läuft durch {stufen} hintereinandergeschaltete T-Flipflops (jedes teilt durch 2). Welche "
            "Frequenz hat das Signal am letzten Ausgang?",
            [("f_ein", f, "frequenz"), ("Anzahl Flipflops", float(stufen), "zahl")],
            ("f_aus", "frequenz", "Frequenz am letzten Flipflop"), e["f_aus"],
            ["Jedes Flipflop halbiert die Frequenz: f_aus = f_ein / 2ⁿ",
             f"f_aus = {_f(f, 'frequenz')} / 2^{stufen} = {_f(f, 'frequenz')} / {2 ** stufen} = {_f(e['f_aus'], 'frequenz')}",
             "Beispiel aus der Uhr: 32'768 Hz durch 15 Stufen = genau 1 Hz."])


def _fmax(z):
    tpd = z.choice([5e-9, 8e-9, 12e-9, 20e-9])
    tsu = z.choice([2e-9, 3e-9, 5e-9])
    tl = z.choice([5e-9, 10e-9, 15e-9, 25e-9])
    e = sw.fmax_synchron(tpd, tsu, tl)
    return ("Synchrones Schaltwerk: Zwischen zwei Flipflops liegt Logik. Wie hoch darf die Taktfrequenz höchstens "
            "sein? (Takt-Skew vernachlässigen)",
            [("t_pd (FF)", tpd, "zeit"), ("t_Logik", tl, "zeit"), ("t_setup", tsu, "zeit")],
            ("f_max", "frequenz", "höchste Taktfrequenz"), e["f_max"],
            ["Innerhalb einer Taktperiode muss das Signal vom FF-Ausgang durch die Logik zum nächsten FF laufen "
             "und t_setup vor der nächsten Flanke stabil sein:",
             f"T_min = t_pd + t_Logik + t_setup = {_f(tpd, 'zeit')} + {_f(tl, 'zeit')} + {_f(tsu, 'zeit')} = {_f(e['t_min'], 'zeit')}",
             f"f_max = 1 / T_min = {_f(e['f_max'], 'frequenz')}"])


# =============================================================================
# BUSSE, SPEICHER, PEGEL
# =============================================================================
def _paritaet(z):
    w = z.randint(0, 255)
    art_p = z.choice(["gerade", "ungerade"])
    p = bm.paritaetsbit(w, art_p)
    einsen = bin(w).count("1")
    return _text(f"Ein Datenbyte {_b(w, 8)} wird mit {art_p.upper()}R Parität übertragen. Welchen Wert hat das "
                 "Paritätsbit?", str(p),
                 [f"Anzahl Einsen im Byte: {einsen}",
                  f"{art_p.capitalize()} Parität: Einsen INKLUSIVE Paritätsbit müssen {art_p} sein -> Paritätsbit = {p}",
                  "Ein einzelnes falsches Bit fällt so auf – zwei falsche Bits aber nicht."],
                 {"zeichen": "Paritätsbit", "text": "0 oder 1"}, "basis2")


def _uart_dauer(z):
    baud = z.choice([9600, 19200, 57600, 115200])
    n = z.choice([10, 64, 100, 1000])
    par = z.choice(["keine", "gerade"])
    e = bm.uart_timing(baud, 8, par, 1)
    t = n * e["t_rahmen"]
    fmt = "8N1" if par == "keine" else "8E1"
    return (f"Über UART werden {n} Bytes im Format {fmt} mit der Baudrate {baud} Bd übertragen (ohne Pausen). "
            "Wie lange dauert das?",
            [("Baudrate", float(baud), "zahl"), ("Bytes", float(n), "zahl")], ("t", "zeit", "Übertragungsdauer"), t,
            [f"Ein Rahmen {fmt}: 1 Startbit + 8 Datenbits + {'0' if par == 'keine' else '1'} Paritätsbit + 1 Stoppbit "
             f"= {e['rahmen_bits']} Bit",
             f"Bitdauer: 1 / {baud} Bd = {_f(e['t_bit'], 'zeit')}",
             f"t = {n} · {e['rahmen_bits']} · {_f(e['t_bit'], 'zeit')} = {_f(t, 'zeit')}",
             f"Nutzdaten nur {e['nutzanteil'] * 100:.0f} % – der Rest sind Start-, Stopp- und Paritätsbits."])


def _speicher(z):
    a = z.choice([8, 10, 11, 12, 13, 15, 16])
    d = z.choice([8, 16])
    e = bm.speicher_organisation(a, d)
    return _text(f"Ein Speicher hat {a} Adressleitungen und {d} Datenleitungen. Wie viele Speicherplätze (Wörter) "
                 "hat er?", str(e["worte"]),
                 [f"Mit {a} Adressbits gibt es 2^{a} verschiedene Adressen: {e['worte']} Wörter",
                  f"Adressen 0x{0:0{e['hex_stellen']}X} … 0x{e['hoechste']:0{e['hex_stellen']}X}",
                  f"Kapazität: {e['worte']} · {d} Bit = {e['bits']} Bit = {int(e['bytes'])} Byte"],
                 {"zeichen": "Wörter", "text": "Anzahl"}, "basis10")


def _adressbits(z):
    kib = z.choice([1, 2, 4, 8, 16, 32, 64])
    worte = kib * 1024
    a = worte.bit_length() - 1
    return _text(f"Ein byteweise adressierter Speicher hat {kib} KiB (1 KiB = 1024 Byte). Wie viele Adressleitungen "
                 "braucht er?", str(a),
                 [f"{kib} KiB = {kib} · 1024 = {worte} Byte = {worte} Adressen",
                  f"2ⁿ = {worte}  ->  n = {a}  (2^10 = 1024, jede Verdopplung braucht 1 Bit mehr)"],
                 {"zeichen": "Adressleitungen", "text": "Anzahl"}, "basis10")


def _pegel(z):
    paare = [("ESP32 (3.3 V)", "74HC (5 V, Werte bei 4.5 V)"), ("ESP32 (3.3 V)", "74HCT (5 V, TTL-Eingang)"),
             ("ATmega328P / Uno (5 V)", "ESP32 (3.3 V)"), ("74LS (TTL, 5 V)", "74HC (5 V, Werte bei 4.5 V)"),
             ("74HC (5 V, Werte bei 4.5 V)", "74LS (TTL, 5 V)"), ("ESP32 (3.3 V)", "74LVC (3.3 V, 5-V-tolerant)"),
             ("ATmega328P / Uno (5 V)", "74LVC (3.3 V, 5-V-tolerant)")]
    sender, empf = z.choice(paare)
    e = pm.kompatibel(sender, empf)
    s, r = e["sender"], e["empfaenger"]
    if e["ok"]:
        richtig = "Ja, direkt verbindbar"
    elif e["ueberspannung"]:
        richtig = "Nein – die Spannung ist zu hoch für den Eingang"
    elif e["s_h"] < 0:
        richtig = "Nein – HIGH wird nicht sicher erkannt"
    else:
        richtig = "Nein – LOW wird nicht sicher erkannt"
    falsch = ["Ja, direkt verbindbar", "Nein – die Spannung ist zu hoch für den Eingang",
              "Nein – HIGH wird nicht sicher erkannt", "Nein – LOW wird nicht sicher erkannt"]
    tabelle = {"kopf": ["", "U_OH min", "U_OL max", "U_IH min", "U_IL max", "U_E max"],
               "zeilen": [[f"Sender: {sender}", _f(s["u_oh"], "spannung"), _f(s["u_ol"], "spannung"), "", "", ""],
                          [f"Empfänger: {empf}", "", "", _f(r["u_ih"], "spannung"), _f(r["u_il"], "spannung"),
                           _f(r["u_e_max"], "spannung")]]}
    return _auswahl(z, f"Darf ein Ausgang von {sender} direkt einen Eingang von {empf} ansteuern? (Werte aus den "
                    "Datenblättern in der Tabelle; Sender-Versorgung = Höhe des HIGH-Pegels)", richtig, falsch,
                    [f"HIGH: U_OH,min = {_f(s['u_oh'], 'spannung')} ≥ U_IH,min = {_f(r['u_ih'], 'spannung')}?  "
                     f"Störabstand S_H = {_f(e['s_h'], 'spannung')}",
                     f"LOW: U_OL,max = {_f(s['u_ol'], 'spannung')} ≤ U_IL,max = {_f(r['u_il'], 'spannung')}?  "
                     f"Störabstand S_L = {_f(e['s_l'], 'spannung')}",
                     f"Spannung: U_B Sender = {_f(s['u_b'], 'spannung')}, Eingang erträgt höchstens {_f(r['u_e_max'], 'spannung')}",
                     f"-> {e['rat']}"],
                    {"zeichen": "verbindbar?", "text": ""}, tabelle=tabelle)


# =============================================================================
# ANMELDEN (id, Titel, Thema, Stufe, Wissensseite, Erzeuger, Schema oder None)
# =============================================================================
_LISTE = [
    ("dez_bin", "Dezimal → Binär", ZAHLEN, 1, "zahlensysteme_codes", _dez_bin, None),
    ("bin_dez", "Binär → Dezimal", ZAHLEN, 1, "zahlensysteme_codes", _bin_dez, None),
    ("hex_bin", "Hexadezimal → Binär", ZAHLEN, 1, "zahlensysteme_codes", _hex_bin, None),
    ("bits_noetig", "Wie viele Bit braucht es?", ZAHLEN, 1, "zahlensysteme_codes", _bits_noetig, None),
    ("dez_hex", "Dezimal → Hexadezimal", ZAHLEN, 2, "zahlensysteme_codes", _dez_hex, None),
    ("bcd", "BCD-Code", ZAHLEN, 2, "zahlensysteme_codes", _bcd, None),
    ("zk_muster", "Zweierkomplement: Bitmuster", ZAHLEN, 2, "zweierkomplement_ueberlauf", _zk_muster, None),
    ("zk_lesen", "Zweierkomplement: Wert lesen", ZAHLEN, 2, "zweierkomplement_ueberlauf", _zk_lesen, None),
    ("bitmaske", "Bitmasken: AND, OR, XOR", ZAHLEN, 2, "bitmasken", _bitmaske, None),
    ("gray", "Gray-Code", ZAHLEN, 3, "zahlensysteme_codes", _gray, None),
    ("ueberlauf", "Überlauf beim Addieren (signed)", ZAHLEN, 3, "zweierkomplement_ueberlauf", _ueberlauf, None),
    ("gatter_ausgang", "Gatter: Ausgang bestimmen", LOGIK, 1, "logikgatter", _gatter, (8.6, 5.0, _s_gatter)),
    ("ausdruck_wert", "Boolescher Ausdruck: Wert berechnen", LOGIK, 2, "boolesche_algebra", _ausdruck, None),
    ("de_morgan", "Regel von De Morgan", LOGIK, 2, "boolesche_algebra", _de_morgan, None),
    ("minterme", "Wahrheitstabelle: Minterme", LOGIK, 3, "normalformen", _minterme, None),
    ("kv_minimal", "KV-Diagramm: minimale Form", LOGIK, 4, "kv_diagramme", _kv_minimal, None),
    ("volladdierer", "Volladdierer", NETZE, 2, "addierer", _volladdierer, (10, 5.4, _s_volladdierer)),
    ("mux", "Multiplexer 4:1", NETZE, 2, "multiplexer", _mux, (10, 7.0, _s_mux)),
    ("decoder", "Decoder 3:8 (aktiv LOW)", NETZE, 2, "decoder_encoder", _decoder, (10, 7.2, _s_decoder)),
    ("siebensegment", "7-Segment-Anzeige", NETZE, 3, "decoder_encoder", _siebensegment, (10, 5.4, _s_siebensegment)),
    ("ripple_laufzeit", "Ripple-Carry-Addierer: Laufzeit", NETZE, 4, "addierer", _laufzeit, None),
    ("jk_flipflop", "JK-Flipflop: nächster Zustand", WERKE, 2, "flipflops", _jk, (10, 6.2, _s_jk)),
    ("zaehler_stand", "Binärzähler: Stand nach n Takten", WERKE, 2, "zaehler", _zaehler, None),
    ("frequenzteiler", "Frequenzteiler mit Flipflops", WERKE, 2, "zaehler", _frequenzteiler, None),
    ("mod_zaehler", "Modulo-Zähler", WERKE, 3, "zaehler_entwurf", _mod_zaehler, None),
    ("schieberegister", "Schieberegister", WERKE, 3, "schieberegister", _schieberegister, (11, 4.8, _s_schieberegister)),
    ("fmax", "Synchrones Schaltwerk: f_max", WERKE, 4, "zaehler_entwurf", _fmax, None),
    ("paritaet", "Paritätsbit", BUSSE, 2, "uart", _paritaet, None),
    ("speicher_worte", "Speicher: Anzahl Wörter", BUSSE, 2, "speicher", _speicher, None),
    ("adressbits", "Speicher: Anzahl Adressleitungen", BUSSE, 3, "speicher", _adressbits, None),
    ("uart_dauer", "UART: Übertragungsdauer", BUSSE, 3, "uart", _uart_dauer, None),
    ("pegel_kompatibel", "Logikpegel: direkt verbindbar?", BUSSE, 3, "logikpegel_stoerabstand", _pegel, None),
]
for _id, _titel, _thema, _stufe, _seite, _erz, _schema in _LISTE:
    art(_id, _titel, D, _thema, _stufe, [(D, _seite)], _erz)
    if _schema:
        SCHEMAS[_id] = _schema
