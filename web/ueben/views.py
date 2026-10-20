# =============================================================================
# web/ueben/views.py
# -----------------------------------------------------------------------------
# ÜBUNGEN IM WEB - die Abo-Funktion. Rechnen, Zufallswerte, Kontrolle: uebungen/aufgaben.py (Projekt).
#
#   liste(request)              /uebungen/                       alle Aufgabenarten nach Thema
#   aufgabe(request, art_id)    /uebungen/ohm_strom/?nr=123      eine Aufgabe lösen, kontrollieren, Lösungsweg
#                                 &antwort=25.5&einheit=mA       -> Antwort kontrollieren
#                                 &loesung=1                     -> Lösungsweg zeigen
#   blatt(request)              /uebungen/blatt/                 Übungsblatt zusammenstellen + drucken
#                                 ?art=ohm_strom&art=rc_tau&anzahl=10&nr=…&loesungen=1
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
from uebungen import aufgaben                                          # -> uebungen/aufgaben.py
from wiki import inhalt                                                # -> web/wiki/inhalt.py

MAX_NR = 10 ** 12


def _nr(text):
    """Nummer aus der Adresse: ganze Zahl 1 … MAX_NR, sonst None"""
    try:
        nr = int(str(text))
    except (TypeError, ValueError):
        return None
    return nr if 1 <= nr <= MAX_NR else None


def _gesperrt(request, titel, art_id="ohm_strom"):
    return render(request, "ueben/gesperrt.html", {"titel": titel, "vorschau": aufgaben.vorschau(art_id),
                                                   "gruppen": aufgaben.alle_arten()})


def _seiten(info):
    """Wissensseiten zur Aufgabenart -> [{"slug", "id", "titel", "icon"}]"""
    return [v for v in (inhalt.verweis(bereich, tid) for bereich, tid in info["seiten"]) if v]


def liste(request):
    if not hat_abo(request.user):
        return _gesperrt(request, "Übungen")
    return render(request, "ueben/liste.html", {"gruppen": aufgaben.alle_arten()})


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
    antwort = request.GET.get("antwort", "")[:40]
    einheit = request.GET.get("einheit", a["einheit"])
    if einheit not in a["einheiten"]:
        einheit = a["einheit"]
    pruefung = aufgaben.antwort_pruefen(a, antwort, einheit) if antwort.strip() else None
    zeige_loesung = request.GET.get("loesung") == "1" or bool(pruefung and pruefung["richtig"])
    return render(request, "ueben/aufgabe.html", {
        "a": a, "info": info, "antwort": antwort, "einheit": einheit, "pruefung": pruefung,
        "zeige_loesung": zeige_loesung, "neue_nr": aufgaben.neue_nr(), "seiten": _seiten(info),
        "toleranz": round(aufgaben.TOLERANZ * 100)})


def blatt(request):
    if not hat_abo(request.user):
        return _gesperrt(request, "Übungsblatt erstellen")
    gewaehlt = [a for a in request.GET.getlist("art") if a in aufgaben.ARTEN]
    try:
        anzahl = max(1, min(int(request.GET.get("anzahl", 10)), aufgaben.MAX_ANZAHL))
    except ValueError:
        anzahl = 10
    mit_loesungen = request.GET.get("loesungen") == "1"
    liste_aufgaben, fehler = [], None
    if "erstellen" in request.GET or "nr" in request.GET:
        nr = _nr(request.GET.get("nr"))
        if not gewaehlt:
            fehler = "Bitte mindestens eine Aufgabenart wählen."
        elif nr is None:                       # neue Nummer -> feste Adresse, damit das Blatt gleich bleibt
            teile = "&".join(f"art={a}" for a in gewaehlt)
            return redirect(f"/uebungen/blatt/?{teile}&anzahl={anzahl}&nr={aufgaben.neue_nr()}"
                            f"{'&loesungen=1' if mit_loesungen else ''}")
        else:
            liste_aufgaben = aufgaben.blatt(gewaehlt, anzahl, nr)
    return render(request, "ueben/blatt.html", {
        "gruppen": aufgaben.alle_arten(), "gewaehlt": gewaehlt, "anzahl": anzahl, "max_anzahl": aufgaben.MAX_ANZAHL,
        "mit_loesungen": mit_loesungen, "aufgaben": liste_aufgaben, "fehler": fehler,
        "nr": _nr(request.GET.get("nr"))}, status=400 if fehler else 200)
