# =============================================================================
# uebungen/aufgaben.py
# -----------------------------------------------------------------------------
# ÜBUNGSGENERATOR: Aufgaben mit zufälligen (aber realistischen) Werten, Kontrolle und Lösungsweg.
# Reine Rechnung - kein Fenster, keine Webseite. Nutzbar in der Webversion und später in der Desktop-App.
#
#   ARTEN, STUFEN, BEREICHE      aus uebungen/kern.py (die Aufgabenarten melden sich in ihren Modulen an)
#   aufgabe(art_id, nr)          EINE Aufgabe. Gleiche art_id + nr -> immer genau dieselbe Aufgabe
#                                (so muss nichts gespeichert werden: die Nummer steht in der Adresse)
#   antwort_pruefen(a, text, einheit)   -> {"richtig", "meldung", ...}
#   blatt(art_ids, anzahl, nr, pro_stufe)   Übungsblatt; pro_stufe = {1: 5, 3: 5} -> 5 Einstieg + 5 Studium
#   alle_arten(stufe, bereich)   nach Bereich und Thema gruppiert, wahlweise nur eine Stufe / ein Bereich
#   arten_zur_seite(bereich, thema_id)  Aufgabenarten, die zu einer Wissensseite passen
#   vorschau(art_id)             Beispiel OHNE Lösung - für die verschwommene Vorschau (ohne Abo)
#
# Eine Aufgabe ist ein dict:
#   {"art", "nr", "titel", "stufe", "text", "antwort": "zahl"|"text"|"auswahl",
#    "gegeben": [(Zeichen, Wert-Text)], "gesucht": {"zeichen", "typ", "text"},
#    "loesung", "loesung_text", "weg": [Zeilen],
#    nur "zahl": "einheiten": ["µA", "mA", "A"], "einheit"      nur "auswahl": "optionen"
#    wahlweise:  "code", "sprache", "tabelle"}
#
# Kontrolle Zahl: Abweichung bis ±1 % gilt als richtig (Rundung auf 3 Stellen ist damit immer ok).
# Kontrolle Text: wie in kern.py beschrieben (vergleich).
#
# MODULE MIT AUFGABEN (jede neue Datei unten bei den Importen eintragen):
#   uebungen/grundlagen.py   Ohm, Leistung, Reihe/Parallel, Teiler, RC, LED
#   (weitere Bereiche folgen: Schaltungen, Digitaltechnik, Programmieren, Server / Linux ...)
# Das passende Schaltbild zu einer Aufgabe zeichnet uebungen/schemas.py.
#
# WER RUFT DAS AUF?  web/ueben/views.py, web/wiki/views.py (Übungen zur Seite), uebungen/schemas.py,
#                    pruefung/rechner_faelle.py
# =============================================================================

import math
import random
import re

from bauteile import einheiten                                       # -> bauteile/einheiten.py
from uebungen.kern import ARTEN, BEREICHE, STUFEN, _f                # -> uebungen/kern.py
from uebungen import grundlagen                                      # noqa: F401  meldet seine Aufgaben an

TOLERANZ = 0.01                    # ±1 %
MAX_ANZAHL = 30                    # höchstens so viele Aufgaben auf einem Blatt
MAX_ANTWORT = 200                  # längere Antworten werden abgeschnitten


def _einheiten(typ):
    return [n for n, _ in einheiten.EINHEITEN[typ]["stufen"]]


def art_info(art_id):
    """{"id", "titel", "bereich", "thema", "stufe", "stufe_text", "stufe_info", "seiten"} oder None"""
    a = ARTEN.get(art_id)
    if a is None:
        return None
    return {"id": art_id, "titel": a["titel"], "bereich": a["bereich"], "thema": a["thema"], "stufe": a["stufe"],
            "stufe_text": STUFEN[a["stufe"]]["name"], "stufe_info": STUFEN[a["stufe"]]["text"], "seiten": a["seiten"]}


def alle_arten(stufe=None, bereich=None):
    """[(Bereich, [(Thema, [art_info ...])])] - Bereiche in fester Reihenfolge, innerhalb nach Stufe sortiert.
    stufe / bereich: nur diese zeigen (None = alle)."""
    baum = {b: {} for b in BEREICHE}
    for art_id in ARTEN:
        info = art_info(art_id)
        if (stufe is None or info["stufe"] == stufe) and (bereich is None or info["bereich"] == bereich):
            baum[info["bereich"]].setdefault(info["thema"], []).append(info)
    return [(b, [(t, sorted(liste, key=lambda i: i["stufe"])) for t, liste in themen.items()])
            for b, themen in baum.items() if themen]


