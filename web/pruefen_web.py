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
#   7) Konten + Abo: Gäste sehen nur das Schloss (keine Lösung im HTML), Registrieren (Passwortregeln, Bot-Falle,
#      CSRF), Login-Sperre, sichere Weiterleitung, Abmelden nur POST, Abo-Gruppe, Admin, Passwort, Löschen
#
# Die Datenbank ist eine TEST-Datenbank in einem temporären Ordner - deine echte (web/daten/) bleibt unberührt.
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
import tempfile                                                        # noqa: E402

_TEST_ORDNER = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)   # Test-Datenbank, nach dem Lauf weg
os.environ["SYSTEMLAB_DB"] = os.path.join(_TEST_ORDNER.name, "test.sqlite3")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging                                                         # noqa: E402

import django                                                          # noqa: E402

django.setup()
from django.core.management import call_command                       # noqa: E402

call_command("migrate", verbosity=0)                                   # Tabellen in der Test-Datenbank anlegen
logging.getLogger("django.request").setLevel(logging.ERROR)     # 404-Tests sind Absicht, nicht melden
logging.getLogger("django.security.csrf").setLevel(logging.ERROR)   # der Test ohne CSRF-Token (403) auch
from django.test import Client                                         # noqa: E402
from django.utils.html import escape                                   # noqa: E402

from wiki import grafiken, inhalt                                      # noqa: E402  -> web/wiki/
from rechner import formular                                           # noqa: E402  -> web/rechner/

# Django schreibt Zahlen schweizerisch ("3,5") - in Slider-Attributen muss es "3.5" sein
KOMMA_ZAHL = re.compile(r'<input type="range"[^>]*\b(min|max|value)="-?\d+,\d')   # nur Slider (Textfelder dürfen Kommas)
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
for v in grafiken.ANIMATIONEN["trafo_animation"].VARIANTEN:              # jede Variante: komprimiert < 200 KB
    gepackt = client.get("/schaltung/trafo_animation/", {"trafo_animation-v": v}, HTTP_ACCEPT_ENCODING="gzip")
    if gepackt.get("Content-Encoding") == "gzip" and len(gepackt.content) < 200_000:
        ok += 1
    else:
        fehler.append(f"Animation {v}: zu gross oder nicht komprimiert ({len(gepackt.content) // 1024} KB)")
dc = client.get("/schaltung/trafo_animation/", {"trafo_animation-v": "═ Gleichspannung (DC)"}).content.decode()
if 'data-schleife-ab="0"' in dc or "data-animation-nochmal" not in dc:  # DC: Umschalten einmal, dann Ruhe
    fehler.append("Trafo DC: Umschalten läuft nicht nur einmal (data-schleife-ab fehlt)")
else:
    ok += 1

# ---- 2c) Einheit wechseln: der Slider-Bereich gilt in der neuen Einheit ---------
#   Messreihe "syst": -100 … 100 mV. Mit V: -100 … 100 V, mit µV: -100 … 100 µV.
EINHEIT_FAELLE = [
    # (Adresse-Teil, muss enthalten, darf nicht enthalten)
    ("syst=30&messreihe-syst-e=V&messreihe-syst-ea=mV", ['value="0.03"', 'max="100.0"'], ["⚠"]),   # Wert bleibt
    ("syst=50&messreihe-syst-e=V&messreihe-syst-ea=V", ['value="50"'], ["⚠"]),                    # 50 V erlaubt
    ("syst=50&messreihe-syst-e=µV&messreihe-syst-ea=mV", ['value="100"', 'max="0.0001"'], ["⚠"]),  # an den Rand
    ("syst=5000&messreihe-syst-e=V&messreihe-syst-ea=V", ["⚠"], []),                              # > Grenze 1000 V
]
for teil, muss, nicht in EINHEIT_FAELLE:
    adresse = f"/schaltung/messreihe/?messreihe-{teil}"
    text = abrufen(adresse, muss_enthalten=muss)
    if text is not None and any(n in text for n in nicht):
        fehler.append(f"{adresse}: enthält {[n for n in nicht if n in text]}")

