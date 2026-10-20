# =============================================================================
# uebungen/programmieren.py
# -----------------------------------------------------------------------------
# ÜBUNGEN PROGRAMMIEREN (Stufen 1–4): "Was gibt das Programm aus?", Datentypen, Schleifen, Funktionen,
# Listen/Strings/Dictionaries, Rekursion, Scope, Referenzen, Fehlerbehandlung, Klassen - Python und C.
#
# PYTHON: Die Aufgabe ist ein kleines Programm aus einer Vorlage mit Zufallswerten. Die richtige Ausgabe
# wird nicht von Hand berechnet, sondern das Programm wird WIRKLICH ausgeführt (_ausgabe) - so stimmt die
# Lösung immer genau. Ausgeführt wird nur Code aus diesen Vorlagen (nie eine Eingabe von aussen), in einem
# Namensraum mit wenigen erlaubten Funktionen (ERLAUBT).
# C: Ergebnis mit den Regeln von C nachgerechnet (Ganzzahldivision schneidet ab, uint8_t rechnet modulo 256,
# i++ liefert den alten Wert) - die Regel steht jeweils im Lösungsweg.
#
# Antworten: mehrere ausgegebene Zeilen mit Leerzeichen trennen (Zeilenumbrüche zählen wie Leerzeichen).
#
# WER RUFT DAS AUF?  uebungen/aufgaben.py (lädt alle Übungs-Module)
# =============================================================================

import contextlib
import io

from uebungen.kern import art                                        # -> uebungen/kern.py

P = "Programmieren"
GRUND, KONTROLLE, FUNK, DATEN, OOP, FORT = ("Grundlagen", "Kontrollstrukturen", "Funktionen", "Datenstrukturen",
                                            "Objektorientierung", "Fortgeschritten")
ERLAUBT = {name: __builtins__[name] if isinstance(__builtins__, dict) else getattr(__builtins__, name)
           for name in ("print", "range", "len", "str", "int", "float", "bool", "list", "dict", "sum", "max", "min",
                        "type", "isinstance", "ValueError", "ZeroDivisionError", "IndexError", "KeyError",
                        "Exception", "super", "object", "__build_class__", "abs", "round", "sorted", "enumerate")}


def _ausgabe(code):
    """Führt ein Vorlagen-Programm aus und gibt seine Ausgabe zurück (Zeilenumbrüche -> Leerzeichen)."""
    puffer = io.StringIO()
    with contextlib.redirect_stdout(puffer):
        exec(code, {"__builtins__": ERLAUBT, "__name__": "aufgabe"})          # noqa: S102 - nur eigene Vorlagen
    return " ".join(puffer.getvalue().split())


def _programm(code, weg, sprache="python", text="Was gibt das Programm aus?", loesung=None):
    ausgabe = loesung if loesung is not None else _ausgabe(code)
    return {"text": text + " (Mehrere Zeilen mit Leerzeichen trennen.)", "antwort": "text", "loesung": ausgabe,
            "weg": weg, "gesucht": {"zeichen": "Ausgabe", "text": "genau wie auf dem Bildschirm"},
            "vergleich": "genau", "code": code, "sprache": sprache}


def _auswahl(z, text, richtig, falsch, weg, code=None, sprache="python"):
    optionen = [richtig] + [f for f in dict.fromkeys(falsch) if f != richtig]
    z.shuffle(optionen)
    return {"text": text, "antwort": "auswahl", "loesung": richtig, "optionen": optionen, "weg": weg,
            "gesucht": {"zeichen": "Antwort", "text": ""}, "code": code, "sprache": sprache}


# =============================================================================
# GRUNDLAGEN
# =============================================================================
def _rechnen(z):
    a, b, c = z.randint(2, 9), z.randint(2, 9), z.randint(2, 5)
    code = f"a = {a}\nb = {b}\nc = {c}\nprint(a + b * c)\nprint((a + b) * c)"
    return _programm(code, ["Punkt vor Strich: zuerst b * c, dann + a.",
                            f"a + b * c = {a} + {b * c} = {a + b * c}",
                            f"Mit Klammern zuerst a + b: ({a + b}) * {c} = {(a + b) * c}"])


