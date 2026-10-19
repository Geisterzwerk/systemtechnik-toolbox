# =============================================================================
# web/pruefen_web.py  -  prüft die WEBVERSION: jede Seite einmal aufrufen
# -----------------------------------------------------------------------------
# Im Ordner web/ starten:   python pruefen_web.py        (-v = jede Seite anzeigen)
#
# Ohne Server und ohne Browser: Django hat einen eingebauten Test-Client, der so tut,
# als ob ein Browser die Adresse aufruft.
#
#   1) Startseite, Suche, alle Bereiche und ALLE Wissensseiten -> Status 200, keine Template-Reste
#   2) Jede interaktive Schaltung mit jeder Variante (auch über /schaltung/<id>/), falsche Eingaben;
#      Animationen (Trafo): jede Variante, falsche Werte, komprimiert unter 200 KB
#   3) Jeder Web-Rechner leer und mit Unsinn ("abc", unbekannte Einheit); alle von Hand gerechneten
#      Fälle aus pruefung/rechner_faelle.py -> Web rechnet genau wie die Desktop-App
#   4) Unbekannte Adressen -> 404 statt Absturz
#   5) Sicherheit: Text aus der Adresse erscheint nie als HTML (kein <script> einschleusen)
#   6) "Fehler melden": Speichern, CSRF-Schutz, Bot-Falle, Längen, Sperre bei vielen Meldungen, fremde Adressen
#
# Ergebnis: Exit-Code 0 = alles ok, 1 = mindestens ein Fehler
# WER RUFT DAS AUF?  du (nach jeder Änderung an web/ oder an den Inhalten)
# =============================================================================

import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systemlab_web.settings")
os.environ["SYSTEMLAB_HOSTS"] = "testserver,127.0.0.1,localhost"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging                                                         # noqa: E402

import django                                                          # noqa: E402

django.setup()
logging.getLogger("django.request").setLevel(logging.ERROR)     # 404-Tests sind Absicht, nicht melden
logging.getLogger("django.security.csrf").setLevel(logging.ERROR)   # der Test ohne CSRF-Token (403) auch
from django.test import Client                                         # noqa: E402
from django.utils.html import escape                                   # noqa: E402

from wiki import grafiken, inhalt                                      # noqa: E402  -> web/wiki/
from rechner import formular                                           # noqa: E402  -> web/rechner/

# Django schreibt Zahlen schweizerisch ("3,5") - in Slider-Attributen muss es "3.5" sein
KOMMA_ZAHL = re.compile(r'\b(min|max|value)="-?\d+,\d')
DOPPELTE_ID = re.compile(r'data-schaltung="([^"]+)"')        # jede Grafik höchstens einmal pro Seite
AUSFUEHRLICH = "-v" in sys.argv
# nicht ausgewertete Template-Teile wie "{{ s.zeilen }}" oder "{% if" (Code-Beispiele mit {{1, 2}} sind ok)
REST = re.compile(r"\{\{ ?[a-z_]+(\.[a-z_]+)*(\|[a-z_]+(:[^}]*)?)? ?\}\}|\{% ?(if|for|end|block|load|include|else)")
client = Client()
fehler, ok = [], 0


def abrufen(adresse, erwartet=200, muss_enthalten=()):
    global ok
    try:
        antwort = client.get(adresse)
    except Exception as e:                            # Absturz in einer View
        fehler.append(f"{adresse}: {type(e).__name__}: {e}")
        return None
    text = antwort.content.decode("utf-8", "replace")
    if antwort.status_code != erwartet:
        fehler.append(f"{adresse}: Status {antwort.status_code} statt {erwartet}")
    elif erwartet == 200 and REST.search(text):
        fehler.append(f"{adresse}: Template-Rest im HTML: …{text[REST.search(text).start() - 40:][:90]}…")
    elif KOMMA_ZAHL.search(text):
        fehler.append(f"{adresse}: Zahl mit Komma in einem HTML-Attribut (Slider versteht nur Punkt)")
    elif DOPPELTE_ID.search(text) and len(set(DOPPELTE_ID.findall(text))) != len(DOPPELTE_ID.findall(text)):
        fehler.append(f"{adresse}: dieselbe Grafik zweimal auf der Seite (doppelte id)")
    elif any(m not in text for m in muss_enthalten):
        fehler.append(f"{adresse}: fehlt {[m for m in muss_enthalten if m not in text]}")
    else:
        ok += 1
        if AUSFUEHRLICH:
            print("  ok", adresse)
    return text