def arten_zur_seite(bereich, thema_id):
    return [art_info(a) for a, d in ARTEN.items() if (bereich, thema_id) in d["seiten"]]


def aufgabe(art_id, nr):
    """Eine Aufgabe. nr = beliebige ganze Zahl (z.B. aus der Adresse) - gleiche Nummer, gleiche Werte."""
    if art_id not in ARTEN:
        raise ValueError(f"Unbekannte Aufgabenart: {art_id}")
    nr = int(nr)
    d = ARTEN[art_id]
    z = random.Random(f"{art_id}:{nr}")                              # Text als Saat -> immer gleich
    ergebnis = d["erzeugen"](z)
    basis = {"art": art_id, "nr": nr, "titel": d["titel"], "stufe": d["stufe"],
             "stufe_text": STUFEN[d["stufe"]]["name"]}
    if isinstance(ergebnis, tuple):                                  # Rechenaufgabe mit Einheit
        text, gegeben, gesucht, loesung, weg = ergebnis
        zeichen, typ, beschreibung = gesucht
        return {**basis, "antwort": "zahl", "text": text,
                "gegeben": [(name, _f(wert, t)) for name, wert, t in gegeben],
                "gesucht": {"zeichen": zeichen, "typ": typ, "text": beschreibung},
                "loesung": loesung, "loesung_text": _f(loesung, typ), "weg": weg,
                "einheiten": _einheiten(typ), "einheit": einheiten.stufe_waehlen(loesung, typ)[0]}
    e = dict(ergebnis)                                               # Text- oder Auswahlaufgabe
    if e["antwort"] == "auswahl" and e["loesung"] not in e["optionen"]:
        raise ValueError(f"{art_id}: Lösung steht nicht in den Optionen")
    gesucht = e.get("gesucht") or {"zeichen": "Antwort", "text": ""}
    return {**basis, "antwort": e["antwort"], "text": e["text"], "gegeben": list(e.get("gegeben", [])),
            "gesucht": {"zeichen": gesucht["zeichen"], "typ": None, "text": gesucht.get("text", "")},
            "loesung": e["loesung"], "loesung_text": e["loesung"], "weg": e["weg"],
            "optionen": e.get("optionen", []), "akzeptiert": e.get("akzeptiert", []),
            "vergleich": e.get("vergleich", "text"), "code": e.get("code"), "sprache": e.get("sprache"),
            "tabelle": e.get("tabelle")}


def _normal(text, vergleich):
    """Antwort vergleichbar machen. Rückgabe: Text oder Zahl (bei basis2/16/10), None = nicht lesbar."""
    t = re.sub(r"\s+", " ", str(text or "")).strip().strip("\"'„“`")
    if vergleich.startswith("basis"):
        basis = int(vergleich[5:])
        t = t.replace(" ", "").replace("_", "").replace("'", "").lower()
        for vorsatz in ("0b", "0x", "0d"):
            if t.startswith(vorsatz):
                t = t[2:]
        t = re.sub(r"[bhd]$", "", t) if basis != 16 else re.sub(r"h$", "", t)    # 1011b, 2Fh
        try:
            return int(t, basis)
        except ValueError:
            return None
    return t if vergleich == "genau" else t.lower()