def _ganzzahl(z):
    a, b = z.randint(10, 60), z.randint(3, 9)
    code = f"a = {a}\nb = {b}\nprint(a // b)\nprint(a % b)\nprint(a / b > {a // b})"
    return _programm(code, [f"// ist die Ganzzahldivision: {a} // {b} = {a // b} (Nachkommastellen fallen weg)",
                            f"% ist der Rest (Modulo): {a} = {a // b} · {b} + {a % b}",
                            f"/ rechnet mit Komma: {a / b:.4g} > {a // b} ist {a / b > a // b}"])


def _typ(z):
    literale = [("42", "int"), ("4.2", "float"), ("'42'", "str"), ("True", "bool"), ("10 / 2", "float"),
                ("10 // 2", "int"), ("[4, 2]", "list"), ("3 > 2", "bool"), ("str(7)", "str"), ("int('7')", "int")]
    lit, typ = z.choice(literale)
    assert type(eval(lit, {"__builtins__": ERLAUBT})).__name__ == typ                 # noqa: S307 - feste Liste
    return _auswahl(z, f"Welchen Datentyp hat der Ausdruck {lit} in Python?", typ,
                    ["int", "float", "str", "bool", "list"],
                    [f"type({lit}) ergibt <class '{typ}'>",
                     "Merke: / liefert in Python immer float (auch 10 / 2 = 5.0), // liefert int; Vergleiche liefern bool."],
                    code=f"print(type({lit}))")


def _verketten(z):
    wert = z.randint(2, 48)
    einheit = z.choice(["V", "mA", "Ohm"])
    code = f"wert = {wert}\neinheit = '{einheit}'\nprint('Messwert: ' + str(wert) + ' ' + einheit)\nprint(str(wert) * 2)"
    return _programm(code, ["+ zwischen Texten hängt sie zusammen; die Zahl muss zuerst mit str() zu Text werden.",
                            f"str({wert}) * 2 wiederholt den TEXT: '{wert}' + '{wert}' = {str(wert) * 2}"])


def _umwandeln(z):
    a, b = z.randint(10, 99), z.randint(2, 9)
    code = f"text = '{a}'\nzahl = {b}\nprint(int(text) + zahl)\nprint(text + str(zahl))\nprint(float(zahl) / 2)"
    return _programm(code, [f"int('{a}') macht aus dem Text die Zahl {a}: {a} + {b} = {a + b}",
                            f"Text + Text wird aneinandergehängt: '{a}' + '{b}' = {a}{b}",
                            f"float({b}) / 2 = {float(b) / 2}"])


# =============================================================================
# KONTROLLSTRUKTUREN
# =============================================================================
def _if(z):
    t = z.randint(-5, 45)
    code = (f"temperatur = {t}\nif temperatur < 0:\n    print('Frost')\nelif temperatur < 25:\n    print('normal')\n"
            f"else:\n    print('warm')\nprint('fertig')")
    return _programm(code, ["if / elif / else: Es wird nur der ERSTE zutreffende Zweig ausgeführt.",
                            f"temperatur = {t}: " + ("< 0 -> Frost" if t < 0 else "< 25 -> normal" if t < 25 else "≥ 25 -> warm"),
                            "'fertig' steht nicht eingerückt -> wird immer ausgegeben."])


def _for_summe(z):
    a, b, s = z.randint(0, 3), z.randint(6, 12), z.choice([1, 2, 3])
    code = f"summe = 0\nfor i in range({a}, {b}, {s}):\n    summe = summe + i\nprint(summe)"
    werte = list(range(a, b, s))
    return _programm(code, [f"range({a}, {b}, {s}) zählt von {a} bis VOR {b} in {s}er-Schritten: {werte}",
                            f"Summe = {' + '.join(map(str, werte))} = {sum(werte)}"])


def _while(z):
    start, faktor, grenze = z.randint(1, 3), 2, z.choice([20, 50, 100, 200])
    code = f"x = {start}\nn = 0\nwhile x < {grenze}:\n    x = x * {faktor}\n    n = n + 1\nprint(n, x)"
    return _programm(code, ["Die Schleife läuft, solange die Bedingung am Anfang wahr ist.",
                            f"x verdoppelt sich: {start}" + "".join(f" → {start * 2 ** k}" for k in range(1, _ausgabe_n(start, grenze) + 1)),
                            "print mit zwei Werten gibt sie mit Leerzeichen getrennt aus."])


