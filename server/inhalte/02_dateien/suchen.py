# =============================================================================
# Thema: Suchen (find, grep, which)  (Kategorie: Dateien & Navigation)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Suchen: find, grep, which",
    "reihenfolge": 5,
    "kurz": "Dateien nach Name, Grösse oder Alter finden – und Text in Dateien suchen.",
    "stichworte": ["suchen", "finden", "find", "grep", "which", "whereis", "locate", "plocate", "text suchen",
                   "datei finden", "grosse dateien", "regex", "rekursiv", "-exec"],

    "erklaerung": """
## find – Dateien finden
`find wo was` – sucht **Dateien und Ordner** nach Name, Typ, Grösse, Alter, Besitzer …
- `find /etc -name "*.conf"` – nach Namen (Anführungszeichen nicht vergessen!)
- `-iname` = ohne Gross/Klein, `-type f` = nur Dateien, `-type d` = nur Ordner
- `-size +100M` = grösser als 100 MB, `-mtime -1` = in den letzten 24 h geändert
## grep – Text in Dateien suchen
`grep muster datei` – zeigt alle **Zeilen**, die das Muster enthalten. Extrem oft mit einer Pipe: `befehl | grep wort`.
- `-i` Gross/Klein egal, `-r` ganzer Ordner, `-n` Zeilennummer, `-v` Zeilen **ohne** das Muster
- `-E` erweiterte reguläre Ausdrücke: `grep -E "error|fail"`
## Wo liegt ein Programm?
`which nginx` zeigt den Pfad zum Programm, `type befehl` sagt, ob es ein Programm, Alias oder eingebauter Befehl ist.
""",

    "befehle": [
        {"titel": "find", "zeilen": [
            ("find /etc -name \"*.conf\"", "Alle .conf-Dateien unter /etc"),
            ("find ~ -iname \"*bericht*\"", "Im Home, Gross-/Kleinschreibung egal"),
            ("sudo find / -type f -size +500M 2>/dev/null", "Dateien grösser als 500 MB (Speicher voll?)"),
            ("find /var/log -mtime -1", "In den letzten 24 h geändert"),
            ("find . -type d -name node_modules", "Nur Ordner mit diesem Namen"),
            ("find /tmp -name \"*.tmp\" -mtime +7 -print", "Alte temp-Dateien ANZEIGEN (vor dem Löschen!)"),
        ]},
        {"titel": "grep", "zeilen": [
            ("grep -i error /var/log/syslog", "Zeilen mit „error“ (egal ob gross/klein)"),
            ("sudo grep -rn \"Port\" /etc/ssh/", "Rekursiv im Ordner, mit Datei und Zeilennummer"),
            ("grep -v \"^#\" datei.conf", "Alle Zeilen, die NICHT mit # beginnen"),
            ("grep -E \"fail|error|denied\" /var/log/syslog", "Mehrere Wörter gleichzeitig"),
            ("grep -c \"Failed password\" /var/log/auth.log", "Nur zählen: wie viele fehlgeschlagene Logins?"),
            ("ps aux | grep nginx", "In der Ausgabe eines anderen Befehls suchen"),
        ]},
        {"titel": "Programme finden", "zeilen": [
            ("which python3", "Pfad des Programms"),
            ("type ll", "Alias, eingebaut oder Programm?"),
            ("apt-file search bin/dig", "Welches Paket liefert diese Datei? (vorher: sudo apt install apt-file && sudo apt-file update)"),
        ]},
    ],

    "beispiele": [
        {"titel": "Wer versucht sich per SSH einzuloggen?",
         "code": {"Bash": r'''sudo grep "Failed password" /var/log/auth.log | tail -5
sudo grep "Failed password" /var/log/auth.log | grep -oE "from [0-9.]+" | sort | uniq -c | sort -rn | head'''},
         "ausgabe": "    312 from 45.xx.xx.12\n     97 from 103.xx.xx.8\n     ..."},
        {"titel": "Gefundene Dateien bearbeiten: erst anzeigen, dann löschen",
         "code": {"Bash": r'''find /var/backups/alt -name "*.tar.gz" -mtime +30 -print     # prüfen
find /var/backups/alt -name "*.tar.gz" -mtime +30 -delete    # erst dann löschen'''}},
    ],

    "sicherheit": [
        "`find … -delete` oder `-exec rm` **immer zuerst mit `-print`** ausführen und die Liste lesen. Die Reihenfolge der Optionen zählt: `-delete` vor `-name` löscht ALLES.",
        "Nie `find / … -exec chmod` oder `-exec chown` ohne genaue Einschränkung – ändert sonst Systemdateien.",
    ],
    "tipps": [
        "`2>/dev/null` hinter `find /` blendet die vielen „Permission denied“ aus.",
        "Nach Namen im ganzen System sehr schnell: `sudo apt install plocate`, dann `locate dateiname`.",
        "`grep -A3 -B3 wort` zeigt zusätzlich 3 Zeilen nach/vor jedem Treffer – Kontext bei Log-Fehlern.",
    ],
    "fehler": [
        "`find / -name *.conf` ohne Anführungszeichen → die Shell ersetzt `*.conf` vorher durch Dateien im aktuellen Ordner.",
        "`grep` findet nichts wegen Gross/Klein → `-i` benutzen.",
        "`ps aux | grep nginx` zeigt immer auch die grep-Zeile selbst – das ist normal. Besser: `pgrep -a nginx`.",
    ],
    "siehe_auch": ["pipes_umleitung", "dateien_anzeigen", "logs", "festplatten"],
}
