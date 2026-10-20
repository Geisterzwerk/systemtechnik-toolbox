# =============================================================================
# uebungen/aufgaben.py
# -----------------------------------------------------------------------------
# ÜBUNGSGENERATOR: Aufgaben mit zufälligen (aber realistischen) Werten, Kontrolle und Lösungsweg.
# Reine Rechnung - kein Fenster, keine Webseite. Nutzbar in der Webversion und später in der Desktop-App.
#
#   ARTEN                        {id: Aufgabenart}  (titel, thema, stufe, seiten, erzeugen)
#   aufgabe(art_id, nr)          EINE Aufgabe. Gleiche art_id + nr -> immer genau dieselbe Aufgabe
#                                (so muss nichts gespeichert werden: die Nummer steht in der Adresse)
#   antwort_pruefen(a, text, einheit)   -> {"richtig", "wert", "abweichung", "meldung"}
#   blatt(art_ids, anzahl, nr)   Übungsblatt: mehrere Aufgaben gemischt
#   arten_zur_seite(bereich, thema_id)  Aufgabenarten, die zu einer Wissensseite passen
#   vorschau(art_id)             Beispiel OHNE Lösung - für die verschwommene Vorschau (ohne Abo)
#
# Eine Aufgabe ist ein dict:
#   {"art", "nr", "titel", "text", "gegeben": [(Zeichen, Wert-Text)], "gesucht": (Zeichen, typ, Beschreibung),
#    "loesung": Zahl (Basiseinheit), "loesung_text": "25.53 mA", "weg": [Zeilen], "einheiten": ["µA", "mA", "A"]}
#
# Gerechnet wird mit den Funktionen, die auch die Rechner benutzen (schaltungen/netzwerk_mathe.py) -
# nichts doppelt. Gegebene Widerstände und Kondensatoren sind Normwerte (E12, IEC 60063).
# Kontrolle: Abweichung bis ±1 % gilt als richtig (Rundung auf 3 Stellen ist damit immer ok).
#
# Das passende Schaltbild zu jeder Aufgabe zeichnet uebungen/schemas.py.
#
# WER RUFT DAS AUF?  web/ueben/views.py, web/wiki/views.py (Übungen zur Seite), uebungen/schemas.py,
#                    pruefung/rechner_faelle.py
# =============================================================================

import math
import random

from bauteile import einheiten                                       # -> bauteile/einheiten.py
from bauteile.rechner.normreihen import E12                          # -> bauteile/rechner/normreihen.py
from schaltungen import netzwerk_mathe as nm                         # -> schaltungen/netzwerk_mathe.py

TOLERANZ = 0.01                    # ±1 %
MAX_ANZAHL = 30                    # höchstens so viele Aufgaben auf einem Blatt
STUFEN = {1: "Einstieg", 2: "Fortgeschritten", 3: "Profi"}


def _f(wert, typ):
    """Wert mit passender Einheit: 0.02553 A -> '25.53 mA'"""
    return einheiten.formatieren(wert, typ)


def _e12(z, von_exp, bis_exp):
    """Zufälliger E12-Normwert zwischen 10^von_exp und 10^bis_exp (z.B. 2, 4 -> 100 Ω … 8.2 kΩ)"""
    return float(f"{z.choice(E12) * 10 ** z.randint(von_exp, bis_exp - 1):.12g}")


def _einheiten(typ):
    return [n for n, _ in einheiten.EINHEITEN[typ]["stufen"]]


# =============================================================================
# DIE AUFGABENARTEN
# Jede erzeugen(z) bekommt einen eigenen Zufallsgenerator und gibt zurück:
#   text, gegeben [(Zeichen, Wert, typ)], gesucht (Zeichen, typ, Beschreibung), loesung, weg [Zeilen]
# =============================================================================
def _ohm_strom(z):
    u = z.choice([3.3, 5.0, 9.0, 12.0, 24.0, 48.0])
    r = _e12(z, 2, 5)                                                # 100 Ω … 82 kΩ
    i = u / r
    return ("An einem Widerstand liegt eine Spannung. Wie gross ist der Strom durch den Widerstand?",
            [("U", u, "spannung"), ("R", r, "widerstand")], ("I", "strom", "Strom durch den Widerstand"), i,
            ["Ohmsches Gesetz: I = U / R", f"I = {_f(u, 'spannung')} / {_f(r, 'widerstand')}",
             f"I = {_f(i, 'strom')}"])