def _ausgabe_n(start, grenze):
    n, x = 0, start
    while x < grenze:
        x, n = x * 2, n + 1
    return n


def _break_continue(z):
    n = z.randint(6, 10)
    stopp = z.randint(4, n - 1)
    teiler = z.choice([2, 3])
    code = (f"for i in range({n}):\n    if i % {teiler} == 0:\n        continue\n    if i == {stopp}:\n        break\n"
            f"    print(i)")
    return _programm(code, [f"continue: Rest der Schleife überspringen, wenn i durch {teiler} teilbar ist.",
                            f"break: Schleife ganz verlassen, sobald i = {stopp} erreicht ist (und {stopp} nicht durch {teiler} teilbar ist).",
                            "Ausgegeben werden nur die übrigen Werte davor."])


def _c_for(z):
    a, b, s = z.randint(0, 5), z.randint(12, 30), z.choice([2, 3, 4, 5])
    n = len(range(a, b, s))
    code = f"int n = 0;\nfor (int i = {a}; i < {b}; i += {s}) {{\n    n++;\n}}\nprintf(\"%d\\n\", n);"
    return _programm(code, [f"i läuft {a}, {a + s}, {a + 2 * s} … solange i < {b}:",
                            f"Werte: {list(range(a, b, s))}  ->  {n} Durchläufe"], sprache="c",
                     text="Was gibt dieses C-Programmstück aus?", loesung=str(n))


# =============================================================================
# FUNKTIONEN
# =============================================================================
def _funktion(z):
    k, x, y = z.randint(2, 5), z.randint(2, 6), z.randint(3, 9)
    code = (f"def leistung(u, i={k}):\n    return u * i\n\nprint(leistung({x}))\nprint(leistung({x}, {y}))\n"
            f"print(leistung(i={y}, u=1))")
    return _programm(code, [f"i hat den Standardwert {k}: leistung({x}) = {x} · {k} = {x * k}",
                            f"Zwei Argumente: leistung({x}, {y}) = {x * y}",
                            f"Benannte Argumente in beliebiger Reihenfolge: u = 1, i = {y} -> {y}"])


def _rekursion(z):
    if z.random() < 0.5:
        n = z.randint(3, 7)
        code = f"def fak(n):\n    if n <= 1:\n        return 1\n    return n * fak(n - 1)\n\nprint(fak({n}))"
        weg = [f"fak({n}) = {n} · fak({n - 1}) = … = {' · '.join(str(k) for k in range(n, 0, -1))}",
               "Abbruchbedingung n <= 1 verhindert eine endlose Rekursion."]
    else:
        n = z.randint(4, 9)
        code = f"def fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n\nprint(fib({n}))"
        reihe, a, b = [], 0, 1
        for _ in range(n + 1):
            reihe.append(a)
            a, b = b, a + b
        weg = [f"Fibonacci: jede Zahl ist die Summe der zwei vorherigen: {', '.join(map(str, reihe))}",
               f"fib({n}) ist die Zahl an Stelle {n} (gezählt ab 0)."]
    return _programm(code, weg)


def _scope(z):
    a, b = z.randint(1, 9), z.randint(10, 20)
    code = (f"x = {a}\n\ndef aendern():\n    x = {b}\n    print(x)\n\ndef global_aendern():\n    global x\n    x = x + 1\n\n"
            f"aendern()\nprint(x)\nglobal_aendern()\nprint(x)")
    return _programm(code, [f"In aendern() ist x eine NEUE lokale Variable: Ausgabe {b}, das globale x bleibt {a}.",
                            f"Danach print(x) ausserhalb: {a}",
                            f"global x: die Funktion ändert das globale x -> {a + 1}"])


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================
def _index(z):
    werte = z.sample(range(10, 99), 5)
    i = z.randint(0, 4)
    code = f"werte = {werte}\nprint(werte[{i}])\nprint(werte[-1])\nprint(len(werte))"
    return _programm(code, [f"Indizes beginnen bei 0: werte[{i}] = {werte[i]}",
                            f"Negativer Index zählt von hinten: werte[-1] = {werte[-1]}",
                            "len() = Anzahl Elemente = 5"])