t0 = time.time()
# ---- 1) Seiten --------------------------------------------------------------
abrufen("/", muss_enthalten=["SystemLab", "Bereiche"])
abrufen("/rechner/")
for begriff in ("tiefpass", "chmod", "while", "pt100", "ne555", "wiederstand", "ohm", ""):
    abrufen(f"/suche/?q={begriff}")
seiten = 0
for slug, name in inhalt.BEREICHE:
    abrufen(f"/{slug}/")
    for k in inhalt.kategorien(name):
        for t in k.themen:
            abrufen(f"/{slug}/{t.id}/", muss_enthalten=[escape(t.titel)])
            seiten += 1

# ---- 2) Schaltungen ----------------------------------------------------------
import bauteile.rechner as registry                                    # noqa: E402
schaltungen = [rid for rid in registry.registry() if grafiken.ist_schaltung(rid)]
for rid in schaltungen:
    klasse = grafiken._modell_klasse(rid)
    for v in klasse.VARIANTEN or [None]:
        param = f"?{rid}-v={v}" if v else ""
        abrufen(f"/schaltung/{rid}/{param}", muss_enthalten=["<svg"])
    if klasse.REGLER:
        r = klasse.REGLER[0][0]
        abrufen(f"/schaltung/{rid}/?{rid}-{r}=abc", muss_enthalten=["⚠"])          # Unsinn -> Meldung
        abrufen(f"/schaltung/{rid}/?{rid}-{r}=1e30", muss_enthalten=["⚠"])         # ausserhalb der Grenzen
        abrufen(f"/schaltung/{rid}/?{rid}-{r}-e=xyz")                                # unbekannte Einheit
    for schluessel, _text in klasse.SCHALTER:
        abrufen(f"/schaltung/{rid}/?{rid}-{schluessel}=1", muss_enthalten=["checked"])

# ---- 2b) Animationen (Trafo) --------------------------------------------------
for rid in grafiken.ANIMATIONEN:
    klasse = grafiken.ANIMATIONEN[rid]
    for v in klasse.VARIANTEN:
        abrufen(f"/schaltung/{rid}/?{rid}-v={v}", muss_enthalten=["data-animation", 'class="bild"'])
    abrufen(f"/rechner/{rid}/", muss_enthalten=["data-animation"])
    abrufen(f"/schaltung/{rid}/?{rid}-{klasse.REGLER[0][0]}=abc", muss_enthalten=["⚠"])
    abrufen(f"/schaltung/{rid}/?{rid}-{klasse.REGLER[0][0]}=1e9", muss_enthalten=["⚠"])
abrufen("/bauteile/transformator/", muss_enthalten=["data-animation"])
abrufen("/schaltung/trafo_animation/?trafo_animation-N1=10&trafo_animation-U1=400", muss_enthalten=["Sättigung"])
gepackt = client.get("/schaltung/trafo_animation/", HTTP_ACCEPT_ENCODING="gzip")
if gepackt.get("Content-Encoding") == "gzip" and len(gepackt.content) < 200_000:
    ok += 1
else:
    fehler.append(f"Animation nicht komprimiert ({len(gepackt.content) // 1024} KB)")

# ---- 3) Rechner ----------------------------------------------------------------
# Jeder Rechner leer + mit Unsinn; dazu ALLE von Hand gerechneten Fälle aus pruefung/rechner_faelle.py:
# Das Web muss genau dasselbe Ergebnis liefern wie die Desktop-App.
from urllib.parse import urlencode                                     # noqa: E402

