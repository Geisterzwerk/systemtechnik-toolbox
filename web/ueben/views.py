# =============================================================================
# web/ueben/views.py
# -----------------------------------------------------------------------------
# ÜBUNGEN IM WEB - die Abo-Funktion. Rechnen, Zufallswerte, Kontrolle: uebungen/aufgaben.py (Projekt).
#
#   liste(request)              /uebungen/                       alle Aufgabenarten nach Thema
#                               /uebungen/?stufe=2&bereich=Schaltungen   nur eine Stufe / ein Bereich
#   aufgabe(request, art_id)    /uebungen/ohm_strom/?nr=123      eine Aufgabe lösen, kontrollieren, Lösungsweg
#                                 &antwort=25.5&einheit=mA       -> Antwort kontrollieren (Zahl, Text oder Auswahl)
#                                 &loesung=1                     -> Lösungsweg zeigen
#   blatt(request)              /uebungen/blatt/                 Übungsblatt zusammenstellen + drucken
#                                 ?art=ohm_strom&art=rc_tau&anzahl_1=5&anzahl_3=5&nr=…&loesungen=1
#                                 (anzahl_<Stufe>: so viele Aufgaben dieser Stufe, z.B. 5 Einstieg + 5 Studium)
#
# OHNE ABO (web/konto/zugang.py hat_abo) zeigen alle drei Seiten das Schloss (konto/schloss.html) mit
# einer verschwommenen BEISPIEL-Aufgabe. Die echte Aufgabe, Lösung und Lösungsweg werden dann gar nicht
# erst berechnet - im HTML steht nichts, was man "freilegen" könnte.
#
# Die Nummer nr bestimmt die Zufallswerte: gleiche Nummer = gleiche Aufgabe. So braucht es keine Datenbank,
# und man kann eine Aufgabe als Link weitergeben. Nur lesend -> GET reicht (nichts wird gespeichert).
#
# WER RUFT DAS AUF?  web/ueben/urls.py
# =============================================================================

from django.http import Http404
from django.shortcuts import redirect, render

from konto.zugang import hat_abo                                       # -> web/konto/zugang.py
from programmieren.engine import syntax                                # -> programmieren/engine/syntax.py
from uebungen import aufgaben, schemas                                 # -> uebungen/aufgaben.py, schemas.py
from wiki import inhalt                                                # -> web/wiki/inhalt.py

MAX_NR = 10 ** 12
SCHEMA_BREITE = 440                    # Schema bei einer Aufgabe (Pixel, wird auf dem Handy kleiner)
SCHEMA_BREITE_BLATT = 300              # Schema auf dem Übungsblatt - kleiner, damit mehr auf eine Seite passt


def _nr(text):
    """Nummer aus der Adresse: ganze Zahl 1 … MAX_NR, sonst None"""
    try:
        nr = int(str(text))
    except (TypeError, ValueError):
        return None
    return nr if 1 <= nr <= MAX_NR else None


def vorschau_mit_schema(art_id="ohm_strom"):
    """Beispiel für die verschwommene Vorschau (ohne Lösung) + sein Schema (zeigt nur Gegebenes und "?")."""
    v = aufgaben.vorschau(art_id)
    return {**v, "schema": schemas.schema_paar(v, SCHEMA_BREITE)}


def _gesperrt(request, titel, art_id="ohm_strom"):
    return render(request, "ueben/gesperrt.html", {"titel": titel, "vorschau": vorschau_mit_schema(art_id),
                                                   "baum": aufgaben.alle_arten(), "stufen": aufgaben.STUFEN,
                                                   "anzahl": len(aufgaben.ARTEN)})


def _seiten(info):
    """Wissensseiten zur Aufgabenart -> [{"slug", "id", "titel", "icon"}]"""
    return [v for v in (inhalt.verweis(bereich, tid) for bereich, tid in info["seiten"]) if v]


def _code(a):
    """Code einer Aufgabe mit Syntaxfarben (wie auf den Wissensseiten) -> [{"text", "klasse"}] oder None"""
    if not a.get("code"):
        return None
    return [{"text": text, "klasse": art or ""} for text, art in syntax.zerlegen(a["code"], a.get("sprache") or "python")]


def _zahl(text, standard, unten=0, oben=None):
    try:
        wert = int(str(text))
    except (TypeError, ValueError):
        return standard
    return max(unten, min(wert, oben if oben is not None else wert))


