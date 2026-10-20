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

## Konten und Abo (lokal)

Die Datenbank (SQLite, in Python eingebaut) liegt in `web/daten/systemlab.sqlite3` – nie im Repo.
Einmalig die Tabellen anlegen und dein **Admin-Konto** erstellen (im Ordner `web/`):

```bash
py manage.py migrate
py manage.py createsuperuser
```

Benutzername und ein starkes Passwort (mind. 10 Zeichen) wählen – E-Mail kannst du leer lassen.
Schon ein Konto über „Konto erstellen“ angelegt? Dann dieses zum Admin machen:
`py manage.py admin_machen <Benutzername>` (zurück: `--zurueck`).

- **Admin** (Superuser): alles frei, auch die Übungen. Verwaltung unter <http://127.0.0.1:8000/verwaltung/>.
- **Abo von Hand vergeben:** Verwaltung → Benutzer → Person öffnen → Gruppen → „Abo“ → Speichern.
  (Ab Phase 4 erledigt das die Zahlung.)
- **Ohne Abo** sehen alle die Übungen nur verschwommen mit Schloss und dem Knopf „Abo wählen“ (→ `/abo/`).
- Registrieren abschalten: `$env:SYSTEMLAB_REGISTRIERUNG = "0"` vor dem Start.

Sicherheit: Passwörter nur als Hash, Login-Sperre nach 5 Fehlversuchen (15 min), alle Formulare mit
CSRF-Schutz, Abmelden nur per Knopf, Weiterleitung nach dem Login nur auf diese Seite. Gesperrte Inhalte
schickt der Server ohne Abo gar nicht erst – die Unschärfe ist nur ein Beispielbild.

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

## Rückmeldungen der Testpersonen lesen

Auf jeder Seite gibt es unten „Fehler melden · Idee teilen“ (bei Rechnern mit den eingegebenen Werten).
Die Meldungen landen in `web/daten/rueckmeldungen.jsonl` – nur auf deinem PC, nie im Repo. Anzeigen:

```bash
python manage.py rueckmeldungen
```

## Prüfen nach Änderungen

```bash
python pruefen_web.py
```

Ruft jede Seite einmal auf – ohne Browser: alle Wissensseiten, jede Schaltung mit jeder Variante, alle Rechner
mit den 298 von Hand gerechneten Fällen aus `pruefung/rechner_faelle.py`, falsche Eingaben, Sicherheit
(Escaping, CSRF, Bot-Falle, Sperre bei vielen Meldungen) und Konten (Schloss ohne Abo, Passwortregeln,
Login-Sperre, Weiterleitung, Abmelden, Löschen). Läuft mit einer eigenen Test-Datenbank – deine echte bleibt
unberührt. Ergebnis `0 Fehler` = alles gut.

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
  konto/                  Anmelden, Registrieren, Konto, Login-Sperre (sperre.py), Abo-Zugang (zugang.py), /abo/
  ueben/                  Übungen und Übungsblatt (Rechnung: ../uebungen/aufgaben.py)
  templates/basis.html    Grundgerüst jeder Seite
  static/                 systemlab.css, systemlab.js (Farben kommen aus config.py)
```

**Neuer Rechner?** Formel-Rechner (`FormelDaten`) erscheinen im Web automatisch (`WEB_ALLE_FORMEL_RECHNER`).
Rechner mit eigener Webseite stehen in `WEB_RECHNER_EXTRA` (Beispiel: Farbcode), die Startseite zeigt
`WEB_RECHNER_EMPFOHLEN`.

## Wie es weitergeht

| Stufe | Inhalt | Status |
|---|---|---|
| 1 | Lokal: Wiki, Suche, alle 121 Rechner, interaktive Schaltpläne, hell/dunkel, Handy, „Fehler melden“ | ✅ (Testphase) |
| 2 | Online: Hosting + Domain, Sicherheits-Checkliste, Impressum/Datenschutz | offen |
| 3 | Konten + Übungen: Login, Admin, Abo-Gruppe, Übungsgenerator (12 Aufgabenarten), Übungsblatt, Schloss-Vorschau | 🟡 lokal fertig, vor online: E-Mail/Passwort vergessen, 2FA Admin, Backup |
| 4 | Bezahlung über einen Merchant of Record, AGB, Prüfungsmodus, Lernkarten, Fortschritt | offen |

Einstellungen für online (nie im Code, nur als Umgebungsvariable): `SYSTEMLAB_DEBUG=0`,
`SYSTEMLAB_SECRET_KEY=<langer zufälliger Text>`, `SYSTEMLAB_HOSTS=meine-domain.ch`.
