# =============================================================================
# web/rechner/formular.py
# -----------------------------------------------------------------------------
# RECHNER IM BROWSER - gerechnet wird mit genau denselben Funktionen wie in der Desktop-App:
#   FormelDaten (bauteile/rechner/kern.py): Felder + Rechenfunktion
#   texte_lesen() "4k7" -> 4700.0 (wie die Eingabefelder im Fenster)
#
#   web_rechner_ids()              alle freigeschalteten IDs (alle Formel-Rechner + Sonderseiten, settings.py)
#   web_id(id)                     Projekt-ID -> Web-ID (farbcode_wert -> farbcode) oder None
#   web_rechner(ids)               Rechner mit Titel/Beschreibung/Kategorie (alle oder nur die genannten)
#   nach_kategorien()              für die Rechner-Übersicht: Kategorie -> Unterkategorie -> Rechner
#   anzahl()                       (Rechner, Schaltpläne) im Web
#   formel_rechnen(daten, eingaben) Felder für das Formular + Ergebnis (oder Meldung)
#   farbcode(eingaben)             Farbringe <-> Wert, mit Zeichnung als SVG
#   smd(eingaben)                  SMD-Aufdruck (103, 4R7, 01C) -> Wert
#
# EINGABEN (Adresse oder Formular):  <feld>=Text   <feld>-e=Einheit   rechnen=1 (Knopf gedrückt)
#
# WER RUFT DAS AUF?  web/rechner/views.py
# =============================================================================

from django.conf import settings

import bauteile.rechner as rechner_registry                            # -> bauteile/rechner/__init__.py
from bauteile import einheiten                                         # -> bauteile/einheiten.py
from bauteile.grafiken.svg_canvas import SvgCanvas                     # -> bauteile/grafiken/svg_canvas.py
from bauteile.grafiken.widerstand_bild import widerstand_zeichnen      # -> bauteile/grafiken/widerstand_bild.py
from bauteile.rechner import widerstand_rechner as wr                  # -> bauteile/rechner/widerstand_rechner.py
from bauteile.rechner.kern import FormelDaten, RechnerFehler, feld_optionen, texte_lesen   # -> rechner/kern.py
from bauteile.rechner.rechner_info import KATEGORIEN, RECHNER_INFO     # -> bauteile/rechner/rechner_info.py
from wiki import grafiken                                              # -> web/wiki/grafiken.py (Schaltpläne)

# Die Web-ID "farbcode" fasst die zwei Fenster-Karten "Farbcode → Wert" und "Wert → Farbcode" zusammen
FARBCODE_IDS = ("farbcode_wert", "wert_farbcode")


def web_rechner_ids():
    """
    Alle im Web freigeschalteten Rechner-IDs, sortiert wie in rechner_info.py:
    alle Formel-Rechner (settings.WEB_ALLE_FORMEL_RECHNER) + Sonderseiten (settings.WEB_RECHNER_EXTRA).
    """
    registry = rechner_registry.registry()
    ids = []
    if settings.WEB_ALLE_FORMEL_RECHNER:
        ids = [rid for rid in RECHNER_INFO if isinstance(registry.get(rid), FormelDaten)]
    if settings.WEB_ALLE_SCHALTUNGEN:
        schaltungen = set(grafiken.interaktive_ids())
        ids += [rid for rid in RECHNER_INFO if rid in schaltungen]
    ids += [rid for rid in settings.WEB_RECHNER_EXTRA if rid not in ids]
    return ids


def web_id(rechner_id):
    """Rechner-ID des Projekts -> ID im Web (oder None, wenn im Web noch nicht freigeschaltet)."""
    if rechner_id in FARBCODE_IDS:
        rechner_id = "farbcode"
    return rechner_id if rechner_id in web_rechner_ids() else None


def info(web_rechner_id):
    """Titel, Beschreibung, Kategorie, Wissensseite ... aus rechner_info.py"""
    if web_rechner_id == "farbcode":
        basis = dict(RECHNER_INFO["farbcode_wert"])
        basis.update(titel="Widerstand: Farbcode ↔ Wert (THT)",
                     beschreibung="Farbringe wählen und den Wert ablesen – oder umgekehrt: Welche Ringe hat 4.7 kΩ?",
                     stichworte=basis["stichworte"] + ["THT", "bedrahtet", "Wert → Farbcode"])
        return basis
    return RECHNER_INFO.get(web_rechner_id)


