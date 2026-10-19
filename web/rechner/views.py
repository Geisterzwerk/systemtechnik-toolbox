# =============================================================================
# web/rechner/views.py
# -----------------------------------------------------------------------------
#   liste(request)               /rechner/              alle im Web freigeschalteten Rechner
#   rechner(request, id)         /rechner/ohm_leistung/ ein Rechner (Formular + Ergebnis),
#                                auch Farbcode, SMD-Code und jeder interaktive Schaltplan
#
# Die Formulare schicken mit GET - so kann man ein Ergebnis als Link weitergeben,
# z.B. /rechner/ohm_leistung/?U=12&I=20&I-e=mA&rechnen=1
#
# WER RUFT DAS AUF?  web/rechner/urls.py
# =============================================================================

from django.http import Http404
from django.shortcuts import render

from rechner import formular                                           # -> web/rechner/formular.py
from wiki import grafiken, inhalt                                      # -> web/wiki/grafiken.py, inhalt.py


def liste(request):
    return render(request, "rechner/liste.html", {"kategorien": formular.nach_kategorien(),
                                                  "anzahl": formular.anzahl()[0], "schaltplaene": formular.anzahl()[1]})


def _wissensseite(info):
    """Link zur passenden Wissensseite (falls vorhanden)."""
    ziel = info.get("wissensseite")
    if not ziel:
        return None
    for _slug, name in inhalt.BEREICHE:
        v = inhalt.verweis(name, ziel)
        if v:
            return v
    return None


def rechner(request, rechner_id):
    info = formular.info(rechner_id) if rechner_id in formular.web_rechner_ids() else None
    if info is None:
        raise Http404("Diesen Rechner gibt es im Web (noch) nicht")
    kontext = {"id": rechner_id, "info": info, "wissen": _wissensseite(info)}
    if rechner_id == "farbcode":
        return render(request, "rechner/farbcode.html", {**kontext, "f": formular.farbcode(request.GET)})
    if rechner_id == "smd_code":
        return render(request, "rechner/smd.html", {**kontext, "f": formular.smd(request.GET)})
    if grafiken.ist_interaktiv(rechner_id):                      # Schaltplan oder Animation als eigene Seite
        return render(request, "rechner/schaltung.html", {**kontext, "s": grafiken.block(rechner_id, request.GET)})
    daten = formular.formel_daten(rechner_id)
    if daten is None:
        raise Http404("Dieser Rechner braucht noch die Desktop-App")
    return render(request, "rechner/formel.html", {**kontext, "daten": daten,
                                                   "r": formular.formel_rechnen(daten, request.GET)})