def _slicing(z):
    wort = z.choice(["Spannung", "Widerstand", "Kondensator", "Transistor", "Frequenz"])
    a = z.randint(0, 3)
    b = z.randint(a + 2, len(wort) - 1)
    code = f"wort = '{wort}'\nprint(wort[{a}:{b}])\nprint(wort[:3].upper())\nprint(wort[::-1][:2])"
    return _programm(code, [f"wort[{a}:{b}]: Zeichen ab Index {a} bis VOR Index {b} -> {wort[a:b]}",
                            f"wort[:3] = {wort[:3]}, .upper() macht Grossbuchstaben -> {wort[:3].upper()}",
                            f"wort[::-1] dreht um ({wort[::-1]}), davon die ersten 2 -> {wort[::-1][:2]}"])


def _dict(z):
    r, u = z.choice([100, 220, 470, 1000]), z.choice([5, 12, 24])
    code = (f"bauteil = {{'typ': 'Widerstand', 'wert': {r}}}\nbauteil['spannung'] = {u}\nbauteil['wert'] = bauteil['wert'] * 2\n"
            f"print(len(bauteil))\nprint(bauteil['wert'])\nprint('farbe' in bauteil)")
    return _programm(code, ["Ein neuer Schlüssel ('spannung') wird einfach angelegt -> jetzt 3 Einträge.",
                            f"'wert' wird überschrieben: {r} · 2 = {r * 2}",
                            "'farbe' in bauteil prüft, ob es den Schlüssel gibt -> False"])


def _listcomp(z):
    n, t = z.randint(6, 11), z.choice([2, 3])
    code = f"quadrate = [x * x for x in range({n}) if x % {t} == 0]\nprint(quadrate)\nprint(sum(quadrate))"
    q = [x * x for x in range(n) if x % t == 0]
    return _programm(code, [f"x läuft 0 … {n - 1}, genommen werden nur Vielfache von {t}: {[x for x in range(n) if x % t == 0]}",
                            f"Davon jeweils x * x: {q}, Summe = {sum(q)}"])


def _alias(z):
    a = z.sample(range(1, 9), 3)
    neu = z.randint(10, 20)
    code = f"a = {a}\nb = a\nc = a.copy()\nb.append({neu})\nprint(a)\nprint(len(c))"
    return _programm(code, ["b = a kopiert die Liste NICHT – a und b zeigen auf dieselbe Liste (Referenz).",
                            f"b.append({neu}) ändert darum auch a: {a + [neu]}",
                            "c = a.copy() ist eine echte Kopie von vorher -> weiterhin 3 Elemente."])


# =============================================================================
# OBJEKTORIENTIERUNG
# =============================================================================
def _klasse(z):
    r, i = z.choice([10, 47, 100, 220]), z.choice([2, 3, 5])           # ganze Zahlen: keine Float-Rundungsreste
    code = (f"class Widerstand:\n    def __init__(self, ohm):\n        self.ohm = ohm\n\n    def spannung(self, strom):\n"
            f"        return self.ohm * strom\n\nr1 = Widerstand({r})\nr2 = Widerstand({r * 2})\n"
            f"print(r1.spannung({i}))\nprint(r2.ohm)")
    return _programm(code, ["__init__ wird beim Erzeugen aufgerufen und speichert ohm im OBJEKT (self.ohm).",
                            f"r1.spannung({i}) = {r} · {i} = {r * i}",
                            f"r2 ist ein eigenes Objekt mit ohm = {r * 2}"])


def _vererbung(z):
    a = z.randint(2, 6)
    code = (f"class Geraet:\n    def __init__(self, name):\n        self.name = name\n\n    def info(self):\n"
            f"        return self.name + ' (Gerät)'\n\nclass Messgeraet(Geraet):\n    def __init__(self, name, kanaele):\n"
            f"        super().__init__(name)\n        self.kanaele = kanaele\n\n    def info(self):\n"
            f"        return super().info() + ' mit ' + str(self.kanaele) + ' Kanälen'\n\n"
            f"m = Messgeraet('Oszi', {a})\nprint(m.info())\nprint(isinstance(m, Geraet))")
    return _programm(code, ["Messgeraet erbt von Geraet und überschreibt info().",
                            "super().info() ruft zuerst die Methode der Elternklasse auf und hängt dann an.",
                            "isinstance(m, Geraet) ist True – ein Messgerät IST auch ein Gerät."])