def anzahl():
    """(Rechner, Schaltpläne) im Web - für Startseite und Übersicht."""
    ids = web_rechner_ids()
    schaltplaene = sum(1 for rid in ids if grafiken.ist_interaktiv(rid))
    return len(ids) - schaltplaene, schaltplaene


def _eintrag(rid):
    i = info(rid)
    return i and {"id": rid, "titel": i["titel"].replace(" (interaktiv)", ""), "beschreibung": i["beschreibung"],
                  "interaktiv": grafiken.ist_interaktiv(rid), "animation": grafiken.ist_animation(rid),
                  "kategorie": i["kategorie"],
                  "unterkategorie": i["unterkategorie"], "stichworte": " ".join(i.get("stichworte", [])),
                  "icon": KATEGORIEN.get(i["kategorie"], ("🧮",))[0]}


def web_rechner(ids=None):
    """[{"id", "titel", "beschreibung", "icon", "kategorie", "unterkategorie", "stichworte"}]
    ids = None -> alle freigeschalteten, sonst genau diese (z.B. settings.WEB_RECHNER_EMPFOHLEN)"""
    erlaubt = web_rechner_ids()
    return [e for e in (_eintrag(rid) for rid in (ids if ids is not None else erlaubt) if rid in erlaubt) if e]


def nach_kategorien():
    """Für /rechner/: [{"name", "icon", "text", "gruppen": [{"name": Unterkategorie, "rechner": [...]}]}]
    Reihenfolge der Kategorien wie im Rechner-Tab der Desktop-App (KATEGORIEN)."""
    alle = web_rechner()
    ergebnis = []
    for name, (icon, text) in KATEGORIEN.items():
        gruppen = {}
        for r in alle:
            if r["kategorie"] == name:
                gruppen.setdefault(r["unterkategorie"], []).append(r)
        if gruppen:
            ergebnis.append({"name": name, "icon": icon, "text": text,
                             "gruppen": [{"name": g, "rechner": liste} for g, liste in gruppen.items()]})
    return ergebnis


def formel_daten(web_rechner_id):
    eintrag = rechner_registry.registry().get(web_rechner_id)
    return eintrag if isinstance(eintrag, FormelDaten) else None


# =============================================================================
# FORMEL-RECHNER
# =============================================================================
def formel_rechnen(daten, eingaben):
    """Rückgabe: {"felder": [...], "ergebnis": Text oder None, "ok": bool}"""
    felder = []
    for eintrag in daten.felder:
        schluessel, beschriftung, typ = eintrag[:3]
        opt = feld_optionen(eintrag)
        feld = {"name": schluessel, "text": beschriftung, "typ": typ, "wert": eingaben.get(schluessel, ""),
                "platzhalter": opt.get("platzhalter", "")}
        if typ == "auswahl":
            feld["optionen"] = opt["werte"]
            feld["wert"] = feld["wert"] or opt.get("standard") or opt["werte"][0]
        elif typ != "text":
            stufen = [n for n, _ in einheiten.EINHEITEN[typ]["stufen"]]
            standard = opt.get("einheit") or einheiten.EINHEITEN[typ]["standard"]
            gewaehlt = eingaben.get(schluessel + "-e") or standard
            feld["einheiten"] = stufen
            feld["einheit"] = gewaehlt if gewaehlt in stufen else standard
        felder.append(feld)

    if not eingaben.get("rechnen"):
        return {"felder": felder, "ergebnis": None, "ok": True}
    texte = {f["name"]: f["wert"] for f in felder}
    wahl = {f["name"]: f["einheit"] for f in felder if "einheit" in f}
    try:
        werte = texte_lesen(daten.felder, texte, wahl)
    except ValueError as fehler:                                # z.B. "abc" im Feld
        return {"felder": felder, "ergebnis": f"Ungültige Eingabe: {fehler}", "ok": False}
    except KeyError as fehler:                                  # Option/Einheit gibt es nicht (Adresse verändert)
        return {"felder": felder, "ergebnis": f"Ungültige Eingabe: {fehler.args[0]}", "ok": False}
    text, ok = daten.auswerten(werte)
    return {"felder": felder, "ergebnis": text, "ok": ok}