def _ohm_spannung(z):
    r = _e12(z, 1, 4)                                                # 10 Ω … 8.2 kΩ
    i = _e12(z, -3, -1)                                              # 1 mA … 82 mA
    u = r * i
    return ("Durch einen Widerstand fliesst ein Strom. Welche Spannung fällt am Widerstand ab?",
            [("R", r, "widerstand"), ("I", i, "strom")], ("U", "spannung", "Spannung am Widerstand"), u,
            ["Ohmsches Gesetz: U = R · I", f"U = {_f(r, 'widerstand')} · {_f(i, 'strom')}", f"U = {_f(u, 'spannung')}"])


def _ohm_widerstand(z):
    u = z.choice([1.5, 3.3, 5.0, 9.0, 12.0, 24.0])
    i = _e12(z, -4, -1)                                              # 100 µA … 82 mA
    r = u / i
    return ("An einem Bauteil werden Spannung und Strom gemessen. Wie gross ist sein Widerstand?",
            [("U", u, "spannung"), ("I", i, "strom")], ("R", "widerstand", "Widerstand"), r,
            ["Ohmsches Gesetz: R = U / I", f"R = {_f(u, 'spannung')} / {_f(i, 'strom')}", f"R = {_f(r, 'widerstand')}"])


def _leistung_ui(z):
    u = z.choice([5.0, 12.0, 24.0, 48.0, 230.0])
    i = _e12(z, -2, 1)                                               # 10 mA … 8.2 A
    p = u * i
    return ("Ein Verbraucher nimmt bei einer bestimmten Spannung einen Strom auf. Welche Leistung nimmt er auf?",
            [("U", u, "spannung"), ("I", i, "strom")], ("P", "leistung", "Leistung"), p,
            ["Leistung: P = U · I", f"P = {_f(u, 'spannung')} · {_f(i, 'strom')}", f"P = {_f(p, 'leistung')}"])


def _leistung_r(z):
    r = _e12(z, 1, 4)                                                # 10 Ω … 8.2 kΩ
    i = _e12(z, -3, -1)                                              # 1 mA … 82 mA
    p = i * i * r
    return ("Durch einen Widerstand fliesst ein Strom. Welche Leistung wird im Widerstand in Wärme umgesetzt?",
            [("R", r, "widerstand"), ("I", i, "strom")], ("P", "leistung", "Verlustleistung im Widerstand"), p,
            ["Leistung mit R und I: P = I² · R", f"P = ({_f(i, 'strom')})² · {_f(r, 'widerstand')}",
             f"P = {_f(p, 'leistung')}"])


def _reihe(z):
    r = [_e12(z, 2, 5) for _ in range(3)]
    rg = sum(r)
    return ("Drei Widerstände sind in Reihe geschaltet. Wie gross ist der Gesamtwiderstand?",
            [("R1", r[0], "widerstand"), ("R2", r[1], "widerstand"), ("R3", r[2], "widerstand")],
            ("R_ges", "widerstand", "Gesamtwiderstand"), rg,
            ["Reihenschaltung: die Widerstände addieren sich: R_ges = R1 + R2 + R3",
             f"R_ges = {_f(r[0], 'widerstand')} + {_f(r[1], 'widerstand')} + {_f(r[2], 'widerstand')}",
             f"R_ges = {_f(rg, 'widerstand')}"])


def _parallel(z):
    r1, r2 = _e12(z, 2, 5), _e12(z, 2, 5)
    rg = nm.parallel(r1, r2)
    return ("Zwei Widerstände sind parallel geschaltet. Wie gross ist der Gesamtwiderstand?",
            [("R1", r1, "widerstand"), ("R2", r2, "widerstand")], ("R_ges", "widerstand", "Gesamtwiderstand"), rg,
            ["Parallelschaltung von zwei Widerständen: R_ges = (R1 · R2) / (R1 + R2)",
             f"R_ges = ({_f(r1, 'widerstand')} · {_f(r2, 'widerstand')}) / ({_f(r1, 'widerstand')} + {_f(r2, 'widerstand')})",
             f"R_ges = {_f(rg, 'widerstand')}",
             "Kontrolle: R_ges ist immer kleiner als der kleinste Einzelwiderstand."])