# ---- 2d) Textfelder und Auswahl der Modelle (Digitaltechnik): sicher und verständlich ----
abrufen("/rechner/werkzeug_uart/", muss_enthalten=["<svg"])                       # früher nur in der Desktop-App
for adresse, muss in (
        ("/schaltung/werkzeug_ausdruck/?werkzeug_ausdruck-ausdruck=A*B%2B!C", ["Gelesen als"]),
        ("/schaltung/werkzeug_ausdruck/?werkzeug_ausdruck-ausdruck=A%2B%2B(", ["⚠"]),                  # Unsinn -> Meldung
        ("/schaltung/werkzeug_zahlensystem/?werkzeug_zahlensystem-zahl=0xFF&werkzeug_zahlensystem-basis=Hexadezimal", ["255"]),
        ("/schaltung/werkzeug_zahlensystem/?werkzeug_zahlensystem-zahl=0xFF", ["⚠"]),       # 0x passt nicht zu Dezimal
        ("/schaltung/werkzeug_zahlensystem/?werkzeug_zahlensystem-zahl=999", ["⚠"]),                  # passt nicht in 8 Bit
        ("/schaltung/werkzeug_kv/?werkzeug_kv-einsen=1,3,5,7&werkzeug_kv-v=3+Variablen&werkzeug_kv-alt=3+Variablen", ["Y = C"]),
        ("/schaltung/werkzeug_logikpegel/?werkzeug_logikpegel-sender=GIBTSNICHT", ["ESP32"]),       # fremder Wert -> Start
        ("/schaltung/werkzeug_uart/?werkzeug_uart-daten=" + "x" * 500, ["⚠"]),                        # gekürzt, Meldung
):
    abrufen(adresse, muss_enthalten=muss)
for adresse in ("/schaltung/werkzeug_ausdruck/?werkzeug_ausdruck-ausdruck=<script>alert(1)</script>",
                "/schaltung/werkzeug_uart/?werkzeug_uart-daten=<b>x</b>",
                "/schaltung/werkzeug_logikpegel/?werkzeug_logikpegel-empf=<script>x</script>"):
    text = abrufen(adresse) or ""
    if "<script>alert" in text or "<b>x</b>" in text or "<script>x" in text:
        fehler.append(f"{adresse}: Eingabe erscheint als HTML (nicht escaped)!")
text = abrufen("/schaltung/werkzeug_uart/?werkzeug_uart-daten=A%00%1B[31m") or ""
if "\x00" in text or "\x1b" in text:   # Steuerzeichen im HTML?
    fehler.append("Textfeld: Steuerzeichen nicht entfernt")
lang = abrufen("/schaltung/werkzeug_ausdruck/?werkzeug_ausdruck-ausdruck=" + "A+" * 400 + "B") or ""
if ("A+" * 70) in lang:
    fehler.append("Textfeld: zu lange Eingabe nicht gekürzt")

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
for adresse in ("/gibtsnicht/", "/bauteile/gibtsnicht/", "/rechner/gibtsnicht/", "/schaltung/gibtsnicht/"):
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

# ---- 7) Konten, Login-Sperre, Abo-Zugang (web/konto/) ---------------------------
# Alles in der Test-Datenbank (oben SYSTEMLAB_DB) - die echte Datenbank bleibt unberührt.
# Passwörter: zufällig erzeugt, nur für diesen Test.
import secrets                                                         # noqa: E402

from django.conf import settings                                       # noqa: E402

from django.contrib.auth.models import Group, User                    # noqa: E402

from konto.models import Fehlversuch                                   # noqa: E402
from bauteile import einheiten                                         # noqa: E402
from uebungen import aufgaben, schemas                                 # noqa: E402


def konto_pruefen(bedingung, text):
    global ok
    if bedingung:
        ok += 1
    else:
        fehler.append("Konto: " + text)