# =============================================================================
# FORTGESCHRITTEN
# =============================================================================
def _exception(z):
    texte = z.choice([("'12'", "12"), ("'abc'", None), ("'0'", 0)])
    lit, wert = texte
    code = (f"try:\n    zahl = int({lit})\n    print(100 // zahl)\nexcept ValueError:\n    print('keine Zahl')\n"
            f"except ZeroDivisionError:\n    print('durch null')\nfinally:\n    print('ende')")
    if wert is None:
        fall = f"int({lit}) wirft ValueError -> 'keine Zahl'"
    elif wert == 0:
        fall = "int('0') = 0 klappt, aber 100 // 0 wirft ZeroDivisionError -> 'durch null'"
    else:
        fall = f"int({lit}) = {wert}, 100 // {wert} = {100 // int(wert)} – kein Fehler"
    return _programm(code, [fall, "finally wird IMMER ausgeführt – mit oder ohne Fehler."])


def _c_division(z):
    a, b = z.randint(7, 29), z.choice([2, 3, 4, 5])
    if a % b == 0:
        a += 1
    code = f"int a = {a} / {b};\nfloat f = {a} / {b};\nfloat g = {a} / {b}.0f;\nprintf(\"%d %.2f %.2f\\n\", a, f, g);"
    ganz = a // b                                                    # beide positiv: C schneidet ab = floor
    loesung = f"{ganz} {ganz:.2f} {a / b:.2f}"
    return _programm(code, [f"{a} / {b} sind zwei int -> GANZZAHLdivision in C: {ganz} (Rest fällt weg)",
                            f"float f = {a} / {b}: zuerst wird ganzzahlig gerechnet ({ganz}), erst dann zu float -> {ganz:.2f}",
                            f"{a} / {b}.0f: ein Operand ist float -> echte Division {a / b:.2f}"],
                     sprache="c", text="Was gibt dieses C-Programmstück aus?", loesung=loesung)


def _c_uint8(z):
    x, plus = z.randint(200, 250), z.randint(10, 80)
    code = f"uint8_t x = {x};\nx = x + {plus};\nprintf(\"%u\\n\", x);"
    return _programm(code, ["uint8_t hat 8 Bit: Werte 0 … 255. Darüber geht es bei 0 weiter (modulo 256).",
                            f"{x} + {plus} = {x + plus}  ->  {x + plus} − 256 = {(x + plus) % 256}"],
                     sprache="c", text="Was gibt dieses C-Programmstück aus?", loesung=str((x + plus) % 256))


def _c_postfix(z):
    i = z.randint(2, 9)
    a, i1 = i, i + 1
    b = i1 + 1
    code = f"int i = {i};\nint a = i++;\nint b = ++i;\nprintf(\"%d %d %d\\n\", a, b, i);"
    return _programm(code, [f"a = i++: zuerst wird der ALTE Wert genommen (a = {a}), danach i erhöht (i = {i1})",
                            f"b = ++i: zuerst erhöhen (i = {b}), dann den NEUEN Wert nehmen (b = {b})"],
                     sprache="c", text="Was gibt dieses C-Programmstück aus?", loesung=f"{a} {b} {b}")


def _c_bits(z):
    wert, n = z.randint(0, 255), z.randint(0, 7)
    gesetzt = wert | (1 << n)
    pruefen = (wert >> n) & 1
    code = (f"uint8_t reg = 0x{wert:02X};\nprintf(\"%u\\n\", (reg >> {n}) & 1);\nreg |= (1 << {n});\n"
            f"printf(\"0x%02X\\n\", reg);")
    return _programm(code, [f"reg = 0x{wert:02X} = {wert:08b}",
                            f"(reg >> {n}) & 1 holt Bit {n}: {pruefen}",
                            f"reg |= (1 << {n}) setzt Bit {n}: {gesetzt:08b} = 0x{gesetzt:02X}"],
                     sprache="c", text="Was gibt dieses C-Programmstück aus? (%02X = Hex mit 2 Stellen, Grossbuchstaben)",
                     loesung=f"{pruefen} 0x{gesetzt:02X}")


