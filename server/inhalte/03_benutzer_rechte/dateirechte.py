# =============================================================================
# Thema: Dateirechte (chmod, chown)  (Kategorie: Benutzer & Rechte)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Dateirechte: chmod, chown, rwx",
    "reihenfolge": 3,
    "kurz": "Wer darf eine Datei lesen, schreiben, ausführen? Und warum chmod 777 nie die Lösung ist.",
    "stichworte": ["rechte", "berechtigung", "permissions", "chmod", "chown", "chgrp", "rwx", "755", "644", "600",
                   "700", "777", "umask", "besitzer", "owner", "gruppe", "ausführbar", "executable", "sticky bit",
                   "setuid", "permission denied", "oktal"],

    "erklaerung": """
## Drei Rechte für drei Personengruppen
`ls -l` zeigt z.B. `-rwxr-x---`. Nach dem ersten Zeichen (Typ) kommen **3 × 3 Zeichen**:
- **u** (user) = Besitzer · **g** (group) = Gruppe · **o** (others) = alle anderen
- **r** = read (lesen) · **w** = write (schreiben) · **x** = execute (ausführen) · **-** = nicht erlaubt
Beispiel `rwxr-x---`: Besitzer darf alles, Gruppe lesen + ausführen, alle anderen **nichts**.
## Bei Ordnern bedeuten die Rechte etwas anderes
- **r** = Inhalt auflisten (`ls`)
- **w** = Dateien darin anlegen, umbenennen, **löschen**
- **x** = hineinwechseln (`cd`) und auf Dateien darin zugreifen
## Zahlenschreibweise (oktal)
Jedes Recht hat einen Wert: **r = 4, w = 2, x = 1**. Pro Personengruppe addieren:
- `7` = rwx (4+2+1) · `6` = rw- · `5` = r-x · `4` = r-- · `0` = ---
- `chmod 755` → rwx r-x r-x · `chmod 640` → rw- r-- ---
## Besitzer ändern
`chown benutzer:gruppe datei` – typisch nach dem Hochladen von Webdateien: `sudo chown -R www-data:www-data /var/www/seite`.
## umask – Standardrechte für neue Dateien
Neue Dateien bekommen auf Ubuntu meist **644** (Ordner **755**). Das legt die `umask` fest (Standard 022).
""",

    "befehle": [
        {"titel": "Rechte ansehen & setzen", "zeilen": [
            ("ls -l datei", "Rechte, Besitzer, Gruppe anzeigen"),
            ("stat -c '%a %U:%G %n' datei", "Rechte als Zahl (z.B. 644) anzeigen"),
            ("chmod 644 datei.txt", "rw-r--r--  normale Datei"),
            ("chmod 755 skript.sh", "rwxr-xr-x  Skript / Programm / Ordner"),
            ("chmod 600 geheim.env", "rw-------  nur Besitzer (Passwörter, Schlüssel)"),
            ("chmod 700 ~/.ssh", "rwx------  privater Ordner"),
            ("chmod +x skript.sh", "Ausführbar machen"),
            ("chmod g+w datei", "Gruppe darf zusätzlich schreiben"),
            ("chmod o-rwx datei", "Allen anderen alle Rechte entziehen"),
        ]},
        {"titel": "Besitzer", "zeilen": [
            ("sudo chown anna datei", "Besitzer ändern"),
            ("sudo chown anna:entwickler datei", "Besitzer und Gruppe ändern"),
            ("sudo chown -R www-data:www-data /var/www/seite", "Rekursiv für einen ganzen Ordner"),
            ("sudo chgrp entwickler projekt/", "Nur die Gruppe ändern"),
        ]},
        {"titel": "Nur Dateien ODER nur Ordner (richtig rekursiv)", "zeilen": [
            ("find /var/www/seite -type d -exec chmod 755 {} +", "Alle Ordner auf 755"),
            ("find /var/www/seite -type f -exec chmod 644 {} +", "Alle Dateien auf 644"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 Die Rechte, die man wirklich braucht",
            "kopf": ["Zahl", "Symbolisch", "Für"],
            "zeilen": [
                ["644", "rw-r--r--", "normale Dateien, Webseiten-Dateien, die meisten Konfigurationen"],
                ["755", "rwxr-xr-x", "Ordner, Skripte, Programme"],
                ["600", "rw-------", "private Schlüssel, .env mit Passwörtern, authorized_keys"],
                ["700", "rwx------", "~/.ssh, private Ordner"],
                ["640", "rw-r-----", "Konfiguration mit Passwörtern, die ein Dienst (Gruppe) lesen muss"],
                ["750", "rwxr-x---", "Ordner nur für Besitzer und Gruppe"],
                ["777", "rwxrwxrwx", "❌ NIE – jeder darf alles ändern"],
            ],
        },
        {
            "titel": "📊 Spezialrechte (zum Erkennen)",
            "kopf": ["Recht", "Anzeige", "Bedeutung"],
            "zeilen": [
                ["Sticky Bit", "drwxrwxrwt (/tmp)", "jeder darf anlegen, aber nur eigene Dateien löschen"],
                ["SetUID", "-rwsr-xr-x (/usr/bin/passwd)", "Programm läuft mit den Rechten des Besitzers (root!)"],
                ["SetGID bei Ordnern", "drwxrwsr-x", "neue Dateien erben die Gruppe des Ordners (gut für Team-Ordner)"],
            ],
        },
    ],

    "beispiele": [
        {"titel": "Team-Ordner für eine Gruppe",
         "code": {"Bash": r'''sudo addgroup team
sudo usermod -aG team anna
sudo mkdir /srv/team
sudo chown root:team /srv/team
sudo chmod 2770 /srv/team        # 2 = SetGID: neue Dateien gehören automatisch der Gruppe team
ls -ld /srv/team'''},
         "ausgabe": "drwxrws--- 2 root team 4096 Sep 29 11:02 /srv/team"},
    ],

    "sicherheit": [
        "**Nie `chmod 777`** und schon gar nicht `chmod -R 777` – jeder Prozess (auch ein gehackter Webserver) darf dann Dateien verändern oder Schadcode ablegen. „Permission denied“ löst man mit dem **richtigen Besitzer**, nicht mit 777.",
        "Nie `chmod -R` oder `chown -R` auf `/`, `/etc`, `/usr` oder `/var` – das zerstört das System (sudo und SSH verweigern dann den Dienst).",
        "Private Schlüssel und Passwort-Dateien immer **600**. SSH verweigert Schlüssel mit zu offenen Rechten sogar absichtlich.",
        "Nie selbst SetUID-Bits setzen (`chmod u+s`) – klassische Hintertür.",
        "Webserver-Dateien sollten dem Webserver **nicht** schreibbar gehören, ausser Upload-Ordnern.",
    ],
    "tipps": [
        "`chmod -R 755` macht auch alle **Dateien** ausführbar – besser mit `find -type d` / `-type f` getrennt setzen.",
        "Zugriff klappt nicht, obwohl die Datei 644 ist? Dann fehlt oft das **x** auf einem der **übergeordneten Ordner**. `namei -l /pfad/zur/datei` zeigt alle Ordner auf dem Weg.",
        "Symbolisch ist oft verständlicher: `chmod u+x`, `chmod go-w`.",
    ],
    "fehler": [
        "Skript mit `./skript.sh` gestartet → `Permission denied`: `chmod +x skript.sh` fehlt.",
        "`chown anna datei` ohne sudo → „Operation not permitted“: Besitzer ändern darf nur root.",
        "SSH-Login mit Schlüssel scheitert → Rechte von `~/.ssh` (700) oder `authorized_keys` (600) zu offen, oder das Home-Verzeichnis ist für andere schreibbar.",
    ],
    "siehe_auch": ["benutzer_gruppen", "sudo_root", "todsuenden", "ssh_verbinden"],
}
