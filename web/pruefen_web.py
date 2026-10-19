# =============================================================================
# web/pruefen_web.py  -  prüft die WEBVERSION: jede Seite einmal aufrufen
# -----------------------------------------------------------------------------
# Im Ordner web/ starten:   python pruefen_web.py        (-v = jede Seite anzeigen)
#
# Ohne Server und ohne Browser: Django hat einen eingebauten Test-Client, der so tut,
# als ob ein Browser die Adresse aufruft.
#
#   1) Startseite, Suche, alle Bereiche und ALLE Wissensseiten -> Status 200, keine Template-Reste
#   2) Jede interaktive Schaltung mit jeder Variante (auch über /schaltung/<id>/), falsche Eingaben
#   3) Jeder Web-Rechner leer, mit Beispielwerten und mit Unsinn ("abc", unbekannte Einheit)
#   4) Unbekannte Adressen -> 404 statt Absturz
#   5) Sicherheit: Text aus der Adresse erscheint nie als HTML (kein <script> einschleusen)
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
from django.test import Client                                         # noqa: E402
from django.utils.html import escape                                   # noqa: E402

from wiki import grafiken, inhalt                                      # noqa: E402  -> web/wiki/
from rechner import formular                                           # noqa: E402  -> web/rechner/

# Django schreibt Zahlen schweizerisch ("3,5") - in Slider-Attributen muss es "3.5" sein
KOMMA_ZAHL = re.compile(r'\b(min|max|value)="-?\d+,\d')
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

# ---- 3) Rechner ----------------------------------------------------------------
BEISPIELE = {
    "ohm_leistung": ("?U=12&I=20&I-e=mA&rechnen=1", "R = 600 Ω"),
    "spannungsteiler": ("?rechnen=1", None),
    "rc_zeit": ("?R=10&R-e=kΩ&C=100&C-e=µF&rechnen=1", "τ = R · C = 1 s"),
    "dmm_genauigkeit": ("?rechnen=1", None),
}
for rid in formular.web_rechner_ids():
    abrufen(f"/rechner/{rid}/")
    if rid in BEISPIELE:
        param, erwartet = BEISPIELE[rid]
        abrufen(f"/rechner/{rid}/{param}", muss_enthalten=[erwartet] if erwartet else [])
    daten = formular.formel_daten(rid)
    if daten:
        feld = daten.felder[0][0]
        abrufen(f"/rechner/{rid}/?{feld}=abc&rechnen=1", muss_enthalten=["Ungültige Eingabe"])
        abrufen(f"/rechner/{rid}/?{feld}=1&{feld}-e=Parsec&rechnen=1")       # unbekannte Einheit -> Starteinheit
abrufen("/rechner/farbcode/?n=4&r1=Braun&r2=Schwarz&r3=Rot&r4=Gold", muss_enthalten=["R = 1 kΩ"])
abrufen("/rechner/farbcode/?n=6&r1=Gelb&r2=Violett&r3=Schwarz&r4=Braun&r5=Braun&r6=Rot", muss_enthalten=["50 ppm/K"])
abrufen("/rechner/farbcode/?wert=4k7&ringe=4&tol=Gold", muss_enthalten=["Gelb – Violett – Rot – Gold"])
abrufen("/rechner/farbcode/?wert=abc", muss_enthalten=["abc"])
abrufen("/rechner/farbcode/?n=9&r1=Lila&wert-e=xyz&ringe=7&tol=Pink")

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

print(f"{seiten} Wissensseiten, {len(schaltungen)} Schaltungen, {len(formular.web_rechner_ids())} Rechner "
      f"geprüft in {time.time() - t0:.1f} s")
print(f"{ok} Aufrufe ok, {len(fehler)} Fehler")
for f in fehler:
    print("  FEHLER", f)
sys.exit(1 if fehler else 0)