def neuer_browser():
    """Browser mit CSRF-Prüfung wie in echt + gültiges CSRF-Token"""
    b = Client(enforce_csrf_checks=True)
    b.get("/konto/anmelden/")
    return b, b.cookies["csrftoken"].value


def html(antwort):
    return antwort.content.decode("utf-8", "replace")


PW = secrets.token_urlsafe(16)
LOESUNG = aufgaben.aufgabe("ohm_strom", 5)

# -- ohne Konto: alles Abo-Pflichtige gesperrt, keine Lösung im HTML --
gast = Client()
for adresse in ("/uebungen/", "/uebungen/ohm_strom/?nr=5&loesung=1", "/uebungen/blatt/?art=ohm_strom&nr=5&loesungen=1"):
    t = html(gast.get(adresse))
    konto_pruefen("gesperrt-vorschau" in t and "Abo wählen" in t, f"{adresse}: kein Schloss für Gäste")
    konto_pruefen(LOESUNG["loesung_text"] not in t and "Lösungsweg</h2>" not in t, f"{adresse}: Lösung für Gäste sichtbar!")
t = html(gast.get("/bauteile/widerstand/"))
konto_pruefen("Übungen zu diesem Thema" in t and "gesperrt-schild" in t, "Wissensseite: Übungen nicht gesperrt angezeigt")
konto_pruefen("bald verfügbar" in html(gast.get("/abo/")), "Abo-Seite fehlt")
konto_pruefen(gast.get("/uebungen/gibtsnicht/").status_code == 404, "unbekannte Aufgabenart kein 404")
konto_pruefen(gast.get("/konto/").status_code == 302, "Konto-Seite ohne Login erreichbar")
konto_pruefen(gast.get("/admin/").status_code == 404, "Verwaltung unter /admin/ erreichbar (soll woanders sein)")
v = gast.get("/" + settings.ADMIN_PFAD, follow=True)                  # Verwaltung -> deren Login -> unser Login
konto_pruefen(v.redirect_chain and v.redirect_chain[-1][0].startswith("/konto/anmelden/"),
              "Verwaltung ohne Login nicht auf die gemeinsame Anmeldung (mit Sperre) umgeleitet")

# -- Registrieren --
b, token = neuer_browser()
seite = b.get("/konto/registrieren/")
konto_pruefen(b"csrfmiddlewaretoken" in seite.content and b'name="webseite"' in seite.content, "Registrieren ohne CSRF/Bot-Falle")
reg = {"csrfmiddlewaretoken": token, "username": "testperson", "password1": PW, "password2": PW}
konto_pruefen(b.post("/konto/registrieren/", {**reg, "password1": "1234567890", "password2": "1234567890"}).status_code == 400,
              "schwaches Passwort (nur Ziffern, häufig) angenommen")
konto_pruefen(b.post("/konto/registrieren/", {**reg, "password1": "kurz", "password2": "kurz"}).status_code == 400,
              "zu kurzes Passwort angenommen")
konto_pruefen(b.post("/konto/registrieren/", {**reg, "username": "<script>x</script>"}).status_code == 400,
              "Benutzername mit HTML angenommen")
konto_pruefen(b.post("/konto/registrieren/", {**reg, "username": "Admin"}).status_code == 400, "reservierter Name angenommen")
konto_pruefen(Client(enforce_csrf_checks=True).post("/konto/registrieren/", {k: w for k, w in reg.items()
                                                                             if k != "csrfmiddlewaretoken"}).status_code == 403,
              "Registrieren ohne CSRF-Token angenommen")
b.post("/konto/registrieren/", {**reg, "username": "botname", "webseite": "http://spam"})
konto_pruefen(not User.objects.filter(username="botname").exists(), "Bot (Honigtopf) konnte ein Konto erstellen")
r = b.post("/konto/registrieren/", reg)
konto_pruefen(r.status_code == 302 and User.objects.filter(username="testperson").exists(), "Registrieren klappt nicht")
user = User.objects.get(username="testperson")
konto_pruefen(PW not in user.password and user.password.startswith("pbkdf2_"), "Passwort nicht gehasht gespeichert!")
konto_pruefen("testperson" in html(b.get("/konto/")), "Konto-Seite zeigt den Namen nicht")
konto_pruefen("gesperrt-vorschau" in html(b.get("/uebungen/")), "Konto ohne Abo sieht die Übungen")
b2, token2 = neuer_browser()
konto_pruefen(b2.post("/konto/registrieren/", {**reg, "csrfmiddlewaretoken": token2, "username": "TestPerson"}).status_code == 400,
              "gleicher Name mit anderer Gross-/Kleinschreibung angenommen")