# =============================================================================
# FARBCODE (Sonderfall mit Zeichnung)
# =============================================================================
def _widerstand_svg(farben):
    c = SvgCanvas(560, 168, hintergrund="none")
    widerstand_zeichnen(c, 560, 168, farben)
    return c.svg()


def farbcode(eingaben):
    """Beide Richtungen auf einer Seite. Rückgabe: dict für das Template farbcode.html"""
    # ---- Ringe -> Wert ----
    n = eingaben.get("n", "4")
    n = int(n) if n in ("4", "5", "6") else 4
    ringe, farben = [], []
    for nummer, (name, tabelle) in enumerate(wr.RINGE[n], start=1):
        gewaehlt = eingaben.get(f"r{nummer}", "")
        gewaehlt = gewaehlt if gewaehlt in tabelle else ""
        farben.append(gewaehlt or None)
        ringe.append({"name": f"r{nummer}", "text": f"Ring {nummer}: {name}", "gewaehlt": gewaehlt,
                      "optionen": [{"farbe": f, "hex": wr.FARB_HEX[f]} for f in tabelle]})
    try:
        zeilen_wert, ok_wert = wr.farben_zu_wert(farben), True
    except RechnerFehler as fehler:
        zeilen_wert, ok_wert = [str(fehler)], False

    # ---- Wert -> Ringe ----
    wert_text = eingaben.get("wert", "")
    wert_einheit = eingaben.get("wert-e", "kΩ")
    stufen = dict(einheiten.EINHEITEN["widerstand"]["stufen"])
    wert_einheit = wert_einheit if wert_einheit in stufen else "kΩ"
    anzahl = eingaben.get("ringe", "4")
    anzahl = int(anzahl) if anzahl in ("4", "5") else 4
    toleranzen = [{"farbe": f, "text": f"±{v:g} % ({f})"} for f, v in wr.TOLERANZ.items()]
    tol = eingaben.get("tol", "Gold")
    tol = tol if tol in wr.TOLERANZ else "Gold"
    zeilen_farbe, ok_farbe, farben_ziel = [], True, [None] * (anzahl + 1)
    if wert_text.strip():
        try:
            wert = einheiten.text_zu_zahl(wert_text, "widerstand", stufen[wert_einheit])
            farben_ziel, zeilen_farbe = wr.farbcode_zeilen(wert, anzahl, tol)
        except (RechnerFehler, ValueError) as fehler:
            zeilen_farbe, ok_farbe = [str(fehler)], False

    return {"n": n, "ringe": ringe, "svg_wert": _widerstand_svg(farben),
            "zeilen_wert": zeilen_wert, "ok_wert": ok_wert,
            "wert": wert_text, "wert_einheit": wert_einheit, "einheiten": list(stufen),
            "anzahl": anzahl, "toleranzen": toleranzen, "tol": tol,
            "svg_farbe": _widerstand_svg(farben_ziel), "zeilen_farbe": zeilen_farbe, "ok_farbe": ok_farbe}


# =============================================================================
# SMD-CODE
# =============================================================================
SMD_BEISPIELE = [("103", "3 Ziffern: 10 × 10³"), ("4R7", "R = Komma"), ("4701", "4 Ziffern: 470 × 10¹"),
                 ("01C", "EIA-96 (1 %)"), ("000", "Drahtbrücke")]


def smd(eingaben):
    """'103' -> Ergebniszeilen (oder Meldung). Rechnung: widerstand_rechner.smd_zeilen (wie im Fenster)."""
    code = eingaben.get("code", "").strip()[:20]
    if not code:
        return {"code": "", "zeilen": [], "ok": True, "beispiele": SMD_BEISPIELE}
    try:
        return {"code": code, "zeilen": wr.smd_zeilen(code), "ok": True, "beispiele": SMD_BEISPIELE}
    except RechnerFehler as fehler:
        return {"code": code, "zeilen": [str(fehler)], "ok": False, "beispiele": SMD_BEISPIELE}
