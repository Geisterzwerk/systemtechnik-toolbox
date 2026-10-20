# =============================================================================
# web/wiki/views.py
# -----------------------------------------------------------------------------
# SEITEN DER WEBVERSION (ausser Rechner -> web/rechner/views.py)
#
#   startseite(request)                 /
#   suche(request)                      /suche/?q=tiefpass
#   bereich(request, slug)              /schaltungen/
#   thema(request, slug, thema_id)      /schaltungen/spannungsteiler/
#   melden(request)                     /rueckmeldung/?seite=/rechner/rc_zeit/   "Fehler melden" (Formular)
#   schaltung(request, rechner_id)      /schaltung/schaltung_ne555/   nur der Schaltplan-Block
#                                       (das JavaScript holt ihn nach jeder Regler-Änderung neu)
#
# WER RUFT DAS AUF?  web/wiki/urls.py
# =============================================================================

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render

from bauteile.rechner.rechner_info import RECHNER_INFO                 # -> bauteile/rechner/rechner_info.py
from core.inhalte_index import gesamtindex                             # -> core/inhalte_index.py
from programmieren.engine import syntax                                # -> programmieren/engine/syntax.py
from konto.zugang import hat_abo                                       # -> web/konto/zugang.py
from rechner import formular                                           # -> web/rechner/formular.py
from ueben.views import vorschau_mit_schema                            # -> web/ueben/views.py (Beispiel fürs Schloss)
from uebungen import aufgaben                                          # -> uebungen/aufgaben.py (Übungen zur Seite)
from wiki import grafiken, inhalt, rueckmeldung                        # -> web/wiki/grafiken.py, inhalt.py, rueckmeldung.py

MAX_TREFFER = 30


def startseite(request):
    return render(request, "wiki/startseite.html", {
        "web_rechner": formular.web_rechner(settings.WEB_RECHNER_EMPFOHLEN),
        "anzahl_web_rechner": formular.anzahl()[0],
        "anzahl_schaltungen": formular.anzahl()[1],
        "anzahl_seiten": sum(b["seiten"] for b in inhalt.bereich_infos()),
    })


def suche(request):
    anfrage = request.GET.get("q", "").strip()[:100]
    treffer = []
    if anfrage:
        for e in gesamtindex()["suche"].suchen(anfrage, max_treffer=MAX_TREFFER):
            if e.art == "seite":
                treffer.append({"titel": e.titel, "kurz": e.kurz, "icon": e.icon, "ort": e.ort,
                                "url": f"/{inhalt.bereich_slug(e.bereich)}/{e.id}/"})
            else:                                                       # Rechner
                web = formular.web_id(e.id)
                ziel = RECHNER_INFO.get(e.id, {}).get("wissensseite")
                url = f"/rechner/{web}/" if web else None
                if url is None and ziel:                                # im Web noch nicht: zur Wissensseite
                    v = inhalt.verweis(e.bereich, ziel)
                    url = v and f"/{v['slug']}/{v['id']}/"
                treffer.append({"titel": e.titel, "kurz": e.kurz, "icon": e.icon, "ort": e.ort, "url": url,
                                "nur_desktop": web is None})
    return render(request, "wiki/suche.html", {"anfrage": anfrage, "treffer": treffer})


def bereich(request, slug):
    name = inhalt.bereich_name(slug)
    if name is None:
        raise Http404("Diesen Bereich gibt es nicht")
    info = next(b for b in inhalt.bereich_infos() if b["slug"] == slug)
    return render(request, "wiki/bereich.html", {"bereich": info, "kategorien": inhalt.kategorien(name)})


def _code_html(code, sprache):
    """Code mit Syntaxfarben (programmieren/engine/syntax.py) -> [(text, css_klasse)]"""
    return [{"text": text, "klasse": art or ""} for text, art in syntax.zerlegen(code, sprache)]