# -- Abmelden nur per POST --
konto_pruefen(b.get("/konto/abmelden/").status_code == 405, "Abmelden per GET möglich (fremde Seite könnte abmelden)")
konto_pruefen(b.post("/konto/abmelden/", {"csrfmiddlewaretoken": b.cookies["csrftoken"].value}).status_code == 302
              and b.get("/konto/").status_code == 302, "Abmelden klappt nicht")

# -- Anmelden: falsches Ziel, Sperre, Cookie --
Fehlversuch.objects.all().delete()
b, token = neuer_browser()
login = {"csrfmiddlewaretoken": token, "username": "testperson", "password": PW}
konto_pruefen(Client(enforce_csrf_checks=True).post("/konto/anmelden/", {"username": "testperson", "password": PW}).status_code == 403,
              "Login ohne CSRF-Token angenommen")
falsch = b.post("/konto/anmelden/", {**login, "password": "falsch-falsch"})
konto_pruefen(falsch.status_code == 400 and "Benutzername oder Passwort falsch" in html(falsch), "falsches Passwort: falsche Meldung")
unbekannt = b.post("/konto/anmelden/", {**login, "username": "gibtesnicht"})
konto_pruefen(html(unbekannt).count("Benutzername oder Passwort falsch") == 1,
              "unbekannter Name: andere Meldung (verrät, welche Namen es gibt)")
konto_pruefen(not Fehlversuch.objects.filter(schluessel__icontains="testperson").exists(), "Benutzername im Klartext gespeichert")
for ziel, erwartet in (("https://boese.example/", "/konto/"), ("//boese.example/x", "/konto/"),
                       ("/uebungen/", "/uebungen/"), ("javascript:alert(1)", "/konto/")):
    Fehlversuch.objects.all().delete()
    b, token = neuer_browser()
    r = b.post("/konto/anmelden/", {"csrfmiddlewaretoken": token, "username": "testperson", "password": PW, "weiter": ziel})
    konto_pruefen(r.status_code == 302 and r["Location"] == erwartet, f"Weiterleitung nach Login zu {ziel!r}: {r.get('Location')}")
konto_pruefen(r.cookies["sessionid"]["httponly"] and r.cookies["sessionid"]["samesite"] == "Lax", "Sitzungs-Cookie nicht HttpOnly/SameSite")
alte_sitzung = b.session.session_key
Fehlversuch.objects.all().delete()
b, token = neuer_browser()
for _ in range(settings.SPERRE_PRO_NAME):
    b.post("/konto/anmelden/", {"csrfmiddlewaretoken": token, "username": "testperson", "password": "falsch-falsch"})
gesperrt = b.post("/konto/anmelden/", {"csrfmiddlewaretoken": token, "username": "testperson", "password": PW})
konto_pruefen(gesperrt.status_code == 400 and "Zu viele" in html(gesperrt), "keine Sperre nach vielen Fehlversuchen (Brute Force)")
Fehlversuch.objects.all().delete()
b3, token3 = neuer_browser()
for i in range(settings.SPERRE_PRO_ADRESSE):                  # viele verschiedene Namen vom selben Absender
    b3.post("/konto/anmelden/", {"csrfmiddlewaretoken": token3, "username": f"name{i}", "password": "x"})
