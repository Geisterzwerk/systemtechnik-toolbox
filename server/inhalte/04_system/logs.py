# =============================================================================
# Thema: Logs (journalctl, /var/log)  (Kategorie: System & Dienste)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Logs lesen: journalctl & /var/log",
    "reihenfolge": 4,
    "kurz": "Wenn etwas nicht geht, steht der Grund fast immer in einem Log.",
    "stichworte": ["log", "logs", "logdatei", "journal", "journalctl", "syslog", "auth.log", "dmesg", "kern.log",
                   "fehlermeldung", "protokoll", "logrotate", "boot log", "journal grösse", "vacuum"],

    "erklaerung": """
## Zwei Orte für Logs
- **systemd-Journal** – alle Dienste, Kernel und Bootvorgänge, gelesen mit **`journalctl`**. Kann filtern nach Dienst, Zeit, Wichtigkeit.
- **Textdateien in `/var/log`** – klassisch, werden von vielen Programmen zusätzlich geschrieben (`syslog`, `auth.log`, Webserver-Logs).
## journalctl – die wichtigsten Filter
- `-u dienst` – nur ein Dienst (Unit)
- `-f` – live mitlesen (follow)
- `-b` – nur seit dem letzten Booten, `-b -1` = vorheriger Boot (warum ist er abgestürzt?)
- `-p err` – nur Fehler und schlimmer
- `--since "1 hour ago"` / `--since today` / `--since "2026-09-29 08:00"`
- `-e` – ans Ende springen, `-x` – mit Erklärungen
## Wichtigkeit (Priorität)
0 emerg · 1 alert · 2 crit · **3 err** · 4 warning · 5 notice · 6 info · 7 debug. `-p err` zeigt 0 bis 3.
## Logs werden automatisch aufgeräumt
**logrotate** komprimiert alte Logs (`syslog.2.gz`) und löscht sehr alte. Das Journal begrenzt sich selbst auf einen Anteil der Festplatte.
""",

    "befehle": [
        {"titel": "journalctl", "zeilen": [
            ("journalctl -u ssh", "Log eines Dienstes"),
            ("sudo journalctl -u nginx -f", "Live mitlesen"),
            ("journalctl -u nginx --since \"1 hour ago\"", "Nur die letzte Stunde"),
            ("journalctl -p err -b", "Alle Fehler seit dem Booten"),
            ("journalctl -b -1 -e", "Ende des VORHERIGEN Boots (warum abgestürzt/neu gestartet?)"),
            ("journalctl -xe", "Letzte Einträge mit Erklärungen (klassisch nach Fehlern)"),
            ("journalctl --disk-usage", "Wie viel Platz braucht das Journal?"),
            ("sudo journalctl --vacuum-time=14d", "Einträge älter als 14 Tage löschen"),
        ]},
        {"titel": "Dateien in /var/log", "zeilen": [
            ("sudo tail -f /var/log/syslog", "Allgemeines System-Log live"),
            ("sudo less /var/log/auth.log", "Anmeldungen, SSH, sudo"),
            ("sudo dmesg -T | tail -30", "Kernel-Meldungen (Hardware, Festplatten, USB)"),
            ("sudo zgrep \"error\" /var/log/syslog.*.gz", "In alten, komprimierten Logs suchen"),
            ("ls -lh /var/log", "Welche Logs gibt es, wie gross sind sie?"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 Wichtige Log-Dateien",
            "kopf": ["Datei", "Inhalt"],
            "zeilen": [
                ["/var/log/syslog", "fast alles – der erste Blick bei Problemen"],
                ["/var/log/auth.log", "Logins, SSH, sudo – für die Sicherheit"],
                ["/var/log/kern.log / dmesg", "Kernel: Hardware, Treiber, Festplattenfehler"],
                ["/var/log/apt/history.log", "welche Pakete wann installiert/aktualisiert"],
                ["/var/log/unattended-upgrades/", "automatische Updates"],
                ["/var/log/ufw.log", "blockierte Verbindungen der Firewall"],
                ["/var/log/nginx/, /var/log/apache2/", "Zugriffe und Fehler des Webservers"],
                ["/var/log/fail2ban.log", "gesperrte IPs"],
            ],
        },
    ],

    "beispiele": [
        {"titel": "Dienst startet nicht – Fehler finden",
         "code": {"Bash": r'''sudo systemctl start meinapp
systemctl status meinapp --no-pager
journalctl -u meinapp -n 50 --no-pager      # die letzten 50 Zeilen'''},
         "ausgabe": "meinapp.service: Main process exited, code=exited, status=1/FAILURE\n...\nPermissionError: [Errno 13] Permission denied: '/opt/meinapp/daten.db'"},
    ],

    "sicherheit": [
        "Nie Logs löschen, um Platz zu schaffen, ohne zu wissen **warum** sie so gross sind – ein explodierendes Log ist ein Symptom (Angriff, Fehler-Schleife).",
        "`/var/log/auth.log` regelmässig anschauen: viele `Failed password` = Bots probieren Passwörter → Passwort-Login abschalten, fail2ban.",
        "Logs können Passwörter, Tokens oder Kundendaten enthalten – nicht ungefiltert in Foren oder Tickets posten.",
    ],
    "tipps": [
        "Standard-Benutzer sehen nicht alle Logs → Gruppe **adm** (`sudo usermod -aG adm name`) oder `sudo`.",
        "Zwei SSH-Fenster: in einem `journalctl -f`, im anderen arbeiten – man sieht sofort, was passiert.",
        "`journalctl -u dienst -o cat` zeigt nur den Text ohne Datum/Host – übersichtlicher.",
    ],
    "fehler": [
        "Nur `systemctl status` angeschaut – der eigentliche Fehler steht oft weiter oben im Journal (`journalctl -u dienst -n 100`).",
        "Nach einem Absturz `journalctl -b` gelesen → das ist der **aktuelle** Boot. Der Absturz steht in `-b -1`.",
    ],
    "siehe_auch": ["dienste_systemctl", "fehlersuche", "dateien_anzeigen", "suchen"],
}