def _teiler(z):
    ue = z.choice([5.0, 9.0, 12.0, 15.0, 24.0])
    r1, r2 = _e12(z, 2, 5), _e12(z, 2, 5)
    ua = nm.spannungsteiler(ue, r1, r2)["ua0"]
    return ("Ein unbelasteter Spannungsteiler: R1 liegt oben, R2 unten. Wie gross ist die Ausgangsspannung an R2?",
            [("Ue", ue, "spannung"), ("R1", r1, "widerstand"), ("R2", r2, "widerstand")],
            ("Ua", "spannung", "Ausgangsspannung an R2"), ua,
            ["Spannungsteiler-Regel: Ua = Ue · R2 / (R1 + R2)",
             f"Ua = {_f(ue, 'spannung')} · {_f(r2, 'widerstand')} / ({_f(r1, 'widerstand')} + {_f(r2, 'widerstand')})",
             f"Ua = {_f(ua, 'spannung')}"])


def _teiler_belastet(z):
    ue = z.choice([5.0, 9.0, 12.0, 15.0, 24.0])
    r1, r2 = _e12(z, 3, 5), _e12(z, 3, 5)                            # 1 kΩ … 82 kΩ
    rl = _e12(z, 3, 6)                                               # 1 kΩ … 820 kΩ
    e = nm.spannungsteiler(ue, r1, r2, rl)
    return ("Ein Spannungsteiler (R1 oben, R2 unten) wird mit einem Lastwiderstand RL parallel zu R2 belastet. "
            "Wie gross ist die Ausgangsspannung?",
            [("Ue", ue, "spannung"), ("R1", r1, "widerstand"), ("R2", r2, "widerstand"), ("RL", rl, "widerstand")],
            ("Ua", "spannung", "Ausgangsspannung mit Last"), e["ua"],
            ["1. R2 und RL parallel: R2∥RL = (R2 · RL) / (R2 + RL)",
             f"   R2∥RL = ({_f(r2, 'widerstand')} · {_f(rl, 'widerstand')}) / ({_f(r2, 'widerstand')} + {_f(rl, 'widerstand')}) = {_f(e['r_unten'], 'widerstand')}",
             "2. Spannungsteiler-Regel mit R2∥RL: Ua = Ue · R2∥RL / (R1 + R2∥RL)",
             f"   Ua = {_f(ue, 'spannung')} · {_f(e['r_unten'], 'widerstand')} / ({_f(r1, 'widerstand')} + {_f(e['r_unten'], 'widerstand')})",
             f"   Ua = {_f(e['ua'], 'spannung')}",
             f"Zum Vergleich ohne Last: {_f(e['ua0'], 'spannung')} - die Last zieht die Spannung nach unten."])


def _rc_tau(z):
    r = _e12(z, 2, 6)                                                # 100 Ω … 820 kΩ
    c = _e12(z, -9, -4)                                              # 1 nF … 82 µF
    tau = r * c
    return ("Ein Kondensator wird über einen Widerstand geladen. Wie gross ist die Zeitkonstante τ?",
            [("R", r, "widerstand"), ("C", c, "kapazitaet")], ("τ", "zeit", "Zeitkonstante"), tau,
            ["Zeitkonstante: τ = R · C", f"τ = {_f(r, 'widerstand')} · {_f(c, 'kapazitaet')}", f"τ = {_f(tau, 'zeit')}",
             "Nach 5 τ gilt der Kondensator als voll geladen (über 99 %)."])


