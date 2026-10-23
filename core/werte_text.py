# =============================================================================
# core/werte_text.py
# -----------------------------------------------------------------------------
# ERGEBNISTEXT -> ZEILEN FÜR EINE TABELLE  (ohne Fenster, darum auch testbar)
#
# Die Rechner und Grafiken liefern ihr Ergebnis als Textzeilen, z.B.
#   "Querstrom I2 = 600 µA   ·   P(R1) = 3.6 mW   P(R2) = 3.6 mW"
#   "τ = R · C = 100 ms  →  nach 5τ = 500 ms ist der Vorgang zu 99.3 % abgeschlossen"
# zerlegen() macht daraus übersichtliche Zeilen:
#   ("wert", "Querstrom I2", "600 µA", "")        Name | Wert | Notiz (Rechenweg, Klammer)
#   ("wert", "P(R1)", "3.6 mW", "")
#   ("wert", "τ", "100 ms", "= R · C")
#   ("text", "nach 5τ = 500 ms ist der Vorgang …", "", "")      erklärender Satz bleibt ein Satz
#   ("warnung", "⚠ …", "", "")
#
# REGELN (bewusst vorsichtig - lieber einmal Text lassen als falsch zerlegen):
#   - Zeilen, die mit Leerzeichen beginnen (eingerückte Listen, Bitmuster), bleiben Text.
#   - Getrennt wird an "   " (3+ Leerzeichen) und an " · " / " → " mit je 2+ Leerzeichen.
#     Stücke, die mit "=" oder "(" beginnen, gehören zum Stück davor.
#   - Ein Stück wird zu Name | Wert, wenn es " = " ausserhalb von Klammern enthält,
#     der Name kurz ist (≤ 28 Zeichen) und der Wert kurz ist (≤ 32 Zeichen).
#
# WER RUFT DAS AUF?  core/widgets.py -> WerteAnzeige (Rechner-Karten, Schaltungen, Trafo, Kurven)
#                    pruefen.py (Selbsttest)
# =============================================================================

import re

# "·" mit nur EINEM Leerzeichen ist ein Malpunkt (R · C) -> dort NICHT trennen
_TRENNER = re.compile(r"\s{2,}[·→]\s{2,}|\s{3,}")
_DOPPELPUNKT = re.compile(r"^([^:=≈]{1,20}):\s+([-−+]?\d[^:]*)$")      # "E24: 1.3 kΩ  (…)"
MAX_NAME = 28
MAX_WERT = 32


def _gleich_teilen(stueck):
    """'τ = R · C = 100 ms' -> (['τ', 'R · C', '100 ms'], ungefaehr)
    Getrennt wird nur an ' = ' und ' ≈ ' ausserhalb von Klammern. ungefaehr = True, wenn vor dem Wert ≈ stand."""
    teile, tiefe, start, i, ungefaehr = [], 0, 0, 0, False
    while i < len(stueck):
        z = stueck[i]
        if z in "([{":
            tiefe += 1
        elif z in ")]}":
            tiefe = max(0, tiefe - 1)
        elif tiefe == 0 and (stueck.startswith(" = ", i) or stueck.startswith(" ≈ ", i)):
            teile.append(stueck[start:i].strip())
            ungefaehr = stueck[i + 1] == "≈"
            start = i + 3
            i += 3
            continue
        i += 1
    teile.append(stueck[start:].strip())
    return teile, ungefaehr


def _stuecke(zeile):
    roh = [s for s in _TRENNER.split(zeile) if s.strip()]
    stuecke = []
    for s in roh:
        s = s.strip()
        if stuecke and (s.startswith("=") or s.startswith("(")):
            stuecke[-1] = f"{stuecke[-1]}  {s}"            # gehört zum Stück davor
            continue
        # "I_C = 1.34 mA, U_CE = 7.7 V" -> zwei Stücke (nur wenn JEDES Komma-Stück ein '=' hat)
        komma = [k.strip() for k in s.split(", ")]
        if len(komma) > 1 and all(len(_gleich_teilen(k)[0]) > 1 for k in komma):
            stuecke.extend(komma)
        else:
            stuecke.append(s)
    return stuecke


def _notiz_abtrennen(wert):
    """'6 V  (unbelastet 6 V)' -> ('6 V', '(unbelastet 6 V)')"""
    klammer = re.match(r"^(.*?)\s{1,}(\(.*\))$", wert)
    if klammer and klammer.group(1).strip():
        return klammer.group(1).strip(), klammer.group(2)
    return wert, ""


def _als_wert(stueck):
    """Stück -> ("wert", name, wert, notiz) oder None, wenn es kein klares 'Name = Wert' ist."""
    teile, ungefaehr = _gleich_teilen(stueck)
    if len(teile) < 2:
        doppelpunkt = _DOPPELPUNKT.match(stueck)
        if not doppelpunkt:
            return None
        teile = [doppelpunkt.group(1).strip(), doppelpunkt.group(2).strip()]
    name = teile[0]
    wert, notiz = _notiz_abtrennen(teile[-1])
    if (not name or not wert or len(name) > MAX_NAME or len(wert) > MAX_WERT
            or not any(z.isalpha() for z in name)):            # "1010 1101" ist kein Name (Bitmuster)
        return None
    if ungefaehr:
        wert = "≈ " + wert
    if len(teile) > 2:
        notiz = ("= " + " = ".join(teile[1:-1]) + ("   " + notiz if notiz else "")).strip()
    return ("wert", name, wert, notiz)


def zerlegen(zeilen):
    """Liste von Ergebniszeilen -> Liste von (art, name, wert, notiz). art: wert | text | warnung"""
    ergebnis = []
    for zeile in zeilen:
        if not zeile.strip():
            continue
        if zeile.lstrip().startswith(("⚠", "❌")):
            ergebnis.append(("warnung", zeile.strip(), "", ""))
            continue
        if zeile[:1].isspace():                              # eingerückt: Liste/Bitmuster -> so lassen
            ergebnis.append(("text", zeile.rstrip(), "", ""))
            continue
        stuecke = _stuecke(zeile)
        werte = [_als_wert(s) for s in stuecke]
        if not any(werte):
            ergebnis.append(("text", zeile.strip(), "", ""))
            continue
        for stueck, wert in zip(stuecke, werte):
            ergebnis.append(wert or ("text", stueck, "", ""))
    return ergebnis
