# =============================================================================
# web/wiki/grafiken.py
# -----------------------------------------------------------------------------
# GRAFIKEN IM BROWSER - derselbe Zeichencode wie in der Desktop-App, nur auf ein SvgCanvas:
#
#   symbole(schluessel)             Schaltzeichen eines Steckbriefs (bauteile/grafiken/symbole.py)
#   ist_schaltung(rechner_id)       interaktive Schaltung, die das Web zeichnen kann?
#   alle_schaltungen()              IDs aller solchen Schaltungen
#   schaltung(rechner_id, eingaben) alles für einen interaktiven Schaltplan: Varianten, Schalter,
#                                   Regler (Text + Einheit + Slider), SVG hell/dunkel, Ergebnis
#   animation(rechner_id, eingaben) dasselbe für eine Animation (Trafo): alle Bilder einer Schleife
#                                   zeichnet Python vorab, systemlab.js spielt sie ab
#   block(rechner_id, eingaben)     Schaltplan oder Animation - je nach ID
#   ist_interaktiv(id), interaktive_ids()   alles, was das Web interaktiv zeichnen kann
#
# Jede Grafik wird ZWEIMAL gezeichnet (hell und dunkel). Das CSS zeigt die passende
# (web/static/systemlab.css: .nur-hell / .nur-dunkel). So braucht es keinen Neuaufbau beim Umschalten.
#
# EINGABEN einer Schaltung (Adresse oder Formular), alle mit der Rechner-ID davor:
#   <id>-v=Variante   <id>-alt=vorherige Variante   <id>-<regler>=Text   <id>-<regler>-e=Einheit
#   <id>-<regler>-ea=Einheit, in der der Text steht (bis zum Wechsel = -e)   <id>-<schalter>=1
#   <id>-<auswahl>=Option (nur Werte aus der Liste)   <id>-<textfeld>=Text (bereinigt, gekürzt - text_eingabe)
#
# WER RUFT DAS AUF?  web/wiki/views.py (Wissensseiten, /schaltung/<id>/)
# =============================================================================

import json
import math

import bauteile.rechner as rechner_registry                            # -> bauteile/rechner/__init__.py
from bauteile import einheiten                                         # -> bauteile/einheiten.py
from bauteile.grafiken.schaltplan import SchaltungsModell, farbe_waehlen, text_eingabe   # -> grafiken/schaltplan.py
from bauteile.grafiken.svg_canvas import SvgCanvas, schaltung_svg     # -> bauteile/grafiken/svg_canvas.py
from bauteile.grafiken.symbole import SYMBOLE                          # -> bauteile/grafiken/symbole.py
from bauteile.grafiken.trafo_modell import TrafoModell                 # -> bauteile/grafiken/trafo_modell.py
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
    # nur Module ohne tkinter (Webserver hat keins) -> bauteile/rechner/__init__.py MODULE_OHNE_FENSTER
    if not isinstance(eintrag, GrafikVerweis) or not eintrag.modul.startswith(rechner_registry.MODULE_OHNE_FENSTER):
        return None
    klasse = eintrag.klasse()
    return klasse if isinstance(klasse, type) and issubclass(klasse, SchaltungsModell) else None


def ist_schaltung(rechner_id):
    return _modell_klasse(rechner_id) is not None


def alle_schaltungen():
    """IDs aller Schaltpläne, die das Web zeichnen kann."""
    return [rid for rid in rechner_registry.registry() if ist_schaltung(rid)]


def _html_zahl(zahl):
    """Zahl für HTML-Attribute: immer mit Punkt, z.B. "4.67" """
    return repr(float(zahl))


def _zahl_text(zahl, ganzzahl=False):
    return f"{zahl:.0f}" if ganzzahl else f"{zahl:.4g}"


