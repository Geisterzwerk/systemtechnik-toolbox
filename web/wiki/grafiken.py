# =============================================================================
# web/wiki/grafiken.py
# -----------------------------------------------------------------------------
# GRAFIKEN IM BROWSER - derselbe Zeichencode wie in der Desktop-App, nur auf ein SvgCanvas:
#
#   symbole(schluessel)             Schaltzeichen eines Steckbriefs (bauteile/grafiken/symbole.py)
#   ist_schaltung(rechner_id)       interaktive Schaltung, die das Web zeichnen kann?
#   schaltung(rechner_id, eingaben) alles für einen interaktiven Schaltplan: Varianten, Schalter,
#                                   Regler (Text + Einheit + Slider), SVG hell/dunkel, Ergebnis
#
# Jede Grafik wird ZWEIMAL gezeichnet (hell und dunkel). Das CSS zeigt die passende
# (web/static/systemlab.css: .nur-hell / .nur-dunkel). So braucht es keinen Neuaufbau beim Umschalten.
#
# EINGABEN einer Schaltung (Adresse oder Formular), alle mit der Rechner-ID davor:
#   <id>-v=Variante   <id>-alt=vorherige Variante   <id>-<regler>=Text   <id>-<regler>-e=Einheit
#   <id>-<schalter>=1
#
# WER RUFT DAS AUF?  web/wiki/views.py (Wissensseiten, /schaltung/<id>/)
# =============================================================================

import json
import math

import bauteile.rechner as rechner_registry                            # -> bauteile/rechner/__init__.py
from bauteile import einheiten                                         # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import SchaltungsModell, farbe_waehlen   # -> bauteile/grafiken/schaltplan.py
from bauteile.grafiken.svg_canvas import SvgCanvas, schaltung_svg     # -> bauteile/grafiken/svg_canvas.py
from bauteile.grafiken.symbole import SYMBOLE                          # -> bauteile/grafiken/symbole.py
from bauteile.rechner.kern import GrafikVerweis                        # -> bauteile/rechner/kern.py
import config                                                          # -> config.py

SYMBOL_BREITE = 300


def _paar(farbe):
    """Farbe (oder Paar hell/dunkel) -> {"hell": ..., "dunkel": ...} für das CSS"""
    return {"hell": farbe_waehlen(farbe, False), "dunkel": farbe_waehlen(farbe, True)}


# =============================================================================
# SCHALTZEICHEN (Steckbrief)
# =============================================================================
def symbole(schluessel):
    """[{"text": "IEC / EN (Europa)", "hell": "<svg…>", "dunkel": "<svg…>"}, ...] oder []"""
    ergebnis = []
    for variante in SYMBOLE.get(schluessel, []):
        hoehe = round(SYMBOL_BREITE * variante.seitenverhaeltnis)
        bilder = {}
        for modus, dunkel in (("hell", False), ("dunkel", True)):
            c = SvgCanvas(SYMBOL_BREITE, hoehe, dunkel, hintergrund="none")
            variante.zeichnen(c, SYMBOL_BREITE, hoehe, farbe_waehlen(config.FARBEN["text"], dunkel))
            bilder[modus] = c.svg()
        ergebnis.append({"text": variante.text, **bilder})
    return ergebnis


# =============================================================================
# INTERAKTIVE SCHALTUNGEN
# =============================================================================
def _modell_klasse(rechner_id):
    eintrag = rechner_registry.registry().get(rechner_id)
    # nur schaltungen/grafiken*.py: diese Dateien laden kein tkinter (Webserver hat keins)
    if not isinstance(eintrag, GrafikVerweis) or not eintrag.modul.startswith("schaltungen."):
        return None
    klasse = eintrag.klasse()
    return klasse if isinstance(klasse, type) and issubclass(klasse, SchaltungsModell) else None


def ist_schaltung(rechner_id):
    return _modell_klasse(rechner_id) is not None


def _html_zahl(zahl):
    """Zahl für HTML-Attribute: immer mit Punkt, z.B. "4.67" """
    return repr(float(zahl))