gesperrt = b3.post("/konto/anmelden/", {"csrfmiddlewaretoken": token3, "username": "testperson", "password": PW})
konto_pruefen("Zu viele" in html(gesperrt), "keine Sperre pro Absender (viele Namen durchprobiert)")
Fehlversuch.objects.all().delete()
r = b.post("/konto/anmelden/", {"csrfmiddlewaretoken": token, "username": "testperson", "password": PW})
konto_pruefen(r.status_code == 302 and b.session.session_key != alte_sitzung, "Login klappt nicht / keine neue Sitzungs-ID")

# -- Abo-Gruppe: jetzt frei --
user.groups.add(Group.objects.get(name="Abo"))
richtig = LOESUNG["loesung"] / dict(einheiten.EINHEITEN["strom"]["stufen"])[LOESUNG["einheit"]]
t = html(b.get(f"/uebungen/ohm_strom/?nr=5&antwort={richtig:.4g}&einheit={LOESUNG['einheit']}"))
konto_pruefen("✓ Richtig" in t and "Lösungsweg" in t and LOESUNG["loesung_text"] in t, "Abo: richtige Antwort nicht erkannt")
t = html(b.get("/uebungen/ohm_strom/?nr=5&antwort=1&einheit=A"))
konto_pruefen("✗ Leider falsch" in t and "Lösungsweg</h2>" not in t, "Abo: falsche Antwort als richtig / Lösung verraten")
t = html(b.get("/uebungen/ohm_strom/?nr=5&antwort=<script>x</script>"))
konto_pruefen("<script>x" not in t, "Antwort erscheint als HTML (nicht escaped)!")
konto_pruefen(b.get("/uebungen/ohm_strom/").status_code == 302, "Aufgabe ohne Nummer: keine neue Nummer")
konto_pruefen(b.get("/uebungen/ohm_strom/?nr=abc").status_code == 302, "Aufgabe mit Unsinn-Nummer: Absturz?")
for art in aufgaben.ARTEN:
    r = b.get(f"/uebungen/{art}/?nr=7&loesung=1")
    konto_pruefen(r.status_code == 200 and ('class="schema"' in html(r)) == (art in schemas.SCHEMAS),
                  f"Aufgabe {art} lädt nicht / Schema fehlt")
    if aufgaben.aufgabe(art, 7)["antwort"] == "auswahl":
        konto_pruefen(html(r).count('type="radio"') >= 2, f"Aufgabe {art}: Auswahl ohne Optionen")
r = b.get("/uebungen/blatt/?art=ohm_strom&art=rc_tau&anzahl_1=2&anzahl_2=2&erstellen=1&loesungen=1")
konto_pruefen(r.status_code == 302 and "nr=" in r["Location"], "Übungsblatt: keine feste Nummer")
t = html(b.get(r["Location"]))
konto_pruefen(t.count('class="antwort-linie"') == 4 and "Lösungen</h2>" in t, "Übungsblatt falsch")
konto_pruefen(b.get("/uebungen/blatt/?erstellen=1").status_code == 400, "Übungsblatt ohne Auswahl angenommen")
konto_pruefen(b.get("/uebungen/blatt/?art=ohm_strom&erstellen=1").status_code == 400, "Übungsblatt ohne Anzahl angenommen")
t = html(b.get("/uebungen/blatt/?art=ohm_strom&anzahl_1=1&anzahl_4=3&nr=9"))
konto_pruefen(t.count('class="antwort-linie"') == 1 and "keine dieser Stufe" in t, "Übungsblatt: Hinweis bei fehlender Stufe fehlt")
for adresse in ("/uebungen/?stufe=2", "/uebungen/?bereich=Schaltungen", "/uebungen/?stufe=99&bereich=<b>x</b>"):
    r = b.get(adresse)
    konto_pruefen(r.status_code == 200 and "<b>x</b>" not in html(r), f"{adresse}: Filter falsch")
konto_pruefen("rc_laden" not in html(b.get("/uebungen/?stufe=1")), "Filter Stufe 1 zeigt Stufe 3")
konto_pruefen(html(b.get("/uebungen/blatt/?art=ohm_strom&anzahl_1=999&nr=3")).count('class="antwort-linie"') == aufgaben.MAX_ANZAHL,
              "Übungsblatt: Anzahl nicht begrenzt")