def _rc_laden(z):
    ue = z.choice([5.0, 10.0, 12.0, 24.0])
    r = _e12(z, 3, 5)                                                # 1 kΩ … 82 kΩ
    c = _e12(z, -7, -4)                                              # 100 nF … 82 µF
    tau = r * c
    faktor = z.choice([0.5, 1.0, 2.0, 3.0])
    t = float(f"{faktor * tau:.3g}")                                 # glatte Zeitangabe
    uc = ue * (1 - math.exp(-t / tau))
    return ("Ein leerer Kondensator wird zum Zeitpunkt t = 0 über einen Widerstand an eine Gleichspannung geschaltet. "
            "Welche Spannung hat der Kondensator nach der Zeit t?",
            [("Ue", ue, "spannung"), ("R", r, "widerstand"), ("C", c, "kapazitaet"), ("t", t, "zeit")],
            ("uC", "spannung", "Kondensatorspannung zum Zeitpunkt t"), uc,
            ["1. Zeitkonstante: τ = R · C", f"   τ = {_f(r, 'widerstand')} · {_f(c, 'kapazitaet')} = {_f(tau, 'zeit')}",
             "2. Ladekurve: uC = Ue · (1 − e^(−t/τ))",
             f"   t/τ = {_f(t, 'zeit')} / {_f(tau, 'zeit')} = {t / tau:.3g}",
             f"   uC = {_f(ue, 'spannung')} · (1 − e^(−{t / tau:.3g})) = {_f(uc, 'spannung')}",
             "Merkhilfe: nach 1 τ sind es 63 %, nach 2 τ 86 %, nach 3 τ 95 % der Endspannung."])


def _led_vorwiderstand(z):
    ub = z.choice([5.0, 9.0, 12.0, 24.0])
    uf = z.choice([1.8, 2.0, 2.1, 3.0, 3.2])                         # Werte stehen in der Aufgabe (Datenblatt)
    i_f = z.choice([0.002, 0.005, 0.01, 0.015, 0.02])
    r = (ub - uf) / i_f
    return ("Eine LED soll an einer Gleichspannung betrieben werden. Laut Datenblatt gelten die Flussspannung UF "
            "und der Strom IF. Wie gross muss der Vorwiderstand sein (genauer Wert, noch kein Normwert)?",
            [("UB", ub, "spannung"), ("UF", uf, "spannung"), ("IF", i_f, "strom")],
            ("RV", "widerstand", "Vorwiderstand"), r,
            ["Am Vorwiderstand liegt der Rest der Spannung: U_R = UB − UF",
             f"U_R = {_f(ub, 'spannung')} − {_f(uf, 'spannung')} = {_f(ub - uf, 'spannung')}",
             "Ohmsches Gesetz: RV = U_R / IF", f"RV = {_f(ub - uf, 'spannung')} / {_f(i_f, 'strom')} = {_f(r, 'widerstand')}",
             "In der Praxis den nächsten GRÖSSEREN Normwert wählen (der Strom wird dann etwas kleiner)."])


# id -> (Titel, Thema, Stufe, [(Bereich, Thema-ID der Wissensseite)], erzeugen)
ARTEN = {
    "ohm_strom":        ("Ohmsches Gesetz: Strom berechnen", "Grundlagen", 1, [("Bauteile", "widerstand")], _ohm_strom),
    "ohm_spannung":     ("Ohmsches Gesetz: Spannung berechnen", "Grundlagen", 1, [("Bauteile", "widerstand")], _ohm_spannung),
    "ohm_widerstand":   ("Ohmsches Gesetz: Widerstand berechnen", "Grundlagen", 1, [("Bauteile", "widerstand")], _ohm_widerstand),
    "leistung_ui":      ("Leistung aus Spannung und Strom", "Grundlagen", 1, [("Bauteile", "widerstand")], _leistung_ui),
    "leistung_r":       ("Verlustleistung im Widerstand", "Grundlagen", 2, [("Bauteile", "widerstand")], _leistung_r),
    "reihe":            ("Reihenschaltung von Widerständen", "Widerstandsnetzwerke", 1,
                         [("Bauteile", "widerstand"), ("Schaltungen", "spannungsteiler")], _reihe),
    "parallel":         ("Parallelschaltung von Widerständen", "Widerstandsnetzwerke", 2,
                         [("Bauteile", "widerstand"), ("Schaltungen", "spannungsteiler")], _parallel),
    "teiler":           ("Spannungsteiler (unbelastet)", "Widerstandsnetzwerke", 1,
                         [("Schaltungen", "spannungsteiler")], _teiler),
    "teiler_belastet":  ("Spannungsteiler (belastet)", "Widerstandsnetzwerke", 3,
                         [("Schaltungen", "spannungsteiler")], _teiler_belastet),
    "rc_tau":           ("RC-Glied: Zeitkonstante τ", "RC-Glied", 1,
                         [("Bauteile", "kondensator"), ("Schaltungen", "rc_laden_entladen")], _rc_tau),
    "rc_laden":         ("RC-Glied: Spannung beim Laden", "RC-Glied", 3,
                         [("Bauteile", "kondensator"), ("Schaltungen", "rc_laden_entladen")], _rc_laden),
    "led_vorwiderstand": ("LED-Vorwiderstand", "Dioden & LED", 2, [("Bauteile", "led")], _led_vorwiderstand),
}


