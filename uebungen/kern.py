# =============================================================================
# uebungen/kern.py
# -----------------------------------------------------------------------------
# GRUNDLAGE DES ÜBUNGSGENERATORS: Stufen, Liste aller Aufgabenarten, Hilfen. Reine Rechnung.
#
#   STUFEN          {1: {"name", "text"}, ...}  vier Schwierigkeitsstufen (Begründung unten)
#   ARTEN           {id: {"titel", "bereich", "thema", "stufe", "seiten", "erzeugen"}}
#   art(...)        eine Aufgabenart anmelden (in uebungen/grundlagen.py, digital.py, programmieren.py ...)
#   _f, _e12        Wert mit Einheit formatieren, zufälliger E12-Normwert
#
# EIN ERZEUGER erzeugen(z) bekommt einen eigenen Zufallsgenerator z (random.Random) und gibt zurück:
#   a) RECHENAUFGABE (Zahl mit Einheit) - Tupel:
#        (text, gegeben [(Zeichen, Wert, typ)], gesucht (Zeichen, typ, Beschreibung), loesung, weg [Zeilen])
#   b) ALLE ANDEREN - dict:
#        text        Aufgabentext
#        antwort     "text"    -> Eingabefeld, verglichen nach 'vergleich'
#                    "auswahl" -> Auswahl aus 'optionen' (eine ist richtig)
#        loesung     richtige Antwort als Text (bei "auswahl": genau eine der optionen)
#        weg         Lösungsweg [Zeilen]
#        gesucht     {"zeichen", "text"}           z.B. {"zeichen": "Ausgabe", "text": "Was gibt das Programm aus?"}
#        optional:   gegeben [(Name, Text)], optionen [...], akzeptiert [weitere richtige Texte],
#                    vergleich "text" (Gross/Klein egal) | "genau" (Gross/Klein zählt, z.B. Befehle) |
#                              "basis2" / "basis16" / "basis10" (Zahl in dieser Basis, führende Nullen egal) |
#                              "menge" (Zahlen, Reihenfolge egal: "1, 3, 5") | "buchstaben" ("bcfg" = "g f c b") |
#                              "worte" (Wörter/Dateinamen, Reihenfolge egal),
#                    code (str) + sprache ("python", "bash", "c" ...), tabelle {"kopf": [...], "zeilen": [[...]]}
#
# DIE VIER STUFEN orientieren sich an öffentlich beschriebenen Niveaus (recherchiert 2026-10-20):
#   1 Einstieg       1.–2. Lehrjahr EFZ; Niveau Linux Essentials (LPI 010) bzw. Python PCEP (Einstiegszertifikat)
#   2 Lehrabschluss  3.–4. Lehrjahr, Niveau Qualifikationsverfahren (QV) EFZ
#   3 Studium / HF   Höhere Fachschule (z.B. Elektrotechniker HF: Fachmathematik, Digital-, Analogtechnik),
#                    FH-Grundstudium; Niveau LPIC-1 bzw. Python PCAP
#   4 Profi          Vertiefung, Dimensionieren mit mehreren Schritten, Fehlersuche, Praxis
# QV-Prüfungen selbst sind meist nicht öffentlich - die Aufgaben sind darum EIGENE Aufgaben auf diesem Niveau.
#
# WER RUFT DAS AUF?  uebungen/aufgaben.py und alle Übungs-Module
# =============================================================================

from bauteile import einheiten                                       # -> bauteile/einheiten.py
from bauteile.rechner.normreihen import E12                          # -> bauteile/rechner/normreihen.py

STUFEN = {
    1: {"name": "Einstieg", "text": "1.–2. Lehrjahr, Grundlagen"},
    2: {"name": "Lehrabschluss", "text": "EFZ / QV-Niveau"},
    3: {"name": "Studium / HF", "text": "Höhere Fachschule, FH-Grundstudium"},
    4: {"name": "Profi", "text": "Vertiefung, Praxis, Fehlersuche"},
}

# Bereiche in dieser Reihenfolge (wie die Wissensseiten); "Grundlagen" = Elektrotechnik-Grundlagen
BEREICHE = ["Grundlagen", "Bauteile", "Schaltungen", "Digitaltechnik", "Messtechnik", "Programmieren", "Server / Linux"]

ARTEN = {}


def art(art_id, titel, bereich, thema, stufe, seiten, erzeugen):
    """Eine Aufgabenart anmelden. seiten = [(Bereich der Wissensseite, Thema-ID)] -> 'Nachlesen'."""
    if art_id in ARTEN:
        raise ValueError(f"Aufgabenart {art_id} gibt es schon")
    if stufe not in STUFEN or bereich not in BEREICHE:
        raise ValueError(f"{art_id}: Stufe {stufe} oder Bereich {bereich} unbekannt")
    ARTEN[art_id] = {"titel": titel, "bereich": bereich, "thema": thema, "stufe": stufe,
                     "seiten": list(seiten), "erzeugen": erzeugen}


def _f(wert, typ):
    """Wert mit passender Einheit: 0.02553 A -> '25.53 mA'"""
    return einheiten.formatieren(wert, typ)


def _e12(z, von_exp, bis_exp):
    """Zufälliger E12-Normwert zwischen 10^von_exp und 10^bis_exp (z.B. 2, 4 -> 100 Ω … 8.2 kΩ)"""
    return float(f"{z.choice(E12) * 10 ** z.randint(von_exp, bis_exp - 1):.12g}")