from pruefung.rechner_faelle import FAELLE                             # noqa: E402  -> pruefung/rechner_faelle.py

web_ids = formular.web_rechner_ids()
for rid in web_ids:
    abrufen(f"/rechner/{rid}/")
    daten = formular.formel_daten(rid)
    zahlenfelder = [e[0] for e in daten.felder if e[2] not in ("auswahl", "text")] if daten else []
    if zahlenfelder:
        feld = zahlenfelder[0]
        abrufen(f"/rechner/{rid}/?{feld}=abc&rechnen=1", muss_enthalten=["Ungültige Eingabe"])
        abrufen(f"/rechner/{rid}/?{feld}=1&{feld}-e=Parsec&rechnen=1")       # unbekannte Einheit -> Starteinheit
faelle = 0
for rid, texte, erwartet, _rechnung in FAELLE:
    if rid not in web_ids:
        continue
    erwartet_html = [escape(erwartet["fehler"])] if isinstance(erwartet, dict) else [escape(e) for e in erwartet]
    abrufen(f"/rechner/{rid}/?" + urlencode({**texte, "rechnen": "1"}), muss_enthalten=erwartet_html)
    faelle += 1
abrufen("/rechner/farbcode/?n=4&r1=Braun&r2=Schwarz&r3=Rot&r4=Gold", muss_enthalten=["R = 1 kΩ"])
abrufen("/rechner/farbcode/?n=6&r1=Gelb&r2=Violett&r3=Schwarz&r4=Braun&r5=Braun&r6=Rot", muss_enthalten=["50 ppm/K"])
abrufen("/rechner/farbcode/?wert=4k7&ringe=4&tol=Gold", muss_enthalten=["Gelb – Violett – Rot – Gold"])
abrufen("/rechner/farbcode/?wert=abc", muss_enthalten=["abc"])
abrufen("/rechner/farbcode/?n=9&r1=Lila&wert-e=xyz&ringe=7&tol=Pink")
abrufen("/rechner/smd_code/?code=103", muss_enthalten=["R = 10 kΩ"])
abrufen("/rechner/smd_code/?code=4R7", muss_enthalten=["R = 4.7 Ω"])
abrufen("/rechner/smd_code/?code=01C", muss_enthalten=["R = 10 kΩ", "EIA-96"])
abrufen("/rechner/smd_code/?code=97C", muss_enthalten=["zwischen 01 und 96"])
abrufen("/rechner/smd_code/?code=" + "9" * 500)                      # sehr lang -> gekürzt, kein Absturz
abrufen("/rechner/schaltung_ne555/?schaltung_ne555-v=monostabil", muss_enthalten=["<svg", "Impulsdauer"])

# ---- 4) Unbekannte Adressen -------------------------------------------------
for adresse in ("/gibtsnicht/", "/bauteile/gibtsnicht/", "/rechner/gibtsnicht/", "/schaltung/gibtsnicht/",
                "/rechner/werkzeug_uart/"):
    abrufen(adresse, erwartet=404)

# ---- 5) Sicherheit: nichts aus der Adresse als HTML -------------------------
for adresse in ("/suche/?q=<script>alert(1)</script>", "/rechner/ohm_leistung/?U=<script>x</script>&rechnen=1",
                "/schaltung/schaltung_spannungsteiler/?schaltung_spannungsteiler-ue=<b>x</b>"):
    text = abrufen(adresse) or ""
    if "<script>alert" in text or "<script>x" in text or "<b>x</b>" in text:
        fehler.append(f"{adresse}: Eingabe erscheint als HTML (nicht escaped)!")

# ---- 6) Rückmeldungen ("Fehler melden") -------------------------------------
# In eine Test-Datei schreiben - die echten Rückmeldungen bleiben unberührt.
import tempfile                                                        # noqa: E402
from pathlib import Path                                               # noqa: E402

