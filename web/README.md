# SystemLab – Webversion

Dieselben Inhalte und Rechner wie die Desktop-App, im Browser. Nichts ist kopiert: Die Webversion liest
`bauteile/`, `schaltungen/`, `programmieren/` usw. direkt. Eine neue Wissensseite erscheint also automatisch
in beiden Versionen.

## Starten (lokal)

Einmalig Django installieren:

```bash
python -m pip install -r web/requirements.txt
```

Server starten (im Ordner `web/`):

```bash
python manage.py runserver
```

Dann im Browser öffnen: <http://127.0.0.1:8000>. Beenden mit `Ctrl+C`.

## Für Kollegen im selben Netz (Schule, WLAN zu Hause)

1. Eigene IP-Adresse herausfinden: `ipconfig` → „IPv4-Adresse“, z.B. `192.168.1.20`.
2. Server für das Netz öffnen. In PowerShell zuerst die erlaubten Adressen setzen:

   ```powershell
   $env:SYSTEMLAB_HOSTS = "192.168.1.20,localhost"
   python manage.py runserver 0.0.0.0:8000
   ```

3. Kollegen öffnen `http://192.168.1.20:8000`.

Windows fragt beim ersten Mal nach der Firewall: nur **private Netzwerke** erlauben.
`runserver` ist ein Entwicklungsserver – für das eigene Netz in Ordnung, aber **nicht** fürs Internet
(dafür Stufe 2, siehe unten).

## Prüfen nach Änderungen

```bash
python pruefen_web.py
```

Ruft jede Seite einmal auf (alle Wissensseiten, jede Schaltung mit jeder Variante, alle Rechner, falsche
Eingaben, Sicherheit) – ohne Browser. Ergebnis `0 Fehler` = alles gut.

## Aufbau

```text
web/
  manage.py               Startpunkt
  pruefen_web.py          Prüfskript (siehe oben)
  requirements.txt        Pakete nur für die Webversion (Django)
  systemlab_web/          Einstellungen (settings.py) und Adressen (urls.py)
  wiki/                   Startseite, Bereiche, Wissensseiten, Suche, Schaltpläne
    inhalt.py             Daten aus core/inhalte_index.py (wie die Desktop-Suche)
    textformat.py         ## Überschrift / - Punkt / **fett** / `code` -> HTML (sicher escaped)
    grafiken.py           Schaltzeichen und interaktive Schaltpläne als SVG
                          (bauteile/grafiken/svg_canvas.py - derselbe Zeichencode wie im Fenster)
  rechner/                Rechner: Formular aus FormelDaten (bauteile/rechner/kern.py) + Farbcode
  templates/basis.html    Grundgerüst jeder Seite
  static/                 systemlab.css, systemlab.js (Farben kommen aus config.py)
```

**Neuer Rechner im Web?** In `systemlab_web/settings.py` die ID in `WEB_RECHNER` eintragen. Formel-Rechner
funktionieren dann sofort, für alle anderen braucht es eine eigene Seite (Beispiel: Farbcode).

## Wie es weitergeht

| Stufe | Inhalt | Status |
|---|---|---|
| 1 | Lokal: Wiki, Suche, 5 Rechner, interaktive Schaltpläne, hell/dunkel, Handy | ✅ |
| 2 | Online: Hosting + Domain, Benutzerkonten (Favoriten, Zuletzt, Notizen), Feedback-Formular, Impressum/Datenschutz | offen |
| 3 | Abo: Prüfungsmodus, Lernkarten, Fortschritt – Bezahlung über Stripe, AGB | offen |

Einstellungen für online (nie im Code, nur als Umgebungsvariable): `SYSTEMLAB_DEBUG=0`,
`SYSTEMLAB_SECRET_KEY=<langer zufälliger Text>`, `SYSTEMLAB_HOSTS=meine-domain.ch`.
