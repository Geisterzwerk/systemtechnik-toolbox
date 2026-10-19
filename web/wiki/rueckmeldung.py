# =============================================================================
# web/wiki/rueckmeldung.py
# -----------------------------------------------------------------------------
# "FEHLER MELDEN / IDEE": Rückmeldungen der Testpersonen speichern und lesen.
#
# Stufe 1 (lokal): eine Zeile JSON pro Meldung in settings.RUECKMELDUNGEN_DATEI
# (web/daten/rueckmeldungen.jsonl, steht in .gitignore -> nie auf GitHub).
# Ab Stufe 2 (online) kommt das in die Datenbank.
#
#   ARTEN                          Auswahl im Formular
#   pruefen(daten)                 -> (meldung_dict, fehler_liste)   Eingaben prüfen und kürzen
#   speichern(meldung)             eine Meldung anhängen (threadsicher)
#   alle()                         alle Meldungen, neueste zuerst
#   zu_viele(adresse)              Schutz gegen Massen-Meldungen: höchstens MAX_PRO_STUNDE pro Absender
#
# SICHERHEIT (siehe Obsidian 03_Sicherheit):
#   - nur POST mit CSRF-Schutz (Django), Länge begrenzt, Steuerzeichen entfernt
#   - "Honigtopf": ein für Menschen unsichtbares Feld - wer es ausfüllt, ist ein Bot
#   - gespeichert wird KEINE IP-Adresse; zum Begrenzen dient nur ein Hash im Arbeitsspeicher
#   - angezeigt wird alles escaped (Django-Templates bzw. Terminal-Ausgabe)
#
# WER RUFT DAS AUF?  web/wiki/views.py (rueckmeldung), web/wiki/management/commands/rueckmeldungen.py
# =============================================================================

import hashlib
import json
import re
import threading
import time
from datetime import datetime

from django.conf import settings

ARTEN = ["Fehler im Inhalt (falsche Formel, falscher Wert)", "Rechner rechnet falsch", "Darstellung / Bedienung",
         "Idee / Wunsch", "Sonstiges"]
MAX_TEXT = 2000
MAX_KONTAKT = 200
MAX_SEITE = 300
MAX_PRO_STUNDE = 10

_sperre = threading.Lock()
_zeiten = {}                                  # Hash des Absenders -> Zeitpunkte der letzten Meldungen
_STEUERZEICHEN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _sauber(text, laenge):
    """Steuerzeichen raus, Leerraum am Rand weg, auf 'laenge' Zeichen kürzen."""
    return _STEUERZEICHEN.sub("", str(text or "")).strip()[:laenge]


def pruefen(daten):
    """daten = request.POST. Rückgabe: (meldung, fehler) - fehler ist eine Liste von Texten (leer = ok)."""
    meldung = {
        "art": daten.get("art", ""),
        "text": _sauber(daten.get("text"), MAX_TEXT + 1),
        "kontakt": _sauber(daten.get("kontakt"), MAX_KONTAKT),
        "seite": _sauber(daten.get("seite"), MAX_SEITE),
    }
    fehler = []
    if meldung["art"] not in ARTEN:
        fehler.append("Bitte eine Art auswählen.")
    if len(meldung["text"]) < 5:
        fehler.append("Bitte kurz beschreiben, was nicht stimmt (mindestens 5 Zeichen).")
    if len(meldung["text"]) > MAX_TEXT:
        fehler.append(f"Bitte höchstens {MAX_TEXT} Zeichen.")
    meldung["seite"] = eigene_seite(meldung["seite"])
    return meldung, fehler


def eigene_seite(adresse):
    """Nur Adressen DIESER Webseite ("/rechner/..."), nie "//fremde-seite.ch" oder "https://..." -> sonst ""."""
    adresse = _sauber(adresse, MAX_SEITE)
    return adresse if adresse.startswith("/") and not adresse.startswith("//") and "\\" not in adresse else ""


def ist_bot(daten):
    """Das Feld 'webseite' ist für Menschen unsichtbar (CSS). Ausgefüllt -> automatisches Programm."""
    return bool(daten.get("webseite"))


def zu_viele(adresse):
    """True, wenn von diesem Absender in der letzten Stunde schon MAX_PRO_STUNDE Meldungen kamen.
    Die Adresse wird nur als Hash und nur im Arbeitsspeicher gehalten (nicht in der Datei)."""
    schluessel = hashlib.sha256((settings.SECRET_KEY + str(adresse)).encode()).hexdigest()
    jetzt = time.time()
    with _sperre:
        liste = [t for t in _zeiten.get(schluessel, []) if jetzt - t < 3600]
        if len(liste) >= MAX_PRO_STUNDE:
            _zeiten[schluessel] = liste
            return True
        liste.append(jetzt)
        _zeiten[schluessel] = liste
    return False


def speichern(meldung):
    datei = settings.RUECKMELDUNGEN_DATEI
    eintrag = {"zeit": datetime.now().isoformat(timespec="seconds"), **meldung}
    with _sperre:
        datei.parent.mkdir(parents=True, exist_ok=True)
        with open(datei, "a", encoding="utf-8") as f:
            f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


def alle():
    """Alle gespeicherten Meldungen, neueste zuerst (kaputte Zeilen werden übersprungen)."""
    datei = settings.RUECKMELDUNGEN_DATEI
    if not datei.exists():
        return []
    meldungen = []
    with open(datei, encoding="utf-8") as f:
        for zeile in f:
            try:
                meldungen.append(json.loads(zeile))
            except ValueError:
                continue
    return meldungen[::-1]