def _bedienung(klasse, rechner_id, eingaben):
    """
    Varianten, Regler und Schalter aus den Eingaben lesen - gemeinsam für Schaltpläne und Animationen.
    Rückgabe: dict mit variante, werte (Basiseinheiten), regler/schalter (für das Template), meldungen
    """
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
        start_einheit = opt.get("einheit") or info["standard"]
        einheit = eingaben.get(f"{p}{schluessel}-e") or start_einheit
        if einheit not in stufen:
            einheit = start_einheit
        # Einheit gerade gewechselt? Die Zahl im Feld steht noch in der ALTEN Einheit (<id>-<regler>-ea)
        alt_einheit = eingaben.get(f"{p}{schluessel}-ea")
        if alt_einheit not in stufen:
            alt_einheit = einheit
        # Der Bereich gilt in der gewählten Einheit: 0 … 600 mV -> mit V 0 … 600 V (bauteile/einheiten.py)
        lo_s, hi_s, (unten, oben) = einheiten.regler_bereich(typ, von, bis, opt.get("grenzen"), start_einheit, einheit)
        wert, fehler = werte[schluessel], None
        eingabe = eingaben.get(p + schluessel)
        if eingabe not in (None, "") and not (gewechselt and schluessel in klasse.STARTWERTE.get(variante, {})):
            try:
                neu = einheiten.text_zu_zahl(eingabe, typ, stufen[alt_einheit])
                if neu is not None and alt_einheit != einheit:          # Wert bleibt, rückt höchstens an den Rand
                    neu = min(max(neu, lo_s), hi_s)
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
        lo, hi = min(lo_s, wert), max(hi_s, wert)
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
    neu_gesetzt = klasse.STARTWERTE.get(variante, {}) if gewechselt else {}      # Variante gewechselt -> Startwerte
    auswahl = []
    for schluessel, text, optionen, _start in getattr(klasse, "AUSWAHL", []):        # Trafo-Animation hat keine
        wert = eingaben.get(p + schluessel)
        if wert not in optionen or schluessel in neu_gesetzt:             # nur Werte aus der Liste - nie fremder Text
            wert = werte[schluessel]
        werte[schluessel] = wert
        auswahl.append({"name": p + schluessel, "text": text, "optionen": optionen, "wert": wert})
    textfelder = []
    for schluessel, text, _start, opt in getattr(klasse, "TEXTFELDER", []):
        laenge = opt.get("max", 40)
        eingabe = eingaben.get(p + schluessel)
        if eingabe is not None and schluessel not in neu_gesetzt:
            werte[schluessel] = text_eingabe(eingabe, laenge)             # Steuerzeichen raus, gekürzt
        textfelder.append({"name": p + schluessel, "text": text, "wert": werte[schluessel], "max": laenge,
                           "platzhalter": opt.get("platzhalter", "")})

    return {"id": rechner_id, "titel": klasse.TITEL, "untertitel": klasse.UNTERTITEL,
            "erklaerung": klasse.ERKLAERUNG, "varianten": varianten, "variante": variante,
            "schalter": schalter, "auswahl": auswahl, "textfelder": textfelder, "regler": regler,
            "meldungen": meldungen, "werte": werte}


def schaltung(rechner_id, eingaben):
    """eingaben: request.GET (oder dict). Rückgabe: dict für das Template schaltung.html"""
    klasse = _modell_klasse(rechner_id)
    b = _bedienung(klasse, rechner_id, eingaben)
    hell = schaltung_svg(klasse, b["werte"], b["variante"], dunkel=False)
    dunkel = schaltung_svg(klasse, b["werte"], b["variante"], dunkel=True)
    return {**b, "svg_hell": hell["svg"], "svg_dunkel": dunkel["svg"],
            "zeilen": hell["zeilen"], "fehler": hell["fehler"],
            "farbe": {"hell": hell["farbe"] or _paar(config.FARBEN["akzent"])["hell"],
                      "dunkel": dunkel["farbe"] or _paar(config.FARBEN["akzent"])["dunkel"]}}


# =============================================================================
# ANIMATIONEN (z.B. Trafo)
# =============================================================================
# Rechner-ID -> Modell ohne Fenster. Ein Modell braucht: REGLER, VARIANTEN, SCHALTER, STARTWERTE, startwerte(),
# setzen(werte, variante, zeit), statisch(c, w, h) -> geo, dynamisch(c, geo, t), weiter(t, dt), info(),
# PERIODE (s), SEITENVERHAELTNIS, MAX_HOEHE, TITEL, UNTERTITEL, ERKLAERUNG.
# Optional UMSCHALT_VARIANTE: diese Variante wird als "Umschalten" gezeigt: 1 s erste Variante, umschalten,
# einmal_dauer() s lang EINMAL abspielen, danach nur noch ruhe_periode() s als Schleife (beim Trafo: AC -> DC
# mit Impuls, danach bleibt U2 = 0 stehen - wie in der Desktop-App).
ANIMATIONEN = {"trafo_animation": TrafoModell}
BREITE = 820
BILDER_PRO_PERIODE = 50                  # 50 Bilder in 2.5 s = 20 Bilder/s (flüssig genug, Seite bleibt klein)