def art_info(art_id):
    """{"id", "titel", "thema", "stufe", "stufe_text", "seiten"} oder None"""
    if art_id not in ARTEN:
        return None
    titel, thema, stufe, seiten, _erzeugen = ARTEN[art_id]
    return {"id": art_id, "titel": titel, "thema": thema, "stufe": stufe, "stufe_text": STUFEN[stufe], "seiten": seiten}


def alle_arten():
    """Alle Aufgabenarten, nach Thema gruppiert: [(Thema, [art_info ...]), ...] in fester Reihenfolge"""
    gruppen = {}
    for art_id in ARTEN:
        info = art_info(art_id)
        gruppen.setdefault(info["thema"], []).append(info)
    return list(gruppen.items())


def arten_zur_seite(bereich, thema_id):
    return [art_info(a) for a, (_t, _th, _s, seiten, _e) in ARTEN.items() if (bereich, thema_id) in seiten]


def aufgabe(art_id, nr):
    """Eine Aufgabe. nr = beliebige ganze Zahl (z.B. aus der Adresse) - gleiche Nummer, gleiche Werte."""
    if art_id not in ARTEN:
        raise ValueError(f"Unbekannte Aufgabenart: {art_id}")
    nr = int(nr)
    titel, _thema, stufe, _seiten, erzeugen = ARTEN[art_id]
    z = random.Random(f"{art_id}:{nr}")                              # Text als Saat -> immer gleich
    text, gegeben, gesucht, loesung, weg = erzeugen(z)
    zeichen, typ, beschreibung = gesucht
    return {"art": art_id, "nr": nr, "titel": titel, "stufe": stufe, "text": text,
            "gegeben": [(name, _f(wert, t)) for name, wert, t in gegeben],
            "gesucht": {"zeichen": zeichen, "typ": typ, "text": beschreibung},
            "loesung": loesung, "loesung_text": _f(loesung, typ), "weg": weg,
            "einheiten": _einheiten(typ), "einheit": einheiten.stufe_waehlen(loesung, typ)[0]}


def antwort_pruefen(a, text, einheit=None):
    """Antwort kontrollieren. text wie in den Rechnern ("25.5", "25,5", "25m5", "0.0255A"),
    einheit = Auswahl im Dropdown (z.B. "mA"). Rückgabe: {"richtig", "wert", "abweichung", "meldung"}"""
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


def blatt(art_ids, anzahl, nr):
    """Übungsblatt: 'anzahl' Aufgaben aus den gewählten Arten, der Reihe nach gemischt.
    Gleiche Auswahl + gleiche nr -> gleiches Blatt (zum Ausdrucken und später Nachkorrigieren)."""
    arten = [a for a in dict.fromkeys(art_ids) if a in ARTEN]
    if not arten:
        raise ValueError("Bitte mindestens eine Aufgabenart wählen.")
    anzahl = max(1, min(int(anzahl), MAX_ANZAHL))
    z = random.Random(f"blatt:{nr}")
    return [aufgabe(arten[i % len(arten)], z.randint(1, 10 ** 9)) for i in range(anzahl)]


BEISPIEL_NR = 1                    # die Vorschau zeigt immer diese Aufgabe


def vorschau(art_id="ohm_strom"):
    """Nur Titel, Text, gegebene Werte und was gesucht ist - KEINE Lösung, kein Lösungsweg."""
    a = aufgabe(art_id, BEISPIEL_NR)
    return {"art": a["art"], "titel": a["titel"], "text": a["text"], "gegeben": a["gegeben"], "gesucht": a["gesucht"]}


def neue_nr():
    """Zufällige Aufgabennummer für 'Neue Aufgabe'"""
    return random.SystemRandom().randint(1, 10 ** 9)