def _zahl_text(zahl, ganzzahl=False):
    return f"{zahl:.0f}" if ganzzahl else f"{zahl:.4g}"


def schaltung(rechner_id, eingaben):
    """eingaben: request.GET (oder dict). Rückgabe: dict für das Template schaltung.html"""
    klasse = _modell_klasse(rechner_id)
    p = f"{rechner_id}-"
    varianten = klasse.VARIANTEN
    variante = eingaben.get(p + "v") if varianten else None
    if varianten and variante not in varianten:
        variante = varianten[0]
    werte = klasse.startwerte(variante)
    gewechselt = varianten and eingaben.get(p + "alt") not in (None, variante)

    regler, meldungen = [], []
    for schluessel, text, typ, von, bis, start, *opt in klasse.REGLER:
        opt = opt[0] if opt else {}
        info = einheiten.EINHEITEN[typ]
        stufen = dict(info["stufen"])
        einheit = eingaben.get(f"{p}{schluessel}-e") or opt.get("einheit") or info["standard"]
        if einheit not in stufen:
            einheit = opt.get("einheit") or info["standard"]
        wert, fehler = werte[schluessel], None
        eingabe = eingaben.get(p + schluessel)
        if eingabe not in (None, "") and not (gewechselt and schluessel in klasse.STARTWERTE.get(variante, {})):
            try:
                neu = einheiten.text_zu_zahl(eingabe, typ, stufen[einheit])
                unten, oben = opt.get("grenzen") or (von, bis)
                if neu is None:
                    fehler = "Bitte einen Wert eingeben"
                elif not unten <= neu <= oben:
                    fehler = f"Erlaubt: {einheiten.formatieren(unten, typ)} … {einheiten.formatieren(oben, typ)}"
                elif opt.get("ganzzahl") and abs(neu - round(neu)) > 1e-9:
                    fehler = "Nur ganze Zahlen erlaubt"
                else:
                    wert = neu
            except ValueError as e:
                fehler = str(e)
        if fehler:
            meldungen.append(f"{text}: {fehler}")
        werte[schluessel] = wert
        log = bool(opt.get("log"))
        lo, hi = min(von, wert), max(bis, wert)
        regler.append({
            "name": p + schluessel, "text": text, "einheit": einheit, "fehler": fehler,
            "feld": eingabe if fehler else _zahl_text(wert / stufen[einheit], opt.get("ganzzahl")),
            "einheiten": [n for n, _ in info["stufen"]],
            "faktoren": json.dumps(dict(info["stufen"])),
            "log": log, "ganzzahl": bool(opt.get("ganzzahl")),
            # als TEXT mit Punkt: Django würde Zahlen schweizerisch mit Komma ausgeben ("3,5"),
            # das versteht <input type="range"> nicht
            "min": _html_zahl(math.log10(lo) if log else lo), "max": _html_zahl(math.log10(hi) if log else hi),
            "pos": _html_zahl(math.log10(wert) if log else wert),
        })
    schalter = []
    for schluessel, text in klasse.SCHALTER:
        werte[schluessel] = eingaben.get(p + schluessel) == "1"
        schalter.append({"name": p + schluessel, "text": text, "an": werte[schluessel]})

    hell = schaltung_svg(klasse, werte, variante, dunkel=False)
    dunkel = schaltung_svg(klasse, werte, variante, dunkel=True)
    return {"id": rechner_id, "titel": klasse.TITEL, "untertitel": klasse.UNTERTITEL,
            "erklaerung": klasse.ERKLAERUNG, "varianten": varianten, "variante": variante,
            "schalter": schalter, "regler": regler, "meldungen": meldungen,
            "svg_hell": hell["svg"], "svg_dunkel": dunkel["svg"],
            "zeilen": hell["zeilen"], "fehler": hell["fehler"],
            "farbe": {"hell": hell["farbe"] or _paar(config.FARBEN["akzent"])["hell"],
                      "dunkel": dunkel["farbe"] or _paar(config.FARBEN["akzent"])["dunkel"]}}