def thema(request, slug, thema_id):
    name = inhalt.bereich_name(slug)
    e = name and inhalt.thema(name, thema_id)
    if not e:
        raise Http404("Diese Seite gibt es nicht")
    d = e.daten

    # Rechner und Grafiken der Seite einteilen: im Web als Rechner / als Schaltplan / (noch) nur Desktop
    web_rechner, schaltungen, nur_desktop = [], [], []
    # dict.fromkeys: jede ID nur einmal (manche Seiten nennen dieselbe Grafik unter "grafiken" UND "rechner")
    for rid in dict.fromkeys(list(d.get("grafiken", [])) + list(d.get("rechner", []))):
        web = formular.web_id(rid)
        if grafiken.ist_interaktiv(rid):                        # Schaltplan oder Animation direkt auf der Seite
            schaltungen.append(grafiken.block(rid, request.GET))
        elif web and not any(r["id"] == web for r in web_rechner):
            web_rechner.append({"id": web, **formular.info(web)})
        elif not web and rid in RECHNER_INFO:
            nur_desktop.append(RECHNER_INFO[rid]["titel"])

    beispiele = []
    for b in d.get("beispiele", []):
        beispiele.append({**b, "code_teile": [{"sprache": s, "teile": _code_html(c, s)}
                                              for s, c in b.get("code", {}).items()]})
    befehle = [{"titel": g.get("titel", ""),
                "zeilen": [{"befehl": bef, "text": txt, "gefahr": syntax.ist_gefaehrlich(bef)}
                           for bef, txt in g.get("zeilen", [])]} for g in d.get("befehle", [])]
    tabellen = list(d.get("tabellen", [])) + ([d["tabelle"]] if d.get("tabelle") else [])
    bilder = [{"titel": "", "text": "", **b, "url": inhalt.bild_url(b["datei"])} for b in d.get("bilder", [])]
    if d.get("bild"):
        bilder.insert(0, {"datei": d["bild"], "titel": "", "text": d.get("bild_text", ""),
                          "url": inhalt.bild_url(d["bild"])})
    steckbrief = d.get("steckbrief")
    uebungen = aufgaben.arten_zur_seite(name, thema_id)

    return render(request, "wiki/thema.html", {
        "bereich": {"slug": slug, "name": name}, "e": e, "d": d,
        "kategorie": e.ort.split(" › ", 1)[-1],
        "steckbrief": steckbrief, "symbole": grafiken.symbole(steckbrief.get("symbol", "")) if steckbrief else [],
        "tabellen": tabellen, "bilder": [b for b in bilder if b["url"]],
        "beispiele": beispiele, "befehle": befehle,
        "siehe_auch": [v for v in (inhalt.verweis(name, s) for s in d.get("siehe_auch", [])) if v],
        "web_rechner": web_rechner, "schaltungen": schaltungen, "nur_desktop": nur_desktop,
        # Übungen zu dieser Seite: Titel immer sichtbar, Links nur mit Abo (sonst Schloss + Beispiel ohne Lösung)
        "uebungen": uebungen,
        "vorschau": vorschau_mit_schema(uebungen[0]["id"]) if uebungen and not hat_abo(request.user) else None,
    })


def schaltung(request, rechner_id):
    if not grafiken.ist_interaktiv(rechner_id):
        raise Http404("Diese Schaltung gibt es nicht")
    return render(request, "wiki/schaltung.html", {"s": grafiken.block(rechner_id, request.GET)})


def melden(request):
    """GET: Formular zeigen.  POST: prüfen, speichern, weiter zur Danke-Seite (kein doppeltes Absenden bei F5)."""
    if request.method == "POST":
        if rueckmeldung.ist_bot(request.POST):
            return redirect("rueckmeldung_danke")                # Bots merken nichts - gespeichert wird nichts
        meldung, fehler = rueckmeldung.pruefen(request.POST)
        if not fehler and rueckmeldung.zu_viele(request.META.get("REMOTE_ADDR", "")):
            fehler = ["Zu viele Meldungen in kurzer Zeit – bitte später nochmals versuchen."]
        if not fehler:
            rueckmeldung.speichern(meldung)
            return redirect("rueckmeldung_danke")
        return render(request, "wiki/rueckmeldung.html", {"arten": rueckmeldung.ARTEN, "m": meldung,
                                                           "fehler": fehler, "max_text": rueckmeldung.MAX_TEXT},
                      status=400)
    meldung = {"art": "", "text": "", "kontakt": "", "seite": rueckmeldung.eigene_seite(request.GET.get("seite", ""))}
    return render(request, "wiki/rueckmeldung.html", {"arten": rueckmeldung.ARTEN, "m": meldung, "fehler": [],
                                                       "max_text": rueckmeldung.MAX_TEXT})


def melden_danke(request):
    return render(request, "wiki/rueckmeldung_danke.html")