from django.test import override_settings                             # noqa: E402

from wiki import rueckmeldung                                          # noqa: E402  -> web/wiki/rueckmeldung.py


def pruefe(bedingung, text):
    global ok
    if bedingung:
        ok += 1
    else:
        fehler.append("Rückmeldung: " + text)


with tempfile.TemporaryDirectory() as ordner, override_settings(RUECKMELDUNGEN_DATEI=Path(ordner) / "r.jsonl"):
    rueckmeldung._zeiten.clear()
    browser = Client(enforce_csrf_checks=True)                         # wie ein echter Browser: CSRF wird geprüft
    seite = browser.get("/rueckmeldung/?seite=/rechner/rc_zeit/")
    pruefe(seite.status_code == 200 and b"csrfmiddlewaretoken" in seite.content, "Formular ohne CSRF-Feld")
    token = browser.cookies["csrftoken"].value
    gut = {"csrfmiddlewaretoken": token, "art": rueckmeldung.ARTEN[1], "seite": "/rechner/rc_zeit/",
           "text": "Bei 10 kΩ und 100 µF kommt <script>alert(1)</script> heraus"}
    antwort = browser.post("/rueckmeldung/", gut)
    pruefe(antwort.status_code == 302 and antwort["Location"].endswith("/rueckmeldung/danke/"), "Senden klappt nicht")
    gespeichert = rueckmeldung.alle()
    pruefe(len(gespeichert) == 1 and gespeichert[0]["seite"] == "/rechner/rc_zeit/", "nicht gespeichert")
    pruefe(not any(k in gespeichert[0] for k in ("ip", "REMOTE_ADDR")), "IP-Adresse gespeichert")
    pruefe(Client(enforce_csrf_checks=True).post("/rueckmeldung/", {k: v for k, v in gut.items()
                                                                     if k != "csrfmiddlewaretoken"}).status_code == 403,
           "ohne CSRF-Token angenommen")
    pruefe(browser.post("/rueckmeldung/", {**gut, "webseite": "http://spam"}).status_code == 302
           and len(rueckmeldung.alle()) == 1, "Bot (Honigtopf) wurde gespeichert")
    pruefe(browser.post("/rueckmeldung/", {**gut, "text": "kurz"}).status_code == 400, "zu kurzer Text angenommen")
    pruefe(browser.post("/rueckmeldung/", {**gut, "text": "x" * 5000}).status_code == 400, "zu langer Text angenommen")
    pruefe(browser.post("/rueckmeldung/", {**gut, "art": "Hack"}).status_code == 400, "unbekannte Art angenommen")
    browser.post("/rueckmeldung/", {**gut, "seite": "//fremde-seite.ch/x"})
    pruefe(rueckmeldung.alle()[0]["seite"] == "", "fremde Adresse als Seite gespeichert")
    pruefe(b"fremde-seite" not in browser.get("/rueckmeldung/?seite=//fremde-seite.ch").content,
           "fremde Adresse im Formular verlinkt")
    for _ in range(rueckmeldung.MAX_PRO_STUNDE):
        letzte = browser.post("/rueckmeldung/", gut)
    pruefe(letzte.status_code == 400 and "Zu viele" in letzte.content.decode(), "keine Sperre bei vielen Meldungen")
    pruefe(len(rueckmeldung.alle()) == rueckmeldung.MAX_PRO_STUNDE, "Sperre zählt falsch")
    rueckmeldung._zeiten.clear()

print(f"{seiten} Wissensseiten, {len(schaltungen)} Schaltungen, {len(web_ids)} Rechner "
      f"({faelle} Fälle aus rechner_faelle.py) geprüft in {time.time() - t0:.1f} s")
print(f"{ok} Aufrufe ok, {len(fehler)} Fehler")
for f in fehler:
    print("  FEHLER", f)
sys.exit(1 if fehler else 0)