def _filter(request):
    """?stufe=2&bereich=Schaltungen -> (stufe oder None, bereich oder None) - nur bekannte Werte"""
    stufe = _zahl(request.GET.get("stufe"), None)
    bereich = request.GET.get("bereich")
    return (stufe if stufe in aufgaben.STUFEN else None,
            bereich if bereich in aufgaben.BEREICHE else None)


def liste(request):
    if not hat_abo(request.user):
        return _gesperrt(request, "Übungen")
    stufe, bereich = _filter(request)
    return render(request, "ueben/liste.html", {
        "baum": aufgaben.alle_arten(stufe, bereich), "stufen": aufgaben.STUFEN, "stufe": stufe,
        "bereiche": [b for b, _ in aufgaben.alle_arten()], "bereich": bereich, "anzahl": len(aufgaben.ARTEN)})


def aufgabe(request, art_id):
    info = aufgaben.art_info(art_id)
    if info is None:
        raise Http404("Diese Aufgabenart gibt es nicht")
    if not hat_abo(request.user):
        return _gesperrt(request, info["titel"], art_id)
    nr = _nr(request.GET.get("nr"))
    if nr is None:
        return redirect(f"/uebungen/{art_id}/?nr={aufgaben.neue_nr()}")
    a = aufgaben.aufgabe(art_id, nr)
    antwort = request.GET.get("antwort", "")[:aufgaben.MAX_ANTWORT]
    einheit = None
    if a["antwort"] == "zahl":
        einheit = request.GET.get("einheit", a["einheit"])
        if einheit not in a["einheiten"]:
            einheit = a["einheit"]
    pruefung = aufgaben.antwort_pruefen(a, antwort, einheit) if antwort.strip() else None
    zeige_loesung = request.GET.get("loesung") == "1" or bool(pruefung and pruefung["richtig"])
    return render(request, "ueben/aufgabe.html", {
        "a": a, "schema": schemas.schema_paar(a, SCHEMA_BREITE), "code": _code(a), "info": info,
        "antwort": antwort, "einheit": einheit, "pruefung": pruefung,
        "zeige_loesung": zeige_loesung, "neue_nr": aufgaben.neue_nr(), "seiten": _seiten(info),
        "toleranz": round(aufgaben.TOLERANZ * 100)})


STANDARD_PRO_STUFE = {1: 5, 2: 5, 3: 0, 4: 0}       # Vorschlag im Formular: 5 Einstieg + 5 Lehrabschluss


def blatt(request):
    if not hat_abo(request.user):
        return _gesperrt(request, "Übungsblatt erstellen")
    gewaehlt = [a for a in request.GET.getlist("art") if a in aufgaben.ARTEN]
    gesendet = "erstellen" in request.GET or "nr" in request.GET
    pro_stufe = {s: _zahl(request.GET.get(f"anzahl_{s}"), 0 if gesendet else STANDARD_PRO_STUFE[s], 0,
                          aufgaben.MAX_ANZAHL) for s in aufgaben.STUFEN}
    mit_loesungen = request.GET.get("loesungen") == "1"
    liste_aufgaben, hinweise, fehler = [], [], None
    if gesendet:
        nr = _nr(request.GET.get("nr"))
        if not gewaehlt:
            fehler = "Bitte mindestens eine Aufgabenart wählen."
        elif not any(pro_stufe.values()):
            fehler = "Bitte bei mindestens einer Stufe eine Anzahl angeben."
        elif nr is None:                       # neue Nummer -> feste Adresse, damit das Blatt gleich bleibt
            teile = "&".join([f"art={a}" for a in gewaehlt] + [f"anzahl_{s}={n}" for s, n in pro_stufe.items() if n])
            return redirect(f"/uebungen/blatt/?{teile}&nr={aufgaben.neue_nr()}{'&loesungen=1' if mit_loesungen else ''}")
        else:
            roh, hinweise = aufgaben.blatt(gewaehlt, 0, nr, {s: n for s, n in pro_stufe.items() if n})
            liste_aufgaben = [{**a, "schema": schemas.schema_paar(a, SCHEMA_BREITE_BLATT), "code_teile": _code(a)}
                              for a in roh]
    return render(request, "ueben/blatt.html", {
        "baum": aufgaben.alle_arten(), "gewaehlt": gewaehlt, "stufen": aufgaben.STUFEN,
        "pro_stufe": [(s, aufgaben.STUFEN[s], n) for s, n in pro_stufe.items()], "max_anzahl": aufgaben.MAX_ANZAHL,
        "mit_loesungen": mit_loesungen, "aufgaben": liste_aufgaben, "hinweise": hinweise, "fehler": fehler,
        "nr": _nr(request.GET.get("nr"))}, status=400 if fehler else 200)