def ist_animation(rechner_id):
    return rechner_id in ANIMATIONEN


def ist_interaktiv(rechner_id):
    """Schaltplan oder Animation - beides kann das Web zeichnen."""
    return ist_schaltung(rechner_id) or ist_animation(rechner_id)


def interaktive_ids():
    return [rid for rid in rechner_registry.registry() if ist_interaktiv(rid)]


def _zeitpunkte(klasse, modell, werte, variante):
    """Zeitpunkte aller Bilder + ab welchem Bild die Schleife beginnt.
    Normal: eine Schwingung, Schleife ab Bild 0. Umschalten: einmal ablaufen, dann nur der Ruhezustand."""
    ziel_dt = klasse.PERIODE / BILDER_PRO_PERIODE
    if variante is not None and variante == getattr(klasse, "UMSCHALT_VARIANTE", None):
        modell.setzen(werte, klasse.VARIANTEN[0], 0.0)
        modell.setzen(werte, variante, 1.0)          # nach 1 s umschalten
        einmal = round(modell.einmal_dauer() / ziel_dt)
        ruhe = max(2, round(modell.ruhe_periode() / ziel_dt))
        dt_ruhe = modell.ruhe_periode() / ruhe       # genau passend -> Punkte stehen am Ende wie am Anfang
        zeiten = [i * ziel_dt for i in range(einmal)]
        zeiten += [einmal * ziel_dt + i * dt_ruhe for i in range(ruhe)]
        return zeiten, einmal
    modell.setzen(werte, variante, 0.0)
    return [i * ziel_dt for i in range(BILDER_PRO_PERIODE)], 0      # genau eine Schwingung


def _bilder(klasse, werte, variante, dunkel):
    """Statische Zeichnung + alle Bilder als EIN SVG: <g class="bild"> pro Bild.
    systemlab.js zeigt nacheinander immer genau eines davon und springt am Ende zurück zum Bild 'schleife_ab'.
    Rückgabe: (svg, Millisekunden pro Bild, schleife_ab)"""
    modell = klasse()
    hoehe = min(int(BREITE * klasse.SEITENVERHAELTNIS), klasse.MAX_HOEHE)
    zeiten, schleife_ab = _zeitpunkte(klasse, modell, werte, variante)
    c = SvgCanvas(BREITE, hoehe, dunkel)
    geo = modell.statisch(c, BREITE, hoehe)
    bilder = []
    for i, t in enumerate(zeiten):
        if i:
            modell.weiter(t, t - zeiten[i - 1])
        bild = SvgCanvas(BREITE, hoehe, dunkel)
        modell.dynamisch(bild, geo, t)
        sichtbar = "" if i == 0 else ' style="display:none"'
        bilder.append(f'<g class="bild"{sichtbar}>{bild.inhalt()}</g>')
    return c.svg("".join(bilder)), round(klasse.PERIODE / BILDER_PRO_PERIODE * 1000), schleife_ab


def animation(rechner_id, eingaben):
    """Wie schaltung(), aber mit Bildern zum Abspielen (Template schaltung.html, s.animation = True)."""
    klasse = ANIMATIONEN[rechner_id]
    b = _bedienung(klasse, rechner_id, eingaben)
    svg_hell, ms, schleife_ab = _bilder(klasse, b["werte"], b["variante"], False)
    svg_dunkel, _ms, _ab = _bilder(klasse, b["werte"], b["variante"], True)
    modell = klasse()
    modell.setzen(b["werte"], b["variante"])
    zeilen, warnung = modell.info()
    farbe = ("#B45309", "#F59E0B") if warnung else config.FARBEN["akzent"]
    return {**b, "animation": True, "bild_ms": ms, "schleife_ab": schleife_ab,
            "svg_hell": svg_hell, "svg_dunkel": svg_dunkel,
            "zeilen": zeilen, "fehler": None, "farbe": _paar(farbe)}


def block(rechner_id, eingaben):
    """Schaltplan ODER Animation - für Wissensseite, Rechner-Seite und /schaltung/<id>/."""
    return animation(rechner_id, eingaben) if ist_animation(rechner_id) else schaltung(rechner_id, eingaben)