def antwort_pruefen(a, text, einheit=None):
    """Antwort kontrollieren -> {"richtig", "meldung"} (+ bei Zahlen "wert", "abweichung").
    Zahl: wie in den Rechnern ("25.5", "25,5", "25m5", "0.0255A"), einheit = Auswahl im Dropdown (z.B. "mA").
    Text: verglichen nach a["vergleich"]. Auswahl: die gewählte Option."""
    text = str(text or "")[:MAX_ANTWORT]
    if a["antwort"] != "zahl":
        if not text.strip():
            return {"richtig": False, "meldung": "Bitte eine Antwort eingeben."}
        if a["antwort"] == "auswahl":
            richtig = text == a["loesung"]
        else:
            soll = [_normal(s, a["vergleich"]) for s in [a["loesung"], *a["akzeptiert"]]]
            ist = _normal(text, a["vergleich"])
            if ist is None:
                return {"richtig": False, "meldung": "Diese Eingabe verstehe ich nicht – bitte nur die Zahl in der verlangten Schreibweise."}
            richtig = ist in soll
        return {"richtig": richtig, "meldung": "Richtig!" if richtig else "Leider falsch – versuche es nochmals oder schau dir die Lösung an."}
    typ = a["gesucht"]["typ"]
    stufen = dict(einheiten.EINHEITEN[typ]["stufen"])
    faktor = stufen.get(einheit, stufen.get(a["einheit"], 1.0))
    try:
        wert = einheiten.text_zu_zahl(text, typ, faktor)
    except ValueError as fehler:
        return {"richtig": False, "wert": None, "abweichung": None, "meldung": str(fehler)}
    if wert is None:
        return {"richtig": False, "wert": None, "abweichung": None, "meldung": "Bitte eine Zahl eingeben."}
    abweichung = (wert - a["loesung"]) / a["loesung"]
    if abs(abweichung) <= TOLERANZ:
        return {"richtig": True, "wert": wert, "abweichung": abweichung, "meldung": "Richtig!"}
    tipp = ""
    for k in (1e3, 1e6, 1e9):                                        # typischer Fehler: Vorsatz vertauscht
        if math.isclose(wert * k, a["loesung"], rel_tol=TOLERANZ) or math.isclose(wert / k, a["loesung"], rel_tol=TOLERANZ):
            tipp = " Die Zahl stimmt fast – prüfe die Einheit (Faktor 1000)."
            break
    return {"richtig": False, "wert": wert, "abweichung": abweichung,
            "meldung": f"Leider falsch: {_f(wert, typ)} weicht um {abweichung * 100:+.1f} % ab.{tipp}"}


def blatt(art_ids, anzahl, nr, pro_stufe=None):
    """Übungsblatt aus den gewählten Arten. Gleiche Auswahl + gleiche nr -> gleiches Blatt.
    pro_stufe = {1: 5, 3: 5}: je Stufe so viele Aufgaben, nur aus den gewählten Arten DIESER Stufe
                (z.B. 5 Einstieg + 5 Studium). None = 'anzahl' Aufgaben aus allen gewählten Arten.
    Rückgabe: (aufgaben, hinweise) - hinweise z.B. "Für Stufe Profi ist keine gewählte Aufgabe da"."""
    arten = [a for a in dict.fromkeys(art_ids) if a in ARTEN]
    if not arten:
        raise ValueError("Bitte mindestens eine Aufgabenart wählen.")
    z = random.Random(f"blatt:{nr}")
    if not pro_stufe:
        anzahl = max(1, min(int(anzahl), MAX_ANZAHL))
        return [aufgabe(arten[i % len(arten)], z.randint(1, 10 ** 9)) for i in range(anzahl)], []
    liste, hinweise, frei = [], [], MAX_ANZAHL
    for stufe in sorted(pro_stufe):
        n = max(0, min(int(pro_stufe[stufe]), frei))
        passend = [a for a in arten if ARTEN[a]["stufe"] == stufe]
        if n and not passend:
            hinweise.append(f"Stufe {STUFEN[stufe]['name']}: unter den gewählten Aufgaben ist keine dieser Stufe.")
            continue
        z.shuffle(passend)
        liste += [aufgabe(passend[i % len(passend)], z.randint(1, 10 ** 9)) for i in range(n)]
        frei -= n
    if not liste and not hinweise:
        raise ValueError("Bitte bei mindestens einer Stufe eine Anzahl angeben.")
    return liste, hinweise


BEISPIEL_NR = 1                    # die Vorschau zeigt immer diese Aufgabe


def vorschau(art_id="ohm_strom"):
    """Nur Titel, Text, gegebene Werte und was gesucht ist - KEINE Lösung, kein Lösungsweg."""
    a = aufgabe(art_id, BEISPIEL_NR)
    return {"art": a["art"], "titel": a["titel"], "text": a["text"], "gegeben": a["gegeben"], "gesucht": a["gesucht"],
            "code": a.get("code"), "sprache": a.get("sprache")}


def neue_nr():
    """Zufällige Aufgabennummer für 'Neue Aufgabe'"""
    return random.SystemRandom().randint(1, 10 ** 9)
