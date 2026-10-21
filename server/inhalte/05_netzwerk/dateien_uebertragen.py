# =============================================================================
# Thema: Dateien übertragen (scp, rsync, wget)  (Kategorie: Netzwerk)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Dateien übertragen: scp, rsync, wget",
    "reihenfolge": 3,
    "kurz": "Dateien zwischen PC und Server kopieren, Ordner synchronisieren, Downloads auf den Server holen.",
    "stichworte": ["übertragen", "kopieren", "hochladen", "upload", "download", "scp", "rsync", "sftp", "wget",
                   "curl", "winscp", "filezilla", "synchronisieren", "sync", "schrägstrich", "trailing slash",
                   "--delete", "--dry-run", "checksumme", "sha256sum"],

    "erklaerung": """
## Stell dir vor …
Zwei Arten umzuziehen: Bei **scp** packst du jedes Mal alles ein und fährst alles hinüber. Bei **rsync** schaust du zuerst, was in der neuen Wohnung schon steht, und bringst nur das, was fehlt oder sich geändert hat. Beim ersten Mal ist es gleich viel Arbeit – ab dem zweiten Mal ist rsync viel schneller.
## scp – einfaches Kopieren über SSH
`scp quelle ziel` – wie `cp`, aber eine Seite liegt auf einem anderen Rechner: `benutzer@server:/pfad`. Funktioniert auch in der Windows-PowerShell. Nutzt SSH – also auch deine SSH-Schlüssel.
## rsync – das bessere Werkzeug
`rsync` überträgt nur **Unterschiede**, kann abgebrochene Übertragungen fortsetzen und erhält Rechte und Zeitstempel. Für alles Grössere und für Backups die erste Wahl.
- `-a` Archiv-Modus (Rechte, Zeiten, Links, rekursiv) · `-v` anzeigen · `-z` komprimieren · `-P` Fortschritt + fortsetzbar
- `-n` bzw. `--dry-run` – **nur anzeigen, was passieren würde**
## Der Schrägstrich am Ende zählt!
- `rsync -a quelle/ ziel/` – kopiert den **Inhalt** von quelle nach ziel
- `rsync -a quelle ziel/` – kopiert den **Ordner** quelle nach ziel → `ziel/quelle/…`
## Grafisch (Windows)
**WinSCP** oder **FileZilla** (Protokoll SFTP, Port 22) – benutzen ebenfalls SSH.
## 🔬 Genauer hingeschaut
- **Erst üben:** `rsync -avn quelle/ ziel/` (n = dry run) zeigt nur, was passieren würde. Besonders wichtig mit `--delete`, das im Ziel alles löscht, was in der Quelle fehlt.
- **Abgebrochen? Weitermachen:** `rsync -avP` zeigt den Fortschritt und kann unterbrochene Übertragungen fortsetzen, statt von vorne zu beginnen.
## 💡 Wusstest du?
- rsync überträgt bei geänderten Dateien nicht die ganze Datei neu, sondern nur die geänderten Teile. Das Verfahren dafür wurde 1996 im Rahmen einer Doktorarbeit entwickelt.
""",

    "befehle": [
        {"titel": "scp (vom PC aus)", "zeilen": [
            ("scp datei.txt benutzer@srv01:~/", "Datei vom PC in dein Home auf dem Server"),
            ("scp benutzer@srv01:/var/log/syslog .", "Datei vom Server in den aktuellen Ordner holen"),
            ("scp -r ordner/ benutzer@srv01:~/", "Ganzen Ordner hochladen"),
            ("scp -P 2222 datei.txt benutzer@srv01:~/", "Anderer SSH-Port (grosses -P!)"),
        ]},
        {"titel": "rsync", "zeilen": [
            ("rsync -avP quelle/ benutzer@srv01:/srv/ziel/", "Ordnerinhalt hochladen, mit Fortschritt"),
            ("rsync -avP benutzer@srv01:/srv/daten/ ./daten/", "Vom Server herunterladen"),
            ("rsync -avn --delete quelle/ ziel/", "TROCKENLAUF: zeigt, was kopiert und gelöscht würde"),
            ("rsync -av --delete quelle/ ziel/", "Spiegeln: im Ziel löschen, was in der Quelle fehlt"),
            ("rsync -av --exclude='*.log' quelle/ ziel/", "Bestimmte Dateien auslassen"),
            ("rsync -avP -e \"ssh -p 2222\" quelle/ benutzer@srv01:ziel/", "Über anderen SSH-Port"),
        ]},
        {"titel": "Aus dem Internet laden", "zeilen": [
            ("wget https://example.com/datei.tar.gz", "Datei herunterladen"),
            ("curl -LO https://example.com/datei.tar.gz", "Dasselbe mit curl (L = Umleitungen folgen)"),
            ("sha256sum datei.tar.gz", "Prüfsumme berechnen – mit der Angabe des Herstellers vergleichen"),
        ]},
    ],

    "beispiele": [
        {"titel": "Erst schauen, dann spiegeln",
         "code": {"Bash": r'''rsync -avn --delete /srv/daten/ /mnt/backup/daten/   # was würde passieren?
rsync -av  --delete /srv/daten/ /mnt/backup/daten/   # erst dann wirklich'''},
         "ausgabe": "sending incremental file list\ndeleting alt/bericht.pdf\nneu/foto.jpg\n\nsent 1.2M  received 64 bytes  (DRY RUN)"},
        {"titel": "Download prüfen",
         "code": {"Bash": r'''wget https://example.com/tool-1.2.tar.gz
sha256sum tool-1.2.tar.gz      # muss exakt der Angabe auf der Hersteller-Seite entsprechen'''}},
    ],

    "sicherheit": [
        "**`rsync --delete` mit vertauschter Quelle/Ziel löscht deine Originale.** Immer zuerst mit `-n` (dry-run) laufen lassen und die Liste lesen.",
        "Nie FTP (unverschlüsselt, Port 21) verwenden – Passwörter gehen im Klartext übers Netz. Immer SFTP/scp/rsync über SSH.",
        "Downloads aus dem Internet mit `sha256sum` gegen die Herstellerangabe prüfen, bevor man sie installiert oder ausführt.",
        "Beim Hochladen keine Dateien mit Geheimnissen (`.env`, Schlüssel) in öffentliche Webordner (`/var/www`) legen.",
    ],
    "tipps": [
        "Bricht eine grosse Übertragung ab: denselben `rsync -avP`-Befehl einfach nochmal – er macht dort weiter.",
        "Viele kleine Dateien? Erst mit `tar` packen, dann übertragen – geht deutlich schneller.",
        "`rsync` muss auf **beiden** Seiten installiert sein (auf Ubuntu Standard; unter Windows WSL oder WinSCP verwenden).",
    ],
    "fehler": [
        "`scp -p 2222` → kleines -p heisst bei scp „Zeitstempel erhalten“. Port ist bei scp **-P**, bei ssh **-p**.",
        "Schrägstrich vergessen → rsync legt einen zusätzlichen Unterordner an (`ziel/quelle/…`).",
        "`Permission denied` beim Hochladen nach `/var/www` → in dein Home kopieren, dann mit `sudo mv` verschieben und Besitzer setzen.",
    ],
    "siehe_auch": ["ssh_verbinden", "backups", "archive", "dateien_verwalten"],
}
