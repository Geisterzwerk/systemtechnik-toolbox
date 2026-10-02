# =============================================================================
# Thema: Dateien verwalten (mkdir, cp, mv, rm, ln)  (Kategorie: Dateien & Navigation)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Dateien anlegen, kopieren, verschieben, löschen",
    "reihenfolge": 2,
    "kurz": "mkdir, touch, cp, mv, rm, ln – und warum rm keinen Papierkorb kennt.",
    "stichworte": ["datei", "ordner", "anlegen", "erstellen", "kopieren", "verschieben", "umbenennen", "löschen",
                   "mkdir", "touch", "cp", "mv", "rm", "rmdir", "ln", "link", "symlink", "verknüpfung",
                   "wildcard", "platzhalter", "stern", "papierkorb", "backup kopie"],

    "erklaerung": """
## Anlegen
- `mkdir ordner` legt einen Ordner an, `mkdir -p a/b/c` auch alle Zwischenordner.
- `touch datei` legt eine leere Datei an (oder aktualisiert den Zeitstempel einer bestehenden).
## Kopieren und Verschieben
- `cp quelle ziel` kopiert eine Datei, `cp -r` ganze Ordner. **Ist das Ziel schon da, wird es ohne Rückfrage überschrieben!** Mit `-i` fragt cp nach.
- `mv alt neu` verschiebt **oder** benennt um – unter Linux ist das dasselbe.
## Löschen – ohne Papierkorb
`rm` löscht **endgültig**. Es gibt keinen Papierkorb und kein „Rückgängig“. Deshalb:
- Erst mit `ls` prüfen, was das Muster trifft, **dann** `rm`
- Bei wichtigen Dingen `rm -i` (fragt bei jeder Datei)
- Vorher sichern: `cp datei datei.bak`
## Platzhalter (Wildcards)
- `*` = beliebig viele Zeichen: `*.log` = alle Dateien, die auf .log enden
- `?` = genau ein Zeichen: `datei?.txt` → datei1.txt, dateiA.txt
- Die **Shell** ersetzt die Platzhalter, bevor der Befehl startet – `echo *.log` zeigt vorher, was betroffen ist.
## Links
Ein **symbolischer Link** (`ln -s`) ist eine Verknüpfung auf eine andere Datei oder einen Ordner. Typisch bei nginx: `/etc/nginx/sites-enabled/` enthält nur Links auf `/etc/nginx/sites-available/`.
""",

    "befehle": [
        {"titel": "Anlegen", "zeilen": [
            ("mkdir backup", "Ordner anlegen"),
            ("mkdir -p projekte/2026/test", "Mit allen Zwischenordnern"),
            ("touch notizen.txt", "Leere Datei anlegen"),
        ]},
        {"titel": "Kopieren & Verschieben", "zeilen": [
            ("cp datei.txt datei.bak", "Sicherungskopie"),
            ("cp -r ordner/ /mnt/backup/", "Ganzen Ordner kopieren"),
            ("cp -a quelle/ ziel/", "Kopieren mit Rechten, Besitzer und Zeitstempel (für Backups)"),
            ("cp -i datei.txt ziel/", "Nachfragen, bevor etwas überschrieben wird"),
            ("mv alt.txt neu.txt", "Umbenennen"),
            ("mv *.log archiv/", "Alle .log-Dateien in den Ordner archiv verschieben"),
        ]},
        {"titel": "Löschen", "zeilen": [
            ("rm datei.txt", "Datei löschen (endgültig!)"),
            ("rm -i *.tmp", "Mit Nachfrage bei jeder Datei"),
            ("rmdir leerer_ordner", "Nur LEERE Ordner löschen (sicher)"),
            ("rm -r ordner/", "Ordner mit Inhalt löschen – vorher ls ordner/"),
            ("rm -rf ordner/", "Ohne jede Rückfrage, auch schreibgeschützte Dateien – nur wenn 100 % sicher"),
        ]},
        {"titel": "Links", "zeilen": [
            ("ln -s /var/www/html web", "Verknüpfung „web“ auf /var/www/html anlegen"),
            ("ls -l web", "Zeigt, wohin der Link zeigt (web -> /var/www/html)"),
        ]},
    ],

    "beispiele": [
        {"titel": "Sicher löschen: erst anzeigen, dann löschen",
         "code": {"Bash": r'''ls /var/log/meineapp/*.gz        # was würde getroffen?
rm /var/log/meineapp/*.gz         # erst jetzt löschen'''}},
        {"titel": "Konfiguration sicher bearbeiten",
         "text": "Vor jeder Änderung in /etc eine Kopie mit Datum – so kommt man jederzeit zurück.",
         "code": {"Bash": r'''sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.$(date +%F).bak
ls /etc/ssh/'''},
         "ausgabe": "moduli  ssh_config  sshd_config  sshd_config.2026-09-29.bak  ..."},
    ],

    "tabellen": [
        {
            "titel": "📊 Wichtige Optionen",
            "kopf": ["Option", "bei", "Bedeutung"],
            "zeilen": [
                ["-r", "cp, rm", "rekursiv – ganze Ordner mit Inhalt"],
                ["-i", "cp, mv, rm", "interaktiv – vor dem Überschreiben/Löschen nachfragen"],
                ["-f", "rm, cp", "force – nie fragen, Fehler ignorieren (gefährlich)"],
                ["-v", "cp, mv, rm", "verbose – jede Datei anzeigen"],
                ["-a", "cp", "archiv – alles erhalten (Rechte, Besitzer, Zeit, Links)"],
                ["-p", "mkdir", "Zwischenordner anlegen, kein Fehler wenn schon vorhanden"],
            ],
        },
    ],

    "sicherheit": [
        "**Nie** `rm -rf /`, `rm -rf /*` oder `rm -rf ~` – löscht das System bzw. alle deine Daten. Ein Leerzeichen zu viel reicht: `rm -rf / home/alt` statt `rm -rf /home/alt`.",
        "Nie `rm -rf $ORDNER/` in Skripten ohne Prüfung – ist die Variable leer, wird daraus `rm -rf /`. Immer `${ORDNER:?}` benutzen.",
        "Nie als root in `/` stehen und mit Platzhaltern löschen – vorher `pwd`!",
        "Kein Befehl mit `-f` (force), wenn man nicht genau weiss, warum er ohne `-f` nicht geht.",
    ],
    "tipps": [
        "Bei `cp`/`rsync` bedeutet ein **Schrägstrich am Ende** oft etwas anderes – Seite „Dateien übertragen“.",
        "Tippfehler vermeiden: Pfade mit **Tab** vervollständigen statt tippen.",
        "Für richtige Backups statt `cp` lieber `rsync -a` – kann abbrechen und weitermachen.",
    ],
    "fehler": [
        "`cp -r ordner ziel` wenn `ziel` schon existiert → landet als `ziel/ordner`, nicht als Ersatz.",
        "`mv datei.txt /etc` ohne sudo → Permission denied; mit falschem Ziel überschreibt mv ohne Frage.",
        "`rm ordner` → `Is a directory`: für Ordner braucht es `-r` (oder `rmdir` bei leeren).",
    ],
    "siehe_auch": ["navigieren", "dateirechte", "dateien_uebertragen", "archive", "todsuenden"],
}