def _komplexitaet(z):
    faelle = [
        ("for i in range(n):\n    print(i)", "O(n)", "Eine Schleife über n Elemente."),
        ("for i in range(n):\n    for j in range(n):\n        print(i, j)", "O(n²)", "Zwei verschachtelte Schleifen über n: n · n Schritte."),
        ("i = n\nwhile i > 1:\n    i = i // 2", "O(log n)", "i wird jedes Mal halbiert: log₂(n) Schritte (wie die binäre Suche)."),
        ("print(liste[0])", "O(1)", "Ein einziger Zugriff – unabhängig von n."),
        ("for i in range(n):\n    for j in range(10):\n        print(i, j)", "O(n)", "Die innere Schleife hat FEST 10 Durchläufe: 10 · n wächst wie n."),
    ]
    code, richtig, grund = z.choice(faelle)
    return _auswahl(z, "Wie wächst die Laufzeit dieses Programmstücks mit der Grösse n? (O-Notation)", richtig,
                    ["O(1)", "O(log n)", "O(n)", "O(n²)"], [grund, "Konstante Faktoren fallen in der O-Notation weg."],
                    code=code)


# =============================================================================
# ANMELDEN (id, Titel, Thema, Stufe, Wissensseite, Erzeuger)
# =============================================================================
_LISTE = [
    ("py_rechnen", "Python: Rechnen und Reihenfolge", GRUND, 1, "operatoren", _rechnen),
    ("py_typ", "Python: Welcher Datentyp?", GRUND, 1, "datentypen", _typ),
    ("py_verketten", "Python: Texte zusammensetzen", GRUND, 1, "datentypen", _verketten),
    ("py_ganzzahl", "Python: // und %", GRUND, 2, "operatoren", _ganzzahl),
    ("py_umwandeln", "Python: Typumwandlung", GRUND, 2, "typumwandlung", _umwandeln),
    ("py_if", "Python: if / elif / else", KONTROLLE, 1, "if_else", _if),
    ("py_for_summe", "Python: for-Schleife mit range", KONTROLLE, 2, "for_schleife", _for_summe),
    ("py_while", "Python: while-Schleife", KONTROLLE, 2, "while_schleife", _while),
    ("c_for", "C: Durchläufe einer for-Schleife", KONTROLLE, 2, "for_schleife", _c_for),
    ("py_break_continue", "Python: break und continue", KONTROLLE, 3, "break_continue", _break_continue),
    ("py_funktion", "Python: Funktion mit Standardwert", FUNK, 2, "parameter_rueckgabe", _funktion),
    ("py_rekursion", "Python: Rekursion", FUNK, 3, "rekursion", _rekursion),
    ("py_scope", "Python: lokal und global", FUNK, 4, "scope", _scope),
    ("py_index", "Python: Listen-Index", DATEN, 1, "arrays_listen", _index),
    ("py_slicing", "Python: Strings schneiden", DATEN, 2, "strings", _slicing),
    ("py_dict", "Python: Dictionary", DATEN, 3, "dictionaries", _dict),
    ("py_listcomp", "Python: List Comprehension", DATEN, 3, "arrays_listen", _listcomp),
    ("py_alias", "Python: Referenz oder Kopie?", DATEN, 4, "pointer_referenzen", _alias),
    ("py_klasse", "Python: Klasse und Objekt", OOP, 3, "klassen_objekte", _klasse),
    ("py_vererbung", "Python: Vererbung und super()", OOP, 4, "vererbung", _vererbung),
    ("c_division", "C: Ganzzahldivision", FORT, 2, "datentypen", _c_division),
    ("c_postfix", "C: i++ und ++i", FORT, 3, "operatoren", _c_postfix),
    ("c_uint8", "C: Überlauf bei uint8_t", FORT, 3, "datentypen", _c_uint8),
    ("c_bits", "C: Bits prüfen und setzen", FORT, 3, "operatoren", _c_bits),
    ("py_exception", "Python: try / except / finally", FORT, 4, "fehlerbehandlung", _exception),
    ("komplexitaet", "Laufzeit: O-Notation", FORT, 4, "programmablauf", _komplexitaet),
]
for _id, _titel, _thema, _stufe, _seite, _erz in _LISTE:
    art(_id, _titel, P, _thema, _stufe, [(P, _seite)], _erz)