konto_pruefen("gesperrt-schild" not in html(b.get("/bauteile/widerstand/")), "Abo: Wissensseite zeigt noch das Schloss")
konto_pruefen(b.get("/" + settings.ADMIN_PFAD).status_code == 302, "Verwaltung für normale Konten offen!")

# -- Passwort ändern, Konto löschen --
neu = secrets.token_urlsafe(16)
token = b.cookies["csrftoken"].value
konto_pruefen(b.post("/konto/passwort/", {"csrfmiddlewaretoken": token, "old_password": "falsch", "new_password1": neu,
                                          "new_password2": neu}).status_code == 400, "Passwort ändern ohne altes Passwort")
r = b.post("/konto/passwort/", {"csrfmiddlewaretoken": token, "old_password": PW, "new_password1": neu, "new_password2": neu})
konto_pruefen(r.status_code == 302 and b.get("/konto/").status_code == 200, "Passwort ändern klappt nicht / abgemeldet")
token = b.cookies["csrftoken"].value
konto_pruefen(b.post("/konto/loeschen/", {"csrfmiddlewaretoken": token, "password": PW}).status_code == 400,
              "Konto löschen mit altem Passwort möglich")
r = b.post("/konto/loeschen/", {"csrfmiddlewaretoken": token, "password": neu})
konto_pruefen(r.status_code == 200 and not User.objects.filter(username="testperson").exists(), "Konto löschen klappt nicht")
konto_pruefen(b.get("/konto/").status_code == 302, "nach dem Löschen noch angemeldet")

# -- bestehendes Konto zum Admin machen (py manage.py admin_machen <name>) --
from konto.zugang import hat_abo                                       # noqa: E402

User.objects.create_user("spaeteradmin", password=secrets.token_urlsafe(16))
call_command("admin_machen", "spaeteradmin", stdout=open(os.devnull, "w"))
konto_pruefen(hat_abo(User.objects.get(username="spaeteradmin")), "admin_machen: Konto hat danach nicht alles frei")
call_command("admin_machen", "spaeteradmin", "--zurueck", stdout=open(os.devnull, "w"))
konto_pruefen(not hat_abo(User.objects.get(username="spaeteradmin")), "admin_machen --zurueck wirkt nicht")

# -- Admin: alles frei, Verwaltung erreichbar --
admin_pw = secrets.token_urlsafe(16)
User.objects.create_superuser("testadmin", password=admin_pw)
Fehlversuch.objects.all().delete()
b, token = neuer_browser()
r = b.post("/konto/anmelden/", {"csrfmiddlewaretoken": token, "username": "testadmin", "password": admin_pw,
                                "weiter": "/" + settings.ADMIN_PFAD})
konto_pruefen(r.status_code == 302 and b.get("/" + settings.ADMIN_PFAD).status_code == 200, "Admin kommt nicht in die Verwaltung")
konto_pruefen("gesperrt-vorschau" not in html(b.get("/uebungen/")) and "👑 Admin" in html(b.get("/konto/")),
              "Admin hat nicht alles frei")
konto_pruefen(b.post("/konto/loeschen/", {"csrfmiddlewaretoken": b.cookies["csrftoken"].value, "password": admin_pw}).status_code == 400
              and User.objects.filter(username="testadmin").exists(), "Admin-Konto über die Webseite löschbar")
Fehlversuch.objects.all().delete()

print(f"{seiten} Wissensseiten, {len(schaltungen)} Schaltungen, {len(web_ids)} Rechner "
      f"({faelle} Fälle aus rechner_faelle.py) geprüft in {time.time() - t0:.1f} s")
print(f"{ok} Aufrufe ok, {len(fehler)} Fehler")
for f in fehler:
    print("  FEHLER", f)
from django.db import connections                                    # noqa: E402

connections.close_all()                       # Windows: Datei schliessen, sonst kann der Test-Ordner nicht weg
sys.exit(1 if fehler else 0)
